"""Screenshots."""
import datetime
import os
import pyautogui
from speech_engine import speak
import config

def take_screenshot():
    os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)
    name = datetime.datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
    path = os.path.join(config.SCREENSHOTS_DIR, name)
    pyautogui.screenshot().save(path)
    speak(f"Screenshot saved as {name}.")

def handle(command):
    cmd = command.lower().strip()
    if "screenshot" in cmd or "capture screen" in cmd:
        take_screenshot()
        return True
    return False
