# Gap: what a Microsoft 365 VDI productivity assessment can judge, and from where

**Searched (2026-10-27):** OneDrive VDI support (`ref:onedrive-vdi`), Microsoft 365 Apps on a custom VHD image (`ref:avd-office-image`), Microsoft Teams on AVD (`ref:teams-on-avd`), Multimedia Redirection (`ref:avd-multimedia-redirection`), the AVD review checklist (B01.09, B01.10, B03.02 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** an open method that separates what a read-only collector can verify about OneDrive Known Folder Move, Files On-Demand, Microsoft 365 Apps Shared Computer Activation, Outlook Cached Exchange Mode, Teams VDI media optimization and Multimedia Redirection from Microsoft Graph and Teams policies against what lives only inside a session host's registry or image.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Intune Settings Catalog and administrative templates (`graph-rest`) | Whether an assigned policy configures OneDrive SilentAccountConfig, Known Folder Move (`KFMOptInWithWizard` / `KFMSilentOptIn`), Files On-Demand, Microsoft 365 Apps `SharedComputerLicensing`, Outlook Cached Exchange Mode sync window, and AVD Multimedia Redirection (`c11.m365.*`) | `DeviceManagementConfiguration.Read.All` |
| Microsoft Teams VDI policy (`teams-ps` or baseline) | Whether `CsTeamsMeetingPolicy` or the VDI baseline enables media optimization (`SlimCoreAndWebRtc`) for AVD users (`c11.m365.teamsMediaOptimizationState`) | Teams Reader or baseline manifest |
| Entra subscribed SKUs (`graph-rest`) | Whether the tenant carries unassigned seats across M365 E3/E5/F3/Business Premium or Windows E3/E5 SKUs (`c11.entra.skuAvdEligibleAvailable`) | `Organization.Read.All` |
| Session host / image | Whether OneDrive is installed per machine (`/allusers`), whether the Teams meeting add-in and SlimCore plugin are present in the image, and whether a local registry key overrides policy | A host-side or image-build read (`avd-azure`) |
| Operator | Whether the estate uses Microsoft 365 on AVD, manages M365 policies in a separate tenant-wide plane, or does not use M365 on AVD (`intake.m365PlaneScope`) | Intake (contract C19) |

Anything none of these shows is `unknown` (or `not-applicable` when `intake.m365PlaneScope` is `not-used`), never guessed.

## Plane applicability

Not every AVD estate runs Microsoft 365 Apps, OneDrive or Teams inside the session (for example, single-purpose line-of-business RemoteApp pools or developer desktops with no Office suite). When `intake.m365PlaneScope` is `not-used`, the `m365` plane's checks evaluate to `not-applicable` and are excluded from both the pillar denominator and the `m365` plane denominator (`gap:scoring`).
