# avd-assess

Part of [avd-ops](https://avd-ops.dev/), the open toolkit for Azure Virtual Desktop.

An open, curated methodology for assessing Azure Virtual Desktop estates: what to collect, how to judge it, what good looks like, and how to score it. It is a research index. It links to what Microsoft and the community already publish, pinned so a reader can see exactly what each source said on the day we read it. It adds what our own runs observed about those sources, and it writes new method only where nothing exists.

Where it sits in the family: [avd-landing-zone](https://github.com/avd-ops/avd-landing-zone) is how an estate is built and changed from here, [avd-current-state](https://github.com/avd-ops/avd-current-state) is what is there now, and avd-assess is what it should be, and why: the standards both engines read. It also holds the [foundation contracts](contracts/README.md), the formats those three repos exchange, which work the same with or without the layers above them.

> [!WARNING]
> **Personal project. Research and learning only. Not for production. No warranty.**
>
> - This is my own personal project, built on my own time **for research and learning**. It is **not affiliated with, endorsed by or supported by my employer, Liquidware or Microsoft**, and it does not represent their views, products or guidance. It is not an official Microsoft methodology.
> - Nothing here is a production-readiness certification, a compliance attestation or a security audit. Check every recommendation against its source and try it in a lab first.
> - It is provided **"as is", without warranty of any kind**, under the [MIT License](LICENSE). You use it at your own risk.
> - **Contributions and forks are welcome and encouraged.** See [Contributing](#contributing).

## Start here: the methods

| Method | Answers |
|---|---|
| [Collection](methods/collection.md) | What to collect about an estate, from where, and how private each fact is |
| [Assessment](methods/assessment.md) | How to judge what was collected against published recommendations |
| [Remediation](methods/remediation.md) | How reviewed findings become an ordered plan of landing zone changes (contract C24) |
| [Targets and benchmarks](methods/targets-benchmarks.md) | What good looks like, as numbers with their sources |
| [Scoring](methods/scoring.md) | How outcomes roll up, and which design decisions the evidence can support |
| [Sample check](methods/sample-check.md) | A short, point-in-time health check of measured user experience, built on the four above |
| [Baseline profile](methods/baseline-profile.md) | What good looks like for a host pool of each workload class: experience, utilization, density |
| [Tune and rightsize](methods/tune-rightsize.md) | A repeatable loop to move a running estate toward its profile at the lowest cost that keeps it there |
| [Use cases](methods/use-cases.md) | Who uses the estate for what (personas, apps, performance, security and compliance needs), and what that says it should be |
| [FinOps](methods/finops.md) | How to judge what an estate costs against Microsoft's and the FinOps Framework's guidance, and which repo holds which part |
| [Security](methods/security.md) | How to judge an estate's security against Microsoft's AVD guidance, and which repo holds which part |
| [Remote protocol and session](methods/remote-protocols.md) | How sessions reach their hosts: RDP transport, Shortpath and Multipath, judged against the networks users connect from, plus the session settings that ride on it |
| [Network](methods/network.md) | How to judge an estate's network, Azure side and client side (AVD Private Link on both), and what can be measured from outside |
| [Reliability](methods/reliability.md) | How to judge zones, backup, continuity and disaster recovery against the workload's own targets, and why only a test proves recovery |

Every step on those pages cites one of three things:

- **`ref:`** a claim from a published source, in [references/](references/). Each source is pinned to a commit or a dated version. We keep a claim ID and one line in our own words, never the source's text.
- **`obs:`** what our own runs showed about a claim, in [observations/](observations/): agrees, disagrees, extends, or not yet tested, with links to the evidence.
- **`gap:`** method we wrote because no source covers it, in [gaps/](gaps/). Each gap says what was searched and not found, and is retired when a source appears.

The [use case library](use-cases.yaml) holds common AVD use cases (task worker, knowledge worker, developer, graphics, contact center, contractor, external customer, plus overlays such as regulated data or an app that can't share a host) as cited starting points for the [use case method](methods/use-cases.md): each says what it usually needs, what usually goes wrong, and what would move a persona elsewhere. How it is built is in [gaps/use-case-library.md](gaps/use-case-library.md).

The [gold-standard registry](gold-standards.yaml) names, for each metric, the claim the methods treat as the reference and its standing (candidate, gold, baseline or demoted). How an entry is promoted or demoted is in [gaps/gold-standards.md](gaps/gold-standards.md).

## The map

Beyond the methods, this repo holds the **map**: one row for every detail an AVD estate is built and assessed by, in [dimensions.yaml](dimensions.yaml), each in one pillar of [pillars.yaml](pillars.yaml). A row says what the detail decides, which pinned upstream claims (or which gap page) say what good is, the facts that measure it, the checks that judge it and the landing zone parameters that set it. It is not a shadow source: where a source exists the row links to it and restates nothing. [map.json](map.json) is the same map as JSON (contract C20, `avd-assess-map/v1`) with the [baselines](baselines.yaml), the [use case library](use-cases.yaml) and the [gold-standard registry](gold-standards.yaml), for readers such as the standards library. A pillar's status in `pillars.yaml` says whether its rows exist yet; the weekly [pins workflow](.github/workflows/pins.yml) reports which checklist items and landing zone parameters still have no row, and which pins have moved.

## What this repo is not

- **No tools.** Nothing here touches Azure. [avd-current-state](https://github.com/avd-ops/avd-current-state) implements the collection and assessment methods, and [avd-second-brain](https://github.com/avd-ops/avd-second-brain) cites them. Both read a pinned copy.
- **No copied guidance.** Microsoft's pages, checklists and tools stay the source of truth. When our observation disagrees with a source, we record it here and offer it back upstream.
- **No estate data.** Observations link to public lessons, run records and knowledge base pages. No tenant, customer, user or machine data goes into this repo.

## How to cite

Cite a claim as `avd-assess@<commit>:references/<file>.yaml#<claim>`, an observation as `avd-assess@<commit>:observations/<file>.yaml`, a gap as `avd-assess@<commit>:gaps/<file>.md`, and a check as `avd-assess@<commit>:method.json#<check id>`.

[method.json](method.json) is the part a tool runs: where each fact comes from, the checks, what each design decision needs, the scoring, and a remediation hint per check (the landing zone parameter or setting that fixes it). [avd-current-state](https://github.com/avd-ops/avd-current-state) runs a pinned copy. The design is in [docs/assess-spec.md](docs/assess-spec.md).

## Checks

```bash
pip install pyyaml jsonschema
python3 scripts/build_index.py --check
python3 tests/check_method.py
python3 tests/check_contracts.py
python3 tests/check_baselines.py
python3 tests/check_use_cases.py
python3 scripts/check_evidence.py
python3 tests/check_wording.py
```

`index.json` and `map.json` are generated: after changing a reference, an observation, a gap, a pillar, a dimension, a baseline, a use case or a registry entry, run `python3 scripts/build_index.py` and commit the result. They are the same content as JSON (contract C20, `avd-assess-index/v1` and `avd-assess-map/v1`, in [contracts/](contracts/README.md)), so the brain, avd-current-state and the standards library read them without a YAML parser.

The check verifies that every reference has a pin, a read date and claims; every observation and method step cites something that exists; every registry entry cites a claim that exists and has the evidence its standing needs; `index.json` and `method.json` match their schemas in [contracts/](contracts/README.md); every check in `method.json` cites real claims and built facts; and no file holds a GUID, email address or IP address. `tests/check_contracts.py` checks the foundation contracts themselves. `tests/check_wording.py` refuses third-party product names: products appear as categories, with their public documentation pinned as a reference ([tests/wording.json](tests/wording.json)).

Pins: a GitHub source is pinned to a commit. A Learn page is pinned by its own `git_commit_id` and `updated_at`, which identify the version but, because the source repository behind most Learn pages is private, can't be opened by a reader; a reference may therefore also carry `archive:`, an archived snapshot of the page taken on the read date, which is the copy a reader opens. The weekly [pins workflow](.github/workflows/pins.yml) compares every pin with its live source and opens one issue naming the claims to re-read; a pin moves only by a reviewed pull request.

## Contributing

Contributions and forks are welcome and encouraged. Fork it and make it your own, or send back what you learn: open an issue or a pull request with a new source, a better pin, or an observation from a real run that agrees or disagrees with a source. Measured results go through the [evidence intake](evidence/README.md): one checked file per submission, aggregates only. We use the same path for our own runs. Small pull requests are easiest to review.

Before you open one, run `python3 scripts/build_index.py`, `python3 tests/check_method.py`, `python3 tests/check_contracts.py`, `python3 tests/check_dimensions.py`, `python3 tests/check_baselines.py`, `python3 tests/check_use_cases.py` and `python3 tests/check_wording.py` as the [check workflow](.github/workflows/check.yml) does. Keep tenant data, IDs and secrets out of the repo, issues and pull requests. By contributing, you agree your contributions are licensed under the repo's [MIT License](LICENSE).

## License

[MIT](LICENSE).
