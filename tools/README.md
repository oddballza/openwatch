# BLE diagnostic tools

Written from scratch against the BlueZ D-Bus API. No third-party code — see
`../docs/LICENSING.md`.

* `scan_debug.py` — LE discovery and device enumeration.
* `full_gatt.py`  — connect, enumerate all services/characteristics, read DIS.
* `read_vals.py`  — read battery, Moyoung steps characteristic, vendor characteristics.

Each takes the target MAC as a module-level constant (`MAC`); edit it for another device.

## Gotchas found the hard way

* **`SetDiscoveryFilter({"Transport": "le"})` is required.** Without it BlueZ's
  default transport will not surface these peripherals and the device never appears.
* BlueZ **evicts the device object** shortly after disconnect; re-scan before
  touching `/org/bluez/hci0/dev_XX_...` or you get `UnknownObject`.
* Battery `0x2A19` is a raw uint8. Do not UTF-8 decode it — `0x30` is 48 %, not `"0"`.
* `btmon` raw HCI capture needs
  `sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/btmon`.
* The watch accepts one BLE central at a time; disconnect it from the phone first.
