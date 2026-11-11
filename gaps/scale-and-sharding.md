# Gap: multi-stamp sharding, storage packing, and wave ceilings

**Searched (2026-10-27):** Microsoft Learn (Azure subscription and service limits for AVD, Azure Files scalability and performance targets for VDI, session host sizing guidance, Well-Architected Framework reliability and performance checklists, Cloud Adoption Framework AVD design guide). **Not found:** a single set of operational sharding ceilings (below hard ARM platform limits) for packing large estates across host pools, Premium Azure Files profile shares, subscription stamps, and migration waves.

**What we write.** Operational planning ceilings so automated target-state design and wave scheduling read every threshold from cited standards rather than hardcoded constants.

## 1. Host pool, profile storage, and subscription stamp ceilings

Hard platform limits (`ref:avd-service-limits#hosts-per-pool`, `ref:avd-service-limits#host-pools-per-workspace`) sit well above the blast-radius and storage-contention boundaries where operational risk rises. The planning ceilings below apply unless overridden by the operator:

| Boundary | Operational ceiling | Basis and citations |
|---|---|---|
| Host pool size | At most 150 session hosts or 2,500 concurrent sessions per host pool; at least 2 hosts per pooled pool plus 10% sign-in storm headroom | `ref:avd-service-limits#hosts-per-pool`, `ref:waf-reliability-checklist#RE:05`, `ref:session-host-sizing#logon-storm-headroom`, `gap:scale-and-sharding` |
| Profile storage packing | Pack Premium Azure Files shares to 80% of the 100 TiB capacity ceiling and 100,000 peak IOPS ceiling (1.20x quota buffer, 100 GiB minimum share quota, 85% steady-state + 15% logon-storm session mix at peak) | `ref:azure-files-vdi#users-per-share`, `ref:azure-files-vdi#storm-sizing`, `ref:session-host-sizing#profile-storage-minimum`, `ref:avd-fslogix-storage#tier-by-workload`, `gap:scale-and-sharding` |
| Subscription stamp blast radius | At most 5,000 concurrent users or 400 session hosts per landing-zone subscription stamp, peered to shared platform connectivity | `ref:arch-avd-design-guide#platform-connectivity`, `ref:waf-reliability-checklist#RE:05`, `gap:scale-and-sharding` |

## 2. Wave scheduling and post-wave parity thresholds

When scheduling waves (`avd-wave-plan/v1`, Contract C29) and evaluating post-wave parity (`avd-verify-report/v1`, Contract C30):

- **Pilot ring (`wave-00`):** 1% to 5% of estate users (target 3%, minimum 5 users, maximum 250 users), followed by bulk waves capped at 250 users (or 1,000 for enterprise estates) per change window (`ref:caf-avd-deploy#persona-iterations`, `gap:scale-and-sharding`).
- **Maintenance window bandwidth ceiling:** Profile delta-sync volume stays within 70% of the scheduled maintenance window (`gap:scale-and-sharding`).
- **Post-wave parity and recalibration (`avd-verify-report/v1`):** Experience targets must hold (`rttMs` p95 <= 150 ms, logon p95 within 1.15x of pre-migration baseline; `ref:avd-prerequisites#rtt-under-150`, `ref:waf-performance-testing#regression-and-drift`, `gap:sample-check`). When binding resource utilization on a completed wave with at least 3 sessions/host and 40% binding utilization drifts by more than 15% from predicted density, subsequent stamps recalibrate toward the 80% target (`ref:advisor-vm-rightsize#user-facing-targets`, `ref:perfmon-troubleshooting#cpu-bands`, `gap:tune-loop`).
