"""Shared helpers for the Brick Aggregat scripts (paths, YAML loading, git-based repo reads)."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE = ROOT / "state"
EXPORT = ROOT / "export"
CATALOG = ROOT / "catalog"

TODAY = dt.date.today()


def load_yaml(name: str):
    with open(DATA / name, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, obj, indent=1):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False, sort_keys=False)
        f.write("\n")
    os.replace(tmp, path)


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repo_slug(url: str | None) -> str | None:
    """https://github.com/Owner/Name(.git) -> Owner/Name"""
    if not url:
        return None
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", url.strip())
    if not m:
        return None
    return f"{m.group(1)}/{m.group(2).removesuffix('.git')}"


def run(cmd: list[str], cwd=None, timeout=120, check=True) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}: {p.stderr.strip()[:300]}")
    return p.stdout


def ls_remote(url: str) -> dict:
    """HEAD sha and tag names without downloading anything."""
    out = run(["git", "ls-remote", "--symref", url, "HEAD", "refs/tags/*"], timeout=60)
    head, tags, branch = None, [], None
    for line in out.splitlines():
        if line.startswith("ref: "):
            branch = line.split()[1].removeprefix("refs/heads/")
            continue
        sha, ref = line.split("\t")
        if ref == "HEAD":
            head = sha
        elif ref.startswith("refs/tags/") and not ref.endswith("^{}"):
            tags.append(ref.removeprefix("refs/tags/"))
    return {"head": head, "branch": branch, "tags": sorted(tags)}


LICENSE_HINTS = [
    ("GPL-3.0", r"GNU GENERAL PUBLIC LICENSE\s+Version 3"),
    ("GPL-2.0", r"GNU GENERAL PUBLIC LICENSE\s+Version 2"),
    ("AGPL-3.0", r"GNU AFFERO GENERAL PUBLIC LICENSE"),
    ("LGPL-3.0", r"GNU LESSER GENERAL PUBLIC LICENSE\s+Version 3"),
    ("LGPL-2.1", r"GNU LESSER GENERAL PUBLIC LICENSE\s+Version 2\.1"),
    ("MPL-2.0", r"Mozilla Public License,? (version|Version) 2\.0"),
    ("Apache-2.0", r"Apache License,?\s+Version 2\.0"),
    ("MIT", r"\bMIT License\b|Permission is hereby granted, free of charge"),
    ("BSD-3-Clause", r"Neither the name of"),
    ("BSD-2-Clause", r"Redistribution and use in source and binary forms"),
    ("Zlib", r"This software is provided 'as-is'"),
    ("Unlicense", r"This is free and unencumbered software"),
    ("CC0-1.0", r"CC0 1\.0|Creative Commons Zero"),
    ("0BSD", r"Permission to use, copy, modify, and/or distribute this software for any"),
    ("ISC", r"\bISC License\b"),
]


def guess_license(text: str) -> str:
    for spdx, pat in LICENSE_HINTS:
        if re.search(pat, text, re.I):
            return spdx
    return "other"


# source files (not scripts that only launch a binary): used to tell a source repo from a release-only repo
CODE_EXT = re.compile(r"\.(c|cc|cpp|cxx|h|hpp|rs|go|zig|py|lua|js|ts|java|kt|cs|swift|nim|odin|v|asm|s|glsl|frag|vert)$", re.I)


def read_repo(url: str, want_readme=True) -> dict:
    """Blobless depth-1 clone (no checkout): commit date, file list, README start, pak.json, licence.

    Costs one small pack download per repo; no API token needed."""
    tmp = tempfile.mkdtemp(prefix="ba-")
    try:
        run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", url, tmp], timeout=180)
        info = {}
        info["head"] = run(["git", "rev-parse", "HEAD"], cwd=tmp).strip()
        info["last_commit"] = run(["git", "log", "-1", "--format=%cs"], cwd=tmp).strip()
        files = run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=tmp).splitlines()
        info["files"] = len(files)
        code = [f for f in files if CODE_EXT.search(f)]
        info["code_files"] = len(code)
        info["script_files"] = sum(1 for f in files if re.search(r"\.(sh|bash)$|(^|/)launch$", f))
        info["binary_files"] = sum(1 for f in files if re.search(r"\.(elf|so|zip|7z|pakz|bin|img|AppImage)$", f, re.I))
        top = [f for f in files if "/" not in f]

        def show(path, limit=20000):
            try:
                return run(["git", "show", f"HEAD:{path}"], cwd=tmp, timeout=60)[:limit]
            except RuntimeError:
                return None

        lic = next((f for f in top if re.match(r"(LICEN[SC]E|COPYING)(\.|$)", f, re.I)), None)
        if lic:
            info["license_file"] = lic
            info["license"] = guess_license(show(lic) or "")
        else:
            info["license"] = None
        if "pak.json" in top:
            try:
                pj = json.loads(show("pak.json") or "{}")
                info["pak"] = {k: pj.get(k) for k in ("name", "version", "type", "description", "author", "platforms")}
            except json.JSONDecodeError:
                info["pak"] = {"error": "pak.json does not parse"}
        info["has_pak_dir"] = any(re.search(r"\.pak/", f) for f in files) or "launch.sh" in top
        if want_readme:
            rd = next((f for f in top if re.match(r"readme(\.md|\.markdown|\.txt|\.rst)?$", f, re.I)), None)
            if rd:
                info["readme"] = show(rd, 6000)
        return info
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- vocabulary (validate.py and build.py)
CATEGORIES = {
    "music-make": ("Make music", "Instruments, trackers, sequencers, samplers, effects and M8 clients"),
    "music-play": ("Listen", "Music, radio, podcast and audiobook players"),
    "os": ("Firmware", "Custom firmwares, launchers and frontends"),
    "app": ("Apps & tools", "Stores, system tools, network, sync, ROM management and everything else on the device"),
    "emulator": ("Emulators", "Emulator paks and cores"),
    "port": ("Games & ports", "PortMaster, ports and original games"),
    "media": ("Video & reading", "Video, TV, readers, galleries"),
    "theme": ("Look", "Themes, overlays, shaders, fonts, LEDs"),
    "dev": ("Developer", "Toolchains, SDKs, UI libraries, kernels, research notes"),
    "guide": ("Guides & companions", "Guides, docs, installers and companion apps on a computer or phone"),
}
FIRMWARES = {
    "nextui": "NextUI", "minui": "MinUI", "knulli": "KNULLI", "muos": "muOS", "crossmix": "CrossMix", "spruce": "spruce",
    "nx-redux": "NX Redux", "stock": "Stock OS", "portmaster": "PortMaster", "tortos": "TortOS",
}
DEVICES = {"brick": "Brick", "brick-hammer": "Brick Hammer", "brick-pro": "Brick Pro", "smart-pro": "Smart Pro"}
SITE_URL = "https://70b185.github.io/trimui-music-apps/"
REPO_URL = "https://github.com/70b185/trimui-music-apps"


def projects():
    return load_yaml("projects.yml").get("projects", [])
