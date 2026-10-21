# Gap: mapping facts to review checklist items

**Searched (2026-10-20):** the AVD review checklist (`ref:review-checklists-avd`), APRL's AVD recommendations (`ref:aprl-desktop-virtualization`), the Well-Architected reliability checklist (`ref:waf-reliability-checklist`), Microsoft Learn, the web. **Not found:** a mapping from the AVD checklist's items to the data that shows whether an estate meets them. The checklist's AVD items carry no Resource Graph query; APRL's reliability items do, and WARA runs them.

**What we write.** For each item we can evidence, the facts that decide it, by fact ID in avd-second-brain's fact register (C15), and the rule. The rules that run are the `checks` in [method.json](../method.json). Items that need data the family doesn't collect yet stay listed here with the fact or rule they would need. That list is a to-do for avd-current-state's facts.

## Checks that run (method.json version 2)

| Check | Item | Facts | Rule |
|---|---|---|---|
| `asm-personal-start-vm-on-connect` | `ref:review-checklists-avd#E01.05` | `c11.hostPool.type`, `c11.hostPool.startVmOnConnect` | Personal host pools have Start VM on Connect on (warn) |
| `asm-pooled-host-redundancy` | `ref:waf-reliability-checklist#RE:05` | `c11.hostPool.type`, `c11.hostPool.sessionHosts.total` | Pooled host pools have at least two session hosts (warn) |
| `asm-files-private-endpoint` | `ref:review-checklists-avd#F01.10` | `c11.storage.kind`, `c11.storage.privateEndpoint` | Premium file storage has a private endpoint (warn) |
| `asm-files-zone-redundant` | `ref:review-checklists-avd#A03.05` | `c11.storage.kind`, `c11.storage.sku` | Premium file storage is zone-redundant (warn) |
| `asm-hosts-trusted-launch` | `ref:review-checklists-avd#G02.03` | `c11.hostPool.sessionHosts.notTrustedLaunch` | Every session host whose VM was read is Trusted launch with Secure Boot and vTPM on (warn; `obs:trusted-launch-by-default`) |
| `asm-drive-usb-redirection-off` | `ref:review-checklists-avd#G02.06` | `c11.hostPool.redirection.drives`, `c11.hostPool.redirection.usb` | Drive and USB redirection are set off; not set counts as a warn too (`obs:redirection-kept-for-usability`) |
| `asm-defender-servers` | `ref:review-checklists-avd#G03.04` | `c11.subscription.defenderPlans` | The Servers plan (`VirtualMachines`) is on the Standard tier (warn) |
| `asm-files-smb-gcm` | `ref:mcsb-avd-baseline#DP-3` | `c11.storage.kind`, `c11.storage.smbChannelEncryption` | Premium file storage allows AES-128-GCM and AES-256-GCM and no CCM (warn; `obs:smb-channel-aes128-gcm-needed`) |

Every check is a `warn`, not a `gap`. The first four items say "consider" or "evaluate", and the facts can't tell which storage account holds profiles, so a failure is a trade-off to review; the security checks are warns because a deliberate trade-off is allowed with its reason (`gap:security-scope`). The storage checks see only premium (`FileStorage`) accounts. Standard file shares in a general-purpose account are missed until a fact says which accounts hold shares.

## Items that need something we don't collect yet

| Item | What it needs |
|---|---|
| `ref:review-checklists-avd#H03.05` | The profile storage account's region beside its host pool's. C11 has both regions, but nothing links a share to a pool, and the rule language has no join |
| `ref:review-checklists-avd#E02.02`, `ref:review-checklists-avd#E02.01` | Diagnostic settings per AVD object, and the agent and Insights data collection rule per host (facts specified in `gap:insights-facts`, waiting to be built; the standard is `ref:avd-insights#hostpool-diagnostics`, `ref:avd-insights#workspace-diagnostics`, `ref:avd-insights#host-data-ama-dcr`) |
| `ref:review-checklists-avd#E01.10`, `ref:aprl-desktop-virtualization#979ff8be-5f3a-4d8e-9aa3-407ecdd6d6f7`, `ref:psrule-azure#AZR-000437` | The host pool's `agentUpdate` setting (`ref:avd-rest-api#hostpool-properties`; a new C11 fact) |
| `ref:review-checklists-avd#E01.11`, `ref:aprl-desktop-virtualization#013ac34e-7c4b-425f-9e0c-216f0cc06181` | C11 has `validationEnvironment` per pool, but the item asks for at least one per estate, and the rule language has no "any" |
| `ref:aprl-desktop-virtualization#499769ae-67c9-492e-9ca5-cfd4cece5209` | Scaling plans and the pools they reference (`ref:avd-rest-api#scalingplan-hostpool-references`; `c11.hostPool.scalingPlan.method`, specified in `gap:monitoring-scope`) |
| `ref:review-checklists-avd#C01.05`, `ref:session-host-sizing#multisession-vcpu-range` | vCPUs per session host size (a public SKU value; a new C11 fact) |
| `ref:review-checklists-avd#C01.06` | C11 counts app groups by type per pool, but a missing type means zero, and the rule language reads a missing property as unknown |
| `ref:review-checklists-avd#E01.13` | The last time each session host was on; C11's stale-heartbeat count has no stated threshold |
| `ref:review-checklists-avd#A01.06`, `ref:aprl-desktop-virtualization#38721758-2cc2-4d6b-b7b7-8b47dadbf7df` | Site Recovery or backup protection for personal session hosts (a new C11 fact) |
| `ref:review-checklists-avd#F01.11`, `ref:review-checklists-avd#H04.03` | Host-side settings (RDP Shortpath, FSLogix size limit): no host fact exists |
| `ref:review-checklists-avd#E01.04`, `ref:review-checklists-avd#E01.08`, `ref:review-checklists-avd#E02.03`, `ref:review-checklists-avd#E02.04` | Scaling plans, Advisor recommendations, storage alerts and Service Health alerts: facts specified in `gap:monitoring-scope`, waiting to be built |
| `ref:review-checklists-avd#G03.05` | Diagnostic settings per AVD object, as for E02.02 (`gap:insights-facts`) |
| `ref:review-checklists-avd#D02.01` | `c11.storage.filesIdentity` is built, but the rule needs it beside `intake.identityConstraints` (Entra-only estates use Entra Kerberos), and the rule language has no join between a snapshot and the intake |
| `ref:review-checklists-avd#G02.04` | Which hosts run Windows 11; C11's OS versions are build numbers per pool, so the Trusted launch check above stands in |
| `ref:review-checklists-avd#G03.03`, `ref:review-checklists-avd#G04.01` | Local administrators on the hosts (host-side) and Conditional Access or MFA for AVD sign-in (a directory read): neither is collected (`gap:security-scope`) |
| `ref:review-checklists-avd#H03.03`, `ref:review-checklists-avd#H04.01`, `ref:review-checklists-avd#H04.02`, `ref:review-checklists-avd#H04.04` to `ref:review-checklists-avd#H04.07`, `ref:review-checklists-avd#B02.01`, `ref:review-checklists-avd#B02.03`, `ref:review-checklists-avd#B02.05`, `ref:review-checklists-avd#B02.06` | Host-side reads: FSLogix settings, antivirus exclusions, which share a host or package uses, package certificate trust and Store auto-update; and the share-to-pool join (`gap:app-delivery-scope`) |
| `ref:review-checklists-avd#B02.02`, `ref:review-checklists-avd#H01.02`, `ref:review-checklists-avd#H02.02`, `ref:review-checklists-avd#A03.02`, `ref:review-checklists-avd#A03.04` | Facts specified in the register, not built: App Attach image format and registration per pool, `c11.storage.smbMultichannel`, `c11.netApp.smbVolumesWithoutContinuousAvailability`, `c11.storage.backupProtected` |
| `ref:review-checklists-avd#H02.01`, `ref:review-checklists-avd#H02.03`, `ref:review-checklists-avd#A03.01`, `ref:review-checklists-avd#A03.03`, `ref:review-checklists-avd#A03.06`, `ref:review-checklists-avd#B02.04` | Decisions the operator records in review (ANF region and AD site, which profile data to protect, the replication and recovery plan, vendor packages); no fact decides them |
| `ref:review-checklists-avd#D03.02`, `ref:review-checklists-avd#D03.04`, `ref:review-checklists-avd#D03.05`, `ref:review-checklists-avd#D01.06` | The identity pillar's facts: join type, single sign-on and direct user assignments are `specified` C11 facts no collector reads yet; The tenant's single sign-on setting needs a directory read, as Conditional Access does for G04.01 above (`gap:identity-scope`). The other D items are about Active Directory, which no collector reads, and stay intake or manual |

## The same items in PSRule for Azure

avd-landing-zone checks its templates and its deployed resources with PSRule for Azure (`ref:psrule-azure`), so a template finding there and an assessment item here should name the same thing. Searched (2026-10-21): PSRule's rule reference at the pinned version. Two of its rules match items above, and each is cited beside them:

| PSRule rule | Same item | How far it matches |
|---|---|---|
| `ref:psrule-azure#AZR-000437` | `ref:review-checklists-avd#E01.10`, `ref:aprl-desktop-virtualization#979ff8be-5f3a-4d8e-9aa3-407ecdd6d6f7` | The same item |
| `ref:psrule-azure#AZR-000195` | `ref:review-checklists-avd#A03.05` (check `asm-files-zone-redundant`) | Partly: the rule covers every storage account and also passes geo replication; the item and the check ask for zone-redundant file storage |

PSRule has no rule for Start VM on Connect, pooled host redundancy or a private endpoint on file storage, so the other checks cite only the checklist. We write no rules of our own: a new match gets a claim in `references/psrule-azure.yaml` and a row here.

The two rule-language limits (no join across subjects, and no "any") are avd-second-brain C20 changes, proposed when a check needs them.
