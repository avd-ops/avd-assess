# Gap: triage when a session host is unhealthy

**Searched (2026-10-21):** session host statuses and health checks (`ref:session-host-health-checks`, `ref:avd-sessionhost-get-api`), the agent and session host VM pages (`ref:troubleshoot-agent`, `ref:troubleshoot-session-host-vm`), the agent health table (`ref:wvdagenthealthstatus-table`), the required URL check (`ref:avd-url-check-tool`), the family knowledge bases and the web. **Not found:** a flow from a host's status to the event that explains it. The status page names the checks, the agent page names the events; nothing joins them. Symptom: `host-unhealthy` in `intake.reportedSymptoms`, or any host not Available in the facts.

## Flow

1. **Read status and checks from the API**, no host sign-in needed (`ref:avd-sessionhost-get-api#health-check-results`). Available is the only healthy status (`ref:session-host-health-checks#available-is-healthy`).
2. **Shutdown or Unavailable on a stopped VM** isn't a fault; check the power state first (`ref:session-host-health-checks#shutdown-vs-unavailable`).
3. **Unavailable on a running VM:** a fatal check failed (domain, trust, reachability, stack listener, FSLogix, encryption) or the agent isn't reporting (`ref:avd-sessionhost-get-api#fatal-by-name`, `ref:session-host-health-checks#fatal-checks`). No heartbeat: the boot loader service or port 443 to the broker (`ref:troubleshoot-session-host-vm#no-heartbeat`, `ref:troubleshoot-agent#bootloader-stopped`).
4. **Needs Assistance:** the URL, metadata or monitoring agent check; users still connect, but connections may carry no logging (`ref:troubleshoot-agent#needs-assistance-checks`, `ref:session-host-health-checks#needs-assistance-nonfatal`). Run the required URL check on the host (`ref:avd-url-check-tool#run-on-host`).
5. **Upgrade Failed or stuck Upgrading:** the agent update; the updater and installer events say why (`ref:session-host-health-checks#status-load-balancing`, `ref:troubleshoot-agent#install-msi-errors`).
6. **Read the host's Application log** under the agent sources and look the event up in `gap:error-code-map` (`ref:troubleshoot-agent#app-event-sources`). Registration events mean a new key (`ref:troubleshoot-agent#event-3277-token`, `ref:troubleshoot-session-host-vm#isregistered-zero`); 3277 `INVALID_FORM`, 3703 and 3019 mean an endpoint is blocked, handed to the networking pillars (`ref:troubleshoot-agent#event-3277-invalid-form`, `ref:troubleshoot-agent#event-3703-gateway`, `ref:troubleshoot-agent#event-3019-websocket`).
7. **Domain checks failing:** the join, DNS or computer account (`ref:troubleshoot-session-host-vm#domain-join-errors`).
8. **Last resort:** reinstall and re-register the agent (`ref:troubleshoot-agent#reinstall-last`). In an estate built from code, replacing the host from its image is the same step done cleanly.

## Facts

`c11.hostPool.sessionHosts.status`, `staleHeartbeat` and the specified `failedHealthChecks`, with the images pillar's update state, answer steps 1 to 5 from a Reader snapshot. The agent health table keeps the history when a host recovered before anyone looked (`ref:wvdagenthealthstatus-table#health-history`).
