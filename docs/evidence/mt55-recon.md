# MT55 — Raw reconnaissance evidence

Identifiers are redacted (see note below).

Captured 2026-09-01 on Kali Linux, BlueZ 5.72, Intel hci0 (adapter MAC redacted), HCI 4.2.
All values below are literal tool output, reproduced by the scripts in `tools/`.

## 1. Advertisement (pre-connection)

```
Device AA:BB:CC:DD:EE:FF MT55
        Name: MT55
        Alias: MT55
        AddressType: public
        RSSI: -59 .. -79 dBm
        UUID:  0000feea-0000-1000-8000-00805f9b34fb
        ManufacturerData.Key:   0xf0ef (61679)
        ManufacturerData.Value: aa bb cc dd ee ff      (== the device's own MAC)
        ServiceData[0000feea-...]: 4a 53 42 06 01 00 90   ascii = "JSB" 06 01 00 90
```

Note: identifiers in this document are **redacted** — the real MAC is replaced by
`AA:BB:CC:DD:EE:FF` and the serial number by `<redacted>`. The genuine address
prefix is not a registered IEEE OUI, yet the device declares the address
type as **public**. This is typical of low-cost ODM hardware. The address appears
stable (identical across all scans and across connect/disconnect cycles), so it is
usable as a persistent device key, but it must be treated as an untrusted identifier.

## 2. Device Information Service (0x180A) — read over GATT

| Characteristic | UUID | Value |
|---|---|---|
| Serial Number  | 0x2A25 | `<redacted>` |
| Firmware Rev   | 0x2A26 | `JLQFNJEJ1.1` |
| Software Rev   | 0x2A28 | `MOY-JSB2-2.0.4` |
| Manufacturer   | 0x2A29 | **`MOYOUNG-V2`** |

`Model Number (0x2A24)` is **absent**. This matters: Gadgetbridge's documented
"packet 19 / DFU status" probe reads the model number string and looks for `DFU`.
That probe cannot succeed on this watch.

## 3. Complete GATT database

```
SERVICE 0x1801  Generic Attribute
   0x2A05  [indicate]                       Service Changed

SERVICE 0x180A  Device Information
   0x2A25  [read]   Serial Number   = "<redacted>"
   0x2A26  [read]   Firmware Rev    = "JLQFNJEJ1.1"
   0x2A28  [read]   Software Rev    = "MOY-JSB2-2.0.4"
   0x2A29  [read]   Manufacturer    = "MOYOUNG-V2"

SERVICE 0x180D  Heart Rate
   0x2A37  [notify]                         HR Measurement
   0x2A38  [read]   = 01                    Body Sensor Location = "Chest" (vendor default, wrong)

SERVICE 0x180F  Battery
   0x2A19  [read,notify]  raw = 0x30        -> 48 %

SERVICE 0x190E  (vendor, undocumented)
   0x0004  [write-without-response]
   0x0003  [notify]

SERVICE 0xAE00  (vendor OTA / firmware update)
   0xAE01  [write-without-response]
   0xAE02  [notify]

SERVICE 0xFEE7  (vendor, undocumented)
   0xFEC9  [read]   = aabbccddeeff          (== MAC again)
   0xFEA1  [read,notify] = 01160300

SERVICE 0xFEEA  *** MOYOUNG PROTOCOL ***
   0xFEE1  [read,notify]              STEPS
   0xFEE2  [write-without-response]   DATA_OUT
   0xFEE3  [notify]                   DATA_IN
   0xFEE4  [read]   = <empty>
   0xFEE5  [write-without-response]   DATA_SPECIAL_1
   0xFEE6  [write-without-response]   DATA_SPECIAL_2
```

Absent: `0xFEE7`/`0xFEE8` *as characteristics of 0xFEEA* (the ECG channels).
This watch therefore has **no ECG capability**. Also absent: Nordic DFU (`0xFE59`).

## 4. Live protocol validation — steps characteristic 0xFEE1

```
raw = 16 03 00 8f 02 00 2a 00 00     (exactly 9 bytes)
```

Decoded as 3x little-endian uint24, in the field order used by Gadgetbridge's
`MoyoungDeviceSupport.handleStepsHistory()` (steps, distance, calories):

```
steps    = 0x000316 = 790
distance = 0x00028f = 655   (metres)
calories = 0x00002a = 42    (kcal)
```

790 steps / 655 m = 0.83 m per step — physically plausible, and the payload is
exactly the 9 bytes Gadgetbridge requires. This is a positive end-to-end match
against the upstream parser.

Note the in-source *comment* in `MoyoungConstants.java` states the order is
`{distance, steps, calories}`. The actual code at
`MoyoungDeviceSupport.java:1325-1329` reads `steps, distance, calories`.
**The code is authoritative; the comment is stale.**

## 5. Reproduction

```sh
python3 tools/scan_debug.py    # LE discovery (needs Transport=le filter)
python3 tools/full_gatt.py     # connect + full GATT enumeration + DIS reads
python3 tools/read_vals.py     # battery + steps + vendor characteristic reads
```

Caveat: `btmon` raw HCI capture required `setcap cap_net_raw,cap_net_admin+eip`
and was not used for the results above — everything here came from the BlueZ
D-Bus API, which is sufficient for enumeration but does *not* capture the
Moyoung packet exchange. Packet-level capture is still outstanding (see
`PROTOCOL_RESEARCH.md`).
