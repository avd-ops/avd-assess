# Gap: what a remote protocol and session assessment can judge, and from where

**Searched (2026-10-21):** RDP Shortpath and its configuration (`ref:rdp-shortpath`, `ref:configure-rdp-shortpath`), Multipath (`ref:rdp-multipath`), QoS (`ref:rdp-qos`), bandwidth (`ref:rdp-bandwidth`), graphics (`ref:graphics-encoding`, `ref:avd-gpu-acceleration`), the log table references (`ref:wvdconnections-table`, `ref:wvdconnectionnetworkdata-table`, `ref:wvdconnectiongraphicsdata-table`), Insights (`ref:avd-insights-use-cases`), the review checklist (F01.11, C02.05, B01.10, B03.02 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** an open method that says which of these settings an assessment can read with Reader access, which need a host or a log read, and what share of connections should end up on each transport. Microsoft documents how a transport is chosen; nobody publishes what a healthy mix looks like.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Control plane | Host pool RDP properties (redirection, `ref:rdp-properties#redirection-properties`); the four UDP switches and the Private Link UDP flag, only through a preview API version (`ref:hostpool-api-changelog#udp-switches-preview-only`) | Reader |
| Host | UDP forced off by policy (`ref:configure-rdp-shortpath#select-transport-policy`), the managed-network listener and its port, the client port range, QoS policies, graphics and codec policy, session time limits and lock behavior | A host-side read, which no family collector does yet |
| Logs | The transport each connection used, RTT and bandwidth estimates, frame drops by cause, client type and version | Diagnostic settings sending those categories (`ref:connection-quality-data#diagnostic-tables`) and Log Analytics Reader |
| Client | App and version, platform support for Shortpath and Multipath (`ref:windows-app-platforms#shortpath-by-platform`) | Logs, or the operator |
| Operator | Which networks users connect from (managed, public, both), which clients they run, whether QoS exists on the managed network | Intake |
| Network | Whether host egress is symmetric NAT (Azure Firewall or NAT Gateway), which forces TURN (`ref:rdp-shortpath#symmetric-nat-means-turn`, `obs:symmetric-nat-egress-means-turn`) | The networking pillars' facts (default routes, NAT Gateway) |

Anything none of these shows is `unknown`, never guessed.

## Intent before outcome

No source says what share of connections should use UDP, or how much TURN is too much. So the method judges each connection against the best path the operator's stated networks and the host egress allow. Behind symmetric NAT egress the best public path is TURN, so TURN there is a pass; TURN isn't available in Azure Government at all (`ref:configure-rdp-shortpath#turn-public-cloud-only`).

- **pass:** the connection used the best transport its network allows (UDP on a network where UDP is expected).
- **warn:** it used TURN where a direct path was expected (egress isn't symmetric NAT), or TCP after UDP should have been possible; also a UDP switch turned off with a recorded reason.
- **gap:** UDP turned off on the host pool or the hosts with no recorded reason, or the web client as the only client for users who need Shortpath.
- **unknown:** no logs, or the setting can't be read.

No percentage target is set until real runs give one (`gap:evidence-intake`). When UDP fails, the operator's next step is Microsoft's NAT type test and the Shortpath error codes in the logs (`ref:troubleshoot-rdp-shortpath#nat-type-test`, `ref:troubleshoot-rdp-shortpath#udp-error-codes`); TURN sessions can also drop briefly during relay maintenance (`ref:rdp-shortpath#turn-maintenance-drops`).

## Split with the networking pillars

This pillar states what RDP needs from the network: outbound UDP from the hosts, the TURN range on UDP 3478, the client port range, the listener port for managed networks, no inspection or proxy as the only path, and room for several ports per session (`ref:rdp-multipath#ports-per-session`). The networking pillars (Azure side and client side) say how to provide it: firewall, NSG and UDR rules, forced tunneling, NAT Gateway and SNAT sizing, DNS, proxies and Private Link on both sides. Their nodes cite this pillar's claims, and this pillar's nodes link theirs, so each detail lives in one place.

## Other display protocols

The method assumes RDP over the AVD gateway, the only display protocol Microsoft documents for AVD. Another display protocol on AVD hosts would need its own transport map row, its own pinned sources and its own nodes. Nothing is written for one yet; ask for it through a research request against this gap.
