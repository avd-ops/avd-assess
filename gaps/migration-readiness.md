# Gap: migration readiness and profile transition paths

**Searched (2026-10-27):** Microsoft Learn (Entra Kerberos for Azure Files, FSLogix storage options, Cloud Adoption Framework AVD migration scenario, OneDrive VDI support), the AVD review checklist, and the Well-Architected Framework reliability checklist. **Not found:** a single deterministic decision table that joins Active Directory to Entra ID readiness, brownfield pool disposition (`in-place-upgrade` versus `side-by-side-migrate`), and the selection rule across the three user profile transition paths.

**What we write.** Three deterministic classifications for brownfield AVD, Remote Desktop Services (RDS), and third-party VDI source pools before wave planning.

## 1. AD-to-Entra readiness gate

Each user group or source pool is classified into one of three readiness outcomes from its discovered application dependencies, user identity sync state, and profile container format:

| Outcome | When it applies | Citations |
|---|---|---|
| `Ready (EntraOnly)` | Session hosts and user profiles can operate on Entra ID join with Entra Kerberos (`AADKERB`) or OneDrive Known Folder Move (KFM) without remediation. | `ref:avd-security-guide#trust-boundary`, `ref:files-entra-kerberos#cloud-only-and-hybrid`, `ref:files-entra-kerberos#clients-entra-joined` |
| `Remediate First` | Pool can move to `EntraOnly` after converting host join mode, transforming legacy profile containers, or retiring blocked applications. | `ref:caf-avd-deploy#app-remediation-blocks`, `ref:avd-fslogix-storage#tier-by-workload` |
| `Blocked (Requires AD DS)` | Pool requires Active Directory Domain Services join due to explicit identity constraints or unsynced SIDs on existing FSLogix containers without KFM. | `ref:files-entra-kerberos#hybrid-acl-line-of-sight`, `ref:caf-avd-assess#application-questions`, `gap:intake` |

## 2. Brownfield pool disposition

| Disposition | When it applies | Action | Citations |
|---|---|---|
| `in-place-upgrade` | Source pool is already on AVD, matches the target `EntraOnly` identity lane, sits in an allowed target region, and has a compatible landing-zone structure. | Update landing-zone parameters and perform blue/green session host rotation. | `ref:waf-reliability-checklist#RE:05`, `gap:migration-readiness` |
| `side-by-side-migrate` | Source pool is on RDS, a third-party VDI platform, AD-joined legacy AVD, or outside target regions. | Deploy target subscription stamp and transition users and profiles in waves. | `ref:caf-avd-deploy#persona-iterations`, `gap:migration-readiness` |

## 3. Three profile transition paths

Per persona and wave (`avd-wave-plan/v1`, Contract C29), one of three profile transition paths is selected:

| Path ID | Title | When it applies | Citations |
|---|---|---|---|
| `path-1-fresh-kfm` | Fresh FSLogix profile + OneDrive Known Folder Move (KFM) | OneDrive KFM is active or local profile state is under 1 GiB. | `ref:onedrive-vdi#silent-config-and-kfm`, `ref:onedrive-vdi#files-on-demand-vdi`, `gap:migration-readiness` |
| `path-2-azcopy-sid-guard` | AzCopy pre-stage + cutover delta sync with SID/ACL guard | Source profiles are FSLogix VHD(X) and hybrid Entra ID users retain matching `onPremisesSecurityIdentifier` for `AADKERB`. | `ref:files-entra-kerberos#cloud-only-and-hybrid`, `ref:files-entra-kerberos#hybrid-acl-line-of-sight`, `gap:migration-readiness` |
| `path-3-profile-transform` | Profile transformation bridge | Source profiles are RDS User Profile Disks (UPD), roaming profiles, third-party VDI containers, or cross a SID boundary. | `ref:avd-fslogix-storage#azure-files-default`, `ref:avd-fslogix-storage#tier-by-workload`, `gap:migration-readiness` |
