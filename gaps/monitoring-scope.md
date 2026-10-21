# Gap: monitoring, operations, scaling and power

**Searched (2026-10-21):** the review checklist's management and monitoring items (`ref:review-checklists-avd#E01.04` to `ref:review-checklists-avd#E02.04`), Microsoft Learn on Insights, diagnostics, service alerts, Advisor, autoscale (concepts, plan, Insights, diagnostics, FAQ), Start VM on Connect and Log Analytics retention (`ref:avd-insights`, `ref:avd-diagnostics`, `ref:avd-service-alerts`, `ref:avd-advisor`, `ref:avd-autoscale`, `ref:autoscale-plan`, `ref:autoscale-insights`, `ref:autoscale-diagnostics`, `ref:autoscale-faq`, `ref:start-vm-on-connect`, `ref:log-retention`), the Azure Monitor Baseline Alerts AVD pattern (`ref:amba-avd`), Azure Files alert guidance (`ref:files-monitoring-alerts`), and the CAF AVD management and platform automation pages (`ref:caf-avd-management`, `ref:caf-avd-platform-automation`). **Not found:**
- a list of control plane facts that say whether an estate's alerts reach anyone, whether its scaling plan is sound, and how long it keeps logs;
- a lead time for ramp-up before users arrive, or a number for the first-connection wait Start VM on Connect adds;
- a retention period for AVD diagnostics.

Microsoft says what to turn on and what each setting means. None of it says how to tell, from read-only data, whether a given estate did it, or how to judge a schedule against the people who use it.

**What we write.** The map rows for the `monitoring` and `scaling` pillars live in `dimensions.yaml`; this page is what those rows need that no source gives: the facts, the draft checks, the intake questions and the two timing methods. Insights wiring itself is `gap:insights-facts`; cost is the FinOps method (`gap:finops-scope`).

## Three kinds of evidence

1. **Control plane, with Reader:** diagnostic settings, agents and data collection rule associations, alert rules and whether they have an action group, Service Health alerts, workspace retention, Advisor recommendations, scaling plans and their schedules. These become C11 facts.
2. **Log Analytics, with Log Analytics Reader on the AVD workspace:** autoscale evaluations, connection times, concurrency and ingestion volume, over a stated window. These become C12 facts, read with the workbook queries where one exists (`ref:avd-insights-workbooks#queries-define-measures`).
3. **The operator's answer:** who acts on an alert, how long logs must be kept, whether users accept a wait while a host starts, and how hosts are deployed. These are intake answers, as enums.

Facts carry counts, booleans and public values only: never alert receivers, action group names, workspace or resource IDs, or tag values.

## Facts specified in the register

These are `specified` in `contracts/fact-register.json`: the path is fixed, avd-current-state builds them. A fact moves to `built` only with a Pester fixture there.

| Fact | Value | Read from |
|---|---|---|
| `c11.hostPool.diagnostics` | the host pool's own diagnostics to Log Analytics: `all-logs`, `required` (Insights' seven categories present), `partial`, `none` | REST `diagnosticSettings` on the host pool |
| `c11.hostPool.autoscaleLogs` | true if the host pool sends the autoscale category for pooled host pools to Log Analytics | the same |
| `c11.monitoring.diagnostics` | count map of the other AVD objects keyed `<kind>:<state>` (kinds `workspace`, `appGroup`, `scalingPlan`; states as above), so `workspace:none` counts workspaces with no diagnostics | REST `diagnosticSettings` per object |
| `c11.hostPool.sessionHosts.monitoringAgent` | hosts with the Azure Monitor Agent provisioned | Resource Graph VM extensions |
| `c11.hostPool.sessionHosts.insightsDcr` | hosts associated with a rule whose name starts `microsoft-avdi-` | Resource Graph `insightsresources` |
| `c11.monitoring.workspace.retentionDays` | count map of workspaces that receive AVD data, by retention days | Resource Graph workspaces |
| `c11.monitoring.alerts` | count map of alert rules scoped to the AVD workspace, host resource groups or host pools, by kind (`log`, `metric`, `activity`) and state (`enabled-with-receiver`, `enabled-no-receiver`, `disabled`) | Resource Graph `scheduledqueryrules`, `metricalerts`, `activitylogalerts` |
| `c11.monitoring.serviceHealthAlerts` | count map, by event type (`incident`, `maintenance`, `advisory`, `security`), of enabled Service Health alerts with an action group that cover that type and AVD (a rule with no type or service filter covers all) | Resource Graph `activitylogalerts` |
| `c11.storage.alerts` | count map of metric alert rules scoped to the storage account or its file service, by state as for `c11.monitoring.alerts` | Resource Graph `metricalerts` |
| `c11.advisor.recommendations` | count map of active Advisor recommendations on the AVD resource groups, by category | REST Advisor recommendations |
| `c11.hostPool.scalingPlan.method` | `none`, `power`, `dynamic`, or `disabled` (assigned but not enabled) | REST scaling plans, `hostPoolReferences` |
| `c11.hostPool.scalingPlan.rampUpStart` | the earliest weekday ramp-up start, `HH:MM` in the plan's time zone | the plan's schedules |
| `c11.hostPool.scalingPlan.rampUpMinimumHostsPct`, `c11.hostPool.scalingPlan.rampUpCapacityThresholdPct` | the same schedule's ramp-up values | the plan's schedules |
| `c11.hostPool.scalingPlan.forceLogoff` | true if any schedule forces sign-out at ramp-down | the plan's schedules |
| `c11.hostPool.scalingPlan.exclusionTag` | true if the plan names an exclusion tag (never the tag's value) | the plan |
| `c11.hostPool.sessionHosts.hibernation` | hosts with hibernation enabled | Resource Graph VMs |
| `c12.group.scaling.occupancyP95ByPhase` | map of p95 session occupancy (%) by schedule phase (`rampUp`, `peak`, `rampDown`, `offPeak`) over the window | `WVDAutoscaleEvaluationPooled` (`ref:autoscale-insights#evaluation-table`) |
| `c12.group.scaling.failedEvaluations` | evaluations whose result isn't `Succeeded` | the same table |
| `c12.group.scaling.coldStartConnectP95Seconds` | p95 time to connect for connections that found no host running | `WVDConnections` and `WVDCheckpoints`, Insights' time to connect |

Still `proposed:` on a row, not in the register: `c12.window.monitoring.ingestMiBPerHostDay`, the workspace's billable ingestion per AVD host per day from the `Usage` table. It needs a C12 window-level shape the brain's contract hasn't got yet.

## Draft checks

They join `method.json` when their facts are `built`. All are `warn`; none needs a model.

| Check | Rule | Claims |
|---|---|---|
| Diagnostics on every AVD object | every host pool's `c11.hostPool.diagnostics` is `all-logs` or `required`, and `workspace:none` and `workspace:partial` are zero | `ref:review-checklists-avd#E02.02`, `ref:avd-insights#hostpool-diagnostics` |
| Insights on every host | `monitoringAgent` and `insightsDcr` equal the host total | `ref:review-checklists-avd#E02.01`, `ref:avd-insights#host-data-ama-dcr` |
| Alerts reach someone | no `enabled-no-receiver` rules, and at least one enabled rule | `ref:caf-avd-management#alerting-model`, `obs:alerts-silent-without-receivers` |
| Profile storage is alerted | every premium file storage account has at least one `enabled-with-receiver` alert (the facts can't yet tell which account holds profiles, as `gap:checklist-mapping` notes) | `ref:review-checklists-avd#E02.03`, `ref:amba-avd#storage` |
| Service Health is alerted | `incident` and `advisory` are each at least 1 in every subscription with AVD | `ref:review-checklists-avd#E02.04`, `ref:avd-service-alerts#issue-and-advisory` |
| Pooled pools scale | every pooled pool has a `power` or `dynamic` plan (this page owns the E01.04 rule; `gap:finops-scope` points here) | `ref:review-checklists-avd#E01.04`, `ref:avd-autoscale#scales-to-save-cost` |
| A scaled pool has its own session limit | a pooled pool with a plan has a session limit other than the service default | `ref:autoscale-plan#max-session-limit-required` |
| Ramp-up leads the working day | `rampUpStart` is before `intake.workingHours` start; needs a join between the snapshot and the intake, which the rule language doesn't have yet | `ref:autoscale-plan#ramp-up-before-peak` |
| Personal pools turn off | defined in `gap:finops-scope` (E01.06), with `c11.hostPool.scalingPlan.method` and `c11.hostPool.sessionHosts.hibernation` as its facts | `ref:review-checklists-avd#E01.06` |
| Advisor's AVD items are clear | no active operational Advisor recommendation on AVD resources | `ref:review-checklists-avd#E01.08`, `ref:avd-advisor#validation-pool` |

Retention is reported, never graded. The report notes that anything under 31 days saves nothing (`ref:log-retention#first-31-included`), and compares the value with `intake.logRetention` when the operator has answered it.

## Ramp-up lead time and the first-connection wait (method)

No source gives either number, so both are measured and judged against the users, not against a constant.

1. **Lead time.** From `c12.group.concurrency.byHour`, take the first hour whose sessions pass the minimum hosts' capacity. Ramp-up should start at least one host start and registration earlier. When `c12.group.scaling.occupancyP95ByPhase` for `rampUp` or `peak` is above the capacity threshold, hosts are starting behind demand: the threshold or the minimum is too low, or ramp-up too late.
2. **First-connection wait.** `c12.group.scaling.coldStartConnectP95Seconds` minus the estate's warm time to connect is what Start VM on Connect or a zero-host phase costs a user. Judge it against `intake.coldStartTolerance`: `no-wait` means keep a host on in every phase people work; `short-wait` accepts it off peak; `accept-wait` accepts it at any time.
3. **Disconnected sessions.** Autoscale counts them as active (`ref:autoscale-faq#disconnected-time-limit`), so a pool that never reaches its off-peak minimum while `c12.group.concurrency.byHour` is near zero points at missing sign-out policy, which is a host-side setting.

Batch S4 (sandbox) tests both numbers on the minimum kit, on its own written estimate and the owner's exact go phrase.

## Proposed for the intake

Not yet in the fact register or the intake schema (C19), as enums with no names. Each joins the register as `proposed`, then the schema, through its own pull request.

| Fact | Question | Values | Why |
|---|---|---|---|
| `intake.alertResponse` | Who acts on an AVD alert, and when? | `on-call`, `business-hours`, `nobody-yet`, `unknown` | `nobody-yet` turns every alert finding into a plan item for a receiver first (`ref:caf-avd-management#alerting-model`) |
| `intake.logRetention` | How long must AVD logs stay queryable? | `31-days`, `90-days`, `1-year`, `2-years`, `longer`, `unknown` | Retention has no published number (`ref:log-retention#analytics-two-years`) |
| `intake.coldStartTolerance` | Can users wait while a host starts? | `no-wait`, `short-wait`, `accept-wait`, `unknown` | Start VM on Connect and zero-host phases (`ref:start-vm-on-connect#slower-first-connection`) |
| `intake.deploymentMethod` | How are host pools and hosts deployed? | `pipeline-gated`, `code-by-hand`, `portal-or-script`, `unknown` | Review checklist E01.12 (`ref:caf-avd-platform-automation#gate-to-validation`) |

## Which repo does what

- **avd-assess:** this page, the rows, the references and the specified facts; the checks above when their facts are built.
- **avd-current-state:** builds the specified facts above, read-only, as its collector backlog; the Log Analytics reads only when the operator grants Log Analytics Reader.
- **avd-landing-zone:** sets most of this. Two items for it, from `obs:alerts-silent-without-receivers`: its log alerts deploy enabled without a receiver when no address is given, and it has no Azure Files metric alert.
- The decisions `operations.monitoring` and `operations.deployment` stay `proposed:` until the target state contract (C14, in avd-second-brain) has a place for them.
