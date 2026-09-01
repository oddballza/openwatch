# OpenWatch — Phase 1 (Reconnaissance)

Investigation into building an open, ad-free replacement for the **Da Fit** Android
companion app, for an `MT55` smartwatch.

## Outcome: no application is being built

Reconnaissance found that the watch self-identifies as **`MOYOUNG-V2`** and speaks a
protocol that **Gadgetbridge already implements in full** — 82 commands, historical
sync, workouts, notifications, weather, alarms, all under test upstream.

The only gap is that Gadgetbridge matches devices by a regex on the advertised name,
and `MT55` matches **0 of 412** patterns in the codebase.

**Recommendation: use Gadgetbridge and contribute a ~40-line `MT55Coordinator`
upstream.** Full reasoning in [`docs/ARCHITECTURE_DECISION.md`](docs/ARCHITECTURE_DECISION.md).

## Upstream contribution status

The recommendation was carried out. MT55 support was built, hardware-tested, and
submitted to Gadgetbridge:

- **[PR #6688](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688)** —
  `MT55Coordinator` (verified-only capabilities). Open, maintainer-triaged
  (`device moyoung`, `new device`); review round 1 addressed (changelog hunk removed).
- **[Issue #6689](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689)** —
  clean-room bug report for a shared-code DND on/off parse error. Open, triaged.

Full hardware-test results and the contribution trail are in
[`docs/MT55_VERIFICATION.md`](docs/MT55_VERIFICATION.md).

## Documents

| Document | Contents |
|---|---|
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | Alternatives, device identification, gap analysis, recommendation, firmware |
| [`docs/GADGETBRIDGE_ANALYSIS.md`](docs/GADGETBRIDGE_ANALYSIS.md) | Upstream architecture map, matching logic, compatibility matrix, limitations |
| [`docs/ARCHITECTURE_DECISION.md`](docs/ARCHITECTURE_DECISION.md) | ADR-001: options A–D and why B was chosen |
| [`docs/LICENSING.md`](docs/LICENSING.md) | AGPL-3.0 analysis and code-origin audit |
| [`docs/evidence/mt55-recon.md`](docs/evidence/mt55-recon.md) | Literal tool output backing every device claim |

## Device summary

| | |
|---|---|
| Name / MAC | `MT55` / MAC redacted (declared public) |
| Manufacturer (DIS) | `MOYOUNG-V2` |
| Software / Firmware | `MOY-JSB2-2.0.4` / `JLQFNJEJ1.1` |
| Protocol | Moyoung V2 (MTU-based framing) |
| Verified live | Battery 48 %; steps 790 / 655 m / 42 kcal |
| Not supported | ECG (`FEE7`/`FEE8` characteristics absent) |

## Tools

Vendor-neutral BLE diagnostics used to produce the evidence — reusable for the next
unlisted watch. Requires BlueZ and `python3-dbus`; no root needed for enumeration.

```sh
python3 tools/scan_debug.py   # LE discovery (note: needs a Transport=le filter)
python3 tools/full_gatt.py    # connect + full GATT enumeration + DIS reads
python3 tools/read_vals.py    # battery + steps + vendor characteristic reads
```
