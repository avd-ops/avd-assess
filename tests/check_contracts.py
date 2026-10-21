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
    "examples/assess/intake.example.json": "intake.schema.json",
    "examples/assess/assessment.example.json": "assessment.schema.json",
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
