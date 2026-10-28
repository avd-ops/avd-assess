#!/usr/bin/env python3
"""Checks a copy of the avd-assess map against its release manifest (datapackage.json, profile
avd-assess-bundle/v1): the manifest's own hash, its shape, every wanted file's size and SHA-256,
each document's schema string, and, when the jsonschema package is installed, each document against
its JSON Schema. Standard library only (Python 3.9+); it never touches the network.

  python3 -I avd_assess_bundle.py <bundle dir>
  python3 -I avd_assess_bundle.py <dir> --manifest vendor/datapackage.json --manifest-sha256 <hex> \\
      --path-map map.json=vendor/map.json --path-map method.json=assess/method.json

With a path map, the wanted files are the mapped ones (a consumer vendors a subset in its own layout);
without one, every file in the manifest under <dir>. Prints RESULT PASS|WARN|FAIL lines and stops at the
first FAIL. Exit 0: all passed; 2: passed, but something was not checked (schemas); 1: failed.

Run it only after the bundle's attestation is checked (gh attestation verify), or use the copy you
already vendor: a tampered bundle must not vouch for itself (docs/distribution-spec.md section 9).

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROFILE = "avd-assess-bundle/v1"
# The schema strings this verifier was written for, by name and the majors it reads. A document whose
# name is here with another major is a FAIL; a name not here is a new document, which readers ignore.
KNOWN = {
    "avd-assess-index": {1}, "avd-assess-method": {1}, "avd-assess-map": {1},
    "avd-assess-security-review": {1}, "avd-assess-endpoints": {1}, "avd-assess-evidence": {1},
    "avd-fact-register": {1}, "avd-run-use-cases": {1}, "avd-current-state-facts": {1},
    "avd-intake": {1}, "avd-assessment": {1}, "avd-assessment-review": {1},
    "avd-remediation-plan": {1}, "avd-benchmark-result": {1}, "avd-run-record": {1}, "avd-run-cost": {1},
    "avd-run-journal": {1}, "avd-assess-bundle": {1},
}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?$")
HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_STRING = re.compile(r"^([a-z0-9-]+)/v([1-9]\d*)$")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def bad_path(p):
    """Why a manifest path is unsafe, or None: relative, forward slashes, no '..' or empty segment."""
    if not isinstance(p, str) or not p:
        return "not a string"
    if p.startswith("/") or "\\" in p or ":" in p:
        return "absolute, drive or backslash"
    if any(seg in ("", ".", "..") for seg in p.split("/")):
        return "empty, '.' or '..' segment"
    return None


def profile_errors(m):
    """The manifest's shape (contracts/schemas/assess-bundle.schema.json), checked with no library."""
    errs = []
    if not isinstance(m, dict):
        return ["the manifest is not a JSON object"]
    for key, kind in (("$schema", str), ("name", str), ("version", str), ("created", str),
                      ("licenses", list), ("resources", list), ("avdAssess", dict)):
        if not isinstance(m.get(key), kind):
            errs.append(f"{key} missing or not a {kind.__name__}")
    if errs:
        return errs
    if m["name"] != "avd-assess":
        errs.append("name is not avd-assess")
    if not SEMVER.match(m["version"]):
        errs.append(f"version {m['version']!r} is not semantic")
    a = m["avdAssess"]
    if a.get("profile") != PROFILE:
        errs.append(f"avdAssess.profile is {a.get('profile')!r}, not {PROFILE}")
    if not isinstance(a.get("commit"), str) or not COMMIT.match(a["commit"]):
        errs.append("avdAssess.commit is not 40 hex")
    if "tag" in a and (not isinstance(a["tag"], str) or a["tag"] != "v" + m["version"]):
        errs.append("avdAssess.tag is not v<version>")
    names, paths = set(), set()
    listed = {r.get("path") for r in m["resources"] if isinstance(r, dict)}
    for i, r in enumerate(m["resources"]):
        where = f"resources[{i}]"
        if not isinstance(r, dict):
            errs.append(f"{where} is not an object")
            continue
        if not isinstance(r.get("name"), str) or not NAME.match(r["name"]):
            errs.append(f"{where}.name missing or not lower case")
        elif r["name"] in names:
            errs.append(f"{where}.name {r['name']} is not unique")
        names.add(r.get("name"))
        why = bad_path(r.get("path"))
        if why:
            errs.append(f"{where}.path {r.get('path')!r}: {why}")
        elif r["path"] in paths:
            errs.append(f"{where}.path {r['path']} is listed twice")
        paths.add(r.get("path"))
        if not isinstance(r.get("bytes"), int) or isinstance(r.get("bytes"), bool) or r["bytes"] < 0:
            errs.append(f"{where}.bytes missing or not a whole number")
        if not isinstance(r.get("hash"), str) or not HASH.match(r["hash"]):
            errs.append(f"{where}.hash is not sha256:<64 lower-case hex>")
        if "jsonSchema" in r and bad_path(r["jsonSchema"]):
            errs.append(f"{where}.jsonSchema {r['jsonSchema']!r}: {bad_path(r['jsonSchema'])}")
        if "jsonSchema" in r and not bad_path(r["jsonSchema"]) and r["jsonSchema"] not in listed:
            errs.append(f"{where}.jsonSchema {r['jsonSchema']} is not a resource, so its hash is not checked")
        if "schemaString" in r and (not isinstance(r["schemaString"], str) or not SCHEMA_STRING.match(r["schemaString"])):
            errs.append(f"{where}.schemaString is not <name>/v<major>")
        if "idPaths" in r and (not isinstance(r["idPaths"], list)
                               or not all(isinstance(p, str) and p.startswith("/") for p in r["idPaths"])):
            errs.append(f"{where}.idPaths is not a list of JSON pointers")
    return errs


def parse_known(values):
    if not values:
        return {k: set(v) for k, v in KNOWN.items()}
    known = {}
    for v in values:
        m = SCHEMA_STRING.match(v)
        if not m:
            raise ValueError(f"--known-schema {v!r} is not <name>/v<major>")
        known.setdefault(m.group(1), set()).add(int(m.group(2)))
    return known


def check_bundle(root, manifest=None, manifest_sha256=None, resources=None, path_map=None, known=None,
                 validate=True):
    """Yields (status, check id, detail) for each check, in order, stopping after the first FAIL.

    root: the folder relative paths resolve against. manifest: the datapackage.json path (default
    root/datapackage.json). path_map: {bundle path: local path}, local paths relative to root.
    resources: wanted resource names (default: the mapped paths, or every resource)."""
    root = Path(root)
    # A relative manifest path is relative to root, as in the PowerShell module.
    mpath = (root / manifest if not Path(manifest).is_absolute() else Path(manifest)) if manifest else root / "datapackage.json"
    try:
        raw = mpath.read_bytes()
    except OSError as e:
        yield ("FAIL", "manifest-read", f"{mpath}: {e.strerror or e}")
        return
    got = sha256(raw)
    if manifest_sha256:
        if got != manifest_sha256.lower():
            yield ("FAIL", "manifest-pin", f"datapackage.json is {got}, the pin says {manifest_sha256.lower()}")
            return
        yield ("PASS", "manifest-pin", f"datapackage.json matches the pin {got}")
    try:
        m = json.loads(raw.decode("utf-8"))
    except ValueError as e:
        yield ("FAIL", "manifest-profile", f"datapackage.json is not JSON ({e})")
        return
    errs = profile_errors(m)
    if errs:
        yield ("FAIL", "manifest-profile", "; ".join(errs[:5]))
        return
    yield ("PASS", "manifest-profile", f"{PROFILE}, version {m['version']}, commit {m['avdAssess']['commit'][:12]}, "
                                       f"{len(m['resources'])} resources")

    by_name = {r["name"]: r for r in m["resources"]}
    by_path = {r["path"]: r for r in m["resources"]}
    path_map = dict(path_map or {})
    for p in path_map:
        if p not in by_path:
            yield ("FAIL", "resource-wanted", f"path map names {p}, which is not in the manifest")
            return
    if resources:
        missing = [n for n in resources if n not in by_name]
        if missing:
            yield ("FAIL", "resource-wanted", f"not in the manifest: {', '.join(missing)}")
            return
        wanted = [by_name[n] for n in resources]
    elif path_map:
        wanted = [by_path[p] for p in sorted(path_map)]
    else:
        wanted = list(m["resources"])

    def local(path):
        return root / path_map.get(path, path)

    data = {}
    for r in wanted:
        f = local(r["path"])
        try:
            b = f.read_bytes()
        except OSError:
            yield ("FAIL", "resource-hash", f"{r['path']}: missing (looked for {f})")
            return
        if len(b) != r["bytes"]:
            yield ("FAIL", "resource-hash", f"{r['path']}: {len(b)} bytes, the manifest says {r['bytes']}")
            return
        if "sha256:" + sha256(b) != r["hash"]:
            yield ("FAIL", "resource-hash", f"{r['path']}: SHA-256 differs from the manifest")
            return
        data[r["path"]] = b
    yield ("PASS", "resource-hash", f"{len(wanted)} files match their size and SHA-256")

    known = known if known is not None else parse_known(None)
    untyped = [r["path"] for r in wanted if r["path"].endswith((".json", ".jsonl")) and r.get("format") not in ("json", "jsonl")]
    if untyped:
        yield ("WARN", "resource-format", f"not parsed or schema-checked, the manifest gives no json format: {', '.join(untyped[:5])}")
    docs = {}
    for r in wanted:
        fmt = r.get("format")
        if fmt not in ("json", "jsonl"):
            continue
        try:
            text = data[r["path"]].decode("utf-8")
            items = [json.loads(line) for line in text.splitlines() if line.strip()] if fmt == "jsonl" else [json.loads(text)]
        except ValueError as e:
            yield ("FAIL", "resource-schema-string", f"{r['path']}: not {fmt} ({e})")
            return
        if fmt == "json":
            top = items[0].get("schema") if isinstance(items[0], dict) else None
            declared = r.get("schemaString")
            if isinstance(top, str) and top != declared:
                yield ("FAIL", "resource-schema-string", f"{r['path']}: says {top!r}, the manifest says {declared!r}")
                return
            if declared and top is None:
                yield ("FAIL", "resource-schema-string", f"{r['path']}: has no schema string, the manifest says {declared!r}")
                return
            if declared:
                name, major = SCHEMA_STRING.match(declared).groups()
                if name in known and int(major) not in known[name]:
                    yield ("FAIL", "resource-schema-string",
                           f"{r['path']}: {declared} is a major this reader does not know ({name} v{sorted(known[name])})")
                    return
        docs[r["path"]] = items
    yield ("PASS", "resource-schema-string", f"{len(docs)} JSON files parse; every schema string matches the manifest")

    if not validate:
        return
    with_schema = [r for r in wanted if r.get("jsonSchema") and r["path"] in docs]
    if not with_schema:
        return
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        yield ("WARN", "resource-schema", f"schemas not checked for {len(with_schema)} files: the jsonschema package is not installed")
        return
    checked, unchecked = 0, []
    for r in with_schema:
        sf = local(r["jsonSchema"])
        try:
            schema = json.loads(sf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            unchecked.append(r["path"])
            continue
        if r["jsonSchema"] in by_path and "sha256:" + sha256(sf.read_bytes()) != by_path[r["jsonSchema"]]["hash"]:
            yield ("FAIL", "resource-schema", f"{r['jsonSchema']}: SHA-256 differs from the manifest")
            return
        v = Draft202012Validator(schema)
        for n, item in enumerate(docs[r["path"]], 1):
            e = next(iter(sorted(v.iter_errors(item), key=lambda e: list(e.path))), None)
            if e is not None:
                where = f"line {n} " if r.get("format") == "jsonl" else ""
                yield ("FAIL", "resource-schema", f"{r['path']}: {where}/{'/'.join(map(str, e.path))}: {e.message[:160]}")
                return
        checked += 1
    if unchecked:
        yield ("WARN", "resource-schema", f"schemas not available locally for: {', '.join(unchecked)}")
    yield ("PASS", "resource-schema", f"{checked} files valid against their JSON Schema")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", help="bundle folder (or the folder path-map entries are relative to)")
    ap.add_argument("--manifest", help="datapackage.json, if not at <root>/datapackage.json")
    ap.add_argument("--manifest-sha256", help="the pin: SHA-256 of datapackage.json")
    ap.add_argument("--resource", action="append", help="check only this resource name (repeatable)")
    ap.add_argument("--path-map", action="append", default=[], metavar="BUNDLE=LOCAL",
                    help="where a bundle path is held locally (repeatable)")
    ap.add_argument("--path-map-file", help="JSON object {bundle path: local path}")
    ap.add_argument("--known-schema", action="append", help="a schema string this reader knows, such as avd-assess-map/v1")
    a = ap.parse_args(argv)
    pm = {}
    if a.path_map_file:
        pm.update(json.loads(Path(a.path_map_file).read_text(encoding="utf-8")))
    for item in a.path_map:
        k, sep, v = item.partition("=")
        if not sep:
            ap.error(f"--path-map {item!r} is not BUNDLE=LOCAL")
        pm[k] = v
    try:
        known = parse_known(a.known_schema)
    except ValueError as e:
        ap.error(str(e))
    worst = 0
    for status, cid, detail in check_bundle(a.root, a.manifest, a.manifest_sha256, a.resource, pm, known):
        print(f"RESULT {status} {cid}: {detail}")
        worst = max(worst, {"PASS": 0, "WARN": 2, "FAIL": 3}[status])
    return {0: 0, 2: 2, 3: 1}[worst]


if __name__ == "__main__":
    sys.exit(main())
