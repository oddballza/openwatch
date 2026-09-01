import dbus, dbus.mainloop.glib, time
from gi.repository import GLib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SystemBus()
import os, sys
# Target device MAC: pass as argv[1], or set WATCH_MAC in the environment.
MAC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WATCH_MAC", "")).upper()
if not MAC:
    sys.exit("usage: %s <MAC>   (or set WATCH_MAC)" % sys.argv[0])
DP="/org/bluez/hci0/dev_"+MAC.replace(":","_")
ad=dbus.Interface(bus.get_object("org.bluez","/org/bluez/hci0"),"org.bluez.Adapter1")
def dp():
    try: return dbus.Interface(bus.get_object("org.bluez",DP),"org.freedesktop.DBus.Properties").GetAll("org.bluez.Device1")
    except Exception: return {}
if not dp().get("Connected"):
    try:
        ad.SetDiscoveryFilter({"Transport":"le"}); ad.StartDiscovery()
        for _ in range(30):
            time.sleep(1)
            if dp(): break
        dbus.Interface(bus.get_object("org.bluez",DP),"org.bluez.Device1").Connect()
        try: ad.StopDiscovery()
        except Exception: pass
    except Exception as e: print("conn err:",e)
for i in range(40):
    if dp().get("ServicesResolved"): break
    time.sleep(0.5)
print("Connected=%s Resolved=%s"%(dp().get("Connected"),dp().get("ServicesResolved")))
om=dbus.Interface(bus.get_object("org.bluez","/"),"org.freedesktop.DBus.ObjectManager")
chars={p:v["org.bluez.GattCharacteristic1"] for p,v in om.GetManagedObjects().items()
       if "org.bluez.GattCharacteristic1" in v and DP in p}
def find(u):
    for p,c in chars.items():
        if str(c["UUID"]).startswith("0000"+u): return p
FEE2=find("fee2"); FEE3=find("fee3"); FEE1=find("fee1")
print("FEE2(out)=%s\nFEE3(in) =%s"%(FEE2,FEE3))
rx=[]
def on_props(iface, changed, inval, path=None):
    if "Value" in changed:
        rx.append((path, bytes(bytearray(changed["Value"]))))
bus.add_signal_receiver(on_props, dbus_interface="org.freedesktop.DBus.Properties",
    signal_name="PropertiesChanged", path_keyword="path")
for cp in (FEE3, FEE1):
    try:
        dbus.Interface(bus.get_object("org.bluez",cp),"org.bluez.GattCharacteristic1").StartNotify()
        print("notify enabled on", cp.split("/")[-1])
    except Exception as e: print("notify err:",str(e)[:60])
def build(ptype, payload=b""):
    ln=len(payload)+5
    return bytes([0xFE,0xEA,(32+(ln>>8))&0xFF, ln&0xFF, ptype&0xFF])+payload
def probe(name, ptype, wait=5.0):
    del rx[:]
    pkt=build(ptype)
    print("\n>>> %s (type=%d / 0x%02X)  TX: %s"%(name,ptype if ptype<128 else ptype-256,ptype&0xFF,pkt.hex()))
    try:
        dbus.Interface(bus.get_object("org.bluez",FEE2),"org.bluez.GattCharacteristic1")\
            .WriteValue(dbus.Array([dbus.Byte(b) for b in pkt],signature='y'),{"type":"command"})
    except Exception as e:
        print("    WRITE FAILED:",str(e)[:80]); return
    loop=GLib.MainLoop()
    GLib.timeout_add(int(wait*1000), lambda: (loop.quit(), False)[1])
    loop.run()
    if not rx: print("    <no response>")
    for path,val in rx:
        print("    RX [%s]: %s"%(path.split("/")[-1], val.hex()))
probe("CONTROL: CMD_QUERY_DISPLAY_WATCH_FACE", 41)
probe("CMD_QUERY_SUPPORT_WATCH_FACE", 0x84)
probe("CMD_QUERY_WATCH_FACE_LAYOUT", 57)
print("\nDisconnecting...")
try: dbus.Interface(bus.get_object("org.bluez",DP),"org.bluez.Device1").Disconnect()
except Exception: pass
