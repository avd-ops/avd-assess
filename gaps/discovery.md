# Gap: discovery

**Searched (2026-10-20):** the Cloud Adoption Framework's AVD assessment (`ref:caf-avd-assess`), the Well-Architected Review questionnaire (`ref:waf-review-assessment#questionnaire`), the AVD prerequisites (`ref:avd-prerequisites`). **Not found:** an interview guide for AVD that says which answers can be structured for a tool and which must stay narrative. The Framework's questions are the closest and are leaving Learn (`ref:caf-avd-assess#deprecated`); the Well-Architected Review covers every workload, not desktops, and keeps its answers in a Learn profile.

Discovery is the second stage of an assessment: the interviews that give the narrative detail inventory can't. It runs alongside collection and before analysis. This page holds the questions and their structure only. **The answers are customer data:** narrative stays in the operator's private evidence (a `discovery/` folder beside their collection output), and only the structured answers below become intake (C19) facts.

## How to run it

1. **Interview by role, not by system:** the business owner, an app owner per major app, the desktop or EUC team, security and compliance, and a few users from each suspected persona.
2. **Start from the default** of one persona with the proof of concept's assumptions (`ref:caf-avd-poc#assumptions`), and ask what breaks it (`ref:caf-avd-assess#assumption-validation`).
3. **Write each answer twice:** the structured value in the intake, and the narrative, with who said it, in the private record.
4. **Mark anything nobody knows as `unknown`.** It becomes something to measure, not a guess.

## Questions

Each question says what kind of answer it takes: **intake** (a field in C19, existing or proposed in `gap:use-cases`), or **narrative** (private evidence only).

### Business drivers and constraints

| Question | Answer | Informs |
|---|---|---|
| Why AVD now: which of productivity, safe access from unmanaged devices, supporting users as workloads move, or replacing aging VDI? | narrative | scope and success measures |
| Where must user data stay? | intake `residency` | region (`gap:intake`) |
| Is there a hub network or an existing identity lane to join? | intake `existingHub`, `identityConstraints` | network, identity (`gap:intake`) |
| What would make this a failure for the business: outage length, data loss, slow sign-in? | intake `criticality` per persona, the numbers as narrative | reliability targets (`ref:waf-reliability-checklist#RE:04`) |
| How will cost be shown back: by business unit, charge code, or not at all? | narrative | cost allocation (`ref:caf-avd-assess#business-function-for-cost`) |

### Users and personas

| Question | Answer | Informs |
|---|---|---|
| Which groups of users do clearly different work? Name each by function, not by team. | intake `function` per persona | the persona list (`ref:caf-avd-assess#persona-criteria`) |
| How many users in each, and how many on at the busiest time? | intake `users`, `peakConcurrent` | host count |
| When does each group work, and does anyone work nights or weekends? | intake `workingHours` | power settings |
| Where do they work from? Have one user per location run the latency test. | intake `userRegions`; the measured numbers stay with the evidence | region (`ref:caf-avd-assess#region-test-from-users`, `obs:region-latency-from-the-user`) |
| What does a heavy day look like for them: which apps open at once, and what is slow today? | intake `workload`; the description as narrative | VM size, sessions per host (`ref:session-host-sizing#workload-types`) |
| Does anyone need graphics acceleration? | intake `gpu` | VM size |
| Does anyone need their own desktop: admin rights, installs of their own, a noisy workload, a security or compliance rule? | intake `desktop`, `dedicatedBecause` | host pool type |

### Apps

| Question | Answer | Informs |
|---|---|---|
| Which apps does each group need? List them in the private record. | narrative (app names never leave it) | app delivery |
| Are any installed rather than web or SaaS? Does the group need Microsoft 365 apps? | intake `apps.installed`, `apps.m365` | image (`ref:caf-avd-assess#app-questions`) |
| Is any app known not to run on multi-session Windows? | intake `apps.multiSession` | host pool type (`ref:caf-avd-deploy#legacy-apps-personal`) |
| Where do the apps' back ends live, and is any of them sensitive to latency? | intake `apps.backend` | region, network (`ref:caf-avd-deploy#app-remediation-blocks`) |
| Full desktop, or only a few apps? | intake `delivery` | application group |

### Security and compliance

| Question | Answer | Informs |
|---|---|---|
| Who may share a host: one organization's standard users, users who need admin, or more than one organization? | intake `trustBoundary` | host pool type, tenant boundary |
| Which data controls must the session enforce: clipboard, drives, printing, screen capture protection, watermarking? | intake `dataControls` | host pool RDP properties and host policy |
| Which regulations apply, and who signs off? | narrative | review of findings |

## What it produces

The intake answers become the `useCases` record (`gap:use-cases`), which the use case method checks against what is deployed and measured. The narrative stays private and is what a person reads when reviewing a finding. Nothing from either goes into this repo.
