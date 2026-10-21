# Gap: the remediation plan

**Searched (2026-10-21):** the Well-Architected Review's guidance on implementing recommendations (`ref:waf-review-assessment#export-to-backlog`, `ref:waf-review-assessment#prioritize-with-tradeoffs`, `ref:waf-review-assessment#track-until-resolved`), the Cloud Adoption Framework's AVD deployment guidance (`ref:caf-avd-deploy#persona-iterations`), Azure Advisor's cost recommendations (`ref:advisor-cost#right-size-or-shutdown-vms`), the AVD review checklist (`ref:review-checklists-avd`) and APRL (`ref:aprl-desktop-virtualization`). **Not found:** a structured AVD remediation plan that ties each finding to the deployment change that fixes it. The Well-Architected Review exports recommendations as a CSV for a backlog, with links to guidance but no change to make; the checklist and APRL say what good is, not which template parameter gets there; Advisor covers one subscription and a few kinds of change.

Recommendation and remediation planning is the fifth stage of an assessment. It reads what the review decided (contract C23) and writes an ordered plan (contract C24, `avd-remediation-plan/v1`). The plan says what to change; avd-landing-zone makes the change, and avd-current-state's next run shows whether it worked. Nothing here writes to an estate.

## What we write

**A remediation hint per check** in [method.json](../method.json), one of three kinds:

| Kind | Means | Carries |
|---|---|---|
| `lz-parameter` | An avd-landing-zone parameter fixes it | The parameter's name and, where it is one public value, the value |
| `lz-setting` | The landing zone always applies the fix, so redeploying from it fixes the finding | A short name for the setting |
| `manual` | Outside what a landing zone redeploy fixes | A code: `collect-evidence` (the outcome was unknown), `rebuild-hosts` (hosts the landing zone deploys have it; existing hosts must be replaced), `private-value` (needs a value only the operator holds), `outside-landing-zone`, `process` (an operating practice, not a setting), `no-known-change` |

Values are public only: a SKU, a count, a boolean, a region. Anything that needs a name, a prefix or an address is `manual` with `private-value`, and the operator puts it in their own parameter file.

**Version 3's hints**, read from avd-landing-zone at the commit in `method.json`'s `landingZoneCommit`:

| Check | Kind | Name, value | Where the landing zone does it |
|---|---|---|---|
| `asm-personal-start-vm-on-connect` | lz-parameter | `startVmOnConnect`, true | [main.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/main.bicep) |
| `asm-pooled-host-redundancy` | lz-parameter | `sessionHostCount`, 2 | [main.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/main.bicep) |
| `asm-files-private-endpoint` | lz-setting | `profile-storage-private-endpoint` | [storage.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/modules/storage.bicep) (private endpoint on the profile share) |
| `asm-files-zone-redundant` | lz-parameter | `profileStorageSku`, Premium_ZRS | [main.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/main.bicep) |
| `asm-hosts-trusted-launch` | manual, `rebuild-hosts` | none: the security type is set when a VM is created, so a redeploy doesn't convert existing hosts | [sessionHosts.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/modules/sessionHosts.bicep) (`securityType`) |
| `asm-drive-usb-redirection-off` | lz-parameter | `rdpProperties` (its default leaves drive and USB redirection empty) | [main.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/main.bicep) |
| `asm-defender-servers` | lz-parameter | `enableDefenderForCloud`, true | [governance.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/modules/governance.bicep) |
| `asm-files-smb-gcm` | lz-setting | `profile-storage-smb-gcm` | [storage.bicep](https://github.com/avd-ops/avd-landing-zone/blob/ae6e80b574cccde570d0053d4c62b519d31052a8/bicep/modules/storage.bicep) (`channelEncryption`) |

**The order of the plan.** Items are numbered 1, 2, 3 by a rule a tool applies with no judgment: gap before warn before unknown, then severity (high, medium, low), then the check ID. The order says what matters most, not when it is done: every `lz-parameter` and `lz-setting` item lands in the same landing zone redeploy. A person changes priorities in the review (C23), not in the plan.

**Which subject a hint covers.** A landing zone hint fixes what the landing zone deployed: its host pools and its profile storage account. A check can fail on a resource the landing zone doesn't own, such as another team's storage account in the same subscription; for that subject the plan item is `manual` with `outside-landing-zone`, whatever the check's hint says.

**Which findings make items.** The review's Fix rows, plus every check that isn't a pass and has no review row (or every such check when there is no review), marked `unreviewed`, as contract C23 says. A plan never hides a finding nobody looked at. Accept and Defer rows make no item; their reasons stay in the review. An `unknown` outcome always plans `manual` with `collect-evidence`, and the C24 schema refuses anything else for it.

## Not yet known

- Whether one landing zone redeploy applies every `lz-setting` in place is not yet tested. Trusted launch, set at VM creation, is already `rebuild-hosts`; another setting may turn out the same. Until a run shows it, the plan says what to change, not how disruptive the change is.
- An effort or disruption field would let the order weigh cost against benefit, as the Well-Architected Review leaves to the team (`ref:waf-review-assessment#prioritize-with-tradeoffs`). We add it only when a run gives evidence for the values.
