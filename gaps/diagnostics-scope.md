# Gap: what a troubleshooting and diagnostics assessment can read, and which part becomes a fact

**Searched (2026-10-21):** Microsoft's AVD troubleshooting pages (`ref:troubleshoot-overview`, `ref:troubleshoot-agent`, `ref:troubleshoot-session-host-vm`, `ref:troubleshoot-service-connection`, `ref:troubleshoot-sso-conditional-access`, `ref:troubleshoot-entra-joined`, `ref:troubleshoot-insights`, `ref:troubleshoot-rdp-shortpath`, `ref:avd-connection-quality`), the diagnostics and table references (`ref:diagnostics-log-analytics`, `ref:wvderrors-table`, `ref:wvdcheckpoints-table`, `ref:wvdagenthealthstatus-table`, `ref:wvdconnections-table`), session host health (`ref:session-host-health-checks`, `ref:avd-sessionhost-get-api`), Insights (`ref:avd-insights`, `ref:avd-insights-glossary`, `ref:avd-insights-use-cases`), FSLogix and Windows App logging (`ref:fslogix-logs`, `ref:windows-app-logs`, `ref:windows-app-basic`), Service Health (`ref:service-alerts`), the review checklist (E02 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** one page that says which diagnostic source answers which symptom, which of them a read-only assessment can reach, and which signals are worth collecting as facts rather than reading by hand. Each Microsoft page covers one component; none joins them into a triage, and none says what a healthy error rate, failure share or time to connect is.

This page is the map. The triage flows that use it are `gap:triage-cannot-connect`, `gap:triage-slow-logon`, `gap:triage-slow-session`, `gap:triage-profile-failed` and `gap:triage-host-unhealthy`; the codes they meet are in `gap:error-code-map`. The method is [methods/diagnostics.md](../methods/diagnostics.md).

## Data sources

| Source | What it shows | Read with | Who can read it | Becomes |
|---|---|---|---|---|
| Session host API | Status, health check results, heartbeat, agent and stack versions, update state, now (`ref:avd-sessionhost-get-api#health-check-results`) | ARM, GA API | Reader | Facts: `c11.hostPool.sessionHosts.*` |
| `WVDAgentHealthStatus` | The same, as history (`ref:wvdagenthealthstatus-table#health-history`) | Log Analytics | Log Analytics Reader | Runbook (the API fact covers now) |
| `WVDConnections` | Started, Connected and Completed per connection, client, transport (`ref:diagnostics-log-analytics#connection-states`) | Log Analytics | Log Analytics Reader | Facts: connections, failed connections |
| `WVDErrors` | Errors by code, source, operation and ServiceError, for connections, feed, registration and management (`ref:wvderrors-table#code-columns`, `ref:diagnostics-log-analytics#errors-scope`) | Log Analytics | Log Analytics Reader | Facts: errors by code, service errors |
| `WVDCheckpoints` | Named steps of each activity, the end of time to connect (`ref:wvdcheckpoints-table#named-steps`, `ref:avd-insights-glossary#time-to-connect-checkpoints`) | Log Analytics | Log Analytics Reader | Fact: time to connect p95 |
| Network and graphics tables | RTT, bandwidth, frame drops by cause (`ref:wvdconnectionnetworkdata-table#rtt-and-bandwidth-only`, `ref:wvdconnectiongraphicsdata-table#frame-drops-by-cause`) | Log Analytics | Log Analytics Reader | The protocol and ux-measurement pillars' facts |
| Insights | All of the above as workbooks, plus host counters and events (`ref:troubleshoot-overview#insights-or-kql`) | Azure portal | Reader on the AVD and host resource groups and the workspace (`ref:troubleshoot-insights#read-access-needed`) | Runbook |
| Host event logs | Agent, boot loader, installer, Remote Desktop Services and FSLogix events (`ref:troubleshoot-agent#app-event-sources`, `ref:avd-insights-glossary#required-event-logs`) | Log Analytics when the data collection rule sends them, otherwise on the host | Log Analytics Reader, or a host sign-in | Runbook; the error-code map names the events |
| FSLogix text and trace logs | Each profile load and unload with codes (`ref:fslogix-logs#profile-log-first`) | On the host | A host sign-in | Runbook |
| Entra sign-in logs | AADSTS code, Conditional Access result, method (`ref:troubleshoot-sso-conditional-access#sign-in-logs-first`) | Entra admin center or Graph | A directory reader role | Runbook until a directory read exists |
| Client logs | Windows App logs per platform (`ref:windows-app-logs#per-platform`) | On the client | The user | Intake |
| Path tests | Required URLs from the host, routes and NAT type (`ref:avd-url-check-tool#run-on-host`, `ref:connection-monitor#path-tests`, `ref:troubleshoot-rdp-shortpath#nat-type-test`) | On the host or a network watcher | A host sign-in, or Network Watcher access for Connection Monitor | Runbook |
| Service Health | Platform incidents and advisories (`ref:troubleshoot-overview#service-health-first`, `ref:service-alerts#service-issue-and-advisory`) | Azure portal, activity log | Reader | Runbook |
| Resource Graph | Session hosts in `DesktopVirtualizationResources`, the rest in `Resources` (`ref:resource-graph-tables#dv-table-session-hosts`) | Resource Graph | Reader | The collector's own read |

A connection that never reached the service is in none of the service tables (`ref:diagnostics-log-analytics#unreached-not-logged`), and recent rows can take about 15 minutes to appear (`ref:troubleshoot-insights#ingestion-delay`). So an empty result is `unknown`, never "no problem".

## Tools, as categories

Microsoft's own tools are named as the sources name them: Insights, Log Analytics, Resource Graph, the required URL check tool, Connection Monitor, the NAT type test (a closed binary, linked as an operator step and never required), the FSLogix support tool, Windows App's log collection, Event Viewer, Performance Monitor and Service Health. Anything else appears only as a category, with no product named, no endorsement and no integration: a third-party monitoring or user experience product, a log analytics or security information and event management platform, a packet capture tool, a synthetic sign-in or load tool. A category is a place where evidence can come from, read through the operator; the method never needs one.

## Facts for the collector

Proposed in the fact register as `specified`, for avd-current-state's collector to build. Each is a count per host pool over one window, with no user name, host name, message text or correlation ID in the snapshot.

| Fact | Definition |
|---|---|
| `c11.hostPool.sessionHosts.failedHealthChecks` | Hosts failing each health check by its API name (`ref:avd-sessionhost-get-api#health-check-names`), read with the session hosts the collector already reads; `HealthCheckFailed` only, never `Unknown` |
| `c11.hostPool.diagnostics.windowDays` | The days the log facts cover; the operator chooses it, seven by default |
| `c11.hostPool.diagnostics.connections` | Distinct correlation IDs with a Started row |
| `c11.hostPool.diagnostics.connectionsFailed` | Of those, the ones with no Connected row |
| `c11.hostPool.diagnostics.errorsByCode` | `WVDErrors` rows with ServiceError false, counted by `CodeSymbolic`, or by `Code` when the symbol is empty |
| `c11.hostPool.diagnostics.serviceErrors` | `WVDErrors` rows with ServiceError true |
| `c11.hostPool.diagnostics.timeToConnectSecondsP95` | p95 from Started to the first ShellReady or RdpShellAppExecuted checkpoint (`ref:avd-insights-glossary#time-to-connect-checkpoints`) |

Two built facts this pillar cites, `c11.hostPool.sessionHosts.status` and `staleHeartbeat`, were already in the snapshot schema and the collector and are now in the register; agent and stack versions and update state are registered by the images pillar. The log facts need a Log Analytics read, which the collector doesn't do yet: it is read-only and opt-in like the host-side and directory reads the map plan names, and it waits on the same kind of owner decision.

## Intake

`intake.reportedSymptoms` (specified): the symptoms the operator reports, any of `no-resources`, `sign-in-fails`, `cannot-connect`, `disconnects`, `slow-logon`, `slow-session`, `profile-failed`, `host-unhealthy`, or `none` or `unknown` alone. Each value picks a triage flow; an assessment with no reported symptom still reads the facts.

## Open points

- **Time to connect and credentials.** The Insights glossary says credential entry is subtracted (`ref:avd-insights-glossary#credential-time-subtracted`); the Insights troubleshooting page says it is included and can cause false peaks (`ref:troubleshoot-insights#time-to-connect-includes-credentials`). Until a run shows which, a slow time to connect is read through its stages, never judged alone.
- **Stale heartbeat.** The collector counts a host as stale after 30 minutes without a heartbeat. No source sets that number; it stays a family choice until a run or a source gives one.
- **Normal levels.** No source says how many errors, failed connections or seconds to connect are normal. The facts are read against the estate's own last run and the operator's reported symptoms, and the evidence intake can add published experience (`gap:evidence-intake`).
