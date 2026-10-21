# Gap: what an endpoints and clients assessment can judge, and from where

**Searched (2026-10-21):** Windows App's getting started and platform comparison pages (`ref:windows-app-get-started`, `ref:windows-app-platforms`), the Remote Desktop client's end of support (`ref:remote-desktop-client-overview`), the AVD prerequisites (`ref:avd-prerequisites#supported-clients`), thin clients (`ref:thin-clients`), client device compliance and client-side redirection with Intune (`ref:windows-app-device-compliance`, `ref:windows-app-redirection-intune`), context-based redirection (`ref:context-based-redirections`), printing (`ref:rdp-printer-redirection`, `ref:universal-print-avd`), the connection log table and Insights (`ref:wvdconnections-table#client-columns`, `ref:avd-insights-use-cases#client-version-usage`), the review checklist (C02.03, C02.05, G02.06 in `ref:review-checklists-avd`), the family knowledge bases and the web. **Not found:** an open method that says which client facts an assessment can read without touching the users' devices, how to turn the log's client type into a supported or unsupported verdict, or what to do about kiosk-mode clients. Microsoft documents each client and platform; nobody publishes the join.

## Where each kind of evidence comes from

| Evidence | What it shows | Needs |
|---|---|---|
| Control plane | The host pool's redirection RDP properties (camera, smart cards, USB, drives, printers, clipboard), which the C11 facts already carry | Reader |
| Logs | Each connection's client type, client OS and client version (`ref:wvdconnections-table#client-columns`), when the client reports them | The connections diagnostic category and Log Analytics Reader, read as C12 facts by group |
| Operator | Which platforms users connect from, whether personal devices connect, which peripherals and printing each group needs | Intake (the proposed questions below) |
| Directory | Device compliance and the Conditional Access policies that require it | A directory read, which no family collector does yet (the identity and intune pillars) |
| Device | Installed client version on devices that never connected in the window, kiosk lock-down | Nothing the family reads; stays `unknown` |

Anything none of these shows is `unknown`, never guessed.

## Judging the client mix

The log names the client; the support status comes from the pinned sources. The method maps each logged client type to one of three states:

- **supported:** Windows App on any platform. Its version is judged against the newest version seen in the same window, the way the Insights Clients view does it (`ref:avd-insights-use-cases#client-version-usage`), and against a feature's own floor where a row needs one (Multipath, `ref:rdp-multipath#client-floors`); some mobile clients report a build number, which is compared as reported.
- **end of support:** the Remote Desktop client for Windows (MSI) or the Remote Desktop web client in public cloud after 2026-03-27, or the Store app after September 2025 (`ref:remote-desktop-client-overview#msi-and-web-end-of-support`, `ref:remote-desktop-client-overview#store-app-ended`). Sovereign clouds keep the MSI client to 2026-09-28 (`ref:remote-desktop-client-overview#msi-sovereign-extension`).
- **unknown:** the row has no client type, or a type the map doesn't list yet. A new type is added to the map with a pinned source, never guessed from its name.

A group with any end-of-support connections gets a `warn`; the plan item is a client rollout, not a landing zone change. The client OS is judged the same way against the published floors (`ref:windows-app-get-started#os-floors`). The browser behind the web client and its age aren't in the log columns, so the browser floor (`ref:windows-app-get-started#web-browser-floor`) is stated to the operator and stays `unknown` in the run.

## Needs before settings

The redirection settings themselves belong to the protocol and security rows. This pillar asks what each group needs (peripherals, printing, displays) and whether the platforms they use can deliver it (`ref:windows-app-platforms#redirection-by-platform`, `ref:windows-app-platforms#display-by-platform`). A need the platform can't meet (multiple monitors on iOS, printing from Android, smart cards from the web) is a `gap` for that group; a redirection left on that no group needs goes to the security rows to judge.

## Managed and unmanaged devices

Device management is asked, not read, until a directory read exists. Where unmanaged devices connect, the published pattern is to require client compliance on the platforms that support it and to narrow redirection for those devices, keeping the host pool settings as the floor (`ref:windows-app-device-compliance#platform-scope`, `ref:windows-app-redirection-intune#not-a-substitute`). Context-based redirection was in preview on the read date (`ref:context-based-redirections`), so a node that cites it stays guidance.

## Thin clients and kiosks

Thin clients are judged against Microsoft's approved partner list and the rule that issues reproduce on Windows App first (`ref:thin-clients#approved-partners`, `ref:thin-clients#reproduce-on-windows-app`); the partners are not named here. No AVD source covers kiosk-mode client devices, so a kiosk answer at intake is recorded and left `unknown` until a source or an observation fills it.

## Proposed intake questions

Four answers, two of them lists, registered as `specified` C19 facts; the intake schema changes once, at the end of the pillar batch (gaps/intake.md).

| Fact | Question | Values |
|---|---|---|
| `intake.clientApps` | Which client apps and platforms do users connect from? Already registered (the remote protocol rows use it too); this page defines its values. | a list of `windows`, `macos`, `ios`, `android`, `web`, `thin-client`, `kiosk`, `other` |
| `intake.clientDeviceManagement` | Are the connecting devices managed? | `managed-only`, `managed-and-personal`, `personal-only`, `unknown` |
| `intake.peripheralNeeds` | What must reach the session? | a list of `camera`, `microphone`, `smart-card`, `usb-device`, `scanner`, `local-drive`, `multi-monitor`, or `none` alone |
| `intake.printing` | How do users print? | `redirection`, `universal-print`, `host-printers`, `mixed`, `none`, `unknown` |

Three C12 facts are registered `specified` for the forensic producer: `c12.group.clients.byType`, `c12.group.clients.byOs` and `c12.group.clients.byVersion`, connection counts by client type, client OS and client type with version, for each group.
