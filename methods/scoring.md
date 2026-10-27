# Scoring method

How check outcomes roll up, and which target-state decisions the evidence can support. No open standard exists, so this method is ours and labeled as a hypothesis (`gap:scoring`).

## Method

1. **Score each Well-Architected pillar** as the passing severity weight over the assessed weight, with a warn counting half, using the checklist's own severities as weights (`gap:scoring`, `ref:review-checklists-avd`).
2. **Score each of the five control planes (`azure`, `entra`, `intune`, `m365`, `power-platform`) as a secondary rollup** alongside the Well-Architected pillars using the same severity-weighted formula, and exclude `not-applicable` checks from both the score and coverage denominators (`gap:scoring`).
3. **Show coverage beside every pillar and plane score,** the share of applicable checks that weren't unknown, so a score with little evidence can't pass for a good one (`gap:scoring`).
4. **Report decision readiness** for each of the 10 target-state decisions: decidable, decidable with intake, or needs measurement (`gap:decision-readiness`).
5. **Keep sizing decisions at "needs measurement"** until measured use replaces the priors (`ref:session-host-sizing#estimates-only`, `gap:decision-readiness`).
6. **Count sample check outcomes as performance-pillar checks,** weighted like any other, with the sample check's coverage beside them (`gap:sample-check`, `gap:scoring`).
7. **Track change between runs** rather than chasing a number (`ref:waf-review-assessment#milestones`).

## Not yet known

- Whether these scores track real problems. That takes runs, and each run that disagrees becomes an observation on `gap:scoring`.
