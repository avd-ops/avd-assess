# Gap: what an Intune and host management assessment can judge, and from where

**Searched (2026-10-21):** Intune's multi-session and single-session AVD pages (`ref:intune-avd-multisession`, `ref:intune-avd-personal`), AVD's management page (`ref:avd-management`), the settings catalog, Group Policy analytics and MDMWinsOverGP (`ref:intune-settings-catalog`, `ref:intune-group-policy-analytics`, `ref:mdm-wins-over-gp`), compliance and its Graph settings (`ref:intune-compliance`, `ref:graph-device-management-settings`), update rings and Autopatch (`ref:intune-update-rings`, `ref:autopatch-avd`), device actions, reports and the managed device resource (`ref:intune-device-actions`, `ref:intune-reports`, `ref:graph-intune-managed-device`), the AVD review checklist (E01.03, E01.09, D01.03, D01.04, G04.01 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** an open method that says which Intune state an AVD assessment should read, how Intune's devices map to host pools, and which Intune limits make a setting not applicable on multi-session rather than missing. Microsoft documents what Intune supports on AVD hosts; nobody publishes how to judge an estate's use of it.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Control plane | The enrollment request on each Entra joined host (the Entra login extension's MDM ID), the host pool type and the image | Reader |
| Intune, through Graph | Whether each host is managed, its compliance state and last sync, the tenant's no-policy setting and check-in period, configuration and baseline state, device records left after hosts are gone (`ref:graph-intune-managed-device#device-fields`, `ref:graph-device-management-settings#secure-by-default`) | Intune read permissions in Graph (managed devices and configuration), which no family collector has yet |
| Host | Whether MDM or Group Policy wins (`ref:mdm-wins-over-gp#diagnostic-report`), the Group Policy result, FSLogix RoamIdentity | A host-side read, which no family collector does yet |
| Directory | Conditional Access policies that require a compliant device | The identity pillar's directory read |
| Operator | Which channel manages hosts, how hosts are serviced, what client devices must prove | Intake (below) |

Anything none of these shows is `unknown`, never guessed.

## Mapping Intune devices to host pools

Intune knows devices by name and Entra device ID; AVD knows session hosts by name. The collector matches them in memory and emits counts per host pool only, never a name:

1. **Normalize both names:** a session host's name is the part of its resource name after the host pool and before the first dot (the domain suffix goes), and both sides compare without case.
2. **One record per host:** when several Intune records share a host's name, as after a host is rebuilt under the same name, the one that synced last stands for the host and the others count as orphans.
3. **Orphans:** a record whose name follows a pool's host name pattern but has no session host behind it, or a superseded record from rule 2, counts in `c11.hostPool.intuneOrphans` (`ref:intune-avd-multisession#orphaned-records`).
4. **No guessing:** a name that matches two pools, or none, leaves that record out and lowers the pool's coverage.

So `intuneManaged` never exceeds the pool's host count.

## Facts this pillar specifies

All are counts or one boolean, so no device or user name leaves the collector. They are `specified` in the fact register; avd-current-state builds them when it gains an Intune read.

| Fact | Counts | Source |
|---|---|---|
| `c11.hostPool.sessionHosts.intuneEnrollRequested` | Entra joined hosts whose Entra login extension asks for Intune enrollment. Hybrid joined hosts enroll through Group Policy or co-management, which Azure can't see, so they never count here | VM extension settings (Reader) |
| `c11.hostPool.sessionHosts.intuneManaged` | Hosts with an Intune managed device record, matched as above; this is enrollment, not management by policy | Graph managed devices |
| `c11.hostPool.sessionHosts.intuneCompliant`, `intuneNoncompliant` | Hosts by compliance state; the rest (in grace, not evaluated, error) count in neither | Graph managed devices |
| `c11.hostPool.sessionHosts.intuneSyncStale` | Hosts whose last sync is older than the tenant's own compliance check-in period | Graph managed devices and device management settings |
| `c11.hostPool.sessionHosts.intuneConfigErrors` | Hosts with a configuration policy in error or conflict | Intune configuration reports through Graph |
| `c11.hostPool.sessionHosts.intuneBaselineApplied` | Hosts with a security baseline profile applied | Intune baseline state through Graph |
| `c11.hostPool.intuneOrphans` | Device records for the pool's host names with no session host | Graph managed devices, matched as above |
| `c11.intune.noPolicyMeansNoncompliant` | Whether the tenant marks a device with no compliance policy noncompliant | Graph device management settings |

Intake answers, proposed for contract C19 (`gap:intake`): `intake.hostManagement`, `intake.hostServicing`, `intake.clientDevices`.

Building any of these is a contract change here first: the per-pool counts join the session host summary in the C11 schema, and the tenant setting needs a new optional top-level `intune` object, because C11 has no tenant-level section yet (`contracts/README.md`).

## Not applicable is not a gap

Intune doesn't deliver some things to multi-session hosts at all: templates other than certificates and device-tunnel VPN, update rings, Autopatch, user-targeted compliance, Available apps, wipe, retire and remote lock (`ref:intune-avd-multisession#settings-catalog-only`, `ref:intune-avd-multisession#quality-updates-catalog-only`, `ref:autopatch-avd#personal-only`, `ref:intune-avd-multisession#compliance-device-targeted`, `ref:intune-avd-multisession#apps-system-required`, `ref:intune-avd-multisession#remote-actions-unsupported`). Their absence on a multi-session pool is a pass, and their presence is a warn (a policy that reports Not applicable and does nothing). On personal single-session pools the same items apply as on physical desktops (`ref:intune-avd-personal#personal-like-physical`).

## Draft checks

None is in `method.json` yet: each reads a fact that isn't built. Outcomes follow `gap:scoring`; a check whose condition doesn't hold for a pool isn't assessed there, the way `method.json` checks use `where`. "Access depends on compliance" means a Conditional Access policy requires a compliant device: until a directory read sees the policies, the operator's `intake.clientDevices` answer stands in, and with neither the outcome is `unknown`.

| Check | Applies when | pass | warn | gap | unknown |
|---|---|---|---|---|---|
| Hosts enrolled | The operator says Intune, both or co-management manage hosts | Every host has an Intune record | | Hosts without a record | No Graph read, or no `intake.hostManagement` answer |
| Enrolled hosts have policy | Hosts are enrolled | Every enrolled host has a baseline applied and a compliance state (compliant or noncompliant) | Some enrolled hosts lack either, so they are enrolled but run on defaults (`obs:intune-enrolled-policies-left-to-owner`) | | No Graph read |
| No policy means noncompliant | Any host or client is enrolled | The tenant marks a device with no policy noncompliant | It doesn't, and access doesn't depend on compliance | It doesn't, and access depends on compliance (`ref:intune-compliance#set-not-compliant-with-ca`) | No Graph read, or the access answer is unknown |
| Hosts compliant | Hosts are enrolled | Every enrolled host compliant, and the tenant marks no-policy devices noncompliant | Hosts in grace, not evaluated or in error, or compliant only because no policy reached them | Noncompliant hosts where access depends on compliance; elsewhere they are a warn | No Graph read |
| Hosts in sync | Hosts are enrolled | No stale host | Stale hosts | | No Graph read |
| No orphaned records | Any host is enrolled | None | Orphans present (`obs:device-records-outlive-hosts`) | | No Graph read |
| Update path fits the pool | Always | Multi-session: image servicing, or in place with catalog quality settings and no update ring or Autopatch. Personal single-session: image servicing, update rings or Autopatch | An update ring or Autopatch assigned to multi-session hosts, which reports Not applicable and does nothing | No update path at all: neither image servicing nor in-place updates | No `intake.hostServicing` answer and no Graph read |

## Group Policy as the alternative

Group Policy is a supported channel for hybrid joined hosts, and an estate that keeps it isn't marked down for that. What the assessment asks is one owner per setting: the GPOs on the hosts' OU reviewed (`ref:review-checklists-avd#D01.03`), and no setting configured through both channels unless MDMWinsOverGP covers it (`ref:mdm-wins-over-gp#policy-csp-only`). Without a host-side read that stays `unknown`. Moving to Intune starts with Group Policy analytics (`ref:intune-group-policy-analytics#mdm-support-percentage`).

## Split with the other pillars

This pillar owns what Intune delivers to a host or a client device and how it is reported. The governance pillar keeps the Azure side (Azure Policy, tags, audit). The identity pillar owns join types and Conditional Access; this pillar gives it the compliance signal. The images pillar owns the servicing model (`updates.os-servicing`); this pillar says what Intune does under it. The app delivery pillar decides image, app attach or Intune for each app. The security pillar owns what the host baseline contains (`gap:host-baseline-profile`); this pillar delivers it. The endpoint protection pillar owns antivirus and endpoint detection and response, even when Intune's endpoint security profiles carry them. The profiles pillar owns FSLogix, except the one setting Intune depends on (RoamIdentity).
