# Upstream contribution status

Every claim below is checkable against the Gadgetbridge repository on Codeberg. Merge
commit SHAs are given so the record can be verified without taking this file's word for
it.

Upstream: [`Freeyourgadget/Gadgetbridge`](https://codeberg.org/Freeyourgadget/Gadgetbridge)
· Verified against `master`, 8 September 2026.

## Merged

| PR | What | Diff | Merged | Merge commit |
|---|---|---|---|---|
| [#6688](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688) | `MT55Coordinator` — new device support | +84 / −0, 3 files | 2026-09-02 00:16 | [`8305c4b7`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/8305c4b7b0a62e9d334842a55584bfb7701e7d1b) |
| [#6690](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6690) | Detect charging from battery level > 100 — **shared Moyoung code** | +10 / −3, 1 file | 2026-09-02 00:16 | [`bb5fcf9d`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/bb5fcf9d32a2) |
| [#6691](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6691) | Lower sleep-overlay log level to debug — **shared Moyoung code** | +1 / −1, 1 file | 2026-09-02 00:17 | [`1506767f`](https://codeberg.org/Freeyourgadget/Gadgetbridge/commit/1506767f6a70) |

All three merged by maintainer `joserebelo`. Labels applied upstream: `device moyoung`,
`new device`.

**Two of the three fix pre-existing defects reported by other users**, in code shared by
every Moyoung device — not only the MT55.

## Open by intent

| Ref | What | Why it is open |
|---|---|---|
| [#6689](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689) | DND on/off parse error — root-caused in shared code | Reported, not fixed. Two candidate fixes offered; choosing between them needs cross-model behaviour I cannot test with one device. Deferred to maintainers, with an offer to test any proposed change on MT55. |
| [#5236](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5236) | Battery reporting | PR #6690 **addresses** it. Left open deliberately — the issue has aspects beyond this change. |
| [#5859](https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5859) | Moyoung log spam | PR #6691 **addresses** it. Same reasoning. |

Referencing issues as *Addresses* rather than *Fixes* is deliberate: an issue should be
closed by the person who can confirm the whole of it is resolved, and that is not me.

## The code in upstream today

`MT55Coordinator.java` is present in `master`:

```
app/src/main/java/nodomain/freeyourgadget/gadgetbridge/devices/moyoung/MT55Coordinator.java
```

```java
/*  Copyright (C) 2026 oddballza
 *
 *  This file is part of Gadgetbridge.
 *  ... AGPL-3.0-or-later ...
 */
```

Also modified upstream by these contributions:

- `.../model/DeviceType.java` — device registration
- `.../res/values/strings.xml` — device name string
- `.../service/devices/moyoung/MoyoungDeviceSupport.java` — charging detection
- `.../devices/moyoung/samples/MoyoungActivitySampleProvider.java` — log level

## Evidence standard applied

- **Only hardware-confirmed capabilities were declared.** `MT55Coordinator` claims
  battery, steps, distance, sleep with REM staging, workouts and live heart rate because
  each was observed on the device. ECG was *not* claimed — the `FEE7`/`FEE8`
  characteristics are absent. See [`docs/MT55_VERIFICATION.md`](../MT55_VERIFICATION.md).
- **Defect reports carry reproduction counts, not impressions.** #6690 quantified the
  fault as a 146% battery display with the raw values behind it; #6691 recorded 208
  occurrences of the warning in roughly two minutes of normal chart navigation.
- **An operational caveat was volunteered unprompted.** The MT55 is dual-mode
  (BR/EDR + LE) and must be paired inside Gadgetbridge only — pairing through Android
  system Bluetooth causes A2DP/GATT contention that stalls the activity fetch. This is
  in the PR body so the maintainers never field it as a bug report.
- **Clean-room throughout.** Device behaviour was established from observation of
  hardware and the vendor's own advertised/GATT data, not from decompiled vendor code.
  See [`docs/LICENSING.md`](../LICENSING.md) for the AGPL-3.0 analysis and code-origin
  audit.
- **Authorship and disclosure.** All commits authored as `oddballza`, with no AI
  attribution in commit metadata; the PR and issue text carried the upstream-required AI
  disclosure alongside the clean-room statement.

## Out of scope — documented, not submitted

- **Watchface upload.** Derived from decompilation, therefore private-use only. It is
  not offered upstream and no part of it appears in the merged code.
- **A *fix* for the DND on/off defect.** The semantics belong to shared code across
  models I cannot test. Reported as #6689 instead.
