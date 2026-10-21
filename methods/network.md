# Network method

How to judge an estate's network, Azure side and client side, against what Microsoft publishes for AVD. It is the [assessment](assessment.md) method applied to the network, and it is a map: each step points at the pinned source, the fact that measures it and the check that judges it, and says so plainly where none exists. Nothing here restates Microsoft's lists; read them at the pin. avd-current-state implements it; findings go in the same report (contract C21). The rows are `network.*` in [dimensions.yaml](../dimensions.yaml).

How RDP itself behaves on the network (reverse connect, Shortpath, STUN and TURN, multipath, QoS) belongs to the remote protocol pillar; this method judges whether the network lets it happen.

## Azure side

1. **Topology first.** Standalone spoke, peered to a hub, or on a Virtual WAN hub, and whether hosts need anything on-premises (`ref:arch-hub-spoke#hub-shared-services`, `ref:virtual-wan#managed-transit`, `ref:review-checklists-avd#F01.01`, `ref:review-checklists-avd#F01.02`, `ref:review-checklists-avd#F01.03`). Entra-joined hosts need no private path for identity (`ref:caf-avd-network#entra-joined-no-private`). Rows `network.mode`, `network.hybrid`.
2. **Address space with headroom** for hosts and private endpoints; no source gives a sizing rule, so report free addresses against the plan (`ref:avd-private-link#address-headroom`, `gap:network-scope`). Row `network.addressing`.
3. **Every private name resolves privately from the hosts**: a linked zone or forwarding for Files, Key Vault and AVD, and a resolver where on-premises must resolve them (`ref:private-endpoint-dns#zone-per-service`, `ref:dns-private-resolver#hybrid-resolution`, `ref:avd-private-link-setup#dns-zones`). Row `network.dns`.
4. **An explicit outbound method** on every host subnet (`ref:default-outbound#explicit-outbound`, `ref:default-outbound#private-subnets-default`, `ref:nat-gateway#subnet-egress`, `ref:review-checklists-avd#F01.04`). Row `network.egress`.
5. **The required endpoints reachable from a host**, by service and FQDN tags, and nothing aimed at the platform addresses (`ref:avd-required-fqdn#host-list`, `ref:avd-required-fqdn#service-and-fqdn-tags`, `ref:avd-fabric-ips#no-deny-no-route`, `ref:firewall-avd#fqdn-tag-rules`, `ref:review-checklists-avd#F01.05`, `ref:review-checklists-avd#F01.07`). Only a read on a host proves reachability; a probe from anywhere else is `unknown` (`ref:avd-url-check-tool#run-on-host`, `obs:endpoint-probe-off-host`). Row `network.required-endpoints`.
6. **What may be inspected or tunnelled.** Forced tunnelling is supported when the requirements hold (`ref:caf-avd-network#forced-tunnel-supported`); no SSL termination or authenticating proxy for AVD (`ref:avd-proxy#no-ssl-termination`, `ref:avd-proxy#no-auth-proxy`, `ref:review-checklists-avd#F01.08`); the platform addresses are never proxied or tunnelled (`ref:avd-fabric-ips#never-proxy-or-tunnel`); a firewall default route needs the AVD service tag routed around it (`ref:firewall-avd#bypass-route-for-scale-in`, `obs:hub-route-without-avd-bypass`). Firewall rules are intake. Row `network.inspection`.
7. **AVD Private Link, Azure side.** Which of the four layouts, chosen on purpose, with the public access settings that match (`ref:avd-private-link#three-sub-resources`, `ref:avd-private-link#four-scenarios`, `ref:avd-private-link#public-access-settings`); the global endpoint on its own workspace and zone (`ref:avd-private-link#global-workspace`, `ref:avd-private-link#separate-global-zone`); the provider re-registered (`ref:avd-private-link-setup#re-register-provider`); the connection endpoint's full TCP range open wherever ports to it are restricted (`ref:avd-private-link#full-port-range`, `obs:private-endpoint-nsg-narrower-than-avd-needs`); UDP only with the opt-in (`ref:avd-private-link#udp-opt-in`); agents restarted after a change (`ref:avd-private-link#agent-restart`). Profile storage and Key Vault behind private endpoints (`ref:review-checklists-avd#F01.10`). Row `network.private-access`.
8. **Operators come in another way**: Bastion or a jumpbox, never a public RDP port (`ref:bastion#admin-path`, `gap:network-scope`). Row `network.admin-access`.
9. **Watch it**: flow logs with traffic analytics, and path tests where hosts depend on a hub or on-premises (`ref:vnet-flow-logs#flow-logging`, `ref:connection-monitor#path-tests`, `ref:caf-avd-network#nsg-on-all-subnets`). Row `network.monitoring`.
10. **Recovery region**: the same network capabilities, or at least identity and DNS (`ref:caf-avd-network#dr-network`); the recovery model itself is in `reliability.dr-model`.

## Client side

1. **Every user network allows the client endpoint list** and reaches the region within the round-trip target, measured from that network (`ref:avd-required-fqdn#client-list`, `ref:avd-prerequisites#rtt-under-150`, `obs:region-latency-from-the-user`). Row `network.client`.
2. **Proxies on the user network** are bypassed for AVD or sit in the same geography; client proxy support differs by platform (`ref:avd-proxy#bypass-proxies`, `ref:avd-proxy#same-geography`, `ref:avd-proxy#client-proxy-support`).
3. **AVD Private Link, client side.** Where users connect privately, each user network resolves the discovery, feed and gateway names to the endpoints over VPN or ExpressRoute; discovery stays public by design; no mixed public and private feeds on a network without internet; clients at the supported versions (`ref:avd-private-link#client-dns-sequence`, `ref:avd-private-link#global-workspace`, `ref:avd-private-link#mixed-feed-limit`, `ref:avd-private-link-setup#client-versions`, `ref:dns-private-resolver#hybrid-resolution`, `gap:client-network`). Row `network.client-private-link`.
4. **Bandwidth** per user and in total, estimated first and then measured (`ref:rdp-bandwidth#per-scenario-estimates`, `ref:review-checklists-avd#F01.09`). Row `network.bandwidth`.
5. **Device VPN and security agents** (SSE, ZTNA, VPN client categories): an extension row, `network.client-agents`, filled later; categories only.
6. **Prove it with users**: a proof of concept from the real networks before the move (`ref:review-checklists-avd#C02.04`).

Client-side steps are intake or a reviewer's test on the user's network (`gap:client-network`); nothing reads them automatically.

## Extension points

- **AVD on Azure Local** (`network.azure-local`): a host pool is all Azure or all Azure Local (`ref:avd-azure-local#no-mixed-pools`); no method yet.
- **Device agents** (`network.client-agents`), above.

## Where the network lives in the family

The slices are the same as for security: avd-assess holds the map and this method, avd-current-state collects the facts and runs the checks from a pinned copy, avd-landing-zone builds a design that should pass them, and the layers above explain and change it. The table, the draft checks and what each needs are in `gap:network-scope`.

## Not yet known

- The draft checks in `gap:network-scope` need facts avd-current-state doesn't collect yet; each enters method.json with its facts.
- No host-side read exists for required endpoints, private name resolution or proxy and inspection on a host.
- Whether the landing zone's private endpoint NSG and its hub route without an AVD bypass matter in practice (`obs:private-endpoint-nsg-narrower-than-avd-needs`, `obs:hub-route-without-avd-bypass`).
