# Gadgetbridge — Moyoung implementation analysis

Upstream commit analysed: `1b7ad478656fbce7ff76a330a4a0f9cf25b05eef` (2026-09-01),
`https://codeberg.org/Freeyourgadget/Gadgetbridge`. License: **AGPL-3.0**.

Paths below are relative to `app/src/main/java/nodomain/freeyourgadget/gadgetbridge/`.

## 1. Architecture map

```
                       ┌──────────────────────────────────────────┐
  BLE advertisement    │ DiscoveryActivityV2                      │
        name  ────────►│   → DeviceCoordinator.supports(candidate)│
                       │      == name regex match ONLY            │
                       └────────────────┬─────────────────────────┘
                                        │ selects
                       ┌────────────────▼─────────────────────────┐
   devices/moyoung/    │ <Model>Coordinator                       │
                       │   getSupportedDeviceName() : Pattern     │
                       │   getMtu() : int                         │
                       │   extends AbstractMoyoungDeviceCoordinator│
                       │     ├ capability flags (supportsX)       │
                       │     ├ settings screens                   │
                       │     └ sample DAO wiring                  │
                       └────────────────┬─────────────────────────┘
                                        │ instantiates
  service/devices/     ┌────────────────▼─────────────────────────┐
        moyoung/       │ MoyoungDeviceSupport                     │
                       │   ├ MoyoungPacketOut.buildPacket()       │
                       │   ├ MoyoungPacketIn.putFragment/parse    │
                       │   ├ FetchDataOperation        (history)  │
                       │   ├ FetchWorkoutsV2Operation   (V2)      │
                       │   ├ QuerySettingsOperation               │
                       │   └ TrainingFinishedDataOperation        │
                       └────────────────┬─────────────────────────┘
                                        │ GATT
                       ┌────────────────▼─────────────────────────┐
                       │ 0xFEEA  FEE1 steps / FEE2 out / FEE3 in  │
                       │ 0x180F battery, 0x180D HR, 0x180A DIS    │
                       └──────────────────────────────────────────┘
```

## 2. Device identification logic — the critical path

`devices/AbstractDeviceCoordinator.java:136-151`:

```java
@Nullable
protected Pattern getSupportedDeviceName() { return null; }

@Override
public boolean supports(@NonNull GBDeviceCandidate candidate) {
    if (supportedDeviceName == null) supportedDeviceName = getSupportedDeviceName();
    if (supportedDeviceName == null) { /* log error */ return false; }
    return supportedDeviceName.matcher(candidate.getName()).matches();
}
```

**This is the entire matching mechanism.** No coordinator in the Moyoung family
overrides `supports()`. Consequences:

* The advertised `0xFEEA` service UUID is **never consulted** for matching.
* The `MOYOUNG-V2` DIS string is **never consulted** for matching (it is only read
  *after* connection, to pick packet framing).
* Therefore an unlisted-but-fully-compatible watch is unpairable by normal means.

I verified this empirically: extracted all `Pattern.compile("…")` literals from
every `getSupportedDeviceName()` in the repository (**412 distinct patterns**) and
regex-matched the string `MT55` against all of them. **Zero matches.**

The 23 Moyoung patterns are all exact model names:

```
^Alt Vibe$   ^C17$    ^C *20$   ^C29$    ^FireBoltt 080$   ^HC96$
^i28 Ultra$  ^iTECH Active 3$   ^KSIX VENTURE$   ^KT80$    ^L *70$
^P22B1       ^P76J$   ^P80$     ^R50Pro$ ^R60$    ^SE1$    ^T97$
^V72$        ^V73$    ^V76$     V89\.?   ^ZL02D$
```

### The escape hatch

`res/values/strings.xml:2851-2852` — *"Discover unsupported devices … Long press
will launch 'Add test device' dialog."*

`util/DeviceTypeDialog.kt` lets the user enter a **MAC address** and pick **any**
`DeviceType`, then at lines 300-315:

```kotlin
val gbDevice = GBDevice(deviceMac, deviceName, "", null, deviceType)
gbDevice.setState(GBDevice.State.INITIALIZED)
DBHelper.getDevice(gbDevice, daoSession)   // the addition happens here
```

This persists a **real** device row — not a simulated one. `TestDeviceCoordinator`
itself returns `supports() == false` and is unrelated. So binding `MT55`'s MAC to,
say, `COLMI_V89` yields a genuine Moyoung V2 connection attempt. This is the
no-code workaround, and it is the recommended first step.

## 3. Protocol implementation

**Framing** (`devices/moyoung/MoyoungConstants.java:44-58`) — 5-byte header
`FE EA <len_hi|flag> <len_lo> <type>` then payload; fragmented to MTU-sized writes
on `FEE2`, reassembled from notifies on `FEE3` by `MoyoungPacketIn.putFragment()`.

**Version selection** (`MoyoungConstants.java:60-62`) — reads DIS manufacturer name:
`MOYOUNG` → V1 fixed-size (256 bytes for fw >= 1.6.5 else 64); `MOYOUNG-V2` → MTU-based.
Firmware version additionally gates individual features.

**Command surface** — `MoyoungConstants.java` defines **82** `CMD_*` opcodes.

**Standard services used alongside the proprietary one** (`MoyoungConstants.java:76-100`):
`0x180A` DIS, `0x180F` battery, `0x180D` HR (upstream comment: *"exposed, but doesn't
seem to work"*), plus custom `FEE1` for real-time pedometer.

Internal pseudo-packet numbers for the standard services: `16` steps, `17` firmware
version, `18` battery, `19` DFU status (reads Model Number, looks for `"DFU"`),
`20` protocol version (reads manufacturer name).

> **MT55 note:** Model Number `0x2A24` is **absent** on this watch, so probe `19`
> cannot resolve. This is a plausible source of a benign warning, not a blocker —
> DFU/flashing is not a feature we need.

## 4. Device compatibility matrix

Gadgetbridge support is read from source. "Likely MT55 support" is from the observed
GATT database and V2 protocol level; *(unverified)* = needs a real pairing session.

| Capability | Gadgetbridge support | Likely watch support | Notes |
|---|---|---|---|
| Pairing / connect | Yes | **Blocked** | Protocol fine; name `MT55` matches no regex. Workaround §2 |
| Battery | Yes — `0x180F` + `batteryInfoProfile` | **Verified — 48 %** | `0x2A19` = `0x30` |
| Steps (realtime) | Yes — notify on `FEE1`, `handleStepsHistory(…, true)` | **Verified — 790** | 9-byte payload decoded correctly |
| Steps (history) | Yes — `FetchDataOperation` | Yes *(unverified)* | |
| Heart rate (manual) | Yes | Yes *(unverified)* | |
| Heart rate (live) | Yes — `supportsHeartRateStreaming()` | Yes *(unverified)* | Upstream notes standard `0x180D` is unreliable on these watches |
| Heart rate (history) | Yes — `supportsHeartRateHistory()` | Yes *(unverified)* | |
| Sleep history | Yes — `FetchDataOperation.decodeSleep()` | Yes *(unverified)* | |
| Stress | Yes | Yes *(unverified)* | |
| SpO2 (manual) | Yes | Yes *(unverified)* | |
| Blood pressure (manual) | Yes | Yes *(unverified)* | |
| Workouts V1 | Yes — `TrainingFinishedDataOperation` | Yes *(unverified)* | |
| Workouts V2 | Yes — `FetchWorkoutsV2Operation` | Likely *(unverified)* | Device is V2 |
| Weather + forecast | Yes — `MoyoungWeatherToday/Forecast` | Yes *(unverified)* | |
| Music control + info | Yes — `supportsMusicInfo()` | Yes *(unverified)* | |
| Notifications | Yes | Yes *(unverified)* | |
| Phone calls | Yes | Yes *(unverified)* | |
| Calendar | Yes — `supportsCalendarEvents()` | Yes *(unverified)* | |
| Alarms | Yes — `getAlarmSlotCount()`, `CMD_QUERY_ALARM_CLOCK` | Yes *(unverified)* | Slot count is per-coordinator |
| World clocks | Yes — `getWorldClocksSlotCount()` | Yes *(unverified)* | |
| Find watch / find phone | Yes — `supportsFindDevice()` | Yes *(unverified)* | |
| Camera trigger | Yes | Yes *(unverified)* | |
| Watch faces | Yes | Yes *(unverified)* | Model-dependent |
| DND / low power / inactivity | Yes — `QuerySettingsOperation` | Yes *(unverified)* | |
| Language, time format, HR interval | Yes | Yes *(unverified)* | |
| **ECG** | Yes — `FEE7`/`FEE8` ECG channels | **No** | Those characteristics are **absent** on MT55 |
| **Firmware flashing** | **No** | n/a | Not implemented for Moyoung; MT55 uses vendor OTA `0xAE00` |
| Data export | Yes — DB export, GPX/FIT | n/a | App-level |

## 5. Known limitations

* **Name-only device matching** — the root cause of this whole investigation, and a
  genuine upstream design weakness for an ODM ecosystem with hundreds of rebrands.
* **No Moyoung firmware update support.**
* Documented unsupported vendor features: stock market data, "Da GPT",
  cycle tracking, always-on-display settings.
* Standard HR service `0x180D` is present but unreliable per upstream's own comment.
* Stale comment in `MoyoungConstants.java` claims the `FEE1` field order is
  `{distance, steps, calories}`; the code (`MoyoungDeviceSupport.java:1325-1329`)
  reads `steps, distance, calories`. Our capture confirms the **code** is right.

## 6. Test coverage upstream

```
test/.../devices/moyoung/MoyoungWorkoutSummaryParserTest.java
test/.../service/devices/moyoung/MoyoungDeviceSupportTest.java
```

Packet parsing and workout summary decoding are covered upstream, so a contributed
coordinator inherits a tested protocol stack rather than an untested one.
