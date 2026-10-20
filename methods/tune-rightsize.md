# Tune and rightsize

A repeatable loop for making a running AVD estate perform as its [baseline profile](baseline-profile.md) says, at the lowest cost that keeps it there: measure, compare, change one thing, measure again, record. avd-assess holds the loop; avd-landing-zone applies each change; avd-current-state measures before and after. The order of levers and the record are ours (`gap:tune-loop`).

## Method

1. **Start from the profile and a baseline measurement** of each host pool, in the profile's window (`gap:baseline-profile`, `ref:waf-performance-checklist#PE:04`, `ref:waf-performance-testing#baseline-defined`).
2. **Compare and classify:** experience pass or fail, and each host's CPU and memory band (`gap:baseline-profile`, `ref:advisor-vm-rightsize#user-facing-targets`, `ref:perfmon-troubleshooting#cpu-bands`).
3. **Fix the experience gate first.** For a failing target, read CPU, memory and disk in the same hours to find the bottleneck (`ref:avd-insights-use-cases#input-delay-then-resources`, `ref:avd-insights-use-cases#high-utilization-resize`).
4. **Then take waste out, in order:** image optimization, density, size and family, host count and hours, and rates last (`gap:tune-loop`, `ref:wdot#test-first`, `ref:finops-workload-optimization#scale-down-off-peak`). A cost change that would make an experience target fail isn't a candidate (`ref:waf-continuous-performance#over-and-under`).
5. **Write the hypothesis before the change:** which lever, from what to what, and which metric should move by how much (`ref:waf-performance-testing#hypothesis-baseline-variant`).
6. **Change one thing on one host pool** through the landing zone's parameters, in a validation pool first where the lever allows (`gap:tune-loop`, `ref:waf-performance-checklist#PE:06`).
7. **Measure again the same way:** the same days of the week, hours, statistic and counters as the baseline (`ref:waf-continuous-performance#test-before-and-after`, `gap:baseline-profile`).
8. **Keep, revert or extend:** keep when the hypothesis held and no experience target got worse, revert when one got worse, extend the window when coverage was too thin to tell (`gap:tune-loop`, `ref:waf-performance-testing#regression-and-drift`).
9. **Record the round** with its hypothesis, before and after values, decision and claims, so the next round starts from evidence (`ref:session-host-sizing#document-capacity-plan`, `gap:tune-loop`).
10. **Feed it back:** the kept values become the estate's measured density and baselines, and a prior that measured rounds keep contradicting becomes a `disagrees` observation (`ref:waf-performance-testing#record-baselines`, `gap:gold-standards`).
11. **Repeat** on a cadence and whenever use is about to change, watching for drift between rounds (`ref:waf-performance-checklist#PE:12`, `ref:waf-performance-checklist#PE:02`, `ref:waf-performance-testing#regression-and-drift`).

## Roles

| Step | avd-assess | avd-landing-zone | avd-current-state |
|---|---|---|---|
| 1, 2 | the profile and bands | | measures and classifies |
| 3 to 5 | the lever order and record shape | | proposes the candidate, with its claims |
| 6 | | applies the one change as a parameter | |
| 7, 8 | the rule for keep, revert or extend | | measures again and compares |
| 9, 10 | takes disagreements as observations | | writes the record's evidence |

Which landing zone parameters are levers, and the facts and checks avd-current-state needs, are in `gap:tune-loop`. The loop needs nothing above the foundation; an upper layer may keep the records or propose rounds as plans a person approves.

## Not yet known

- No round has run on real users; the lever order is our judgment, not a published sequence (`gap:tune-loop`).
- The scaling plan's thresholds and the load balancing algorithm are set by hand in the landing zone, so the loop can record them but not change them through it yet (`obs:tuning-levers-set-by-hand`).
- Most measured facts the loop needs are proposed, not built (`gap:tune-loop`).
