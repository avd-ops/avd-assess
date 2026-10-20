# Baseline profile: what good looks like

What a healthy AVD host pool looks like, as numbers: the experience users should get, the utilization a host should run at, and the density and size to start from, each with its source and standing. [Targets and benchmarks](targets-benchmarks.md) lists the numbers one by one; this method puts them together into one profile per workload class, in [baselines.yaml](../baselines.yaml), so an estate can be judged and tuned against it. Most of the assembly is ours (`gap:baseline-profile`).

## Method

1. **Set targets as numbers before measuring anything,** one per experience metric, tied to the workload (`ref:waf-performance-checklist#PE:01`, `ref:waf-performance-targets#measurable-targets`).
2. **Give each host pool a workload class,** light, medium, heavy or power, from its persona record in the use case method, or from the sizing guide's examples when there is none (`ref:session-host-sizing#multisession-users-per-vcpu`, `ref:session-host-sizing#estimates-only`, `gap:baseline-profile`).
3. **Start from the class's profile:** the common experience targets and utilization bands plus the class's density and minimum size (`gap:baseline-profile`). A persona may tighten a value, never loosen it without a recorded reason.
4. **Treat experience as a gate:** round-trip time (`ref:avd-prerequisites#rtt-under-150`), input delay per session and per host (`ref:avd-insights-glossary#input-delay-bands`, `ref:avd-insights-use-cases#input-delay-host-100`, `ref:session-host-sizing#input-delay-expectation`), and logon and app load time as the estate's own baseline (`gap:logon-target`).
5. **Treat utilization as bands,** under, good, watch and over, for CPU and memory per host in working hours (`ref:advisor-vm-rightsize#user-facing-targets`, `ref:perfmon-troubleshooting#cpu-bands`, `ref:perfmon-troubleshooting#pql-per-processor`). Both over- and under-provisioning are findings (`ref:waf-continuous-performance#over-and-under`).
6. **Measure the same way every time:** at least seven days, the ramp-up and peak hours from intake, percentiles rather than averages (`ref:advisor-vm-rightsize#lookback`, `ref:waf-performance-targets#percentiles`, `gap:intake`).
7. **Keep density inside the published range** and start at or under the class prior: multi-session hosts of 6 to 24 vCPU, more smaller hosts, two or more per pool and headroom for sign-in storms (`ref:session-host-sizing#multisession-vcpu-range`, `ref:session-host-sizing#more-smaller-vms`, `ref:session-host-sizing#logon-storm-headroom`).
8. **Replace priors with the estate's own measurement:** the first full window becomes the estate's baseline (`ref:waf-performance-testing#baseline-defined`, `ref:waf-performance-testing#record-baselines`), and the measured density replaces the class prior (`obs:users-per-vcpu-adopted`).
9. **Show the deviation thresholds** next to every result, so a reader sees how far from the profile is acceptable (`ref:waf-continuous-performance#deviation-thresholds`).
10. **Refresh the profile before a predicted change in use** (a new team, a new app, a season) and on the assessment cadence (`ref:waf-performance-checklist#PE:02`, `ref:waf-review-assessment#milestones`).

## Where it fits

| Repo | Its part |
|---|---|
| avd-assess | The profile and its sources ([baselines.yaml](../baselines.yaml)) |
| avd-landing-zone | Deploys a new host pool at or inside the class's profile: size, session limit, host count |
| avd-current-state | Measures the estate and judges each host pool against its profile |

The [tune and rightsize method](tune-rightsize.md) is how a running estate moves toward its profile.

## Not yet known

- No profile value has been checked against users we measured; every density is still the sizing guide's estimate (`obs:users-per-vcpu-adopted`).
- Memory per user, users per GPU, disk latency and a memory ceiling for a session host have no published number (`gap:baseline-profile`, `gap:deployment-dimensions`).
