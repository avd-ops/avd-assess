#!/usr/bin/env python3
"""Runs every check a pull request runs, in order, and fails if any fails. check.yml and release.yml both
call it, so a check added here runs at every release tag too (docs/distribution-spec.md section 7).

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = [
    ["scripts/build_index.py", "--check"],
    ["tests/check_method.py"],
    ["tests/check_contracts.py"],
    ["tests/check_dimensions.py"],
    ["tests/check_baselines.py"],
    ["tests/check_use_cases.py"],
    ["scripts/check_evidence.py"],
    ["tests/check_evidence_fixtures.py"],
    ["tests/check_evidence_issue.py"],
    ["tests/check_endpoints.py"],
    ["tests/check_wording.py"],
    ["tests/check_security_review.py"],
    ["tests/check_bundle.py"],
]

failed = []
for args in CHECKS:
    print(f"== {' '.join(args)}", flush=True)
    if subprocess.run([sys.executable, *args], cwd=ROOT).returncode:
        failed.append(args[0])
if failed:
    print(f"RESULT FAIL {', '.join(failed)}")
    sys.exit(1)
print(f"RESULT PASS all {len(CHECKS)} checks")
