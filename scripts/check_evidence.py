#!/usr/bin/env python3
"""Checks evidence submissions (evidence/*.json and evidence/*/*.json, avd-assess-evidence/v1 or
avd-benchmark-result/v1 C25, gap:evidence-intake and gap:workload-benchmark) before they are merged:
the schema, the privacy rules, and that every metric, profile, claim and observation exists. Anyone
runs the same check on their own file before submitting, and CI runs it on every pull request.

  python3 scripts/check_evidence.py                      # every file in evidence/
  python3 scripts/check_evidence.py my-submission.json   # one file, before you submit it

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
SCHEMA = json.loads((EVIDENCE / "schema.json").read_text(encoding="utf-8"))
BENCHMARK_SCHEMA = json.loads((ROOT / "contracts" / "schemas" / "benchmark-result.schema.json").read_text(encoding="utf-8"))

# Metrics the baselines measure that have no registry entry yet; each says where its baseline lives.
EXTRA_METRICS = {
    "memory-per-user": "gap:baseline-profile",
    "users-per-gpu": "gap:deployment-dimensions",
    "measured-density": "gap:baseline-profile",
    "sessions-per-host-peak": "gap:baseline-profile",
    "time-to-connect": "gap:logon-target",
}

GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
DOMAIN = re.compile(r"\b[a-z0-9-]+\.(?:com|net|org|io|local|corp|internal|lan|onmicrosoft)\b", re.IGNORECASE)


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def known_claims():
    known = set()
    for path in (ROOT / "references").glob("*.yaml"):
        ref = load_yaml(path)
        known.add(f"ref:{ref.get('id')}")
        known.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
    known.update(f"gap:{p.stem}" for p in (ROOT / "gaps").glob("*.md") if p.stem != "README")
    return known


def known_observations():
    return {f"obs:{p.stem}" for p in (ROOT / "observations").glob("*.yaml")}


def known_profiles():
    profiles_path = ROOT / "benchmarks" / "profiles.yaml"
    if not profiles_path.exists():
        return set()
    return {p["id"] for p in (load_yaml(profiles_path).get("profiles") or []) if p.get("id")}


def registry():
    entries = load_yaml(ROOT / "gold-standards.yaml").get("entries") or []
    return {e["metric"]: e["claim"] for e in entries if e.get("metric")}


def check(path, known=None, metrics=None, observations=None, profiles=None):
    """Returns the problems with one submission; an empty list means it passes."""
    known = known if known is not None else known_claims()
    metrics = metrics if metrics is not None else {**EXTRA_METRICS, **registry()}
    observations = observations if observations is not None else known_observations()
    profiles = profiles if profiles is not None else known_profiles()
    problems = []
    raw = path.read_text(encoding="utf-8")
    if any(ord(ch) > 127 for ch in raw):
        problems.append("non-ASCII character")
    for name, pattern in (("a GUID", GUID), ("an email address", EMAIL), ("an IP address", IPV4), ("a domain", DOMAIN)):
        if pattern.search(raw):
            problems.append(f"contains what looks like {name}")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as e:
        return problems + [f"not valid JSON ({e.msg})"]
    schema_str = doc.get("schema") if isinstance(doc, dict) else None
    active_schema = BENCHMARK_SCHEMA if schema_str == "avd-benchmark-result/v1" else SCHEMA
    for e in sorted(Draft202012Validator(active_schema, format_checker=FormatChecker()).iter_errors(doc), key=lambda e: list(e.path))[:8]:
        where = "/".join(map(str, e.path)) or "(top)"
        problems.append(f"{where}: {e.message[:120]}")
    if problems:
        return problems
    if doc["id"] != path.stem:
        problems.append(f"id {doc['id']!r} must match the file name")
    if schema_str == "avd-benchmark-result/v1":
        if doc["source"] == "estate" and doc.get("consent") is not True:
            problems.append("an estate submission needs consent: true (the owner agreed to share these aggregates)")
        pid = doc["profile"]["id"]
        if profiles and pid not in profiles:
            problems.append(f"profile {pid!r} isn't in benchmarks/profiles.yaml")
        for item in doc["verdict"]["claims"]:
            c = item["claim"]
            if c not in known:
                problems.append(f"verdict claim {c!r} doesn't exist")
            obs = item.get("observation")
            if obs and obs not in observations:
                problems.append(f"verdict observation {obs!r} doesn't exist")
        return problems
    scope = doc["scope"]
    if doc["source"] == "estate":
        if doc.get("consent") is not True:
            problems.append("an estate submission needs consent: true (the owner agreed to share these aggregates)")
        # Any size may submit; a real estate gives its size as bands, never exact counts (gap:evidence-intake).
        for exact, band in (("hosts", "hostsBand"), ("users", "usersBand")):
            if exact in scope:
                problems.append(f"an estate submission gives {band}, not the exact {exact}")
            if band not in scope:
                problems.append(f"an estate submission needs {band}")
    elif "hosts" not in scope:
        problems.append("a sandbox or lab submission needs hosts")
    for m in doc["metrics"]:
        name = m["metric"]
        if name not in metrics:
            problems.append(f"metric {name!r} isn't in the gold-standard registry or the checker's list")
            continue
        claim = m.get("claim", metrics[name])
        if claim not in known:
            problems.append(f"metric {name}: claim {claim!r} doesn't exist")
        if m["verdict"] != "not-yet-tested" and not any(k in m for k in ("p50", "p95", "p99")):
            problems.append(f"metric {name}: a verdict needs at least one of p50, p95 or p99")
    return problems


def main(argv):
    paths = [Path(a) for a in argv] or sorted(p for p in EVIDENCE.rglob("*.json") if p.name != "schema.json")
    known, metrics = known_claims(), {**EXTRA_METRICS, **registry()}
    observations, profiles = known_observations(), known_profiles()
    failed = 0
    for path in paths:
        problems = check(path, known, metrics, observations, profiles)
        for p in problems:
            print(f"{path.name}: {p}")
        failed += bool(problems)
    if failed:
        print(f"RESULT FAIL ({failed} of {len(paths)} submissions)")
        return 1
    print(f"RESULT PASS ({len(paths)} submissions)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
