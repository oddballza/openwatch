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

---

# Static analysis — Da Fit APK (`com.crrepa.band.dafit` 2.9.23)

Decompiled with jadx 1.5.6. **Findings below are facts about the wire protocol —
no vendor code is reproduced or reused.** See `LICENSING.md`.

The vendor SDK lives under `com.crrepa.ble.*` and is only partly obfuscated.

## The 9 "undocumented" trailing bytes — solved

`com.crrepa.ble.conn.bean.CRPWatchFaceLayoutInfo` declares exactly the fields
seen on the wire:

```
timePosition, timeTopContent, timeBottomContent, textColor,
backgroundPictureMd5 (PICTURE_MD5_LENGTH = 32),
width, height, thumWidth, thumHeight, compressionType
```

So the live capture `01d2 0118 01d2 0118 ff` decodes as:

| Bytes | Field | Value |
|---|---|---|
| `01d2` | `width` | 466 |
| `0118` | `height` | 280 |
| `01d2` | `thumWidth` | 466 |
| `0118` | `thumHeight` | 280 |
| `ff` | `compressionType` | **255 = `ORIGINAL`** |

`CompressionType` enum: `LZO(0)`, `RGB_DEDUPLICATION(1)`, `RGB_LINE(2)`,
`BLUETRUM(3)`, `RTK_8773(4)`, `JIELI(5)`, `JIELI_707(21)`, `SIFLI(254)`,
`ORIGINAL(255)`.

**MT55 reports `ORIGINAL`** — background images are sent uncompressed. That is the
simplest of the nine paths, and it means no LZO/vendor codec is needed.

## CMD_SET_WATCH_FACE_LAYOUT (56) — write format confirmed

The builder produces a payload of **exactly 37 bytes**:

```
[0]      timePosition
[1]      timeTopContent
[2]      timeBottomContent
[3..4]   textColor as RGB565, BIG-endian
[5..36]  backgroundPictureMd5 - 32 bytes, one hex digit per byte (value 0-15)
```

**The 9 read-only fields are NOT sent back.** The query *response* is 46 bytes
(37 + 9); the *write* is 37. This fully reconciles the live capture with the
format documented in `MoyoungConstants.java`, which is therefore **correct**.

## Framing confirmed identical to Gadgetbridge

The app's packet builder produces `FE EA <flag> <len> <type> <payload>`, with
`flag = 16` when MTU is 20, else `32 + (len >> 8)`. This matches
`MoyoungPacketOut.buildPacket()` exactly. Gadgetbridge's framing is correct.

## Correction: CMD_QUERY_SUPPORT_WATCH_FACE

Earlier in this document I concluded the enumeration was unavailable because
`0x84` returned an empty payload. That was **an incomplete probe, not a device
limitation**. The app issues `0x84` followed by four `0xB4` sub-queries with
payloads `{0}`, `{18}`, `{16}`, `{32}`. The capability data likely arrives via
`0xB4`. This needs re-probing before any conclusion is drawn.

## Background image upload — entry point found, wire format still open

The SDK exposes:

```
sendWatchFaceBackground(CRPWatchFaceBackgroundInfo, CRPFileTransListener)
sendWatchFaceLayout(CRPWatchFaceLayoutInfo)
queryWatchFaceScreenInfo(CRPWatchFaceScreenCallback)
```

`CRPWatchFaceBackgroundInfo` carries `bitmap`, `thumBitmap`, `CompressionType`
and a 30-second default timeout. The implementation selects a transfer class from
a factory keyed on compression type, hands it both bitmaps, sets the timeout and
starts the transfer — i.e. a **separate file-transfer channel**, not a
`CMD_*` on `FEE2`. This is consistent with the earlier hypothesis that the
undocumented `0x190E` service (write `0x0004` / notify `0x0003`) carries bulk
data, but that link is **not yet proven**.

Remaining work: trace the `ORIGINAL` transfer implementation to recover the
chunking, header and acknowledgement scheme, and confirm which characteristic it
writes to. An HCI snoop of Da Fit performing one background upload remains the
best cross-check.

---

# Watchface image transfer — reconstructed from static analysis

Traced through the vendor SDK's transfer classes. **Not yet verified on hardware**
— treat as a hypothesis with good evidence, not as fact.

## CMD 110 (0x6E) — the transfer control command

**This opcode does not exist in Gadgetbridge's `MoyoungConstants` at all.**

| Packet | Meaning |
|---|---|
| `110` + `uint32` big-endian total length | begin transfer, announce payload size |
| `110` + `FF FF FF FF` | abort / cancel transfer |

Framed with the standard `FE EA` header, so a start looks like:
`FE EA 20 09 6E <len32be>`.

## Transfer sequence

1. Bitmaps (background + thumbnail) are encoded per `CompressionType`. MT55
   negotiates `ORIGINAL` (255) — uncompressed.
2. App sends `110` with the total byte length.
3. **The watch replies with its preferred package length**, and the app adopts it
   as the chunk size. Default before negotiation is **256** bytes, or the MTU
   where available.
4. Chunk count is computed as `floor(total / chunkSize) + 1`.
5. Chunks are written on a **different characteristic from the control channel** —
   control and bulk data use separate write paths in the SDK.
6. Progress is reported as `(chunkIndex * 100) / chunkCount`.
7. A watchdog ticks every 1 s with a default timeout of **30 s**.

## Characteristic selection

The SDK picks the target characteristic from the packet type byte:

| Packet type | Characteristic |
|---|---|
| 1 | `FEE5` (DATA_SPECIAL_1) |
| 2 | `FEE6` (DATA_SPECIAL_2) |
| 3 | *(unidentified)* |
| 4 | *(unidentified)* |
| default | `FEE2` (DATA_OUT) |

Types 1 and 2 match `MoyoungDeviceSupport.getTargetCharacteristicForPacketType()`
exactly, which is a good check that this reading is correct. **Types 3 and 4 are
two channels Gadgetbridge does not know about** — plausible homes for the bulk
image data, alongside the undocumented `0x190E` service.

## What is still unresolved

* **Which characteristic carries the bulk chunks.** The SDK resolves it through a
  field holder populated during service discovery; mapping those fields to UUIDs
  needs one more hop through the discovery code.
* **The exact chunk framing** — chunks pass through a helper that pads or wraps
  them to the negotiated size before writing.
* Whether a completion/ack packet follows the final chunk.

## Why this is not yet safe to attempt

Writing a background image requires all three unknowns above to be right, and the
layout packet then has to reference the image by MD5. A mismatch leaves the watch
with a layout pointing at an image it does not have. Until the chunk channel and
framing are confirmed — by an over-the-air capture, or by resolving the remaining
static hop — **no write should be attempted**.

Phone-side capture is **not available on this hardware**: ColorOS records the
snoop log but strips it from `adb bugreport`, blocks `/data/misc/bluetooth/logs/`
without root, and stubs the btsnoop-net socket (TCP 8872 accepts, then closes with
zero bytes). GATT client apps (BLE Scanner, nRF Toolbox, etc.) cannot observe
another app's connection — Android forbids it. A dedicated BLE sniffer
(e.g. nRF52840) or a stock-Android phone remains the way to get ground truth.

---

# Live handshake confirmation (2026-09-01)

Ran `tools/wf_handshake_probe.py` against the watch: announce a transfer with
`CMD 110`, observe the reply, then **abort** (`110` + `FFFFFFFF`). No image bytes
were written, so nothing was committed.

```
TX  FEE2:  FE EA 20 09 6E 00 00 00 64      CMD 110, announce length = 100
RX  FEE3:  FE EA 20 08 BA 01 00 28         negotiation reply, type 0xBA, payload 01 00 28
RX  FEE3:  FE EA 20 09 6E FF FF 00 01      CMD 110 echo/status
TX  FEE2:  FE EA 20 09 6E FF FF FF FF      abort
RX  FEE3:  FE EA 20 05 64                  CMD 100 (weather-resend) = watch back to main menu
```

Confirmed:

* **The transfer handshake is real and reachable.** The watch accepts `CMD 110`
  on FEE2 and answers with a negotiation packet (type **0xBA / 186**, payload
  `01 00 28`) — the package-length / screen-info reply the SDK expects before
  chunking. `0xBA` is not in Gadgetbridge's constants.
* **Responses arrive on FEE3** (DATA_IN), the standard notify channel.
* **Abort is clean.** After `FFFFFFFF` the watch emitted its normal
  weather-resend message and returned to the main menu — no lingering
  "awaiting data" state, nothing written.

Still NOT confirmed by this probe:

* **The chunk write characteristic (FEE5 vs FEE6).** Chunks are writes *from* the
  phone; the watch does not notify on the write channel, so a passive handshake
  cannot distinguish them. Static analysis points to **FEE6** (channel 2 ->
  `mra.k()` -> field assigned on UUID `fee6`). Confirming it requires actually
  sending chunk data — the one destructive-capable step — so it stays a
  well-evidenced hypothesis, not a proven fact.
* The exact meaning of the `0xBA` payload `01 00 28` (likely `[status=01]
  [pkglen=0x0028=40]`, but unverified).

## Net state of the watchface-upload protocol

| Element | Status |
|---|---|
| Layout query/set (CMD 56/57), 37-byte format | **Confirmed** (APK + live read) |
| Displayed-face switch (CMD 25) | **Confirmed working on hardware** |
| Transfer control CMD 110 (start/abort) | **Confirmed working on hardware** |
| Negotiation reply 0xBA | Observed; payload semantics unverified |
| Chunk framing (raw, MTU-mode) | From APK; not yet sent |
| Chunk write characteristic | **Hypothesis: FEE6**; needs a real write to confirm |
| Background image encoding (ORIGINAL) | From APK; not yet reproduced |
