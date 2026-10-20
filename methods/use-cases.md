# Use case method

Who uses the estate, for what, and what that means it should be. Collection says what is there and assessment judges it against published guidance; this method supplies the other half of "should be": the personas, their apps, their performance and experience needs, and their security and compliance needs. It is the analysis side of discovery, the second stage of an assessment (`gap:discovery`). avd-current-state checks a use case record against what it collects; nothing here needs a layer above it.

## Method

1. **Start from the default, then test it.** Assume one persona with the proof of concept's assumptions (one shared pool, multi-session compatible apps, light density, low latency) and look for what breaks each one (`ref:caf-avd-poc#assumptions`, `ref:caf-avd-poc#assumptions-rarely-all-true`, `ref:caf-avd-assess#assumption-validation`). The landing zone builds that default today (`obs:landing-zone-one-persona`).
2. **Interview before you group.** Run the discovery questions by role; structured answers go to the intake, narrative stays in the operator's private evidence (`gap:discovery`).
3. **Group users into personas** by the eight published criteria: dedicated or pooled, density, performance, GPU, where they work from, business function, user count and peak sessions (`ref:caf-avd-assess#persona-criteria`). Fold any group under 10 users into its nearest neighbor (`gap:use-cases`).
4. **Give each persona a workload type** from the published examples, as a prior to be measured, not a fact (`ref:session-host-sizing#workload-types`, `ref:session-host-sizing#estimates-only`, `obs:users-per-vcpu-adopted`).
5. **Ask the app questions per persona:** installed apps and Microsoft 365 decide the image, multi-session compatibility decides pooled or personal, and back-end latency can decide the region or block the persona until the app moves (`ref:caf-avd-assess#app-questions`, `ref:caf-avd-deploy#legacy-apps-personal`, `ref:caf-avd-deploy#app-remediation-blocks`). Where personas share a pool, deliver their different apps by assignment, not by separate images (`ref:app-attach#per-user-per-host-pool`).
6. **Record security and compliance needs per persona:** who may share a host, which data controls the session must enforce, and how critical the work is, which sets reliability targets before anything else (`gap:use-cases`, `ref:waf-reliability-checklist#RE:04`).
7. **Write each persona as a structured record** with no names: enums, counts, public regions and clock times (`gap:use-cases`). Absent records mean the default from step 1.
8. **Map each record to the design decisions it informs**, one persona to one host pool configuration (`ref:caf-avd-assess#persona-to-host-pool`, `gap:use-cases`).
9. **Check each record against what is there:** the deployed host pool type, application groups, sizes, session limits and region from current-state facts, and, once measured, concurrency, per-user demand, profile size and latency from the users' side (`gap:use-cases`, `ref:avd-insights-use-cases#utilization-for-scaling`, `obs:region-latency-from-the-user`). Each field gets pass, warn, gap or unknown; a model never decides which (`gap:scoring`).
10. **Plan in persona iterations,** one persona and host pool at a time, so the business absorbs one change at once (`ref:caf-avd-deploy#persona-iterations`).
11. **Repeat when use changes,** not only on the assessment cadence: a new team, a new app or a move to new regions reopens the record (`ref:waf-review-assessment#milestones`).

## Where it fits

| Assessment stage | This method's part |
|---|---|
| 1. Collection | none; it reads the current-state facts collection writes |
| 2. Discovery | the persona, app and control questions (`gap:discovery`) |
| 3. Analysis | steps 3 to 9: the record, the decisions it informs, and the check against what is there |
| 4. Review | each `gap` or `warn` is a finding a person reviews against the private narrative |
| 5. Recommendations | step 10: persona iterations become the order of the plan |

The second brain can keep the record over the estate's life as the reason behind each decision. That is an optional reader: the record, this method and avd-current-state's checks work the same without it.

## Not yet known

- The record isn't in the intake contract or the fact register yet; it is proposed in `gap:use-cases`.
- Whether published workload types agree with measured per-user demand hasn't been tested on real users (`obs:users-per-vcpu-adopted`).
- No published source covers personas after the Framework's AVD pages leave Learn (`ref:caf-avd-assess#deprecated`); the pins keep the citations working.
