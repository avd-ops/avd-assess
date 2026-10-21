# Foundation contracts

This folder is the authority for the formats the foundation repos exchange: avd-assess (the standards), [avd-current-state](https://github.com/avd-ops/avd-current-state) (the signal engine) and [avd-landing-zone](https://github.com/avd-ops/avd-landing-zone) (the deployment engine). They work the same with or without the layers above them: [avd-second-brain](https://github.com/avd-ops/avd-second-brain) and [avd-swarm](https://github.com/avd-ops/avd-swarm) read these formats and may add guidance, but nothing here requires them (owner, 2026-10-20). The brain's decision 0021 records the move; until then these files were vendored from the brain's `contracts/`, and the bytes didn't change when they moved.

| Contract | Files | Produced by | Read by |
|---|---|---|---|
| C11 `avd-current-state-facts/v1` | `schemas/current-state-facts.schema.json` | avd-current-state | the brain (import), the assess method |
| C15 `avd-fact-register/v1` | `fact-register.json`, `schemas/fact-register.schema.json` | here | every repo that cites a fact |
| C17 `avd-run-record/v1`, `avd-run-cost/v1` | `schemas/run-record.schema.json`, `schemas/run-journal.schema.json`, `schemas/run-cost.schema.json`, `run-use-cases.json`, `examples/run-record/` | avd-landing-zone, then the other use cases | the operator, the run report |
| C19 `avd-intake/v1` | `schemas/intake.schema.json` | the operator's answers | avd-current-state, the brain |
| C20 `avd-assess-index/v1`, `avd-assess-method/v1`, `avd-assess-map/v1`, `avd-assess-endpoints/v1` | `schemas/assess-index.schema.json`, `schemas/assess-method.schema.json`, `schemas/assess-map.schema.json`, `schemas/assess-endpoints.schema.json` | here (`index.json`, `method.json`, `map.json`, `endpoints.json`) | avd-current-state, the brain; the map by the standards library; the endpoint map by avd-current-state's endpoint check and avd-linecheck |
| C21 `avd-assessment/v1` | `schemas/assessment.schema.json` | avd-current-state | the operator, the brain |
| C23 `avd-assessment-review/v1` | `schemas/assessment-review.schema.json` | avd-current-state's assessment portal | the plan (C24), the brain (optional import) |
| C24 `avd-remediation-plan/v1` | `schemas/remediation-plan.schema.json` | avd-current-state's assessment portal | the operator, the landing zone (later), the brain and avd-swarm (optional import) |

The release manifest, `datapackage.json` with profile `avd-assess-bundle/v1` (`schemas/assess-bundle.schema.json`), is how all of the above ship together; it carries no contract number and is never committed ([distribution spec](../docs/distribution-spec.md)).

Contract numbers stay as the brain assigned them. The brain keeps the formats only the upper layers use (C8 to C10, C12, C13, C16, C18) and C14, the target state, which the landing zone reads when one is given.

## How other repos use these files

Each consumer carries byte-identical copies with a `PINS.json` naming `https://github.com/avd-ops/avd-assess`, a commit here, and a SHA-256 per file, and a test that checks the hashes. Nothing fetches these files at run time. A repo still pinned to an older brain commit keeps working; it switches its `source` to this repo at its next pin bump.

`python3 tests/check_contracts.py` checks that every schema is valid JSON Schema 2020-12, every example passes its schema, and the fact register follows its rules (unique IDs, tier prefixes, known decisions, no proposed fact as evidence, every built fact's path present in its contract's schema).

## Changing a contract

Changes start here, then go to the producers and readers, then to the brain and avd-swarm, which vendor these files like everyone else.

These rules keep the foundation working with or without the upper layers: upstream use is supported, never required, and upstream input is guidance that fails open.

1. **Upstream data goes in optional extension points, never in required fields.** A schema validates with its `extensions` absent. Run records already work this way (`extensions.<useCase>`); the other contracts gain an optional `extensions` object, keyed by namespace, the next time each one changes.
2. **Readers ignore what they don't know.** A foundation reader skips unknown extension keys and optional fields, and accepts a newer minor version. A major version it can't read counts as no guidance, not as an error.
3. **Upstream input is advice.** Absent: the foundation runs on its own defaults. Present but stale, invalid or unsupported: that item is dropped with a warning and the run continues, unless the operator asked for `-Strict`. Dropping guidance is failing open; applying an unchecked value never is.
4. **Precedence, lowest to highest: the foundation's baseline, upstream guidance, the operator's explicit choice,** and every applied value records which one it came from. Guidance never lowers the floor: current-state stays read-only, only the landing zone writes, secrets are recreated and never carried.
5. **The register's upstream tiers are optional.** `c12.*` and partner facts may be listed, but no foundation tool needs them, and a method check that cites a fact a run doesn't have scores `unknown`.
6. **Renaming or removing a fact bumps the register's `version`;** adding one doesn't.
