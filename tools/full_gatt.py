import dbus, dbus.mainloop.glib, time
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SystemBus(); MAC="AA:BB:CC:DD:EE:FF"; DP="/org/bluez/hci0/dev_"+MAC.replace(":","_")
ad=dbus.Interface(bus.get_object("org.bluez","/org/bluez/hci0"),"org.bluez.Adapter1")
def dprops(): return dbus.Interface(bus.get_object("org.bluez",DP),"org.freedesktop.DBus.Properties").GetAll("org.bluez.Device1")
try:
    if not dprops().get("Connected"):
        ad.SetDiscoveryFilter({"Transport":"le"}); ad.StartDiscovery(); time.sleep(3)
        dbus.Interface(bus.get_object("org.bluez",DP),"org.bluez.Device1").Connect()
        try: ad.StopDiscovery()
        except Exception: pass
except Exception as e: print("conn:",e)
for i in range(30):
    if dprops().get("ServicesResolved"): break
    time.sleep(0.5)
print("Connected=%s ServicesResolved=%s\n"%(dprops().get("Connected"),dprops().get("ServicesResolved")))
om=dbus.Interface(bus.get_object("org.bluez","/"),"org.freedesktop.DBus.ObjectManager")
objs=om.GetManagedObjects()
svcs={p:v["org.bluez.GattService1"] for p,v in objs.items() if "org.bluez.GattService1" in v and DP in p}
chars={p:v["org.bluez.GattCharacteristic1"] for p,v in objs.items() if "org.bluez.GattCharacteristic1" in v and DP in p}
READABLE_NAMES={"00002a00":"Device Name","00002a24":"Model Number","00002a25":"Serial Number",
 "00002a26":"Firmware Rev","00002a27":"Hardware Rev","00002a28":"Software Rev","00002a29":"Manufacturer",
 "00002a19":"Battery Level","00002a23":"System ID","00002a50":"PnP ID"}
for sp in sorted(svcs, key=lambda p:svcs[p]["UUID"]):
    print("SERVICE %s"%svcs[sp]["UUID"])
    for cp in sorted(chars):
        c=chars[cp]
        if str(c["Service"])!=sp: continue
        u=str(c["UUID"]); flags=",".join(str(f) for f in c.get("Flags",[]))
        line="   %s  [%s]"%(u,flags)
        short=u[:8]
        if "read" in flags and short in READABLE_NAMES:
            try:
                v=dbus.Interface(bus.get_object("org.bluez",cp),"org.bluez.GattCharacteristic1").ReadValue({})
                b=bytes(bytearray(v))
                try: txt=b.decode("utf-8").strip("\x00")
                except Exception: txt=None
                line+="  %s = %r"%(READABLE_NAMES[short], txt if txt else b.hex())
            except Exception as e: line+="  <read failed: %s>"%str(e)[:60]
        print(line)
    print()
