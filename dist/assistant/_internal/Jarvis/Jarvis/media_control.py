"""Media and volume keys."""
import re
import pyautogui
from speech_engine import speak

def volume_up(n=5):
    for _ in range(n):
        pyautogui.press("volumeup")
    speak("Volume up.")

def volume_down(n=5):
    for _ in range(n):
        pyautogui.press("volumedown")
    speak("Volume down.")

def handle(command):
    cmd = command.lower().strip()
    m = re.search(r"(?:set volume|volume)\s+(?:to\s+)?(\d+)", cmd)
    if m:
        level = int(m.group(1))
        for _ in range(50):
            pyautogui.press("volumedown")
        for _ in range(level // 2):
            pyautogui.press("volumeup")
        speak(f"Volume about {level} percent.")
        return True
    if "volume up" in cmd or "louder" in cmd:
        volume_up(); return True
    if "volume down" in cmd or "quieter" in cmd:
        volume_down(); return True
    if "mute" in cmd:
        pyautogui.press("volumemute"); speak("Muted."); return True
    if any(p in cmd for p in ("play", "pause", "play pause")):
        pyautogui.press("playpause"); speak("Play pause."); return True
    if "next" in cmd:
        pyautogui.press("nexttrack"); speak("Next track."); return True
    if "previous" in cmd or "prev" in cmd:
        pyautogui.press("prevtrack"); speak("Previous."); return True
    return False
