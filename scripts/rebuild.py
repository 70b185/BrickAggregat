#!/usr/bin/env python3
"""Run every local generator in order (no network): validate, then build."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for script in ("validate.py", "build.py"):
    r = subprocess.run([sys.executable, str(HERE / script)])
    if r.returncode != 0:
        sys.exit(r.returncode)
