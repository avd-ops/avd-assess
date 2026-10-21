# Gap: triage when a user can't sign in, sees no resources or can't connect

**Searched (2026-10-21):** the service connection, single sign-on and Conditional Access, and Entra joined connection pages (`ref:troubleshoot-service-connection`, `ref:troubleshoot-sso-conditional-access`, `ref:troubleshoot-entra-joined`), the agent page (`ref:troubleshoot-agent`), Windows App's basic troubleshooting (`ref:windows-app-basic`), the diagnostics page (`ref:diagnostics-log-analytics`), the family knowledge bases and the web. **Not found:** one flow from the symptom to the source that explains it. Each page starts from an error the reader already has; this page is the order to find it in. Symptoms: `no-resources`, `sign-in-fails`, `cannot-connect` in `intake.reportedSymptoms`.

## Flow

1. **Rule out the platform.** Service Health for an AVD incident in the region (`ref:troubleshoot-overview#service-health-first`).
2. **One user or many?** Many users at once points at the service, a host pool or the network; one user points at their assignment, sign-in or device.
3. **Signed in, no resources.** The user isn't assigned to an application group, is assigned through a distribution group, or the subscription moved tenants (`ref:troubleshoot-service-connection#no-feed-assignment`, `ref:troubleshoot-service-connection#feed-lost-after-tenant-move`, `ref:windows-app-basic#no-resources-message`).
4. **Sign-in fails or loops.** Read the sign-in log entries for the AVD and Windows Cloud Login apps and follow the AADSTS code (`ref:troubleshoot-sso-conditional-access#sign-in-logs-first`, `ref:troubleshoot-sso-conditional-access#aadsts-codes`, `gap:error-code-map`). Repeated prompts: sign-in frequencies and per-user MFA (`ref:troubleshoot-sso-conditional-access#frequency-mismatch`). On Entra joined hosts, the Virtual Machine User Login role (`ref:troubleshoot-entra-joined#vm-user-login-role`). Conditional Access must allow every app the client signs in to (`ref:troubleshoot-service-connection#conditional-access-blocks`); a compliance requirement there applies to the client device (`ref:troubleshoot-sso-conditional-access#compliance-on-client`).
5. **Resources show, connection fails.** Find the connection in `WVDConnections`: Started with no Connected is a failure the service saw; read its `WVDErrors` rows by correlation ID (`ref:diagnostics-log-analytics#connection-states`, `ref:wvderrors-table#code-columns`). ServiceError true goes to Microsoft (`ref:diagnostics-log-analytics#service-error-split`).
6. **No row at all.** The connection never reached the service: the client or its network (`ref:diagnostics-log-analytics#unreached-not-logged`). Latest Windows App, the browser client, then client logs (`ref:windows-app-basic#first-steps`, `ref:windows-app-logs#per-platform`); the user's network is its administrators' (`ref:troubleshoot-overview#network-is-local`).
7. **No host to connect to.** `ENDPOINT_NOT_FOUND` or every host at its limit, off or unhealthy: go to `gap:triage-host-unhealthy` (`ref:troubleshoot-agent#endpoint-not-found`, `ref:troubleshoot-agent#at-connection-limit`).

## Facts

`c11.hostPool.diagnostics.connectionsFailed` and `errorsByCode` show whether the symptom is broad; `c11.hostPool.sessionHosts.status` shows whether any host could take the connection. Sign-in log reads wait on a directory read; until then step 4 is the operator's.
