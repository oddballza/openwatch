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
