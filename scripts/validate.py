#!/usr/bin/env python3
"""Check data/*.yml and knowledge/*.md: required fields, vocabularies, unique ids and repos, no repo both catalogued
and ignored, every {source-key} used in knowledge/ defined in knowledge/SOURCES.md, no binaries in the repo."""
from __future__ import annotations

import re
import sys
from collections import Counter

from common import CATEGORIES, DEVICES, FIRMWARES, ROOT, load_yaml, repo_slug

REQ = ("id", "name", "author", "category", "repo", "added")


def main():
    err = []
    data = load_yaml("projects.yml")
    ps = data.get("projects") or []
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(data.get("checked", ""))):
        err.append("projects.yml: `checked` must be a date")
    ids = Counter(p.get("id") for p in ps)
    err += [f"duplicate id: {i}" for i, n in ids.items() if n > 1]
    slugs = Counter((repo_slug(p.get("repo")) or "").lower() for p in ps)
    err += [f"repo listed twice: {s}" for s, n in slugs.items() if n > 1 and s]
    for p in ps:
        where = p.get("id", "?")
        for k in REQ:
            if not p.get(k):
                err.append(f"{where}: missing {k}")
        if p.get("category") not in CATEGORIES:
            err.append(f"{where}: unknown category {p.get('category')}")
        if p.get("repo") and not repo_slug(p["repo"]):
            err.append(f"{where}: repo must be a https://github.com/owner/name URL")
        for f in p.get("runs_on") or []:
            if f not in FIRMWARES:
                err.append(f"{where}: unknown firmware {f} (see scripts/common.py FIRMWARES)")
        for d in p.get("devices") or []:
            if d not in DEVICES:
                err.append(f"{where}: unknown device {d}")
        if p.get("id") and not re.match(r"^[a-z0-9][a-z0-9-]*$", p["id"]):
            err.append(f"{where}: id must be lower-case letters, digits and dashes")
        if p.get("note") and len(p["note"]) > 300:
            err.append(f"{where}: note longer than 300 characters")
    ign = load_yaml("ignore.yml").get("ignore") or []
    for e in ign:
        s = (repo_slug(e.get("repo")) or "").lower()
        if not e.get("reason"):
            err.append(f"ignore.yml: {e.get('repo')} has no reason")
        if s and slugs.get(s):
            err.append(f"{s} is both catalogued and ignored")
    # knowledge source keys
    srcs = (ROOT / "knowledge" / "SOURCES.md").read_text(encoding="utf-8")
    defined = set(re.findall(r"^\| `\{([a-z0-9-]+)\}`", srcs, re.M))
    for f in (ROOT / "knowledge").glob("*.md"):
        if f.name == "SOURCES.md":
            continue
        for k in set(re.findall(r"(?<![\w/$])\{([a-z0-9-]+)\}", f.read_text(encoding="utf-8"))):
            if k not in defined:
                err.append(f"knowledge/{f.name}: source key {{{k}}} is not in SOURCES.md")
    # no binaries
    for f in ROOT.rglob("*"):
        if ".git" in f.parts or not f.is_file():
            continue
        if re.search(r"\.(bin|img|elf|so|zip|7z|pakz|tar|gz)$", f.name, re.I):
            err.append(f"binary file in the repo: {f.relative_to(ROOT)}")
    if err:
        print("\n".join(err))
        print(f"\n{len(err)} problem(s)")
        sys.exit(1)
    print(f"ok: {len(ps)} projects, {len(ign)} ignored, {len(defined)} source keys")


if __name__ == "__main__":
    main()
