# Gap: triage when a user profile fails to load

**Searched (2026-10-21):** FSLogix logging (`ref:fslogix-logs`), FSLogix prerequisites (`ref:fslogix-prerequisites`), the session host health checks (`ref:avd-sessionhost-get-api`), the Insights glossary's event logs (`ref:avd-insights-glossary`), the family's profile observations, the family knowledge bases and the web. **Not found:** a flow from "temporary profile" or "profile failed" to the source that says why, in the order an assessment can read them. Symptom: `profile-failed` in `intake.reportedSymptoms`.

## Flow

1. **Many users or one?** The `FSLogixHealthCheck` result says whether the service is down on a host (`ref:avd-sessionhost-get-api#fatal-by-name`); one user points at their container.
2. **Read the FSLogix events centrally** where the data collection rule sends them; the landing zone also alerts on any FSLogix error event (`ref:avd-insights-glossary#required-event-logs`, `ref:fslogix-logs#event-log-location`, `obs:landing-zone-alerts-read-the-wvd-tables`).
3. **Read the profile log on the host** for the user's sign-in and its warning or error code (`ref:fslogix-logs#profile-log-first`, `gap:error-code-map`). The support tool gathers every log for a case (`ref:fslogix-logs#three-log-types`).
4. **Share access:** Kerberos and SMB settings on the storage account, the April 2026 RC4 change above all (`ref:fslogix-logs#kerberos-rc4-change`, `obs:smb-channel-aes128-gcm-needed`).
5. **Share health:** latency, handles and capacity are the profiles pillar's (`ref:fslogix-prerequisites#storage-latency`, `ref:azure-files-vdi#handle-limits`).
6. **Antivirus:** missing exclusions for containers (`ref:fslogix-prerequisites#av-exclusions`); the endpoint-protection pillar owns them.

## Facts

The specified `failedHealthChecks` (FSLogix) is the only fact here; `c11.storage.smbChannelEncryption` and `c11.storage.filesIdentity` cover step 4. Everything else is a host-side read.
