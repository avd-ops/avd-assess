# Gap: a security baseline profile for multi-session hosts

**Searched (2026-10-20):** the Windows security baselines (`ref:windows-security-baselines`), Intune's security baselines (`ref:intune-security-baselines`), the AVD security guide (`ref:avd-security-guide`), the benchmark's AVD baseline (`ref:mcsb-avd-baseline#PV-3`), Microsoft Learn, the web. **Not found:** a published, open list of which OS baseline settings to apply, change or skip on Windows multi-session AVD hosts. Microsoft's baselines target single-user devices; the AVD guidance names the features to turn on but no baseline profile. Commercial CIS benchmarks exist but aren't openly licensed, so they are prior art we don't cite or copy.

**What we write.** The same approach the method takes for WDOT (`ref:wdot#categories`): judge a host against a reviewed profile, not against every item.

1. **The reference is Microsoft's baseline** for the host's Windows release, from the Intune baseline when hosts are enrolled, otherwise the Security Compliance Toolkit.
2. **A profile lists the departures** from it, each with a reason and a source: a setting that breaks something in multi-session, FSLogix or the AVD agent, or one the estate accepts as a trade-off. A departure without a reason counts as a gap.
3. **The outcome** is pass when the host matches the profile, warn for each accepted departure, gap for a drift nobody recorded, and unknown when the host can't be read.
4. **avd-landing-zone owns the profile it builds,** as it owns its WDOT profile; this repo records what runs showed about each departure as observations.

Retired when Microsoft publishes a multi-session baseline or an AVD baseline profile.
