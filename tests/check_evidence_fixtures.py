#!/usr/bin/env python3
"""Proves the evidence check (scripts/check_evidence.py) passes the good fixtures and refuses each bad one.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_evidence  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "evidence"
errors = []
for path in sorted((FIXTURES / "good").glob("*.json")):
    for p in check_evidence.check(path):
        errors.append(f"good/{path.name} should pass: {p}")
bad = sorted((FIXTURES / "bad").glob("*.json"))
for path in bad:
    if not check_evidence.check(path):
        errors.append(f"bad/{path.name} should be refused but passed")
# A GUID can't sit in a committed fixture (the repo's own leak check refuses it), so build that case here.
with tempfile.TemporaryDirectory() as tmp:
    doc = json.loads((FIXTURES / "bad" / "2026-10-21-domain-in-note.json").read_text(encoding="utf-8"))
    doc["id"] = "2026-10-21-guid-in-note"
    doc["metrics"][0]["note"] = "sub " + "-".join(["0" * 8, "1" * 4, "2" * 4, "3" * 4, "4" * 12])
    path = Path(tmp) / f"{doc['id']}.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    bad.append(path)
    if not any("GUID" in p for p in check_evidence.check(path)):
        errors.append("a GUID in a note should be refused")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(bad)} bad submissions refused)")
