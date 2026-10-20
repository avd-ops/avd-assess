#!/usr/bin/env python3
"""Builds index.json (avd-second-brain contract C20, avd-assess-index/v1) from references/,
observations/ and gaps/, so readers need no YAML parser. --check fails when index.json is stale.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.json"
REF_KEYS = ["id", "title", "url", "pin", "read", "license", "areas", "notes", "claims"]
CLAIM_KEYS = ["id", "says", "kind"]
OBS_KEYS = ["id", "claim", "verdict", "observed", "evidence", "date"]


def pick(data, keys):
    return {k: (str(data[k]) if k in ("read", "date") else data[k]) for k in keys if data.get(k) not in (None, "")}


def build():
    refs = []
    for path in sorted((ROOT / "references").glob("*.yaml")):
        ref = pick(yaml.safe_load(path.read_text(encoding="utf-8")) or {}, REF_KEYS)
        ref["claims"] = [pick(c, CLAIM_KEYS) for c in ref.get("claims") or []]
        refs.append(ref)
    obs = [pick(yaml.safe_load(p.read_text(encoding="utf-8")) or {}, OBS_KEYS)
           for p in sorted((ROOT / "observations").glob("*.yaml"))]
    gaps = []
    for p in sorted((ROOT / "gaps").glob("*.md")):
        if p.name == "README.md":
            continue
        heading = next((l[2:].strip() for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), p.stem)
        gaps.append({"id": p.stem, "title": heading.removeprefix("Gap: ")})
    doc = {"schema": "avd-assess-index/v1", "references": refs, "observations": obs, "gaps": gaps}
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def main():
    text = build()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("RESULT FAIL index.json is stale; run python3 scripts/build_index.py")
            return 1
        print("RESULT PASS index.json is current")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
