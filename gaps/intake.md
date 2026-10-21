# Gap: intake

**Searched (2026-10-20):** the Well-Architected Review's questionnaire (`ref:waf-review-assessment#questionnaire`), the AVD prerequisites (`ref:avd-prerequisites`). **Not found:** a machine-readable set of the few answers an AVD design needs that telemetry can't give. The Well-Architected Review asks about 60 questions, but its answers stay in a Learn profile and aren't structured for a tool.

**What we write.** Five required questions, five optional security ones and three optional app delivery and profile ones, one per `intake.*` fact in avd-second-brain's fact register. Each answer is an enum or a pattern, with no names, domains, addresses or free text. The schema is contract C19 (`contracts/schemas/intake.schema.json`).

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

**Proposed questions (2026-10-21, the capacity and images pillars).** How apps reach the hosts (`intake.appDelivery`) is the app delivery pillar's question, above. Each one below is in the fact register as `specified`: the question and its enum are settled, and it joins `intake.schema.json` as an optional field when a producer asks it. Until then the dimension rows that cite them stay `measure: intake` with no answer.

| Fact | Question | Answers | Why it matters |
|---|---|---|---|
| `intake.graphicsWorkloads` | What is the heaviest graphics work any user group does? | `none`, `media`, `design-2d`, `visualization-3d`, `unknown` | Whether a pool needs GPU hosts (`ref:session-host-sizing#gpu-for-graphics`, `ref:review-checklists-avd#C01.12`) |
| `intake.languages` | How many display languages do users of shared hosts need? | `one`, `few` (2 to 5), `many` (6 or more), `unknown` | Languages in a pooled image or one pool per language (`ref:avd-language-packs#pool-per-language-or-shared`, `ref:review-checklists-avd#B01.11`) |
| `intake.appDelivery` (optional) | Every way apps reach the hosts (`image`, `app-attach`, `host-deployment`, `app-layering`, `user-installed`, `undecided`)? | Which app delivery rows apply; an app layering product is a category (`gap:app-delivery-scope`) |
| `intake.appCompatibility` (optional) | Are the apps known to run on multi-session (`all-tested`, `some-untested`, `known-blockers`, `unknown`)? | Pooled against personal, and what to test first (`ref:windows-multisession-faq#reports-as-server`) |
| `intake.profileSolution` (optional) | What carries the profile (`fslogix`, `other-profile-product`, `local-only`, `undecided`)? | Which profile rows apply (`ref:fslogix-azure-files#files-or-anf`) |

**Proposed, not yet in the schema (2026-10-21).** Three optional answers for the Intune and host management pillar (`gap:intune-scope`). They are `specified` in the fact register and join `contracts/schemas/intake.schema.json` when avd-current-state reads them, so readers pinned to today's schema keep working.

| Fact | Question | Why it matters |
|---|---|---|
| `intake.hostManagement` (optional) | What manages host settings (`intune`, `group-policy`, `both`, `co-management`, `other`, `undecided`)? | Decides whether missing Intune enrollment is a gap or expected, and whether one-owner-per-setting applies (`ref:avd-management#intune-recommended`, `ref:mdm-wins-over-gp#policy-csp-only`) |
| `intake.hostServicing` (optional) | How do hosts get Windows updates (`image`, `in-place`, `mixed`, `undecided`)? | Decides whether update rings, Autopatch or nothing is right for each pool (`ref:avd-update-methods#multisession-image-based`, `ref:autopatch-avd#personal-only`) |
| `intake.clientDevices` (optional) | What must a client device prove to connect (`compliant`, `compliant-or-app-protected`, `any`, `undecided`)? | Whether Conditional Access should require a compliant device or app protection, until a directory read can see the policies (`ref:windows-app-device-compliance#app-protection-for-clients`) |
**Proposed for the reliability pillar (2026-10-21).** Five more optional answers, `specified` in the register and not yet in the schema: `intake.recoveryTime`, `intake.recoveryPoint`, `intake.regionRecovery`, `intake.recoveryDependencies` and `intake.profileData`. Their questions and enums are in `gap:reliability-scope`; they join the schema as optional fields, so an intake file written today stays valid.

**Proposed, not yet in the schema:** `intake.alertResponse`, `intake.logRetention`, `intake.coldStartTolerance` and `intake.deploymentMethod`, with their values and reasons in `gap:monitoring-scope`; the FinOps license and commitment questions in `gap:finops-scope`.
**Specified for the identity pillar (2026-10-21), not yet in the C19 schema.** The fact register lists these as `specified` with their paths, so the intake form and avd-current-state's reader can add them together in one contract change; every answer is an enum, with no names, domains or IDs (`gap:identity-scope`).

| Fact | Question | Answers | Why it matters |
|---|---|---|---|
| `intake.joinType` | How will session hosts join? | `entra-joined`, `hybrid-joined`, `ad-ds-joined`, `entra-ds-joined`, `undecided` | Single sign-on, Entra Kerberos and external users all depend on it (`ref:avd-sso#join-types`, `ref:files-entra-kerberos#clients-entra-joined`) |
| `intake.userIdentitySource` | Where do user accounts live? | `cloud-only`, `hybrid-synced`, `mixed`, `undecided` | Profile share authentication and the cloud the estate can use (`ref:files-entra-kerberos#cloud-only-and-hybrid`, `obs:fslogix-cloud-only-users-work`) |
| `intake.sso` | How do users sign in to Windows on the host? | `entra`, `adfs`, `none`, `undecided` | Credential prompts, the Windows Cloud Login policy and lock behavior (`ref:avd-authentication#sso-recommended`) |
| `intake.mfaScope` | When does AVD sign-in require MFA? | `every-sign-in`, `conditional`, `none`, `unknown` | Refines `intake.avdMfa` until a directory read exists (`ref:avd-mfa-conditional-access#two-aligned-policies`) |
| `intake.signInMethods` | Which credentials do users sign in with (any of)? | `password`, `passwordless`, `smartcard`, `federated` | Smart cards and Windows Hello for Business need a domain controller line of sight or a KDC proxy (`ref:avd-authentication#smartcard-needs-kdc`) |
| `intake.externalUsers` | Do invited users from outside the tenant use the estate? | `none`, `invited`, `undecided` | External identities need Entra joined hosts, recent builds, single sign-on and Windows App (`ref:avd-authentication#external-identity-requirements`) |

## Proposed by the pillar batch (2026-10-21)

The map's pillars add enum questions as `specified` facts in the register, each defined on its pillar's gap page. The intake schema (C19) gains them once, when the batch ends, so producers change once.

| Fact | Pillar | Defined in |
|---|---|---|
| `intake.clientApps`, `intake.clientDeviceManagement`, `intake.peripheralNeeds`, `intake.printing` | endpoints | [endpoints-scope](endpoints-scope.md#proposed-intake-questions) |
| `intake.complianceFrameworks`, `intake.auditRetentionDays`, `intake.changeControl` | governance | [governance-scope](governance-scope.md#proposed-intake-questions) |
