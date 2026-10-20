# Scoring method

How check outcomes roll up, and which target-state decisions the evidence can support. No open standard exists, so this method is ours and labeled as a hypothesis (`gap:scoring`).

## Method

1. **Score each Well-Architected pillar** as the passing severity weight over the assessed weight, with a warn counting half, using the checklist's own severities as weights (`gap:scoring`, `ref:review-checklists-avd`).
2. **Show coverage beside every score,** the share of checks that weren't unknown, so a score with little evidence can't pass for a good one (`gap:scoring`).
3. **Report decision readiness** for each of the 10 target-state decisions: decidable, decidable with intake, or needs measurement (`gap:decision-readiness`).
4. **Keep sizing decisions at "needs measurement"** until measured use replaces the priors (`ref:session-host-sizing#estimates-only`, `gap:decision-readiness`).
5. **Track change between runs** rather than chasing a number (`ref:waf-review-assessment#milestones`).

## Not yet known

- Whether these scores track real problems. That takes runs, and each run that disagrees becomes an observation on `gap:scoring`.
