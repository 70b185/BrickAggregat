#!/usr/bin/env python3
"""Public GitHub numbers for every catalogued repo: description, stars, archived flag, creation date.

Uses the search API through `gh` (several repos per query), so it needs `gh` with a token (GH_TOKEN in Actions).
Writes into state/meta.json next to what check_updates.py stores. Failing queries keep the old values.
"""
from __future__ import annotations

import json
import subprocess
import time

from common import STATE, load_json, projects, repo_slug, write_json

META = STATE / "meta.json"
FIELDS = "fullName,description,stargazersCount,isArchived,createdAt,pushedAt,isFork"


def search(slugs):
    q = [f"repo:{s}" for s in slugs]   # separate arguments: gh would quote one string as a phrase
    for attempt in range(3):
        p = subprocess.run(["gh", "search", "repos", *q, "--include-forks", "true", "--limit", "100", "--json", FIELDS],
                           capture_output=True, text=True, timeout=90)
        if p.returncode == 0:
            return json.loads(p.stdout or "[]")
        time.sleep(5 * (attempt + 1))
    print("search failed:", p.stderr.strip()[:200])
    return None


def main():
    meta = load_json(META, {})
    slugs = {repo_slug(p["repo"]): p["repo"] for p in projects() if repo_slug(p.get("repo"))}
    keys = list(slugs)
    got = 0
    for i in range(0, len(keys), 6):
        batch = keys[i:i + 6]
        res = search(batch)
        time.sleep(2.2)  # search API: 30 requests a minute
        if res is None:
            continue
        low = {s.lower(): s for s in batch}
        for r in res:
            s = low.get(r["fullName"].lower())
            if not s:
                continue
            m = meta.setdefault(slugs[s], {})
            m["description"] = r.get("description") or m.get("description")
            m["stars"] = r.get("stargazersCount", 0)
            m["created"] = (r.get("createdAt") or "")[:10] or m.get("created")
            m["pushed"] = (r.get("pushedAt") or "")[:10]
            m["fork"] = bool(r.get("isFork"))
            if r.get("isArchived"):
                m["archived"] = True
            else:
                m.pop("archived", None)
            got += 1
    write_json(META, dict(sorted(meta.items())))
    print(f"GitHub numbers for {got} of {len(keys)} repos")


if __name__ == "__main__":
    main()
