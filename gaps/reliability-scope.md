# Gap: what a reliability assessment covers, what it can measure, and which repo does what

**Searched (2026-10-21):** the review checklist's reliability items (`ref:review-checklists-avd#A01.01` to `ref:review-checklists-avd#A03.06`), the AVD disaster recovery concepts and service resilience pages (`ref:avd-disaster-recovery`, `ref:avd-service-resilience`), the Architecture Center's multiregion guide (`ref:avd-multiregion-bcdr`), the Cloud Adoption Framework's AVD BCDR article (`ref:caf-avd-bcdr`, deprecated), the Well-Architected disaster recovery strategy (`ref:waf-disaster-recovery`), and the Azure Files, Compute Gallery, Site Recovery, Azure NetApp Files and Entra recoverability pages listed in the method. Microsoft has no AVD service reliability guide among its per-service reliability pages. **Not found:** a method that says which recovery requirements an assessment can judge from read-only data, an SLA figure for the AVD service itself, any way to see a recovery test's result in Azure, and a single source that agrees with itself on Azure NetApp Files replication.

**What we write.** This page and [methods/reliability.md](../methods/reliability.md) are the map's reliability method; the sources stay the authority.

1. **Targets are intake.** No platform setting says what the business needs. Without `intake.recoveryTime` and `intake.recoveryPoint` the method reports what exists and judges nothing against a target.
2. **Three kinds of evidence.** Control plane with Reader (host zones, host pool type and region, storage SKU, backup protected items, backup jobs and Site Recovery replicated items in the RecoveryServicesResources table, `ref:resource-graph-tables#recovery-services-table`, image versions and their target regions). The operator's answer (targets, region loss in scope, dependencies, what profile data matters). A run record (contract C17, use case `recovery`) for a restore or failover test. Unlike security and network, Insights adds nothing here: nothing it measures proves recovery. Anything else is `unknown`.
3. **A configured backup is not a working one.** A snapshot-tier backup keeps its copies in the account it protects (`ref:azure-files-backup#snapshot-and-vaulted`). Microsoft's pages differ on the key access a backup needs: the support matrix asks for account key access (`ref:files-backup-support#key-access-needed`), the portal guide accepts key access off when public network access is disabled (`ref:files-backup-portal#keys-or-private`). So the method never judges the key setting; a backup counts once its last job succeeded (`c11.storage.lastBackupJob`), and a policy with no successful job is `unknown` (`obs:files-backup-key-access-off`).
4. **Zones are availability, not recovery** (`ref:avd-multiregion-bcdr#zones-not-dr`). A pool spread across zones passes the zone row and says nothing about the region rows.
5. **A test is the only proof.** A tier's RTO and RPO are estimates until a run times them (`ref:avd-multiregion-bcdr#estimates-to-test`, `ref:waf-disaster-recovery#drills-prove-targets`). Without a run record the recovery-test row is `gap`, never `pass`.
6. **Sources disagree on Azure NetApp Files.** The multiregion guide says cross-zone and cross-region replication are mutually exclusive per volume (`ref:avd-multiregion-bcdr#anf-zone-or-region`); the product's own page, newer, allows both on one source volume (`ref:anf-replication#zone-and-region-together`). The method follows the product page and the pin drift report watches both.
7. **A deprecated source with no replacement.** The Cloud Adoption Framework article (`ref:caf-avd-bcdr`) goes on 2026-10-30. Three of its claims have no living Learn source: that the AVD service has no financially backed SLA (`ref:caf-avd-bcdr#no-financial-sla`), that the availability option is fixed at creation (`ref:caf-avd-bcdr#availability-option-at-create`), and that pooled host VM state isn't worth backing up (`ref:caf-avd-bcdr#hosts-stateless-no-vm-backup`, partly carried by `ref:avd-multiregion-bcdr#pool-types-state`). Until a living page says them, they stand on the pinned read and Microsoft's own PDF of the article; when the drift report shows the page gone, each becomes a gap line here, not a deleted row.
8. **Targets are per estate for now.** C19 has one answer per estate, so the intake asks for the strictest workload's targets and the critical-pools row says which pools they bind. Per-pool targets need a pool-keyed intake, which C19 doesn't have.

**Draft checks.** Each fits method.json's rule grammar (one subject, one `where`, one `expect`, `onFail` warn) and cites facts the register lists as `specified` (2026-10-21); a check enters method.json in the same pull request that builds its facts in avd-current-state, because a check may only cite built facts.

| Check | Claims | Facts | Rule |
|---|---|---|---|
| `asm-hosts-zone-spread` | `ref:review-checklists-avd#A01.04`, `ref:avd-multiregion-bcdr#spread-and-overprovision` | `c11.hostPool.sessionHosts.total`, `c11.hostPool.sessionHosts.zones` | each host pool where `sessionHosts/total` min 2, expect `sessionHosts/zones` min 2. A pool in a region without zones warns; the reviewer accepts it with that reason (C23) |
| `asm-pooled-hosts-not-backed-up` | `ref:review-checklists-avd#A01.05`, `ref:avd-multiregion-bcdr#pool-types-state` | `c11.hostPool.type`, `c11.hostPool.sessionHosts.backupProtected` | each host pool where `type` eq Pooled, expect `sessionHosts/backupProtected` max 0 (a cost with no recovery value) |
| `asm-personal-hosts-replicated` | `ref:review-checklists-avd#A01.06`, `ref:avd-multiregion-bcdr#personal-site-recovery` | `c11.hostPool.type`, `c11.hostPool.sessionHosts.notReplicated` | each host pool where `type` eq Personal, expect `sessionHosts/notReplicated` max 0. A same-region VM backup doesn't count: it doesn't survive the region (`ref:reliability-virtual-machines#backup-not-availability`) |
| `asm-image-replicated` | `ref:review-checklists-avd#A02.01`, `ref:compute-gallery#not-global` | `c11.hostPool.imageSource`, `c11.hostPool.imageRegions` | each host pool where `imageSource` eq gallery, expect `imageRegions` count min 2. A marketplace image is available in every region and isn't judged |
| `asm-profile-backup-ran` | `ref:review-checklists-avd#A03.02`, `ref:files-backup-portal#keys-or-private` | `c11.storage.kind`, `c11.storage.lastBackupJob` | each storage account where `kind` eq FileStorage, expect `lastBackupJob` eq succeeded |
| `asm-profile-backup-offsite` | `ref:review-checklists-avd#A03.04`, `ref:azure-files-backup#vaulted-survives-source-loss` | `c11.storage.kind`, `c11.storage.backupTier` | each storage account where `kind` eq FileStorage, expect `backupTier` eq vaulted |

The existing `asm-files-zone-redundant` stays the check for share redundancy (`profile.resilience`). The FileStorage filter is the same proxy for "a profile account" that check uses.

**Needs more than one rule can say.** The grammar can't compare a host pool with an intake answer, so three judgments stay with the reviewer until it can: that the image's regions include the recovery region (`asm-image-replicated` only proves two regions), that a snapshot-only backup is acceptable because `intake.profileData` is `settings-only`, and that a pool's recovery model matches `intake.recoveryTime`. Growing the grammar is a C20 change, made here first.

**Proposed intake answers.** Each is an enum, so C19 keeps its rule of no names, addresses or free text; they are `specified` in the register and join `contracts/schemas/intake.schema.json` as optional fields when a reader is built (`gap:intake`).

| Fact | Question | Answers |
|---|---|---|
| `intake.recoveryTime` | After an outage, deletion or bad change, how long can users of the most critical workload be without their desktops? | `under-1h`, `1h-to-8h`, `8h-to-24h`, `over-24h`, `undecided` |
| `intake.recoveryPoint` | For the same workload, how much recent profile and app data may be lost? | `minutes`, `under-24h`, `over-24h`, `undecided` |
| `intake.regionRecovery` | Must the estate come back after a whole region is lost? | `required`, `not-required`, `undecided` |
| `intake.recoveryDependencies` | Are identity, DNS, network paths and line-of-business apps available in the recovery region? | `all`, `some`, `none`, `unknown` |
| `intake.profileData` | What do the profile containers hold? | `settings-only` (user data in OneDrive or SharePoint), `user-data`, `unknown` |

**Which repo does what.**

| Repo | Part |
|---|---|
| avd-assess | This map, the method, the draft checks, the intake questions |
| avd-current-state | Collects the specified facts read-only and runs the checks from a pinned copy |
| avd-landing-zone | Builds zones and same-tenant recovery (rebuild, restore, warm standby), its status check, configuration snapshot and recovery tests, each test a run record |
| avd-second-brain, avd-swarm | Read the outcomes and run records; never a dependency of the two above |
