#!/usr/bin/env python3
"""Checks the release tooling offline (docs/distribution-spec.md sections 4 to 8): the Python verifier
against the shared fixtures, diff_bundle's bump rules and deprecation gate, the leak scan, and the
schemas' $id, deprecated field and local-only $refs. The PowerShell verifier runs the same fixtures in
tests/AvdAssessBundle.Tests.ps1; the bundle itself is built by scripts/bundle/build_bundle.py --check.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import contextlib
import copy
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures" / "bundle"
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "scripts" / "bundle"), str(FIX)]
import avd_assess_bundle  # noqa: E402
import build_bundle  # noqa: E402
import diff_bundle  # noqa: E402
import make_fixtures  # noqa: E402

from jsonschema import Draft202012Validator  # noqa: E402

errors = []


def expect(cond, msg):
    if not cond:
        errors.append(msg)


# 1. Fixtures are current, and the Python verifier gives each case its expected first FAIL.
r = subprocess.run([sys.executable, str(FIX / "make_fixtures.py"), "--check"], capture_output=True, text=True)
expect(r.returncode == 0, r.stdout.strip() or r.stderr.strip())
cases = json.loads((FIX / "cases.json").read_text(encoding="utf-8"))["cases"]
for c in cases:
    a = c.get("args", {})
    results = list(avd_assess_bundle.check_bundle(FIX / c["case"], (FIX / c["case"] / a["manifest"]) if "manifest" in a else None,
                                                  a.get("manifestSha256"), None, a.get("pathMap")))
    fails = [cid for status, cid, _ in results if status == "FAIL"]
    got = fails[0] if fails else "PASS"
    expect(got == c["expect"], f"verifier case {c['case']} ({c['why']}): got {got}, want {c['expect']}")
    expect(len(fails) <= 1, f"verifier case {c['case']}: went on after a FAIL")

# The command line: exit codes 0 / 1, and RESULT lines.
with contextlib.redirect_stdout(io.StringIO()) as out:
    code = avd_assess_bundle.main([str(FIX / "good")])
expect(code == 0 and "RESULT PASS resource-hash" in out.getvalue(), f"verifier CLI on good: exit {code}")
with contextlib.redirect_stdout(io.StringIO()):
    code = avd_assess_bundle.main([str(FIX / "changed-byte")])
expect(code == 1, f"verifier CLI on changed-byte: exit {code}, want 1")
with contextlib.redirect_stdout(io.StringIO()):
    code = avd_assess_bundle.main([str(FIX / "good"), "--known-schema", "avd-assess-map/v2"])
expect(code == 1, f"verifier CLI with only v2 known: exit {code}, want 1")


# 2. diff_bundle: bump rules, declarations, version enforcement, deprecation gate.
def doc(pillars, extra=None):
    d = {"schema": "avd-assess-map/v1", "pillars": pillars}
    d.update(extra or {})
    return make_fixtures.dump(d)


META = {"map.json": {"idPaths": ["/pillars/*/id"]}}


def bump(old_files, new_files, *args, old_version="1.0.0"):
    with tempfile.TemporaryDirectory() as tmp:
        o, n = Path(tmp) / "old", Path(tmp) / "new"
        make_fixtures.write_bundle(o, old_files, old_version, META)
        make_fixtures.write_bundle(n, new_files, "1.0.1", META)
        res = Path(tmp) / "r.json"
        argv = [str(o), str(n), "--json", str(res)]
        for x in args:
            argv.append(x.replace("{tmp}", tmp))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = diff_bundle.main(argv)
        result = json.loads(res.read_text(encoding="utf-8"))
        return result["bump"], code, out.getvalue(), result


base = make_fixtures.base_files()
same = dict(base)
expect(bump(base, same)[0] == "none", "diff: identical bundles should need no bump")

f = dict(base, **{"notes.md": b"# Notes, reworded\n"})
expect(bump(base, f)[0] == "patch", "diff: a reworded page is a patch")

f = dict(base, **{"map.json": doc([{"id": "identity"}, {"id": "network"}, {"id": "storage"}])})
b, _, out, res = bump(base, f)
expect(b == "minor", f"diff: an added ID is a minor, got {b}")

f = dict(base, **{"map.json": doc([{"id": "identity"}])})
b, _, out, res = bump(base, f)
expect(b == "major", f"diff: a removed ID is a major, got {b}")
expect(any(g for g in res["gate"]), "diff: a removed ID without --history should report the gate as not evaluated")

f = dict(base, **{"extra.json": make_fixtures.dump({"x": 1})})
expect(bump(base, f)[0] == "minor", "diff: a new file is a minor")
f = {k: v for k, v in base.items() if k != "notes.md"}
expect(bump(base, f)[0] == "major", "diff: a removed file is a major")

f = dict(base, **{"map.json": doc([{"id": "identity"}, {"id": "network"}]).replace(b"v1", b"v2")})
expect(bump(base, f)[0] == "major", "diff: a schema string major bump is a major")

s = copy.deepcopy(make_fixtures.SCHEMA)
s["properties"]["pillars"]["items"]["required"] = ["id", "title"]
f = dict(base, **{"schemas/map.schema.json": make_fixtures.dump(s)})
b, _, out, res = bump(base, f)
expect(b == "major", f"diff: a newly required field is a major, got {b}")
key = next((x["key"] for x in res["findings"] if x["key"].startswith("schema-required")), None)
expect(key is not None, "diff: the required finding has a schema-required key")

s2 = copy.deepcopy(make_fixtures.SCHEMA)
s2["properties"]["pillars"]["items"]["properties"]["id"]["pattern"] = "^[a-z]+$"
f = dict(base, **{"schemas/map.schema.json": make_fixtures.dump(s2)})
b, _, out, res = bump(base, f)
pkey = next(x["key"] for x in res["findings"] if x["key"].startswith("schema-pattern"))
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as t:
    t.write(f"Release notes\nNOT-BREAKING: {pkey} the pattern only widens what was already written\n")
b2 = bump(base, f, "--declared", t.name)[0]
expect(b == "major" and b2 == "minor", f"diff: NOT-BREAKING lowers a pattern change to minor (got {b} then {b2})")
with open(t.name, "w") as fh:
    fh.write("BREAKING: pillar ids now mean the area, not the team\n")
expect(bump(base, dict(base, **{"notes.md": b"# x\n"}), "--declared", t.name)[0] == "major", "diff: BREAKING raises to major")
Path(t.name).unlink()

f = dict(base, **{"map.json": doc([{"id": "identity"}, {"id": "network"}, {"id": "storage"}])})
expect(bump(base, f, "--version", "1.0.1")[1] == 1, "diff: a patch tag over a minor change must fail")
expect(bump(base, f, "--version", "1.1.0")[1] == 0, "diff: a minor tag over a minor change passes")
expect(bump(base, f, "--version", "1.0.0")[1] == 1, "diff: a tag equal to the last release must fail")

# Deprecation gate: the removed ID must carry 'deprecated' in a release published 30+ days earlier.
dep = dict(base, **{"map.json": doc([{"id": "identity"}, {"id": "network", "deprecated": {"since": "1.0.0", "replacedBy": None}}])})
gone = dict(base, **{"map.json": doc([{"id": "identity"}])})
with tempfile.TemporaryDirectory() as hist:
    make_fixtures.write_bundle(Path(hist) / "1.0.0", dep, "1.0.0", META)
    (Path(hist) / "dates.json").write_text(json.dumps({"1.0.0": "2026-10-01T00:00:00Z"}), encoding="utf-8")
    ok = bump(dep, gone, "--history", hist, "--now", "2026-11-05T00:00:00Z", "--version", "2.0.0")
    early = bump(dep, gone, "--history", hist, "--now", "2026-10-20T00:00:00Z", "--version", "2.0.0")
    make_fixtures.write_bundle(Path(hist) / "1.0.0", base, "1.0.0", META)
    never = bump(base, gone, "--history", hist, "--now", "2026-11-05T00:00:00Z", "--version", "2.0.0")
expect(ok[1] == 0, f"diff gate: deprecated 35 days ago should pass: {ok[2]}")
expect(early[1] == 1, "diff gate: deprecated 19 days ago must fail")
expect(never[1] == 1, "diff gate: an ID never marked deprecated must fail")
expect(bump(base, dep)[0] == "minor", "diff: a deprecation mark is a minor")

# Qualified IDs: a claim is known by its reference, so moving it between references is a remove and an add.
idx = {"references": [{"id": "a", "claims": [{"id": "x"}]}, {"id": "b", "claims": [{"id": "y"}]}]}
expect(sorted(i for i, _ in diff_bundle.ids_at(idx, "/references/*/claims/*/id")) == ["a#x", "b#y"],
       "ids_at: claims are qualified by their reference")

# Index: a claim's words changed is a minor; a pin refresh alone is a patch.
IDX_META = {"index.json": {"idPaths": ["/references/*/id", "/references/*/claims/*/id"]}}


def index_bump(old, new):
    with tempfile.TemporaryDirectory() as tmp:
        o, n = Path(tmp) / "o", Path(tmp) / "n"
        make_fixtures.write_bundle(o, {"index.json": make_fixtures.dump(old)}, "1.0.0", IDX_META)
        make_fixtures.write_bundle(n, {"index.json": make_fixtures.dump(new)}, "1.0.0", IDX_META)
        findings, _, _ = diff_bundle.diff(o, n)
        return max([x[0] for x in findings], key=diff_bundle.RANK.get, default="none")


i0 = {"schema": "avd-assess-index/v1", "references": [{"id": "r", "pin": "p1", "claims": [{"id": "c", "says": "one"}]}]}
i1 = copy.deepcopy(i0)
i1["references"][0]["pin"] = "p2"
i2 = copy.deepcopy(i1)
i2["references"][0]["claims"][0]["says"] = "two"
expect(index_bump(i0, i1) == "patch", "diff: a pin refresh with the same claim is a patch")
expect(index_bump(i0, i2) == "minor", "diff: a claim whose words changed is a minor")

# 3. The leak scan finds each kind of leak, and passes the allowlists. The samples are assembled at run
# time so the repo's own leak check (tests/check_method.py) doesn't see them in this file.
ALLOWED = "-".join(["0" * 8, "0" * 4, "0" * 4, "0" * 4, "0" * 11 + "a"]).encode()
GUID_SAMPLE = "-".join(["1" * 8, "2" * 4, "3" * 4, "4" * 4, "5" * 12]).encode()
files = {"tests/public-ids.txt": ALLOWED + b"\n", "tests/public-ipv4.txt": b"0.0.0.0\n",
         "ok.md": b"default route 0.0.0.0/0 and " + ALLOWED + b", version 10.0.19045.1234\n"}
expect(build_bundle.leak_scan(files, {"banned": ["Examplecorp"]}) == [], "leak scan: allowlisted values flagged")
for bad, what in ((b"id " + GUID_SAMPLE + b"\n", "GUID"), (b"mail someone" + b"@" + b"example.org\n", "email"),
                  (b"host " + ".".join(["10", "1", "2", "3"]).encode() + b"\n", "IPv4"), ("caf\u00e9\n".encode("utf-8"), "non-ASCII"),
                  (b"uses examplecorp agent\n", "names")):
    found = build_bundle.leak_scan(dict(files, **{"bad.md": bad}), {"banned": ["Examplecorp"]})
    expect(any(what in e for e in found), f"leak scan: missed a {what}: {found}")

# 4. Schemas: $id under assess.avd-ops.dev naming their schema string, only local $refs, and every
# document schema accepts 'deprecated' on each object its idPaths reach.
schema_files = sorted((ROOT / "contracts" / "schemas").glob("*.json")) + [ROOT / "evidence" / "schema.json"]
for p in schema_files:
    rel = p.relative_to(ROOT).as_posix()
    s = json.loads(p.read_text(encoding="utf-8"))
    name = build_bundle.schema_string_of(rel, p.read_bytes()) or (s.get("title", "").split(":")[0] if rel == "evidence/schema.json" else None)
    m = re.match(r"^([a-z0-9-]+)/v(\d+)$", name or "")
    expect(m is not None, f"{rel}: no schema string to name its $id by")
    if m:
        want = f"{build_bundle.SCHEMA_BASE}{m.group(1)}/v{m.group(2)}.json"
        expect(s.get("$id") == want, f"{rel}: $id is {s.get('$id')!r}, want {want}")
    refs = re.findall(r'"\$ref"\s*:\s*"([^"]*)"', p.read_text(encoding="utf-8"))
    for ref in refs:
        expect(ref.startswith("#"), f"{rel}: $ref {ref!r} points outside the file; a validator would fetch it")

for path, (_, id_paths) in build_bundle.DOCUMENTS.items():
    dp = ROOT / path
    if not dp.exists():
        continue
    d = json.loads(dp.read_text(encoding="utf-8"))
    sp = next((q for q in schema_files if build_bundle.schema_string_of(q.relative_to(ROOT).as_posix(), q.read_bytes()) == d.get("schema")), None)
    if sp is None:
        continue
    v = Draft202012Validator(json.loads(sp.read_text(encoding="utf-8")))
    for ptr in id_paths:
        trial = copy.deepcopy(d)
        hit = next(iter(diff_bundle.ids_at(trial, ptr)), None)
        if hit is None:
            continue
        hit[1]["deprecated"] = {"since": "1.0.0", "replacedBy": None}
        e = next(iter(v.iter_errors(trial)), None)
        expect(e is None, f"{path}: {sp.name} refuses 'deprecated' at {ptr} ({e.message[:100] if e else ''})")

# 5. The Pages site, from release assets: catalog, schemas at their $id, mirror, withdrawal marks.
import build_site  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    files, manifest, sums, commit = build_bundle.build("HEAD", "1.0.0", "v1.0.0")
    rel = Path(tmp) / "rel"
    for v, body in (("1.0.0", "First release."), ("1.0.1", "Fixes.\nWITHDRAWS: v1.0.0 a wrong pin")):
        (rel / v).mkdir(parents=True)
        (rel / v / "datapackage.json").write_bytes(manifest if v == "1.0.0" else build_bundle.build("HEAD", v, f"v{v}")[1])
        m = manifest if v == "1.0.0" else (rel / v / "datapackage.json").read_bytes()
        (rel / v / f"avd-assess-{v}.zip").write_bytes(build_bundle.zip_bytes(files, m, sums))
        (rel / v / "release.json").write_text(json.dumps({"tag": f"v{v}", "publishedAt": "2026-10-22T00:00:00Z",
                                                          "body": body}), encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        build_site.build(rel, Path(tmp) / "site")
    cat = json.loads((Path(tmp) / "site" / "catalog.json").read_text(encoding="utf-8"))
    expect([e["version"] for e in cat["releases"]] == ["1.0.1", "1.0.0"], "site: catalog lists releases newest first")
    expect(cat["releases"][1].get("withdrawn", "").startswith("a wrong pin"), "site: WITHDRAWS marks the earlier release")
    expect((Path(tmp) / "site" / "schemas" / "avd-assess-map" / "v1.json").exists(), "site: schema at its $id path")
    expect((Path(tmp) / "site" / "v" / "1.0.0" / "map.json").read_bytes() == files["map.json"], "site: mirror bytes")

if errors:
    print("\n".join(f"RESULT FAIL {e}" for e in errors))
    sys.exit(1)
print(f"RESULT PASS ({len(cases)} verifier cases, diff rules, leak scan, {len(schema_files)} schemas)")
