#!/usr/bin/env python3
"""SAFE first chunk-write test for the Moyoung watchface transfer.

For each candidate channel (FEE6 then FEE5):
  1. announce a LARGE transfer via CMD 110 (so it can never complete)
  2. send ONE small test chunk to the candidate characteristic
  3. observe any notify response (progress / ack / error)
  4. ABORT (110 + FFFFFFFF)

Because the announced length (100000) is far larger than the bytes sent (20),
the watch can never finalise the transfer, so nothing is committed to flash.
Abort after every attempt returns the watch to its main menu.

Usage: wf_chunk_test.py <MAC>
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
        ad.SetDiscoveryFilter({"Transport":"le"}); ad.StartDiscovery()
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
        if str(c["UUID"]).startswith("0000"+short): return p
P = {u: find(u) for u in ("fee1","fee2","fee3","fee5","fee6")}
rx = []
def on_props(iface, changed, inv, path=None):
    if "Value" in changed:
        u = next((k for k,v in P.items() if v==path), path.split("/")[-1])
        rx.append((u, bytes(bytearray(changed["Value"]))))
bus.add_signal_receiver(on_props, dbus_interface="org.freedesktop.DBus.Properties",
    signal_name="PropertiesChanged", path_keyword="path")
for u in ("fee3","fee1","fee5","fee6"):
    p = P.get(u)
    if p and "notify" in [str(f) for f in chars[p].get("Flags",[])]:
        try: dbus.Interface(bus.get_object("org.bluez", p),"org.bluez.GattCharacteristic1").StartNotify()
        except Exception: pass
def frame(t, pl=b""):
    ln = len(pl)+5
    return bytes([0xFE,0xEA,(32+(ln>>8))&0xFF, ln&0xFF, t&0xFF])+pl
def w(uuid, data, wait=4.0, label=""):
    del rx[:]
    print("    TX %s ->%s: %s" % (label, uuid, data.hex()))
    dbus.Interface(bus.get_object("org.bluez", P[uuid]),"org.bluez.GattCharacteristic1")\
        .WriteValue(dbus.Array([dbus.Byte(b) for b in data],signature='y'), {"type":"command"})
    loop=GLib.MainLoop(); GLib.timeout_add(int(wait*1000), lambda:(loop.quit(),False)[1]); loop.run()
    for u,v in rx: print("      RX [%s]: %s" % (u, v.hex()))
    if not rx: print("      <no response>")
    return list(rx)

ANNOUNCE = frame(110, (100000).to_bytes(4,"big"))   # huge -> can never complete
ABORT    = frame(110, b"\xff\xff\xff\xff")
CHUNK    = bytes(range(20))                          # 20-byte test pattern, raw (MTU mode)

for ch in ("fee6", "fee5"):
    print("=== ROUND: chunk channel %s ===" % ch)
    w("fee2", ANNOUNCE, 4.0, "announce(100000)")
    time.sleep(0.3)
    w(ch, CHUNK, 4.0, "test-chunk(20 raw)")
    time.sleep(0.3)
    w("fee2", ABORT, 3.0, "abort")
    print()
    time.sleep(1.0)

print("all rounds aborted; disconnecting")
try: dbus.Interface(bus.get_object("org.bluez", DP),"org.bluez.Device1").Disconnect()
except Exception: pass
