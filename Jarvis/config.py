# ============================================================
# JARVIS - Unified Configuration (GUI + Voice)
# ============================================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
DATA_DIR = os.path.join(BASE_DIR, "data")
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
ALARMS_FILE = os.path.join(MEMORY_DIR, "jarvis_alarms.json")

# OpenAI API
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key-here")
OPENAI_MODEL = "gpt-3.5-turbo"

# Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-gemini-api-key-here")
GEMINI_MODEL = "gemini-2.5-flash"

# Spotify API (Phase 4)
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# Primary wake phrase (must appear in speech)
WAKE_WORD = "hey jarvis"
WAKE_WORDS = ("hey jarvis", "ok jarvis", "okay jarvis", "jarvis")

# Speech recognition
ENERGY_THRESHOLD = 150
PAUSE_THRESHOLD = 1.0
PHRASE_TIME_LIMIT = 10
LISTEN_TIMEOUT = 8
DYNAMIC_ENERGY = False

# After wake: follow-up commands without saying Jarvis again
ACTIVE_LISTEN_SECONDS = 30
ALLOW_DIRECT_COMMANDS = True
POST_SPEAK_DELAY = 0.6

# TTS
TTS_RATE = 175
TTS_VOLUME = 1.0
TTS_VOICE_INDEX = None

# GUI
GUI_THEME = "dark"
GUI_COLOR_THEME = "blue"
GUI_WIDTH = 960
GUI_HEIGHT = 700

BATTERY_LOW_THRESHOLD = 20
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
DEFAULT_CITY = "London"
ASSISTANT_NAME = "JARVIS"
USER_NAME = "Sir"

CONFIRM_WORDS = ("yes", "yeah", "yep", "confirm", "sure", "proceed", "do it")
CANCEL_WORDS = ("no", "nope", "cancel", "abort", "never mind")

# Voice commands that shut down JARVIS itself (not the PC)
EXIT_COMMANDS = (
    "stop",
    "stop jarvis",
    "stop listening",
    "exit",
    "exit jarvis",
    "quit",
    "quit jarvis",
    "goodbye",
    "good bye",
    "bye",
    "farewell",
    "shut down jarvis",
    "turn off jarvis",
    "go offline",
    "deactivate",
    "deactivate jarvis",
    "close jarvis",
    "jarvis stop",
    "jarvis exit",
    "jarvis quit",
    "jarvis off",
    "power off jarvis",
)

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://www.reddit.com",
    "stack overflow": "https://stackoverflow.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "wikipedia": "https://www.wikipedia.org",
    "linkedin": "https://www.linkedin.com",
    "netflix": "https://www.netflix.com",
    "chatgpt": "https://chat.openai.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "amazon": "https://www.amazon.com",
    "whatsapp": "https://web.whatsapp.com",
}

APPLICATIONS = {
    "vs code": "code",
    "visual studio code": "code",
    "vscode": "code",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
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
    "zoom": "zoom",
    "teams": "msteams",
    "slack": "slack",
    "snipping tool": "snippingtool",
    "vlc": "vlc",
    "steam": "steam",
}
