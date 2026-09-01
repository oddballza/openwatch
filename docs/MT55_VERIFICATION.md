# MT55 — on-device verification in Gadgetbridge

Built Gadgetbridge (mainline debug, v0.93.0) with the `MT55Coordinator` from
`patches/0001-moyoung-add-mt55-support.patch`, installed on an Android 13 phone,
and paired the real watch. This records what was confirmed against hardware, so
the upstream contribution claims only what actually works.

All identifiers redacted; observations are from the paired author's own device.

## Confirmed working (personal observation, GB's own Moyoung stack)

| Capability | Evidence |
|---|---|
| Device match by name `^MT55$` | Card shows "MT55", not "unknown" — coordinator regex matched |
| Connect (BLE, via GB) | Card "Connected"; no vendor app needed |
| Battery | Live level shown (e.g. 46%), `0x2A19` notify |
| Steps history | Fetch completed 3/3 packets; today decoded 790 steps / 655 m / 42 kcal |
| Sleep history + stages | Fetch completed 3/3 packets; light/deep/REM segments decoded |
| Workouts (V2) | `FetchWorkoutsV2Operation` decoded list + details + HR packets |
| Stress | `fetchStress` transaction ran during sync |
| Settings surface | Language, Generic (watch face, time format, DND, world clocks, camera, calendar), Health (whole-day HR, inactivity), Connection all present |
| Full sync completes | "Mark device as NOT busy anymore: Fetching activity data" |

## Known issue — do NOT system-pair (important)

MT55 advertises as **dual-mode (BR/EDR + LE)**. If Android bonds it in system
Bluetooth settings, it is treated as an **audio device**: the A2DP state machine
repeatedly attempts to connect and Google Play Services registers a competing
GATT client. The watch accepts only one central, so this contention **stalls
Gadgetbridge's activity fetch** (card stuck on "Fetching activity data").

**Fix:** forget MT55 in Android system Bluetooth; pair only within Gadgetbridge.
After removing the system bond, sync completes reliably. This should be a
"Known issues" note on the device's docs page, like other Moyoung watches.

## Not independently confirmed

* **Heart-rate history / streaming** — the coordinator sets these true (as L70
  does). The sync completes without stalling with them enabled, but no HR-history
  packets were observed in the fetch log, so this is inferred, not proven. To be
  verified with a live HR measurement before claiming in the PR, or dropped to
  the conservative default.
* Alarm slot count (8), world-clock slot count (6) — the settings screens exist,
  but exact counts were not exercised.

## Consequence for the coordinator

The core capabilities are verified. Before submitting upstream, either verify the
HR flags with a live measurement or trim them to the `AbstractMoyoungDeviceCoordinator`
defaults, so the contribution claims nothing unproven. Add the system-pairing
known issue to the device notes.

## Full dashboard-tile audit (2026-09-01)

Went through Gadgetbridge's dashboard tiles on the paired watch. Categorised:

### Working / data confirmed
* Battery, Steps (790), Distance (592 m), Total calories (42 kcal — in steps packet)
* Sleep with stages incl. REM (9h 57m)
* Heart rate (86 shown on card)
* Workouts (training data decoded)

### Supported, but manual / needs enabling before data appears
* **SpO2** — inherited `supportsSpo2()==true`; it is a *manual* measurement
  (`CMD_TRIGGER_MEASURE_BLOOD_OXYGEN`), so the tile is empty until one is taken.
* **Blood pressure** — same pattern (manual).
* **Stress** — `fetchStress` runs but the watch returned **no samples**; likely
  stress monitoring is disabled on the watch (as "Whole day HR" was Off). Enable
  on-watch, wear, re-sync to confirm before claiming.
* **Whole-day HR** — was Off in Health settings; enable for continuous HR history.

### Correctly UNSUPPORTED — Moyoung protocol / hardware limits (do not flag)
* **Body Energy / Body Battery** — no HRV source in the protocol.
* **HRV** — protocol carries no RR-interval data.
* **VO2 max** — not in GB's Moyoung stack; the watch does **SpO2, not VO2max**.
* **Active calories** — Moyoung reports total calories only (mapped
  `activeCalories=-1`), not the active/resting split the tile needs.

`supportsBodyEnergy`, `supportsVO2Max`, HRV all default false and are overridden
only by Garmin/Xiaomi — never by Moyoung. Leaving them off is correct.

## "Test new function" = QuerySettingsOperation (read-only) — results

The device-card overflow "Test new function" runs `MoyoungDeviceSupport.onTestNewFunction()`,
which is `QuerySettingsOperation` — a **read-only** settings dump. Confirmed values:

```
GOAL_STEP = 8000            HR_AUTO_INTERVAL = 6        DEVICE_VERSION = INTERNATIONAL_EDITION
DEVICE_LANGUAGE = ENGLISH   TIME_SYSTEM_24             METRIC_SYSTEM
DISPLAY_WATCH_FACE = 9      OTHER_MESSAGE_STATE = false QUICK_VIEW = true (06:00-21:00)
SEDENTARY_REMINDER = false  REMINDERS_TO_MOVE{60min,50 steps,10-22}
DO_NOT_DISTURB_TIME = 21:00-06:00
Supported languages: EN, ZH, JA, DE, FR, ES, AR, RU, UK, IT, PT, PL, DA, RO
```

(`DISPLAY_WATCH_FACE = 9` also independently confirms the earlier face restore.)

## BUG FOUND: DO_NOT_DISTURB_ONOFF parse error (shared Moyoung code)

```
Parse error for DO_NOT_DISTURB_ONOFF:
  IllegalArgumentException: Wrong data length, should be 1, was 4
  at MoyoungSettingBool.decode(MoyoungSettingBool.java:32)
```

Root cause (in upstream shared code, not MT55-specific):

* `AbstractMoyoungDeviceCoordinator` line 217-218 maps **both**
  `DO_NOT_DISTURB_TIME` (a `MoyoungSettingTimeRange`) **and**
  `DO_NOT_DISTURB_ONOFF` (a `MoyoungSettingBool`) to the **same** query command
  `CMD_QUERY_DO_NOT_DISTURB_TIME` (-127).
* That command's only response is the 4-byte time range (documented in
  `MoyoungConstants`). The `TimeRange` decoder handles it; the `Bool` decoder
  receives the same 4 bytes and throws (it demands exactly 1).
* There is **no** separate DND on/off command in `MoyoungConstants` — DND state
  appears to be defined solely by the time window.

Impact: non-fatal (caught + logged), but DND on/off never reads correctly, and
the log fills with stack traces on every settings query.

**This is a candidate for a SECOND, separate contribution** — but it edits shared
Moyoung code, so it must be raised with the maintainers (correct semantics of DND
on/off across models) rather than patched blindly in the MT55 PR. Discovered via
clean-room observation (own device logcat); no decompilation involved.

## Google Fit / Health Connect (corrected)

Health Connect (`com.google.android.apps.healthdata`), Google Fit and Fitbit are
all installed on the test phone. GB syncs to Health Connect (steps, distance, HR,
resting HR, sleep, SpO2, active calories, workouts, weight, +others); Google Fit
etc. read from Health Connect. Only data types MT55 produces will flow. GB feeds
Health Connect via local IPC — no INTERNET permission needed (the build only holds
the custom `internethelper.INTERNET` permission; weather would need the Internet
Helper app).

## Latent-capability sweep (read-only QUERY probe, 2026-09-01)

Swept the `CMD_QUERY_*` opcodes Gadgetbridge does not currently expose, using
`tools/moyoung_probe.py` (read-only; QUERY commands only). Responses on FEE3:

| Opcode | Feature | Result |
|---|---|---|
| 36 DOMINANT_HAND | `24 01` (value 1) | **Supported** — GB has this setting commented out in AbstractMoyoungDeviceCoordinator |
| 89 STEPS_CATEGORY | 54-byte data packet | **Supported** — not exposed by GB |
| 0xA4 POWER_SAVING | `a4 00 01` | **Supported** |
| 0x85 PSYCHOLOGICAL_PERIOD | 20-byte data packet | **Supported — women's cycle tracking**, listed "unsupported" on gadgetbridge.org |
| 0x88 BREATHING_LIGHT | echo, empty payload | Ambiguous (ack, no data) |
| 0x84 SUPPORT_WATCH_FACE | echo, empty | No face count (consistent w/ earlier) |
| 52, 58, 37, 55 | none | No response → unsupported / no data |

These are clean-room discoveries (own-device probing, no decompilation). They are
**potential future contributions**, distinct from the MT55 coordinator PR:
* DOMINANT_HAND — GB already defines the setting (commented out); MT55 answers it.
* Cycle tracking / STEPS_CATEGORY — not implemented in GB at all; would need new
  data models and maintainer discussion (cycle tracking is a large feature).

None change the **verified-only** coordinator's capability flags — they are
settings/features, not the supportsX flags. Recorded for follow-up.

## Upstream contribution status (2026-09-01)

**PR #6688 — MT55 coordinator:** https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688
Open; triaged by maintainers (labels: `device moyoung`, `new device`).
Review round 1 (joserebelo): "do not modify changelog_master.xml" — addressed by
removing the changelog hunk and force-pushing. PR now touches only
`MT55Coordinator.java`, `DeviceType.java`, `strings.xml`. Still mergeable.

**Issue #6689 — DND on/off parse bug:** https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689
Open; triaged by joserebelo (label: `device moyoung`). Clean-room bug report;
fix deferred to maintainers (shared code); offered to test on MT55.

---

## Upstream contribution submitted (2026-09-01)

Pushed the **verified-only** MT55 coordinator to the fork
`oddballza/Gadgetbridge`, branch `mt55-support`, based on current upstream
master. Compiles clean. Submitted as PR #6688:
https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/6688
(Status at submission: open, CI mergeable, auto-labeled "device moyoung", 1 commit / 4 files / +85.)

Coordinator declares only hardware-confirmed capabilities:
`^MT55$`, MTU 508, `supportsRemSleep`, `supportsHeartRateStreaming`.
Dropped (unproven): stress, HR-history, alarm-slot count, world-clock count.

Deliberately excluded from this PR (kept for separate work):
* Watchface layout/upload protocol (decompilation-derived — not clean-room).
* DND on/off parse bug (shared code — needs maintainer discussion).
* Latent capabilities: cycle tracking, dominant-hand, steps-category.

## Battery charging encoding (clean-room finding, 2026-09-01)

Investigated open issue #5236 ("battery misreported while charging") with MT55.
Standard Battery Level `0x2A19`, own-device reads:

| State | Raw | Level |
|---|---|---|
| Not charging | `0x2d`=45, `0x3c`=60 | 45%, 60% |
| Charging | `0x92`=146, `0x93`=147 (rising) | 46%, 47% **+100 offset** |

**Finding:** MT55 encodes charging by **adding 100** to the battery byte
(raw >100 = charging; actual level = raw − 100; ≤100 = not charging). GB shows the
raw >100 value and always sets `BATTERY_NORMAL` (Moyoung protocol has no charging
flag; `handleBatteryInfo` doesn't derive one).

Distinct from the issue's Colmi V72 (flat 100% while charging) → behaviour is
firmware-specific. Posted as a data point + possible fix (treat >100 as charging,
subtract 100) on issue #5236:
https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/5236 — deferred to
maintainers since it varies by firmware.
