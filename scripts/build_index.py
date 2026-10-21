#!/usr/bin/env python3
"""Builds index.json (contract C20, avd-assess-index/v1) from references/, observations/ and gaps/,
map.json (avd-assess-map/v1) from pillars.yaml, dimensions.yaml, baselines.yaml, use-cases.yaml and
gold-standards.yaml, and endpoints.json (avd-assess-endpoints/v1) from endpoints.yaml, so readers need no
YAML parser. --check fails when any of them is stale.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.json"
MAP = ROOT / "map.json"
ENDPOINTS = ROOT / "endpoints.json"
# Where a probe can run, in the order views are written.
VANTAGES = ["browser", "device", "host"]
REF_KEYS = ["id", "title", "url", "pin", "archive", "read", "license", "areas", "pillars", "notes", "claims"]
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


def build_endpoints():
    """The endpoint map with each row's source URL and pin filled in from its reference, plus one list of
    row IDs per vantage, so a reader such as avd-linecheck's pack builder filters nothing itself."""
    doc = yaml.safe_load((ROOT / "endpoints.yaml").read_text(encoding="utf-8")) or {}
    refs = {}
    for path in (ROOT / "references").glob("*.yaml"):
        ref = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        refs[ref.get("id")] = ref
    lists = {lst["id"]: lst for lst in doc.get("lists", [])}

    def source(claim):
        ref = refs.get(claim.removeprefix("ref:").split("#")[0], {})
        return {"claim": claim, "url": ref.get("url"), "pin": ref.get("pin")}

    rows = []
    for e in doc.get("endpoints", []):
        row = dict(e)
        row["source"] = source(lists.get(e.get("list"), {}).get("claim", ""))
        rows.append(row)
    out = {
        "schema": doc.get("schema"),
        "version": doc.get("version"),
        "cloud": doc.get("cloud"),
        "readAt": doc.get("readAt", {}),
        "lists": [dict(lst, source=source(lst.get("claim", ""))) for lst in doc.get("lists", [])],
        "endpoints": rows,
        "views": {v: [r["id"] for r in rows if v in (r.get("probeFrom") or [])] for v in VANTAGES}
                 | {"notProbed": [r["id"] for r in rows if not r.get("probeFrom")]},
    }
    return json.dumps(out, indent=2, ensure_ascii=True, default=str) + "\n"


def main():
    wanted = {OUT: build(), MAP: build_map(), ENDPOINTS: build_endpoints()}
    if "--check" in sys.argv:
        stale = [p.name for p, text in wanted.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print(f"RESULT FAIL {', '.join(stale)} stale; run python3 scripts/build_index.py")
            return 1
        print("RESULT PASS index.json, map.json and endpoints.json are current")
        return 0
    for p, text in wanted.items():
        p.write_text(text, encoding="utf-8")
        print(f"Wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
