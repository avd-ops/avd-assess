#!/usr/bin/env python3
"""Builds index.json (contract C20, avd-assess-index/v1) from references/, observations/ and gaps/, and
map.json (avd-assess-map/v1) from pillars.yaml, dimensions.yaml, baselines.yaml, use-cases.yaml and
gold-standards.yaml, so readers need no YAML parser. --check fails when either file is stale.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.json"
MAP = ROOT / "map.json"
REF_KEYS = ["id", "title", "url", "pin", "archive", "read", "license", "areas", "pillars", "notes", "deprecated", "claims"]
CLAIM_KEYS = ["id", "says", "kind", "deprecated"]
OBS_KEYS = ["id", "claim", "verdict", "observed", "evidence", "date", "deprecated"]
# A gap page that a later major release may remove says so in one line (docs/distribution-spec.md section 6):
# <!-- deprecated: since=1.2.0 replacedBy=other-gap -->
GAP_DEPRECATED = re.compile(r"<!-- deprecated: since=(\S+)(?: replacedBy=(\S+))? -->")


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
        text = p.read_text(encoding="utf-8")
        heading = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), p.stem)
        gap = {"id": p.stem, "title": heading.removeprefix("Gap: ")}
        mark = GAP_DEPRECATED.search(text)
        if mark:
            gap["deprecated"] = {"since": mark.group(1), "replacedBy": mark.group(2)}
        gaps.append(gap)
    doc = {"schema": "avd-assess-index/v1", "references": refs, "observations": obs, "gaps": gaps}
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def build_map():
    """The map as one document: the pillars and every row, baseline, persona and registry entry, as written."""
    def read(name):
        return yaml.safe_load((ROOT / name).read_text(encoding="utf-8")) or {}
    dims = read("dimensions.yaml")
    doc = {
        "schema": "avd-assess-map/v1",
        "pillars": read("pillars.yaml").get("pillars", []),
        "landingZone": dims.get("landingZone", {}),
        "dimensions": dims.get("dimensions", []),
        "baselines": {k: v for k, v in read("baselines.yaml").items() if k != "schema"},
        "useCases": read("use-cases.yaml").get("entries", []),
        "goldStandards": read("gold-standards.yaml").get("entries", []),
    }
    return json.dumps(doc, indent=2, ensure_ascii=True, default=str) + "\n"


def main():
    wanted = {OUT: build(), MAP: build_map()}
    if "--check" in sys.argv:
        stale = [p.name for p, text in wanted.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print(f"RESULT FAIL {', '.join(stale)} stale; run python3 scripts/build_index.py")
            return 1
        print("RESULT PASS index.json and map.json are current")
        return 0
    for p, text in wanted.items():
        p.write_text(text, encoding="utf-8")
        print(f"Wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
