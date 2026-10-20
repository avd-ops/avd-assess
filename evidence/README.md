# Evidence

Measured results that check the baselines: one file per submission, in the format of [schema.json](schema.json). Anyone can submit, and the maintainers use the same path for their own runs. How it works, and why, is in [gaps/evidence-intake.md](../gaps/evidence-intake.md).

1. Measure one host pool class over a window (at least 7 days for a real estate, peak hours), as [baselines.yaml](../baselines.yaml) describes.
2. Write the file. Copy a [good example](../tests/fixtures/evidence/good/) and change the values. Never add names, IDs, regions, domains or dates of the window; the format has no place for them.
3. Check it: `pip install pyyaml jsonschema` then `python3 scripts/check_evidence.py <your file>`.
4. Open a pull request that adds it here, or paste it into the "Baseline evidence" issue form.

A real estate's results need its owner's consent and at least 5 hosts and 20 users. Keep the raw data with the owner.
