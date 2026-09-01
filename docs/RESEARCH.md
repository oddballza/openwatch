# OpenWatch — Phase 1 Research

**Date:** 2026-09-01
**Device under investigation:** `MT55` (MAC redacted as `AA:BB:CC:DD:EE:FF`)
**Status:** Reconnaissance complete. Recommendation issued. **No application code written yet — by design.**

All device claims in this document are backed by literal tool output in
[`evidence/mt55-recon.md`](evidence/mt55-recon.md). All Gadgetbridge claims are
backed by file:line references into upstream source at commit
`1b7ad478656fbce7ff76a330a4a0f9cf25b05eef` (2026-09-01).

---

## 0. Executive summary

The investigation produced an unusually clean result:

1. The watch **self-identifies as `MOYOUNG-V2`** in its Device Information Service.
   This is not an inference from the marketing name — it is the exact string
   Gadgetbridge itself uses to select the protocol variant.
2. It exposes the Moyoung service `0xFEEA` with characteristics
   `FEE1/FEE2/FEE3/FEE5/FEE6` matching `MoyoungConstants.java` exactly.
3. A live read of the steps characteristic returned a 9-byte payload that decodes
   correctly under Gadgetbridge's own parser (790 steps / 655 m / 42 kcal).
4. **However:** Gadgetbridge selects device support purely by matching a regex
   against the advertised name. I tested `MT55` against all **412** device-name
   patterns in the entire codebase. **Zero match.**

So the protocol is fully implemented upstream; only the four-character model name
is unregistered. This is a ~40-line upstream patch, not a reverse-engineering project.

**Recommendation: Option B — use Gadgetbridge, and contribute an `MT55Coordinator`
upstream. Do not build OpenWatch.** See §6 and [`ARCHITECTURE_DECISION.md`](ARCHITECTURE_DECISION.md).

---

## 1. Existing alternatives

| Project | License | Relevance to MT55 | Verdict |
|---|---|---|---|
| **Gadgetbridge** | AGPL-3.0 | Full Moyoung V1+V2 protocol; 24 Moyoung model coordinators; 82 protocol commands | **Directly applicable.** Only the name registration is missing |
| **Da Fit** (vendor) | Proprietary | The stock app. Ads, account, cloud, analytics | Rejected — it is the thing being replaced |
| **ATCwatch** (atc1441) | Custom FW | Replacement *firmware* for DaFit watches — **nRF52832 only** | **Not applicable**, see §7 |
| **Gadgetbridge-MT863** (krzys-h) | AGPL-3.0 | The original Moyoung-V2 fork. Its work was **already merged upstream** (PR #4070) | Historical only — use upstream |
| **AsteroidOS / wasp-os / InfiniTime** | Various | Replacement OS/firmware for *other* hardware (PineTime, Wear-class) | Not applicable to this SoC |

There is no ad-free Android companion app for Moyoung watches other than Gadgetbridge.
The niche is occupied, and occupied well.

## 2. Gadgetbridge — how much is already there

The Moyoung implementation is substantial and current:

```
devices/moyoung/          24 model coordinators + constants + weather + workout parser
service/devices/moyoung/  MoyoungDeviceSupport, MoyoungPacket{,In,Out},
                          FetchDataOperation, FetchWorkoutsV2Operation,
                          QuerySettingsOperation, TrainingFinishedDataOperation
test/.../moyoung/         MoyoungDeviceSupportTest, MoyoungWorkoutSummaryParserTest
```

`MoyoungConstants.java` defines **82 `CMD_*` opcodes**. The protocol, framing,
MTU negotiation, historical sync, and workout parsing are all implemented and
under test upstream. Detail in [`GADGETBRIDGE_ANALYSIS.md`](GADGETBRIDGE_ANALYSIS.md).

## 3. Da Fit / Moyoung ecosystem

Moyoung is the Chinese ODM that publishes the Da Fit app. The same firmware and BLE
protocol is resold under dozens of brands (Colmi, Blackview, FireBoltt, KSIX, iTech,
Rainbuvvy…), and "Colmi Fit" is a rebadged Da Fit. This is exactly why Gadgetbridge
carries 24 near-identical coordinators that differ only in a name regex and an MTU.

Two protocol generations exist, and upstream selects between them by reading the
**manufacturer name string** from DIS (`MoyoungConstants.java:60-62`):

* `MOYOUNG` — V1, fixed-size packets (256 bytes for fw >= 1.6.5, else 64)
* `MOYOUNG-V2` — V2, MTU-negotiated packets

Framing (`MoyoungConstants.java:44-58`):

```
packet[0] = 0xFE
packet[1] = 0xEA
packet[2] = (MTU == 20) ? 16 : (32 + ((len >> 8) & 0xFF))
packet[3] = len & 0xFF
packet[4] = packetType
packet[5:] = payload
```

## 4. My device — MT55

| Property | Value | How determined |
|---|---|---|
| Advertised name | `MT55` | LE scan |
| Address | redacted; declared **public** | LE scan. Real prefix is not a registered OUI; stable across reconnects |
| Advertised service | `0xFEEA` | LE scan — **the Moyoung service** |
| Service data | `4a 53 42 06 01 00 90` = `"JSB" 06 01 00 90` | LE scan; `JSB` matches the `JSB2` firmware family |
| Manufacturer data | key `0xF0EF`, value = own MAC | LE scan |
| Manufacturer (DIS) | **`MOYOUNG-V2`** | GATT read 0x2A29 |
| Software rev | `MOY-JSB2-2.0.4` | GATT read 0x2A28 |
| Firmware rev | `JLQFNJEJ1.1` | GATT read 0x2A26 |
| Serial | `<redacted>` | GATT read 0x2A25 |
| Model number | **absent** | 0x2A24 not present |
| Battery | 48 % | GATT read 0x2A19 = `0x30` |
| Protocol | **Moyoung V2, MTU-based** | DIS manufacturer string, per upstream's own rule |
| ECG | **not supported** | `FEE7`/`FEE8` ECG characteristics absent from `0xFEEA` |
| Gadgetbridge recognition | **NONE** | `MT55` matches 0 of 412 name patterns |

The device also exposes the odd `0xFEE7` service (`FEA1` read/notify, `FEC9` read)
that `MoyoungConstants.java:90-93` flags as unidentified — our watch matches the
original reverse engineer's device here, including `FEC9` returning the MAC.

### Why the name matters so much

`AbstractDeviceCoordinator.supports()` (line 140-151) is the whole of device matching:

```java
return supportedDeviceName.matcher(candidate.getName()).matches();
```

There is no fallback on advertised service UUID, no manufacturer-data match, no
DIS probe. A watch that speaks a perfectly supported protocol is invisible if its
name is not on the list. That is the entire gap for MT55.

## 5. Gap analysis

Legend: **Y** implemented / **N** absent / **n/a** not applicable to this hardware.
"MT55 likely" is inferred from the V2 protocol level and observed GATT; entries
marked *(unverified)* need a real pairing session to confirm.

| Feature | Da Fit | Gadgetbridge (Moyoung) | MT55 likely | OpenWatch would add |
|---|---|---|---|---|
| Pairing | Y | Y — **blocked on name regex only** | Y | nothing |
| Battery | Y | Y (0x180F + cmd 18) | **Y — verified 48 %** | nothing |
| Steps | Y | Y (FEE1 + history) | **Y — verified 790/655/42** | nothing |
| Heart rate (live) | Y | Y | Y *(unverified)* | nothing |
| HR history | Y | Y | Y *(unverified)* | nothing |
| Sleep | Y | Y | Y *(unverified)* | nothing |
| SpO2 | Y | Y (manual) | Y *(unverified)* | nothing |
| Stress | Y | Y | Y *(unverified)* | nothing |
| Blood pressure | Y | Y (manual) | Y *(unverified)* | nothing |
| Workouts | Y | Y (V1 + V2 ops) | Y *(unverified)* | nothing |
| Notifications | Y | Y | Y *(unverified)* | nothing |
| Calls | Y | Y | Y *(unverified)* | nothing |
| Music | Y | Y (control + info) | Y *(unverified)* | nothing |
| Weather | Y | Y (today + forecast) | Y *(unverified)* | nothing |
| Alarms | Y | Y | Y *(unverified)* | nothing |
| Watch faces | Y | Y | Y *(unverified)* | nothing |
| DND | Y | Y | Y *(unverified)* | nothing |
| Historical sync | Y | Y (FetchDataOperation) | Y *(unverified)* | nothing |
| ECG | Y | Y | **N — chars absent** | cannot add |
| Data export | N | Y (DB export, GPX/FIT) | — | nothing |
| Ads / account / cloud | **Yes** | **None** | — | nothing |

The "OpenWatch would add" column is empty on every row. That is the finding.

## 6. Recommendation

> **Should we build OpenWatch, extend Gadgetbridge, or simply use Gadgetbridge?**

**Use Gadgetbridge, and contribute one small coordinator upstream.**

Concretely, in priority order:

1. **Today, no code:** enable *Discover unsupported devices* in Gadgetbridge's
   discovery settings, long-press `MT55`, and use the "Add test device" dialog to
   bind the MAC to an existing MTU-508 Moyoung device type. `DeviceTypeDialog.kt:303-310`
   creates a **real persisted `GBDevice`** with the chosen type — this is a genuine
   working path, not a simulation. Verify function, then:
2. **Upstream patch:** add `MT55Coordinator extends AbstractMoyoungDeviceCoordinator`
   with `Pattern.compile("^MT55$")` and `getMtu() = 508`, plus a `DeviceType` entry
   and a string resource. ~40 lines, mirroring `C20Coordinator.java` verbatim.
3. **Only if step 1 reveals real protocol divergence** — which the evidence does not
   predict — reopen the question of a separate application.

**Do not build OpenWatch.** Every capability in the original brief is already
implemented, tested, and maintained upstream, and the philosophy requirements
(open source, no ads, no account, no cloud, no telemetry, local-first, minimal
permissions) are already Gadgetbridge's own design constraints. Building a parallel
Kotlin/Compose implementation would mean re-deriving 82 protocol opcodes and a
historical-sync engine to arrive at a strictly worse version of software that
already exists — and, because of AGPL-3.0, without being able to shortcut by
copying (see [`LICENSING.md`](LICENSING.md)).

The brief's own architectural principle settles it:

> *"If there is an existing open-source implementation that already solves 80–95%
> of this problem, prefer extending or integrating with it."*

Measured against the gap analysis, upstream solves **~100 %** of it, minus one regex.

## 7. Firmware

**Official updates:** delivered only in-band via the Da Fit app over the vendor OTA
service `0xAE00` (`AE01` write / `AE02` notify). There is no public firmware
repository, no published changelog, and no version feed for `MOY-JSB2-2.0.4` /
`JLQFNJEJ1.1`. Gadgetbridge does not implement Moyoung firmware flashing.

**Open-source firmware: not available for this watch.** ATCwatch/DaFlasher — the
only mature open firmware for Da Fit watches — targets the **nRF52832** (P8,
PineTime-class hardware). MT55 presents an `0xAE00` vendor OTA service and has
**no Nordic DFU service (`0xFE59`)**, so it is not running an nRF52 DFU bootloader
and is outside ATCwatch's supported hardware.

Attempting to push unsigned images at `0xAE00` without a known-good image and a
recovery path risks an unrecoverable brick, with no vendor restore route. Not
recommended, and out of scope.

---

## Sources

- [Gadgetbridge — Moyoung / Da Fit](https://gadgetbridge.org/gadgets/wearables/moyoung/)
- [Gadgetbridge upstream (Codeberg)](https://codeberg.org/Freeyourgadget/Gadgetbridge)
- [PR #4070 — Add Moyoung(-v2) protocol](https://codeberg.org/Freeyourgadget/Gadgetbridge/pulls/4070)
- [krzys-h/Gadgetbridge-MT863](https://github.com/krzys-h/Gadgetbridge-MT863)
- [atc1441/ATCwatch](https://github.com/atc1441/ATCwatch) / [DaFlasherFiles](https://github.com/atc1441/DaFlasherFiles)
