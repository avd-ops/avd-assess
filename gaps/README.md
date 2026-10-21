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
| [network-scope](network-scope.md) | What a network assessment can judge, from which evidence, the draft network checks, and which repo does what |
| [client-network](client-network.md) | Judging the networks users connect from, AVD Private Link from the client included |

The parts of these gaps that a tool runs (the collection map, checks, readiness and scoring) are in [method.json](../method.json), avd-second-brain contract C20 (`avd-assess-method/v1`). avd-current-state runs a pinned copy.
