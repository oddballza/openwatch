# OpenWatch — Phase 1 (Reconnaissance)

## What this is

This began as reconnaissance on one undocumented smartwatch. It ended somewhere wider,
and that widening is the point of the repository rather than an accident of it.

The investigation established that the MT55 spoke a protocol Gadgetbridge already
implemented in full, 82 commands deep. The only real gap was device identification — MT55
matched 0 of 412 name patterns in the codebase. The engineering problem was 84 lines, not
an Android app, and the contribution went upstream rather than into a private fork.

Reading a codebase closely enough to add one device turns up what else is wrong with it.
The changes that followed reach beyond the MT55 into shared Moyoung code, Xiaomi scale
drivers, bio-impedance storage, dashboard widgets and a core framework change for devices
that never connect at all.

So this repository holds two things: the original protocol research — ADR-001 with options
A–D, an AGPL-3.0 code-origin audit, seven rootless BLE diagnostic tools, literal tool
output behind every device claim — and the verified record of what came out of it.

## Upstream contributions

**14 pull requests merged into Gadgetbridge, 3 open**, totalling
**+2437 / −114** lines across the merged set. All merged by maintainer
`joserebelo`. These figures are a dated snapshot, not a running total — the authoritative
list is [every pull request by `oddballza`](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls?state=all&poster=1443751).

### Merged

| PR | Merged | What | Diff | Merge commit |
|---|---|---|---|---|
| [#6688](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688) | 2026-09-02 | Moyoung: add MT55 support | +84 / −0 | [`8305c4b7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/8305c4b7b0a62e9d334842a55584bfb7701e7d1b) |
| [#6690](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6690) | 2026-09-02 | Moyoung: detect charging from battery level > 100 | +10 / −3 | [`bb5fcf9d`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bb5fcf9d32a229e50d3a9788599f0d09ce573d82) |
| [#6691](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691) | 2026-09-02 | Moyoung: lower sleep-overlay log level to debug | +1 / −1 | [`1506767f`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/1506767f6a7077dc0ee73020399ec5dbcb59f10b) |
| [#6705](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6705) | 2026-09-05 | Dashboard: SpO2 widget | +154 / −0 | [`b9bee0a7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/b9bee0a7098365a612c59fa780666f148b90bbe8) |
| [#6704](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6704) | 2026-09-06 | Dashboard: empty state for the sleep score widget | +67 / −2 | [`45dfd4e7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/45dfd4e7f6aba3c9efff5ae782c87abd4a19a1ed) |
| [#6694](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6694) | 2026-09-07 | Scales: store bio-impedance and estimate body composition | +1011 / −77 | [`00545e25`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/00545e25fb5f35050a3eb0268c16aedce6cb0626) |
| [#6706](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6706) | 2026-09-07 | Dashboard: weight widget | +178 / −0 | [`c1d20c6a`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/c1d20c6a861540eec5d3534bb741b5234b5ac4e5) |
| [#6708](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6708) | 2026-09-07 | Dashboard: BMI widget | +316 / −0 | [`2e93e43b`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/2e93e43b38c2e761455ec6f394425bd723724948) |
| [#6728](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6728) | 2026-09-08 | Mi scales: refresh the dashboard after a measurement | +4 / −0 | [`bef7dcf0`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bef7dcf0df72f21ffc03616b00aa390dbfa9c0e1) |
| [#6709](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6709) | 2026-09-09 | Moyoung: measure blood oxygen on demand from the device card | +100 / −4 | [`3987f4e3`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/3987f4e34f18548d23a829db73b99a5e1a7a7f2a) |
| [#6739](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6739) | 2026-09-10 | Moyoung: refresh the dashboard after a blood oxygen measurement | +84 / −0 | [`78102b60`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/78102b6065533ab2195575c6076d1ebd26b483cd) |
| [#6703](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6703) | 2026-09-15 | Weight chart: show BMI | +117 / −19 | [`08f202e5`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/08f202e5f5a9782aabf4c2e85f3dcdd7a2fedf68) |
| [#6710](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6710) | 2026-09-15 | Moyoung: read the battery level from the raw byte so charging is detected | +98 / −8 | [`a3f2fa03`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/a3f2fa03a66f70241ad08c50b224080732be13f9) |
| [#6707](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6707) | 2026-09-16 | Dashboard: heart rate widget | +213 / −0 | [`d37370d7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/d37370d703caa3e744d3232e974faa4f4194e1ae) |

**MT55 is officially supported in Gadgetbridge.** `MT55Coordinator.java` is in upstream
`master` carrying `Copyright (C) 2026 oddballza` — verify at
[`devices/moyoung/MT55Coordinator.java`](https://codeberg.org/Freeyourgadget/Gadgetbridge/src/branch/master/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/devices/moyoung/MT55Coordinator.java).
Two of the first three changes fix pre-existing defects reported by other users, in code
shared by every Moyoung device.

### Open, in review

| PR | What | Diff |
|---|---|---|
| [#6695](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6695) | Add support for the LeFu "Health Scale" (1byone, Veeway and other rebrands) | +450 / −0 |
| [#6698](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6698) | Support device supports that consume BLE advertisements | +168 / −6 |
| [#6726](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6726) | Dashboard: body fat, body water, muscle mass and BMR widgets | +533 / −64 |

### Left open by intent

- **[Issue #6689](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689)** — clean-room report root-causing a DND on/off parse
  error in shared Moyoung code. Two candidate fixes offered and neither chosen: deciding
  between them needs cross-model behaviour that one device cannot establish, so it is
  deferred to the maintainers with an offer to test whatever they choose.
- **Issues #5236 and #5859** are referenced as *Addresses*, not *Fixes*. An issue should
  be closed by someone who can confirm the whole of it is resolved.

Full merge record, evidence standard and scope boundaries:
[`docs/contributions/STATUS.md`](docs/contributions/STATUS.md).
Hardware-test results: [`docs/MT55_VERIFICATION.md`](docs/MT55_VERIFICATION.md).

## Protocol research

| Document | Contents |
|---|---|
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | Alternatives, device identification, gap analysis, recommendation, firmware |
| [`docs/GADGETBRIDGE_ANALYSIS.md`](docs/GADGETBRIDGE_ANALYSIS.md) | Upstream architecture map, matching logic, compatibility matrix, limitations |
| [`docs/ARCHITECTURE_DECISION.md`](docs/ARCHITECTURE_DECISION.md) | ADR-001: options A–D and why B was chosen |
| [`docs/LICENSING.md`](docs/LICENSING.md) | AGPL-3.0 analysis and code-origin audit |
| [`docs/evidence/mt55-recon.md`](docs/evidence/mt55-recon.md) | Literal tool output backing every device claim |

### Device summary

| | |
|---|---|
| Name / MAC | `MT55` / MAC redacted (declared public) |
| Manufacturer (DIS) | `MOYOUNG-V2` |
| Software / Firmware | `MOY-JSB2-2.0.4` / `JLQFNJEJ1.1` |
| Protocol | Moyoung V2 (MTU-based framing) |
| Verified live | Battery 48 %; steps 790 / 655 m / 42 kcal |
| Not supported | ECG (`FEE7`/`FEE8` characteristics absent) |

## Tooling

Vendor-neutral BLE diagnostics used to produce the evidence — reusable for the next
unlisted watch. Requires BlueZ and `python3-dbus`; no root needed for enumeration.

```sh
python3 tools/scan_debug.py   # LE discovery (note: needs a Transport=le filter)
python3 tools/full_gatt.py    # connect + full GATT enumeration + DIS reads
python3 tools/read_vals.py    # battery + steps + vendor characteristic reads
```
