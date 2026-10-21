#!/usr/bin/env python3
"""Checks the foundation contracts held in contracts/: schemas, examples and the fact register.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
SCHEMAS = CONTRACTS / "schemas"

# Each example and the schema it must pass. A .jsonl example is checked line by line.
EXAMPLES = {
    "examples/assess/index.example.json": "assess-index.schema.json",
    "examples/assess/method.example.json": "assess-method.schema.json",
    "examples/assess/map.example.json": "assess-map.schema.json",
    "examples/assess/endpoints.example.json": "assess-endpoints.schema.json",
    "examples/assess/intake.example.json": "intake.schema.json",
    "examples/assess/assessment.example.json": "assessment.schema.json",
    "examples/assess/review.example.json": "assessment-review.schema.json",
    "examples/assess/plan.example.json": "remediation-plan.schema.json",
    "examples/checks/catalog.example.json": "check-catalog.schema.json",
    "examples/run-record/run.example.json": "run-record.schema.json",
    "examples/run-record/cost.example.json": "run-cost.schema.json",
    "examples/run-record/journal.example.jsonl": "run-journal.schema.json",
}
# The contract each built fact's path resolves in.
SCHEMA_BY_CONTRACT = {"C11": "current-state-facts.schema.json", "C19": "intake.schema.json"}
# Tiers the foundation produces, and the ID prefix each needs. Upstream tiers are optional:
# their facts may sit in the register, and a foundation tool ignores what it doesn't produce.
PREFIX = {"azure": "c11.", "forensic": "c12.", "intake": "intake.", "liquidware": "liquidware."}

errors = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        err(path, f"not readable JSON ({e})")
        return None


def report(path, validator, doc, where=""):
    for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))[:5]:
        err(path, f"{where}{'/'.join(map(str, e.path))}: {e.message[:120]}")


schemas = {}
for path in sorted(SCHEMAS.glob("*.schema.json")):
    schema = load(path)
    if schema is None:
        continue
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:  # SchemaError carries the reason
        err(path, f"not a valid JSON Schema 2020-12 ({str(e).splitlines()[0][:120]})")
        continue
    schemas[path.name] = schema

for rel, schema_name in EXAMPLES.items():
    path = CONTRACTS / rel
    if schema_name not in schemas:
        err(path, f"its schema {schema_name} is missing")
        continue
    validator = Draft202012Validator(schemas[schema_name])
    if path.suffix == ".jsonl":
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                report(path, validator, json.loads(line), f"line {n}: ")
    else:
        doc = load(path)
        if doc is not None:
            report(path, validator, doc)
for path in sorted((CONTRACTS / "examples").rglob("*.json*")):
    if str(path.relative_to(CONTRACTS)) not in EXAMPLES:
        err(path, "example isn't listed in tests/check_contracts.py, so nothing checks it")

# C22: unique check IDs, and the shapes the schema must refuse (the oneOf and the method rule).
catalog_schema = schemas.get("check-catalog.schema.json")
if catalog_schema:
    cv = Draft202012Validator(catalog_schema)
    catalog_path = CONTRACTS / "examples/checks/catalog.example.json"
    catalog = load(catalog_path)
    if catalog is not None:
        ids = [c["id"] for c in catalog.get("checks", [])]
        if len(ids) != len(set(ids)):
            err(catalog_path, "a check ID appears more than once")
        base = {"id": "sample-check", "title": "A sample check", "phase": ["drift"], "gate": "advise",
                "pillar": "operations", "severity": "low", "claims": ["gap:governance-scope"]}
        for bad in ({"reads": ["arm"]},
                    {"reads": ["arm"], "impl": "Get-SampleResult", "source": "method"},
                    {"impl": "Get-SampleResult"},
                    {"source": "method"},
                    {"id": "asm-sample-check", "source": "method", "facts": ["c11.hostPool.count"]}):
            doc = json.loads(json.dumps(catalog))
            doc["checks"][0] = {**base, **bad}
            if cv.is_valid(doc):
                err(catalog_path, f"the C22 schema accepts a check it must refuse: {bad}")


# C23: one decision per check, and a reason that fits its disposition (the schema's allOf).
review_schema = schemas.get("assessment-review.schema.json")
if review_schema:
    rv = Draft202012Validator(review_schema)
    review_path = CONTRACTS / "examples/assess/review.example.json"
    review = load(review_path)
    if review is not None:
        seen = [d["check"] for d in review.get("decisions", [])]
        if len(seen) != len(set(seen)):
            err(review_path, "a check has more than one decision")
        for bad in ({"disposition": "fix", "reason": "cost"}, {"disposition": "accept", "reason": "later-phase"},
                    {"disposition": "defer", "reason": "fix-planned"}, {"disposition": "fix", "reason": "fix-planned", "reviewBy": "2027-01-01"},
                    {"disposition": "accept", "reason": "cost", "note": "free text"}):
            doc = json.loads(json.dumps(review))
            doc["decisions"][0] = {"check": "asm-sample-check", "outcome": "warn", **bad}
            if rv.is_valid(doc):
                err(review_path, f"the C23 schema accepts a decision it must refuse: {bad}")


# C24: one item per check, orders 1..n, and a change shaped by its kind (the schema's allOf).
plan_schema = schemas.get("remediation-plan.schema.json")
if plan_schema:
    pv = Draft202012Validator(plan_schema)
    plan_path = CONTRACTS / "examples/assess/plan.example.json"
    plan = load(plan_path)
    if plan is not None:
        items = plan.get("items", [])
        checks = [i["check"] for i in items]
        if len(checks) != len(set(checks)):
            err(plan_path, "a check has more than one item")
        if sorted(i["order"] for i in items) != list(range(1, len(items) + 1)):
            err(plan_path, "orders must run 1, 2, 3 ... with no gaps or repeats")
        # The order rule (methods/remediation.md step 6): outcome, then severity, then check ID.
        rank = {"gap": 0, "warn": 1, "unknown": 2, "high": 0, "medium": 1, "low": 2}
        by_rule = sorted(items, key=lambda i: (rank[i["outcome"]], rank[i["severity"]], i["check"]))
        if [i["check"] for i in by_rule] != [i["check"] for i in sorted(items, key=lambda i: i["order"])]:
            err(plan_path, "items aren't in rule order: gap, warn, unknown; then high, medium, low; then check ID")
        for bad in ({"kind": "manual"}, {"kind": "manual", "code": "process", "name": "startVmOnConnect"},
                    {"kind": "lz-parameter", "to": True}, {"kind": "lz-parameter", "name": "x", "code": "process"},
                    {"kind": "lz-setting", "name": "trusted-launch", "to": True},
                    {"kind": "lz-parameter", "name": "spokeAddressPrefix", "to": "subnet/22"},
                    {"kind": "lz-parameter", "name": "dnsServer", "to": ".".join(["10", "20", "30", "4"])},
                    {"kind": "lz-parameter", "name": "resourceGroup", "to": "contoso-avd-rg"},
                    {"kind": "manual", "code": "process", "note": "free text"}):
            doc = json.loads(json.dumps(plan))
            doc["items"][0]["change"] = bad
            if pv.is_valid(doc):
                err(plan_path, f"the C24 schema accepts a change it must refuse: {bad}")
        doc = json.loads(json.dumps(plan))
        doc["items"][0]["outcome"] = "pass"
        if pv.is_valid(doc):
            err(plan_path, "the C24 schema accepts an item for a passing check")
        doc = json.loads(json.dumps(plan))
        doc["items"][0]["outcome"] = "unknown"
        if pv.is_valid(doc):
            err(plan_path, "the C24 schema accepts a fix for an unknown outcome (it must plan collect-evidence)")
    # C20's remediation hint and C24's change share their values and codes; keep the copies equal.
    method_schema = schemas.get("assess-method.schema.json", {})
    hint = method_schema.get("$defs", {}).get("remediation", {}).get("properties", {})
    change = plan_schema["properties"]["items"]["items"]["properties"]["change"]["properties"]
    for key in ("kind", "name", "code"):
        if hint.get(key) != change.get(key):
            err(SCHEMAS / "remediation-plan.schema.json", f"change.{key} differs from assess-method's remediation.{key}")
    if method_schema.get("$defs", {}).get("publicValue") != plan_schema["$defs"]["publicValue"]:
        err(SCHEMAS / "remediation-plan.schema.json", "publicValue differs from assess-method's")


def schema_has(schema, pointer):
    """True when a JSON pointer (with * for every array item) names a property the schema
    defines. Follows local $ref and steps into allOf branches (same rule as the brain's
    Test-SchemaPath)."""
    node = schema
    for seg in pointer.strip("/").split("/"):
        for _ in range(10):
            ref = node.get("$ref") if isinstance(node, dict) else None
            if not ref:
                break
            node = schema
            for r in ref.lstrip("#/").split("/"):
                node = node.get(r, {}) if isinstance(node, dict) else {}
        if not isinstance(node, dict):
            return False
        if seg == "*":
            node = node.get("items")
        else:
            nxt = (node.get("properties") or {}).get(seg)
            if nxt is None:
                for branch in node.get("allOf") or []:
                    nxt = (branch.get("properties") or {}).get(seg)
                    if nxt is not None:
                        break
            node = nxt
        if node is None:
            return False
    return True


# Contract C15: the fact register (the brain's Test-FactRegister rules, ported).
rpath = CONTRACTS / "fact-register.json"
register = load(rpath)
if register is not None and "fact-register.schema.json" in schemas:
    report(rpath, Draft202012Validator(schemas["fact-register.schema.json"]), register)
    decisions = [d["id"] for d in register.get("decisions", [])]
    for d in {d for d in decisions if decisions.count(d) > 1}:
        err(rpath, f"decision {d!r} is listed twice")
    ids = [f["id"] for f in register.get("facts", [])]
    for f in {f for f in ids if ids.count(f) > 1}:
        err(rpath, f"fact {f!r} is listed twice")
    for f in register.get("facts", []):
        prefix = PREFIX.get(f.get("tier"))
        if prefix and not f["id"].startswith(prefix):
            err(rpath, f"fact {f['id']!r} is tier {f['tier']}; its ID must start with {prefix!r}")
        for e in f.get("evidences") or []:
            if e not in decisions:
                err(rpath, f"fact {f['id']!r} evidences {e!r}, which isn't a decision in the register")
        if f.get("status") == "proposed" and f.get("evidences"):
            err(rpath, f"fact {f['id']!r} is proposed; it can't evidence a decision until it is specified")
        if f.get("status") != "built":
            continue
        schema_name = SCHEMA_BY_CONTRACT.get(f.get("contract"))
        if not f.get("contract") or not f.get("path"):
            err(rpath, f"fact {f['id']!r} is built but names no contract and path")
        elif not schema_name or schema_name not in schemas:
            err(rpath, f"fact {f['id']!r} is built, but there is no schema here for {f['contract']}")
        elif not schema_has(schemas[schema_name], f["path"]):
            err(rpath, f"fact {f['id']!r}: {f['path']} isn't in the {f['contract']} schema")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(schemas)} schemas, {len(EXAMPLES)} examples, {len(register['facts'])} facts)")
