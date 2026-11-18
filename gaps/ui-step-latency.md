# Gap: UI step-latency thresholds for synthetic desktop benchmarks

**Searched (2026-11-18):** the AVD review checklist (`ref:review-checklists-avd#C01.10`), the session host sizing guide (`ref:session-host-sizing#capacity-approaches`), the AVD Insights glossary (`ref:avd-insights-glossary#input-delay-bands`), and Microsoft Learn. **Not found:** any published AVD pass/fail threshold for synthetic UI step timings (`appLaunchMs`, `windowReadyMs`, `actionLatencyMs`, `saveCloseMs`). Existing published guidance covers `User Input Delay` bands (`ref:avd-insights-glossary#input-delay-bands`) and host CPU/memory utilization (`gap:baseline-profile`), not per-step UI Automation timings.

**What we write.** Until an empirical `C25` corpus (`rpa-ui-responsiveness`) establishes baseline percentiles across SKUs and workload classes:

1. **Report step metrics without a verdict.** `rpa-ui-responsiveness` records report `appLaunchMs`, `windowReadyMs`, `actionLatencyMs`, `saveCloseMs`, `stepSuccessRatePct`, and `stepTimeoutRatePct` for completed steps only (omitting any tail percentile exceeded by `stepTimeoutRatePct`).
2. **Gate only on existing input-delay rules.** `verdict.experienceGate` evaluates only the established `inputDelayMs` rule (`gap:baseline-profile`).
3. **Never mix with `multisession-density`.** Host counters in `rpa-ui-responsiveness` include the in-session UIA worker's own load and are tracked separately from `multisession-density`.

Retire or narrow this page once enough redacted `rpa-ui-responsiveness` `C25` runs exist to set empirical step-latency baselines.
