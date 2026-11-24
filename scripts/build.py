#!/usr/bin/env python3
"""Generate everything derived from data/projects.yml + state/meta.json + knowledge/*.md.

Writes: export/projects.json, export/news.json, feed.xml, catalog/*.md, kb/*.html, llms.txt, sitemap.xml and the
counts block in README.md. Run through scripts/rebuild.py.
"""
from __future__ import annotations

import datetime as dt
import html
import re
from collections import Counter
from pathlib import Path

import markdown

from common import (CATALOG, CATEGORIES, DEVICES, EXPORT, FIRMWARES, REPO_URL, ROOT, SITE_URL, STATE, TODAY,
                    load_json, load_yaml, write_json, write_text)

CONTENT_CATS = {"guide", "theme"}   # repos of these hold content more than code: a licence is enough for "open"


def version_key(t):
    nums = [int(x) for x in re.findall(r"\d+", t or "")[:4]]
    return nums + [0] * (4 - len(nums))


def merge():
    data = load_yaml("projects.yml")
    meta = load_json(STATE / "meta.json", {})
    out = []
    for p in data["projects"]:
        if p.get("hidden"):
            continue
        m = meta.get(p.get("repo") or "", {})
        e = {k: p[k] for k in ("id", "name", "author", "category")}
        e["repo"] = p.get("repo") or ""
        e["url"] = p.get("url") or p.get("repo")
        for k in ("note", "links", "pak_store", "added", "aliases", "description"):
            if p.get(k):
                e[k] = p[k]
        e["runs_on"] = p.get("runs_on") or []
        e["devices"] = p.get("devices") or []
        e["description"] = (m.get("description") or (m.get("pak") or {}).get("description") or p.get("description") or "").strip()
        lic = m.get("license")
        e["license"] = lic or None
        src = "code" if m.get("code_files") else "scripts" if m.get("script_files") else "none"
        if not p.get("repo"):
            src, lic = "none", p.get("license")   # no public repo: store page or website only
        e["source"] = src
        e["open"] = bool(lic) and (src != "none" or p["category"] in CONTENT_CATS)
        e["last_commit"] = m.get("last_commit")
        tags = sorted(m.get("tags") or [], key=version_key)
        e["version"] = (m.get("pak") or {}).get("version") or (tags[-1] if tags else None)
        e["stars"] = m.get("stars")
        if m.get("archived"):
            e["archived"] = True
        if m.get("unreachable"):
            e["unreachable"] = m["unreachable"]
        days = (TODAY - dt.date.fromisoformat(e["last_commit"])).days if e["last_commit"] else 9999
        e["activity"] = ("archived" if m.get("archived") else "active" if days <= 90 else "quiet" if days <= 365
                         else "dormant")
        e["new"] = bool(p.get("added")) and (TODAY - dt.date.fromisoformat(str(p["added"]))).days <= 14 \
            and str(p["added"]) > "2026-11-24"   # the first import does not count as new
        out.append(e)
    return data.get("checked"), out


def news(entries):
    events = load_json(STATE / "changes.json", [])
    byid = {e["id"]: e for e in entries}
    rows = []
    for e in entries:
        if e.get("added") and str(e["added"]) > "2026-11-24":
            rows.append({"date": str(e["added"]), "id": e["id"], "what": "added", "detail": ""})
    for ev in events:
        if ev["what"] in ("release", "back online", "licence") and ev["id"] in byid:
            rows.append({k: ev.get(k, "") for k in ("date", "id", "what", "detail")})
    rows.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    cutoff = (TODAY - dt.timedelta(days=90)).isoformat()
    return [r for r in rows if r["date"] >= cutoff][:200]


def feed(rows, entries):
    byid = {e["id"]: e for e in entries}
    items = []
    for r in rows[:60]:
        e = byid[r["id"]]
        title = f"{e['name']}: {'new in the index' if r['what'] == 'added' else r['what']} {r.get('detail') or ''}".strip()
        items.append(f"""  <entry>
    <title>{html.escape(title)}</title>
    <link href="{html.escape(e['url'])}"/>
    <id>{html.escape(SITE_URL)}#{r['date']}-{r['id']}-{html.escape(r['what'])}-{html.escape(r.get('detail') or '')}</id>
    <updated>{r['date']}T00:00:00Z</updated>
    <summary>{html.escape(e.get('note') or e.get('description') or '')}</summary>
  </entry>""")
    updated = rows[0]["date"] if rows else TODAY.isoformat()
    write_text(ROOT / "feed.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Brick Aggregat: what is new</title>
  <link href="{SITE_URL}"/>
  <link rel="self" href="{SITE_URL}feed.xml"/>
  <id>{SITE_URL}</id>
  <updated>{updated}T00:00:00Z</updated>
{chr(10).join(items)}
</feed>
""")


def md_row(e):
    lic = e["license"] or "no licence"
    src = {"code": "", "scripts": " (scripts)", "none": " (no source)"}[e["source"]]
    fw = ", ".join(FIRMWARES.get(x, x) for x in e["runs_on"]) or "-"
    what = (e.get("note") or e.get("description") or "").replace("|", "/").replace("\n", " ")
    return (f"| [{e['name']}]({e['url']}) | {e['author']} | {what} | {fw} | {e.get('version') or '-'} |"
            f" {e.get('last_commit') or '-'} | {lic}{src} |")


def catalog(entries, checked):
    cnt = Counter(e["category"] for e in entries)
    idx = ["# Catalogue", "", f"Generated from `data/projects.yml` (checked {checked}). Do not edit by hand.", "",
           "| List | What | Entries |", "| --- | --- | --- |"]
    for c, (label, desc) in CATEGORIES.items():
        idx.append(f"| [{label}]({c}.md) | {desc} | {cnt.get(c, 0)} |")
        rows = sorted([e for e in entries if e["category"] == c], key=lambda e: (e["activity"] != "active", e["name"].lower()))
        page = [f"# {label}", "", desc + ".", "", f"{len(rows)} entries, generated {TODAY} from `data/projects.yml`."
                " Licence as found in the repo; *no source* = the repo holds releases or docs only.", "",
                "| Project | Author | What | Runs on | Version | Last commit | Licence |", "| --- | --- | --- | --- | --- | --- | --- |"]
        page += [md_row(e) for e in rows]
        write_text(CATALOG / f"{c}.md", "\n".join(page) + "\n")
    write_text(CATALOG / "README.md", "\n".join(idx) + "\n")


KB_CSS = """body{margin:0;background:#fbe4ee;color:#3a1027;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif}
a{color:#b4237a}code,pre{font:13px ui-monospace,Menlo,Consolas,monospace;background:#fad3e3;padding:1px 4px}th,td{border:1px solid #f1bcd3;padding:4px 8px;text-align:left;vertical-align:top}
@media(prefers-color-scheme:dark){:root:not([data-theme]) body{background:#0a0a0b;color:#f2eef0}:root:not([data-theme]) a{color:#ff5fa8}:root:not([data-theme]) code,:root:not([data-theme]) pre{background:#24191f}:root:not([data-theme]) th,:root:not([data-theme]) td{border-color:#2a2328}}
:root[data-theme=dark] body{background:#0a0a0b;color:#f2eef0}:root[data-theme=dark] a{color:#ff5fa8}:root[data-theme=dark] code,:root[data-theme=dark] pre{background:#24191f}:root[data-theme=dark] th,:root[data-theme=dark] td{border-color:#2a2328}
main{max-width:880px;margin:0 auto;padding:24px}pre{padding:10px;overflow:auto}table{border-collapse:collapse;font-size:14px;display:block;overflow:auto}
.top{font:12px ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px}.src{font-size:12px;vertical-align:super;text-decoration:none}"""


def kb_pages():
    src = ROOT / "knowledge"
    out = ROOT / "kb"
    out.mkdir(exist_ok=True)
    pages = []
    for f in sorted(src.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        title = (re.search(r"^# (.+)$", text, re.M) or [None, f.stem])[1]
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
        body = re.sub(r'href="([\w-]+)\.md(#[^"]*)?"', lambda m: f'href="{"index" if m[1] == "README" else m[1]}.html{m[2] or ""}"', body)
        body = re.sub(r'href="\.\./catalog/([\w-]+)\.md"', r'href="../?c=\1"', body)
        if f.stem == "SOURCES":
            body = re.sub(r"<td><code>\{([a-z0-9-]+)\}</code></td>", r'<td id="\1"><code>\1</code></td>', body)
        body = re.sub(r"(?<![\w/])\{([a-z0-9-]+)\}", r'<a class="src" href="SOURCES.html#\1">[\1]</a>', body)
        name = "index" if f.stem == "README" else f.stem
        write_text(out / f"{name}.html", f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="icon" href="data:,"><title>{html.escape(title)} - Brick Aggregat</title>
<script>try{{var t=localStorage.getItem("ba-theme");if(t==="pink"||t==="brick")t="light";if(t&&t!=="auto")document.documentElement.dataset.theme=t;}}catch(e){{}}</script><style>{KB_CSS}</style></head><body><main><div class="top"><a href="../">Brick Aggregat</a> / <a href="index.html">Developing</a>
 / <a href="{REPO_URL}/blob/main/knowledge/{f.name}">edit this page</a></div>
{body}</main></body></html>
""")
        pages.append({"file": f"kb/{name}.html", "title": title, "md": f"knowledge/{f.name}"})
    return pages


def readme_counts(entries, checked):
    p = ROOT / "README.md"
    if not p.exists():
        return
    cnt = Counter(e["category"] for e in entries)
    opened = sum(e["open"] for e in entries)
    active = sum(e["activity"] == "active" for e in entries)
    lines = [f"**{len(entries)} projects** ({opened} with a licence and source, {active} with commits in the last 90 days),"
             f" checked {checked}:", ""]
    lines.append(" · ".join(f"[{CATEGORIES[c][0]}]({SITE_URL}?c={c}) {cnt.get(c, 0)}" for c in CATEGORIES))
    block = "<!-- counts -->\n" + "\n".join(lines) + "\n<!-- /counts -->"
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"<!-- counts -->.*?<!-- /counts -->", block, text, flags=re.S)
    p.write_text(text, encoding="utf-8")


def main():
    checked, entries = merge()
    rows = news(entries)
    kb = kb_pages()
    cnt = Counter(e["category"] for e in entries)
    write_json(EXPORT / "projects.json", {
        "generated": TODAY.isoformat(), "checked": str(checked),
        "categories": [{"id": c, "label": l, "desc": d, "count": cnt.get(c, 0)} for c, (l, d) in CATEGORIES.items()],
        "firmwares": FIRMWARES, "devices": DEVICES, "kb": kb, "projects": entries}, indent=None)
    write_json(EXPORT / "news.json", rows)
    if not (EXPORT / "discussions.json").exists():
        write_json(EXPORT / "discussions.json", [])
    feed(rows, entries)
    catalog(entries, checked)
    readme_counts(entries, checked)
    llms = ["# Brick Aggregat", "", "> Index of free and open-source software for the TrimUI Brick, Brick Hammer and Brick Pro:"
            " firmwares, music apps, emulators, tools, plus a developer knowledge base.", "",
            "## Data", f"- [All projects as JSON]({SITE_URL}export/projects.json): one object per project, with licence, activity, firmwares",
            f"- [Catalogue as Markdown]({REPO_URL}/tree/main/catalog)", "", "## Developing for the Brick"]
    llms += [f"- [{k['title']}]({REPO_URL}/blob/main/{k['md']})" for k in kb]
    write_text(ROOT / "llms.txt", "\n".join(llms) + "\n")
    urls = [SITE_URL] + [SITE_URL + k["file"] for k in kb]
    write_text(ROOT / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls) + "\n</urlset>\n")
    print(f"built {len(entries)} entries, {len(rows)} news rows, {len(kb)} knowledge pages")


if __name__ == "__main__":
    main()
