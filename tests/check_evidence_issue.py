#!/usr/bin/env python3
"""Proves the evidence intake (scripts/evidence_issue.py) turns a good "Baseline evidence" issue into
evidence/<id>.json with a PR body that closes the issue, and refuses a broken form, a file the evidence
check refuses, a mismatched source, an unsafe id and a duplicate.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_issue  # noqa: E402

GOOD = json.loads((ROOT / "tests" / "fixtures" / "evidence" / "good" / "2026-10-21-sandbox-light-example.json").read_text(encoding="utf-8"))
BAD = json.loads((ROOT / "tests" / "fixtures" / "evidence" / "bad" / "2026-10-21-domain-in-note.json").read_text(encoding="utf-8"))
errors = []


def form(doc, source="sandbox", fence="```json"):
    """An issue body the way GitHub renders the Baseline evidence form."""
    text = doc if isinstance(doc, str) else json.dumps(doc, indent=2)
    return (f"### Source\n\n{source}\n\n### The checked evidence file\n\n{fence}\n{text}\n```\n\n"
            "### Before you submit\n\n- [X] The file passed scripts/check_evidence.py.\n")


def run(body, evidence_dir, number=7):
    event = Path(evidence_dir).parent / "event.json"
    event.write_text(json.dumps({"issue": {"number": number, "body": body, "user": {"login": "someone"}}}), encoding="utf-8")
    pr = Path(evidence_dir).parent / "pr-body.md"
    out = Path(evidence_dir).parent / "output.txt"
    out.write_text("", encoding="utf-8")
    os.environ["GITHUB_OUTPUT"] = str(out)
    code = evidence_issue.main(["--event", str(event), "--body-file", str(pr), "--evidence-dir", str(evidence_dir)])
    return code, pr, out


def expect_refused(name, body, evidence_dir, words):
    before = set(Path(evidence_dir).glob("*.json"))
    cwd = os.getcwd()
    os.chdir(Path(evidence_dir).parent)
    try:
        code, _, _ = run(body, evidence_dir)
        reason = Path("evidence-error.txt").read_text(encoding="utf-8") if code else ""
    finally:
        os.chdir(cwd)
    if code != 1:
        errors.append(f"{name}: should be refused")
    elif words not in reason:
        errors.append(f"{name}: reason {reason!r} should mention {words!r}")
    left = set(Path(evidence_dir).glob("*.json")) - before
    if left:
        errors.append(f"{name}: a refused submission left {sorted(p.name for p in left)} behind")
        for p in left:
            p.unlink()


with tempfile.TemporaryDirectory() as tmp:
    evidence_dir = Path(tmp) / "evidence"
    evidence_dir.mkdir()
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        code, pr, out = run(form(GOOD), evidence_dir)
    finally:
        os.chdir(cwd)
    written = evidence_dir / f"{GOOD['id']}.json"
    if code != 0 or not written.exists():
        errors.append("a good submission should be written to evidence/<id>.json")
    else:
        if json.loads(written.read_text(encoding="utf-8")) != GOOD:
            errors.append("the written file should equal the submitted document")
        if "Closes #7" not in pr.read_text(encoding="utf-8"):
            errors.append("the PR body should close the issue")
        if "branch=evidence/issue-7" not in out.read_text(encoding="utf-8"):
            errors.append("the branch should be named after the issue")
    expect_refused("duplicate id", form(GOOD), evidence_dir, "already exists")
    written.unlink()

    expect_refused("no file section", "### Source\n\nsandbox\n", evidence_dir, "no \"The checked evidence file\"")
    expect_refused("not JSON", form("{ not json"), evidence_dir, "isn't valid JSON")
    expect_refused("not an object", form("[1, 2]"), evidence_dir, "one JSON object")
    expect_refused("evidence check refuses it", form(BAD, source=BAD["source"]), evidence_dir, "check_evidence.py refused it")
    expect_refused("source mismatch", form(GOOD, source="estate"), evidence_dir, "the form says source")
    expect_refused("unsafe id", form({**GOOD, "id": "../../scripts/x"}), evidence_dir, "id must be")
    expect_refused("non-ASCII", form({**GOOD, "metrics": [{**GOOD["metrics"][0], "note": "caf" + chr(233)}]}), evidence_dir, "non-ASCII")
    if evidence_issue.evidence_from_issue(form(GOOD, fence="```"))[0] != GOOD:
        errors.append("a fence without a language should still parse")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print("RESULT PASS (evidence intake: 1 written, 8 refused)")
