# Gap: what a FinOps assessment of an AVD estate covers, and which repo does what

**Searched (2026-10-20):** the FinOps Framework as Microsoft summarizes it (`ref:finops-framework#capabilities`), the Well-Architected cost checklist (`ref:waf-cost-optimization-checklist`), the review checklist's cost items (`ref:review-checklists-avd#E01.05` and the rest), Azure Advisor's cost recommendations (`ref:advisor-cost`), Microsoft's AVD cost, licensing, autoscale and tagging pages (`ref:avd-costs`, `ref:avd-licensing`, `ref:avd-autoscale`, `ref:avd-tagging`), and the FinOps toolkit (`ref:finops-toolkit#tools`). **Not found:** an open method that says which of these an AVD estate assessment can judge from read-only data, which need billing access, which need the operator's answer, and which stay unknown. The framework judges an organization's practice; the checklists say what to do for a workload; the toolkit reports on cost data across an organization. None says how to tell, for one AVD estate, whether it was done.

**What we write.**

1. **Scope is the workload, not the practice.** The method judges the estate's own capabilities from the framework: workload optimization, rate optimization, licensing, allocation, budgeting and unit economics (`ref:finops-framework#capabilities`). How mature an organization's FinOps practice is stays with the framework's own assessment, per capability (`ref:finops-framework#maturity-per-capability`).
2. **Three kinds of evidence.** Control plane, with Reader: host pool type, VM sizes, scaling plans, Start VM on Connect, tags, budgets and unattached disks. Billing, with Cost Management Reader or a billing role: actual cost by meter, running hours, commitment utilization and Advisor's commitment advice. A run without billing access marks those `unknown`, as the run recorder does (`obs:run-cost-settles-late`). The operator's answer: which licenses users hold, which commitments exist at a scope the run can't see, and working hours.
3. **Advisor is evidence, not a rival score.** Where Advisor has cost recommendations for the estate's resources, the method cites them rather than recomputing them (`ref:advisor-cost#right-size-or-shutdown-vms`). Low use is often by design on hosts a scaling plan deallocates, so a right-size recommendation on an autoscaled host is a `warn` to review, never a `gap` by itself.
4. **Prices are retail unless the operator says otherwise.** The method prices with the Retail Prices API, matched on product, SKU and meter (`obs:retail-price-lookalike-meters`). Retail is list price, so an estimate is an upper bound for anyone with negotiated rates or commitments (`obs:estimate-before-deploy`). Cost data read from Cost Management uses FOCUS column names where it can (`ref:focus#list-contracted-effective-billed`).
5. **Cost per user is reported, not scored.** Unit economics is one of the framework's capabilities, but no published benchmark says what an AVD user should cost. Version 1 reports the month's actual cost per user who connected beside the coverage, with no target, until our own runs give one.
6. **Findings carry two codes:** the review checklist item or the Well-Architected code (`CO:03` and the rest) and pillar for scoring, and the FinOps capability, so a FinOps reader can group them.

**How avd-current-state would run it.** Draft rules, in the same shape as `gap:checklist-mapping`. Facts marked "needs a fact" are proposals for the fact register in [contracts/](../contracts/); a check that cites a fact a run doesn't have scores `unknown`.

| Claim | Evidence (fact) | Rule (draft) | Status |
|---|---|---|---|
| `ref:review-checklists-avd#E01.05` | `c11.hostPool.type`, `c11.hostPool.startVmOnConnect` | Personal host pools use Start VM on Connect | Built (`asm-personal-start-vm-on-connect` in method.json) |
| `ref:review-checklists-avd#E01.04` | `c11.hostPool.scalingPlan.method` (specified) | Every pooled host pool has a scaling plan; the rule is kept in `gap:monitoring-scope` | Specified, not built |
| `ref:review-checklists-avd#E01.06` | `c11.hostPool.type`, `c11.hostPool.startVmOnConnect` (built); `c11.hostPool.scalingPlan.method`, `c11.hostPool.sessionHosts.hibernation` (specified) | A personal host pool with Start VM on Connect and no scaling plan that deallocates or hibernates is a `warn`: hosts start on demand but never stop (`ref:start-vm-on-connect-faq#no-automatic-deallocation`) | Specified, not built |
| `ref:review-checklists-avd#E01.07` | Tags on host pools and session hosts (not yet a C11 fact) | Every host pool and its session hosts carry a cost allocation tag; `cm-resource-parent` set to the host pool counts (`ref:avd-tagging#cm-resource-parent`); a tag only on the resource group counts when tag inheritance is on, which a Reader run can't see, so that case is `unknown` (`ref:avd-tagging#tags-only-direct`, `ref:cost-tag-inheritance#inherit-to-usage-records`) | Needs a fact |
| `ref:waf-cost-optimization-checklist#CO:03` | Budgets at the estate's subscription or resource groups, and whether each calls an action group (not yet a C11 fact) | A budget that calls an action group passes; a budget that only alerts is a `warn` (`obs:budget-alert-needs-a-lock`); no budget is a `gap` | Needs a fact |
| `ref:advisor-cost#unattached-disks` | Advisor cost recommendations for the estate's resource groups (`c11.advisor.recommendations` counts them by category; per-resource findings are not yet a fact) | Each unattached disk in an AVD resource group is a `warn` | Needs a fact |
| `ref:advisor-cost#right-size-or-shutdown-vms` | As above | Cited per host, `warn`, with the scaling plan beside it | Needs a fact |
| `ref:reservations#hourly-billing-discount` | Running hours by size and region (billing read), the operator's commitments | `gap:commitment-floor` | Needs billing access |
| `ref:avd-licensing#separate-subscription-for-licensed-users` | The operator's answer | A subscription enrolled in per-user access pricing that also serves internally licensed users is a `warn` | Needs an intake answer |
| `ref:review-checklists-avd#H04.03` | FSLogix maximum profile size (host-side, not collected) | The configured size matches the plan | Unknown |

**Proposed for the intake** (not yet in the fact register, as enums with no names): which license covers the users (`m365-or-windows-enterprise`, `rds-cal`, `per-user-access`, `unknown`), because it decides whether per-user access pricing applies (`ref:avd-licensing#eligible-license-per-user`); and whether the organization holds VM reservations or a savings plan at a scope the run can't see (`reservation`, `savings-plan`, `both`, `none`, `unknown`), because Advisor's commitment advice is per subscription (`ref:advisor-cost#vm-reservations`).

**Which repo does what.** The three foundation repos hold FinOps the same way they hold everything else, and the upper layers build on them without becoming a dependency:

| Repo | FinOps slice | Depends on |
|---|---|---|
| avd-assess | What it should be: this method, its references, observations and gaps | Nothing |
| avd-current-state | What is there now: collects the cost facts with Reader, reads billing when it has access, and runs the checks from a pinned copy of this method | Its own pinned copies only |
| avd-landing-zone | How it's built: an estimate before every deployment, a scaling plan and Start VM on Connect by default, a budget with a Lock runbook, and each run's expected and actual cost (contract C17) | Nothing above it |
| avd-second-brain | Why: cost decisions and accepted spend over the estate's life, such as why a host stays on or why a commitment was bought | Reads the three |
| avd-swarm | How it's operated: its spend guard for lab runs, and schedule or size changes as plans a person approves, behind the gate and kill switch | Cites the brain |

A separate FinOps repo isn't needed while cost is one section of each layer. The organization-wide tools already exist as open source (`ref:finops-toolkit#tools`), and the family links to them rather than rebuilding them.
