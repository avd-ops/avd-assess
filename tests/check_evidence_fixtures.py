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

    # Verify IPv6, generic domain, and extensions.generator (euc-score-byo) checks on C25
    c25_sample = next((ROOT / "evidence").rglob("bm-*.json"))
    base_c25 = json.loads(c25_sample.read_text(encoding="utf-8"))

    good_euc = json.loads(json.dumps(base_c25))
    good_euc["extensions"] = {
        "generator": {
            "kind": "euc-score-byo",
            "version": "1.0.0",
            "persona": "knowledge-worker",
            "licenseSelfDeclared": "community-public-results",
            "exportSha256": "a" * 64,
        }
    }
    good_path = Path(tmp) / f"{good_euc['id']}.json"
    good_path.write_text(json.dumps(good_euc), encoding="utf-8")
    for p in check_evidence.check(good_path):
        errors.append(f"valid euc-score-byo C25 should pass: {p}")

    bad_gen = json.loads(json.dumps(good_euc))
    bad_gen["extensions"]["generator"]["licenseSelfDeclared"] = "enterprise"
    bad_gen_path = Path(tmp) / f"{bad_gen['id']}.json"
    bad_gen_path.write_text(json.dumps(bad_gen), encoding="utf-8")
    bad.append(bad_gen_path)
    if not any("licenseSelfDeclared" in p for p in check_evidence.check(bad_gen_path)):
        errors.append("non-community licenseSelfDeclared should be refused")

    bad_ipv6 = json.loads(json.dumps(base_c25))
    bad_ipv6["extensions"] = {"note": "2001:db8::1"}
    ipv6_path = Path(tmp) / f"{bad_ipv6['id']}.json"
    ipv6_path.write_text(json.dumps(bad_ipv6), encoding="utf-8")
    bad.append(ipv6_path)
    if not any("IPv6" in p for p in check_evidence.check(ipv6_path)):
        errors.append("an IPv6 address should be refused")

    bad_dom = json.loads(json.dumps(base_c25))
    bad_dom["extensions"] = {"note": "host01.acme.co.uk"}
    dom_path = Path(tmp) / f"{bad_dom['id']}.json"
    dom_path.write_text(json.dumps(bad_dom), encoding="utf-8")
    bad.append(dom_path)
    if not any("domain" in p for p in check_evidence.check(dom_path)):
        errors.append("a generic domain should be refused")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(bad)} bad submissions refused)")
