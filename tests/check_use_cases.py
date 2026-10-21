#!/usr/bin/env python3
"""Checks the use case library (use-cases.yaml, gap:use-case-library): every entry uses the use case
record's enums, cites claims that exist, names a real baseline class, fact register decisions and dimension
rows, and every move it suggests points at an entry that exists.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "use-cases.yaml"
STANDINGS = {"published", "prior", "guidance", "baseline"}
KINDS = {"persona", "overlay"}
# The record's fields and values, as gap:use-cases proposes them for C19.
RECORD = {
    "function": {"task", "knowledge", "developer", "creative", "engineering", "frontline", "external", "admin", "other"},
    "workload": {"light", "medium", "heavy", "power"},
    "gpu": {"none", "required", "unknown"},
    "desktop": {"pooled", "personal", "either"},
    "dedicatedBecause": {"security", "compliance", "performance", "noisy-neighbor", "app-compatibility", "admin-rights"},
    "delivery": {"desktop", "remoteapp", "both"},
    "apps.installed": {"yes", "no", "unknown"},
    "apps.m365": {"yes", "no", "unknown"},
    "apps.multiSession": {"yes", "no", "unknown"},
    "apps.backend": {"none", "azure", "on-premises", "saas", "unknown"},
    "trustBoundary": {"one-org-standard", "needs-admin", "multi-org"},
    "dataControls": {"clipboard-restricted", "drives-off", "printing-restricted", "screen-capture-protection", "watermarking", "none"},
    "criticality": {"standard", "business-critical", "mission-critical"},
}
LISTS = {"dedicatedBecause", "dataControls"}
PATTERN = {
    "hours": {"office", "shifts", "follow-the-sun", "seasonal"},
    "media": {"none", "teams", "web-calls", "video"},
    "endpoints": {"managed", "unmanaged", "any"},
}

errors = []


def err(msg):
    errors.append(f"use-cases.yaml: {msg}")


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


known = set()
for path in (ROOT / "references").glob("*.yaml"):
    ref = load(path)
    known.add(f"ref:{ref.get('id')}")
    known.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
known.update(f"obs:{p.stem}" for p in (ROOT / "observations").glob("*.yaml"))
known.update(f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README")
classes = {c.get("id") for c in load(ROOT / "baselines.yaml").get("classes") or []}
decisions = {d["id"] for d in json.loads((ROOT / "contracts" / "fact-register.json").read_text(encoding="utf-8"))["decisions"]}
dimensions = {d.get("id") for d in load(ROOT / "dimensions.yaml").get("dimensions") or []}


def check_claims(where, claims):
    if not claims:
        err(f"{where}: cites nothing")
    for c in claims or []:
        if c not in known:
            err(f"{where}: cites {c}, which doesn't exist")


def check_standing(where, item):
    standing = item.get("standing")
    claims = item.get("claims") or []
    if standing not in STANDINGS:
        err(f"{where}: standing must be one of {sorted(STANDINGS)}")
    if standing == "baseline" and not any(str(c).startswith("gap:") for c in claims):
        err(f"{where}: a baseline must cite the gap that sets it")
    if standing in {"published", "prior"} and not any(str(c).startswith("ref:") for c in claims):
        err(f"{where}: {standing} needs a ref: claim")


doc = load(PATH)
if doc.get("schema") != "avd-assess-use-cases/v1":
    err("schema must be avd-assess-use-cases/v1")
entries = doc.get("entries") or []
ids = [e.get("id") for e in entries]
for dup in {i for i in ids if ids.count(i) > 1}:
    err(f"entry {dup} is listed twice")

for e in entries:
    eid, kind = e.get("id"), e.get("kind")
    where = f"entry {eid}"
    for key in ("title", "summary"):
        if not e.get(key):
            err(f"{where}: missing {key}")
    if kind not in KINDS:
        err(f"{where}: kind must be one of {sorted(KINDS)}")
    starts = e.get("starts") or {}
    pattern = e.get("pattern") or {}
    for field, value in starts.items():
        if field not in RECORD:
            err(f"{where}: starts.{field} isn't a use case record field")
            continue
        values = value if field in LISTS else [value]
        if field in LISTS and not isinstance(value, list):
            err(f"{where}: starts.{field} must be a list")
            values = []
        for v in values:
            if str(v) not in RECORD[field]:
                err(f"{where}: starts.{field} {v!r} isn't one of {sorted(RECORD[field])}")
    for field, value in pattern.items():
        if field not in PATTERN or value not in PATTERN[field]:
            err(f"{where}: pattern.{field} {value!r} isn't a known pattern value")
    covered = set()
    for i, why in enumerate(e.get("why") or []):
        for field in why.get("sets") or []:
            if field not in starts and not (field.startswith("pattern.") and field[8:] in pattern):
                err(f"{where}: why {i + 1} sets {field}, which the entry doesn't set")
            covered.add(field)
        check_claims(f"{where} why {i + 1}", why.get("claims"))
        check_standing(f"{where} why {i + 1}", why)
    if not e.get("why"):
        err(f"{where}: needs at least one why")
    if kind == "persona":
        for field in ("function", "workload"):
            if field not in starts:
                err(f"{where}: a persona sets starts.{field}")
            elif field not in covered:
                err(f"{where}: starts.{field} needs a why")
        if e.get("profile") not in classes:
            err(f"{where}: profile must be a baselines.yaml class {sorted(classes)}")
        elif e.get("profile") != starts.get("workload"):
            err(f"{where}: profile {e.get('profile')} doesn't match starts.workload {starts.get('workload')}")
    if kind == "overlay":
        for field in ("function", "workload"):
            if field in starts:
                err(f"{where}: an overlay doesn't set {field}")
        if e.get("profile"):
            err(f"{where}: an overlay has no profile")
    for i, t in enumerate(e.get("tighten") or []):
        if not t.get("rule"):
            err(f"{where} tighten {i + 1}: missing rule")
        check_claims(f"{where} tighten {i + 1}", t.get("claims"))
        check_standing(f"{where} tighten {i + 1}", t)
    if not e.get("risks"):
        err(f"{where}: needs at least one risk")
    for i, r in enumerate(e.get("risks") or []):
        if not r.get("risk"):
            err(f"{where} risk {i + 1}: missing risk")
        check_claims(f"{where} risk {i + 1}", r.get("claims"))
    for i, b in enumerate(e.get("breaks") or []):
        if not b.get("if"):
            err(f"{where} break {i + 1}: missing if")
        if bool(b.get("to")) == bool(b.get("then")):
            err(f"{where} break {i + 1}: needs exactly one of to or then")
        if b.get("to") and b["to"] not in ids:
            err(f"{where} break {i + 1}: to {b['to']}, which isn't an entry")
        if b.get("to") == eid:
            err(f"{where} break {i + 1}: points at itself")
        check_claims(f"{where} break {i + 1}", b.get("claims"))
    for d in e.get("decisions") or []:
        if d not in decisions:
            err(f"{where}: decision {d} isn't in the fact register")
    for d in e.get("dimensions") or []:
        if d not in dimensions:
            err(f"{where}: dimension {d} isn't in dimensions.yaml")
    if not e.get("decisions") or not e.get("dimensions"):
        err(f"{where}: needs decisions and dimensions")

personas = sum(1 for e in entries if e.get("kind") == "persona")
if not personas:
    err("needs at least one persona")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({personas} personas, {len(entries) - personas} overlays)")
