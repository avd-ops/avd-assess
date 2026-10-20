# Gap: the sample check

**Searched (2026-10-20):** Microsoft Learn (AVD Insights, connection quality, session host sizing, Windows performance troubleshooting), the Well-Architected Review, the review checklist, GitHub, the web. **Not found:** an open, tool-neutral method for a short, point-in-time health check of an AVD estate's measured user experience. Learn gives counters and some thresholds (`ref:avd-insights-glossary#perf-counters`, `ref:perfmon-troubleshooting#cpu-bands`) but no sampling plan, no rule for when a reading counts, and no way to roll readings up. Commercial health-check guides exist, but they are tied to their own collectors and aren't openly licensed, so we cite none of them here.

**What we write.** A sample check is a short inspection of measured data against thresholds that each carry their source. It is not monitoring and not a sizing study: it answers "is the experience healthy right now, and where is it not", from a few chosen hours, before anyone changes anything.

## Sampling

1. **Days:** at least three working days in one week, spread across it (start, middle and end), so one unusual day can't carry the result.
2. **Windows:** at least four one-hour windows on each day, chosen from the estate's working hours (`intake.workingHours`): the logon peak, mid-morning, early afternoon and the end of the day. Add the hours the business says are its hardest (month end, shift change).
3. **Granularity:** one value per metric per host per hour. A source that reports finer data is rolled up to the hour by its average, and the report says so.
4. **Coverage:** a host counts as sampled when it reported in at least 80% of the chosen windows. Hosts below that are listed as `unknown`, never as healthy.

## When a reading counts

5. **One hour is a data point, not a finding.** A host is over a threshold only when at least 5% of its sampled hours are over it (at least one hour in a 3 x 4 plan, two in larger plans).
6. **Severity comes from the share of hosts:** any host over makes the finding low, 5% of hosts medium, 20% high. The three numbers are ours (this gap) and versioned; an estate may override them in its own run, and the report prints the values used.
7. **Context can excuse a window, never a metric.** A known event (a patch night, a logon storm at shift change) may be excluded from a window with a stated reason; the exclusion is printed with the result.

## Outcomes and evidence

8. Each metric gets one of the assessment outcomes: `pass`, `warn` (over in some windows but below the host share), `gap` (over the host share) or `unknown` (not measured, or coverage too low).
9. The evidence for each metric is: the threshold and its citation, the windows sampled, hosts sampled and their coverage, hosts over and their share of hours. Hosts appear only as pseudonyms. No user or machine names.

## Thresholds

10. Every threshold comes from the gold-standard registry (`gap:gold-standards`). Where no published number exists, the metric has no threshold: the first run records the estate's own median and 95th percentile as its baseline (`gap:logon-target`), and later runs judge change against it.

## Not yet known

- The 5% host share and the 5% and 20% severity lines are a starting hypothesis. Runs that disagree become observations on this gap.
- avd-second-brain's C12 forensic facts today carry window-level medians and 95th percentiles, not the per-hour share over a threshold this method needs. Until a contract change adds it, a producer can only report `pass` or `gap` from the 95th percentile and must say so.
