# Gap: intake

**Searched (2026-10-20):** the Well-Architected Review's questionnaire (`ref:waf-review-assessment#questionnaire`), the AVD prerequisites (`ref:avd-prerequisites`). **Not found:** a machine-readable set of the few answers an AVD design needs that telemetry can't give. The Well-Architected Review asks about 60 questions, but its answers stay in a Learn profile and aren't structured for a tool.

**What we write.** Five required questions, two optional security ones and three optional app delivery and profile ones, one per `intake.*` fact in avd-second-brain's fact register. Each answer is an enum or a pattern, with no names, domains, addresses or free text. The schema is contract C19 (`contracts/schemas/intake.schema.json`).

| Fact | Question | Why it matters |
|---|---|---|
| `intake.residency` | Where must user data stay? | Narrows the region (`ref:avd-prerequisites#rtt-under-150`) |
| `intake.preferredRegions` | Which regions, in order, are acceptable? | Region choice, checked against latency measured from users (`obs:region-latency-from-the-user`) |
| `intake.existingHub` | Is there a hub network to join (`none`, `azure-hub`, `vwan`, `other`)? | Network mode |
| `intake.identityConstraints` | Which identity lane (`entra-only`, `hybrid-ad`, `entra-ds`, `undecided`)? | Identity and profile storage |
| `intake.workingHours` | When do people work (start, end, time zone)? | Power settings and scaling (`ref:avd-insights-use-cases#utilization-for-scaling`) |
| `intake.hostSharing` (optional) | Who shares a session host (`one-org-standard`, `needs-admin`, `multi-org`, `undecided`)? | The security guide's trust boundary decides between pooled, personal and a separate tenant (`ref:avd-security-guide#trust-boundary`) |
| `intake.avdMfa` (optional) | Does sign-in to AVD require MFA (`required`, `not-required`, `unknown`)? | Stands in for a directory read until one exists (`ref:review-checklists-avd#G04.01`, `gap:security-scope`) |
| `intake.appDelivery` (optional) | Every way apps reach the hosts (`image`, `app-attach`, `host-deployment`, `app-layering`, `user-installed`, `undecided`)? | Which app delivery rows apply; an app layering product is a category (`gap:app-delivery-scope`) |
| `intake.appCompatibility` (optional) | Are the apps known to run on multi-session (`all-tested`, `some-untested`, `known-blockers`, `unknown`)? | Pooled against personal, and what to test first (`ref:windows-multisession-faq#reports-as-server`) |
| `intake.profileSolution` (optional) | What carries the profile (`fslogix`, `other-profile-product`, `local-only`, `undecided`)? | Which profile rows apply (`ref:fslogix-azure-files#files-or-anf`) |

**Specified for the identity pillar (2026-10-21), not yet in the C19 schema.** The fact register lists these as `specified` with their paths, so the intake form and avd-current-state's reader can add them together in one contract change; every answer is an enum, with no names, domains or IDs (`gap:identity-scope`).

| Fact | Question | Answers | Why it matters |
|---|---|---|---|
| `intake.joinType` | How will session hosts join? | `entra-joined`, `hybrid-joined`, `ad-ds-joined`, `entra-ds-joined`, `undecided` | Single sign-on, Entra Kerberos and external users all depend on it (`ref:avd-sso#join-types`, `ref:files-entra-kerberos#clients-entra-joined`) |
| `intake.userIdentitySource` | Where do user accounts live? | `cloud-only`, `hybrid-synced`, `mixed`, `undecided` | Profile share authentication and the cloud the estate can use (`ref:files-entra-kerberos#cloud-only-and-hybrid`, `obs:fslogix-cloud-only-users-work`) |
| `intake.sso` | How do users sign in to Windows on the host? | `entra`, `adfs`, `none`, `undecided` | Credential prompts, the Windows Cloud Login policy and lock behavior (`ref:avd-authentication#sso-recommended`) |
| `intake.mfaScope` | When does AVD sign-in require MFA? | `every-sign-in`, `conditional`, `none`, `unknown` | Refines `intake.avdMfa` until a directory read exists (`ref:avd-mfa-conditional-access#two-aligned-policies`) |
| `intake.clientDevices` | Which devices do users connect from? | `managed-compliant`, `managed`, `unmanaged`, `mixed`, `unknown` | Whether device conditions are possible and how often to reauthenticate (`ref:avd-mfa-conditional-access#sign-in-frequency`); the endpoints pillar reads it too |
| `intake.signInMethods` | Which credentials do users sign in with (any of)? | `password`, `passwordless`, `smartcard`, `federated` | Smart cards and Windows Hello for Business need a domain controller line of sight or a KDC proxy (`ref:avd-authentication#smartcard-needs-kdc`) |
| `intake.externalUsers` | Do invited users from outside the tenant use the estate? | `none`, `invited`, `undecided` | External identities need Entra joined hosts, recent builds, single sign-on and Windows App (`ref:avd-authentication#external-identity-requirements`) |
