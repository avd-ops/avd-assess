# Gap: what a Power Platform day-2 automation assessment can judge, and from where

**Searched (2026-10-27):** Power Platform data loss prevention policies (`ref:power-platform-dlp`), Power Platform Virtual Network support (`ref:power-platform-vnet`), the Cloud Adoption Framework and Well-Architected operational excellence guidance (`ref:caf-avd-platform-automation`), the family knowledge bases and the web. **Not found:** an open assessment method for Power Platform environments, DLP connector classifications, `Microsoft.PowerPlatform/enterprisePolicies` Virtual Network injection and Power Automate day-2 approval workflows operating an AVD estate.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Azure Resource Graph / ARM (`resource-graph`) | `Microsoft.PowerPlatform/enterprisePolicies` resources (`c11.powerPlatform.enterprisePoliciesCount`) and virtual network subnets delegated to `Microsoft.PowerPlatform/enterprisePolicies` (`c11.powerPlatform.vnetInjectedSubnets`) | Azure `Reader` |
| Power Platform BAP REST (`bap-rest`) | Non-default dedicated environments (`c11.powerPlatform.dedicatedEnvironments`), DLP policies covering the AVD environment (`c11.powerPlatform.dlpPoliciesCoveringAvdEnv`), and the default connector group classification (`c11.powerPlatform.dlpDefaultGroupClassification`) | Power Platform Administrator or System Reader read-only token |
| Dataverse Web API (`dataverse-rest`) | Deployed AVD day-2 solutions (`c11.powerPlatform.avdDay2SolutionsDeployed`) and cloud flow counts by state (`c11.powerPlatform.avdDay2FlowsActive`) | Environment Maker / System Customizer / System Reader read access |
| Operator | Whether the estate uses Power Platform for AVD day-2 operations (`intake.powerPlatformPlaneScope`) | Intake (contract C19) |

Anything none of these shows is `unknown` (or `not-applicable` when `intake.powerPlatformPlaneScope` is `not-used`), never guessed.

## Plane applicability and graceful degradation

Power Platform day-2 automation (`avd-power-platform`) is an optional operational tier in the five-plane architecture (`avd-ops` decision 0009):

1. When `intake.powerPlatformPlaneScope` is `not-used`, all `power-platform` checks evaluate to `not-applicable` (`gap:scoring`).
2. When `intake.powerPlatformPlaneScope` is `in-scope` (or omitted) and `c11.powerPlatform.dedicatedEnvironments` is `0`, `asm-power-platform-dlp-coverage` evaluates to `not-applicable` rather than failing an estate that has not provisioned a Power Platform environment.
3. When the BAP or Dataverse API is unreachable or unconsented, `planesCollected["power-platform"]` records `skipped` or `unconsented` with reason `bap-unavailable` or `insufficient-scope`, while the Azure-side `Microsoft.PowerPlatform/enterprisePolicies` and subnet delegation facts still come from Azure Resource Graph.
