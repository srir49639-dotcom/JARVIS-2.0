"""Command router."""
from colorama import Fore, Style
from speech_engine import speak
import system_control, apps, search, info, system_info, notes
import media_control, alarm, screenshot

_HANDLERS = [
    system_control.handle, screenshot.handle, alarm.handle, notes.handle,
    media_control.handle, system_info.handle, info.handle, search.handle, apps.handle,
]

def dispatch(command):
    if not command or not command.strip():
        return
    cmd = command.lower().strip()
    print(f"{Fore.MAGENTA}[DISPATCH]{Style.RESET_ALL} {cmd}")
    if any(g in cmd for g in ("hello", "hi", "hey jarvis")):
        speak("Hello! I am Jarvis. How can I help?")
        return
    if any(f in cmd for f in ("goodbye", "bye", "exit", "quit")):
        speak("Goodbye!")
        return
    if "help" in cmd or "what can you do" in cmd:
        speak("I open apps and sites, search the web, tell time and weather, notes, alarms, system control, volume, screenshots. Say hey jarvis then your command.")
        return
    for handler in _HANDLERS:
        try:
            if handler(cmd):
                return
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
            speak("Something went wrong. Try again.")
            return
    speak(f"I am not sure how to do that. You said: {command}")
