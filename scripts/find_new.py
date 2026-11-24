#!/usr/bin/env python3
"""Find Brick projects that are in none of data/projects.yml, data/candidates.yml, data/ignore.yml.

Sources (configured in data/sources.yml):
  1. GitHub repository search: names/descriptions, README text (`--match readme`), forks, topics   (needs gh)
  2. NextUI Pak Store storefront                                                                      (git)
  3. itch.io tag feeds (RSS): many music apps are published there, often without a GitHub repo        (https)
  4. YouTube search, only when YOUTUBE_API_KEY is set: video titles and the links in their descriptions
     (GitHub, itch.io, Gumroad, own sites). Many Brick music apps are first shown on YouTube.

Output: state/NEW.md and state/new.json. A hit is "known" when its GitHub repo or its URL (itch.io page,
Gumroad page, website, video) appears in projects.yml (repo, url, links), candidates.yml or ignore.yml.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from common import STATE, TODAY, load_json, load_yaml, projects, repo_slug, run, write_json, write_text

FIELDS = "fullName,description,pushedAt,stargazersCount,isFork,isArchived,url"
UA = {"User-Agent": "brick-aggregat/1.0 (+https://github.com/70b185/trimui-music-apps)"}


def norm(u):
    """Comparable form of a URL: no scheme, no www, no query, no trailing slash, lower case."""
    if not u:
        return ""
    u = re.sub(r"^https?://(www\.)?", "", u.strip().lower()).split("#")[0]
    if not u.startswith("youtube.com/watch"):
        u = u.split("?")[0]
    return u.rstrip("/").removesuffix(".git")


def known_urls():
    known = set()
    for p in projects():
        for u in [p.get("repo"), p.get("url"), *(p.get("links") or {}).values()]:
            if u:
                known.add(norm(u))
    for f, key in (("candidates.yml", "projects"), ("ignore.yml", "ignore")):
        for e in load_yaml(f).get(key) or []:
            for u in (e.get("repo"), e.get("url")):
                if u:
                    known.add(norm(u))
    return known


def gh_search(args):
    for attempt in range(3):
        p = subprocess.run(["gh", "search", "repos", *args, "--limit", "200", "--json", FIELDS],
                           capture_output=True, text=True, timeout=120)
        if p.returncode == 0:
            return json.loads(p.stdout or "[]")
        time.sleep(8 * (attempt + 1))
    print("search failed:", " ".join(args), p.stderr.strip()[:200])
    return []


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def storefront(cfg):
    tmp = tempfile.mkdtemp(prefix="ba-sf-")
    try:
        run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", cfg["repo"], tmp], timeout=180)
        data = json.loads(run(["git", "show", f"HEAD:{cfg['file']}"], cwd=tmp))
        out = []
        for sec in ("paks", "experimental_paks"):
            for p in data.get(sec, []):
                if not p.get("disabled"):
                    out.append({"url": p["repo_url"], "title": p.get("storefront_name") or "",
                                "why": f"Pak Store{' (experimental)' if sec != 'paks' else ''}: {', '.join(p.get('categories') or [])}"})
        return out
    except Exception as e:
        print("storefront failed:", e)
        return []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def itch(cfg, since):
    """itch.io browse pages have an RSS twin: the same path with .xml appended."""
    out = []
    for kind in cfg.get("kinds", ["tools", "games"]):
        for tag in cfg.get("tags", []):
            url = f"https://itch.io/{kind}/newest/tag-{tag}.xml"
            try:
                root = ET.fromstring(http_get(url))
            except Exception as e:
                print(f"itch.io {url}: {e}")
                continue
            for it in root.iter("item"):
                link = (it.findtext("link") or "").strip()
                title = (it.findtext("plainTitle") or it.findtext("title") or "").strip()
                date = (it.findtext("updateDate") or it.findtext("pubDate") or "").strip()
                d = ""
                for fmt in ("%a, %d %b %Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        d = dt.datetime.strptime(date[:25].strip(), fmt).date().isoformat()
                        break
                    except ValueError:
                        pass
                if d and d < since:
                    continue
                desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", it.findtext("description") or "")).strip()
                out.append({"url": link, "title": title, "desc": desc[:160], "date": d, "why": f"itch.io {kind}/tag-{tag}"})
            time.sleep(1)
    return out


LINK_RE = re.compile(r"https?://(?:www\.)?(?:github\.com/[\w.-]+/[\w.-]+|[\w-]+\.itch\.io/[\w-]+|[\w-]+\.gumroad\.com/l/[\w-]+"
                     r"|gumroad\.com/l/[\w-]+|codeberg\.org/[\w.-]+/[\w.-]+|gitlab\.com/[\w.-]+/[\w.-]+)", re.I)


def youtube(cfg, since):
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        print("youtube: no YOUTUBE_API_KEY, skipped")
        return []
    out = []
    must = re.compile(cfg.get("must_match", "trimui|brick"), re.I)
    for q in cfg.get("queries", []):
        params = {"part": "snippet", "q": q, "type": "video", "maxResults": "50", "order": "date",
                  "publishedAfter": f"{since}T00:00:00Z", "key": key}
        try:
            data = json.loads(http_get("https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(params)))
            ids = [i["id"]["videoId"] for i in data.get("items", []) if i.get("id", {}).get("videoId")]
            if not ids:
                continue
            vids = json.loads(http_get("https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
                {"part": "snippet", "id": ",".join(ids), "key": key})))  # full descriptions
        except Exception as e:
            print(f"youtube '{q}': {e}")
            continue
        for v in vids.get("items", []):
            sn = v["snippet"]
            if not must.search(f"{sn['title']} {sn.get('description', '')}"):
                continue
            links = sorted({m.group(0).rstrip(".,)") for m in LINK_RE.finditer(sn.get("description", ""))})
            out.append({"url": f"https://www.youtube.com/watch?v={v['id']}", "title": sn["title"],
                        "desc": f"channel {sn.get('channelTitle', '?')}", "date": sn["publishedAt"][:10],
                        "links": links, "why": f"YouTube: {q}"})
        time.sleep(0.5)
    return out


def main():
    cfg = load_yaml("sources.yml")
    known = known_urls()
    meta = load_json(STATE / "meta.json", {})
    known_desc = {(m.get("description") or "").strip().lower() for m in meta.values() if m.get("description")}
    since = (TODAY - dt.timedelta(days=cfg.get("days", 30))).isoformat()
    must = re.compile(cfg["must_match"], re.I)
    mustnot = re.compile(cfg["must_not_match"], re.I)
    hits = {}

    def add(url, title, desc, date, why, fork=False, links=()):
        h = hits.setdefault(norm(url), {"url": url, "title": title, "desc": desc or "", "date": date or "",
                                        "fork": fork, "links": list(links), "found_by": []})
        h["found_by"].append(why)

    # 1. GitHub
    queries = [([q], q) for q in cfg["searches"]]
    queries += [([q, "--match", "readme"], f"{q} (README)") for q in cfg.get("readme_searches", [])]
    queries += [([q, "--include-forks", "only"], f"{q} (forks)") for q in cfg.get("forks_too", [])]
    queries += [(["--topic", t], f"topic:{t}") for t in cfg.get("topics", [])]
    for args, label in queries:
        for r in gh_search([*args, "--updated", f">={since}"]):
            t = f"{r['fullName']} {r.get('description') or ''}"
            trusted = label.endswith("(README)") or (label.startswith("topic:") and "trimui" in label)
            if r["isArchived"] or mustnot.search(t) or not (must.search(t) or trusted):
                continue
            if r["isFork"] and (r.get("description") or "").strip().lower() in known_desc:
                continue
            url = f"https://github.com/{r['fullName']}"
            if norm(url) not in known:
                add(url, r["fullName"], r.get("description"), r["pushedAt"][:10], label, r["isFork"])
        time.sleep(2.2)
    # 2. Pak Store
    for p in storefront(cfg["storefront"]):
        if norm(p["url"]) not in known:
            add(p["url"], repo_slug(p["url"]) or p["url"], p["title"], "", p["why"])
    # 3. itch.io
    for p in itch(cfg.get("itch") or {}, since):
        if norm(p["url"]) not in known:
            add(p["url"], p["title"], p["desc"], p["date"], p["why"])
    # 4. YouTube: report a video unless it or one of its links is already catalogued
    for p in youtube(cfg.get("youtube") or {}, since):
        if norm(p["url"]) in known or any(norm(l) in known for l in p["links"]):
            continue
        add(p["url"], p["title"], p["desc"], p["date"], p["why"], links=p["links"])

    rows = sorted(hits.values(), key=lambda h: h["date"], reverse=True)
    groups = [("GitHub", lambda h: "github.com" in h["url"]), ("itch.io", lambda h: "itch.io" in h["url"]),
              ("YouTube (check the linked pages)", lambda h: "youtube.com" in h["url"])]
    lines = ["# Not catalogued yet", "",
             f"Found since {since} by the sources in data/sources.yml and in none of projects, candidates, ignore.",
             "Triage each (docs/UPDATING.md): add to data/projects.yml, or to data/ignore.yml with a reason (`repo:` or"
             " `url:`), or to data/candidates.yml when unclear.", ""]
    if not rows:
        lines.append("Nothing new.")
    for name, test in groups:
        sel = [h for h in rows if test(h)]
        if not sel:
            continue
        lines += [f"## {name} ({len(sel)})", ""]
        for h in sel:
            extra = f" links: {', '.join(h['links'])}" if h["links"] else ""
            lines.append(f"- [{h['title']}]({h['url']}){' (fork)' if h['fork'] else ''}"
                         f"{' - ' + h['desc'][:140] if h['desc'] else ''}{extra}"
                         f" _({h['date'] or 'date ?'}; {'; '.join(sorted(set(h['found_by'])))})_")
        lines.append("")
    write_text(STATE / "NEW.md", "\n".join(lines) + "\n")
    write_json(STATE / "new.json", rows)
    print(f"{len(rows)} not catalogued yet")


if __name__ == "__main__":
    main()
