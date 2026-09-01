# DRAFT — MT55 content for the Gadgetbridge website (gadgetbridge.org)

The website content lives in a SEPARATE repo from the app. Once PR #6688 merges,
MT55 can be added to the Moyoung gadget page. Draft entry (mirrors the existing
Moyoung device blocks):

---

## MT55

- Status: Highly supported (all major features)
- No-vendor pair: yes (initial pairing works in Gadgetbridge)
- Added via: (link PR #6688)

**Known issues:**
- MT55 is dual-mode (BR/EDR + LE). Do **not** pair it in Android's system
  Bluetooth settings — Android may bond it as an audio device, causing A2DP/GATT
  contention that stalls Gadgetbridge's activity fetch. Pair only within
  Gadgetbridge. If already system-paired, "Forget" it in Android Bluetooth
  settings and reconnect from Gadgetbridge.

**Confirmed working:** battery, steps, distance, sleep (incl. REM stages),
workouts, live heart rate. SpO2 / blood pressure are manual measurements.

**Not available (protocol/hardware limits):** Body Energy, HRV, VO2max (the
watch does SpO2, not VO2max). Continuous HR/stress must be enabled on the watch.
