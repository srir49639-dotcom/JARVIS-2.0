"""System control: lock, shutdown, restart, sleep."""
import subprocess
import ctypes
import time
import pyautogui
from speech_engine import speak, listen_yes_no
import config

def _ask_confirmation(action):
    speak(f"Are you sure you want to {action}? Say yes or no.")
    response = listen_yes_no()
    if response is None:
        speak("No response. Cancelled.")
        return False
    for word in config.CONFIRM_WORDS:
        if word in response:
            return True
    speak("Cancelled.")
    return False

def lock_screen():
    speak("Locking the screen.")
    try:
        pyautogui.hotkey("win", "l")
    except Exception:
        ctypes.windll.user32.LockWorkStation()

def shutdown(delay=1):
    if not _ask_confirmation("shut down the laptop"):
        return
    speak("Shutting down. Goodbye.")
    subprocess.run(["shutdown", "/s", "/t", str(delay)], shell=True)

def restart(delay=1):
    if not _ask_confirmation("restart the laptop"):
        return
    speak("Restarting now.")
    subprocess.run(["shutdown", "/r", "/t", str(delay)], shell=True)

def sleep_pc():
    speak("Going to sleep.")
    subprocess.run(
        ["powershell", "-Command",
         "Add-Type -AssemblyName System.Windows.Forms; "
         "[System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"],
        shell=True,
    )

def cancel_shutdown():
    result = subprocess.run(["shutdown", "/a"], shell=True, capture_output=True)
    if result.returncode == 0:
        speak("Shutdown cancelled.")
    else:
        speak("No pending shutdown to cancel.")

def handle(command):
    cmd = command.lower()
    if any(p in cmd for p in ("lock screen", "lock laptop", "lock computer", "lock the screen")):
        lock_screen(); return True
    if any(p in cmd for p in ("shutdown", "shut down", "turn off", "power off")) and "cancel" not in cmd:
        shutdown(); return True
    if any(p in cmd for p in ("restart", "reboot")):
        restart(); return True
    if any(p in cmd for p in ("sleep", "hibernate", "go to sleep")):
        sleep_pc(); return True
    if "cancel shutdown" in cmd or "abort shutdown" in cmd:
        cancel_shutdown(); return True
    return False
