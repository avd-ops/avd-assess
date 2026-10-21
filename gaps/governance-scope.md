# Gap: what a governance assessment can judge, and from where

**Searched (2026-10-21):** Azure Policy's assignment structure and built-in definitions (`ref:policy-assignment-structure`, `ref:policy-built-ins`), the Cloud Adoption Framework's AVD security and governance page (`ref:caf-avd-security-governance`, deprecated and due off Learn on 2026-10-30, pinned on GitHub) and its abbreviations (`ref:caf-resource-abbreviations`), AVD tagging, data locations, RBAC, the administrative template and host management (`ref:avd-tagging`, `ref:avd-data-locations`, `ref:avd-rbac`, `ref:avd-admin-template`, `ref:avd-management`), the activity log (`ref:activity-log`), the benchmark's logging control and its AVD baseline (`ref:mcsb-logging`, `ref:mcsb-avd-baseline`), Defender for Cloud's regulatory compliance (`ref:defender-regulatory-compliance`), the review checklist (C03, D03.01, E01.01, E01.02, E01.07, G03.05, G03.06), the family knowledge bases and the web. **Not found:** a minimum set of Azure Policy assignments for an AVD subscription, a retention number for audit logs, or a change control process for AVD. Each source says to have one; none says what it is.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Control plane | Policy assignments in scope, inherited ones included, and how many are in DoNotEnforce; role assignments by role name; Defender plans; regions | Reader (C11 facts built) |
| Rebuild | The activity log export, tags and diagnostic settings as deployed | avd-current-state's rebuild package; C11 facts proposed |
| Operator | Compliance frameworks in scope, audit retention required, how changes are made | Intake (the proposed questions below) |
| Host | Whether the AVD template settings come from Intune, Group Policy or local policy | A host-side read, which no family collector does yet |

## The guardrail checks

Two checks run on the built policy facts, both `warn`, because a subscription can be governed from a management group the operator doesn't own. The producer reads assignments with the cmdlet that includes those inherited from management groups (gap:collection-map).

- `asm-policy-guardrails-assigned` (low): a subscription holding AVD has at least one policy assignment in scope (`ref:mcsb-avd-baseline#AM-2`). It is a floor, not a judgment of the guardrails: Defender for Cloud's default benchmark assignment alone passes it, so a fail means no policy reaches the subscription at all. The landing zone fix is `enablePolicyGuardrails`.
- `asm-policy-enforced` (low): no assignment in scope is left in DoNotEnforce, which evaluates without enforcing and is meant for trying an assignment out (`ref:policy-assignment-structure#do-not-enforce`, `ref:policy-assignment-structure#do-not-enforce-for-testing`). The fix is a process step, not a redeploy.

A count can't say which policies are assigned. Judging named guardrails (allowed locations against the residency answer, allowed sizes against the sizing choice, private access, tags) needs `proposed:c11.policy.builtInDefinitions`, the built-in definition names in scope. Built-in names are public; assignment names and custom definitions may not be, so the fact would carry built-in names only, and anything custom as a count. Until avd-current-state builds it, the governance.locations and governance.allowed-sizes rows read the landing zone's own parameters from the rebuild package and are `unknown` for guardrails it didn't deploy.

## Compliance frameworks are mappings

The method never says an estate complies with a framework. It records which frameworks the operator says apply, notes that Defender for Cloud assesses the benchmark by default and other standards only with a paid plan (`ref:defender-regulatory-compliance#mcsb-default`, `ref:defender-regulatory-compliance#more-standards-need-paid-plan`), and maps findings to benchmark controls. The dashboard shows gaps against controls, not a certification (`ref:defender-regulatory-compliance#assessed-against-controls`).

## The benchmark's AVD baseline, control by control

Every control in the AVD security baseline (`ref:mcsb-avd-baseline`) now has a claim, and the table names the map row or pillar that judges it. Controls the baseline marks not supported for the service are kept so a reader sees they were checked.

| Control | Map row | Note |
|---|---|---|
| NS-1, NS-2 | networking rows | Session hosts in a customer network; Private Link by need |
| IM-1, IM-7 | identity pillar | Entra ID and Conditional Access |
| IM-3 | governance.rbac | Managed identities for automation |
| IM-8, PA-8, DP-5, DP-6, DP-7, PV-6 | none | Not supported for the service |
| PA-1 | security.posture | Local admin account for emergencies only |
| PA-7 | governance.rbac | Built-in AVD roles, least privilege |
| DP-1, DP-2 | endpoints.peripherals | Classification and data loss prevention; redirection is the leak path |
| DP-3, DP-4 | encryption rows | In transit; platform keys at rest |
| AM-2 | governance.policy-guardrails | Azure Policy audit and enforce |
| AM-5 | hostpool.app-group | RemoteApps narrow what users can run |
| LT-1, ES-1, ES-2, ES-3 | security.endpoint-protection-tuning | Threat detection, EDR, anti-malware and its updates |
| LT-4 | governance.audit-logging | Resource logs for investigation |
| PV-3, PV-5 | images and security rows | Secure image baseline, vulnerability assessment |
| BR-1 | reliability rows | Azure Backup for hosts and shares |

## Proposed intake questions

Three answers (one a list), registered as `specified` C19 facts; the intake schema changes once, at the end of the pillar batch (gaps/intake.md).

| Fact | Question | Values |
|---|---|---|
| `intake.complianceFrameworks` | Which compliance frameworks apply? | a list of `cis`, `iso-27001`, `nist-800-53`, `nist-800-171`, `pci-dss`, `hipaa`, `soc2`, `fedramp`, `other`, or `none` alone |
| `intake.auditRetentionDays` | How long must audit logs be kept, in days? | an integer from 0 to 4383 (12 years, the longest a workspace keeps it, `ref:activity-log#workspace-retention-12-years`) |
| `intake.changeControl` | How are changes to the estate made? | `pipeline-only`, `ticketed`, `ad-hoc`, `unknown` |

## Change control

No AVD source sets a change process. The method asks how changes are made and, when the answer is `pipeline-only`, treats drift between the deployed estate and its last deployment as a finding. Staged policy rollout (`ref:policy-assignment-structure#enroll-staged`) is the one published pattern it cites.
