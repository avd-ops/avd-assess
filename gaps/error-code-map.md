# Gap: one map from the code an operator sees to its meaning and its flow

**Searched (2026-10-21):** the AVD troubleshooting pages (`ref:troubleshoot-agent`, `ref:troubleshoot-session-host-vm`, `ref:troubleshoot-sso-conditional-access`, `ref:troubleshoot-rdp-shortpath`), the session host API (`ref:avd-sessionhost-get-api`), the `WVDErrors` reference (`ref:wvderrors-table`), Insights' troubleshooting page, the family knowledge bases and the web. **Not found:** a published list of AVD error codes. Codes are spread over the component pages, `WVDErrors` holds open-ended symbolic codes with no reference list, and Microsoft says not every error message is documented (`ref:troubleshoot-insights#errors-not-all-documented`).

**What we write.** One table keyed by the code as the operator sees it, pointing at the claim that explains it and the triage flow that handles it. The explanation stays in the source; this page holds only the key and the pointer.

| Code | Where it appears | Meaning (claim) | Flow |
|---|---|---|---|
| `DomainJoinedCheck`, `DomainTrustCheck`, `DomainReachable` failing | Session host health checks | Fatal: the host takes no connections (`ref:avd-sessionhost-get-api#fatal-by-name`; the status page lists only joined and trust, `gap:diagnostics-scope`) | `gap:triage-host-unhealthy` |
| `SxSStackListenerCheck` failing | Session host health checks | Fatal: the stack isn't listening (`ref:avd-sessionhost-get-api#fatal-by-name`) | `gap:triage-host-unhealthy` |
| `FSLogixHealthCheck` failing | Session host health checks | Fatal: profiles won't load (`ref:avd-sessionhost-get-api#fatal-by-name`) | `gap:triage-profile-failed` |
| `SupportedEncryptionCheck` failing | Session host health checks | Fatal: the RDP security layer setting is wrong (`ref:avd-sessionhost-get-api#fatal-by-name`) | `gap:triage-host-unhealthy` |
| `UrlsAccessibleCheck`, `MetaDataServiceCheck`, `MonitoringAgentCheck` failing | Session host health checks | Non-fatal: Needs Assistance (`ref:troubleshoot-agent#needs-assistance-checks`, `ref:session-host-health-checks#needs-assistance-nonfatal`) | `gap:triage-host-unhealthy` |
| `AppAttachHealthCheck` failing | Session host health checks | Non-fatal: some App Attach apps stop working (`ref:session-host-health-checks#app-attach-nonfatal`) | `gap:triage-host-unhealthy` |
| `WebRTCRedirectorCheck` failing | Session host health checks | The Teams media component isn't healthy (`ref:avd-sessionhost-get-api#webrtc-check`) | `gap:triage-slow-session` |
| Event 3277 `INVALID_REGISTRATION_TOKEN`, `EXPIRED_MACHINE_TOKEN` | Host Application log | Registration key not valid (`ref:troubleshoot-agent#event-3277-token`, `ref:troubleshoot-session-host-vm#isregistered-zero`) | `gap:triage-host-unhealthy` |
| Event 3277 `INVALID_FORM` | Host Application log | Agent can't reach the broker (`ref:troubleshoot-agent#event-3277-invalid-form`) | `gap:triage-host-unhealthy` |
| Event 3277 `ENDPOINT_NOT_FOUND` | Host Application log | No host to connect to (`ref:troubleshoot-agent#endpoint-not-found`) | `gap:triage-host-unhealthy` |
| Event 3277 `InstallMsiException`, `DownloadMsiException` | Host Application log | Agent install blocked or no disk space (`ref:troubleshoot-agent#install-msi-errors`) | `gap:triage-host-unhealthy` |
| Event 3277 `InstallationHealthCheckFailedException` | Host Application log | Stack listener not working (`ref:troubleshoot-agent#installation-health-check-failed`) | `gap:triage-host-unhealthy` |
| Event 3703 | Host Application log | Gateway URLs unreachable (`ref:troubleshoot-agent#event-3703-gateway`) | `gap:triage-host-unhealthy` |
| Event 3019 | Host Application log | Web socket URLs unreachable (`ref:troubleshoot-agent#event-3019-websocket`) | `gap:triage-host-unhealthy` |
| `NAME_ALREADY_REGISTERED` | Host Application log | Duplicate host name in the pool (`ref:troubleshoot-agent#name-already-registered`) | `gap:triage-host-unhealthy` |
| `Connection not found` (no active broker connection) | Host / `WVDErrors` | Host is at its session limit or the agent lost its broker connection (`ref:troubleshoot-agent#at-connection-limit`) | `gap:triage-cannot-connect` |
| `O_REVERSE_CONNECT_STACK_FAILURE` | Host / `WVDErrors` | Side-by-side stack not installed (`ref:troubleshoot-session-host-vm#reverse-connect-stack-failure`) | `gap:triage-host-unhealthy` |
| `AADSTS50058`, `AADSTS50076`, `AADSTS530002`, `AADSTS530032`, `AADSTS65001` | Entra sign-in logs | Session, MFA, compliance, tenant block, consent (`ref:troubleshoot-sso-conditional-access#aadsts-codes`) | `gap:triage-cannot-connect` |
| Entra VM sign-in account / credentials error | Client / Entra sign-in | Missing `Virtual Machine User Login` role or per-user MFA enforced on Entra-joined host (`ref:troubleshoot-entra-joined#vm-user-login-role`, `ref:troubleshoot-entra-joined#per-user-mfa-unsupported`) | `gap:triage-cannot-connect` |
| Feed empty (`no resources available`) | Client feed / `WVDFeeds` | User not assigned to an application group, assigned via distribution group, or subscription moved across tenants (`ref:troubleshoot-service-connection#no-feed-assignment`, `ref:troubleshoot-service-connection#feed-lost-after-tenant-move`) | `gap:triage-cannot-connect` |
| Shortpath UDP drop / fallback codes | `WVDErrors` | UDP path dropped or below its reliability threshold (`ref:troubleshoot-rdp-shortpath#udp-error-codes`) | `gap:triage-slow-session` |
| FSLogix `[WARN:...]`, `[ERROR:...]` (including Kerberos RC4/AES ticket errors) | FSLogix profile log / Event log | Container attach, VHDX lock or Kerberos encryption failure (`ref:fslogix-logs#profile-log-first`, `ref:fslogix-logs#kerberos-rc4-change`) | `gap:triage-profile-failed` |
| Any other `CodeSymbolic` | `WVDErrors` | `unmapped`: read its message and source, then the component's page | by Source and Operation |

Rules:

1. **Key by what the operator sees.** For `WVDErrors`, the key is `CodeSymbolic`, or `code ` and the decimal `Code` when the symbol is empty (`ref:wvderrors-table#code-columns`). The collector fact `c11.hostPool.diagnostics.errorsByCode` uses the same key.
2. **`ServiceError` first.** Rows with ServiceError true go to Microsoft with their correlation ID, whatever the code (`ref:diagnostics-log-analytics#service-error-split`).
3. **Never guess a meaning.** A code with no claim is `unmapped` and stays so until a source or a run explains it and this table changes in a reviewed PR. A run that explains one is an observation.
4. **No message text in facts.** Messages can carry user and host names; the map and the facts hold codes only.
