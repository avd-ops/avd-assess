#!/usr/bin/env python3
"""Checks that no tracked text file names a third-party product from tests/wording.json: products appear
as categories, with their public documentation pinned, never by name (owner, 2026-10-21).

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "tests" / "wording.json"
TEXT = {".md", ".yaml", ".yml", ".json", ".jsonl", ".py", ".txt"}

rules = json.loads(RULES.read_text(encoding="utf-8"))
pattern = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in rules["banned"]) + r")(?![\w-])", re.I)
files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
                       capture_output=True, text=True, check=True).stdout.split()

errors = []
for rel in files:
    path = ROOT / rel
    if path.suffix not in TEXT or path == RULES or not path.exists():
        continue
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        m = pattern.search(line)
        if m:
            errors.append(f"{rel}:{n}: names {m.group(1)!r}; use the category instead (tests/wording.json)")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} lines)")
    sys.exit(1)
print(f"RESULT PASS ({len(files)} files, {len(rules['banned'])} terms)")
