#!/usr/bin/env python3
"""List repos that look like Brick projects but are in none of data/projects.yml, data/candidates.yml,
data/ignore.yml. Sources and filters: data/sources.yml. Output: state/NEW.md (and state/new.json).

Needs `gh` with a token for the searches; the Pak Store storefront is read with git (no token).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
import time

from common import STATE, TODAY, load_json, load_yaml, projects, repo_slug, run, write_json, write_text

FIELDS = "fullName,description,pushedAt,stargazersCount,isFork,isArchived,url"


def gh_search(args):
    for attempt in range(3):
        p = subprocess.run(["gh", "search", "repos", *args, "--limit", "200", "--json", FIELDS],
                           capture_output=True, text=True, timeout=120)
        if p.returncode == 0:
            return json.loads(p.stdout or "[]")
        time.sleep(8 * (attempt + 1))
    print("search failed:", " ".join(args), p.stderr.strip()[:200])
    return []


def storefront(cfg):
    tmp = tempfile.mkdtemp(prefix="ba-sf-")
    try:
        run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", cfg["repo"], tmp], timeout=180)
        data = json.loads(run(["git", "show", f"HEAD:{cfg['file']}"], cwd=tmp))
        out = []
        for sec in ("paks", "experimental_paks"):
            for p in data.get(sec, []):
                if not p.get("disabled"):
                    out.append({"slug": repo_slug(p["repo_url"]), "name": p.get("storefront_name"),
                                "why": f"Pak Store{' (experimental)' if sec != 'paks' else ''}: {', '.join(p.get('categories') or [])}"})
        return out
    except Exception as e:
        print("storefront failed:", e)
        return []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    cfg = load_yaml("sources.yml")
    known = {repo_slug(p["repo"]).lower() for p in projects() if repo_slug(p.get("repo"))}
    # a fork whose description is the same as a catalogued repo's is a copy: not reported
    meta = load_json(STATE / "meta.json", {})
    known_desc = {(m.get("description") or "").strip().lower() for m in meta.values() if m.get("description")}
    for f in ("candidates.yml", "ignore.yml"):
        d = load_yaml(f) if (STATE.parent / "data" / f).exists() else {}
        for e in (d.get("ignore") or d.get("projects") or []):
            s = repo_slug(e.get("repo"))
            if s:
                known.add(s.lower())
    since = (TODAY - dt.timedelta(days=cfg.get("days", 30))).isoformat()
    must = re.compile(cfg["must_match"], re.I)
    mustnot = re.compile(cfg["must_not_match"], re.I)
    hits = {}
    queries = [([q], q) for q in cfg["searches"]]
    queries += [([q, "--include-forks", "only"], f"{q} (forks)") for q in cfg.get("forks_too", [])]
    queries += [(["--topic", t], f"topic:{t}") for t in cfg.get("topics", [])]
    for args, label in queries:
        for r in gh_search([*args, "--updated", f">={since}"]):
            t = f"{r['fullName']} {r.get('description') or ''}"
            trimui_topic = label.startswith("topic:") and "trimui" in label
            if r["isArchived"] or mustnot.search(t) or not (must.search(t) or trimui_topic):
                continue
            if r["isFork"] and (r.get("description") or "").strip().lower() in known_desc:
                continue
            s = r["fullName"]
            if s.lower() in known:
                continue
            h = hits.setdefault(s, {"slug": s, "description": r.get("description") or "", "pushed": r["pushedAt"][:10],
                                    "stars": r["stargazersCount"], "fork": r["isFork"], "found_by": []})
            h["found_by"].append(label)
        time.sleep(2.2)
    for p in storefront(cfg["storefront"]):
        if p["slug"] and p["slug"].lower() not in known:
            h = hits.setdefault(p["slug"], {"slug": p["slug"], "description": p["name"], "pushed": "", "stars": None,
                                            "fork": False, "found_by": []})
            h["found_by"].append(p["why"])
    rows = sorted(hits.values(), key=lambda h: (not any(x.startswith("Pak Store") for x in h["found_by"]), h["pushed"]), reverse=False)
    lines = ["# Not catalogued yet", "",
             f"Repos pushed since {since} that match the searches in data/sources.yml, plus Pak Store paks we do not list.",
             "Triage each (docs/UPDATING.md): add to data/projects.yml, or to data/ignore.yml with a reason, or to"
             " data/candidates.yml when unclear.", ""]
    if not rows:
        lines.append("Nothing new.")
    for h in rows:
        lines.append(f"- [{h['slug']}](https://github.com/{h['slug']}){' (fork)' if h['fork'] else ''}"
                     f"{' - ' + h['description'][:140] if h['description'] else ''}"
                     f" _({h['pushed'] or 'date ?'}; {'; '.join(sorted(set(h['found_by'])))})_")
    write_text(STATE / "NEW.md", "\n".join(lines) + "\n")
    write_json(STATE / "new.json", rows)
    print(f"{len(rows)} repo(s) not catalogued yet")


if __name__ == "__main__":
    main()
