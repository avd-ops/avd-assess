# Gap: decision readiness

**Searched (2026-10-20):** Microsoft Learn, the Well-Architected Review, the review checklist. **Not found:** a rule for which target-state design decisions an estate's evidence can support before anyone measures users.

**What we write.** For each of the 10 decisions in avd-second-brain's fact register (C15), one of three states:

- `decidable`: Azure-side facts are enough;
- `decidable with intake`: Azure-side facts plus the intake answers (`gap:intake`);
- `needs measurement`: only measured use can decide it. The sizing claims stay priors (`ref:session-host-sizing#estimates-only`).

| Decision | Readiness without measurement | Basis |
|---|---|---|
| Identity lane | decidable with intake | `intake.identityConstraints` |
| Region | decidable with intake | C11 regions, `intake.residency`, latency from users |
| Network mode | decidable with intake | C11 network facts, `intake.existingHub` |
| Host pool type | decidable | C11 host pool type |
| Application group | decidable | C11 app group types |
| Power settings | decidable with intake | C11 Start VM on Connect, `intake.workingHours` |
| VM size | needs measurement | `ref:session-host-sizing#multisession-vcpu-range` as the prior |
| Sessions per host | needs measurement | `ref:session-host-sizing#multisession-users-per-vcpu` as the prior |
| Host count | needs measurement | peak concurrency |
| Profile share quota | needs measurement | `ref:session-host-sizing#profile-storage-minimum` as the prior |

This generalizes avd-current-state's coverage line ("N of 10 decisions"), which reads the register's `decidableFrom`.
