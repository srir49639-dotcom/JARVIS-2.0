"""
Jarvis AI Assistant -- Configuration
"""
import os

WAKE_WORD = "hey jarvis"

ENERGY_THRESHOLD = 180
PAUSE_THRESHOLD = 0.8
PHRASE_TIME_LIMIT = 8
DYNAMIC_ENERGY = False

TTS_RATE = 185
TTS_VOLUME = 1.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_FILE = os.path.join(BASE_DIR, "data", "jarvis_notes.txt")
TODO_FILE = os.path.join(BASE_DIR, "data", "jarvis_todo.txt")
ALARMS_FILE = os.path.join(BASE_DIR, "data", "jarvis_alarms.json")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

DEFAULT_CITY = "London"

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://www.reddit.com",
    "stack overflow": "https://stackoverflow.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "wikipedia": "https://www.wikipedia.org",
    "linkedin": "https://www.linkedin.com",
    "netflix": "https://www.netflix.com",
    "chatgpt": "https://chat.openai.com",
    "instagram": "https://www.instagram.com",
}

APPLICATIONS = {
    "vs code": "code",
    "visual studio code": "code",
    "vscode": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "paint": "mspaint",
    "task manager": "taskmgr",
    "file explorer": "explorer",
    "explorer": "explorer",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "discord": "discord",
    "telegram": "telegram",
    "snipping tool": "snippingtool",
    "zoom": "zoom",
    "teams": "msteams",
}

CONFIRM_WORDS = ("yes", "yeah", "yep", "confirm", "sure", "proceed", "do it")
CANCEL_WORDS = ("no", "nope", "cancel", "stop", "abort", "never mind")
