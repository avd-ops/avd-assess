# avd-assess

An open, curated methodology for assessing Azure Virtual Desktop estates: what to collect, how to judge it, what good looks like, and how to score it. It is a research index. It links to what Microsoft and the community already publish, pinned so a reader can see exactly what each source said on the day we read it. It adds what our own runs observed about those sources, and it writes new method only where nothing exists.

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
| [Targets and benchmarks](methods/targets-benchmarks.md) | What good looks like, as numbers with their sources |
| [Scoring](methods/scoring.md) | How outcomes roll up, and which design decisions the evidence can support |
| [Sample check](methods/sample-check.md) | A short, point-in-time health check of measured user experience, built on the four above |

Every step on those pages cites one of three things:

- **`ref:`** a claim from a published source, in [references/](references/). Each source is pinned to a commit or a dated version. We keep a claim ID and one line in our own words, never the source's text.
- **`obs:`** what our own runs showed about a claim, in [observations/](observations/): agrees, disagrees, extends, or not yet tested, with links to the evidence.
- **`gap:`** method we wrote because no source covers it, in [gaps/](gaps/). Each gap says what was searched and not found, and is retired when a source appears.

The [gold-standard registry](gold-standards.yaml) names, for each metric, the claim the methods treat as the reference and its standing (candidate, gold, baseline or demoted). How an entry is promoted or demoted is in [gaps/gold-standards.md](gaps/gold-standards.md).

## What this repo is not

- **No tools.** Nothing here touches Azure. [avd-current-state](https://github.com/nickprignano/avd-current-state) implements the collection and assessment methods, and [avd-second-brain](https://github.com/nickprignano/avd-second-brain) cites them. Both read a pinned copy.
- **No copied guidance.** Microsoft's pages, checklists and tools stay the source of truth. When our observation disagrees with a source, we record it here and offer it back upstream.
- **No estate data.** Observations link to public lessons, run records and knowledge base pages. No tenant, customer, user or machine data goes into this repo.

## How to cite

Cite a claim as `avd-assess@<commit>:references/<file>.yaml#<claim>`, an observation as `avd-assess@<commit>:observations/<file>.yaml`, and a gap as `avd-assess@<commit>:gaps/<file>.md`. The design is in avd-second-brain's [assess spec](https://github.com/nickprignano/avd-second-brain/blob/main/docs/assess-spec.md).

## Checks

```bash
pip install pyyaml
python3 tests/check_method.py
```

The check verifies that every reference has a pin, a read date and claims; every observation and method step cites something that exists; every registry entry cites a claim that exists and has the evidence its standing needs; and no file holds a GUID, email address or IP address.

## Contributing

Contributions and forks are welcome and encouraged. Fork it and make it your own, or send back what you learn: open an issue or a pull request with a new source, a better pin, or an observation from a real run that agrees or disagrees with a source. Small pull requests are easiest to review.

Before you open one, run `python3 tests/check_method.py` as the [check workflow](.github/workflows/check.yml) does. Keep tenant data, IDs and secrets out of the repo, issues and pull requests. By contributing, you agree your contributions are licensed under the repo's [MIT License](LICENSE).

## License

[MIT](LICENSE).
