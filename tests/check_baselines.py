#!/usr/bin/env python3
"""Checks the baseline profiles (baselines.yaml, gap:baseline-profile): every value has a rule or target,
claims that exist and a known standing; a baseline cites a gap; every class has its density and sizes.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "baselines.yaml"
STANDINGS = {"published", "prior", "guidance", "baseline"}
BANDS = {"under", "good", "watch", "over", "idle"}
CLASSES = {"light", "medium", "heavy", "power"}

errors = []


def err(msg):
    errors.append(f"baselines.yaml: {msg}")


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


known = set()
for path in (ROOT / "references").glob("*.yaml"):
    ref = load(path)
    known.add(f"ref:{ref.get('id')}")
    known.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
known.update(f"obs:{p.stem}" for p in (ROOT / "observations").glob("*.yaml"))
known.update(f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README")


def check_value(where, item, text_key):
    if not item.get(text_key):
        err(f"{where}: missing {text_key}")
    claims = item.get("claims") or []
    if not claims:
        err(f"{where}: cites nothing")
    for c in claims:
        if c not in known:
            err(f"{where}: cites {c}, which doesn't exist")
    standing = item.get("standing")
    if standing not in STANDINGS:
        err(f"{where}: standing must be one of {sorted(STANDINGS)}")
    if standing == "baseline" and not any(str(c).startswith("gap:") for c in claims):
        err(f"{where}: a baseline must cite the gap that sets it")
    if standing in {"published", "prior"} and not any(str(c).startswith("ref:") for c in claims):
        err(f"{where}: {standing} needs a ref: claim")


doc = load(PATH)
if doc.get("schema") != "avd-assess-baselines/v1":
    err("schema must be avd-assess-baselines/v1")
for item in doc.get("window") or []:
    check_value(f"window {item.get('id')}", item, "rule")
for item in doc.get("experience") or []:
    check_value(f"experience {item.get('metric')}", item, "target")
for metric in doc.get("utilization") or []:
    for band in metric.get("bands") or []:
        if band.get("band") not in BANDS:
            err(f"utilization {metric.get('metric')}: unknown band {band.get('band')!r}")
        check_value(f"utilization {metric.get('metric')}.{band.get('band')}", band, "rule")
for i, item in enumerate(doc.get("host") or []):
    check_value(f"host rule {i + 1}", item, "rule")
seen = set()
for cls in doc.get("classes") or []:
    cid = cls.get("id")
    if cid in seen:
        err(f"class {cid} is listed twice")
    seen.add(cid)
    multi = cls.get("multiSession") or {}
    for key in ("usersPerVcpuMax", "minVcpu", "minMemoryGiB", "osDiskGiB"):
        if not isinstance(multi.get(key), (int, float)):
            err(f"class {cid}: multiSession.{key} must be a number")
    check_value(f"class {cid}", cls, "id")
if seen != CLASSES:
    err(f"classes must be exactly {sorted(CLASSES)}, found {sorted(seen)}")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(seen)} classes)")
