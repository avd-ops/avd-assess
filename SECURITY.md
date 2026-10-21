# Security policy

avd-assess is a personal research project, not for production, provided as is, and not affiliated with the author's employer, Liquidware or Microsoft. There is no support agreement and no response time, but reports are welcome and read.

## Reporting a vulnerability

- **Privately, please.** Use **Report a vulnerability** on this repository's Security tab (GitHub private vulnerability reporting). If that button isn't there, open an issue titled "Security contact request" with no details, and a private channel will be arranged.
- **Never put secrets, tenant, subscription or object IDs, names or estate data in a report or an issue.** Issues are public.
- Say what is affected (a file, a contract, a check), how it can be misused, and how to reproduce it with synthetic data.

## What is in scope here

This repo holds the assessment method, references, the foundation contracts and their checks. Nothing here calls Azure. A flaw that matters most here is a contract, schema or check that would let a reader accept something it should refuse, or a pin that could change under a reader. A vulnerability in a repo that runs against Azure belongs to that repo; the [security review map](security-review.yaml) says which repo does what.
