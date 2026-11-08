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

## Configuration facts (C11)

| Fact | Status | Type | Read from |
|---|---|---|---|
| `c11.hostPool.diagnosticsSetting` | built | per host pool (`all`, `required`, `partial`, `none`): whether required diagnostic categories are forwarded | REST `diagnosticSettings` per host pool |
| `c11.monitoring.diagnostics` | specified | per other AVD object kind as a count map: sends all logs, the required categories, part of them, or nothing | REST `diagnosticSettings` per object |
| `c11.hostPool.sessionHosts.monitoringAgent` | built | hosts with the Azure Monitor Agent `Succeeded`, out of the total | Resource Graph VM extensions |
| `c11.hostPool.sessionHosts.insightsDcr` | built | hosts associated with a rule whose name starts `microsoft-avdi-` | Resource Graph `InsightsResources` |
| `c11.logAnalytics.retentionDays` | built | count map, workspaces by retention days | Resource Graph workspaces |
| `c11.monitoring.alerts` | specified | alert rules on the workspace, the hosts' resource groups or the host pools, counted by kind and by state (enabled with a receiver, enabled without, disabled); never their receivers | Resource Graph `scheduledqueryrules`, `metricalerts`, `activitylogalerts` |

With the built configuration facts, two checks run in `method.json`:
- `asm-hostpool-diagnostics-enabled` (`ref:review-checklists-avd#E02.02`, `ref:review-checklists-avd#G03.05`): every host pool forwards all or required diagnostic categories.
- `asm-hosts-insights-agent` (`ref:review-checklists-avd#E02.01`): session hosts have the Azure Monitor Agent provisioned and an AVD Insights DCR associated.

These are in the register, defined in full in `gap:monitoring-scope` with the storage alert and Service Health facts beside them.

## Measured facts from Insights KQL (built in C11, forensic in C12)

Six host-pool telemetry facts are built in C11 (`contracts/schemas/current-state-facts.schema.json` under `/subscriptions/*/hostPools/*/insights/*`) and read over a stated KQL window from the Log Analytics tables the estate already collects (`ref:avd-insights-workbooks#queries-define-measures`):

| Fact | Table | Measure | Check in `method.json` |
|---|---|---|---|
| `c11.insights.rttP50` | `WVDConnectionNetworkData` | Median round-trip latency (ms) | Observational (`insights-observational` benchmark profile) |
| `c11.insights.rttP95` | `WVDConnectionNetworkData` | p95 round-trip latency (ms) | `asm-insights-rtt-target` (<= 150 ms, `ref:avd-prerequisites#rtt-under-150`) |
| `c11.insights.inputDelayP95` | `Perf` | p95 per-session user input delay (ms) | `asm-insights-input-delay-target` (<= 100 ms, `ref:avd-insights-glossary#input-delay-bands`) |
| `c11.insights.timeToConnectP95` | `WVDConnections` / `WVDCheckpoints` | p95 time from connection start to shell-ready (seconds) | `asm-insights-time-to-connect` (<= 30 s, `ref:avd-insights-glossary#time-to-connect-stages`) |
| `c11.insights.fslogixReadIopsP95` | `Perf` | p95 logical disk read IOPS during sign-in and steady state | Observational (`storage-fslogix-io` and `insights-observational` profiles) |
| `c11.insights.connectionFailureRate` | `WVDConnections` | Percentage of connection attempts that fail before reaching a session | `asm-insights-connection-reliability` (<= 5%, `ref:diagnostics-log-analytics#connection-states`) |

Additional per-user and per-group forensic distributions remain in C12 (`c12.group.*`):
- **Use:** concurrency (peak, and by hour).
- **Density:** sessions per host (peak); CPU (p95) and available memory (p5) per host.
- **Experience:** stage-by-stage time to connect, connection errors by symbolic code (`c11.hostPool.diagnostics.errorsByCode`), and spread of client versions (`c12.group.clients.byVersion`).

They serve:
- the declarative Insights checks in `method.json` and the `insights-observational` profile in `benchmarks/profiles.yaml`;
- the readiness rows that `needs-measurement` (`gap:decision-readiness`);
- the sample check (`gap:sample-check`);
- the benchmarks in `methods/targets-benchmarks.md`.

Their contract lives with the other foundation schemas in this repo's `contracts/`. A tier above the foundation may map its own measured facts onto them, and never the other way round.

## Cost

Reading costs nothing beyond query time. Turning Insights on costs ingestion: about 3 to 5 GB per host every 31 days for a host running all day (`ref:avd-insights-costs#per-vm-estimate`). Diagnostics are a small share and shouldn't be cut (`ref:avd-insights-costs#keep-diagnostics`).
