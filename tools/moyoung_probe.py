#!/usr/bin/env python3
"""Send Moyoung QUERY packets to a watch and print the responses.

Usage:  moyoung_probe.py <MAC> [cmd[:hexpayload] ...]
Example: moyoung_probe.py AA:BB:CC:DD:EE:FF 41 57 0x84 0xB4:00 0xB4:12

Only send QUERY commands unless you know exactly what a SET does.
"""
import os, sys, time
import dbus, dbus.mainloop.glib
from gi.repository import GLib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

MAC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WATCH_MAC", "")).upper()
if not MAC:
    sys.exit(__doc__)
DP = "/org/bluez/hci0/dev_" + MAC.replace(":", "_")
ad = dbus.Interface(bus.get_object("org.bluez", "/org/bluez/hci0"), "org.bluez.Adapter1")

def dprops():
    try:
        return dbus.Interface(bus.get_object("org.bluez", DP),
                              "org.freedesktop.DBus.Properties").GetAll("org.bluez.Device1")
    except Exception:
        return {}

if not dprops().get("Connected"):
    try:
        ad.SetDiscoveryFilter({"Transport": "le"}); ad.StartDiscovery()
        for _ in range(30):
            time.sleep(1)
            if dprops(): break
        dbus.Interface(bus.get_object("org.bluez", DP), "org.bluez.Device1").Connect()
        try: ad.StopDiscovery()
        except Exception: pass
    except Exception as e:
        print("connect error:", e)
for _ in range(40):
    if dprops().get("ServicesResolved"): break
    time.sleep(0.5)
if not dprops().get("Connected"):
    sys.exit("could not connect to %s" % MAC)
print("connected to %s\n" % MAC)

om = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
chars = {p: v["org.bluez.GattCharacteristic1"]
         for p, v in om.GetManagedObjects().items()
         if "org.bluez.GattCharacteristic1" in v and DP in p}

def find(short):
    for p, c in chars.items():
        if str(c["UUID"]).startswith("0000" + short):
            return p

FEE2, FEE3 = find("fee2"), find("fee3")
rx = []
bus.add_signal_receiver(
    lambda i, changed, inv, path=None: rx.append(bytes(bytearray(changed["Value"])))
        if "Value" in changed else None,
    dbus_interface="org.freedesktop.DBus.Properties",
    signal_name="PropertiesChanged", path_keyword="path")
dbus.Interface(bus.get_object("org.bluez", FEE3), "org.bluez.GattCharacteristic1").StartNotify()

def build(ptype, payload=b""):
    ln = len(payload) + 5
    return bytes([0xFE, 0xEA, (32 + (ln >> 8)) & 0xFF, ln & 0xFF, ptype & 0xFF]) + payload

def probe(ptype, payload=b"", wait=4.0):
    del rx[:]
    pkt = build(ptype, payload)
    print(">>> cmd %d (0x%02X) payload=%s  TX: %s"
          % (ptype if ptype < 128 else ptype - 256, ptype & 0xFF,
             payload.hex() or "-", pkt.hex()))
    dbus.Interface(bus.get_object("org.bluez", FEE2), "org.bluez.GattCharacteristic1")\
        .WriteValue(dbus.Array([dbus.Byte(b) for b in pkt], signature='y'), {"type": "command"})
    loop = GLib.MainLoop()
    GLib.timeout_add(int(wait * 1000), lambda: (loop.quit(), False)[1])
    loop.run()
    if not rx:
        print("    <no response>")
    for v in rx:
        print("    RX: %s" % v.hex())
    print()

for arg in sys.argv[2:]:
    cmd, _, pl = arg.partition(":")
    probe(int(cmd, 0), bytes.fromhex(pl) if pl else b"")

print("done (leaving connection open)")
