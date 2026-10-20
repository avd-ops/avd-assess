# Gap: mapping facts to review checklist items

**Searched (2026-10-20):** the AVD review checklist (`ref:review-checklists-avd`), APRL's AVD recommendations (`ref:aprl-desktop-virtualization`), Microsoft Learn, the web. **Not found:** a mapping from the AVD checklist's items to the data that shows whether an estate meets them. The checklist's AVD items carry no Resource Graph query; APRL's reliability items do, and WARA runs them.

**What we write.** For each checklist item we can evidence, the facts that decide it, by fact ID in avd-second-brain's fact register (C15), and the rule. Items that need data the family doesn't collect stay listed as `unknown`, with the data they would need.

| Item | Facts | Rule | State |
|---|---|---|---|
| `ref:review-checklists-avd#E01.05` | `c11.hostPool.type`, `c11.hostPool.startVmOnConnect` | Personal host pools have Start VM on Connect on | Draft |
| `ref:review-checklists-avd#H03.05` | `c11.hostPool.region`, the profile storage account's region (not yet a C11 fact) | Same region | Needs a fact |
| `ref:review-checklists-avd#F01.10` | `c11.storage.privateEndpoint` | The profile share has a private endpoint | Draft |
| `ref:review-checklists-avd#E02.02` | Diagnostic settings per AVD object (not yet a C11 fact) | All four object types send to Log Analytics | Needs a fact |

Rules become C20 check files when avd-second-brain's schema lands (spec phase 2). Facts marked "needs a fact" go to avd-current-state as register changes.
