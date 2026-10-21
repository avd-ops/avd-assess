# Gap: assessing the networks users connect from

**Searched (2026-10-21):** the client endpoint list (`ref:avd-required-fqdn#client-list`), the Private Link client connection sequence (`ref:avd-private-link#client-dns-sequence`), the proxy page's client section (`ref:avd-proxy#client-proxy-support`), the round-trip target (`ref:avd-prerequisites#rtt-under-150`) and the checklist's proof-of-concept item (`ref:review-checklists-avd#C02.04`). **Not found:** a method for judging a user network before users move, a test that a user network resolves AVD's private names, or guidance on device-side VPN, security service edge and zero-trust agents beyond the platform address rule for hosts (`ref:avd-fabric-ips#never-proxy-or-tunnel`).

**What we write.**

1. **One intake entry per user network** (office, branch, home, guest, partner), proposed as `intake.userNetworks`: users on it, whether it allows the client endpoint list, whether outbound UDP is allowed, whether a proxy or inspection sits in the path, whether a device VPN or agent tunnels AVD traffic, and round trip to the candidate regions measured from that network, never from Azure (`obs:region-latency-from-the-user`).
2. **Private Link from the client is a per-network test.** Where users must connect privately, a person on each network resolves the discovery, feed and gateway names and compares the answers with the endpoint addresses; any public answer is `warn`. Global discovery is public by design (`ref:avd-private-link#global-workspace`), so "fully private" is never an outcome.
3. **Mixed feeds.** A network with no internet access and users subscribed to public and private feeds is `warn` for the Windows Remote Desktop client (`ref:avd-private-link#mixed-feed-limit`).
4. **Device agents are an extension.** The row `network.client-agents` holds SSE, ZTNA and VPN client categories (what must bypass, split tunneling, inspection, effect on UDP). It names categories only, never products, and is filled by the map plan's agent-category work.
5. **Measured, not assumed.** After users move, Insights round trip and transport per client network replace the intake answers (the remote protocol pillar reads transport; this pillar reads where it failed).

Nothing here is automated: it runs on users' devices and networks, so it is intake or a reviewer's test, recorded with the date and the network, never a user or device name.
