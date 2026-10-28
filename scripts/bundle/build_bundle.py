#!/usr/bin/env python3
"""Builds the avd-assess release bundle (docs/distribution-spec.md section 4) from a commit's git blobs,
never from the working tree or git archive, so every file's bytes equal its blob at that commit.

  python3 scripts/bundle/build_bundle.py --check                     # CI: dry run of HEAD, built twice
  python3 scripts/bundle/build_bundle.py --ref v1.0.0 --tag v1.0.0 --out out/   # the release workflow

--out writes: bundle/ (the files at their repo paths, plus datapackage.json and SHA256SUMS),
assets/ (the release assets: avd-assess-<version>.zip, datapackage.json, SHA256SUMS and every JSON
file under its base name). --check also runs the release gates that need no network: the bundle
profile, the .gitattributes guard, the leak scan, unique base names, a deterministic rebuild and the
Python verifier.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import avd_assess_bundle  # noqa: E402  (the verifier ships in the bundle; the builder reuses its checks)
import diff_bundle  # noqa: E402

PROFILE = "avd-assess-bundle/v1"
# What goes in the bundle (section 4.1), as patterns over the commit's tracked paths. '*' stays within
# a folder; '**' crosses folders.
INCLUDE = [
    "index.json", "method.json", "map.json", "security-review.json", "endpoints.json",
    "contracts/fact-register.json", "contracts/run-use-cases.json",
    "contracts/schemas/*.json", "evidence/schema.json", "contracts/examples/**",
    "methods/*.md", "gaps/*.md", "contracts/README.md", "README.md", "LICENSE", "NOTICE",
    "tools/avd_assess_bundle.py", "tools/AvdAssessBundle.psm1", "tools/diff_bundle.py",
    "tests/public-ids.txt", "tests/public-ipv4.txt",
]
# Files that must be there; the rest of INCLUDE is taken when present (security-review.json and
# endpoints.json join when their pull requests merge).
REQUIRED = ["index.json", "method.json", "map.json", "contracts/fact-register.json", "LICENSE", "NOTICE",
            "tools/avd_assess_bundle.py", "tools/AvdAssessBundle.psm1", "tools/diff_bundle.py"]
# The documents: resource name and the JSON pointers to their IDs ('*' = every array item). A test
# (tests/check_bundle.py) fails when a document holds an 'id' at a path not listed here.
DOCUMENTS = {
    "index.json": ("index", ["/references/*/id", "/references/*/claims/*/id", "/observations/*/id", "/gaps/*/id"]),
    "method.json": ("method", ["/checks/*/id"]),
    "map.json": ("map", ["/pillars/*/id", "/dimensions/*/id", "/baselines/window/*/id", "/baselines/classes/*/id",
                         "/useCases/*/id", "/benchmarks/*/id"]),
    "security-review.json": ("security-review", ["/areas/*/id", "/areas/*/claims/*/id", "/operator/*/id",
                                                 "/checklist/*/id", "/gaps/*/id"]),
    "endpoints.json": ("endpoints", ["/lists/*/id", "/endpoints/*/id"]),
    "contracts/fact-register.json": ("fact-register", ["/facts/*/id", "/decisions/*/id"]),
    "contracts/run-use-cases.json": ("run-use-cases", ["/useCases/*/id"]),
}
# Schemas whose documents carry no top-level schema string (a journal line has 'v' instead).
SCHEMA_NAMES = {"contracts/schemas/run-journal.schema.json": "avd-run-journal",
                "contracts/schemas/assess-bundle.schema.json": "avd-assess-bundle"}
SCHEMA_BASE = "https://assess.avd-ops.dev/schemas/"
MEDIA = {"json": "application/json", "jsonl": "application/jsonl", "md": "text/markdown", "py": "text/x-python",
         "psm1": "text/plain", "txt": "text/plain", "": "text/plain"}
MANIFEST_KEYS = ["$schema", "name", "title", "version", "created", "homepage", "description", "licenses",
                 "sources", "avdAssess", "resources"]
RESOURCE_KEYS = ["name", "path", "format", "mediatype", "bytes", "hash", "schemaString", "jsonSchema", "idPaths"]
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def git(*args, binary=False):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=False)
    if r.returncode:
        raise SystemExit(f"RESULT FAIL git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode("utf-8")


def glob_re(pattern):
    out = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(f"^{out}$")


PATTERNS = [glob_re(p) for p in INCLUDE]


def members(ref):
    """The bundle's paths at a commit, from git ls-tree; refuses symlinks and submodules."""
    entries = git("ls-tree", "-r", "-z", "--full-tree", ref, binary=True).decode("utf-8").split("\0")
    paths = []
    for e in filter(None, entries):
        meta, path = e.split("\t", 1)
        mode, kind, _ = meta.split()
        if not any(p.match(path) for p in PATTERNS):
            continue
        if kind != "blob" or mode == "120000":
            raise SystemExit(f"RESULT FAIL bundle: {path} is a {'symlink' if mode == '120000' else kind}, not a file")
        paths.append(path)
    missing = [p for p in REQUIRED if p not in paths]
    if missing:
        raise SystemExit(f"RESULT FAIL bundle: required files missing at {ref}: {', '.join(missing)}")
    return sorted(paths)


def resource_name(path):
    return _resource_name(path).lower()


def _resource_name(path):
    if path in DOCUMENTS:
        return DOCUMENTS[path][0]
    p = Path(path)
    stem = p.name.split(".")[0]
    if path.startswith("contracts/schemas/"):
        return f"schema-{p.name[:-len('.schema.json')]}"
    if path == "evidence/schema.json":
        return "schema-evidence"
    if path.startswith("contracts/examples/"):
        return f"example-{p.parent.name}-{stem}"
    if path.startswith("methods/"):
        return f"method-{stem}"
    if path.startswith("gaps/"):
        return f"gap-{stem}"
    if path.startswith("tools/"):
        return "tool-" + re.sub(r"[^a-z0-9]+", "-", p.name.lower()).strip("-")
    return re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def schema_string_of(path, data):
    """The schema string a JSON Schema file describes: its properties.schema.const, or SCHEMA_NAMES."""
    if path in SCHEMA_NAMES:
        return SCHEMA_NAMES[path] + "/v1"
    try:
        doc = json.loads(data)
    except ValueError:
        return None
    const = doc.get("properties", {}).get("schema", {}).get("const") if isinstance(doc, dict) else None
    return const if isinstance(const, str) else None


def build(ref="HEAD", version="0.0.0-dev", tag=None):
    """Returns (files {path: bytes}, manifest bytes, SHA256SUMS bytes, commit)."""
    commit = git("rev-parse", f"{ref}^{{commit}}").strip()
    created = git("log", "-1", "--format=%cI", commit).strip()
    files = {p: git("cat-file", "blob", f"{commit}:{p}", binary=True) for p in members(commit)}
    schema_file = {}
    for p, b in files.items():
        if p.startswith("contracts/schemas/") or p == "evidence/schema.json":
            s = schema_string_of(p, b)
            if s:
                schema_file[s] = p
    resources = []
    for p, b in files.items():
        ext = p.rsplit(".", 1)[-1] if "." in Path(p).name else ""
        fmt = ext if ext in ("json", "jsonl", "md", "py", "psm1", "txt") else "txt"
        r = {"name": resource_name(p), "path": p, "format": fmt, "mediatype": MEDIA.get(fmt, "text/plain"),
             "bytes": len(b), "hash": "sha256:" + hashlib.sha256(b).hexdigest()}
        if fmt == "json":
            doc = json.loads(b)
            s = doc.get("schema") if isinstance(doc, dict) else None
            if isinstance(s, str):
                r["schemaString"] = s
                if s in schema_file:
                    r["jsonSchema"] = schema_file[s]
        elif fmt == "jsonl" and "avd-run-journal/v1" in schema_file and "journal" in p:
            r["jsonSchema"] = schema_file["avd-run-journal/v1"]
        if p in DOCUMENTS:
            r["idPaths"] = DOCUMENTS[p][1]
        resources.append({k: r[k] for k in RESOURCE_KEYS if k in r})
    names = [r["name"] for r in resources]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise SystemExit(f"RESULT FAIL bundle: resource names not unique: {', '.join(dupes)}")
    a = {"commit": commit, "profile": PROFILE}
    if tag:
        a = {"commit": commit, "tag": tag, "profile": PROFILE}
    m = {
        "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
        "name": "avd-assess",
        "title": "avd-assess: the AVD assessment map",
        "version": version,
        "created": created,
        "homepage": "https://github.com/avd-ops/avd-assess",
        "description": "Personal project, not for production, as is; not affiliated with the author's employer, "
                       "Liquidware or Microsoft.",
        "licenses": [{"name": "MIT", "path": "LICENSE"}],
        "sources": [{"title": "Microsoft Learn and the other pinned references in index.json, linked, never copied",
                     "path": "NOTICE"}],
        "avdAssess": a,
        "resources": resources,
    }
    manifest = (json.dumps({k: m[k] for k in MANIFEST_KEYS}, indent=2, ensure_ascii=True) + "\n").encode("ascii")
    sums = "".join(f"{r['hash'][7:]}  {r['path']}\n" for r in resources).encode("ascii")
    return files, manifest, sums, commit


def zip_bytes(files, manifest, sums):
    """A deterministic zip: entries sorted, fixed time and permissions."""
    buf = io.BytesIO()
    entries = dict(files)
    entries["datapackage.json"] = manifest
    entries["SHA256SUMS"] = sums
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(entries):
            info = zipfile.ZipInfo(p, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            z.writestr(info, entries[p], compresslevel=9)
    return buf.getvalue()


MARKER = ".avd-assess-build"


def clear_output(out):
    """Empties an output folder this tool made before (it holds MARKER), or refuses a folder with anything
    else in it: --out names a build folder, never a checkout or a home folder."""
    out = Path(out)
    if out.exists():
        if not out.is_dir() or (any(out.iterdir()) and not (out / MARKER).is_file()):
            raise SystemExit(f"RESULT FAIL {out} exists and is not an output folder this tool made; name a new folder")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARKER).write_bytes(b"")


def write(out, files, manifest, sums, version):
    out = Path(out)
    clear_output(out)
    bundle, assets = out / "bundle", out / "assets"
    for p, b in files.items():
        (bundle / p).parent.mkdir(parents=True, exist_ok=True)
        (bundle / p).write_bytes(b)
    (bundle / "datapackage.json").write_bytes(manifest)
    (bundle / "SHA256SUMS").write_bytes(sums)
    assets.mkdir(parents=True)
    (assets / f"avd-assess-{version}.zip").write_bytes(zip_bytes(files, manifest, sums))
    (assets / "datapackage.json").write_bytes(manifest)
    (assets / "SHA256SUMS").write_bytes(sums)
    for p, b in files.items():
        if p.endswith(".json"):
            (assets / Path(p).name).write_bytes(b)


# --- release gates that need no network --------------------------------------------------------------

GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
IPV4 = re.compile(r"(?<![\w.])((?:\d{1,3}\.){3}\d{1,3})(?![\w.]*\d)")


def allowlist(files, path):
    text = files.get(path, b"").decode("utf-8")
    return {line.strip().lower() for line in text.splitlines() if line.strip() and not line.startswith("#")}


def leak_scan(files, wording):
    """GUIDs not in tests/public-ids.txt, emails, IPv4 addresses not in tests/public-ipv4.txt, non-ASCII
    bytes, and the third-party product names in tests/wording.json (section 7, step 4)."""
    ids, ips = allowlist(files, "tests/public-ids.txt"), allowlist(files, "tests/public-ipv4.txt")
    banned = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in wording["banned"]) + r")(?![\w-])", re.I)
    errors = []
    for p, b in sorted(files.items()):
        bad = next((i for i, c in enumerate(b) if c > 127), None)
        if bad is not None:
            errors.append(f"{p}: non-ASCII byte at offset {bad}")
        text = b.decode("utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            for g in GUID.findall(line):
                if g.lower() not in ids:
                    errors.append(f"{p}:{n}: GUID {g} is not in tests/public-ids.txt")
            for e in EMAIL.findall(line):
                errors.append(f"{p}:{n}: email address {e}")
            for ip in IPV4.findall(line):
                if all(int(o) <= 255 for o in ip.split(".")) and ip not in ips:
                    errors.append(f"{p}:{n}: IPv4 address {ip} is not in tests/public-ipv4.txt")
            m = banned.search(line)
            if m:
                errors.append(f"{p}:{n}: names {m.group(1)!r} (tests/wording.json)")
    return errors


def attributes_guard(ref, paths):
    """No eol, text or export-* attribute may apply to a bundled path at this commit (section 4.1)."""
    out = git("check-attr", f"--source={ref}", "-z", "text", "eol", "export-ignore", "export-subst", "--", *paths)
    parts = out.split("\0")
    errors = []
    for i in range(0, len(parts) - 2, 3):
        path, attr, value = parts[i:i + 3]
        if value != "unspecified":
            errors.append(f"{path}: .gitattributes sets {attr}={value}")
    return errors


def basename_guard(files):
    seen = {}
    for p in files:
        if p.endswith(".json"):
            seen.setdefault(Path(p).name, []).append(p)
    clash = {k: v for k, v in seen.items() if len(v) > 1 or k == "datapackage.json"}
    return [f"release asset name {k} is not unique: {', '.join(v)}" for k, v in sorted(clash.items())]


def profile_schema_check(manifest, files):
    """The manifest against contracts/schemas/assess-bundle.schema.json, with jsonschema (CI has it)."""
    schema = files.get("contracts/schemas/assess-bundle.schema.json")
    if schema is None:
        return ["contracts/schemas/assess-bundle.schema.json is not in the bundle"]
    from jsonschema import Draft202012Validator
    v = Draft202012Validator(json.loads(schema))
    return [f"datapackage.json /{'/'.join(map(str, e.path))}: {e.message[:160]}"
            for e in v.iter_errors(json.loads(manifest))][:5]


def id_paths_guard(files):
    """Every 'id' in a document sits under one of its idPaths, so diff_bundle sees every ID set."""
    errors = []

    def walk(node, ptr, found):
        if isinstance(node, dict):
            if isinstance(node.get("id"), (str, int)):
                found.add(ptr + "/id")
            for k, v in node.items():
                walk(v, f"{ptr}/{k}", found)
        elif isinstance(node, list):
            for item in node:
                walk(item, ptr + "/*", found)

    for p, (_, paths) in DOCUMENTS.items():
        if p not in files:
            continue
        found = set()
        walk(json.loads(files[p]), "", found)
        for missing in sorted(found - set(paths)):
            errors.append(f"{p}: IDs at {missing} are not in its idPaths (scripts/bundle/build_bundle.py DOCUMENTS)")
        doc = json.loads(files[p])
        for ptr in paths:
            if not any(True for _ in diff_bundle.ids_at(doc, ptr)):
                errors.append(f"{p}: idPaths {ptr} resolves to nothing (a typo, or the array moved)")
    return errors


def check(ref):
    print(f"Building the bundle from {ref} twice, from git blobs ...", flush=True)
    files, manifest, sums, commit = build(ref)
    files2, manifest2, sums2, _ = build(ref)
    failures = []
    if manifest != manifest2 or sums != sums2 or zip_bytes(files, manifest, sums) != zip_bytes(files2, manifest2, sums2):
        failures.append("determinism: two builds of the same commit differ")
    wording = json.loads(git("cat-file", "blob", f"{commit}:tests/wording.json"))
    for name, errs in (("profile", profile_schema_check(manifest, files)),
                       ("gitattributes", attributes_guard(commit, sorted(files))),
                       ("asset names", basename_guard(files)),
                       ("idPaths", id_paths_guard(files)),
                       ("leak scan", leak_scan(files, wording))):
        failures += [f"{name}: {e}" for e in errs]
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp, files, manifest, sums, "0.0.0-dev")
        results = list(avd_assess_bundle.check_bundle(Path(tmp) / "bundle"))
        for status, cid, detail in results:
            print(f"  verifier {status} {cid}: {detail}")
        failures += [f"verifier {cid}: {detail}" for status, cid, detail in results if status != "PASS"]
    for f in failures:
        print(f"RESULT FAIL {f}")
    if failures:
        return 1
    print(f"RESULT PASS bundle of {commit[:12]}: {len(files)} files, {len(manifest)} byte manifest, deterministic, "
          f"profile valid, no leak, verifier passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ref", default="HEAD", help="the commit or tag to build from (default HEAD)")
    ap.add_argument("--tag", help="the release tag, v<MAJOR.MINOR.PATCH>; sets the version")
    ap.add_argument("--out", help="write bundle/ and assets/ here")
    ap.add_argument("--check", action="store_true", help="dry run: build twice and run the offline release gates")
    ap.add_argument("--scan", nargs="+", metavar="FILE", help="run only the leak scan over these files (release notes)")
    a = ap.parse_args(argv)
    if a.scan:
        commit = git("rev-parse", f"{a.ref}^{{commit}}").strip()
        wording = json.loads(git("cat-file", "blob", f"{commit}:tests/wording.json"))
        allow = {p: git("cat-file", "blob", f"{commit}:{p}", binary=True) for p in ("tests/public-ids.txt", "tests/public-ipv4.txt")}
        errs = leak_scan(dict(allow, **{f: Path(f).read_bytes() for f in a.scan}), wording)
        for e in errs:
            print(f"RESULT FAIL leak scan: {e}")
        if not errs:
            print(f"RESULT PASS leak scan: {', '.join(a.scan)}")
        return 1 if errs else 0
    if a.check:
        return check(a.ref)
    version = "0.0.0-dev"
    if a.tag:
        if not re.match(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$", a.tag):
            print(f"RESULT FAIL tag {a.tag} is not v<MAJOR.MINOR.PATCH>")
            return 1
        version = a.tag[1:]
    if not a.out:
        ap.error("--out or --check is required")
    files, manifest, sums, commit = build(a.ref, version, a.tag)
    write(a.out, files, manifest, sums, version)
    print(f"RESULT PASS wrote {a.out}: {len(files)} files from {commit}, version {version}, "
          f"manifest sha256 {hashlib.sha256(manifest).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
