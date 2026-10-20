# Gap: gold standards

**Searched (2026-10-20):** Microsoft Learn (the Well-Architected Review, AVD documentation), the review checklist, GitHub, the web. **Not found:** a published rule for deciding which source an assessment treats as its reference for a threshold, and for changing that choice when evidence disagrees. Sources state numbers; none says how to rank them against each other or against real runs.

**What we write.** A registry, [gold-standards.yaml](../gold-standards.yaml), with one entry per metric or judgment the method makes. Each entry names the claim the method uses and its standing:

| Standing | Means | How an entry gets there |
|---|---|---|
| `candidate` | The best source we have; the method uses it | A pinned `published` or `guidance` claim in [references/](../references/) |
| `gold` | The reference the family adopts and other sources are compared with | A candidate with at least one `agrees` or `extends` observation backed by evidence, and no open `disagrees` |
| `baseline` | No source has a number; the estate's own measurement sets one | The metric matters but nothing is published (for example `gap:logon-target`) |
| `demoted` | No longer used; kept so the history stays readable | A `disagrees` observation with evidence, a source withdrawn or changed so the pin no longer says it, or a better source |

## Rules

1. **A person changes a standing, by pull request,** with the observation or source change that justifies it linked in the entry's `why`. A model may draft the entry; it never decides one (the repo rule).
2. **Promotion needs evidence from a run,** submitted through the evidence intake (`gap:evidence-intake`), not agreement between sources. Two sources saying the same number make one candidate stronger; they don't make it gold.
3. **Demotion keeps the entry.** A demoted entry stays with its date and reason, and the replacement names it in `replaces`.
4. **One standing per metric at a time.** Two candidates for one metric are allowed only when they measure different things (for example per host and per session); the entry says which.
5. **Re-read pins on a cadence.** When a source's pin moves, the entry is checked again; a changed number is a new claim, and the old one is demoted with the reason "source changed".
6. **A source we can't name or pin publicly can't be a public gold standard.** Its numbers may inform a private comparison, but the public method cites only pinned, linkable sources, our observations or a gap.
