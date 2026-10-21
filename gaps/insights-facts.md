# Gap: AVD Insights as evidence

**Searched (2026-10-20):** Microsoft Learn (Insights setup, costs, use cases, glossary, what's new), the Insights workbook source (`ref:avd-insights-workbooks`), the Azure Monitor Baseline Alerts AVD pattern (`ref:amba-avd`), the CAF AVD management baseline (`ref:caf-avd-management`), the AVD review checklist, GitHub and the web. **Not found:**
- a list of facts that say, from the control plane, whether an estate meets the Insights configuration baseline;
- a tool-neutral list of measured facts read from Insights data, with their windows and roll-ups.

The configuration workbook checks the setup interactively, one host pool at a time (`ref:avd-insights-workbooks#config-check`). Its result isn't something an assessment can keep.

**What we write.** avd-assess holds the standard; avd-current-state reads it. Facts are counts, booleans and public values only, never names, IDs or contact data (`methods/collection.md` step 3).

## The standard

| Item | Source |
|---|---|
| Host pool diagnostics: seven categories | `ref:avd-insights#hostpool-diagnostics` |
| AVD workspace diagnostics: four categories | `ref:avd-insights#workspace-diagnostics` |
| Every session host: Azure Monitor Agent, managed identity, associated with the Insights data collection rule | `ref:avd-insights#host-data-ama-dcr` |
| The rule sends the 20 counters and 6 event logs | `ref:avd-insights-costs#counter-set`, `ref:avd-insights-costs#event-logs` |
| One workspace, in the session hosts' region | `ref:caf-avd-management#regional-workspace`, `ref:avd-insights#designated-workspace` |
| An alerting model | `ref:caf-avd-management#alerting-model`; the published alert set is `ref:amba-avd` |
| Matching the current workbook version | `ref:avd-insights-whats-new#latest-version` |

No source sets a retention number. Retention stays the estate's choice and is reported, not graded.

## Configuration facts (specified, C11)

| Fact | Type | Read from |
|---|---|---|
| `c11.monitoring.diagnostics` | count map: host pools, app groups and workspaces by diagnostic setting (all logs, the listed categories, off) | REST `diagnosticSettings` per object |
| `c11.hostPool.sessionHosts.monitoringAgent` | hosts with the Azure Monitor Agent `Succeeded`, out of the total | Resource Graph VM extensions |
| `c11.hostPool.sessionHosts.insightsDcr` | hosts associated with a rule whose name starts `microsoft-avdi-` | Resource Graph `InsightsResources` |
| `c11.logAnalytics.retentionDays` | count map, workspaces by retention days (built) | Resource Graph workspaces |
| `c11.monitoring.alerts` | enabled log and metric alert rules on the workspace or the hosts' resource groups: a count, never their receivers | Resource Graph `scheduledqueryrules`, `metricalerts` |

With these, two checks can run:
- E02.02: every AVD object sends the listed categories.
- E02.01: every host sends Insights data.

They join `method.json` once avd-current-state collects these facts and they are built in the register.

## Measured facts (proposed)

These are read over a stated window from the Insights data the estate already collects, using the workbook queries (`ref:avd-insights-workbooks#queries-define-measures`):

- **Use:** concurrency (peak, and by hour).
- **Density:** sessions per host (peak); CPU (p95) and available memory (p5) per host.
- **Experience:**
  - input delay (p95);
  - round-trip time (p95, by gateway region);
  - time to connect (p95, and by stage);
  - connection errors by symbolic code;
  - spread of client versions.

They serve:
- the readiness rows that `needs-measurement` (`gap:decision-readiness`);
- the sample check (`gap:sample-check`);
- the benchmarks in `methods/targets-benchmarks.md`.

Their contract lives with the other foundation schemas in this repo's `contracts/`. A tier above the foundation may map its own measured facts onto them, and never the other way round.

## Cost

Reading costs nothing beyond query time. Turning Insights on costs ingestion: about 3 to 5 GB per host every 31 days for a host running all day (`ref:avd-insights-costs#per-vm-estimate`). Diagnostics are a small share and shouldn't be cut (`ref:avd-insights-costs#keep-diagnostics`).
