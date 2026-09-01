# Protocol research — MT55 (Moyoung V2)

**Date:** 2026-09-01. All results below are live captures against the physical
watch, not static analysis. Reproduce with `tools/probe_watchface.py`.

## Method

Moyoung V2 framing, taken from `MoyoungPacketOut.buildPacket()`:

```
packet[0] = 0xFE
packet[1] = 0xEA
packet[2] = 32 + ((len >> 8) & 0xFF)     # MTU != 20 (V2)
packet[3] = len & 0xFF                   # len = 5 + payload length
packet[4] = packetType
packet[5:] = payload
```

Write to `0xFEE2` (write-without-response), read replies via notify on `0xFEE3`.
**Only QUERY commands were sent — nothing on the watch was modified.**

## Result 1 — control (sanity check)

`CMD_QUERY_DISPLAY_WATCH_FACE` (41 / 0x29) — implemented upstream.

```
TX: fe ea 20 05 29
RX: fe ea 20 06 29 09      -> payload {09} = watch face index 9
```

The transport, framing and notify path all work.

## Result 2 — CMD_QUERY_SUPPORT_WATCH_FACE (-124 / 0x84)

```
TX: fe ea 20 05 84
RX: fe ea 20 05 84         -> echo, EMPTY payload (no count)
RX: fe ea 20 05 64         -> unrelated: CMD_NOTIFY_WEATHER_CHANGE (100),
                              documented upstream as "ONLY INCOMING"
```

Upstream documents this as `{} -> {count >> 8, count, ...}`. **This watch returns
no count.** Treat the supported-watchface enumeration as unavailable on MT55.

## Result 3 — CMD_QUERY_WATCH_FACE_LAYOUT (57 / 0x39) — **works**

```
TX: fe ea 20 05 39
RX: fe ea 20 33 39 01 01 04 ff ff
    0b 06 0e 06 00 0d 08 0e 06 05 0d 04 05 0e 0d 0b
    0c 08 08 07 02 06 0b 01 04 04 0f 0d 01 09 03 0f
    01 d2 01 18 01 d2 01 18 ff
```

Decoded against the upstream-documented layout:

| Field | Bytes | Value |
|---|---|---|
| `time_position` | `01` | 1 |
| `time_top_content` | `01` | 1 |
| `time_bottom_content` | `04` | 4 |
| `text_color` (R5G6B5) | `ff ff` | `0xFFFF` = white |
| `background_picture_md5[32]` | 32 nibble-bytes | `b6e60d8e65d45edbc88726b144fd193f` |
| **undocumented trailing** | `01d2 0118 01d2 0118 ff` | **466, 280, 466, 280, 0xFF** |

The MD5 field decodes to exactly 32 valid hex characters, and the colour is a
sensible R5G6B5 white. The documented format is **correct**, and the nibble
encoding quirk ("hex digits as values 0-15, not ASCII") is confirmed on hardware.

### Why this matters

Upstream marks these commands `(*)`, which `MoyoungConstants.java:32-34` defines as:

> *"based only on static reverse engineering of the original app code, **not
> supported by my watch so not implemented** (or at least I didn't manage to get
> any response out of it)"*

**That assumption does not hold for MT55.** This watch answers
`CMD_QUERY_WATCH_FACE_LAYOUT` with a well-formed, fully decodable response. The
setting is commented out at `AbstractMoyoungDeviceCoordinator.java:209`:

```java
// (*) new MoyoungSetting("WATCH_FACE_LAYOUT", CMD_QUERY_WATCH_FACE_LAYOUT, CMD_SET_WATCH_FACE_LAYOUT),
```

Enabling it is therefore a real, evidence-backed upstream contribution — and the
9 undocumented trailing bytes (two `466 x 280` pairs plus a `0xFF` terminator,
almost certainly canvas/preview dimensions) are new information upstream does
not have.

## What is still unknown — the background image

`background_picture_md5` references an image the watch already holds. **No image
or file transfer command exists anywhere in `MoyoungConstants.java`** — I grepped
for `PICTURE|IMAGE|FILE|TRANSFER|UPLOAD|BACKGROUND|MD5` and found only this one
field. So changing the *layout* (time position, contents, colour) is reachable
now; supplying a *new background image* is not, and needs fresh reverse
engineering.

Leading hypothesis, to be tested: MT55 exposes an undocumented service **`0x190E`**
(char `0x0004` write-without-response, char `0x0003` notify) that Gadgetbridge
never touches. A separate write/notify pair with no known purpose is the natural
place for bulk image transfer. The vendor OTA service `0xAE00` is the other
candidate. Neither is confirmed.

### How to confirm

Capture the Da Fit app setting a custom background:

1. Android Developer options -> **Enable Bluetooth HCI snoop log**.
2. Reproduce exactly one action (set a custom watch face background).
3. Pull the log: `adb pull /sdcard/btsnoop_hci.log` (path varies by OEM; check
   `adb shell settings get global bluetooth_hci_log`).
4. Open in Wireshark, filter `btatt`, and look for large writes to a handle that
   is **not** `0xFEE2`.
5. Correlate the transferred bytes' MD5 against the value returned by
   `CMD_QUERY_WATCH_FACE_LAYOUT`.

On this Linux host, `btmon -w capture.btsnoop` also works once granted
`cap_net_raw,cap_net_admin` — but the phone-side snoop log is the better source
because the Da Fit app is the only known implementation of the upload.

## Suggested order of work

1. **Layout customisation** — uncomment the setting, add a composite
   `MoyoungSetting` for the 5 header fields, preserve the existing MD5 and the
   trailing bytes on write. Evidence already in hand. *Low risk.*
2. **Background upload** — requires the capture above first. *Unknown scope.*

Do not send `CMD_SET_WATCH_FACE_LAYOUT` with a guessed payload before step 1's
round-trip is understood; a malformed layout write is the one realistic way to
make the watch face unusable.
