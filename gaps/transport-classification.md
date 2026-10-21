# Gap: one name for the transport a connection used

**Searched (2026-10-21):** RDP Shortpath and its configuration page (`ref:rdp-shortpath`, `ref:configure-rdp-shortpath#verify-transport`), Multipath (`ref:rdp-multipath`), the connection quality page (`ref:connection-quality-data#sample-queries-udpuse`), the WVDConnections table reference (`ref:wvdconnections-table#transport-type`), Insights' connection reliability view (`ref:avd-insights-use-cases#transport-pivot`), the review checklist (`ref:review-checklists-avd#F01.11`) and the web. **Not found:** a page that maps the three ways Microsoft names a connection's transport to each other. Two pages query a `UdpUse` column with values 1, 2 and 4; the table reference lists `TransportType` with `Shortpath`, `TURN` and `Websocket`; Insights pivots on `Multipath`, `Relay`, `ShortpathPublic`, `ShortpathPrivate` and `NotUsed`. Which column a workspace really has is `obs:transport-column-names-disagree`.

**What we write.** One family vocabulary, used by checks, C12 facts and reports whatever table they read:

| Family value | Meaning | UdpUse | TransportType | Insights transport |
|---|---|---|---|---|
| `udp-private` | Shortpath for managed networks (listener, or ICE/STUN over a private path) | 1 | Shortpath | ShortpathPrivate |
| `udp-direct` | Shortpath for public networks, direct through STUN | 2 | Shortpath | ShortpathPublic |
| `udp-relay` | Shortpath for public networks, relayed through TURN | 4 | TURN | Relay |
| `multipath` | Several paths kept, switching as they degrade | none documented | none documented | Multipath |
| `udp-unspecified` | UDP Shortpath, with no source saying private or public | none | Shortpath (see rule 2) | none |
| `tcp` | TCP reverse connect through the gateway | 0 | Websocket | NotUsed |
| `unknown` | No transport recorded, any other value, or no row | empty or anything else | empty or anything else | empty, `<>` or anything else |

The UdpUse column follows the configuration page; the other two columns are matched by name only, because no source states the correspondence. That is why this is a gap.

Rules:

1. **Never guess.** A value not in the table is `unknown`, and it stays `unknown` until a run shows what it means and this table changes in a reviewed PR.
2. **`Shortpath` in `TransportType` doesn't say private or public.** Read it as `udp-private` when the operator's intake says users connect over managed networks alone, as `udp-direct` when public networks alone, and otherwise as `udp-unspecified`. Every `udp-*` value counts as UDP; checks that apply only to managed-network UDP (QoS, throttling) read `udp-unspecified` as `unknown`.
3. **Multipath counts as UDP.** Insights lists it among the UDP transports (`ref:avd-insights-use-cases#transport-pivot`), though the backup paths it keeps can include TCP (`ref:rdp-multipath#automatic`). Which path carried the traffic is unknown, so checks about private, direct or relayed paths read it as `unknown`.
4. **No transport recorded is `unknown`, never `tcp`.** A connection that failed before negotiation has no transport. Insights groups an empty value (`<>`) with TCP; the family map deliberately doesn't, so every vocabulary gives the same answer for the same connection.
5. **Retire this page** the day Microsoft publishes the mapping; the checks then cite that source.
