# Gap: a logon time target

**Searched (2026-10-20):** Microsoft Learn (AVD Insights, connection quality, prerequisites), the web. **Not found:** a published target for logon time or time to connect. Insights splits time to connect into stages (`ref:avd-insights-glossary#time-to-connect-stages`) but gives no number. Commercial experience scores tune their thresholds per customer and are proprietary.

**What we write.** A baseline method, not a number:

1. Measure time to connect and its stages over a stated window of at least two working weeks, new sessions apart from reconnections (Insights notes they differ).
2. Record the median and the 95th percentile per host pool.
3. Set the target as a change from that baseline, and judge a change by the same two figures over the same kind of window.

A number becomes a `published` benchmark only if a source publishes one.
