# MT55 GATT services — classified against the Bluetooth SIG assigned numbers

Cross-referenced against the authoritative SIG YAML
(`assigned_numbers/uuids/service_uuids.yaml` and `member_uuids.yaml`, retrieved
2026-09-01). Identifiers redacted per repo policy.

| Service UUID | SIG assignment | Role on MT55 |
|---|---|---|
| `0x1800` | Standard — GAP | Generic Access |
| `0x1801` | Standard — GATT | Service Changed |
| `0x180A` | Standard — Device Information | manufacturer / fw / serial (read by GB) |
| `0x180D` | Standard — Heart Rate | present but unused; Moyoung uses its own HR path |
| `0x180F` | Standard — Battery | battery level (read by GB) |
| `0xFEEA` | **Member UUID — "Swirl Networks, Inc."** | **reused** as Moyoung's main protocol service (FEE1/FEE2/FEE3/FEE5/FEE6) |
| `0xFEE7` | **Member UUID — "Tencent Holdings Limited."** | **reused** — undocumented service (FEA1 notify / FEC9 read) |
| `0x190E` | **Not SIG-assigned** | vendor/arbitrary (char 0x0004 write / 0x0003 notify) — untouched by GB |
| `0xAE00` | **Not SIG-assigned** | vendor/arbitrary — OTA/firmware (AE01 write / AE02 notify) |

## What this establishes

1. **UUID squatting.** `0xFEEA` and `0xFEE7` are SIG *member* allocations owned by
   Swirl Networks and Tencent respectively — **not** Moyoung. The watch reuses
   plausible 16-bit UUIDs it does not own. `0x190E` and `0xAE00` are entirely
   unassigned values. Per the SIG spec, custom services should use 128-bit UUIDs;
   squatting 16-bit space is non-compliant but ubiquitous on low-cost ODM watches.

2. **A vendor coordinator is necessary.** MT55 exposes the standard DIS/Battery/HR
   services, but all real functionality (steps, sleep, HR history, workouts,
   settings, watchface, OTA) rides the proprietary/squatted services. The SIG's
   "adhere to standards, no companion app needed" ideal therefore cannot drive
   this watch — it requires the Moyoung protocol coordinator (which is what the
   MT55 coordinator provides via Gadgetbridge's existing Moyoung stack).

Source: https://www.bluetooth.com/specifications/assigned-numbers/ (service_uuids.yaml, member_uuids.yaml)
