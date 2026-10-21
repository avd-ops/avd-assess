#!/usr/bin/env python3
"""Checks the security review map (security-review.yaml and its generated security-review.json): the
JSON passes its schema, IDs are unique, every cross-link resolves (claims, operator items, pillars,
ref/obs/gap citations), avd-assess evidence exists here, and no claim is stronger than its evidence:
run needs a lesson or run record, guarded a test or CI job, built some code.

With --family-root DIR (a folder holding checkouts of the other repos, such as the parent folder),
it also checks that every other repo's evidence path exists at its pinned commit and that a #L<n>
anchor is within the file. CI has no such checkouts, so it checks the shape only.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
REPOS = {"avd-landing-zone", "avd-current-state", "avd-assess", "avd-second-brain", "avd-swarm", "avd-ops"}
NEEDS = {"run": {"lesson", "run"}, "guarded": {"test", "ci"}, "built": {"code", "test", "ci"}}

errors = []


def err(msg):
    errors.append(f"security-review.yaml: {msg}")


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


doc = load(ROOT / "security-review.yaml")
schema = json.loads((ROOT / "contracts/schemas/assess-security-review.schema.json").read_text(encoding="utf-8"))
built = json.loads((ROOT / "security-review.json").read_text(encoding="utf-8"))
for e in Draft202012Validator(schema).iter_errors(built):
    err(f"security-review.json {'/'.join(map(str, e.absolute_path))}: {e.message}")

known = set()
for path in (ROOT / "references").glob("*.yaml"):
    ref = load(path)
    known.add(f"ref:{ref.get('id')}")
    known.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
known.update(f"obs:{p.stem}" for p in (ROOT / "observations").glob("*.yaml"))
known.update(f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README")
pillars = {p["id"] for p in load(ROOT / "pillars.yaml").get("pillars", [])}

pins = doc.get("pins", {})
if set(doc.get("maturity", {}).get("repos", {})) != REPOS:
    err("maturity.repos must name each of the six public repos once")
std = doc.get("standards", {})
if not (ROOT / std.get("method", "")).is_file():
    err(f"standards.method {std.get('method')!r} is not a file here")
for cite in [std.get("scope"), *std.get("references", [])]:
    if cite and cite not in known:
        err(f"standards cites {cite!r}, which does not exist")
for p in std.get("pillars", []):
    if p not in pillars:
        err(f"standards names pillar {p!r}, not in pillars.yaml")

evidence = []
claims = {}
for area in doc.get("areas", []):
    for p in area.get("pillars", []):
        if p not in pillars:
            err(f"area {area['id']} names pillar {p!r}, not in pillars.yaml")
    for c in area.get("claims", []):
        if c["id"] in claims:
            err(f"claim {c['id']} appears twice")
        claims[c["id"]] = c
        kinds = {e["kind"] for e in c.get("evidence", [])}
        need = NEEDS.get(c.get("standing"))
        if need and not kinds & need:
            err(f"claim {c['id']} says {c['standing']} but has no {' or '.join(sorted(need))} evidence")
        evidence += [(c["id"], e) for e in c.get("evidence", [])]
evidence.append(("maturity", doc["maturity"]["source"]))
evidence += [(f"threat {t['repo']}", t["formal"]) for t in doc.get("threats", []) if isinstance(t.get("formal"), dict)]

ops = {o["id"] for o in doc.get("operator", [])}
if ops & set(claims):
    err(f"operator IDs reuse claim IDs: {sorted(ops & set(claims))}")
targets = set(claims) | ops | known


def check_links(where, items):
    for s in items:
        if s not in targets:
            err(f"{where} points at {s!r}, which is no claim, operator item or citation")


for o in doc.get("operator", []):
    check_links(f"operator {o['id']}", o.get("see", []))
for q in doc.get("checklist", []):
    check_links(f"checklist {q['id']}", q.get("see", []))
for t in doc.get("threats", []):
    check_links(f"threat {t['repo']}", t.get("limits", []))
covered = {s for q in doc.get("checklist", []) for s in q.get("see", [])}
for cid in sorted(set(claims) | ops):
    if cid not in covered:
        err(f"{cid} is not reached from any checklist question")

for owner, ev in evidence:
    repo, (path, _, anchor) = ev["repo"], ev["path"].partition("#")
    if repo == "avd-assess":
        if not (ROOT / path).is_file():
            err(f"{owner}: {path} is not a file here")
    elif repo not in pins:
        err(f"{owner}: {repo} has no pin")

family = sys.argv[sys.argv.index("--family-root") + 1] if "--family-root" in sys.argv else None
if family:
    for owner, ev in evidence:
        repo, (path, _, anchor) = ev["repo"], ev["path"].partition("#")
        if repo == "avd-assess":
            continue
        out = subprocess.run(["git", "-C", str(Path(family) / repo), "show", f"{pins[repo]}:{path}"],
                             capture_output=True, text=True)
        if out.returncode:
            err(f"{owner}: {repo}@{pins[repo][:7]}:{path} not found ({out.stderr.strip()[:80]})")
            continue
        m = re.fullmatch(r"L(\d+)", anchor)
        if m and int(m.group(1)) > out.stdout.count("\n") + 1:
            err(f"{owner}: {repo}:{path} has no line {m.group(1)}")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL {len(errors)} problem(s) in the security review map")
    sys.exit(1)
print(f"RESULT PASS security review map: {len(claims)} claims, {len(ops)} operator items, "
      f"{len(doc.get('gaps', []))} gaps" + (", every pinned path found" if family else ""))
