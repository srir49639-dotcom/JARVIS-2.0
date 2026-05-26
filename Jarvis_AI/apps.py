"""App and website launcher."""
import subprocess
import webbrowser
from speech_engine import speak
import config

def open_website(name):
    key = name.strip().lower()
    for site_name, url in config.WEBSITES.items():
        if site_name in key:
            speak(f"Opening {site_name}.")
            webbrowser.open(url)
            return True
    return False

def open_application(name):
    key = name.strip().lower()
    for app_name, exe in config.APPLICATIONS.items():
        if app_name in key:
            speak(f"Opening {app_name}.")
            try:
                if exe in ("chrome", "firefox", "msedge", "code", "spotify", "discord"):
                    subprocess.Popen(f"cmd /c start {exe}", shell=True,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(exe, shell=True,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                speak(f"Could not open {app_name}. {e}")
            return True
    return False

def handle(command):
    cmd = command.lower().strip()
    target = None
    for prefix in ("open ", "launch ", "start ", "run "):
        if cmd.startswith(prefix):
            target = cmd[len(prefix):]
            break
    if target is None:
        for site in config.WEBSITES:
            if site in cmd:
                target = site
                break
        if target is None:
            for app in config.APPLICATIONS:
                if app in cmd:
                    target = app
                    break
    if target is None:
        return False
    if open_website(target) or open_application(target):
        return True
    speak(f"I could not find {target}.")
    return True
