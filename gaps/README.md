# Gaps

Method we wrote because no source covers it. Each file opens with what was searched and not found, and it is retired the day a published source covers it: the method then cites that source instead.

| Gap | What it fills |
|---|---|
| [collection-map](collection-map.md) | Where each fact comes from: Resource Graph table, resource type and property |
| [checklist-mapping](checklist-mapping.md) | Which collected fact evidences which review checklist item |
| [intake](intake.md) | The questions only an operator can answer |
| [decision-readiness](decision-readiness.md) | Which target-state decisions the evidence can support |
| [insights-facts](insights-facts.md) | The facts that show whether AVD Insights is set up, and the measured facts read from its data |
| [logon-target](logon-target.md) | A target for logon time, where none is published |
| [scoring](scoring.md) | How outcomes roll up into scores |
| [sample-check](sample-check.md) | A point-in-time health check of measured user experience: sampling, when a reading counts, outcomes |
| [gold-standards](gold-standards.md) | Which source is the reference for each metric, and how that changes |
| [baseline-profile](baseline-profile.md) | One profile per workload class of what good looks like: experience gate, utilization bands, density |
| [evidence-intake](evidence-intake.md) | One path for anyone, us included, to send measured results back to the baselines |
| [tune-loop](tune-loop.md) | The order of tuning levers, one change per round, and the record each round leaves |
| [remediation-plan](remediation-plan.md) | Which change fixes each finding, which findings make plan items, and their order |
| [discovery](discovery.md) | The interview questions, and which answers become intake facts and which stay private narrative |
| [use-cases](use-cases.md) | The structured use case record, the decisions it informs, and how it is checked against what is deployed and measured |
| [use-case-library](use-case-library.md) | Common AVD use cases (base personas and overlays) as cited starting points for that record |
| [finops-scope](finops-scope.md) | What a FinOps assessment can judge, from which evidence, and which repo does what |
| [commitment-floor](commitment-floor.md) | How much compute to commit for host pools a scaling plan turns off |
| [security-scope](security-scope.md) | What a security assessment can judge, from which evidence, and which repo does what |
| [host-baseline-profile](host-baseline-profile.md) | Judging a multi-session host against Microsoft's OS baseline through a reviewed profile |
| [remote-protocols-scope](remote-protocols-scope.md) | What a remote protocol and session assessment can judge from where, intent before outcome, and the split with the networking pillars |
| [transport-classification](transport-classification.md) | One family name for the transport a connection used, mapped to the three vocabularies Microsoft uses |
| [diagnostics-scope](diagnostics-scope.md) | Which diagnostic source answers which symptom, who can read it, tools as categories, and the facts proposed for the collector |
| [error-code-map](error-code-map.md) | One map from the code an operator sees to the claim that explains it and the triage flow that handles it |
| [triage-cannot-connect](triage-cannot-connect.md) | Triage when a user can't sign in, sees no resources or can't connect |
| [triage-host-unhealthy](triage-host-unhealthy.md) | Triage when a session host isn't Available |
| [triage-slow-logon](triage-slow-logon.md) | Triage when sign-in to a session is slow, by stage |
| [triage-slow-session](triage-slow-session.md) | Triage when a session is slow or disconnects: network, host or client |
| [triage-profile-failed](triage-profile-failed.md) | Triage when a user profile fails to load |
| [network-scope](network-scope.md) | What a network assessment can judge, from which evidence, the draft network checks, and which repo does what |
| [client-network](client-network.md) | Judging the networks users connect from, AVD Private Link from the client included |
| [app-delivery-scope](app-delivery-scope.md) | What an app delivery and profile assessment can judge from where, the ways apps reach a host, and the joins the facts can't make yet |

The parts of these gaps that a tool runs (the collection map, checks, readiness and scoring) are in [method.json](../method.json), avd-second-brain contract C20 (`avd-assess-method/v1`). avd-current-state runs a pinned copy.
