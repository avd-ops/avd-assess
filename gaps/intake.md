# Gap: intake

**Searched (2026-10-20):** the Well-Architected Review's questionnaire (`ref:waf-review-assessment#questionnaire`), the AVD prerequisites (`ref:avd-prerequisites`). **Not found:** a machine-readable set of the few answers an AVD design needs that telemetry can't give. The Well-Architected Review asks about 60 questions, but its answers stay in a Learn profile and aren't structured for a tool.

**What we write.** Five required questions and two optional security ones, one per `intake.*` fact in avd-second-brain's fact register. Each answer is an enum or a pattern, with no names, domains, addresses or free text. The schema is contract C19 (`contracts/schemas/intake.schema.json`).

| Fact | Question | Why it matters |
|---|---|---|
| `intake.residency` | Where must user data stay? | Narrows the region (`ref:avd-prerequisites#rtt-under-150`) |
| `intake.preferredRegions` | Which regions, in order, are acceptable? | Region choice, checked against latency measured from users (`obs:region-latency-from-the-user`) |
| `intake.existingHub` | Is there a hub network to join (`none`, `azure-hub`, `vwan`, `other`)? | Network mode |
| `intake.identityConstraints` | Which identity lane (`entra-only`, `hybrid-ad`, `entra-ds`, `undecided`)? | Identity and profile storage |
| `intake.workingHours` | When do people work (start, end, time zone)? | Power settings and scaling (`ref:avd-insights-use-cases#utilization-for-scaling`) |
| `intake.hostSharing` (optional) | Who shares a session host (`one-org-standard`, `needs-admin`, `multi-org`, `undecided`)? | The security guide's trust boundary decides between pooled, personal and a separate tenant (`ref:avd-security-guide#trust-boundary`) |
| `intake.avdMfa` (optional) | Does sign-in to AVD require MFA (`required`, `not-required`, `unknown`)? | Stands in for a directory read until one exists (`ref:review-checklists-avd#G04.01`, `gap:security-scope`) |

**Proposed questions (2026-10-21, the capacity and images pillars).** Each is in the fact register as `specified`: the question and its enum are settled, and it joins `intake.schema.json` as an optional field when a producer asks it. Until then the dimension rows that cite them stay `measure: intake` with no answer.

| Fact | Question | Answers | Why it matters |
|---|---|---|---|
| `intake.graphicsWorkloads` | Which graphics work do users do? (any that apply) | `none`, `media`, `design-2d`, `visualization-3d`, `unknown` | Whether a pool needs GPU hosts (`ref:session-host-sizing#gpu-for-graphics`, `ref:review-checklists-avd#C01.12`) |
| `intake.appDelivery` | How do apps reach the hosts? | `in-image`, `app-attach`, `intune`, `mixed`, `undecided` | How many images, and how they are built (`ref:review-checklists-avd#B01.01`, `ref:avd-golden-image#approaches`); shared with the app delivery pillar |
| `intake.languages` | How many display languages do users of shared hosts need? | `one`, `few` (2 to 5), `many` (6 or more), `unknown` | Languages in a pooled image or one pool per language (`ref:avd-language-packs#pool-per-language-or-shared`, `ref:review-checklists-avd#B01.11`) |
