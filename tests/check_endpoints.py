#!/usr/bin/env python3
"""Checks the endpoint map (endpoints.yaml, gap:endpoint-map): every row cites a list whose claim exists
in references/ with an immutable Learn pin, the map was read at the pin each cited reference now carries
(lists and notes alike), no row restates an address, only concrete names are probed, a browser probes
only HTTPS on 443, every claim a note cites exists, and endpoints.json passes its schema (contract C20, avd-assess-endpoints/v1).

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
LEARN_PIN = re.compile(r"^Learn git_commit_id ([0-9a-f]{40}), updated_at \d{4}-\d{2}-\d{2}$")
IPV4 = re.compile(r"(?<![\d.])\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?(?![\d.])")
CITE = re.compile(r"ref:[a-z0-9-]+#[a-z0-9-]+")

errors = []


def err(msg):
    errors.append(f"endpoints.yaml: {msg}")


doc = yaml.safe_load((ROOT / "endpoints.yaml").read_text(encoding="utf-8")) or {}

refs, claims = {}, set()
for path in (ROOT / "references").glob("*.yaml"):
    ref = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    refs[ref.get("id")] = ref
    claims.update(f"ref:{ref.get('id')}#{c['id']}" for c in ref.get("claims") or [] if c.get("id"))
dimensions = {d["id"] for d in (yaml.safe_load((ROOT / "dimensions.yaml").read_text(encoding="utf-8")) or {})
              .get("dimensions", [])}

# readAt: the map was read at the pin each reference carries now, so a moved pin means a re-read.
read_at = doc.get("readAt") or {}
for ref_id, commit in read_at.items():
    pin = LEARN_PIN.match(str(refs.get(ref_id, {}).get("pin", "")))
    if not pin:
        err(f"readAt {ref_id}: the reference is missing or has no Learn git_commit_id pin")
    elif pin.group(1) != commit:
        err(f"readAt {ref_id} is {commit[:7]} but the reference is pinned at {pin.group(1)[:7]}; "
            "re-read the page and update the rows, then readAt")

lists = {}
for lst in doc.get("lists") or []:
    lid, claim = lst.get("id"), lst.get("claim", "")
    lists[lid] = lst
    if claim not in claims:
        err(f"list {lid}: claim {claim} is not in references/")
    ref_id = claim.removeprefix("ref:").split("#")[0]
    if not LEARN_PIN.match(str(refs.get(ref_id, {}).get("pin", ""))):
        err(f"list {lid}: {ref_id} has no immutable Learn pin")
    if ref_id not in read_at:
        err(f"list {lid}: readAt has no entry for {ref_id}")
    if lst.get("dimension") not in dimensions:
        err(f"list {lid}: dimension {lst.get('dimension')} is not a row in dimensions.yaml")

seen, cited = set(), {lst.get("claim", "").removeprefix("ref:").split("#")[0] for lst in lists.values()}
for e in doc.get("endpoints") or []:
    eid, kind, host = e.get("id", "?"), e.get("kind"), e.get("host", "")
    if eid in seen:
        err(f"{eid} is listed twice")
    seen.add(eid)
    if e.get("list") not in lists:
        err(f"{eid}: list {e.get('list')} is not defined")
    elif not eid.startswith(f"{e['list']}."):
        err(f"{eid}: the id must start with its list ({e['list']}.)")
    if IPV4.search(json.dumps(e)):
        err(f"{eid}: restates an address; name the service tag or cite the page instead")
    if kind in ("fqdn", "wildcard") and not host:
        err(f"{eid}: a {kind} row needs host")
    if kind in ("range", "address") and host:
        err(f"{eid}: a {kind} row has no host (addresses stay on the cited page)")
    if (kind == "wildcard") != host.startswith("*."):
        err(f"{eid}: kind {kind} doesn't match host {host!r}")
    probe = e.get("probeFrom") or []
    if kind != "fqdn" and probe:
        err(f"{eid}: a {kind} row is never probed from the map; probeFrom must be empty")
    if "browser" in probe and (e.get("protocol"), e.get("port")) != ("tcp", 443):
        err(f"{eid}: a browser can probe only HTTPS on TCP 443")
    for cite in CITE.findall(e.get("note", "")):
        cited.add(cite.removeprefix("ref:").split("#")[0])
        if cite not in claims:
            err(f"{eid}: note cites {cite}, which is not in references/")

# Every page a note cites is read at a pin too, and readAt names no page nothing cites.
for ref_id in sorted(cited - set(read_at)):
    err(f"readAt has no entry for {ref_id}, which a note cites")
for ref_id in sorted(set(read_at) - cited):
    err(f"readAt names {ref_id}, which no list or note cites")

schema = json.loads((ROOT / "contracts" / "schemas" / "assess-endpoints.schema.json").read_text(encoding="utf-8"))
built = json.loads((ROOT / "endpoints.json").read_text(encoding="utf-8"))
for e in sorted(Draft202012Validator(schema).iter_errors(built), key=lambda e: list(e.path))[:5]:
    errors.append(f"endpoints.json: {'/'.join(map(str, e.path))}: {e.message[:120]}")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} problems)")
    sys.exit(1)
print(f"RESULT PASS ({len(seen)} endpoints in {len(lists)} lists, read at {len(read_at)} pins)")
