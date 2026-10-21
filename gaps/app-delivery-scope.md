# Gap: what an app delivery and profile assessment can judge, and from where

**Searched (2026-10-21):** App Attach (`ref:app-attach`, `ref:app-attach-setup`, `ref:app-attach-msix-image`), RemoteApp and application groups (`ref:remoteapp-publish`, `ref:avd-terminology`), multi-session Windows (`ref:windows-multisession-faq`), FSLogix (`ref:fslogix-container-types`, `ref:fslogix-settings-reference`, `ref:fslogix-configuration-examples`, `ref:fslogix-concurrent-connections`, `ref:fslogix-redirections`, `ref:fslogix-prerequisites`, `ref:fslogix-storage-options`, `ref:fslogix-bcdr`), profile storage (`ref:fslogix-azure-files`, `ref:avd-fslogix-storage`, `ref:azure-files-vdi`, `ref:azure-files-smb`, `ref:files-redundancy`, `ref:azure-files-backup`, `ref:anf-fslogix`, `ref:anf-ad-connections`, `ref:anf-continuous-availability`, `ref:anf-replication`), continuity (`ref:avd-disaster-recovery`, `ref:avd-multiregion-bcdr`, `ref:avd-faq`), the review checklist (B02, H01 to H04, A03 and C01.06 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** an open method that says which of these an assessment can read with Reader access, which need a read on a session host, and how to name the ways apps reach a host when more than one is in use. Microsoft documents each mechanism on its own; nobody publishes the map across them.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Control plane | App groups and the preferred type per pool (built); App Attach packages per pool, their registration type and image format (`ref:app-attach-setup#packages-are-resources`; specified facts) | Reader |
| Storage control plane | Account kind, SKU and redundancy, channel encryption and identity (built); SMB Multichannel, Kerberos ticket encryption and backup protection (specified); Azure NetApp Files SMB volumes without Continuous Availability (specified) | Reader, and Backup Reader for backup items |
| Host | Every FSLogix setting (`ref:fslogix-settings-reference`): container locations, size, VHD or VHDX, ODFC, ProfileType, Cloud Cache, redirections.xml; antivirus exclusions; certificate trust for packages; the Store auto-update settings (`ref:app-attach-setup#disable-auto-update`); which share each host mounts | A host-side read, which no family collector does yet; the landing zone's own readiness script reads a few FSLogix values back after deployment (`obs:fslogix-standard-example-adopted`) |
| Logs and measures | Profile size and sign-in IOPS (`c12.group.profile.*`), the app catalog and unknown apps (`c12.group.apps.*`), logon time | The forensic tier |
| Operator | How apps reach hosts, whether apps are known to work on multi-session, what carries the profile | Intake (`intake.appDelivery`, `intake.appCompatibility`, `intake.profileSolution`) |

Anything none of these shows is `unknown`, never guessed.

## How apps reach a host

One estate often uses several ways at once, so `intake.appDelivery` is a list:

| Value | Means | Source |
|---|---|---|
| `image` | Installed in the golden image | `ref:windows-multisession-faq#user-installs-lost` |
| `app-attach` | MSIX, Appx or App-V packages attached at sign-in | `ref:app-attach#package-formats` |
| `host-deployment` | Software distribution to running hosts (Intune or a configuration manager) | the intune pillar |
| `app-layering` | A third-party app layering or streaming product, as a category | its own public documentation, pinned when a row needs it |
| `user-installed` | Users install their own apps; on non-persistent hosts these are lost at sign-out | `ref:windows-multisession-faq#user-installs-lost` |
| `undecided` | Not decided yet | |

The answer doesn't judge anything on its own. It tells the method which rows apply: App Attach rows are `unknown` when `app-attach` isn't in the list, not `gap`.

## Two joins the facts can't make yet

1. **Which share serves which pool.** C11 reads storage accounts and host pools, but nothing links a profile or package share to a pool; the link is the host's `VHDLocations`, `CCDLocations` or a package's image path. Until a host-side read or the package facts are built, H03.03 (one profile store per pool), H03.05 (same region) and B02.01 (packages apart from profiles) are judged from the operator's review, and the C11 storage checks see every account, not just profile ones (`gap:checklist-mapping`).
2. **Which storage is in use.** A check on SMB Multichannel or ZRS can only tell a profile account from any other premium account by the same join.

## Where the checklist and Learn read differently

- **Cloud Cache location.** H04.06 says to consider the VM's temporary drive for the cache; the settings reference says the cache must be on highly available, high-performing storage comparable to SSD or NVMe (`ref:fslogix-settings-reference#cache-on-fast-available-storage`). A temporary disk is fast but lost on deallocation, and a non-persistent pool with Cloud Cache rebuilds the cache at sign-in. The map treats the temporary drive as a choice to record with its reason, not a finding either way, until a run measures sign-in time both ways.
- **The checklist's links have moved.** The B02 FAQ and file share pages, A03.01's profile content page and H02.02's NetApp page all redirect now; the references here name the page each now lands on.

## Split with the other pillars

- **Endpoint protection** owns antivirus and EDR on the host. The exclusions FSLogix and App Attach need are a row here (`profile.av-exclusions`), because the source that sets them is the profile and package guidance; that pillar cites it.
- **Reliability and DR** owns recovery plans for the estate. Profile and package storage redundancy, replication and backup are rows here, because the checklist files them under A03 and they are set on the storage; that pillar cites them.
- **Identity** owns join types and Kerberos for file shares; the Kerberos encryption change for shares (`ref:fslogix-redirections#kerberos-aes-sha1`) is a storage row here, cited from there.
- **Images** owns FSLogix in the image update (B01.07) and the image itself.
