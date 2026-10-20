# Gap: scoring

**Searched (2026-10-20):** Microsoft Learn (the Well-Architected Review, Azure Advisor), the review checklist, the web. **Not found:** an open scoring model for an AVD estate. The Well-Architected Review scores answers inside a Learn profile; commercial experience scores are proprietary and tuned per customer.

**What we write.** A research hypothesis, simple enough to recompute by hand, and tested by observations like any other claim:

1. **Pillar score:** for each Well-Architected pillar, the severity weight of checks that pass divided by the weight of checks assessed (pass, warn or gap). A `warn` counts half. Weights: high 3, medium 2, low 1 (the checklist's own severities).
2. **Coverage beside every score:** the share of the pillar's checks that weren't `unknown`. An unknown never counts as a pass or a gap.
3. **Decision readiness** from `gap:decision-readiness`, shown next to the scores.
4. **No single overall number** in version 1, because one figure hides which pillar or decision is weak.

If a high score keeps coming with real problems in our runs, that becomes a `disagrees` observation on this gap.
