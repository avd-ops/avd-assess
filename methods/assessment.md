# Assessment method

How to judge what was collected against published recommendations. avd-current-state implements this method and writes the report (avd-second-brain contract C21).

## Baseline

Microsoft publishes no single AVD assessment standard, so the baseline is three public sources, each for one job:

- **Scope** (what an assessment must answer): the Cloud Adoption Framework's AVD assessment questions (`ref:caf-avd-assess`). Microsoft is retiring that page; the pin keeps it.
- **Items** (what to check, with short IDs, pillar and severity): the AVD review checklist (`ref:review-checklists-avd`), with APRL through WARA for reliability (`ref:aprl-desktop-virtualization`, `ref:wara`).
- **Questionnaire** (the design-choice self-assessment): the Well-Architected Review, core plus the AVD workload review (`ref:waf-review-assessment#avd-workload-review`).

Everything else here builds on those three: evidence mapped to items, measured targets, scoring and our own observations.

## Method

1. **Start from Microsoft's lists, not ours:** the AVD review checklist for all pillars (`ref:review-checklists-avd`) and APRL through WARA for reliability (`ref:aprl-desktop-virtualization`, `ref:wara#collector-avd-json`).
2. **Map each item to the facts that decide it**, and leave the rest `unknown` with the data they would need (`gap:checklist-mapping`).
3. **Give each check one of four outcomes:** pass, warn (a trade-off to review), gap, or unknown. Unknown is never guessed, and a model never decides an outcome (`gap:scoring`).
4. **Judge the image against the landing zone's reviewed WDOT profile**, not against every WDOT item: some items destroy evidence or break sysprep (`ref:wdot#categories`, `obs:wdot-disk-cleanup-deletes-evidence`, `obs:wdot-appx-removal-left-off`).
5. **Use the Well-Architected checklists' codes** (RE:04 and the rest) to place each finding in its pillar (`ref:waf-reliability-checklist#RE:04`).
6. **Repeat on a cadence** and compare to the last run, as the Well-Architected Review does with milestones (`ref:waf-review-assessment#milestones`).

## Not yet known

- Most checklist items aren't mapped yet; version 1 maps a handful (`gap:checklist-mapping`).
- Whether our outcomes agree with the Well-Architected Review's own answers for the same estate has not been tested (`ref:waf-review-assessment#questionnaire`).
