#!/usr/bin/env python3
"""Checks the method: references, observations, gaps, the method pages and the gold-standard registry.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VERDICTS = {"agrees", "disagrees", "extends", "not-yet-tested"}
KINDS = {"published", "prior", "guidance"}
AREAS = {"collection", "assessment", "benchmarks", "scoring"}
METHODS = ["collection", "assessment", "targets-benchmarks", "scoring", "sample-check"]
STANDINGS = {"candidate", "gold", "baseline", "demoted"}
CITE = re.compile(r"`((?:ref|obs|gap):[A-Za-z0-9._:#-]+)`")
GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PIN = re.compile(r"(/(?:blob|tree)/[0-9a-f]{40}(?:/|$)|^Learn git_commit_id [0-9a-f]{40}, updated_at \d{4}-\d{2}-\d{2}$)")

errors = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def load(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        err(path, f"not valid YAML ({e})")
        return {}


claims = set()
for path in sorted((ROOT / "references").glob("*.yaml")):
    ref = load(path)
    rid = ref.get("id")
    if rid != path.stem:
        err(path, f"id {rid!r} must match the file name")
    for key in ("title", "url", "pin", "read", "license", "areas", "claims"):
        if not ref.get(key):
            err(path, f"missing {key}")
    if ref.get("pin") and not PIN.search(str(ref["pin"])):
        err(path, "pin must be a GitHub blob or tree URL at a 40-character commit, or 'Learn git_commit_id <sha>, updated_at <date>'")
    for area in ref.get("areas") or []:
        if area not in AREAS:
            err(path, f"unknown area {area!r}")
    claims.add(f"ref:{rid}")
    for c in ref.get("claims") or []:
        if not c.get("id") or not c.get("says"):
            err(path, "every claim needs an id and says")
            continue
        if c.get("kind") and c["kind"] not in KINDS:
            err(path, f"claim {c['id']}: unknown kind {c['kind']!r}")
        claims.add(f"ref:{rid}#{c['id']}")

observations = set()
observation_data = []
for path in sorted((ROOT / "observations").glob("*.yaml")):
    obs = load(path)
    observation_data.append(obs)
    if obs.get("id") != path.stem:
        err(path, "id must match the file name")
    observations.add(f"obs:{path.stem}")
    if obs.get("claim") not in claims:
        err(path, f"claim {obs.get('claim')!r} is not in references/")
    if obs.get("verdict") not in VERDICTS:
        err(path, f"verdict must be one of {sorted(VERDICTS)}")
    if not obs.get("observed") or not obs.get("date"):
        err(path, "needs observed and date")
    if obs.get("verdict") != "not-yet-tested" and not obs.get("evidence"):
        err(path, "a verdict other than not-yet-tested needs evidence")
    for link in obs.get("evidence") or []:
        if not str(link).startswith("https://"):
            err(path, f"evidence must be an https link: {link}")

gaps = {f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README"}
for path in sorted((ROOT / "gaps").glob("*.md")):
    if path.stem != "README" and "**Searched" not in path.read_text(encoding="utf-8"):
        err(path, "a gap must say what was searched and not found")

known = claims | observations | gaps


def check_cites(path, text):
    for cite in CITE.findall(text):
        if cite not in known:
            err(path, f"cites {cite}, which doesn't exist")


for name in METHODS:
    path = ROOT / "methods" / f"{name}.md"
    if not path.exists():
        err(ROOT / "methods", f"missing {name}.md")
        continue
    text = path.read_text(encoding="utf-8")
    check_cites(path, text)
    section = text.split("## Method", 1)[-1].split("\n## ", 1)[0]
    steps = [line for line in section.splitlines() if re.match(r"^\d+\. ", line)]
    if not steps:
        err(path, "has no numbered steps under ## Method")
    for step in steps:
        if not CITE.search(step):
            err(path, f"step cites no ref:, obs: or gap: -> {step[:60]}")

for path in sorted((ROOT / "gaps").glob("*.md")):
    check_cites(path, path.read_text(encoding="utf-8"))

registry = ROOT / "gold-standards.yaml"
entries = load(registry).get("entries") or []
all_metrics = {e.get("metric") for e in entries}
metrics = set()
for entry in entries:
    metric = entry.get("metric")
    if not metric or metric in metrics:
        err(registry, f"every entry needs a unique metric ({metric!r})")
    metrics.add(metric)
    for key in ("claim", "standing", "since", "why"):
        if not entry.get(key):
            err(registry, f"{metric}: missing {key}")
    standing = entry.get("standing")
    if standing not in STANDINGS:
        err(registry, f"{metric}: standing must be one of {sorted(STANDINGS)}")
    claim = entry.get("claim")
    if claim not in known:
        err(registry, f"{metric}: claim {claim!r} doesn't exist")
    if standing in {"candidate", "gold"} and not str(claim).startswith("ref:"):
        err(registry, f"{metric}: a {standing} must cite a ref: claim")
    if standing == "baseline" and not str(claim).startswith("gap:"):
        err(registry, f"{metric}: a baseline must cite the gap that sets it")
    if standing == "gold":
        backing = [o for o in observation_data if o.get("claim") == claim]
        if not any(o.get("verdict") in {"agrees", "extends"} for o in backing):
            err(registry, f"{metric}: gold needs an agrees or extends observation on {claim}")
        if any(o.get("verdict") == "disagrees" for o in backing):
            err(registry, f"{metric}: gold can't stand with a disagrees observation on {claim}")
    if entry.get("replaces") and entry["replaces"] not in all_metrics:
        err(registry, f"{metric}: replaces {entry['replaces']!r}, which isn't in the registry")

public_ids = {
    line.strip().lower()
    for line in (ROOT / "tests" / "public-ids.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
}
for path in sorted(ROOT.rglob("*")):
    if not path.is_file() or ".git" in path.parts or path.name == "public-ids.txt" or path.suffix not in {".md", ".yaml", ".yml", ".py", ".txt"}:
        continue
    text = path.read_text(encoding="utf-8")
    for g in GUID.findall(text):
        if g.lower() not in public_ids:
            err(path, f"GUID {g[:4]}*** isn't a listed public ID")
    for e in EMAIL.findall(text):
        err(path, f"looks like an email address ({e[:3]}***)")
    for ip in IPV4.findall(text):
        err(path, f"looks like an IP address ({ip.split('.')[0]}.***)")
    if any(ord(ch) > 127 for ch in text):
        err(path, "non-ASCII character")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print(f"RESULT PASS ({len(claims)} claims, {len(observations)} observations, {len(gaps)} gaps)")
