#!/usr/bin/env python3
"""Reports pin drift: a Learn page whose git_commit_id or updated_at no longer matches a reference's pin,
a GitHub source whose pinned path no longer exists at its branch head, new or removed landing zone
parameters against dimensions.yaml, and new or removed AVD review checklist items against the pinned
claims. It only reports; nothing moves a pin except a reviewed pull request. Run by
.github/workflows/pins.yml weekly, which opens or updates one issue with the output.

Usage: python3 scripts/check_pins.py [--write-report FILE]
Exit code is 0 whether or not drift was found (drift is a to-do, not a failure); 2 on a network problem that
stopped the comparison.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEARN_PIN = re.compile(r"^Learn git_commit_id ([0-9a-f]{40}), updated_at (\d{4}-\d{2}-\d{2})$")
META = re.compile(r'<meta name="(git_commit_id|updated_at)" content="([^"]+)"')
LANDING_ZONE_MAIN = "https://raw.githubusercontent.com/avd-ops/avd-landing-zone/master/bicep/main.bicep"
CHECKLIST_MAIN = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/avd_checklist.en.json"
UA = {"User-Agent": "avd-assess pin check (https://github.com/avd-ops/avd-assess)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def learn_drift(refs):
    rows, failed = [], []
    for ref in refs:
        m = LEARN_PIN.match(str(ref.get("pin", "")))
        if not m:
            continue
        try:
            page = fetch(ref["url"])
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            failed.append(f"{ref['id']}: {e}")
            continue
        meta = dict(META.findall(page))
        live_commit = meta.get("git_commit_id", "")
        live_date = meta.get("updated_at", "")[:10]
        if live_commit != m.group(1):
            rows.append(f"| `{ref['id']}` | {m.group(2)} | {live_date or '?'} | {len(ref.get('claims') or [])} | {ref['url']} |")
    return rows, failed


def github_drift(refs):
    rows, failed = [], []
    for ref in refs:
        pin = str(ref.get("pin", ""))
        m = re.match(r"^https://github\.com/([^/]+)/([^/]+)/blob/[0-9a-f]{40}/(.+)$", pin)
        if not m:
            continue
        owner, repo, path = m.groups()
        ok = False
        for branch in ("main", "master"):
            try:
                fetch(f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}")
                ok = True
                break
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    failed.append(f"{ref['id']}: {e}")
                    ok = True
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                failed.append(f"{ref['id']}: {e}")
                ok = True
                break
        if not ok:
            rows.append(f"| `{ref['id']}` | {path} | {owner}/{repo} |")
    return rows, failed


def landing_zone_drift():
    dims = yaml.safe_load((ROOT / "dimensions.yaml").read_text(encoding="utf-8"))
    pinned = set(dims["landingZone"]["parameters"])
    live = set(re.findall(r"^param ([A-Za-z0-9_]+)", fetch(LANDING_ZONE_MAIN), re.M))
    return sorted(live - pinned), sorted(pinned - live), dims["landingZone"]["commit"]


def checklist_drift():
    ref = yaml.safe_load((ROOT / "references" / "review-checklists-avd.yaml").read_text(encoding="utf-8"))
    pinned = {c["id"] for c in ref.get("claims") or []}
    live = json.loads(fetch(CHECKLIST_MAIN))["items"]
    live_ids = {i["id"] for i in live}
    pinned_commit = re.search(r"/blob/([0-9a-f]{40})/", ref["pin"]).group(1)
    removed = sorted(pinned - live_ids)
    unpinned = sorted(live_ids - pinned)
    return removed, unpinned, len(live), pinned_commit


def main():
    refs = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "references").glob("*.yaml"))]
    out = ["# Pin drift report", ""]
    failures = []

    learn, failed = learn_drift(refs)
    failures += failed
    out.append(f"## Learn pages whose commit moved ({len(learn)})")
    out.append("")
    if learn:
        out += ["| Reference | Pinned | Live | Claims to re-read | Page |", "|---|---|---|---|---|"] + learn
    else:
        out.append("None.")
    out.append("")

    gh, failed = github_drift(refs)
    failures += failed
    out.append(f"## GitHub sources whose pinned path is gone at the branch head ({len(gh)})")
    out.append("")
    out += (["| Reference | Path | Repo |", "|---|---|---|"] + gh) if gh else ["None."]
    out.append("")

    try:
        new, gone, commit = landing_zone_drift()
        out.append(f"## Landing zone parameters against dimensions.yaml (pinned at `{commit[:7]}`)")
        out.append("")
        out.append(f"- New at head, no dimension yet: {', '.join(f'`{p}`' for p in new) or 'none'}")
        out.append(f"- Pinned but gone at head: {', '.join(f'`{p}`' for p in gone) or 'none'}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        failures.append(f"landing zone: {e}")
    out.append("")

    try:
        removed, unpinned, total, commit = checklist_drift()
        out.append(f"## AVD review checklist against the pinned claims (pinned at `{commit[:7]}`)")
        out.append("")
        out.append(f"- Items at head: {total}; pinned as claims: {total - len(unpinned)}; not yet pinned: {len(unpinned)}")
        out.append(f"- Pinned items no longer at head: {', '.join(f'`{i}`' for i in removed) or 'none'}")
    except (urllib.error.URLError, TimeoutError, OSError, KeyError) as e:
        failures.append(f"checklist: {e}")
    out.append("")

    if failures:
        out.append("## Could not check")
        out.append("")
        out += [f"- {f}" for f in failures]
        out.append("")
    out.append("A pin moves only by a reviewed pull request: re-read the page, update the claims that changed, and move the pin and `read` date together.")
    text = "\n".join(out) + "\n"
    print(text)
    if "--write-report" in sys.argv:
        Path(sys.argv[sys.argv.index("--write-report") + 1]).write_text(text, encoding="utf-8")
    drift = bool(learn or gh)
    print(f"RESULT {'DRIFT' if drift else 'OK'} ({len(learn)} Learn, {len(gh)} GitHub, {len(failures)} unchecked)")
    return 2 if failures and not (learn or gh) and len(failures) > len(refs) // 2 else 0


if __name__ == "__main__":
    sys.exit(main())
