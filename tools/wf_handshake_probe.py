#!/usr/bin/env python3
"""Probe the Moyoung watchface-transfer HANDSHAKE only. Sends CMD 110 (announce
transfer) and observes the watch's reply, then ABORTS. No image data is written,
so nothing is committed to the watch. Read-only in effect.

Usage: wf_handshake_probe.py <MAC>
"""
import os, sys, time
import dbus, dbus.mainloop.glib
from gi.repository import GLib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
MAC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WATCH_MAC", "")).upper()
if not MAC: sys.exit(__doc__)
DP = "/org/bluez/hci0/dev_" + MAC.replace(":", "_")
ad = dbus.Interface(bus.get_object("org.bluez", "/org/bluez/hci0"), "org.bluez.Adapter1")
def dprops():
    try: return dbus.Interface(bus.get_object("org.bluez", DP), "org.freedesktop.DBus.Properties").GetAll("org.bluez.Device1")
    except Exception: return {}
if not dprops().get("Connected"):
    try:
        ad.SetDiscoveryFilter({"Transport": "le"}); ad.StartDiscovery()
        for _ in range(30):
            time.sleep(1)
            if dprops(): break
        dbus.Interface(bus.get_object("org.bluez", DP), "org.bluez.Device1").Connect()
        try: ad.StopDiscovery()
        except Exception: pass
    except Exception as e: print("connect:", e)
for _ in range(40):
    if dprops().get("ServicesResolved"): break
    time.sleep(0.5)
if not dprops().get("Connected"): sys.exit("could not connect")
print("connected to %s\n" % MAC)
om = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
chars = {p: v["org.bluez.GattCharacteristic1"] for p, v in om.GetManagedObjects().items()
         if "org.bluez.GattCharacteristic1" in v and DP in p}
def find(short):
    for p, c in chars.items():
        if str(c["UUID"]).startswith("0000" + short): return p
paths = {u: find(u) for u in ("fee1","fee2","fee3","fee5","fee6")}
print("characteristics:", {u: ("ok" if p else "MISSING") for u,p in paths.items()}, "\n")
rx = []
def on_props(iface, changed, inv, path=None):
    if "Value" in changed:
        short = next((u for u,p in paths.items() if p==path), path.split("/")[-1])
        rx.append((short, bytes(bytearray(changed["Value"]))))
bus.add_signal_receiver(on_props, dbus_interface="org.freedesktop.DBus.Properties",
    signal_name="PropertiesChanged", path_keyword="path")
# subscribe to every notify-capable char so we see the reply wherever it lands
for u in ("fee3","fee1","fee5","fee6"):
    p = paths.get(u)
    if p and "notify" in [str(f) for f in chars[p].get("Flags",[])]:
        try: dbus.Interface(bus.get_object("org.bluez", p), "org.bluez.GattCharacteristic1").StartNotify(); print("notify on", u)
        except Exception as e: print("notify %s failed: %s" % (u, str(e)[:40]))
print()
def frame(ptype, payload=b""):
    ln = len(payload) + 5
    return bytes([0xFE,0xEA,(32+(ln>>8))&0xFF, ln&0xFF, ptype&0xFF]) + payload
def send(uuid, data, label):
    del rx[:]
    print(">>> %s  ->%s  %s" % (label, uuid, data.hex()))
    dbus.Interface(bus.get_object("org.bluez", paths[uuid]), "org.bluez.GattCharacteristic1")\
        .WriteValue(dbus.Array([dbus.Byte(b) for b in data], signature='y'), {"type":"command"})
    loop = GLib.MainLoop(); GLib.timeout_add(5000, lambda:(loop.quit(),False)[1]); loop.run()
    if not rx: print("    <no response>")
    for u,v in rx: print("    RX [%s]: %s" % (u, v.hex()))
    print()

# Announce a small transfer (100 bytes) on FEE2 — watch should reply with preferred package length
send("fee2", frame(110, (100).to_bytes(4,"big")), "CMD 110 announce len=100")
# ALWAYS abort so the watch does not sit waiting for data
send("fee2", frame(110, b"\xff\xff\xff\xff"), "CMD 110 ABORT")
print("aborted; disconnecting")
try: dbus.Interface(bus.get_object("org.bluez", DP), "org.bluez.Device1").Disconnect()
except Exception: pass
