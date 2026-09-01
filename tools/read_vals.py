import dbus, dbus.mainloop.glib, time
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SystemBus(); MAC="AA:BB:CC:DD:EE:FF"; DP="/org/bluez/hci0/dev_"+MAC.replace(":","_")
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
        ad.StopDiscovery()
    except Exception as e: print("conn err:",e)
for i in range(30):
    if dp().get("ServicesResolved"): break
    time.sleep(0.5)
om=dbus.Interface(bus.get_object("org.bluez","/"),"org.freedesktop.DBus.ObjectManager")
objs=om.GetManagedObjects()
chars={p:v["org.bluez.GattCharacteristic1"] for p,v in objs.items() if "org.bluez.GattCharacteristic1" in v and DP in p}
def find(u):
    for p,c in chars.items():
        if str(c["UUID"]).startswith("0000"+u): return p
    return None
def rd(u):
    p=find(u)
    if not p: return None
    try: return bytes(bytearray(dbus.Interface(bus.get_object("org.bluez",p),"org.bluez.GattCharacteristic1").ReadValue({})))
    except Exception as e: return ("ERR",str(e)[:70])
b=rd("2a19"); print("Battery(0x2A19) raw=%s -> %s%%"%(b.hex() if isinstance(b,bytes) else b, b[0] if isinstance(b,bytes) and b else "?"))
s=rd("fee1")
if isinstance(s,bytes) and len(s)>=9:
    u24=lambda o: int.from_bytes(s[o:o+3],"little")
    print("Steps(0xFEE1) raw=%s len=%d"%(s.hex(),len(s)))
    print("   LE uint24 triple -> distance=%d steps=%d calories=%d"%(u24(0),u24(3),u24(6)))
    be=lambda o: int.from_bytes(s[o:o+3],"big")
    print("   BE uint24 triple -> distance=%d steps=%d calories=%d"%(be(0),be(3),be(6)))
else: print("Steps(0xFEE1) =",s)
for u,n in [("fee4","FEE4"),("fec9","FEC9"),("fea1","FEA1"),("2a38","HR BodySensorLoc")]:
    v=rd(u); print("%s = %s"%(n, v.hex() if isinstance(v,bytes) else v))
print("\nDisconnecting...")
try:
    dbus.Interface(bus.get_object("org.bluez",DP),"org.bluez.Device1").Disconnect(); print("disconnected")
except Exception as e: print("disc err:",e)
