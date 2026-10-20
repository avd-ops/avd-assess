# Targets and benchmarks

What good looks like, as numbers with their sources. A benchmark is `published` (a source states it), `prior` (a source states it but calls it an estimate) or `baseline` (no source has a number, so the estate's own measurement sets it).

## Method

1. **Round-trip time** from the user's network to the host pool's region: under 150 ms (published, `ref:avd-prerequisites#rtt-under-150`). Under 100 ms is ideal and over 200 ms is low quality (published, `ref:avd-insights-use-cases#rtt-ideal-100-poor-200`, `ref:avd-connection-quality#rtt-bands`). Measure it from the user (`obs:region-latency-from-the-user`).
2. **User input delay:** each host ideally under 100 ms (published, `ref:avd-insights-use-cases#input-delay-host-100`); per session, good under 150 ms, acceptable to 500 ms, poor to 2 s (published, `ref:avd-insights-glossary#input-delay-bands`).
3. **Users per vCPU, multi-session:** light 6, medium 4, heavy 2, power 1 (prior, `ref:session-host-sizing#multisession-users-per-vcpu`, `ref:session-host-sizing#estimates-only`). Replace it with measurement (`obs:users-per-vcpu-adopted`).
4. **Multi-session host size:** 6 to 24 vCPUs, never under 4 (published, `ref:session-host-sizing#multisession-vcpu-range`). Our own minimum kit sits at the floor (`obs:sizing-floor-not-measured`).
5. **Profile storage:** at least 30 GB per user (prior, `ref:session-host-sizing#profile-storage-minimum`), and the profile storage in the hosts' region (`ref:review-checklists-avd#H03.05`).
6. **Logon and time to connect:** no published number; set a baseline (`gap:logon-target`, `ref:avd-insights-glossary#time-to-connect-stages`).
7. **Reliability and recovery targets** are the workload's own, set first (`ref:waf-reliability-checklist#RE:04`).

## Not yet known

- No benchmark here has been checked against users we measured; every sizing number is still a prior (`obs:users-per-vcpu-adopted`).
