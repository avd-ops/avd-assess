# Gap: a repeatable tune and rightsize loop for AVD

**Searched (2026-10-20):** the Well-Architected performance pillar (`ref:waf-performance-checklist#PE:12`, `ref:waf-continuous-performance`, `ref:waf-performance-testing`), the cost pillar and commitment guidance read for the FinOps method, Advisor's right-size criteria (`ref:advisor-vm-rightsize`), the FinOps workload optimization capability (`ref:finops-workload-optimization`), the session host sizing guide (`ref:session-host-sizing#capacity-approaches`), AVD Insights use cases, autoscale, WDOT (`ref:wdot#test-first`), GitHub and the web. **Not found:** an open, tool-neutral loop for tuning and rightsizing an AVD estate that says in what order to pull the levers, keeps user experience as a gate on every cost change, changes one thing at a time, and writes down each change so the next one starts from evidence. The Well-Architected pillar gives the shape (targets, baselines, test before and after); Advisor gives a resize rule for one VM at a time and doesn't know about sessions, scaling plans or logon storms; the sizing guide says to pilot or simulate before sizing and to document the plan (`ref:session-host-sizing#document-capacity-plan`), but not how to keep doing it once the estate runs.

## What we write

The loop is in the [tune and rightsize method](../methods/tune-rightsize.md). The parts that are ours:

1. **The lever order.** Fix the experience gate first, then take waste out: (1) the bottleneck behind a failing experience target (CPU, memory, disk or network, read in the same hours, `ref:avd-insights-use-cases#input-delay-then-resources`); (2) the image (optimizations, tested first, `ref:wdot#test-first`); (3) density (session limit); (4) size and family; (5) host count and hours (scaling plan, power); (6) rates last, after hours and sizes are settled, as the FinOps method orders it (`ref:finops-workload-optimization#scale-down-off-peak`). Cheaper and more reversible levers come first; a lever later in the list is judged only after the ones before it are settled.
2. **One change, one hypothesis.** Each round changes one lever on one host pool, and states beforehand what should move and by how much (`ref:waf-performance-testing#hypothesis-baseline-variant`).
3. **The same measurement before and after:** the same days of the week, hours, statistic and counters, from [baselines.yaml](../baselines.yaml) `window` (`ref:waf-performance-checklist#PE:04`).
4. **Keep, revert or extend.** Keep the change when the hypothesis held and no experience target got worse; revert when an experience target got worse; extend the window when coverage was too thin to tell.
5. **A tuning record per round,** with no names: host pool pseudonym, class, lever, from and to values, hypothesis, before and after values with their windows and coverage, decision, and the claims that justified it. A record is evidence for the next round and becomes the estate's measured density and baselines.

## Roles in the foundation

| Repo | Its part of the loop |
|---|---|
| avd-assess | The baseline profile, the bands, the lever order and the record shape (this page, [baselines.yaml](../baselines.yaml)) |
| avd-landing-zone | Applies a change as a parameter, through the same deploy path as the first deployment, and prints what it changed |
| avd-current-state | Measures before and after, judges against the profile, and writes the record's evidence; it never changes the estate |

The loop works with these three alone. A layer above the foundation can keep the records over the estate's life or propose the next round as a plan a person approves; it is an optional reader, never a step the loop needs.

## Proposal for avd-landing-zone (not code)

Tuning levers among the template's 57 parameters at [53c9e7d](https://github.com/nickprignano/avd-landing-zone/blob/53c9e7d131f0dc7e0dd9acb40f9f4b2f2bd58cd7/bicep/main.bicep) (`profileBackupTier` and `recoveryLocation` among them, neither a tuning lever):

| Lever | Parameters | Flag and variable today |
|---|---|---|
| Density | `maxSessionLimit` | `--max-sessions`, `AVD_MAX_SESSION_LIMIT` |
| Size and family | `sessionHostVmSize` | `--vm-size`, `AVD_SESSION_HOST_VM_SIZE` |
| Host count | `sessionHostCount` | `--hosts`, `AVD_SESSION_HOST_COUNT` |
| Hours and power | `startVmOnConnect`, `enableAutoShutdown`, `autoShutdownTime`, `autoShutdownDays`, `scalingTimeZone` | `--start-vm-on-connect`, `--auto-shutdown` |
| Profile capacity | `profileShareQuotaGiB`, `fslogixProfileSizeMiB`, `profileStorageSku` | `--profile-quota` for the quota |
| Image | `sessionHostImage` (an optimized image version) | none; image pipeline |
| Session settings | `rdpProperties` | none |

Not parameters, so the loop can only record them today (`obs:tuning-levers-set-by-hand`): load balancing (fixed breadth-first), the scaling plan's capacity thresholds, minimum host shares and schedule, the OS disk type (fixed Premium SSD) and accelerated networking (fixed on).

Proposed, in this order, each only when a real round needs it:

1. A `--tune-record <id>` flag (and the same field in the target-state reader) that carries the record ID into the deployment's state line and run record, so a change can be traced to the round that asked for it.
2. Parameters for the scaling plan's ramp-up and peak capacity threshold and minimum host share, with `empty()` guards, a flag, a reader capability line and a test, following the sizing rule in decision 0010.
3. A parameter for the load balancing algorithm, defaulting to today's breadth-first.
4. The existing warning on a size change to a running landing zone stays; a tuning round is not a reason to apply it silently.

## Proposal for avd-current-state (not code)

Facts it needs (built facts in the register today: `c11.hostPool.vmSizes`, `c11.hostPool.maxSessionLimit`, `c11.hostPool.sessionHosts.total`, `c11.hostPool.sessionHosts.sessions`, `c11.hostPool.startVmOnConnect`, `c11.hostPool.images`, `c11.storage.sku`):

- **Configuration, proposed:** the vCPU and memory of each VM size in use, read from the public resource SKU list, so density per vCPU can be computed (`c11.hostPool.vmSizeCapabilities`); the load balancing type (already proposed in the dimension register); the scaling plan's presence, capacity thresholds and minimum host shares per phase (`c11.hostPool.scalingPlan.*`).
- **Measured, proposed:** the measured facts the Insights standard lists (concurrency, sessions per host, CPU P95 and available memory per host, input delay, round-trip time, time to connect), read in the profile's window and hours, plus CPU queue per core, P99 memory, disk latency P95 and, per host, the share of sampled hours in each band.

Checks it would run from a pinned copy of the method (warn, never fail, until a run has checked them against users):

| Check | Outcome |
|---|---|
| Density over the class prior | `warn` when the session limit per vCPU is above the class's users per vCPU |
| Host size out of range | `warn` outside 6 to 24 vCPU for multi-session |
| Experience gate | `gap` when an experience target fails in the window |
| CPU and memory bands | the band per host, and the pool's share of hosts in each |
| Rightsize candidate | `warn` with the direction (down, up, density) and the claims, never the size to buy |
| Before and after | for two runs with the same window, each metric's change, and whether the record's hypothesis held |

A record is written as a file in the operator's own private output, never in a shared repo; only its counts and outcomes may become a public observation.

**Not yet known.** No round of the loop has run on real users. The lever order is our judgment from the sources, not a published sequence.
