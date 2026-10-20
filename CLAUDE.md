# CLAUDE.md

avd-assess: the AVD family's assessment methodology (collection, assessment, targets and benchmarks, scoring) as a research index. Design: `docs/assess-spec.md` (moved here from avd-second-brain). Roles: avd-landing-zone is how an estate is built and changed from here, avd-current-state is what is there now, avd-assess is what it should be and why.

## Validate before pushing
```bash
python3 scripts/build_index.py --check   # index.json is generated; run without --check to rebuild
python3 tests/check_method.py
python3 tests/check_contracts.py
```

## Rules
- **Methodology only, no tools.** Nothing here calls Azure. avd-current-state implements the method; avd-second-brain cites it.
- **This repo holds the foundation contracts** (`contracts/`: C11, C15, C17, C19, C20, C21), the authority the landing zone, avd-current-state, the brain and avd-swarm vendor (brain decision 0021). Upstream use is supported, never required, and upstream input fails open: follow the rules in [contracts/README.md](contracts/README.md). A contract change starts here, then the producers and readers follow.
- **Don't reinvent.** Link out to the published source with an immutable pin (a commit SHA, or a Learn page's `git_commit_id` and `updated_at`). Store a claim ID and one line in our own words, never the source's text.
- **Our value is observations.** Each one links public family evidence (a lesson, a run record, a KB page). A `disagrees` verdict also goes to avd-second-brain's upstream list.
- **Write method only for a gap**, and say what was searched and not found.
- **A model never decides** a verdict or an outcome.
- **No GUIDs, emails, IPs, tenant, customer, user or machine names**, and no secrets. Cite review checklist items by short ID (`A01.01`), never by GUID.
- **Liquidware is the only partner named.** Other vendors appear only as prior art, never by product name in public text unless explaining how we differ.
- **Personal project, not for production, as is, not affiliated with the author's employer, Liquidware or Microsoft.** The README warning and LICENSE stay.
- **American English.**
