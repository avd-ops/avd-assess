# Gaps

Method we wrote because no source covers it. Each file opens with what was searched and not found, and it is retired the day a published source covers it: the method then cites that source instead.

| Gap | What it fills |
|---|---|
| [collection-map](collection-map.md) | Where each fact comes from: Resource Graph table, resource type and property |
| [checklist-mapping](checklist-mapping.md) | Which collected fact evidences which review checklist item |
| [intake](intake.md) | The questions only an operator can answer |
| [decision-readiness](decision-readiness.md) | Which target-state decisions the evidence can support |
| [logon-target](logon-target.md) | A target for logon time, where none is published |
| [scoring](scoring.md) | How outcomes roll up into scores |

The parts of these gaps that a tool runs (the collection map, checks, readiness and scoring) are in [method.json](../method.json), avd-second-brain contract C20 (`avd-assess-method/v1`). avd-current-state runs a pinned copy.
