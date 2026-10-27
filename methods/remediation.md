# Remediation method

How to turn reviewed findings into an ordered plan of changes. This is the fifth stage of an assessment, after collection, discovery, analysis and review. avd-current-state's assessment portal writes the plan (contract C24, `avd-remediation-plan/v1`) from the assessment report (C21), its review (C23) and the hints in [method.json](../method.json). avd-landing-zone makes the changes; nothing here needs a layer above it.

## Method

1. **Plan what a person decided to fix, and what nobody reviewed.** Start from the review's Fix rows. Accept and Defer keep their reasons in the review and make no item, as the Well-Architected Review lets a team assign, postpone or dismiss a recommendation (`ref:waf-review-assessment#prioritize-with-tradeoffs`, `gap:remediation-plan`).
2. **Plan every finding that isn't a pass and has no review row,** marked unreviewed (all of them when there is no review), so nothing is hidden because nobody looked (`gap:remediation-plan`).
3. **Cite what good is and why for each item:** the check's own claims, the review checklist item or Well-Architected code it judged against (`ref:review-checklists-avd`, `ref:waf-reliability-checklist#RE:05`).
4. **Name the change and the target control plane, not the effort:** the target plane (`azure`, `entra`, `intune`, `m365`, `power-platform`, or `orchestrator`), the parameter and its public value, a setting a redeploy applies (`avd-entra`, `avd-intune`, `avd-m365`, `avd-azure`, `avd-power-platform`, or `avd-landing-zone`), or manual with a code (rebuilding hosts or removing orphaned device records are two). A value that is a name, prefix or address is never in the plan (`gap:remediation-plan`).
5. **An unknown outcome plans evidence, not a fix:** collect the missing fact and run again before changing anything (`gap:remediation-plan`, `gap:scoring`).
6. **Order by rule, not by judgment:** gap, then warn, then unknown; then severity; then check ID. The order is priority, not schedule. A person changes it through the review, and a model never does (`gap:remediation-plan`, `gap:scoring`).
7. **Group landing zone changes into one redeploy,** and plan persona-specific changes one persona and host pool at a time, so the business absorbs one change at once (`ref:caf-avd-deploy#persona-iterations`).
8. **Put the plan in the backlog and track each item until it is resolved:** the next assessment is the evidence that it worked (`ref:waf-review-assessment#export-to-backlog`, `ref:waf-review-assessment#track-until-resolved`).
9. **Compare against the last run:** an item whose check now passes is done; one whose outcome changed asks for a new review decision (`ref:waf-review-assessment#milestones`).

## Where it fits

| Assessment stage | This method's part |
|---|---|
| 1. Collection | none |
| 2. Discovery | none; persona iterations come from the use case method |
| 3. Analysis | none; it reads the C21 report |
| 4. Review | its input: the C23 Fix rows |
| 5. Recommendations | steps 1 to 9 and the C24 plan |

The second brain may import the plan to design a fuller target state, and avd-swarm may turn approved items into gated changes for an estate it operates. Both are optional readers: the plan, this method and the landing zone work the same without them.

## Not yet known

- How disruptive each landing zone change is (some settings need hosts rebuilt) is not yet tested (`gap:remediation-plan`).
- No run has yet taken a plan through a landing zone redeploy and a second assessment.
