# Gap: a register of deployment dimensions and their baselines

**Searched (2026-10-20):** Microsoft Learn (AVD sizing, GPU, disks, ephemeral OS disks, load balancing, update methods, session host update, disk encryption, FSLogix and Azure Files storage, RDP bandwidth, RDP Shortpath, Teams), Defender for Endpoint VDI guidance, the Azure review checklist for AVD (`ref:review-checklists-avd`), the Well-Architected reliability checklist, the session host sizing guide (`ref:session-host-sizing`) and the web. **Not found:** one published list that names every design choice an AVD deployment makes and ties each to the baseline that says what good looks like. The checklist comes closest, but it asks questions ("determine the disk type") without answers, and its items don't say what evidence settles them (`gap:checklist-mapping`). Also not found, each recorded in the register as a `gap` row or note: memory per user, users per GPU, disk latency on session hosts, an open workload benchmark with a pass threshold, a maximum image age, the CPU cost of antivirus per user, and a log retention period for monitoring.

**What we write.** [dimensions.yaml](../dimensions.yaml), one row per dimension:

1. **What it decides**, in one line.
2. **Its home in the contracts:** the target-state decision (a decision in [contracts/fact-register.json](../contracts/fact-register.json), or `proposed:` when the register doesn't have it yet), the current-state and measured facts that evidence it, the intake questions only an operator can answer, and any check in [method.json](../method.json) that judges it.
3. **Its baseline:** the standing (`published`, `prior`, `guidance`, `gap`, or `owned` when another method here holds it), the claims it rests on, and a one-line summary in our own words. A `gap` row cites this page or another gap, and the estate's own measurement sets the number, as the [gold-standard registry](../gold-standards.yaml) does for `baseline` metrics.
4. **What avd-current-state can see today:** a built C11 fact, the private rebuild package, measured performance data, intake only, or nothing yet.
5. **The landing zone parameters** that set it, at a pinned avd-landing-zone commit. Every one of the template's 55 parameters is either set by a dimension or listed with the reason it isn't one (a name, a group ID, a secret), so a new parameter can't arrive without a home.

The register is for the three foundation repos: avd-assess says what good is, avd-current-state measures it, avd-landing-zone builds it. Other tools may read it; none is needed.

**How a row changes.** A `proposed:` decision or fact becomes real by a change to the fact register in this repo, then a collector change in avd-current-state. A `gap` row is retired the day a source publishes a number: the row cites that source and moves to `published` or `prior`. An `owned` row follows the method that owns it (security, FinOps or use cases) once that method is merged.

**Not yet known.** Every number in the register is still a source's estimate or a gap; none has been checked against users we measured. The observations that say so are linked from each row.
