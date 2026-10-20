# Gap: use cases

**Searched (2026-10-20):** the Cloud Adoption Framework's AVD assessment, proof of concept and deployment pages (`ref:caf-avd-assess`, `ref:caf-avd-poc`, `ref:caf-avd-deploy`), the session host sizing guidelines (`ref:session-host-sizing`), App Attach (`ref:app-attach`), the Well-Architected Review questionnaire (`ref:waf-review-assessment#questionnaire`), the Well-Architected AVD workload pages, and Azure Migrate. **Not found:** a maintained, vendor-neutral, structured record of who uses an AVD estate for what, and a rule for checking that record against what is deployed and measured.

- The Cloud Adoption Framework's persona criteria and app questions are the best published method, but they are prose and a sample table, and the pages are deprecated and leave Learn on 2026-10-30 (`ref:caf-avd-assess#deprecated`, `ref:caf-avd-poc#deprecated`). We pin them by Learn commit so the citation survives, and we keep only claim IDs and one line each.
- The Well-Architected AVD workload pages now redirect to the AVD product overview, so there is no live Well-Architected AVD design area to cite for user requirements.
- Azure Migrate has no first-party discovery of desktop users and their apps; Microsoft points to third-party tools (`ref:caf-avd-assess#isv-discovery`).
- The workload types are examples, not measurements (`ref:session-host-sizing#workload-types`, `ref:session-host-sizing#estimates-only`).

## What we write

A **use case** is one persona: a group of users with the same business function, apps, performance needs and controls, who can share one host pool configuration (`ref:caf-avd-assess#persona-to-host-pool`). A use case assessment writes each persona as a structured record, maps it to the design decisions it informs, and checks it against what avd-current-state can see.

### The record (proposed for C19, not yet in the fact register)

Optional `useCases` in the intake (C19), one entry per persona, foundation data in C19's core, not an upstream extension. Every value is an enum, a count, a public Azure region or a clock time. The narrative behind each answer (who said it, which team, which app by name) stays in the operator's private evidence, never in the record, a contract, this repo or an issue.

| Field | Values | From |
|---|---|---|
| `id` | `persona-<n>` | the same pseudonym form the target state and measured groups use |
| `function` | `task`, `knowledge`, `developer`, `creative`, `engineering`, `frontline`, `external`, `admin`, `other` | business function (`ref:caf-avd-assess#persona-criteria`) |
| `users`, `peakConcurrent` | counts | user count and peak sessions (`ref:caf-avd-assess#persona-criteria`) |
| `workload` | `light`, `medium`, `heavy`, `power` | the published examples (`ref:session-host-sizing#workload-types`) |
| `gpu` | `none`, `required`, `unknown` | GPU need (`ref:caf-avd-assess#persona-criteria`) |
| `desktop` | `pooled`, `personal`, `either` | dedicated or pooled |
| `dedicatedBecause` | any of `security`, `compliance`, `performance`, `noisy-neighbor`, `app-compatibility`, `admin-rights` | the published reasons for dedicated desktops (`ref:caf-avd-assess#persona-criteria`, `ref:caf-avd-deploy#legacy-apps-personal`) |
| `delivery` | `desktop`, `remoteapp`, `both` | application group |
| `apps.installed`, `apps.m365` | `yes`, `no`, `unknown` | custom image need (`ref:caf-avd-assess#app-questions`) |
| `apps.multiSession` | `yes`, `no`, `unknown` | multi-session compatibility (`ref:caf-avd-assess#app-questions`) |
| `apps.backend` | `none`, `azure`, `on-premises`, `saas`, `unknown` | where a latency-sensitive back end lives (`ref:caf-avd-assess#app-questions`) |
| `userRegions` | up to 3 Azure regions, nearest first | where users work, measured from them (`ref:caf-avd-assess#region-test-from-users`) |
| `workingHours` | the intake's working hours shape | when this persona works, if it differs from the estate's |
| `trustBoundary` | `one-org-standard`, `needs-admin`, `multi-org` | who may share a host, the security slice's proposed intake question |
| `dataControls` | any of `clipboard-restricted`, `drives-off`, `printing-restricted`, `screen-capture-protection`, `watermarking`, `none` | compliance needs the host pool's settings must carry |
| `criticality` | `standard`, `business-critical`, `mission-critical` | sets the reliability targets first (`ref:waf-reliability-checklist#RE:04`) |

**Absent means defaults.** With no `useCases`, a reader assumes one persona with the proof of concept's assumptions (`ref:caf-avd-poc#assumptions`), which is what the landing zone builds today (`obs:landing-zone-one-persona`). An entry a reader can't validate is dropped with a warning, never applied, following the contracts' fail-open rules.

**Small groups fold.** A persona under 10 users folds into its nearest neighbor before anything is measured or reported for it, so a record never singles out a small team.

### What each field decides

| Decision (fact register) | Use case fields | Checked against |
|---|---|---|
| `hostPool.type` | `desktop`, `dedicatedBecause`, `apps.multiSession`, `trustBoundary` | `c11.hostPool.type` |
| `hostPool.appGroup` | `delivery` | `c11.hostPool.preferredAppGroupType`, `c11.hostPool.appGroups` |
| `hostPool.vmSize` | `workload`, `gpu` | `c11.hostPool.vmSizes`; measured `c12.group.perUser.p95CpuPercentOfCore`, `c12.group.perUser.p95MemoryMiB` |
| `hostPool.maxSessions` | `workload` (users per vCPU, `ref:session-host-sizing#multisession-users-per-vcpu`) | `c11.hostPool.maxSessionLimit`; measured `c12.group.perHost.peakSessionsPerHost` |
| `hostPool.hosts` | `users`, `peakConcurrent` | `c11.hostPool.sessionHosts.total`; measured `c12.group.concurrency.peak` |
| `hostPool.power` | `workingHours` | `c11.hostPool.startVmOnConnect`, `intake.workingHours`; measured `c12.group.concurrency.byHour` |
| `hostPool.profileQuotaGiB` | `users`, `workload` | measured `c12.group.profile.p95SizeGiB` |
| `region` | `userRegions` | `c11.hostPool.region`, `intake.residency`, latency from users (`obs:region-latency-from-the-user`); measured `c12.group.rttMsP95` |
| `network` | `apps.backend` | `c11.network.*`, `intake.existingHub` |

Three things a use case decides have no decision in the register yet: the **image** (`apps.installed`, `apps.m365`, `c11.hostPool.images`), **app delivery** by image or App Attach (`ref:app-attach#per-user-per-host-pool`), and the **data controls** (judged by the security method once it lands). They are proposed as new decisions, not added here.

Decision readiness (`gap:decision-readiness`) says host pool type and application group are `decidable` from C11. That holds for what is deployed. Whether it is right for the people using it is a use case question: C11 can say a pool is pooled, not that its users can share a host.

### How a use case is validated

Each field gets one of the four outcomes, as checks do (`gap:scoring`), and a model never decides which:

- **pass:** the deployed configuration and, where measured, the behavior agree with the record.
- **warn:** they differ for a reason someone recorded (a trade-off), for example a personal pool kept for a persona marked `either`.
- **gap:** they differ with no recorded reason, for example `apps.multiSession: no` on a pooled host pool, or measured per-user demand a tier above the stated `workload`.
- **unknown:** nothing measured yet. Every sizing field stays unknown until measured use exists (`obs:users-per-vcpu-adopted`).

A disagreement is a finding for a person to review, never a silent rewrite of the record or the deployment.

## Not yet decided

- Where the record lives: optional fields in C19 (preferred, foundation data) or a sibling contract. Either way it lands in avd-assess `contracts/` first, after the schemas move there, and the fact register gains `intake.useCases.*` facts in one version bump.
- How a measured group maps to a persona for an estate already on AVD: today a host pool (`hp-`) is the group, so personas that share a pool can't be told apart without per-user grouping, which the privacy rules don't allow below 10 users.
