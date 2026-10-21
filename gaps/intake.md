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
