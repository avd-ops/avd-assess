# Troubleshooting and diagnostics method

How to find out why something is wrong in an AVD estate: which source answers which symptom, in what order to read them, and what stays `unknown`. It is the [assessment](assessment.md) method applied to the troubleshooting and diagnostics pillar (`diagnostics` in `dimensions.yaml`). It is the one pillar that is a flow rather than a list of settings, so it needs this page. Microsoft documents each component's troubleshooting; the method links to those pages and adds only the map that joins them: the data sources (`gap:diagnostics-scope`), the error-code map (`gap:error-code-map`) and one triage flow per symptom. The monitoring pillar says the data must exist; this page says how to read it when something is wrong.

## Method

1. **Start from the symptom the operator reports** (`intake.reportedSymptoms`), and say whether it is one user, one host pool or everyone. With no symptom, read the facts in steps 3 and 4 and treat anything unusual as the symptom (`gap:diagnostics-scope`).
2. **Rule out the platform first:** Service Health for an AVD incident or advisory (`ref:troubleshoot-overview#service-health-first`, `ref:service-alerts#service-issue-and-advisory`).
3. **Read host health from the API,** which needs only Reader: status, failing checks, stale heartbeats, update state (`ref:avd-sessionhost-get-api#health-check-results`, `ref:session-host-health-checks#status-load-balancing`).
4. **Read the service's own record** if diagnostics are on: connection outcomes, errors by code and ServiceError, checkpoints (`ref:diagnostics-log-analytics#categories`, `ref:diagnostics-log-analytics#connection-states`, `ref:diagnostics-log-analytics#service-error-split`). Absent diagnostics, the triage is blind on the service side; say so and hand the gap to the monitoring pillar.
5. **Follow the flow for the symptom:** `gap:triage-cannot-connect`, `gap:triage-host-unhealthy`, `gap:triage-slow-logon`, `gap:triage-slow-session`, `gap:triage-profile-failed`. Each names the sources in the order to read them and the pillar that owns the fix.
6. **Look every code up in the map,** never by guess; an unmapped code stays `unmapped` (`gap:error-code-map`, `ref:troubleshoot-insights#errors-not-all-documented`).
7. **Go to the host, the directory or the client only when the flow says so,** and record which read it needed: host event and FSLogix logs, Entra sign-in logs, client logs (`ref:troubleshoot-agent#app-event-sources`, `ref:fslogix-logs#profile-log-first`, `ref:troubleshoot-sso-conditional-access#sign-in-logs-first`, `ref:windows-app-logs#per-platform`).
8. **Escalate what is the platform's:** ServiceError true and anything past the component pages go to Microsoft with the correlation ID (`ref:diagnostics-log-analytics#service-error-split`, `ref:troubleshoot-overview#escalation-tracks`).
9. **Record the finding as a fix in its owning pillar,** not here: this pillar finds causes; the remediation method plans the change (`gap:remediation-plan`).
10. **Record what stays `unknown`** and why: no diagnostics, a connection that never reached the service, recent rows not yet ingested, or a read nobody could make (`ref:diagnostics-log-analytics#unreached-not-logged`, `ref:troubleshoot-insights#ingestion-delay`).

## Not yet known

- Whether the flows find a fault planted on purpose. One sandbox run (a blocked required URL, a stopped agent, a full profile share) checks that the facts and the flows catch each; it is planned with the scaling batch and waits on a cost estimate and the owner's go.
- What error counts, failure shares and connection times are normal. No source publishes one (`gap:diagnostics-scope`); the estate's own last run is the comparison until evidence submissions give more (`gap:evidence-intake`).
- No check runs yet. The log facts need a Log Analytics read in the collector; the health check fact needs one more field from a read it already makes.
