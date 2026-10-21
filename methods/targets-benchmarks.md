# Targets and benchmarks

What good looks like, as numbers with their sources. A benchmark is `published` (a source states it), `prior` (a source states it but calls it an estimate) or `baseline` (no source has a number, so the estate's own measurement sets it).

## Method

1. **Round-trip time** from the user's network to the host pool's region: under 150 ms (published, `ref:avd-prerequisites#rtt-under-150`). Under 100 ms is ideal and over 200 ms is low quality (published, `ref:avd-insights-use-cases#rtt-ideal-100-poor-200`, `ref:avd-connection-quality#rtt-bands`). Measure it from the user (`obs:region-latency-from-the-user`).
2. **User input delay:** each host ideally under 100 ms (published, `ref:avd-insights-use-cases#input-delay-host-100`); per session, good under 150 ms, acceptable to 500 ms, poor to 2 s (published, `ref:avd-insights-glossary#input-delay-bands`).
3. **Users per vCPU, multi-session:** light 6, medium 4, heavy 2, power 1 (prior, `ref:session-host-sizing#multisession-users-per-vcpu`, `ref:session-host-sizing#estimates-only`). Replace it with measurement (`obs:users-per-vcpu-adopted`).
4. **Multi-session host size:** 6 to 24 vCPUs, never under 4 (published, `ref:session-host-sizing#multisession-vcpu-range`). Our own minimum kit sits at the floor (`obs:sizing-floor-not-measured`).
5. **Profile storage:** at least 30 GB per user (prior, `ref:session-host-sizing#profile-storage-minimum`), and the profile storage in the hosts' region (`ref:review-checklists-avd#H03.05`).
6. **Logon and time to connect:** no published number; set a baseline (`gap:logon-target`, `ref:avd-insights-glossary#time-to-connect-stages`).
7. **CPU on session hosts:** under 50% healthy, over 80% critical, and a queue of two or more per core with high CPU worth investigating (published for Windows generally, not AVD, `ref:perfmon-troubleshooting#cpu-bands`, `ref:perfmon-troubleshooting#pql-per-processor`).
8. **Which number is the reference** for each metric, and its standing, is in the gold-standard registry (`gap:gold-standards`).
9. **Reliability and recovery targets** are the workload's own, set first (`ref:waf-reliability-checklist#RE:04`).
10. **Before the estate has users,** a pilot or scripted load test replaces the users-per-vCPU and size priors for a class; how it is run and where its result goes is ours, because no open workload or pass threshold is published (`gap:workload-benchmark`, `ref:review-checklists-avd#C01.10`).
11. **Together, per workload class,** these numbers make the [baseline profile](baseline-profile.md), with the utilization bands a host should run in (`gap:baseline-profile`).

## Not yet known

- No benchmark here has been checked against users we measured; every sizing number is still a prior (`obs:users-per-vcpu-adopted`).
