#!/usr/bin/env python3
"""Writes the shared verifier fixtures in this folder (one small bundle per case) and cases.json, which
both tests/check_bundle.py and tests/AvdAssessBundle.Tests.ps1 read, so the Python and PowerShell
verifiers are held to the same expectations. --check fails when the committed fixtures are stale.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMIT = "0123456789abcdef0123456789abcdef01234567"
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://assess.avd-ops.dev/schemas/test-fixture-map/v1.json",
    "type": "object",
    "required": ["schema", "pillars"],
    "properties": {
        "schema": {"const": "avd-assess-map/v1"},
        "pillars": {"type": "array", "items": {"type": "object", "required": ["id"],
                                               "properties": {"id": {"type": "string"}}}},
    },
}


def dump(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def manifest(files, version="1.0.0", meta=None, override=None):
    """A datapackage.json for {path: bytes}; meta adds per-path resource fields, override replaces some."""
    resources = []
    for p in sorted(files):
        b = files[p]
        fmt = p.rsplit(".", 1)[-1]
        r = {"name": p.lower().replace("/", "-").replace(".", "-"), "path": p, "format": fmt, "bytes": len(b),
             "hash": "sha256:" + hashlib.sha256(b).hexdigest()}
        if fmt == "json":
            doc = json.loads(b)
            if isinstance(doc, dict) and isinstance(doc.get("schema"), str):
                r["schemaString"] = doc["schema"]
                r["jsonSchema"] = "schemas/map.schema.json"
        r.update((meta or {}).get(p, {}))
        r.update((override or {}).get(p, {}))
        resources.append(r)
    return dump({"$schema": "https://datapackage.org/profiles/2.0/datapackage.json", "name": "avd-assess",
                 "version": version, "created": "2026-10-21T00:00:00+00:00",
                 "licenses": [{"name": "MIT", "path": "LICENSE"}],
                 "avdAssess": {"commit": COMMIT, "profile": "avd-assess-bundle/v1"}, "resources": resources})


def write_bundle(d, files, version="1.0.0", meta=None, override=None, manifest_bytes=None):
    d = Path(d)
    for p, b in files.items():
        (d / p).parent.mkdir(parents=True, exist_ok=True)
        (d / p).write_bytes(b)
    (d / "datapackage.json").write_bytes(manifest_bytes or manifest(files, version, meta, override))


def base_files():
    return {
        "LICENSE": b"MIT\n",
        "map.json": dump({"schema": "avd-assess-map/v1", "pillars": [{"id": "identity"}, {"id": "network"}]}),
        "notes.md": b"# Notes\n",
        "schemas/map.schema.json": dump(SCHEMA),
    }


def build(out):
    out = Path(out)
    cases = []

    def case(name, expect, why, args=None):
        cases.append({"case": name, "expect": expect, "why": why, **({"args": args} if args else {})})

    write_bundle(out / "good", base_files())
    case("good", "PASS", "a whole bundle: every check passes")
    good_manifest = (out / "good" / "datapackage.json").read_bytes()
    case("good", "manifest-pin", "the manifest's SHA-256 is not the pin",
         {"manifestSha256": "0" * 64})
    case("good", "PASS", "the pin matches", {"manifestSha256": hashlib.sha256(good_manifest).hexdigest()})

    f = base_files()
    write_bundle(out / "changed-byte", f, manifest_bytes=good_manifest)
    (out / "changed-byte" / "map.json").write_bytes(f["map.json"].replace(b"identity", b"identitY"))
    case("changed-byte", "resource-hash", "one byte of map.json changed, same size")

    write_bundle(out / "missing-file", base_files(), manifest_bytes=good_manifest)
    (out / "missing-file" / "notes.md").unlink()
    case("missing-file", "resource-hash", "notes.md is in the manifest but not on disk")

    write_bundle(out / "bad-hash", base_files(), override={"notes.md": {"hash": "sha256:NOT-HEX"}})
    case("bad-hash", "manifest-profile", "a resource hash is not sha256:<64 hex>")

    write_bundle(out / "dotdot", base_files(), override={"notes.md": {"path": "../notes.md"}})
    case("dotdot", "manifest-profile", "a resource path climbs out of the bundle")

    write_bundle(out / "schema-unlisted", base_files(), override={"map.json": {"jsonSchema": "other/map.schema.json"}})
    case("schema-unlisted", "manifest-profile", "a document names a schema file the manifest doesn't hash")

    f = base_files()
    f["map.json"] = dump({"schema": "avd-assess-map/v2", "pillars": [{"id": "identity"}]})
    write_bundle(out / "unknown-major", f)
    case("unknown-major", "resource-schema-string", "map.json is avd-assess-map/v2, a major the reader doesn't know")

    f = base_files()
    f["map.json"] = dump({"schema": "avd-assess-map/v1", "pillars": [{"id": 7}]})
    write_bundle(out / "schema-invalid", f)
    case("schema-invalid", "resource-schema", "a pillar id is a number; the schema wants a string")

    # A consumer's own layout: the manifest and two files under vendor/, map.json renamed.
    f = base_files()
    d = out / "path-map"
    (d / "vendor").mkdir(parents=True)
    (d / "vendor" / "datapackage.json").write_bytes(good_manifest)
    (d / "vendor" / "assess-map.json").write_bytes(f["map.json"])
    (d / "vendor" / "map.schema.json").write_bytes(f["schemas/map.schema.json"])
    case("path-map", "PASS", "a subset in the consumer's layout, through a path map",
         {"manifest": "vendor/datapackage.json",
          "pathMap": {"map.json": "vendor/assess-map.json", "schemas/map.schema.json": "vendor/map.schema.json"}})
    case("path-map", "resource-wanted", "the path map names a file the manifest doesn't list",
         {"manifest": "vendor/datapackage.json", "pathMap": {"other.json": "vendor/assess-map.json"}})

    (out / "cases.json").write_bytes(dump({"description": "Shared verifier fixtures; written by make_fixtures.py. "
                                           "expect is PASS (no FAIL) or the id of the first FAIL.", "cases": cases}))


def main():
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            stale = []
            for p in sorted(Path(tmp).rglob("*")):
                if p.is_file():
                    rel = p.relative_to(tmp)
                    if not (HERE / rel).exists() or (HERE / rel).read_bytes() != p.read_bytes():
                        stale.append(str(rel))
            known = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts} - {"make_fixtures.py"}
            ours = {str(p.relative_to(tmp)) for p in Path(tmp).rglob("*") if p.is_file()}
            stale += sorted(known - ours)
        if stale:
            print(f"RESULT FAIL bundle fixtures stale: {', '.join(stale)}; run python3 {Path(__file__).relative_to(HERE.parents[2])}")
            return 1
        print("RESULT PASS bundle fixtures are current")
        return 0
    for p in HERE.iterdir():
        if p.is_dir():
            shutil.rmtree(p)
    build(HERE)
    print(f"Wrote fixtures in {HERE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
