"""Battery, CPU, RAM, disk, internet."""
import socket
import urllib.request
import psutil
from speech_engine import speak

def tell_battery():
    b = psutil.sensors_battery()
    if b is None:
        speak("No battery on this device.")
        return
    status = "charging" if b.power_plugged else "on battery"
    speak(f"Battery {int(b.percent)} percent, {status}.")

def tell_cpu():
    speak(f"CPU usage {psutil.cpu_percent(interval=1)} percent.")

def tell_ram():
    m = psutil.virtual_memory()
    speak(f"RAM {m.percent} percent. {round(m.used/1e9,1)} GB used of {round(m.total/1e9,1)} GB.")

def tell_disk():
    d = psutil.disk_usage("C:\\")
    speak(f"C drive {d.percent} percent full. {round(d.free/1e9,1)} GB free.")

def tell_internet():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=3)
        speak("Internet is connected.")
    except Exception:
        speak("No internet connection.")

def system_overview():
    parts = [f"CPU {psutil.cpu_percent(interval=0.5)}%"]
    parts.append(f"RAM {psutil.virtual_memory().percent}%")
    b = psutil.sensors_battery()
    if b:
        parts.append(f"battery {int(b.percent)}%")
    speak("System: " + ", ".join(parts))

def handle(command):
    cmd = command.lower().strip()
    if "battery" in cmd:
        tell_battery(); return True
    if "cpu" in cmd or "processor" in cmd:
        tell_cpu(); return True
    if "ram" in cmd or "memory" in cmd:
        tell_ram(); return True
    if "disk" in cmd or "storage" in cmd:
        tell_disk(); return True
    if "internet" in cmd or "wifi" in cmd or "network" in cmd:
        tell_internet(); return True
    if "system status" in cmd or "system info" in cmd:
        system_overview(); return True
    return False
