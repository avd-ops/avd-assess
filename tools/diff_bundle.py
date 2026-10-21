#!/usr/bin/env python3
"""Compares two full avd-assess release bundles and prints the smallest semantic version bump the change
allows, with the reasons (docs/distribution-spec.md section 6). Standard library only; no network.

  python3 -I diff_bundle.py <old bundle dir> <new bundle dir>
  python3 -I diff_bundle.py OLD NEW --declared pr-body.txt --version 1.1.0 --notes notes.md \\
      --history releases/ --now 2026-11-30T00:00:00Z

What it computes: the file set; each document's schema string; each JSON Schema's required, type, enum,
pattern, const, properties and additionalProperties; ID sets from each resource's idPaths (removed: major,
added: minor) and deprecation marks; method.json and the fact register's own version; and, per reference
claim, whether its words changed (minor) or only its pin (patch). What a diff can't see is declared in the
release PR: a line 'BREAKING: <why>' raises the bump to major; a line 'NOT-BREAKING: <key> <why>' lowers one
schema finding (its key is printed below) to minor, for the owner to accept at the release gate.

--version: fail (exit 1) unless the new version is at least the required bump over the old one.
--history: a folder holding one unzipped earlier release per version (history/1.0.0/...) and
dates.json ({"1.0.0": "<published ISO time>"}); with it, an ID may be removed only when it carried a
'deprecated' mark in a release published at least 30 days before --now (the deprecation gate).

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}
SECTIONS = {"major": "Breaking", "minor": "Added", "patch": "Other"}
WINDOW_DAYS = 30
SCHEMA_STRING = re.compile(r"^([a-z0-9-]+)/v([1-9]\d*)$")
VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def ids_at(doc, pointer):
    """Yields (qualified id, owning object) for an idPaths pointer such as /references/*/claims/*/id.
    A '*' matches every item of an array; an ID inside another ID'd item is qualified by it (ref#claim)."""
    segs = [s.replace("~1", "/").replace("~0", "~") for s in pointer.split("/")[1:]]

    def walk(node, i, chain):
        if i == len(segs) - 1:
            if isinstance(node, dict) and isinstance(node.get(segs[i]), (str, int)):
                yield "#".join(chain + [str(node[segs[i]])]), node
            return
        seg = segs[i]
        if seg == "*":
            if isinstance(node, list):
                for item in node:
                    inner = chain
                    if i + 1 < len(segs) - 1 and isinstance(item, dict) and isinstance(item.get("id"), str):
                        inner = chain + [item["id"]]
                    yield from walk(item, i + 1, inner)
        elif isinstance(node, dict) and seg in node:
            yield from walk(node[seg], i + 1, chain)
        elif isinstance(node, list) and seg.isdigit() and int(seg) < len(node):
            yield from walk(node[int(seg)], i + 1, chain)

    yield from walk(doc, 0, [])


def load_bundle(d):
    d = Path(d)
    m = json.loads((d / "datapackage.json").read_text(encoding="utf-8"))
    res = {r["path"]: r for r in m["resources"]}
    return d, m, res


def read_json(d, path):
    try:
        return json.loads((d / path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_schema(doc):
    return isinstance(doc, dict) and "json-schema.org" in str(doc.get("$schema", ""))


def schema_diff(path, old, new, out, ptr=""):
    """Walks two JSON Schemas side by side and adds (bump, key, text) findings."""
    if not isinstance(old, dict) or not isinstance(new, dict):
        if old != new:
            out.append(("major", f"schema-node {path}#{ptr}", f"{path}#{ptr or '/'}: a subschema changed shape"))
        return
    key = f"{path}#{ptr or '/'}"
    ro, rn = set(old.get("required", [])), set(new.get("required", []))
    for f in sorted(rn - ro):
        out.append(("major", f"schema-required {key}/{f}", f"{key}: '{f}' became required"))
    for f in sorted(ro - rn):
        out.append(("minor", f"schema-optional {key}/{f}", f"{key}: '{f}' is no longer required"))
    if "enum" in old or "enum" in new:
        eo, en = old.get("enum"), new.get("enum")
        if eo is None:
            out.append(("major", f"schema-enum {key}", f"{key}: values now restricted to an enum"))
        elif en is None:
            out.append(("minor", f"schema-enum {key}", f"{key}: enum lifted"))
        else:
            for v in [v for v in eo if v not in en]:
                out.append(("major", f"schema-enum {key}={v}", f"{key}: enum value {v!r} removed"))
            for v in [v for v in en if v not in eo]:
                out.append(("minor", f"schema-enum {key}+{v}", f"{key}: enum value {v!r} added"))
    for kw in ("type", "pattern", "const", "format"):
        if old.get(kw) != new.get(kw):
            out.append(("major", f"schema-{kw} {key}", f"{key}: {kw} {old.get(kw)!r} -> {new.get(kw)!r}"))
    ao, an = old.get("additionalProperties", True), new.get("additionalProperties", True)
    if ao is not False and an is False:
        out.append(("major", f"schema-closed {key}", f"{key}: additional properties now refused"))
    elif ao is False and an is not False:
        out.append(("minor", f"schema-open {key}", f"{key}: additional properties now allowed"))
    po, pn = old.get("properties", {}), new.get("properties", {})
    if isinstance(po, dict) and isinstance(pn, dict):
        for f in sorted(set(po) - set(pn)):
            out.append(("major", f"schema-removed {key}/{f}", f"{key}: property '{f}' removed"))
        for f in sorted(set(pn) - set(po)):
            out.append(("minor", f"schema-added {key}/{f}", f"{key}: property '{f}' added"))
    for k in sorted(set(old) & set(new)):
        if k in ("required", "enum", "type", "pattern", "const", "format", "description", "title", "$id",
                 "$schema", "$comment", "examples", "default"):
            continue
        a, b = old[k], new[k]
        if k in ("properties", "$defs", "patternProperties") and isinstance(a, dict) and isinstance(b, dict):
            for name in sorted(set(a) & set(b)):
                schema_diff(path, a[name], b[name], out, f"{ptr}/{k}/{name}")
        elif isinstance(a, dict) and isinstance(b, dict):
            schema_diff(path, a, b, out, f"{ptr}/{k}")
        elif isinstance(a, list) and isinstance(b, list) and k in ("allOf", "anyOf", "oneOf", "prefixItems"):
            if len(a) != len(b):
                out.append(("major", f"schema-{k} {key}", f"{key}: {k} has {len(a)} -> {len(b)} branches"))
            for i, (x, y) in enumerate(zip(a, b)):
                schema_diff(path, x, y, out, f"{ptr}/{k}/{i}")
        elif a != b and not isinstance(a, (dict, list)):
            out.append(("major", f"schema-{k} {key}", f"{key}: {k} {a!r} -> {b!r}"))


def diff(old_dir, new_dir):
    """Returns findings: (bump, key, section, text). Keys are stable, so NOT-BREAKING can name one."""
    od, om, ores = load_bundle(old_dir)
    nd, nm, nres = load_bundle(new_dir)
    out = []

    def add(bump, key, text, section=None):
        out.append((bump, key, section or SECTIONS[bump], text))

    for p in sorted(set(ores) - set(nres)):
        add("major", f"file-removed {p}", f"{p} removed")
    for p in sorted(set(nres) - set(ores)):
        add("minor", f"file-added {p}", f"{p} added")
    for p in sorted(set(ores) & set(nres)):
        o, n = ores[p], nres[p]
        if o["hash"] == n["hash"]:
            continue
        before = len(out)
        oj, nj = (read_json(od, p), read_json(nd, p)) if p.endswith(".json") else (None, None)
        so, sn = o.get("schemaString"), n.get("schemaString")
        if so and sn and so != sn:
            mo, mn = SCHEMA_STRING.match(so), SCHEMA_STRING.match(sn)
            if not mo or not mn or mo.group(1) != mn.group(1) or int(mn.group(2)) > int(mo.group(2)):
                add("major", f"schema-string {p}", f"{p}: {so} -> {sn}")
        if is_schema(oj) and is_schema(nj):
            found = []
            schema_diff(p, oj, nj, found)
            for bump, key, text in found:
                add(bump, key, text)
        if isinstance(oj, dict) and isinstance(nj, dict):
            for ptr in sorted(set(o.get("idPaths", [])) | set(n.get("idPaths", []))):
                io, inn = dict(ids_at(oj, ptr)), dict(ids_at(nj, ptr))
                for i in sorted(set(io) - set(inn)):
                    add("major", f"id-removed {p}{ptr}={i}", f"{p}: ID {i} removed ({ptr})")
                for i in sorted(set(inn) - set(io)):
                    add("minor", f"id-added {p}{ptr}={i}", f"{p}: ID {i} added ({ptr})")
                for i in sorted(set(io) & set(inn)):
                    if "deprecated" in inn[i] and "deprecated" not in io[i]:
                        add("minor", f"id-deprecated {p}{ptr}={i}", f"{p}: ID {i} deprecated "
                            f"(replaced by {inn[i]['deprecated'].get('replacedBy')})", "Deprecated")
            if p == "method.json":
                add("minor", "method-changed", f"method changed: scores can move (version {oj.get('version')} -> "
                    f"{nj.get('version')})", "Method")
            if p == "contracts/fact-register.json" and oj.get("version") != nj.get("version"):
                add("patch", "register-version", f"fact register version {oj.get('version')} -> {nj.get('version')}", "Method")
            if p == "index.json":
                orefs = {r.get("id"): r for r in oj.get("references", []) if isinstance(r, dict)}
                nrefs = {r.get("id"): r for r in nj.get("references", []) if isinstance(r, dict)}
                for rid in sorted(set(orefs) & set(nrefs), key=str):
                    oc = {c.get("id"): c.get("says") for c in orefs[rid].get("claims", [])}
                    nc = {c.get("id"): c.get("says") for c in nrefs[rid].get("claims", [])}
                    changed = [c for c in sorted(set(oc) & set(nc), key=str) if oc[c] != nc[c]]
                    for c in changed:
                        add("minor", f"claim-words {rid}#{c}", f"ref:{rid}#{c}: the claim's words changed")
                    if orefs[rid].get("pin") != nrefs[rid].get("pin") and not changed:
                        add("patch", f"pin-refreshed {rid}", f"ref:{rid}: pin refreshed, same claims")
        if len(out) == before:
            add("patch", f"bytes {p}", f"{p}: content changed (no ID, field or method change found)")
    return out, om, nm


def declarations(text):
    breaking, not_breaking = [], {}
    for line in (text or "").splitlines():
        line = line.strip()
        if line.startswith("BREAKING:"):
            breaking.append(line[len("BREAKING:"):].strip())
        elif line.startswith("NOT-BREAKING:"):
            rest = line[len("NOT-BREAKING:"):].strip()
            # The key is the finding's two-word key: "<kind> <where>".
            parts = rest.split(None, 2)
            if len(parts) >= 2:
                not_breaking[f"{parts[0]} {parts[1]}"] = parts[2] if len(parts) > 2 else ""
    return breaking, not_breaking


def deprecation_gate(findings, new_res_dir, history, now):
    """For each removed ID, the earliest release in history that marked it deprecated must be 30+ days old."""
    errors = []
    removed = [f for f in findings if f[1].startswith("id-removed ")]
    if not removed:
        return errors
    if history is None:
        return [f"{f[3]}: deprecation gate not evaluated (no --history)" for f in removed]
    hist = Path(history)
    dates = json.loads((hist / "dates.json").read_text(encoding="utf-8"))
    for f in removed:
        ref = f[1][len("id-removed "):]
        path_ptr, _, ident = ref.partition("=")
        marked = []
        for version, published in dates.items():
            d = hist / version
            if not (d / "datapackage.json").exists():
                continue
            _, _, res = load_bundle(d)
            for p, r in res.items():
                if not path_ptr.startswith(p + "/"):
                    continue
                ptr = path_ptr[len(p):]
                doc = read_json(d, p)
                obj = dict(ids_at(doc, ptr)).get(ident) if doc is not None else None
                if isinstance(obj, dict) and "deprecated" in obj:
                    marked.append(datetime.fromisoformat(published.replace("Z", "+00:00")))
        if not marked:
            errors.append(f"{f[3]}: it was never marked deprecated in a published release")
        elif now - min(marked) < timedelta(days=WINDOW_DAYS):
            errors.append(f"{f[3]}: marked deprecated on {min(marked).date()}, under {WINDOW_DAYS} days ago")
    return errors


def bump_ok(old, new, need):
    o, n = tuple(map(int, old.split("."))), tuple(map(int, new.split(".")))
    if n <= o:
        return False
    if need == "major":
        return n[0] > o[0]
    if need == "minor":
        return n[0] > o[0] or n[1] > o[1]
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--declared", help="text holding the release PR's BREAKING: and NOT-BREAKING: lines")
    ap.add_argument("--version", help="the new version (from the tag); fail unless the bump is big enough")
    ap.add_argument("--history", help="earlier releases, unzipped, with dates.json (the deprecation gate)")
    ap.add_argument("--now", help="ISO time for the deprecation gate (default: now)")
    ap.add_argument("--notes", help="write release notes (Markdown) here")
    ap.add_argument("--json", help="write the result as JSON here")
    a = ap.parse_args(argv)

    findings, om, nm = diff(a.old, a.new)
    breaking, not_breaking = declarations(Path(a.declared).read_text(encoding="utf-8") if a.declared else "")
    accepted = []
    final = []
    for bump, key, section, text in findings:
        if bump == "major" and key.startswith("schema-") and key in not_breaking:
            accepted.append(f"{text} (NOT-BREAKING: {not_breaking[key]})")
            bump, section = "minor", "Added"
        final.append((bump, key, section, text))
    for b in breaking:
        final.append(("major", "declared", "Breaking", f"declared: {b}"))
    need = max([f[0] for f in final], key=RANK.get, default="none")
    now = datetime.fromisoformat(a.now.replace("Z", "+00:00")) if a.now else datetime.now(timezone.utc)
    gate = deprecation_gate(final, a.new, a.history, now)

    print(f"RESULT INFO bump: {need} ({om['version']} -> {a.version or nm['version']})")
    for bump, key, _, text in final:
        print(f"  {bump:5} {text}    [{key}]")
    for line in accepted:
        print(f"  accepted NOT-BREAKING: {line}")
    unknown = sorted(set(not_breaking) - {f[1] for f in findings})
    for k in unknown:
        print(f"  NOT-BREAKING names no finding: {k}")
    failed = False
    for g in gate:
        hard = a.history is not None
        print(f"RESULT {'FAIL' if hard else 'WARN'} deprecation-gate: {g}")
        failed |= hard
    if a.version:
        if not VERSION.match(a.version) or not VERSION.match(om["version"]):
            print(f"RESULT FAIL version: {om['version']} -> {a.version} is not MAJOR.MINOR.PATCH")
            failed = True
        elif not bump_ok(om["version"], a.version, need if need != "none" else "patch"):
            print(f"RESULT FAIL version: {om['version']} -> {a.version} is smaller than the required {need} bump")
            failed = True
        else:
            print(f"RESULT PASS version: {om['version']} -> {a.version} covers the {need} bump")

    if a.notes:
        lines = [f"Required bump over {om['version']}: **{need}**.", ""]
        for section in ("Breaking", "Method", "Deprecated", "Added", "Other"):
            items = [t for _, _, s, t in final if s == section]
            if items:
                lines += [f"## {section}", ""] + [f"- {t}" for t in items] + [""]
        if accepted:
            lines += ["## Accepted as not breaking", ""] + [f"- {t}" for t in accepted] + [""]
        Path(a.notes).write_text("\n".join(lines), encoding="utf-8")
    if a.json:
        Path(a.json).write_text(json.dumps({"from": om["version"], "bump": need, "findings": [
            {"bump": b, "key": k, "section": s, "text": t} for b, k, s, t in final],
            "gate": gate, "accepted": accepted}, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
