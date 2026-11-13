# Desktop DevOps: how DevOps applies to Azure Virtual Desktop, Windows 365 and Microsoft Intune

> Personal project. Research and learning only, not for production, provided as is. Not affiliated with, endorsed by or supported by the author's employer, Liquidware or Microsoft. Azure Virtual Desktop, Windows 365 and Microsoft Intune are trademarks of their owner.

- **Status:** Built (`methods/desktop-devops.md`, `gaps/desktop-devops-scope.md`, `references/windows-365-intune.yaml`, `method.json` v6, `contracts/fact-register.json` v6)
- **Date:** 2026-11-02
- **Related specs:** [docs/assess-spec.md](assess-spec.md), [avd-ops Desktop DevOps specification](https://github.com/avd-ops/avd-ops/blob/main/docs/desktop-devops-spec.md), [avd-ops decision 0012](https://github.com/avd-ops/avd-ops/blob/main/docs/knowledge/decisions/0012-desktop-devops-for-avd-win365-and-intune.md), [avd-second-brain decision 0027](https://github.com/avd-ops/avd-second-brain/blob/main/docs/knowledge/decisions/0027-desktop-devops-across-avd-win365-and-intune.md)

---

## 1. Why Desktop DevOps exists

Enterprise cloud and virtual desktops span three Microsoft platforms that share the same users, devices, security baselines and connection client (`Windows App`), yet are traditionally operated as separate silos:

1. **Azure Virtual Desktop (`avd`):** Pooled multi-session (`Windows 10/11 Enterprise multi-session`) and personal single-session host pools deployed as Azure Resource Manager (`Microsoft.DesktopVirtualization`) and compute/storage resources.
2. **Windows 365 (`win365`):** Enterprise and Frontline Cloud PCs provisioned through the Microsoft Intune Graph surface (`deviceManagement/virtualEndpoint`: provisioning policies, user settings, Azure Network Connections and gallery/custom images).
3. **Microsoft Intune (`intune`):** Settings Catalog configuration profiles, security baselines, device compliance policies, Windows Update rings / Autopatch, and platform assignment filters (`deviceAndAppManagementAssignmentFilters`) governing both virtual and physical Windows endpoints.

When administrators manage these three surfaces manually across three portals (Azure Portal, Intune Admin Center and Entra Admin Center), four recurring failure modes appear:

- **Silent configuration drift:** Portal clicks leave no pull request, no code review and no link to the architectural decision that required the setting.
- **Cross-platform policy bleed:** An Intune Settings Catalog or compliance policy assigned to "All Devices" without an assignment filter hits pooled AVD multi-session session hosts, applying single-user workstation power, BitLocker or reboot settings to shared hosts serving dozens of concurrent users (`ref:intune-avd-multisession#settings-catalog-only`, `ref:windows-365-intune#assignment-filters-separate-platforms`).
- **Orphaned device records and stale compliance:** Rebuilding AVD session hosts or reprovisioning Cloud PCs leaves stale Entra ID and Intune device records behind, skewing compliance reporting and Conditional Access enforcement (`ref:intune-avd-multisession#orphaned-records`, `obs:device-records-outlive-hosts`).
- **Ungoverned day-2 mutations:** Operators run ad-hoc scripts with standing privileged roles (Intune Service Administrator, Desktop Virtualization Contributor) without automated precondition checks, session-drain verification or restore-point validation.

**Desktop DevOps** replaces manual portal administration across all three platforms with one closed-loop engineering system: declarative infrastructure and policy-as-code in Git, offline read-only fact collection, deterministic standards evaluation, longitudinal reasoning, and human-approved, gate-checked execution.

---

## 2. How Desktop DevOps differs from stateless server DevOps

Applying DevOps to cloud desktops is not identical to deploying stateless Linux containers or web APIs. Five domain constraints shape every check, contract and guardrail in `avd-assess` and the wider `avd-ops` family:

### 2.1 Three distinct Windows execution surfaces in one tenant

A single Entra tenant and Intune instance commonly governs four Windows device classes simultaneously:

| Platform surface | OS SKU / Model | Session model | Servicing & state model | Required Intune assignment filter |
|---|---|---|---|---|
| **AVD Pooled Multi-Session** | `Windows 10/11 Enterprise multi-session` (`ServerRdsh`) | Shared (`N` users per VM) | Ephemeral compute rebuilt from Compute Gallery image; profile in FSLogix on Azure Files | `(device.osSku -eq "ServerRdsh")` (`avd-multisession`) |
| **AVD Personal Single-Session** | `Windows 10/11 Enterprise` | Dedicated (`1:1` user to VM) | Persistent VM; serviced via image, update rings or Autopatch (`ref:autopatch-avd#personal-only`) | `(device.osSku -ne "ServerRdsh") and (device.deviceName -startsWith "avd-pers-")` (`avd-personal`) |
| **Windows 365 Cloud PC** | `Windows 10/11 Enterprise` (`Model -startsWith "Cloud PC"`) | Dedicated (`1:1` Enterprise) or shift-shared (`Frontline`) | Persistent Cloud PC in Microsoft-managed subscription; backed by Cloud PC restore points | `(device.model -startsWith "Cloud PC")` (`win365-cloudpc`) |
| **Physical Windows Desktop** | `Windows 10/11 Enterprise / Pro` | Dedicated hardware | Autopilot + Intune update rings / Autopatch | `(device.osSku -ne "ServerRdsh") and not (device.model -startsWith "Cloud PC")` (`physical-desktop`) |

In Desktop DevOps, **platform assignment filters are mandatory infrastructure**. Every policy-as-code deployment in `avd-intune` provisions the four platform filters first, and `avd-assess` checks both that the filters exist (`asm-intune-assignment-filters-separate-platforms`) and that no configuration policy targets All Devices without a filter (`asm-intune-no-unfiltered-all-devices`).

### 2.2 Stateful user sessions and local user state

Unlike a stateless microservice replica that can be terminated at any moment, a session host or Cloud PC holds active user work:

- **Active and disconnected sessions:** When the AVD agent is unhealthy, its reported session count can be stale while users still hold disconnected sessions with unsaved work. In `avd-swarm`, unknown session state counts as occupied (`noActiveSessions` requires both a fresh heartbeat and zero `WVDConnections` activity over the lookback window).
- **Persistent local state on Cloud PCs and personal desktops:** Reprovisioning a Windows 365 Cloud PC or replacing a personal AVD session host destroys the OS disk. Desktop DevOps enforces the family rule **"Never delete the last copy"** (`avd-second-brain` decision 0016) through the governance gate's **Data-Loss Guard (`D1`)**: any plan whose `desktopDevOpsAction` is `reprovision`, `deprovision` or `replace-session-host` is refused unless `dataLossGuard` proves either a verified Cloud PC / VM restore point within 24 hours (`restorePointVerified: true`, `restorePointAgeHours <= 24`) or explicit owner approval (`discardLastCopyApproved: true`).

### 2.3 Two FinOps cost models in one desktop estate

Desktop DevOps must evaluate and optimize two fundamentally different billing models side by side (`methods/finops.md`, `gaps/finops-scope.md`):

- **AVD consumption billing (hourly compute, storage and bandwidth):** Governed by autoscale schedules, Start VM on Connect (`asm-personal-start-vm-on-connect`), right-sizing against measured concurrency (`c12`), and Azure Reservations / Savings Plans.
- **Windows 365 step-function licensing (`CPC_E_*`, `WINDOWS_365_*`):** Billed per seat per month regardless of whether the Cloud PC is powered on. Waste on Windows 365 comes from purchased licenses sitting unassigned (`c11.entra.skuWin365Available`) or provisioned Cloud PCs with zero connections over 14 to 30 days, where deprovisioning (after a verified restore point) or converting inactive Enterprise seats to Frontline shared seats reclaims spend.

### 2.4 Two governed write paths: GitOps PRs vs. runtime plans

Desktop DevOps separates **fleet configuration changes** from **tactical runtime operations**:

| Change category | Examples | Governed write path | Why |
|---|---|---|---|
| **Fleet configuration & policy** | Changing an Intune Settings Catalog policy, adding a Conditional Access rule, updating a Cloud PC provisioning policy or Bicep parameter | **GitOps Pull Request** (`desktopDevOpsAction: policy-pr` against `avd-intune`, `avd-entra` or `avd-landing-zone`) | Fleet policies affect every host or Cloud PC at once; they require a Git diff, schema validation (`scripts/validate.py`), CI checks and code review before merge |
| **Tactical runtime action** | Draining an unhealthy session host, restarting the AVD agent, restarting or resizing a single Cloud PC, taking an on-demand Cloud PC restore point | **Gate-Checked Runtime Plan** (`propose_change` / `C9` -> `avd-swarm` gate -> GitHub Environment `approve`) | Tactical actions target a single resource in response to live telemetry (`C11` / KQL / Graph), verify preconditions live before acting, and confirm recovery by positive evidence |

Neither path ever executes directly from chat or uses a standing write credential in an agent process.

### 2.5 Optionality and intake-driven scoping (`not-applicable` vs. `gap`)

Many organizations run AVD only, Windows 365 only, or both under Intune. A Desktop DevOps assessment never penalizes an estate for a platform it does not use:

- Contract **C19** (`intake.schema.json`) records `intake.avdScope` (`pooled`, `personal`, `both`, `not-used`) and `intake.win365Scope` (`not-used`, `enterprise`, `frontline`, `both`).
- Every Windows 365 check in `method.json` carries a `when` clause (`intake.win365Scope != 'not-used'`). When Windows 365 is not used, those checks evaluate to `not-applicable` (`gap:scoring`), keeping pillar coverage and scores accurate.

---

## 3. The six-stage Desktop DevOps lifecycle across the `avd-ops` family

```
+-----------------------------------------------------------------------------+
| Stage 1: INTAKE & USE CASES (avd-assess C19, use-cases.yaml)                |
|   Define personas, workload classes, avdScope, win365Scope, security goals  |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 2: DECLARATIVE BUILD & POLICY-AS-CODE (GitOps Foundation)             |
|   avd-landing-zone + avd-azure (Bicep) | avd-entra (Groups, CA, SSO)        |
|   avd-intune (Assignment filters, Settings Catalog, Win365 policies)        |
|   avd-m365 (FSLogix, OneDrive KFM, Teams VDI) | avd-power-platform (DLP)    |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 3: OFFLINE READ-ONLY SENSING & REDACTION (avd-current-state)          |
|   Collect Azure ARM, Entra, Intune & Windows 365 Graph state read-only      |
|   Emit redacted avd-current-state-facts/v1 (C11) using C15 fact register    |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 4: DETERMINISTIC ASSESSMENT & DRIFT CHECK (avd-assess C20, C21, C24)  |
|   Run method.json checks against C11 + C19 -> C21 assessment report         |
|   Review findings (C23) -> generate ordered C24 remediation plan            |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 5: LONGITUDINAL MEMORY & DIAGNOSIS (avd-second-brain C9, C10, C18)    |
|   Correlate C11 drift + C12 UX telemetry + C18 lifecycle decision history   |
|   Emit C9 playbook proposals (targetSurface, desktopDevOpsAction, guard)    |
+--------------------------------------+--------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage 6: GATED EXECUTION & POSITIVE VERIFICATION (avd-swarm)                |
|   Check V1-4 operator provenance, D1 dataLossGuard, host preconditions      |
|   Human approves in GitHub Environment -> apply -> verify -> C10 outcome    |
+-----------------------------------------------------------------------------+
```

### Stage 1: Intake and use-case mapping (`avd-assess`)

Before inspecting resources, the operator captures what telemetry cannot infer (`methods/use-cases.md`, `gaps/intake.md`):

- Which user personas exist (`use-cases.yaml`: task worker, knowledge worker, developer, graphics, contact center, contractor) and whether each persona fits pooled multi-session AVD, personal AVD or a Windows 365 Cloud PC.
- Which desktop platforms are in scope (`intake.avdScope`, `intake.win365Scope`), how hosts are managed (`intake.hostManagement`), and what client devices must prove (`intake.clientDevices`).

### Stage 2: Declarative build and policy-as-code (`avd-landing-zone` + five control-plane repos)

Each control plane is versioned in its own repository and orchestrated by `avd-landing-zone`:

- **`avd-azure` / `avd-hcl`:** Host pools, session hosts, Compute Gallery, Azure Files Premium ZRS profile storage, Private Endpoints and scaling plans -- in Bicep (`avd-azure`, zero-state Azure-native) or Terraform and Packer (`avd-hcl`, recommended enterprise IaC option for multi-provider orchestration, explicit state, and `plan` fidelity).
- **`avd-entra`:** Security and dynamic device groups (including `cloudPcDynamicGroupId` with rule `(device.devicePhysicalIds -any (_ -startsWith "[OrderId]:"))` or `(device.model -startsWith "Cloud PC")`) and Conditional Access policies requiring phishing-resistant MFA across both the AVD client app and the Windows 365 web client first-party enterprise applications.
- **`avd-intune`:** Four platform assignment filters (`profiles/filters/*.json`), multi-session Settings Catalog baselines (`profiles/settings-catalog/*.json`), and Windows 365 provisioning policy and user-setting templates (`profiles/win365/*.json`), deployed idempotently via `Deploy-AvdIntune.ps1 -DeployAssignmentFilters -IncludeWin365`.
- **`avd-m365`:** Shared Computer Activation, OneDrive Known Folder Move and Files On-Demand, and Teams media optimization.
- **`avd-power-platform`:** Dedicated environments and DLP connector policies for administrative and day-2 flows.

### Stage 3: Offline read-only sensing and redaction (`avd-current-state`)

`avd-current-state` collects the live estate without holding any write permission (`tests/ReadOnlyGuard.Tests.ps1` enforces read-only verbs across the entire repository):

- `Get-AvdStateIntune` in `lib/AvdRebuild.psm1` queries Microsoft Graph read-only endpoints for Settings Catalog policies, MDM auto-enrollment, device assignment filters (`deviceAndAppManagementAssignmentFilters`), managed devices (`managedDevices`), Windows 365 Cloud PCs (`virtualEndpoint/cloudPCs`), provisioning policies (`virtualEndpoint/provisioningPolicies`), user settings (`virtualEndpoint/userSettings`), and Azure Network Connections (`virtualEndpoint/onPremisesConnections`).
- `avd_current_state_facts.ps1` normalizes and redacts the package offline into a `C11` snapshot (`avd-current-state-facts/v1`): only counts, booleans, public enums and keyed HMAC pseudonyms (`hp-3fa2c1d0`) leave the collector. Real tenant IDs, subscription IDs, user principal names, device names and IP addresses are stripped and checked by a post-redaction leak guard.

### Stage 4: Deterministic assessment and remediation planning (`avd-assess`)

`avd-current-state`'s assessment engine (`lib/AvdAssess.psm1`) and browser portal (`site/portal/`) evaluate the redacted `C11` snapshot and `C19` intake against the pinned `method.json` (`C20`):

- Every check is a deterministic rule over registered `C15` facts, citing pinned upstream claims (`ref:`), family observations (`obs:`) or documented gaps (`gap:`). No language model ever decides a check outcome or a score.
- Each check carries a structured `remediation` hint (`lz-parameter`, `lz-setting` or `manual`) naming the exact control plane (`azure`, `entra`, `intune`, `m365`, `power-platform`) and setting that resolves a finding (`methods/remediation.md`).
- Reviewing the `C21` assessment report produces a `C23` review (`review.json`) and a `C24` remediation plan (`plan.json`).

### Stage 5: Longitudinal memory, diagnosis and playbook proposals (`avd-second-brain`)

When the optional intelligence layer is deployed, `avd-second-brain` ingests the redacted `C11` snapshots, optional `C12` forensic user-experience summaries, and `C18` environment lifecycle records:

- It correlates symptoms across control planes (for example, distinguishing a slow logon caused by Azure Files storage latency from one caused by an unfiltered Intune script policy or a failing Cloud PC Azure Network Connection).
- When a playbook applies, it emits a `C9` proposal carrying `targetSurface` (`avd`, `win365`, `intune`), `desktopDevOpsAction` (`restart`, `resize`, `reprovision`, `deprovision`, `restore-point`, `replace-session-host`, `policy-pr`), and `dataLossGuard`.

### Stage 6: Gated execution, human approval and positive verification (`avd-swarm`)

`avd-swarm` is the only component that can execute a change, and only after deterministic gate checks and human approval:

- **Scheduled and manual read-only runbooks (`runbooks/`):** `hosts.agent-unhealthy`, `hosts.connection-errors`, `hosts.cloudpc-health`, `cost.idle-hosts`, and `intune.policy-drift` evaluate fixed facts first and invoke a specialist agent (`hosts`, `cost`, `intune`) within a strict token budget only when a check fails with `onFail: investigate`.
- **Deterministic governance gate (`gate/avd_gate/`):** Checks operator thread provenance (`V1-4`), the Desktop DevOps data-loss guard (`D1`), host preconditions (`noActiveSessions`, `notDrainedByOthers`, `hostPoolAvailableHostsAbove`), spend caps and Defender for Cloud compliance floors.
- **Human approval in a GitHub Environment (`approve`):** No standing write token exists in any agent container. Only approving the plan in the adopter's private repository mints a short-lived OIDC federated credential scoped to the action, re-verifies live state against the approved plan hash, executes the change, verifies positive post-change telemetry, and emits a `C10` outcome event back to the brain.

---

## 4. Desktop DevOps check and fact traceability matrix

Every Desktop DevOps check in `method.json` traces from its upstream source claim (`references/windows-365-intune.yaml`, `references/intune-avd-multisession.yaml`) through its `C15` fact IDs to its foundation remediation target and `avd-swarm` runbook:

| Check ID (`method.json`) | Plane | Pillar | Severity | C15 Facts Evaluated | Upstream Claims Cited | Foundation Remediation Target | `avd-swarm` Runbook / Action |
|---|---|---|---|---|---|---|---|
| `asm-intune-no-policy-noncompliant` | `intune` | `security` | `high` | `c11.intune.noPolicyMeansNoncompliant` | `ref:intune-compliance#no-policy-default-compliant`, `ref:graph-device-management-settings#secure-by-default` | `avd-intune`: `intune-compliance-secure-by-default` | `intune.policy-drift` (`policy-pr`) |
| `asm-intune-fslogix-configured` | `intune` | `reliability` | `high` | `c11.intune.fslogixProfileConfigured` | `ref:intune-avd-multisession#settings-catalog-only`, `ref:fslogix-settings#roamidentity-off` | `avd-intune`: `profiles/settings-catalog/fslogix-profile.json` | `intune.policy-drift` (`policy-pr`) |
| `asm-intune-shortpath-configured` | `intune` | `network` | `medium` | `c11.intune.rdpShortpathConfigured` | `ref:rdp-shortpath#udp-transport`, `ref:intune-avd-multisession#settings-catalog-only` | `avd-intune`: `profiles/settings-catalog/rdp-shortpath.json` | `intune.policy-drift` (`policy-pr`) |
| `asm-intune-session-limits-configured` | `intune` | `cost` | `medium` | `c11.intune.sessionTimeLimitsConfigured` | `ref:intune-avd-multisession#settings-catalog-only`, `ref:review-checklists-avd#E01.03` | `avd-intune`: `profiles/settings-catalog/session-time-limits.json` | `intune.policy-drift` (`policy-pr`) |
| `asm-intune-no-multisession-update-ring` | `intune` | `operations` | `medium` | `c11.intune.multiSessionUpdateRingAssigned` | `ref:intune-avd-multisession#quality-updates-catalog-only`, `ref:autopatch-avd#personal-only` | `avd-intune`: exclude `avd-multisession` filter on update rings | `intune.policy-drift` (`policy-pr`) |
| `asm-intune-assignment-filters-separate-platforms` | `intune` | `security` | `high` | `c11.intune.multiSessionFilterPresent`, `c11.intune.unfilteredAllDevicesPolicies` | `ref:windows-365-intune#assignment-filters-separate-platforms`, `ref:intune-avd-multisession#settings-catalog-only` | `avd-intune`: `Deploy-AvdIntune.ps1 -DeployAssignmentFilters` (`profiles/filters/*.json`) | `intune.policy-drift` (`policy-pr`) |
| `asm-win365-sso-enabled` | `intune` | `security` | `high` | `c11.intune.win365.ssoEnabledOnAllPolicies` (when `intake.win365Scope != 'not-used'`) | `ref:windows-365-intune#provisioning-policy-sso` | `avd-intune`: `profiles/win365/provisioning-policy.json` (`enableSingleSignOn: true`) | `hosts.cloudpc-health` (`policy-pr`) |
| `asm-win365-no-local-admin` | `intune` | `security` | `high` | `c11.intune.win365.localAdminDisabled` (when `intake.win365Scope != 'not-used'`) | `ref:windows-365-intune#user-settings-least-privilege` | `avd-intune`: `profiles/win365/user-setting.json` (`localAdminEnabled: false`) | `hosts.cloudpc-health` (`policy-pr`) |
| `asm-win365-restore-points-24h` | `intune` | `reliability` | `medium` | `c11.intune.win365.restorePointFrequencyHoursMax` (when `intake.win365Scope != 'not-used'`) | `ref:windows-365-intune#restore-point-cadence` | `avd-intune`: `profiles/win365/user-setting.json` (`frequencyInHours <= 12`) | `hosts.cloudpc-health` / `D1` `dataLossGuard` |
| `asm-win365-anc-healthy` | `intune` | `network` | `high` | `c11.intune.win365.ancFailedCount` (when `intake.win365Scope != 'not-used'`) | `ref:windows-365-intune#anc-health-checks` | `avd-intune` + `avd-azure`: `win365-anc-subnet-dns-remediation` | `hosts.cloudpc-health` |
| `asm-win365-cloudpcs-compliant` | `intune` | `security` | `high` | `c11.intune.cloudPcManagedCompliant`, `c11.intune.cloudPcManagedNoncompliant` (when `intake.win365Scope != 'not-used'`) | `ref:windows-365-intune#cloudpc-intune-compliance`, `ref:ca-require-compliant-device#compliance-signal` | `avd-intune`: `win365-cloudpc-compliance-policy` + `avd-entra` Conditional Access | `intune.policy-drift` (`policy-pr`) |
