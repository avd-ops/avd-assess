# Security method

How to judge an estate's security against what Microsoft publishes for AVD. It is the [assessment](assessment.md) method applied to the security pillar, with the extra sources security needs. avd-current-state implements it; the findings go in the same report (avd-second-brain contract C21). Nothing here is a security audit or a compliance attestation.

## Method

1. **Scope to the customer's half** of the shared responsibility table: identity, session host OS, deployment configuration, network controls and app security (`ref:avd-security-guide#shared-responsibility`, `gap:security-scope`).
2. **Start from Microsoft's lists:** the review checklist's security items (`ref:review-checklists-avd#G02.03`, the G items and the rest) and the AVD security guide (`ref:avd-security-guide`), read in the Zero Trust order of identity, endpoints, storage, network, hosts, governance and monitoring (`ref:zero-trust-avd#seven-steps`).
3. **Settle the trust boundary first:** who shares a host decides between pooled, personal and a separate tenant, and it comes from the operator, not telemetry (`ref:avd-security-guide#trust-boundary`, `gap:intake`).
4. **Judge what the control plane shows** with Reader only: Trusted launch with Secure Boot and vTPM (`ref:review-checklists-avd#G02.03`, `obs:trusted-launch-by-default`), device redirection from the host pool's RDP properties (`ref:rdp-properties#redirection-properties`, `obs:redirection-kept-for-usability`), private endpoints and SMB encryption on the profile share (`ref:review-checklists-avd#F01.10`, `obs:smb-channel-aes128-gcm-needed`), diagnostic and audit logging (`ref:review-checklists-avd#G03.05`), and Defender for Cloud plans (`ref:review-checklists-avd#G03.04`).
5. **Read Defender for Cloud's own results** for session hosts where its plan is on, such as a missing EDR or vulnerability findings, and cite them rather than recompute them (`ref:defender-compute-recommendations#vm-recommendations`, `gap:security-scope`).
6. **Judge the host OS against a reviewed baseline profile,** Microsoft's baseline for the release minus recorded departures, never against every setting (`ref:windows-security-baselines#baselines-published`, `ref:intune-security-baselines#baselines-in-intune`, `gap:host-baseline-profile`).
7. **Leave inside-the-host and directory items `unknown`** until something reads them: local administrators, app control, screen capture protection and watermarking, Conditional Access and MFA (`ref:review-checklists-avd#G03.03`, `ref:screen-capture-protection#host-policy`, `ref:watermarking#needs-capture-protection`, `ref:review-checklists-avd#G04.01`, `gap:security-scope`).
8. **Treat a deliberate trade-off as `warn` with its reason,** and a setting nobody chose as `gap`; a model never decides which (`obs:redirection-kept-for-usability`, `gap:scoring`).
9. **Tag each finding twice:** the checklist item and pillar for the score, and the security benchmark control for a security reader (`ref:mcsb-avd-baseline#ES-1`, `gap:security-scope`).
10. **Repeat on a cadence** and compare with the last run, as for every other pillar (`ref:waf-review-assessment#milestones`).

## Where security lives in the family

Security isn't a separate project. Each foundation repo holds its usual slice, and the upper layers build on them; dependencies point down only, and avd-landing-zone and avd-current-state keep working with nothing above them.

- **avd-assess** (this page): what it should be, and why.
- **avd-current-state**: what is there now. It collects the security facts and runs these checks from a pinned copy of this method.
- **avd-landing-zone**: how it's built. Its defaults should pass these checks, its readiness checks catch drift, and it owns the host baseline profile it builds.
- **avd-second-brain**: why it is the way it is over the estate's life, including accepted risks.
- **avd-swarm**: how it's operated, with any fix a plan a person approves.

The table and the reasons are in `gap:security-scope`.

## Not yet known

- Four security checks run (method.json version 2); the items that still need a fact, a join or a host-side read are listed in `gap:checklist-mapping`.
- No host-side collector reads baseline drift, local administrators or app control yet (`gap:host-baseline-profile`).
- Whether our outcomes agree with Defender for Cloud's for the same estate hasn't been tested (`ref:defender-compute-recommendations#vm-recommendations`).
