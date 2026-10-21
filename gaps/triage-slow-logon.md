# Gap: triage when sign-in to a session is slow

**Searched (2026-10-21):** the Insights glossary and troubleshooting page (`ref:avd-insights-glossary`, `ref:troubleshoot-insights`), the checkpoints table (`ref:wvdcheckpoints-table`), FSLogix logging (`ref:fslogix-logs`), the logon target gap (`gap:logon-target`), the family knowledge bases and the web. **Not found:** a flow that turns a slow time to connect into the stage that caused it, using only what an assessment can read. Insights draws the stages; it doesn't say which to read first or how to tell a slow user from a slow estate. Symptom: `slow-logon` in `intake.reportedSymptoms`.

## Flow

1. **Measure before judging.** Time to connect runs from the Started row to the shell-ready checkpoint (`ref:avd-insights-glossary#time-to-connect-checkpoints`); a new session takes longer than a reconnect. No source sets a target (`gap:logon-target`); compare with the estate's last run.
2. **Split it into stages:** user route, stack connected, logon (profiles, Group Policy, shell start) and shell ready (`ref:avd-insights-glossary#time-to-connect-stages`). Stages can overlap, so they don't add up to the total.
3. **Route or stack slow:** the network path and proxies, not the host; hand to the networking and protocol pillars.
4. **Profiles slow:** the FSLogix profile log on the host shows load time and any warning code (`ref:fslogix-logs#profile-log-first`); storage latency and sizing are the profiles pillar's (`ref:fslogix-prerequisites#storage-latency`).
5. **Group Policy or shell slow:** policies and startup apps on the host; the intune pillar owns how settings are delivered.
6. **Check the reading itself.** A missing completion event skews times (`ref:troubleshoot-insights#missing-completion`), and two pages disagree on whether credential entry is counted (`ref:avd-insights-glossary#credential-time-subtracted`, `ref:troubleshoot-insights#time-to-connect-includes-credentials`; `gap:diagnostics-scope`).

## Facts

The specified `c11.hostPool.diagnostics.timeToConnectSecondsP95` gives the estate-wide reading; `c12.group.logonSeconds.p95` is the measured logon ux-measurement owns. Stage timings stay a runbook read until a run shows they are stable enough to be a fact.
