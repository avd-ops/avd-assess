# Gap: intake

**Searched (2026-10-20):** the Well-Architected Review's questionnaire (`ref:waf-review-assessment#questionnaire`), the AVD prerequisites (`ref:avd-prerequisites`). **Not found:** a machine-readable set of the few answers an AVD design needs that telemetry can't give. The Well-Architected Review asks about 60 questions, but its answers stay in a Learn profile and aren't structured for a tool.

**What we write.** Five required questions and five optional security ones, one per `intake.*` fact in avd-second-brain's fact register. Each answer is an enum or a pattern, with no names, domains, addresses or free text. The schema is contract C19 (`contracts/schemas/intake.schema.json`).

| Fact | Question | Why it matters |
|---|---|---|
| `intake.residency` | Where must user data stay? | Narrows the region (`ref:avd-prerequisites#rtt-under-150`) |
| `intake.preferredRegions` | Which regions, in order, are acceptable? | Region choice, checked against latency measured from users (`obs:region-latency-from-the-user`) |
| `intake.existingHub` | Is there a hub network to join (`none`, `azure-hub`, `vwan`, `other`)? | Network mode |
| `intake.identityConstraints` | Which identity lane (`entra-only`, `hybrid-ad`, `entra-ds`, `undecided`)? | Identity and profile storage |
| `intake.workingHours` | When do people work (start, end, time zone)? | Power settings and scaling (`ref:avd-insights-use-cases#utilization-for-scaling`) |
| `intake.hostSharing` (optional) | Who shares a session host (`one-org-standard`, `needs-admin`, `multi-org`, `undecided`)? | The security guide's trust boundary decides between pooled, personal and a separate tenant (`ref:avd-security-guide#trust-boundary`) |
| `intake.avdMfa` (optional) | Does sign-in to AVD require MFA (`required`, `not-required`, `unknown`)? | Stands in for a directory read until one exists (`ref:review-checklists-avd#G04.01`, `gap:security-scope`) |
| `intake.hostAgents` (optional) | Which security agent categories run on the session hosts (`defender-antivirus`, `defender-endpoint`, `third-party-antivirus`, `third-party-edr`, `sse-ztna-client`, `vpn-client`, `web-proxy`, `dlp-agent`, or `none` or `unknown` alone)? | One active antivirus, an EDR on every host, and no tunnel on a multi-session host its vendor doesn't support (`ref:defender-av-compatibility#third-party-av-state`, `ref:gsa-known-limitations#no-multi-session`, `gap:security-agents-scope`) |
| `intake.clientAgents` (optional) | What sits in the path on users' devices (`sse-ztna-client`, `vpn-full-tunnel`, `vpn-split-tunnel`, `web-proxy`, `tls-inspection`, or `none` or `unknown` alone)? | Whether RDP can leave the device directly and on UDP (`ref:rdp-traffic-optimization#bypass-tunnels`, `ref:avd-proxy#proxy-forces-tcp`) |
| `intake.agentRdpBypass` (optional) | Is RDP split out of tunnels, proxies and inspection on `both-sides`, `client-only`, `host-only`, `neither`, or are there `no-agents` (or `unknown`)? | The published bypass on both sides (`ref:rdp-traffic-optimization#bypass-tunnels`, `ref:rdp-traffic-optimization#no-tls-inspection`) |
