# Collection method

What to collect about an AVD estate, from where, and how private each fact is. avd-current-state implements this method; the facts it writes are avd-second-brain's contract C11, named by the fact register (C15).

## Method

1. **Read the control plane with Reader only, through Azure Resource Graph** where it has the property, one query per resource type, and REST where it doesn't. Cmdlets that reshape output are a last resort. APRL's AVD queries show the Resource Graph shapes for host pools and scaling plans (`ref:aprl-desktop-virtualization`). Host pools are in the `Resources` table and only session hosts in `DesktopVirtualizationResources` (`ref:resource-graph-tables#dv-table-session-hosts`); each fact's table, type and property is in `method.json` (`gap:collection-map`).
2. **Run WARA's collector for reliability** (`Start-WARACollector -AVD`) and keep its JSON, not its Excel or PowerPoint (`ref:wara#collector-avd-json`, `ref:wara#report-needs-windows`). It covers Reliability only (`ref:wara#reliability-only`), so the other pillars come from step 1.
3. **Redact before anything leaves the operator's session.** Facts are counts, booleans, public Azure values and keyed pseudonyms, with no names, IDs, addresses or free text. Each fact's privacy class is in the register (`gap:checklist-mapping` lists the facts the checks need).
4. **Ask the intake questions** that telemetry can't answer (`gap:intake`).
5. **Measure latency where the user is,** from the user's device against regional endpoints, never from Cloud Shell (`obs:region-latency-from-the-user`, `ref:avd-prerequisites#rtt-under-150`).
6. **For measured use, read AVD Insights' data** (time to connect by stage, round-trip time, input delay, the recommended performance counters) over a stated window (`ref:avd-insights-glossary#time-to-connect-stages`, `ref:avd-insights-glossary#perf-counters`). Measuring real users is outside the free family; this step says what such work would read.
7. **Don't build a general inventory; wrap ARI for it.** For a full inventory and a network diagram, use ARI as an opt-in step (`ref:ari#excel-inventory`). Its diagram draws from the Resource Graph rows it is given (`ref:ari#diagram-from-rows`), so the rows are redacted before it draws, keeping each ID's shape. An AVD overlay and stable IDs are our additions. The collector, the validator and the C11 facts never require ARI.

## Not yet known

- Which checklist items need facts the collector doesn't read yet: the profile storage region and diagnostic settings per AVD object (`gap:checklist-mapping`).
- Image optimization state inside the guest isn't visible from the control plane (`ref:wdot#categories`). What is visible is the WDOT pin and profile an image version records, when its build tagged it (`obs:wdot-pin-on-image-version`); an untagged image's state stays unknown, not failed.
