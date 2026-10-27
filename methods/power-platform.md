# Power Platform and low-code governance method

How to judge the Power Platform control plane (`power-platform`) when makers, Power Automate Desktop flows, or line-of-business apps run on Azure Virtual Desktop session hosts or reach data inside the AVD virtual network (`gap:power-platform-scope`).

## Method

1. **Ask whether the estate uses Power Platform in or alongside AVD** (`intake.powerPlatformPlaneScope`: `"used"` or `"not-used"`) before scoring Power Platform checks (`gap:intake`, `gap:power-platform-scope`).
2. **Inventory non-default Power Platform environments and Managed Environments** from the Business Application Platform (BAP) read-only API so every sandbox and production environment used with AVD is visible (`ref:power-platform-dlp#environment-coverage`, `gap:power-platform-scope`).
3. **Check Data Loss Prevention (DLP) policy coverage across every non-default environment:** require at least one tenant-wide or environment-scoped DLP policy classifying connectors into Business, Non-Business, and Blocked groups (`ref:power-platform-dlp#connector-groups`, `ref:power-platform-dlp#environment-coverage`, `gap:power-platform-scope`).
4. **Check default connector group classification** so uncategorized connectors land in `Blocked` or `Confidential` rather than unrestricted sharing (`ref:power-platform-dlp#default-group-blocked`, `gap:power-platform-scope`).
5. **Check Power Platform VNet integration (Enterprise Policies)** when Power Platform environments connect to private resources on the AVD spoke or hub virtual network, verifying `Microsoft.PowerPlatform/enterprisePolicies` and subnet delegation to `Microsoft.PowerPlatform/enterprisePolicies` (`ref:power-platform-vnet#enterprise-policy-subnet`, `ref:power-platform-vnet#delegated-subnet-egress`, `gap:power-platform-scope`).
6. **Check Power Automate Desktop machine-group governance** when unattended or attended RPA flows run on AVD session hosts (`gap:power-platform-scope`).
7. **Score Power Platform checks as not applicable** when `intake.powerPlatformPlaneScope` is `"not-used"` (the default for AVD estates that do not use Power Platform), so non-Power-Platform estates suffer no score or coverage penalty (`gap:power-platform-scope`, `gap:scoring`).

## Not yet known

- Whether read-only BAP API calls with a service principal without Power Platform Administrator or System Administrator role return full DLP policy assignments in every sovereign and commercial cloud (`gap:power-platform-scope`).
