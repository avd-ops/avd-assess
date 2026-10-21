#!/usr/bin/env python3
"""Checks the deployment dimension register (dimensions.yaml, gap:deployment-dimensions): every row has a
home, a baseline whose claims exist, and landing zone parameters that exist; every landing zone parameter
has a home or a reason.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "dimensions.yaml"
STANDINGS = {"published", "prior", "guidance", "gap", "owned"}
MEASURES = {"fact", "rebuild", "measured", "intake", "none"}
PROPOSED = re.compile(r"^proposed:[a-z][A-Za-z0-9.]+$")
REQUIRED = ("id", "area", "title", "decides", "home", "baseline", "measure", "landingZone")

errors = []


def err(msg):
    errors.append(f"dimensions.yaml: {msg}")


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


known = set()
for path in (ROOT / "references").glob("*.yaml"):
    ref = load(path)
    known.add(f"ref:{ref.get('id')}")
    known.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
known.update(f"obs:{p.stem}" for p in (ROOT / "observations").glob("*.yaml"))
known.update(f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README")

register = json.loads((ROOT / "contracts" / "fact-register.json").read_text(encoding="utf-8"))
facts = {f["id"] for f in register["facts"]}
decisions = {d["id"] for d in register["decisions"]}
checks = {c["id"] for c in json.loads((ROOT / "method.json").read_text(encoding="utf-8")).get("checks", [])}

doc = load(PATH)
if doc.get("schema") != "avd-assess-dimensions/v1":
    err("schema must be avd-assess-dimensions/v1")
lz = doc.get("landingZone") or {}
if not re.fullmatch(r"[0-9a-f]{40}", str(lz.get("commit", ""))):
    err("landingZone.commit must be a 40-character commit")
params = lz.get("parameters") or []
if len(params) != len(set(params)):
    err("landingZone.parameters lists a name twice")
not_dims = lz.get("notDimensions") or {}
for name, why in not_dims.items():
    if name not in params:
        err(f"notDimensions names {name}, which isn't a landing zone parameter")
    if not why:
        err(f"notDimensions {name} needs a reason")

used = set()
ids = []
for row in doc.get("dimensions") or []:
    did = row.get("id", "?")
    ids.append(did)
    for key in REQUIRED:
        if key not in row or row[key] in (None, ""):
            err(f"{did}: missing {key}")
    home = row.get("home") or {}
    d = home.get("decision")
    if d and d not in decisions and not PROPOSED.match(d):
        err(f"{did}: decision {d} isn't in the fact register and isn't proposed:")
    for f in (home.get("facts") or []) + (home.get("intake") or []):
        if f not in facts and not PROPOSED.match(f):
            err(f"{did}: fact {f} isn't in the fact register and isn't proposed:")
    for c in home.get("checks") or []:
        if c not in checks:
            err(f"{did}: check {c} isn't in method.json")
    base = row.get("baseline") or {}
    standing = base.get("standing")
    if standing not in STANDINGS:
        err(f"{did}: standing must be one of {sorted(STANDINGS)}")
    claims = base.get("claims") or []
    for c in claims + (row.get("observations") or []):
        if c not in known:
            err(f"{did}: cites {c}, which doesn't exist")
    if not base.get("says"):
        err(f"{did}: baseline needs says")
    if standing == "owned" and not str(row.get("seeAlso", "")).startswith("https://"):
        err(f"{did}: an owned baseline needs a seeAlso link to the method that owns it")
    if standing == "gap" and not any(c.startswith("gap:") for c in claims):
        err(f"{did}: a gap baseline must cite a gap")
    if standing in {"published", "prior"} and not any(c.startswith("ref:") for c in claims):
        err(f"{did}: a {standing} baseline must cite a ref: claim")
    if row.get("measure") not in MEASURES:
        err(f"{did}: measure must be one of {sorted(MEASURES)}")
    for p in row.get("landingZone") or []:
        if p not in params:
            err(f"{did}: landing zone parameter {p} isn't in landingZone.parameters")
        if p in not_dims:
            err(f"{did}: {p} is also listed in notDimensions")
        used.add(p)

for dup in {i for i in ids if ids.count(i) > 1}:
    err(f"dimension {dup} is listed twice")
for p in params:
    if p not in used and p not in not_dims:
        err(f"landing zone parameter {p} has no dimension and no reason in notDimensions")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
gaps = sum(1 for r in doc["dimensions"] if r["baseline"]["standing"] == "gap")
print(f"RESULT PASS ({len(ids)} dimensions, {gaps} gaps, {len(params)} landing zone parameters with a home)")
