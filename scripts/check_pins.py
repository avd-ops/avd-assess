#!/usr/bin/env python3
"""Reports pin drift: a Learn page whose git_commit_id no longer matches a reference's pin, a GitHub
source whose pinned path no longer exists at its default branch, new or removed landing zone parameters
against dimensions.yaml, and new or removed AVD review checklist items against the pinned claims. It only
reports; nothing moves a pin except a reviewed pull request. Run by .github/workflows/pins.yml weekly,
which opens or updates one issue with the output.

Usage: python3 scripts/check_pins.py [--write-report FILE]
The report is always written, with a "Could not check" section for anything a fetch failed on, and the
exit code is 0: drift is a to-do, not a failure. Under GitHub Actions it also writes items= (drift found)
and unchecked= (fetches that failed) to $GITHUB_OUTPUT; the workflow closes its issue when both are 0.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEARN_PIN = re.compile(r"^Learn git_commit_id ([0-9a-f]{40}), updated_at (\d{4}-\d{2}-\d{2})$")
GITHUB_PIN = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/(blob|tree)/[0-9a-f]{40}(?:/(.*))?$")
META = re.compile(r'<meta name="(git_commit_id|updated_at)" content="([^"]+)"')
CHECKLIST = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/avd_checklist.en.json"
UA = {"User-Agent": "avd-assess pin check (https://github.com/avd-ops/avd-assess)"}
TIMEOUT = 20
WORKERS = 4
RETRY_CAP = 30  # seconds; the longest Retry-After we honor before the one retry


def retry_after(error):
    """Seconds to wait before retrying a 429 or 5xx, or None for an error worth reporting at once."""
    if not isinstance(error, urllib.error.HTTPError) or not (error.code == 429 or 500 <= error.code < 600):
        return None
    try:
        return min(RETRY_CAP, max(1, int(error.headers.get("Retry-After", ""))))
    except (TypeError, ValueError):
        return 5


def fetch(url, method="GET"):
    """One retry, after a backoff, on a rate limit (429) or server error (5xx): Learn rate-limits a
    weekly run of every page, and a transient error is not drift."""
    req = urllib.request.Request(url, headers=UA, method=method)
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", "replace") if method == "GET" else ""
        except urllib.error.HTTPError as e:
            wait = retry_after(e)
            if attempt == 2 or wait is None:
                raise
            time.sleep(wait)


def exists(owner, repo, branch, path):
    """True if the path exists at the branch, False if GitHub says 404, None if it can't be checked.
    github.com answers for files and folders; raw.githubusercontent.com only for files, but it is the
    one host some build containers can reach, so it is the fallback for files and, best effort, for a
    folder's README; a folder raw can't see stays unchecked rather than reported gone."""
    for url, kinds in ((f"https://github.com/{owner}/{repo}/tree/{branch}/{path}".rstrip("/"), "any"),
                       (f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}".rstrip("/"), "file"),
                       (f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}/README.md".replace("//README", "/README"), "folder")):
        try:
            fetch(url, "HEAD")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404 and kinds == "any":
                return False
            continue  # raw can't say a folder is gone (it may just have no README); only github.com can
        except Exception:
            continue
    return None


def default_branch(owner, repo):
    """The repo's default branch from the API, or the first of main and master whose root README answers."""
    try:
        return json.loads(fetch(f"https://api.github.com/repos/{owner}/{repo}"))["default_branch"]
    except Exception:  # the API is rate-limited or blocked; probe the usual names instead
        for branch in ("main", "master"):
            if exists(owner, repo, branch, ""):
                return branch
    return None


def learn_one(ref):
    m = LEARN_PIN.match(str(ref.get("pin", "")))
    if not m:
        return None
    try:
        meta = dict(META.findall(fetch(ref["url"])))
    except Exception as e:
        return ("fail", f"{ref['id']}: {e}")
    if meta.get("git_commit_id", "") != m.group(1):
        return ("drift", f"| `{ref['id']}` | {m.group(2)} | {meta.get('updated_at', '?')[:10]} | {len(ref.get('claims') or [])} | {ref['url']} |")
    return ("ok", "")


def github_one(ref):
    m = GITHUB_PIN.match(str(ref.get("pin", "")))
    if not m:
        return None
    owner, repo, kind, path = m.groups()
    branch = default_branch(owner, repo)
    if branch is None:
        return ("fail", f"{ref['id']}: no default branch found for {owner}/{repo}")
    found = exists(owner, repo, branch, path or "")
    if found is None:
        return ("fail", f"{ref['id']}: {owner}/{repo} {kind} {path or '(root)'} at {branch} could not be checked from here")
    if not found:
        return ("drift", f"| `{ref['id']}` | {path or '(repo root)'} | {owner}/{repo} |")
    return ("ok", "")


def run(fn, refs):
    rows, failed = [], []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for result in pool.map(fn, refs):
            if result is None:
                continue
            kind, text = result
            if kind == "drift":
                rows.append(text)
            elif kind == "fail":
                failed.append(text)
    return rows, failed


def landing_zone_drift():
    dims = yaml.safe_load((ROOT / "dimensions.yaml").read_text(encoding="utf-8"))
    lz = dims["landingZone"]
    m = re.match(r"^https://github\.com/([^/]+)/([^/]+)/blob/[0-9a-f]{40}/(.+)$", lz["source"])
    owner, repo, path = m.groups()
    branch = default_branch(owner, repo)
    if branch is None:
        raise RuntimeError(f"no default branch found for {owner}/{repo}")
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    live = set(re.findall(r"^param ([A-Za-z0-9_]+)", fetch(url), re.M))
    pinned = set(lz["parameters"])
    return sorted(live - pinned), sorted(pinned - live), lz["commit"], url


def checklist_drift():
    ref = yaml.safe_load((ROOT / "references" / "review-checklists-avd.yaml").read_text(encoding="utf-8"))
    pinned = {c["id"] for c in ref.get("claims") or []}
    live_ids = {i["id"] for i in json.loads(fetch(CHECKLIST))["items"]}
    pinned_commit = re.search(r"/blob/([0-9a-f]{40})/", str(ref["pin"]))
    return sorted(pinned - live_ids), sorted(live_ids - pinned), len(live_ids), pinned_commit.group(1) if pinned_commit else "?"


def main():
    refs = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "references").glob("*.yaml"))]
    out = ["# Pin drift report", ""]
    failures = []
    items = 0

    learn, failed = run(learn_one, refs)
    failures += failed
    out += [f"## Learn pages whose commit moved ({len(learn)})", ""]
    out += (["| Reference | Pinned | Live | Claims to re-read | Page |", "|---|---|---|---|---|"] + learn) if learn else ["None."]
    out.append("")

    gh, failed = run(github_one, refs)
    failures += failed
    out += [f"## GitHub sources whose pinned path is gone at the default branch ({len(gh)})", ""]
    out += (["| Reference | Path | Repo |", "|---|---|---|"] + gh) if gh else ["None."]
    out.append("")

    try:
        new, gone, commit, url = landing_zone_drift()
        items += len(new) + len(gone)
        out += [f"## Landing zone parameters against dimensions.yaml (pinned at `{commit[:7]}`, compared with {url})", ""]
        out.append(f"- New at head, no dimension yet: {', '.join(f'`{p}`' for p in new) or 'none'}")
        out.append(f"- Pinned but gone at head: {', '.join(f'`{p}`' for p in gone) or 'none'}")
    except Exception as e:
        failures.append(f"landing zone: {e}")
    out.append("")

    try:
        removed, unpinned, total, commit = checklist_drift()
        items += len(removed) + len(unpinned)
        out += [f"## AVD review checklist against the pinned claims (pinned at `{commit[:7]}`)", ""]
        out.append(f"- Items at head: {total}; pinned as claims: {total - len(unpinned)}; not yet pinned: {len(unpinned)}")
        out.append(f"- Pinned items no longer at head: {', '.join(f'`{i}`' for i in removed) or 'none'}")
    except Exception as e:
        failures.append(f"checklist: {e}")
    out.append("")

    if failures:
        out += ["## Could not check", ""] + [f"- {f}" for f in failures] + [""]
    out.append("A pin moves only by a reviewed pull request: re-read the page, update the claims that changed, and move the pin and `read` date together.")
    text = "\n".join(out) + "\n"
    print(text)
    if "--write-report" in sys.argv:
        Path(sys.argv[sys.argv.index("--write-report") + 1]).write_text(text, encoding="utf-8")
    items += len(learn) + len(gh)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"items={items}\nunchecked={len(failures)}\n")
    print(f"RESULT {'DRIFT' if items else 'OK'} ({items} items: {len(learn)} Learn, {len(gh)} GitHub, the rest landing zone and checklist; {len(failures)} unchecked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
