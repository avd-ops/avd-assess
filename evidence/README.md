# Evidence

Measured results that check the baselines and benchmark profiles: one file per submission, in the format of [schema.json](schema.json) (`avd-assess-evidence/v1`) or Contract C25 ([benchmark-result.schema.json](../contracts/schemas/benchmark-result.schema.json), `avd-benchmark-result/v1`). Anyone can submit, and the maintainers use the same path for their own runs. How it works, and why, is in [gaps/evidence-intake.md](../gaps/evidence-intake.md) and [gaps/workload-benchmark.md](../gaps/workload-benchmark.md).

1. Run a Tier 1 active benchmark profile (`benchmarks/profiles.yaml`) or measure one host pool class over a window (at least 7 days for a real estate, peak hours), as [baselines.yaml](../baselines.yaml) describes.
2. Write the file. Copy a [good example](../tests/fixtures/evidence/good/) or [benchmark-result.example.json](../contracts/examples/assess/benchmark-result.example.json) and change the values. Never add names, IDs, regions, domains or dates of a live window; the formats use closed enums, public SKUs and banded counts only.
3. Check it: `pip install pyyaml jsonschema` then `python3 scripts/check_evidence.py <your file>`.
4. Open a pull request that adds it here, or paste it into the "Baseline evidence" issue form.

Any size of estate can submit, from one user up. A real estate's results need its owner's consent (`consent: true`) and give host and session counts as bands (`hostsBand` / `usersBand` or `sampleHostsBand` / `sampleSessionsBand`), never exact. Keep the raw data with the owner.
