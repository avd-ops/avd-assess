# Gap: triage when a session is slow or disconnects

**Searched (2026-10-21):** connection quality (`ref:avd-connection-quality`, `ref:connection-quality-data`), the network and graphics tables (`ref:wvdconnectionnetworkdata-table`, `ref:wvdconnectiongraphicsdata-table`), Insights use cases and glossary (`ref:avd-insights-use-cases`, `ref:avd-insights-glossary`), Shortpath troubleshooting (`ref:troubleshoot-rdp-shortpath`), Performance Monitor (`ref:perfmon-troubleshooting`), the family knowledge bases and the web. **Not found:** one flow that separates the network, the host and the client for a slow session. Each page covers one of them. Symptoms: `slow-session`, `disconnects` in `intake.reportedSymptoms`.

## Flow

1. **Network or host?** Round-trip time from the network data against the published bands; input delay against its bands (`ref:avd-connection-quality#rtt-bands`, `ref:avd-insights-use-cases#rtt-ideal-100-poor-200`, `ref:wvdconnectionnetworkdata-table#rtt-and-bandwidth-only`, `ref:avd-insights-glossary#input-delay-bands`). High RTT with normal input delay is the path; high input delay is the host (`ref:avd-insights-use-cases#input-delay-then-resources`).
2. **Path slow:** the transport each connection used, through the family map (`gap:transport-classification`), and the region against where users are (`ref:avd-connection-quality#review-region-latency`). Shortpath failures have their own codes (`ref:troubleshoot-rdp-shortpath#udp-error-codes`, `gap:error-code-map`). The protocol and networking pillars own the fix.
3. **Host slow:** CPU and memory counters over a working day, against the published bands (`ref:perfmon-troubleshooting#cpu-bands`, `ref:perfmon-troubleshooting#patterns-over-days`); sizing is the capacity pillar's.
4. **Graphics:** frame drops by cause say whether the network, the client or the server dropped them (`ref:wvdconnectiongraphicsdata-table#frame-drops-by-cause`).
5. **Teams and media:** the WebRTC component's health check (`ref:avd-sessionhost-get-api#webrtc-check`); media settings are the protocol pillar's.
6. **Disconnects:** Insights' connection reliability view groups them by host, client, transport and gateway region (`ref:avd-insights-use-cases#transport-pivot`); a cluster on one pivot is the lead.

## Facts

`c12.group.rttMsP95` and the protocol pillar's transport shares answer step 1 and 2; host counters are measured, not C11. This pillar adds no fact here.
