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

The recommendation was carried out. The **first three** pull requests were merged into
Gadgetbridge on 2 September 2026, all by maintainer `joserebelo`:

| PR | What | Diff | Merge commit |
|---|---|---|---|
| [#6688](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688) | `MT55Coordinator` — new device support, verified-only capabilities | +84 / −0 | [`8305c4b7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/8305c4b7b0a62e9d334842a55584bfb7701e7d1b) |
| [#6690](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6690) | Charging detected from battery level > 100 — fixes a 146% battery display. **Shared Moyoung code**, addresses [#5236](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5236) | +10 / −3 | [`bb5fcf9d`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bb5fcf9d32a2) |
| [#6691](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691) | Sleep-overlay log spam reduced to debug — 208 warnings in ~2 min of normal use. **Shared Moyoung code**, addresses [#5859](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5859) | +1 / −1 | [`1506767f`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/1506767f6a70) |

**MT55 is officially supported in Gadgetbridge.** Two of the three changes fix
pre-existing defects reported by other users, in code shared by every Moyoung device.

Contribution continued past this milestone — further Moyoung driver fixes, smart-scale
bio-impedance storage, and dashboard widgets. The authoritative, current list is
[every pull request by `oddballza`](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls?state=all&poster=1443751).
No running total is restated here on purpose: a hand-maintained count drifts from the
registry, and the registry is one click away.

`MT55Coordinator.java` is in upstream `master` today, carrying
`Copyright (C) 2026 oddballza` — verify at
[`devices/moyoung/MT55Coordinator.java`](https://codeberg.org/Freeyourgadget/Gadgetbridge/src/branch/master/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/devices/moyoung/MT55Coordinator.java).

Left open by intent:

- **[Issue #6689](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689)** —
  clean-room report root-causing a DND on/off parse error in shared Moyoung code. Two
  candidate fixes offered and neither chosen: deciding between them needs cross-model
  behaviour that one device cannot establish, so it is deferred to the maintainers with
  an offer to test whatever they choose.
- **Issues #5236 and #5859** are referenced as *Addresses*, not *Fixes*. An issue should
  be closed by someone who can confirm the whole of it is resolved.

Full merge record, evidence standard and scope boundaries:
[`docs/contributions/STATUS.md`](docs/contributions/STATUS.md).
Hardware-test results: [`docs/MT55_VERIFICATION.md`](docs/MT55_VERIFICATION.md).

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
