# FILED as #6689 — Moyoung: DO_NOT_DISTURB_ONOFF parse error (shared code)

Filed: https://codeberg.org/Freeyourgadget/Gadgetbridge/issues/6689

File at: https://codeberg.org/Freeyourgadget/Gadgetbridge/issues  (bug template)

---

**Title:** Moyoung: DO_NOT_DISTURB_ONOFF fails to parse (shares query command with DO_NOT_DISTURB_TIME)

**Body:**

On every settings query, Moyoung devices log a parse error:

```
Parse error in packet for setting DO_NOT_DISTURB_ONOFF:
  java.lang.IllegalArgumentException: Wrong data length, should be 1, was 4
  at MoyoungSettingBool.decode(MoyoungSettingBool.java:32)
  at QuerySettingsOperation.handlePacket(QuerySettingsOperation.java:109)
```

**Root cause** (in shared code, not device-specific):

`AbstractMoyoungDeviceCoordinator` maps two settings to the *same* query command
`CMD_QUERY_DO_NOT_DISTURB_TIME` (-127):

```java
new MoyoungSettingTimeRange("DO_NOT_DISTURB_TIME",  CMD_QUERY_DO_NOT_DISTURB_TIME, CMD_SET_DO_NOT_DISTURB_TIME),
new MoyoungSettingBool     ("DO_NOT_DISTURB_ONOFF", CMD_QUERY_DO_NOT_DISTURB_TIME, CMD_SET_DO_NOT_DISTURB_TIME),
```

`QuerySettingsOperation.handlePacket()` runs the decoder of *every* setting whose
`cmdQuery` matches the response packet type. When the watch answers -127 with the
4-byte time range, `TimeRange.decode` handles it, but `Bool.decode` also runs on
the same 4 bytes and throws (it requires exactly 1).

**Device-observed evidence** (MT55, MOYOUNG-V2, own device, clean-room):
The -127 response is exactly 4 bytes (`ec 04 68 01` in one capture) — the time
range only. There is no separate on/off byte, and `MoyoungConstants` defines no
separate DND on/off command.

**Impact:** non-fatal (caught + logged) but every settings query logs a stack
trace, and the DND on/off toggle cannot reflect real state.

**Suggested fix (for maintainer decision, since this is shared across ~24 devices):**
Either remove `DO_NOT_DISTURB_ONOFF` (DND appears defined solely by the time
window), or, if some models encode on/off within the time-range packet, decode it
from there rather than as a standalone Bool. I only have an MT55 to test, so I'd
defer to maintainers on cross-model behaviour and am happy to test any proposed
change on MT55.

_Reported from clean-room observation (own-device logcat + BLE probing); no
decompiled sources used._
