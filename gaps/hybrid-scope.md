# Gap: what a hybrid and Azure Local assessment can judge, and where Azure Arc helps on-premises

**Searched (2026-11-09):** the AVD Hybrid overview and deployment guides (`ref:avd-hybrid-overview`, `ref:avd-hybrid-deploy`), the AVD on Azure Local overview and workload architecture guide (`ref:avd-azure-local`, `ref:avd-azure-local-workload`), the Azure Arc-enabled servers overview and Run command documentation (`ref:arc-servers-overview`, `ref:arc-servers-run-command`), the AVD review checklist (`ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** any item in the AVD review checklist for AVD Hybrid or AVD on Azure Local, an open decision rule comparing AVD Hybrid against Azure Local when workloads must remain on-premises, or a method stating which parts of an on-premises desktop estate Azure Arc can evidence and operate versus where agentless discovery or broker exports are still required.

## Two on-premises host paths, with different boundaries

When residency, latency to local hardware or legacy back-end dependencies keep session hosts on-premises, Microsoft offers two paths that share the Azure control plane (`ref:avd-hybrid-overview#arc-enabled-hosts`, `ref:avd-azure-local#no-mixed-pools`):

| Dimension | AVD Hybrid (Arc-enabled servers) | AVD on Azure Local |
|---|---|---|
| Underlying host | Existing on-premises hypervisor virtual machines or dedicated headless physical servers (`ref:avd-hybrid-overview#arc-enabled-hosts`) | Registered Azure Local 23H2 or later hyperconverged cluster (`ref:avd-azure-local#multisession-and-shortpath`) |
| Windows 10/11 Enterprise multi-session | Not supported (`ref:avd-hybrid-overview#no-client-multisession`) | Supported (`ref:avd-azure-local#multisession-and-shortpath`) |
| Supported OS | Windows Server 2016-2025 (VM or headless physical) and single-session Windows 10/11 Enterprise (VM or dedicated rack-mounted headless host) (`ref:avd-hybrid-overview#supported-os`) | Windows 10/11 Enterprise multi-session or single-session, Windows Server 2019-2025 (`ref:avd-azure-local#multisession-and-shortpath`) |
| Directory join | Client OS: Entra, AD DS or hybrid join; Windows Server: AD DS or hybrid join only (`ref:avd-hybrid-deploy#join-types-by-os`) | AD DS or hybrid join in the portal; native Entra join via PowerShell or templates (`ref:avd-azure-local#entra-join-outside-portal`) |
| Native AVD autoscale, Start VM on Connect, power management and session host configuration | Not supported; the operator manages provisioning and power (`ref:avd-hybrid-overview#no-platform-lifecycle`) | Managed through Azure and Azure Local (`ref:avd-azure-local#multisession-and-shortpath`) |
| Host registration | Connected Machine agent, host pool managed identity with `Reader` on the Arc resource group, and `Microsoft.AzureVirtualDesktop.CloudDeviceExtension` (`ref:avd-hybrid-deploy#hostpool-identity-reader`, `ref:avd-hybrid-deploy#cloud-device-extension`) | Connected Machine agent installed automatically during portal deployment (`ref:avd-azure-local#connected-machine-agent`) |
| Licensing and fees | OS entitlement plus AVD Hybrid user license (`ref:avd-hybrid-overview#hybrid-licensing`) | User access rights, Azure Local service fee, and per-active-vCPU fee (`ref:avd-azure-local#three-part-pricing`) |

## What Azure Arc gives an on-premises assessment and operation - and what it does not

1. **AVD Hybrid session host registration:** Required for every AVD Hybrid session host (`ref:avd-hybrid-overview#arc-enabled-hosts`, `ref:avd-hybrid-deploy#cloud-device-extension`) and for Azure Local session hosts (`ref:avd-azure-local#connected-machine-agent`).
2. **Resource Graph inventory when Arc is already deployed:** Connected machines appear as `Microsoft.HybridCompute/machines` resources in Azure Resource Graph (`ref:arc-servers-overview#azure-resource-projection`), giving OS, SKU, core and memory counts, domain status and tags with Reader access at no extra cost. Where Arc is not already deployed on an on-premises source estate, rolling out agents solely for a read-only assessment is unnecessary overhead; an agentless discovery export is preferred.
3. **Outbound-only remote script execution (`Run command`):** Built into the Connected Machine agent (`ref:arc-servers-run-command#agent-script-execution`, `ref:arc-servers-run-command#free-control-plane`), allowing an operator to run read-only inventory collectors or approved host diagnostics from Azure CLI, PowerShell or REST over outbound HTTPS without opening inbound RDP, WinRM or VPN paths.
4. **Monitoring and change tracking:** Arc-enabled servers accept the Azure Monitor Agent and data collection rules (`ref:arc-servers-overview#ama-and-extensions`), feeding the same Log Analytics tables as Azure session hosts (`gap:monitoring-scope`).
5. **What Arc cannot see:** Arc inventories the machine OS, not on-premises desktop brokers, session collections, published applications or profile shares. Assessing an existing on-premises RDS or third-party VDI farm still requires a broker and profile inventory alongside machine facts.

## Proposed facts for the collector

All proposed facts emit counts or booleans per host pool so no machine name, domain or IP address leaves the collector (`contracts/README.md`):

| Proposed fact | What it measures | Source |
|---|---|---|
| `proposed:c11.hostPool.sessionHosts.arcConnected` | Session hosts in the pool backed by an Arc-enabled server (`Microsoft.HybridCompute/machines`) | AVD session host resource link and Resource Graph |
| `proposed:c11.hostPool.sessionHosts.arcAgentDisconnected` | Arc-backed session hosts whose Connected Machine agent status is not `Connected` | Resource Graph `HybridCompute/machines` |
| `proposed:c11.hostPool.sessionHosts.cloudDeviceExtensionFailed` | Arc-backed session hosts where `Microsoft.AzureVirtualDesktop.CloudDeviceExtension` is not `Succeeded` (`ref:avd-hybrid-deploy#cloud-device-extension`) | Resource Graph `HybridCompute/machines/extensions` |
| `proposed:c11.hostPool.arcResourceGroupReaderAssigned` | Whether the host pool has a managed identity with `Reader` on the resource group holding its Arc-enabled servers (`ref:avd-hybrid-deploy#hostpool-identity-reader`) | Host pool identity and role assignments |

## Draft checks

None is in `method.json` until its facts are built in `avd-current-state`:

| Check | Applies when | pass | warn | gap | unknown |
|---|---|---|---|---|---|
| `asm-hybrid-no-mixed-pool` | Pool has any Arc or Azure Local host | All hosts in the pool share one placement model (`ref:avd-azure-local#no-mixed-pools`) | | Azure and Azure Local hosts mixed in one pool | Placement not read |
| `asm-hybrid-hostpool-identity-reader` | Pool holds Arc-enabled session hosts | Host pool managed identity holds `Reader` on every Arc server resource group (`ref:avd-hybrid-deploy#hostpool-identity-reader`) | | Missing managed identity or missing `Reader` role assignment | Role assignments not read |
| `asm-hybrid-arc-extension-healthy` | Pool holds Arc-enabled session hosts | Every Arc host is `Connected` with `CloudDeviceExtension` in `Succeeded` (`ref:avd-hybrid-deploy#cloud-device-extension`) | Agent disconnected on deallocated or maintenance hosts | Extension failed or missing on active hosts | Arc resource group not read |
| `asm-hybrid-no-native-autoscale` | Pool holds AVD Hybrid session hosts | No Azure autoscale plan or Start VM on Connect enabled on an AVD Hybrid pool (`ref:avd-hybrid-overview#no-platform-lifecycle`) | Autoscale or Start VM on Connect enabled where the platform ignores it | No external power or provisioning runbook recorded when scaling is required | Intake not answered |
