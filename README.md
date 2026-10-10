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

**22 pull requests merged into Gadgetbridge, 4 open**, totalling
**+4822 / −204** lines across the merged set. All merged by maintainer
`joserebelo`. These figures are a snapshot taken from the Codeberg API on 10 October 2026,
not a running total — the authoritative list is
[every pull request by `oddballza`](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls?state=all&poster=1443751).

### Merged

| PR | Merged | What | Diff | Merge commit |
|---|---|---|---|---|
| [#6688](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688) | 2026-09-02 | Moyoung: add MT55 support | +84 / −0 | [`8305c4b7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/8305c4b7b0a62e9d334842a55584bfb7701e7d1b) |
| [#6690](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6690) | 2026-09-02 | Moyoung: detect charging from battery level > 100 | +10 / −3 | [`bb5fcf9d`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bb5fcf9d32a229e50d3a9788599f0d09ce573d82) |
| [#6691](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691) | 2026-09-02 | Moyoung: lower sleep-overlay log level to debug | +1 / −1 | [`1506767f`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/1506767f6a7077dc0ee73020399ec5dbcb59f10b) |
| [#6705](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6705) | 2026-09-05 | Dashboard: SpO2 widget | +154 / −0 | [`b9bee0a7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/b9bee0a7098365a612c59fa780666f148b90bbe8) |
| [#6704](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6704) | 2026-09-06 | Dashboard: empty state for the sleep score widget | +67 / −2 | [`45dfd4e7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/45dfd4e7f6aba3c9efff5ae782c87abd4a19a1ed) |
| [#6706](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6706) | 2026-09-07 | Dashboard: weight widget | +178 / −0 | [`c1d20c6a`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/c1d20c6a861540eec5d3534bb741b5234b5ac4e5) |
| [#6708](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6708) | 2026-09-07 | Dashboard: BMI widget | +316 / −0 | [`2e93e43b`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/2e93e43b38c2e761455ec6f394425bd723724948) |
| [#6694](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6694) | 2026-09-07 | Scales: store bio-impedance and estimate body composition | +1011 / −77 | [`00545e25`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/00545e25fb5f35050a3eb0268c16aedce6cb0626) |
| [#6728](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6728) | 2026-09-08 | Mi scales: refresh the dashboard after a measurement | +4 / −0 | [`bef7dcf0`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bef7dcf0df72f21ffc03616b00aa390dbfa9c0e1) |
| [#6709](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6709) | 2026-09-09 | Moyoung: measure blood oxygen on demand from the device card | +100 / −4 | [`3987f4e3`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/3987f4e34f18548d23a829db73b99a5e1a7a7f2a) |
| [#6739](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6739) | 2026-09-10 | Moyoung: refresh the dashboard after a blood oxygen measurement | +84 / −0 | [`78102b60`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/78102b6065533ab2195575c6076d1ebd26b483cd) |
| [#6710](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6710) | 2026-09-15 | Moyoung: read the battery level from the raw byte so charging is detected | +98 / −8 | [`a3f2fa03`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/a3f2fa03a66f70241ad08c50b224080732be13f9) |
| [#6703](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6703) | 2026-09-15 | Weight chart: show BMI | +117 / −19 | [`08f202e5`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/08f202e5f5a9782aabf4c2e85f3dcdd7a2fedf68) |
| [#6707](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6707) | 2026-09-16 | Dashboard: heart rate widget | +213 / −0 | [`d37370d7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/d37370d703caa3e744d3232e974faa4f4194e1ae) |
| [#6794](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6794) | 2026-09-19 | Logging: roll over a log left from an earlier day on start | +35 / −1 | [`3149dcb9`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/3149dcb9b0b9a73eb9d836fa5cee346332296e85) |
| [#6791](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6791) | 2026-09-20 | Add GenericImpedanceSample for scales that report more than one impedance reading | +153 / −1 | [`3c42da18`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/3c42da187a55d53f21e8648cbfced5b74db033de) |
| [#6805](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6805) | 2026-09-23 | Add support for the Sennheiser MOMENTUM In-Ear Wireless | +800 / −0 | [`dc8ee082`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/dc8ee08200706279c2bab43bfef7453a449de1aa) |
| [#6695](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6695) | 2026-09-23 | Add support for the LeFu "Health Scale" (1byone, Veeway and other rebrands) | +450 / −0 | [`9f78215d`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/9f78215d1ce0be5e1a6cef89a55768b99072dcff) |
| [#6777](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6777) | 2026-09-23 | Xiaomi: convert the reported heart rate interval to seconds | +228 / −1 | [`33493b92`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/33493b9214d69a1ea1ae9b53dcfef886979a09aa) |
| [#6726](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6726) | 2026-09-23 | Dashboard: body fat, body water, muscle mass and BMR widgets | +452 / −81 | [`75f92390`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/75f923904f8504b03fabdee0987fd1c269a92278) |
| [#6793](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6793) | 2026-09-23 | Generic headphones: only show connected while the headphones are | +207 / −5 | [`188e2ea9`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/188e2ea9319cd3d2ce1b8f2382f031ad99919dfc) |
| [#6846](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6846) | 2026-09-25 | Moyoung: take the end minute of a time range from the end of the range | +60 / −1 | [`e48504f0`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/e48504f0d01defe0f481ace5c2c4327669e2f0c3) |

**MT55 is officially supported in Gadgetbridge.** `MT55Coordinator.java` is in upstream
`master` carrying `Copyright (C) 2026 oddballza` — verify at
[`devices/moyoung/MT55Coordinator.java`](https://codeberg.org/Freeyourgadget/Gadgetbridge/src/branch/master/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/devices/moyoung/MT55Coordinator.java).
Two of the first three changes fix pre-existing defects reported by other users, in code
shared by every Moyoung device. Later changes added two new devices (LeFu Health Scale,
Sennheiser MOMENTUM In-Ear Wireless), bio-impedance storage with body-composition
estimates, eight dashboard widgets, and fixes in Xiaomi, generic-headphones and logging
code.

### Open

| PR | What | Diff | State |
|---|---|---|---|
| [#6698](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6698) | Support device supports that consume BLE advertisements | +372 / −7 | In review since 7 Sep. Maintainer's one review point (struct creation racing like the old BLE connect path) answered by delivering only to devices that already have a struct; a test class covers it. Rebased onto `master` on 2 and 7 Oct for conflicts. Exercised daily on S400 hardware by a tester since 25 Sep. |
| [#6911](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6911) | Xiaomi Body Composition Scale S400 | +2193 / −7 | Draft, stacked on #6698 — the first device that consumes advertisements without connecting. |
| [#6845](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6845) | Moyoung: stop querying the do not disturb toggle with the time range command | +73 / −1 | Fix for issue #6689. One maintainer review comment on 24 Sep, answered the same day with hardware captures of the 4-byte payload. Description wording still to be corrected. |
| [#6856](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6856) | GbLineChart: optional points, value labels, curves, axis step and a pinned marker | +97 / −5 | Overtaken. On 8 Oct the maintainers paused it while reconsidering the Vico migration; on 10 Oct it was called "heavily superseded" by [#7004](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/7004), the GbChartView migration, which has since merged. Expect it to close without merging. |

### Issues

- **[#6689](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689)** — clean-room report root-causing a DND on/off parse
  error in shared Moyoung code. Originally left open by intent because choosing between
  two candidate fixes needed cross-model behaviour one device could not establish. Hardware
  captures later settled it, and the fix is now up as #6845. Open until that merges.
- **[#5236](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5236)** — battery reported as 100 % while charging. Addressed by
  #6690 and properly fixed by #6710. Closed on 30 Sep after a user confirmed the nightly.
- **[#5859](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5859)** — Moyoung log spam. #6691 is referenced as *Addresses*,
  not *Fixes*, because the issue also covers duplicate notifications. Still open.

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
