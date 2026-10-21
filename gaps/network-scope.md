# Gap: what a network assessment covers, what it can measure, and which repo does what

**Searched (2026-10-21):** the review checklist's networking items (`ref:review-checklists-avd#F01.01` to `ref:review-checklists-avd#F01.11`), the Cloud Adoption Framework's AVD network article (`ref:caf-avd-network#hybrid-scenarios`, deprecated), the Architecture Center's AVD design guide and hub-spoke pages (`ref:arch-avd-design-guide#platform-connectivity`, `ref:arch-hub-spoke#hub-shared-services`), the AVD Private Link, required endpoint, platform address and proxy pages (`ref:avd-private-link`, `ref:avd-required-fqdn`, `ref:avd-fabric-ips`, `ref:avd-proxy`), and the Azure Firewall AVD guide (`ref:firewall-avd`). **Not found:** a checklist item for AVD Private Link, for DNS of private endpoints, for the operator access path, or for what must never be tunneled; a rule for sizing a host subnet from a host count; and any method that says which network requirements an assessment can judge from read-only data. Each source says what to configure; none says how to tell from outside whether it was.

**What we write.** This page is the map's network method; the sources stay the authority and nothing here restates them.

1. **Two halves.** The Azure side is everything in the customer's subscriptions that hosts and endpoints sit on. The client side is every network a user connects from. AVD on Azure Local and any third network are named extension points (`network.azure-local`, `network.client-agents` in [dimensions.yaml](../dimensions.yaml)) with no method yet.
2. **Four kinds of evidence, as for security.** Control plane with Reader (virtual networks, subnets, routes, NSG rules, NAT gateways, private endpoints and their DNS zone groups, zone links, host pool and workspace access settings, flow logs). A read on a session host (the Agent URL Tool's result, name resolution of each private endpoint, proxy settings, the certificate chain seen for the AVD service), which needs a write permission to run, so it is a preflight step the operator chooses. The operator's answer (hub firewall rules, inspection, user networks, client VPN and agents, hybrid links). Insights for what users experienced (round trip, transport). Anything else is `unknown`.
3. **An off-host probe is `unknown`, never `pass`.** Reachability tested from Cloud Shell or the operator's machine says nothing about the host subnet (`obs:endpoint-probe-off-host`, and the same lesson for latency in `obs:region-latency-from-the-user`).
4. **No subnet sizing number.** Without a published hosts-to-prefix rule, the method checks only that a subnet has free addresses for the hosts the plan adds plus the endpoint headroom the Private Link page asks for (`ref:avd-private-link#address-headroom`), and reports the free count.
5. **Operator access is a separate path.** Users reach hosts only through AVD; operators through Bastion or a jumpbox (`ref:bastion#admin-path`); a public RDP port on a host is a finding whatever its NSG says.

**Draft checks.** Each needs facts the register lists as `specified` (a path, not yet collected); a check enters method.json in the same pull request that builds its facts in avd-current-state, because a check may only cite built facts.

| Check | Claims | Facts | Outcomes |
|---|---|---|---|
| `asm-net-explicit-egress` | `ref:default-outbound#explicit-outbound`, `ref:review-checklists-avd#F01.04` | `c11.network.hostSubnets.explicitEgress`, `c11.network.hostSubnets.defaultOutboundAccess` | pass: NAT Gateway, a default route to an appliance or load balancer outbound rules, and default outbound off; warn: default outbound only, or a default route to nothing; unknown: subnet not read |
| `asm-net-fabric-not-blocked` | `ref:avd-fabric-ips#no-deny-no-route`, `ref:review-checklists-avd#F01.07` | `c11.network.hostSubnets.fabricDenyRules` | pass: no NSG deny or route aimed at the platform addresses or their service tags; warn otherwise |
| `asm-net-avd-outbound-allowed` | `ref:avd-required-fqdn#service-and-fqdn-tags`, `ref:review-checklists-avd#F01.05` | `c11.network.hostSubnets.avdOutboundDenied` | pass: no outbound deny ahead of the AVD, Entra and Monitor service tags on 443; warn: denied; unknown: egress through a firewall, whose rules are intake |
| `asm-net-private-dns-linked` | `ref:private-endpoint-dns#zone-per-service`, `ref:review-checklists-avd#F01.10` | `c11.network.privateEndpointZoneGroups`, `c11.network.privateDnsZoneLinks` | pass: every AVD, Files and Key Vault endpoint in an Azure-DNS network has a zone group and a linked zone; warn: missing; endpoints in custom-DNS networks are not judged (forwarding isn't visible) |
| `asm-net-avd-private-link-layout` | `ref:avd-private-link#four-scenarios`, `ref:avd-private-link#public-access-settings` | `c11.hostPool.publicNetworkAccess`, `c11.network.privateEndpoints` (a count by group ID, built) | pass: a host pool not fully public has a connection endpoint; warn: public access restricted with no endpoint; gap: no Private Link and no recorded reason |
| `asm-net-flow-logs` | `ref:vnet-flow-logs#flow-logging`, `ref:caf-avd-network#nsg-on-all-subnets` | `c11.network.flowLogs` | pass: host subnet or its network has flow logs; warn: none |

Host-side checks, `unknown` until a host read exists: required endpoints reachable from a host (`ref:avd-url-check-tool#run-on-host`), private names resolving to private addresses on a host (`ref:private-endpoint-dns#zone-per-service`), and no authenticating proxy or SSL interception for AVD (`ref:avd-proxy#no-auth-proxy`, `ref:avd-proxy#no-ssl-termination`).

**Which repo does what.**

| Repo | Network slice |
|---|---|
| avd-assess | The map, this method, references, observations and gaps |
| avd-current-state | Collects the Reader facts above and runs the checks from its pinned copy; its validator's network section already reads most of them |
| avd-landing-zone | Builds the default design (standalone spoke with NAT Gateway, or hub-peered through a firewall; Private Link for the host pool connection); its preflight checks the private endpoint DNS |
| avd-second-brain | Why the network is the way it is: accepted departures with their reasons |
| avd-swarm | Approved network changes only |

The remote protocol pillar owns how RDP behaves on the network (transports, Shortpath, multipath, QoS); this pillar owns whether the network lets it.
