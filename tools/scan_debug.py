import dbus, dbus.mainloop.glib, time
import os, sys
# Target device MAC: pass as argv[1], or set WATCH_MAC in the environment.
MAC = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("WATCH_MAC", "")).upper()
if not MAC:
    sys.exit("usage: %s <MAC>   (or set WATCH_MAC)" % sys.argv[0])

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
adapter = dbus.Interface(bus.get_object("org.bluez","/org/bluez/hci0"),"org.bluez.Adapter1")
try:
    adapter.SetDiscoveryFilter({"Transport":"le","DuplicateData":dbus.Boolean(True)})
    print("filter set")
except Exception as e: print("filter err:",e)
try: adapter.StartDiscovery(); print("discovery started")
except Exception as e: print("start err:",e)
om = dbus.Interface(bus.get_object("org.bluez","/"),"org.freedesktop.DBus.ObjectManager")
for i in range(24):
    time.sleep(1)
    objs = om.GetManagedObjects()
    devs = {p:v["org.bluez.Device1"] for p,v in objs.items() if "org.bluez.Device1" in v}
    if any(MAC.replace(":", "_") in p for p in devs):
        print("FOUND at t=%ds" % i); break
else:
    print("not found after 24s")
objs = om.GetManagedObjects()
devs = {p:v["org.bluez.Device1"] for p,v in objs.items() if "org.bluez.Device1" in v}
print("total device objects:",len(devs))
for p,d in devs.items():
    print("  %s  name=%r rssi=%s" % (p.split("/")[-1], d.get("Name"), d.get("RSSI")))
try: adapter.StopDiscovery()
except Exception: pass
