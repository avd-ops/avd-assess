# Gap: what a security assessment covers, and which repo does what

**Searched (2026-10-20):** the AVD security guide (`ref:avd-security-guide#shared-responsibility`), the Zero Trust walk-through (`ref:zero-trust-avd#seven-steps`), the review checklist's security items (`ref:review-checklists-avd`), the benchmark's AVD baseline (`ref:mcsb-avd-baseline`). **Not found:** an open method that says which of these an estate assessment can judge from read-only data, which need the operator's answer, and which stay unknown. Each source lists what to do; none says how to tell whether it was done.

**What we write.**

1. **Scope is the customer's half of the shared responsibility table:** identity, session host OS, deployment configuration, network controls and app security. User devices are out of scope; the control plane is Microsoft's.
2. **Three kinds of evidence.** Control plane (Reader through Resource Graph and REST: Trusted launch, RDP properties, private endpoints, SMB settings, diagnostic settings, Defender plans and its assessment results); inside the host (baseline drift, local admins, app control, screen capture protection), read only when a host-side collector ran; and the operator's answer (trust between users, data sensitivity). Anything else is `unknown`.
3. **Tenant-wide identity settings** (Conditional Access, MFA, Security Defaults) need a directory read. Version 1 marks them `unknown` unless the operator answers the intake question, because a Reader-only run can't see them.
4. **Defender for Cloud is evidence, not a rival score.** Where its plan is on, the method reads its assessment results for session hosts and cites them; it doesn't recompute Secure Score (`ref:defender-compute-recommendations#vm-recommendations`).
5. **Findings carry two codes:** the checklist item and pillar for scoring, and the benchmark control (`NS-2`, `ES-1` and the rest) so a security reader can group them.

**Which repo does what.** The three foundation repos hold security the same way they hold everything else, and the upper layers build on them without becoming a dependency:

| Repo | Security slice | Depends on |
|---|---|---|
| avd-assess | What it should be: this method, its references, observations and gaps | Nothing |
| avd-current-state | What is there now: collects the security facts and runs the checks from a pinned copy of this method | Its own pinned copies only |
| avd-landing-zone | How it's built: defaults that pass the checks, readiness checks that catch drift, the host baseline profile | Nothing above it |
| avd-second-brain | Why: accepted risks and departures with their reasons over the estate's life, the fact register entries | Reads the three |
| avd-swarm | How it's operated: remediation as plans a person approves, behind the gate and kill switch | Cites the brain |

A separate security repo is not needed while security is one section of each layer. It would be worth it if security grew its own tools or audience that fit none of these, for example a hunting query catalog run by a security team, and even then the method stays here.
