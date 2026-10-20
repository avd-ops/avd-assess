# Sample check method

A short, point-in-time health check of an estate's measured user experience: a few chosen hours, judged against thresholds that each carry their source, before anyone changes anything. It sits between the [assessment](assessment.md), which judges configuration, and the [targets and benchmarks](targets-benchmarks.md), which say what good looks like. No open method covers it, so most of it is ours (`gap:sample-check`).

## Method

1. **Collect the counters Insights recommends** for session hosts, at the intervals it lists, so the check reads data an estate may already have (`ref:avd-insights-glossary#perf-counters`).
2. **Sample at least three working days and four one-hour windows a day,** spread over the week and over the working hours from intake, rather than a single busy afternoon (`gap:sample-check`, `ref:perfmon-troubleshooting#patterns-over-days`, `gap:intake`).
3. **Treat an hour as a data point, not a finding:** a host is over a threshold only when 5% of its sampled hours are, and severity comes from the share of hosts over (`gap:sample-check`).
4. **Take every threshold from the gold-standard registry** and print its citation with the result (`gap:gold-standards`): round-trip time (`ref:avd-prerequisites#rtt-under-150`), input delay (`ref:avd-insights-glossary#input-delay-bands`, `ref:avd-insights-use-cases#input-delay-host-100`), CPU (`ref:perfmon-troubleshooting#cpu-bands`) and CPU queue per core (`ref:perfmon-troubleshooting#pql-per-processor`).
5. **Where nothing is published, record a baseline instead of a verdict:** memory, disk latency, application load and logon time start as the estate's own median and 95th percentile (`gap:logon-target`, `gap:sample-check`).
6. **Give each metric an assessment outcome:** pass, warn, gap or unknown; too little coverage is unknown, never a pass (`gap:sample-check`, `gap:scoring`).
7. **Keep the evidence, not the people:** windows, coverage, hosts over and their share of hours, with hosts as pseudonyms only (`gap:sample-check`).
8. **Feed the results forward:** outcomes count as performance-pillar checks in the score, and baselines become the estate's `baseline` benchmarks (`gap:scoring`, `gap:logon-target`).
9. **Repeat with the same days and windows after a change** and compare, so before and after are measured the same way (`ref:waf-review-assessment#milestones`).
10. **Send disagreements back:** a threshold that real runs keep contradicting becomes a `disagrees` observation and can demote its registry entry (`gap:gold-standards`).

## Not yet known

- No sample check has run against real users yet; every threshold except round-trip time is still a candidate in the registry (`gap:gold-standards`).
- The per-hour share this method needs isn't in avd-second-brain's C12 forensic facts yet; until it is, producers judge from the 95th percentile and say so (`gap:sample-check`).
