# Gap: one evidence intake for everyone

**Searched (2026-10-20):** GitHub issue forms and contribution guides in the AVD review checklist, WARA and the Well-Architected repositories, the FinOps Foundation's open data efforts, Microsoft's AVD Insights and Advisor pages, and the web. **Not found:** an open, tool-neutral way for anyone to send measured AVD results (density, experience, utilization) back to a published baseline, with privacy checks a contributor can run before sending, and a rule for how those results change the baseline. Sources publish numbers; none takes measurements back. Commercial benchmark services collect results, but into closed datasets.

**What we write.** One path, used the same way by the public and by us. There is no private shortcut: our sandbox runs and customer work go through the same file, the same check and the same review as anyone else's.

1. **A submission is one file,** `evidence/<id>.json`, in the format of [evidence/schema.json](../evidence/schema.json) (`avd-assess-evidence/v1`): the source (sandbox, lab or estate), the window, the host pool class and size, and per metric the percentiles, the claim it was compared with and a verdict. Every object is closed, so the format has no place for a name, an ID, a region or a date of the window. Free text is one short note per metric.
2. **Anyone runs the check first:** `python3 scripts/check_evidence.py <file>`. It refuses GUIDs, email addresses, IP addresses, domains, non-ASCII, unknown fields, unknown metrics or claims, and a verdict without numbers. CI runs the same check on every pull request.
3. **A real estate's results need its owner's consent** (`consent: true`) and cover at least 5 hosts and 20 users, so the aggregates can't point back at one estate. The raw data stays with the owner; only the checked file leaves. Smaller estates aren't submitted. Sandboxes and labs have no one to identify, so these minimums don't apply.
4. **Two ways in.** Open a pull request that adds the file, or, if you can't, use the "Baseline evidence" issue form and paste the checked file; a maintainer then opens the pull request for you. Either way, a person reviews and merges; a model may draft, never decide (`gap:gold-standards`).
5. **A merged file is public evidence.** An observation cites it at its commit (`https://github.com/nickprignano/avd-assess/blob/<commit>/evidence/<id>.json`), with the verdict from the file. That is the evidence the gold-standard registry needs: a candidate becomes `gold` with an `agrees` or `extends` observation and no open `disagrees`, and a `disagrees` can demote it (`gap:gold-standards`).
6. **Measured values fill baselines.** For a metric whose standing is `baseline` (memory per user, disk latency, logon time), merged files from several sources become the published range; once a pinned source states a number, the files are compared with it instead.
7. **Ours look exactly like yours.** avd-current-state is to write this file from a run (proposal below); a sandbox run's file is submitted with its run record; customer work is aggregated and checked in the customer's own environment with a pinned copy of this repo, then submitted only if it passes and the owner agrees.

## Proposal for avd-current-state and avd-landing-zone (not code)

- **avd-current-state:** a `-AssessEvidence` step that writes `assess-evidence.json` from the measured facts and the profile's window, runs the pinned `check_evidence.py`, and refuses to write the file when the minimums or the check fail. The slug it suggests is neutral (`<date>-<source>-<class>`).
- **avd-landing-zone:** a sandbox run record links the evidence file it produced, so the cost and the measurement of a run stay together.

**Not yet known.** Whether 5 hosts and 20 users is enough to keep an estate untraceable is our judgment, not a published rule; it can only go up without a new decision. No submission has been made yet.
