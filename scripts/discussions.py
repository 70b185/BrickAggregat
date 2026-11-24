#!/usr/bin/env python3
"""Latest GitHub Discussions of this repo -> export/discussions.json (shown on the website's Ask tab).

Needs `gh` with a token that can read discussions (the workflow's GITHUB_TOKEN with `discussions: read`).
Keeps the old file when the query fails or Discussions are off.
"""
from __future__ import annotations

import json
import subprocess

from common import EXPORT, REPO_URL, write_json

QUERY = """query($owner:String!,$name:String!){repository(owner:$owner,name:$name){
  discussions(first:30, orderBy:{field:UPDATED_AT,direction:DESC}){nodes{
    title url number createdAt updatedAt isAnswered upvoteCount
    category{name slug emoji} author{login} comments{totalCount}}}}}"""


def main():
    owner, name = REPO_URL.rstrip("/").split("/")[-2:]
    p = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"owner={owner}", "-f", f"name={name}"],
                       capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        print("discussions: query failed, keeping the old file:", p.stderr.strip()[:200])
        return
    nodes = (((json.loads(p.stdout).get("data") or {}).get("repository") or {}).get("discussions") or {}).get("nodes") or []
    out = [{"title": n["title"], "url": n["url"], "number": n["number"], "created": n["createdAt"][:10],
            "updated": n["updatedAt"][:10], "answered": n.get("isAnswered"), "votes": n.get("upvoteCount", 0),
            "category": (n.get("category") or {}).get("name"), "slug": (n.get("category") or {}).get("slug"),
            "author": (n.get("author") or {}).get("login"), "comments": n["comments"]["totalCount"]} for n in nodes]
    write_json(EXPORT / "discussions.json", out)
    print(f"{len(out)} discussions")


if __name__ == "__main__":
    main()
