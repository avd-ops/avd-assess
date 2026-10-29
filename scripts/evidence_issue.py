#!/usr/bin/env python3
"""Turns an accepted "Baseline evidence" issue into a pull request (gap:evidence-intake, step 4). When a
maintainer adds the accepted label to an evidence issue, .github/workflows/evidence-intake.yml runs this:
it takes the JSON file from the issue form, refuses anything scripts/check_evidence.py refuses, and writes
evidence/<id>.json for the workflow to commit. Issue text is untrusted: it is only parsed as JSON and
written under a name the schema's id pattern allows; nothing merges without a person reviewing the PR.

  python3 scripts/evidence_issue.py --event "$GITHUB_EVENT_PATH" --body-file pr-body.md

Writes branch= and title= to $GITHUB_OUTPUT. On a refusal it writes the reason to evidence-error.txt
and exits 1, so the workflow can tell the submitter what to fix.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_evidence  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FILE_HEADING = "The checked evidence file"
SOURCE_HEADING = "Source"
ID = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]{3,48}$")  # evidence/schema.json, id


class Refused(Exception):
    pass


def section(body, heading):
    """The text under one '### heading' of a GitHub issue form, or None."""
    m = re.search(rf"^###\s+{re.escape(heading)}\s*$(.*?)(?=^###\s|\Z)", body or "", re.M | re.S)
    return m.group(1).strip() if m else None


def evidence_from_issue(body):
    """The submitted document and the form's Source answer; Refused when the form isn't usable."""
    text = section(body, FILE_HEADING)
    if not text:
        raise Refused(f'the issue has no "{FILE_HEADING}" section')
    fenced = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n?```", text, re.S)
    raw = fenced.group(1) if fenced else text
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as e:
        raise Refused(f"the evidence file isn't valid JSON ({e.msg}, line {e.lineno})") from None
    if not isinstance(doc, dict):
        raise Refused("the evidence file must be one JSON object")
    return doc, (section(body, SOURCE_HEADING) or "").strip()


def write_evidence(doc, source, evidence_dir):
    """Checks the document and writes it to evidence_dir/<id>.json; returns the path."""
    eid = doc.get("id")
    if not isinstance(eid, str) or not ID.fullmatch(eid):
        raise Refused("the file's id must be the submission date plus a short slug, like 2026-10-21-sandbox-light")
    if source and doc.get("source") != source:
        raise Refused(f"the form says source {source!r} but the file says {doc.get('source')!r}")
    path = evidence_dir / f"{eid}.json"
    if path.exists():
        raise Refused(f"evidence/{eid}.json already exists; give the submission a new id")
    # ensure_ascii=False keeps any non-ASCII text visible to the check instead of escaping it.
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    problems = check_evidence.check(path)
    if problems:
        path.unlink()
        raise Refused("scripts/check_evidence.py refused it: " + "; ".join(problems))
    return path


def pr_body(issue, path):
    login = (issue.get("user") or {}).get("login", "unknown")
    return "\n".join([
        f"Adds `{path.name}` from the Baseline evidence issue #{issue['number']}, submitted by `{login}`.",
        "",
        "Opened by the evidence-intake workflow after a maintainer labeled the issue `accepted`. The file",
        "passed `scripts/check_evidence.py`; a person still reviews the numbers and merges",
        "(gap:evidence-intake). PRs opened by the workflow token don't start other workflows: close and",
        "reopen this PR to run CI.",
        "",
        f"Closes #{issue['number']}",
        "",
    ])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--evidence-dir", default=str(ROOT / "evidence"))
    args = ap.parse_args(argv)
    issue = json.loads(Path(args.event).read_text(encoding="utf-8"))["issue"]
    try:
        doc, source = evidence_from_issue(issue.get("body"))
        path = write_evidence(doc, source, Path(args.evidence_dir))
    except Refused as e:
        Path("evidence-error.txt").write_text(str(e), encoding="utf-8")
        print(f"RESULT REFUSED {e}")
        return 1
    Path(args.body_file).write_text(pr_body(issue, path), encoding="utf-8")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"branch=evidence/issue-{issue['number']}\ntitle=Evidence: {doc['id']} (#{issue['number']})\n")
    print(f"RESULT WROTE {path.relative_to(path.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
