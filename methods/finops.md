# FinOps method

How to judge what an estate costs, and whether it costs what it should, against what Microsoft and the FinOps Foundation publish. It is the [assessment](assessment.md) method applied to the cost pillar, with the extra sources cost needs. avd-current-state implements it; the findings go in the same report (contract C21). Nothing here is a bill, a quote or financial advice.

## Method

1. **Scope to the workload:** the FinOps capabilities one estate can show, workload and rate optimization, licensing, allocation, budgeting and unit economics, not the maturity of an organization's FinOps practice (`ref:finops-framework#capabilities`, `gap:finops-scope`).
2. **Start from Microsoft's lists:** the review checklist's cost items (`ref:review-checklists-avd#E01.05`, `ref:review-checklists-avd#E01.06`, `ref:review-checklists-avd#E01.07` and the rest), the Well-Architected cost checklist (`ref:waf-cost-optimization-checklist#CO:02`), and the AVD cost page (`ref:avd-costs#two-sources`), read in the framework's order of inform, optimize, operate (`ref:finops-framework#lifecycle`).
3. **Settle licensing first,** because it decides whether per-user access pricing applies and it comes from the operator, not telemetry (`ref:avd-licensing#eligible-license-per-user`, `ref:avd-licensing#per-user-access-external-only`, `gap:finops-scope`).
4. **Judge hours before rates:** a scaling plan on every pooled host pool (`ref:review-checklists-avd#E01.04`, `ref:avd-autoscale#scales-to-save-cost`, `obs:scaling-and-start-on-connect-by-default`), Start VM on Connect where hosts can be off (`ref:start-vm-on-connect#power-on-when-needed`), and something that deallocates personal hosts, since nothing does by default (`ref:start-vm-on-connect-faq#no-automatic-deallocation`).
5. **Judge size and density** with the sizing method's numbers, not against cost alone, and leave profile size and redirections `unknown` until a host-side read (`ref:session-host-sizing#multisession-users-per-vcpu`, `ref:waf-cost-optimization-checklist#CO:14`, `ref:review-checklists-avd#H04.03`, `ref:review-checklists-avd#H04.07`).
6. **Read Advisor's cost results** for the estate's resources and cite them rather than recompute them; a right-size note on an autoscaled host is a trade-off to review (`ref:advisor-cost#right-size-or-shutdown-vms`, `ref:advisor-cost#unattached-disks`, `gap:finops-scope`).
7. **Judge rates last:** commit only the floor of hours that always run, after the hours and sizes are settled (`ref:commitment-choice#right-size-first`, `gap:commitment-floor`).
8. **Check allocation and guardrails:** host pools and their hosts carry a cost allocation tag (`ref:avd-tagging#tag-host-pools-first`, `ref:avd-tagging#cm-resource-parent`), and a budget that acts, not only alerts (`ref:cost-management-budgets#alerts-dont-stop`, `obs:budget-alert-needs-a-lock`).
9. **Price with retail prices matched on product, SKU and meter,** report an unmatched line instead of guessing, and call the result an upper bound (`ref:retail-prices-api#unauthenticated-retail`, `obs:retail-price-lookalike-meters`, `obs:estimate-before-deploy`).
10. **Report actual cost only once it has settled,** with the time it was read; before that it is `pending` (`ref:cost-management-data#data-latency`, `ref:cost-management-data#open-month-estimated`, `obs:run-cost-settles-late`).
11. **Treat a deliberate trade-off as `warn` with its reason,** such as a host kept on for a night batch, and a setting nobody chose as `gap`; a model never decides which (`gap:scoring`).
12. **Repeat on a cadence** and compare with the last run, as for every other pillar (`ref:waf-review-assessment#milestones`, `ref:finops-framework#maturity-per-capability`).

## Where FinOps lives in the family

FinOps isn't a separate project. Each foundation repo holds its usual slice, and the upper layers build on them; dependencies point down only, and avd-landing-zone and avd-current-state keep working with nothing above them.

- **avd-assess** (this page): what it should cost, and why.
- **avd-current-state**: what it costs now. It collects the cost facts and runs these checks from a pinned copy of this method.
- **avd-landing-zone**: how it's built. It prices every deployment before it runs, its defaults should pass these checks, and it records each run's expected and actual cost.
- **avd-second-brain**: why it costs what it does over the estate's life, including accepted spend.
- **avd-swarm**: how it's operated, with its spend guard for lab runs and any change a plan a person approves.

The table and the reasons are in `gap:finops-scope`. The FinOps Foundation's own framework and the open-source FinOps toolkit cover the organization-wide practice; this method links to them rather than restating them (`ref:finops-toolkit#tools`, `ref:focus#common-billing-format`).

## Not yet known

- Most cost items need facts avd-current-state doesn't collect yet: scaling plans, tags, budgets and Advisor results (`gap:finops-scope`).
- No run has measured how long a pay-as-you-go sandbox's actual cost takes to appear, or compared a month of running hours with the scaling plan (`obs:run-cost-settles-late`, `obs:scaling-and-start-on-connect-by-default`).
- There is no published or measured target for cost per user, so it is reported without a score.
