#!/usr/bin/env python3
"""Checks the baseline profiles (baselines.yaml, gap:baseline-profile) and the benchmark profile
catalog (benchmarks/profiles.yaml, gap:workload-benchmark): every value has a rule or target,
claims that exist and a known standing; a baseline cites a gap; every class has its density and sizes;
every benchmark profile has a semantic version, tier, harness, metrics and valid citations.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "baselines.yaml"
BENCHMARKS_PATH = ROOT / "benchmarks" / "profiles.yaml"
STANDINGS = {"published", "prior", "guidance", "baseline"}
BANDS = {"under", "good", "watch", "over", "idle"}
CLASSES = {"light", "medium", "heavy", "power"}
TIERS = {"synthetic", "observational"}
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")

errors = []


def err(msg):
    errors.append(f"baselines.yaml: {msg}")


def berr(msg):
    errors.append(f"benchmarks/profiles.yaml: {msg}")


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

bdoc = load(BENCHMARKS_PATH) if BENCHMARKS_PATH.exists() else {}
if bdoc.get("schema") != "avd-assess-benchmarks/v1":
    berr("schema must be avd-assess-benchmarks/v1")
profiles = bdoc.get("profiles") or []
seen_profiles = set()
for prof in profiles:
    pid = prof.get("id")
    if not pid:
        berr("profile missing id")
        continue
    if pid in seen_profiles:
        berr(f"profile {pid} is listed twice")
    seen_profiles.add(pid)
    if not SEMVER.match(str(prof.get("version", ""))):
        berr(f"profile {pid}: version {prof.get('version')!r} is not semantic")
    if prof.get("tier") not in TIERS:
        berr(f"profile {pid}: tier must be one of {sorted(TIERS)}")
    for key in ("title", "summary", "harness", "metrics", "claims"):
        if not prof.get(key):
            berr(f"profile {pid}: missing {key}")
    for c in (prof.get("claims") or []) + (prof.get("observations") or []):
        if c not in known:
            berr(f"profile {pid}: cites {c}, which doesn't exist")

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
    bp = cls.get("benchmarkProfile")
    if bp and bp not in seen_profiles:
        err(f"class {cid}: benchmarkProfile {bp!r} isn't in benchmarks/profiles.yaml")
    check_value(f"class {cid}", cls, "id")
if seen != CLASSES:
    err(f"classes must be exactly {sorted(CLASSES)}, found {sorted(seen)}")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(seen)} classes, {len(seen_profiles)} benchmark profiles)")
