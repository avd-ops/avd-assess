# CLAUDE.md

avd-assess: the AVD family's assessment methodology (collection, assessment, targets and benchmarks, scoring) as a research index. Design: `docs/assess-spec.md` (moved here from avd-second-brain). Roles: avd-landing-zone is how an estate is built and changed from here, avd-current-state is what is there now, avd-assess is what it should be and why.

## Validate before pushing
```bash
python3 scripts/build_index.py --check   # index.json, map.json and endpoints.json are generated; run without --check to rebuild
python3 tests/check_method.py
python3 tests/check_contracts.py
python3 tests/check_dimensions.py
python3 tests/check_baselines.py
python3 tests/check_use_cases.py
python3 tests/check_endpoints.py         # the endpoint map: pins, no addresses, probe rules, schema
python3 tests/check_wording.py           # third-party products as categories only (tests/wording.json)
python3 tests/check_bundle.py            # release tooling: verifier fixtures, diff rules, leak scan, schema $id
python3 scripts/bundle/build_bundle.py --check   # release bundle dry run from HEAD's git blobs (commit first)
pwsh -c "Invoke-Pester ./tests/AvdAssessBundle.Tests.ps1 -CI"   # the PowerShell verifier, same fixtures
```

## Rules
- **Methodology only, no tools: the map and the dictionary.** Nothing here calls Azure or runs a probe. avd-current-state implements the method; avd-second-brain cites it. Reference data the tools read is allowed when each row is a pointer to a pinned upstream claim plus what the source doesn't say: the endpoint map (`endpoints.yaml`, `gap:endpoint-map`) is the one case today. The only other code that ships is the release bundle's verifiers and diff (`tools/`), which read local files.
- **Sessions never tag or release.** The map is published as an immutable, attested release bundle ([distribution spec](docs/distribution-spec.md)); only the owner creates `v*` tags, from Cloud Shell, and approves the `release` environment. A session may open a release PR (with `tools/diff_bundle.py` output and any `BREAKING:` or `NOT-BREAKING:` lines), never push a tag, create a release or move a consumer's pin without the owner's go.
- **Not a shadow source: a map.** Where an upstream source exists, link to it pinned; never restate it. What this repo holds is the map: one row in `dimensions.yaml` for every detail an estate is built and assessed by, in a pillar from `pillars.yaml`, pointing at an upstream claim, an observation or a gap, plus the facts that measure it, the checks that judge it and the landing zone parameters that set it. A new topic is a row before it is a page. The endpoint map follows the same rule: one row per endpoint a family tool probes or must report as not tested, citing the pinned claim that lists it, carrying only what a probe needs from the source (name, protocol, port, the service tag where given) plus our own fields; purposes in our own words, no address or range restated, the source's descriptions and other clouds left on the page.
- **This repo holds the foundation contracts** (`contracts/`: C11, C15, C17, C19, C20, C21, C23, C24), the authority the landing zone, avd-current-state, the brain and avd-swarm vendor (brain decision 0021). Upstream use is supported, never required, and upstream input fails open: follow the rules in [contracts/README.md](contracts/README.md). A contract change starts here, then the producers and readers follow.
- **Don't reinvent.** Link out to the published source with an immutable pin (a commit SHA, or a Learn page's `git_commit_id` and `updated_at`). Store a claim ID and one line in our own words, never the source's text.
- **Our value is observations.** Each one links public family evidence (a lesson, a run record, a KB page). A `disagrees` verdict also goes to avd-second-brain's upstream list.
- **Write method only for a gap**, and say what was searched and not found.
- **A model never decides** a verdict or an outcome.
- **No GUIDs, emails, IPs, tenant, customer, user or machine names**, and no secrets. Cite review checklist items by short ID (`A01.01`), never by GUID.
- **Liquidware is the only partner named.** Third-party products appear as categories (an SSE or ZTNA client, a VPN client, an endpoint detection and response product, a monitoring product) with their public documentation pinned as a reference, never by product name; `tests/check_wording.py` refuses the names in `tests/wording.json`. Prior-art comparisons that must name a product stay in the owner's private notes.
- **Personal project, not for production, as is, not affiliated with the author's employer, Liquidware or Microsoft.** The README warning and LICENSE stay.
- **American English.**
