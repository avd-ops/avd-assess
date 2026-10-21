# Gap: assessing security agents on session hosts and user devices

**Searched (2026-10-21):** Microsoft's VDI antivirus and EDR pages (`ref:defender-av-vdi`, `ref:defender-endpoint-vdi`, `ref:defender-endpoint-avd`), antivirus coexistence (`ref:defender-av-compatibility`, `ref:defender-side-by-side`), Defender for Cloud's EDR detection (`ref:defender-cloud-edr-detection`, `ref:defender-cloud-edr-settings`, `ref:defender-compute-recommendations`), the FSLogix exclusion list (`ref:fslogix-prerequisites#exclusion-scope`), AVD's security recommendations (`ref:avd-security-guide`), the RDP traffic optimization page (`ref:rdp-traffic-optimization`), Microsoft's own security service edge client (`ref:gsa-known-limitations`), the proxy page (`ref:avd-proxy`), the review checklist (G02.01, G03.04, H04.02, F01.08 in `ref:review-checklists-avd`), App Attach's pages (`ref:app-attach`) and the family knowledge bases. **Not found:**

1. A measured CPU, memory or logon cost of antivirus or EDR per user on a multi-session host, from Microsoft or any open source. The pages give settings that reduce the cost, never its size.
2. Antivirus exclusions for App Attach disk images (CIM, VHDX). FSLogix and AVD's security page cover profile containers only.
3. Any Microsoft guidance for a third-party EDR on multi-session hosts beyond "Microsoft's or a third-party product" (`ref:avd-security-guide#edr-microsoft-or-third-party`).
4. Whether a security service edge (SSE), zero trust network access (ZTNA) or VPN client that isn't Microsoft's supports concurrent sessions on a multi-session host. Microsoft's own doesn't (`ref:gsa-known-limitations#no-multi-session`), although AVD's security page suggests it on session hosts with no scope note (`ref:avd-security-guide#gsa-on-hosts`). Read together, that advice holds for personal and single-session pools only; on a multi-session host any client in the category is `unknown` support until the operator shows its vendor supports concurrent sessions.

## Categories, never products

Every agent appears here as a category (tests/wording.json): antivirus, an endpoint detection and response (EDR) product, a security service edge or zero trust network access client, a VPN client, a web proxy or PAC file, TLS inspection, a data loss prevention agent. Microsoft's own products are named as Microsoft names them, because their pages are the published reference points. Vendors' own guides aren't pinned in this repo: their URLs name the product. A reviewer reads the estate's vendor guide alongside these rows and records what it says as intake; nothing here endorses or integrates with any product.

## What an assessment judges, and from where

| Row | Judges | Evidence | Needs |
|---|---|---|---|
| `agents.av-edr-present` | Antivirus and EDR run on every session host | `c11.subscription.defenderPlans` (built); Defender for Cloud's EDR recommendation per host, `c11.hostPool.sessionHosts.edrMissing` (specified); `intake.hostAgents` | Reader, and a Defender plan that runs the agentless scan |
| `agents.coexistence` | One active antivirus; any other passive and mutually excluded | Defender Antivirus running mode (`proposed:c11.sessionHost.defenderRunningMode`); `intake.hostAgents` | A host-side read |
| `agents.edr-onboarding` | EDR onboarded at first boot as one entry per host, the image itself never onboarded | `intake.hostAgents`; the Defender portal | Intake |
| `security.endpoint-protection-tuning` | The published VDI antivirus settings and image sealing | Defender preferences (`proposed:c11.sessionHost.defenderVdiSettings`) | A host-side read |
| `agents.exclusions` | The FSLogix exclusions in every security layer | Defender exclusions against the published list (`proposed:c11.sessionHost.fslogixExclusions`) | A host-side read, plus intake for the other layers |
| `agents.vulnerability-assessment` | Vulnerability assessment covers the hosts | `c11.hostPool.sessionHosts.vulnerabilityFindings` (specified) | Reader, and a Defender plan |
| `agents.host-network-agents` | Tunnels and proxies on the host leave RDP and the platform addresses alone | `intake.hostAgents`, `intake.agentRdpBypass` | Intake, later a host-side read |
| `network.client-agents` | Tunnels, inspection and proxies on user devices let RDP out directly | `intake.clientAgents`, `intake.agentRdpBypass` | Intake |
| `agents.measured-cost` | What the agents cost per user | Nothing yet | A measured run (sandbox batch S3) |

Anything none of these shows is `unknown`, never guessed.

**Collector notes** (avd-current-state's backlog, `ref:resource-graph-tables`): the two `specified` facts read Defender for Cloud's recommendations for each session host VM with Reader, as Resource Graph security assessments: the EDR presence recommendation's unhealthy hosts (`edrMissing`) and the vulnerability findings recommendation's unhealthy hosts (`vulnerabilityFindings`), counted per host pool. With no plan running the scan, both are absent and the rows score `unknown`, never pass. The three `proposed:c11.sessionHost.*` facts wait for the owner's decision on a read-only host-side collector. The three intake facts are new optional fields in C19; the schema refuses unknown fields, so a reader on an older pin rejects an intake file that uses them, and operators answer them only after avd-current-state re-pins.

## Outcomes

- **pass:** each host runs one active antivirus and an EDR the scan sees (or the operator shows an exemption for one it can't discover, `ref:defender-cloud-edr-detection#third-party-recognized`); the FSLogix list is excluded in every layer the estate runs; RDP leaves both sides directly, uninspected (`ref:rdp-traffic-optimization#bypass-tunnels`, `ref:rdp-traffic-optimization#no-tls-inspection`).
- **warn:** a deliberate trade-off with its reason recorded, such as RDP inspected or tunneled by policy, or a second antivirus kept active for a stated period.
- **gap:** a host with no EDR and no recorded reason; two active antivirus products (`ref:defender-av-compatibility#security-center-required`); exclusions missing from a layer that scans profile containers; a tunnel or inspection on the path to the platform addresses (`ref:avd-fabric-ips#never-proxy-or-tunnel`); a client in this category on multi-session hosts that its vendor doesn't support there.
- **unknown:** no Defender plan running the scan, no host-side read, no intake answer.

A model never decides between `warn` and `gap`: the recorded reason does (`gap:scoring`).

## What we don't set

No target for agent CPU or logon cost until a measured run gives one (`gap:evidence-intake`). The first candidate is sandbox batch S3 in the map plan: the same light baseline profile with the agents on and off, on the smallest hosts, with its own estimate and the owner's go.

## Split with the other pillars

This pillar owns what runs on the host or device and how it is configured. The networking pillars own the network devices: firewalls, proxies, forced tunneling and the routes around them (`network.inspection`, `gap:client-network`). The remote protocol pillar owns transport and states what RDP needs (`gap:remote-protocols-scope`); a tunnel that can't carry UDP, or a proxy as the only path, leaves RDP on TCP (`ref:avd-proxy#proxy-forces-tcp`, `ref:gsa-known-limitations#no-udp-internet-access`). The security posture pillar owns Defender for Cloud plans and the host baseline profile (`methods/security.md`, `gap:host-baseline-profile`); the intune pillar owns how agents and their policies are delivered.
