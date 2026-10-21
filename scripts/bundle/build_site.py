#!/usr/bin/env python3
"""Builds the GitHub Pages site for assess.avd-ops.dev from published release assets only, never from a
working tree (docs/distribution-spec.md section 5): catalog.json, each schema at its $id, and a mirror
of every release. A convenience, never a trust anchor: every reader still checks the manifest hash.

  python3 scripts/bundle/build_site.py --releases rel/ --out site/

rel/<version>/ holds one published release: datapackage.json and avd-assess-<version>.zip from its
assets, and release.json ({"tag", "publishedAt", "url", "body"} from gh release view). A release is
marked withdrawn by a line 'WITHDRAWN: <reason>' in its own notes, or 'WITHDRAWS: v<version> <reason>'
in a later release's notes.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import avd_assess_bundle  # noqa: E402

REPO = "https://github.com/avd-ops/avd-assess"
SCHEMA_BASE = "https://assess.avd-ops.dev/schemas/"
NOTICE = ("Personal project, not for production, as is. Not affiliated with, endorsed by or supported by the "
          "author's employer, Liquidware or Microsoft.")


def semver(v):
    return tuple(int(x) for x in v.split("."))


def safe_extract(zip_path, dest):
    """Unzips with every entry checked: relative, no '..', no absolute or drive paths."""
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            why = avd_assess_bundle.bad_path(info.filename)
            if why or info.is_dir():
                raise SystemExit(f"RESULT FAIL {zip_path.name}: entry {info.filename!r} refused ({why or 'a folder entry'})")
            out = dest / info.filename
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read(info))


def build(releases, out):
    releases, out = Path(releases), Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    found = sorted((d for d in releases.iterdir() if d.is_dir() and re.match(r"^\d+\.\d+\.\d+$", d.name)),
                   key=lambda d: semver(d.name))
    withdrawn = {}
    infos = {}
    for d in found:
        info = json.loads((d / "release.json").read_text(encoding="utf-8"))
        infos[d.name] = info
        for line in (info.get("body") or "").splitlines():
            m = re.match(r"^WITHDRAWN:\s*(.+)$", line.strip())
            if m:
                withdrawn[d.name] = m.group(1)
            m = re.match(r"^WITHDRAWS:\s*v(\d+\.\d+\.\d+)\s+(.+)$", line.strip())
            if m:
                withdrawn.setdefault(m.group(1), f"{m.group(2)} (see v{d.name})")
    catalog, schemas, previous = [], {}, {}
    for d in found:
        v = d.name
        manifest = (d / "datapackage.json").read_bytes()
        mirror = out / "v" / v
        safe_extract(d / f"avd-assess-{v}.zip", mirror)
        if (mirror / "datapackage.json").read_bytes() != manifest:
            raise SystemExit(f"RESULT FAIL v{v}: the zip's datapackage.json differs from the release asset")
        results = list(avd_assess_bundle.check_bundle(mirror, validate=False))
        failed = [f"{c}: {t}" for s, c, t in results if s == "FAIL"]
        if failed:
            raise SystemExit(f"RESULT FAIL v{v}: {failed[0]}")
        m = json.loads(manifest)
        majors = {r["path"]: r["schemaString"] for r in m["resources"] if r.get("schemaString")}
        changed = sorted(p for p, s in majors.items()
                         if p in previous and previous[p].split("/v")[1] != s.split("/v")[1])
        previous = majors
        info = infos[v]
        entry = {
            "version": v, "tag": f"v{v}", "commit": m["avdAssess"]["commit"], "created": m["created"],
            "published": info.get("publishedAt"), "manifestSha256": hashlib.sha256(manifest).hexdigest(),
            "assets": {name: f"{REPO}/releases/download/v{v}/{name}"
                       for name in (f"avd-assess-{v}.zip", "datapackage.json", "SHA256SUMS")},
            "mirror": f"v/{v}/", "majorChanged": changed,
        }
        if v in withdrawn:
            entry["withdrawn"] = withdrawn[v]
        catalog.append(entry)
        for r in m["resources"]:
            if r["path"].endswith(".json"):
                doc = json.loads((mirror / r["path"]).read_text(encoding="utf-8"))
                sid = doc.get("$id") if isinstance(doc, dict) else None
                if isinstance(sid, str) and sid.startswith(SCHEMA_BASE) and v not in withdrawn:
                    schemas[sid[len(SCHEMA_BASE):]] = (mirror / r["path"]).read_bytes()
    for rel, data in schemas.items():
        if avd_assess_bundle.bad_path(rel):
            raise SystemExit(f"RESULT FAIL schema $id path {rel!r} refused")
        (out / "schemas" / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / "schemas" / rel).write_bytes(data)
    catalog.sort(key=lambda e: semver(e["version"]), reverse=True)
    doc = {"schema": "avd-assess-catalog/v1", "description": NOTICE + " A convenience list of releases; pin the "
           "manifest's SHA-256, never this file.", "repository": REPO, "releases": catalog}
    (out / "catalog.json").write_text(json.dumps(doc, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    (out / ".nojekyll").write_bytes(b"")
    rows = "\n".join(
        f"<li><a href=\"{html.escape(e['assets'][f'avd-assess-{e['version']}.zip'])}\">v{e['version']}</a> "
        f"({html.escape(str(e['published'] or ''))[:10]}), manifest <code>{e['manifestSha256']}</code>"
        + (f" <strong>withdrawn: {html.escape(e['withdrawn'])}</strong>" if "withdrawn" in e else "") + "</li>"
        for e in catalog) or "<li>No release yet.</li>"
    (out / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>avd-assess releases</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 48rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.5">
<p><strong>{html.escape(NOTICE)}</strong></p>
<h1>avd-assess releases</h1>
<p>The map of an Azure Virtual Desktop estate, released as a versioned bundle. The canonical copies are the
<a href="{REPO}/releases">immutable GitHub releases</a>; this page, <a href="catalog.json">catalog.json</a>,
the schemas under <code>/schemas/</code> and the mirror under <code>/v/</code> are conveniences. Check the
attestation (<code>gh attestation verify &lt;file&gt; -R avd-ops/avd-assess</code>) and pin the manifest's SHA-256.</p>
<ul>
{rows}
</ul>
<p>Contributions and forks are welcome: <a href="{REPO}">{REPO}</a>.</p>
</body></html>
""", encoding="utf-8")
    print(f"RESULT PASS site: {len(catalog)} releases, {len(schemas)} schemas, {len(withdrawn)} withdrawn")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--releases", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return build(a.releases, a.out)


if __name__ == "__main__":
    sys.exit(main())
