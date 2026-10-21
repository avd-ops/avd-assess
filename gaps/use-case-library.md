# Gap: use case library

**Searched (2026-10-21):** Microsoft Learn: the session host sizing guide's workload types (`ref:session-host-sizing#workload-types`), the Cloud Adoption Framework's AVD assessment and innovation pages (`ref:caf-avd-assess`, `ref:caf-avd-innovate`), AVD on Surface (`ref:avd-surface-scenarios`), the Architecture Center's AVD for Azure Local and GIS example scenario (`ref:avd-azure-local-workload`, `ref:avd-gis-workload-example`), licensing and internal or external deployments (`ref:avd-licensing`, `ref:avd-internal-external`), multimedia redirection (`ref:multimedia-redirection`), a contact center voice page (`ref:contact-center-voice-avd`), the AVD security guide and review checklist, and Azure Migrate. Also the workload profiles that load simulation tools publish for benchmarking. **Not found:** a maintained, public, vendor-neutral library of AVD use cases, each with the traits that set its design decisions, the risks that come with it, and the sources behind both.

- Microsoft names use cases in pieces: four workload types by example users (`ref:session-host-sizing#workload-types`), three innovation scenarios (`ref:caf-avd-innovate#temporary-workers`, `ref:caf-avd-innovate#latency-sensitive-apps`, `ref:caf-avd-innovate#secure-environments`), five business conversations on a device page (`ref:avd-surface-scenarios#business-conversations`), and the internal and external split in licensing (`ref:avd-licensing#contractors-are-internal`, `ref:avd-internal-external#tenant-per-customer`). None ties a use case to the decisions it moves, and the Framework pages leave Learn on 2026-10-30 (`ref:caf-avd-innovate#deprecated`).
- The workload types are examples, and Microsoft points to load simulation and real use to replace them (`ref:session-host-sizing#estimates-only`, `ref:avd-azure-local-workload#workload-types-examples`).
- App vendors can publish their own tiers for one app, which beat the generic types for that app (`ref:avd-gis-workload-example#app-specific-tiers`).
- Load simulation tools publish scripted user profiles for measuring density. They answer "how many of this load fit on a host", one of the published capacity approaches (`ref:session-host-sizing#capacity-approaches`); they don't say who an estate's users are, what they need besides compute, or which decision each need moves. We treat them as prior art only and copy nothing from them.

## What we write

[use-cases.yaml](../use-cases.yaml) (schema `avd-assess-use-cases/v1`, checked by `tests/check_use_cases.py`): common AVD use cases as **starting points** for the use case record (`gap:use-cases`), never as conclusions.

- **Two kinds of entry.** A **persona** is a base (task worker, knowledge worker, developer, graphics, contact center, contractor, external customer): it sets `function` and `workload`, and names the `baselines.yaml` class it is judged against (`gap:baseline-profile`). An **overlay** adds needs to any persona (an app that can't share a host, an app that needs its back end close, regulated data, a seasonal workforce) and sets neither. A persona in an estate starts from one base and any overlays.
- **Starting values use the record's own fields and enums,** so a match drops straight into the record. Values the library can't express as record fields yet (working pattern, media, endpoints) sit under `pattern` until the record gains them.
- **Every value says why or says it's a default.** A `why` line cites the claims behind the fields it sets, with a standing as in `baselines.yaml`; a starting value with no `why` is a default to confirm in discovery (`gap:discovery`), never evidence.
- **Risks** name what usually goes wrong for that use case, each with its source. A risk is a question for discovery and review, not a finding.
- **Breaks** say what discovery or measurement finds that moves a persona off the entry, and where to: another entry, or a field change.
- **Links** name the fact register decisions the entry moves most and the `dimensions.yaml` rows it leans on (`gap:deployment-dimensions`), so a reader goes from a use case to the baselines and checks that apply.

How it is used is in the use case method (step 4). The library is the one shared list: other tools, in this family or outside it, read it as a primitive and don't keep their own persona list; a use case they need is added here by pull request. The library holds no estate data: a match is recorded in the operator's record as enums, and groups under 10 users still fold into a neighbor (`gap:use-cases`).

## How an entry changes

- By a pull request a person merges, like the baselines.
- A starting value moves when measured evidence from the evidence intake (`gap:evidence-intake`) shows a use case's demand sits elsewhere, for example contact center agents measuring a class above light. Until then every workload stays a `prior` (`obs:users-per-vcpu-adopted`).
- A new entry needs at least one source for why it exists as its own use case, and at least one risk with a source. A use case that differs from an existing entry only in numbers is a measured profile, not a new entry.

## Not covered yet

Privileged administration desktops, shared kiosks and frontline devices, classrooms and labs, and AVD on Azure Local or other hosts outside Azure. Each needs its own sources before it is added.

## Not yet decided

- Whether the record carries which entries a persona started from (proposed: an optional `startedFrom` with one persona and its overlays), so a check can report where an estate's record departs from its starting point. It would land with `useCases` in the intake contract and the fact register in one version bump (`gap:use-cases`).
- Whether `pattern` (hours, media, endpoints) becomes record fields. Media and endpoints decide real things today (multimedia redirection, data controls) that the record can't say.
