# Gap: what a reliability assessment covers, what it can measure, and which repo does what

**Searched (2026-10-21):** the review checklist's reliability items (`ref:review-checklists-avd#A01.01` to `ref:review-checklists-avd#A03.06`), the AVD disaster recovery concepts and service resilience pages (`ref:avd-bcdr-concepts`, `ref:avd-service-resilience`), the Architecture Center's multiregion guide (`ref:avd-multiregion-bcdr`), the Cloud Adoption Framework's AVD BCDR article (`ref:caf-avd-bcdr`, deprecated), the Well-Architected disaster recovery strategy (`ref:waf-disaster-recovery`), and the Azure Files, Compute Gallery, Site Recovery, Azure NetApp Files and Entra recoverability pages listed in the method. Microsoft has no AVD service reliability guide among its per-service reliability pages. **Not found:** a method that says which recovery requirements an assessment can judge from read-only data, an SLA figure for the AVD service itself, any way to see a recovery test's result in Azure, and a single source that agrees with itself on Azure NetApp Files replication.

**What we write.** This page and [methods/reliability.md](../methods/reliability.md) are the map's reliability method; the sources stay the authority.

1. **Targets are intake.** No platform setting says what the business needs. Without `intake.recoveryTime` and `intake.recoveryPoint` the method reports what exists and judges nothing against a target.
2. **Four kinds of evidence, as for security.** Control plane with Reader (host zones, host pool type and region, storage SKU, backup protected items and Site Recovery replicated items in the RecoveryServicesResources table, `ref:resource-graph-tables#recovery-services-table`, image versions and their target regions). The operator's answer (targets, region loss in scope, dependencies, what profile data matters). A run record (contract C17, use case `recovery`) for a restore or failover test. Nothing measured in Insights proves recovery. Anything else is `unknown`.
3. **A configured backup is not a working one.** A snapshot-tier backup keeps its copies in the account it protects (`ref:files-backup#snapshot-and-vaulted`), and a backup needs the account's key access (`ref:files-backup-support#key-access-needed`). A share with a snapshot policy and key access off is `unknown` until a job is seen to succeed (`obs:files-backup-key-access-off`).
4. **Zones are availability, not recovery** (`ref:avd-multiregion-bcdr#zones-not-dr`). A pool spread across zones passes the zone row and says nothing about the region rows.
5. **A test is the only proof.** A tier's RTO and RPO are estimates until a run times them (`ref:avd-multiregion-bcdr#estimates-to-test`, `ref:waf-disaster-recovery#drills-prove-targets`). Without a run record the recovery-test row is `gap`, never `pass`.
6. **Sources disagree on Azure NetApp Files.** The multiregion guide says cross-zone and cross-region replication are mutually exclusive per volume (`ref:avd-multiregion-bcdr#anf-zone-or-region`); the product's own page, newer, allows both on one source volume (`ref:anf-replication#zone-and-region-together`). The method follows the product page and the pin drift report watches both.

**Draft checks.** Each cites facts the register lists as `specified` (2026-10-21); a check enters method.json in the same pull request that builds its facts in avd-current-state, because a check may only cite built facts.

| Check | Claims | Facts | Outcomes |
|---|---|---|---|
| `asm-hosts-zone-spread` | `ref:review-checklists-avd#A01.04`, `ref:avd-multiregion-bcdr#spread-and-overprovision` | `c11.hostPool.sessionHosts.zones`, `c11.hostPool.sessionHosts.total` | pass: hosts in two or more zones; warn: one zone or regional in a region with zones; unknown: zone not read |
| `asm-pooled-hosts-not-backed-up` | `ref:review-checklists-avd#A01.05`, `ref:caf-avd-bcdr#hosts-stateless-no-vm-backup` | `c11.hostPool.type`, `c11.hostPool.sessionHosts.backupProtected` | pass: a pooled pool with no host backup; warn: pooled hosts backed up (cost with no recovery value); personal pools not judged |
| `asm-personal-hosts-replicated` | `ref:review-checklists-avd#A01.06`, `ref:avd-multiregion-bcdr#personal-site-recovery` | `c11.hostPool.type`, `c11.hostPool.sessionHosts.replicated`, `c11.hostPool.sessionHosts.backupProtected` | pass: every personal host replicated or backed up; warn: some or none are; pooled pools not judged |
| `asm-image-in-recovery-region` | `ref:review-checklists-avd#A02.01`, `ref:compute-gallery#two-galleries-for-dr` | `c11.hostPool.imageRegions` | pass: the image is in two or more regions; warn: one region and `intake.regionRecovery` is `required`; unknown: a marketplace image (available everywhere) or not read |
| `asm-profile-backup-offsite` | `ref:review-checklists-avd#A03.04`, `ref:files-backup#vaulted-survives-source-loss` | `c11.storage.backupTier` | pass: vaulted; warn: snapshot only, or no backup on a profile account when `intake.profileData` is `user-data`; unknown: not read |

The existing `asm-files-zone-redundant` stays the check for share redundancy (`profile.resilience`).

**Proposed intake answers.** Each is an enum, so C19 keeps its rule of no names, addresses or free text; they are `specified` in the register and join `contracts/schemas/intake.schema.json` as optional fields when a reader is built (`gap:intake`).

| Fact | Question | Answers |
|---|---|---|
| `intake.recoveryTime` | How long can users be without their desktops after a region loss? | `under-1h`, `1h-to-8h`, `8h-to-24h`, `over-24h`, `undecided` |
| `intake.recoveryPoint` | How much recent profile and app data may be lost? | `minutes`, `under-24h`, `over-24h`, `undecided` |
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
