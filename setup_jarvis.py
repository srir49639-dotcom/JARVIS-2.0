"""
Jarvis AI Assistant -- Legacy self-extractor (optional).
Unified GUI+voice project: Jarvis/  ->  python assistant.py
This script still builds flat Jarvis_AI/ if you want the old layout:
  python setup_jarvis.py --legacy
"""

import os
import sys
import textwrap

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Jarvis_AI")
UNIFIED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Jarvis")


def _files():
    """Return all project files as {filename: content}."""
    return {
        "config.py": _CONFIG,
        "speech_engine.py": _SPEECH,
        "system_control.py": _SYSTEM,
        "apps.py": _APPS,
        "search.py": _SEARCH,
        "info.py": _INFO,
        "system_info.py": _SYSINFO,
        "notes.py": _NOTES,
        "media_control.py": _MEDIA,
        "alarm.py": _ALARM,
        "screenshot.py": _SCREENSHOT,
        "commands.py": _COMMANDS,
        "main.py": _MAIN,
        "requirements.txt": _REQUIREMENTS,
        "run_jarvis.py": _RUN,
    }


_CONFIG = textwrap.dedent('''\
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
    ''')

_SPEECH = textwrap.dedent('''\
    """
    Jarvis AI Assistant -- Speech Engine
    """
    import speech_recognition as sr
    import pyttsx3
    import threading
    import time
    import re
    from colorama import Fore, Style
    import config

    _tts_lock = threading.Lock()
    _tts_engine = None

    def _get_tts_engine():
        global _tts_engine
        if _tts_engine is None:
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty("rate", config.TTS_RATE)
            _tts_engine.setProperty("volume", config.TTS_VOLUME)
            voices = _tts_engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or "zira" not in v.name.lower():
                    _tts_engine.setProperty("voice", v.id)
                    break
        return _tts_engine

    def speak(text):
        print(f"{Fore.CYAN}[JARVIS]{Style.RESET_ALL} {text}")
        with _tts_lock:
            engine = _get_tts_engine()
            engine.say(text)
            engine.runAndWait()
        time.sleep(0.5)

    _recogniser = None

    def _get_recogniser():
        global _recogniser
        if _recogniser is None:
            _recogniser = sr.Recognizer()
            _recogniser.energy_threshold = config.ENERGY_THRESHOLD
            _recogniser.pause_threshold = config.PAUSE_THRESHOLD
            _recogniser.dynamic_energy_threshold = config.DYNAMIC_ENERGY
        return _recogniser

    def listen_for_wake_word():
        recogniser = _get_recogniser()
        print(f"{Fore.YELLOW}[LISTENING]{Style.RESET_ALL} Say \\"{config.WAKE_WORD}\\" ...")
        with sr.Microphone() as source:
            recogniser.adjust_for_ambient_noise(source, duration=0.5)
            while True:
                try:
                    audio = recogniser.listen(source, timeout=None, phrase_time_limit=5)
                    text = recogniser.recognize_google(audio).lower().strip()
                    print(f"{Fore.WHITE}[HEARD]{Style.RESET_ALL} {text}")
                    if config.WAKE_WORD in text:
                        return text
                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"{Fore.RED}[STT ERROR]{Style.RESET_ALL} {e}")
                    time.sleep(1)

    def extract_command_from_wake(text):
        cmd = text.lower()
        cmd = cmd.replace(config.WAKE_WORD, "").strip()
        cmd = re.sub(r"^(hey|ok|okay)\\s+", "", cmd)
        return cmd.strip()

    def listen_for_command(prompt="Yes? How can I help?"):
        recogniser = _get_recogniser()
        speak(prompt)
        with sr.Microphone() as source:
            recogniser.adjust_for_ambient_noise(source, duration=0.3)
            print(f"{Fore.GREEN}[COMMAND]{Style.RESET_ALL} Listening...")
            try:
                audio = recogniser.listen(source, timeout=8, phrase_time_limit=config.PHRASE_TIME_LIMIT)
            except sr.WaitTimeoutError:
                speak("I did not hear anything. Try again.")
                return None
        try:
            text = recogniser.recognize_google(audio).lower().strip()
            print(f"{Fore.GREEN}[COMMAND TEXT]{Style.RESET_ALL} \\"{text}\\"")
            return text
        except sr.UnknownValueError:
            speak("Sorry, I did not catch that.")
            return None
        except sr.RequestError:
            speak("Speech service is unavailable. Check your internet.")
            return None

    def listen_yes_no():
        recogniser = _get_recogniser()
        with sr.Microphone() as source:
            recogniser.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = recogniser.listen(source, timeout=8, phrase_time_limit=4)
                return recogniser.recognize_google(audio).lower().strip()
            except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
                return None
    ''')

_SYSTEM = textwrap.dedent('''\
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
    ''')

_APPS = textwrap.dedent('''\
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
    ''')

_SEARCH = textwrap.dedent('''\
    """Google and YouTube search."""
    import webbrowser
    import urllib.parse
    from speech_engine import speak

    def google_search(query):
        if not query:
            speak("What should I search for?")
            return
        url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
        speak(f"Searching Google for {query}.")
        webbrowser.open(url)

    def youtube_search(query):
        if not query:
            speak("What should I search on YouTube?")
            return
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
        speak(f"Searching YouTube for {query}.")
        webbrowser.open(url)

    def handle(command):
        cmd = command.lower().strip()
        for prefix in ("search youtube for ", "youtube search ", "play on youtube ", "youtube "):
            if cmd.startswith(prefix):
                youtube_search(cmd[len(prefix):].strip())
                return True
        for prefix in ("search for ", "search ", "google search ", "google for ", "look up ", "find "):
            if cmd.startswith(prefix):
                google_search(cmd[len(prefix):].strip())
                return True
        return False
    ''')

_INFO = textwrap.dedent('''\
    """Time, date, weather, jokes, Wikipedia."""
    import datetime
    import random
    import re
    import requests
    import wikipedia
    from speech_engine import speak
    import config

    def tell_time():
        now = datetime.datetime.now()
        speak(f"The time is {now.strftime('%I:%M %p')}.")

    def tell_date():
        now = datetime.datetime.now()
        speak(f"Today is {now.strftime('%A, %B %d, %Y')}.")

    def get_weather(city=""):
        city = city or config.DEFAULT_CITY
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=3"
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                speak(f"Weather in {city}: {r.text.strip()}")
            else:
                speak(f"Could not get weather for {city}.")
        except requests.RequestException:
            speak("Weather service unavailable. Check internet.")

    def wiki_summary(query):
        if not query:
            speak("What topic?")
            return
        try:
            wikipedia.set_lang("en")
            speak(wikipedia.summary(query, sentences=2, auto_suggest=True))
        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"Did you mean {e.options[0]}?")
        except wikipedia.exceptions.PageError:
            speak(f"No Wikipedia page for {query}.")
        except Exception:
            speak("Wikipedia error.")

    _JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs.",
        "Why do Java developers wear glasses? Because they do not C sharp.",
        "A SQL query walks into a bar and asks: Can I join you?",
    ]

    def tell_joke():
        speak(random.choice(_JOKES))

    def handle(command):
        cmd = command.lower().strip()
        if any(p in cmd for p in ("what time", "current time", "tell me the time", "what is the time")):
            tell_time(); return True
        if any(p in cmd for p in ("what date", "today", "what day", "current date")):
            tell_date(); return True
        if "weather" in cmd or "temperature" in cmd or "forecast" in cmd:
            city = ""
            for phrase in ("weather in ", "weather for ", "temperature in "):
                if phrase in cmd:
                    city = cmd.split(phrase, 1)[-1].strip()
            get_weather(city); return True
        if "joke" in cmd or "funny" in cmd:
            tell_joke(); return True
        for trigger in ("tell me about ", "what is ", "who is ", "wikipedia ", "wiki "):
            if cmd.startswith(trigger):
                wiki_summary(cmd[len(trigger):].strip())
                return True
        return False
    ''')

_SYSINFO = textwrap.dedent('''\
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
        d = psutil.disk_usage("C:\\\\")
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
    ''')

_NOTES = textwrap.dedent('''\
    """Notes and todos."""
    import os
    import datetime
    from speech_engine import speak
    import config

    def _ensure(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "w").close()

    def _read(path):
        _ensure(path)
        with open(path, "r", encoding="utf-8") as f:
            return [l.rstrip() for l in f if l.strip()]

    def _append(path, line):
        _ensure(path)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\\n")

    def add_note(note):
        if not note:
            speak("What should I note?")
            return
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        _append(config.NOTES_FILE, f"[{ts}] {note}")
        speak(f"Noted: {note}")

    def read_notes():
        lines = _read(config.NOTES_FILE)
        if not lines:
            speak("No notes.")
            return
        for line in lines[-5:]:
            speak(line.split("] ", 1)[-1] if "] " in line else line)

    def add_todo(task):
        if not task:
            speak("What task?")
            return
        _append(config.TODO_FILE, f"[ ] {task}")
        speak(f"Added task: {task}")

    def read_todos():
        lines = _read(config.TODO_FILE)
        pending = [l[4:] for l in lines if l.startswith("[ ]")]
        if not pending:
            speak("Todo list empty.")
            return
        for t in pending[:5]:
            speak(t)

    def handle(command):
        cmd = command.lower().strip()
        for prefix in ("note ", "remember ", "save note "):
            if cmd.startswith(prefix):
                add_note(command[len(prefix):].strip())
                return True
        if any(p in cmd for p in ("read notes", "show notes", "my notes")):
            read_notes(); return True
        for prefix in ("add task ", "todo ", "add to todo "):
            if cmd.startswith(prefix):
                add_todo(command[len(prefix):].strip())
                return True
        if any(p in cmd for p in ("show tasks", "read todo", "my tasks")):
            read_todos(); return True
        return False
    ''')

_MEDIA = textwrap.dedent('''\
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
        m = re.search(r"(?:set volume|volume)\\s+(?:to\\s+)?(\\d+)", cmd)
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
    ''')

_ALARM = textwrap.dedent('''\
    """Alarms and timers."""
    import datetime
    import json
    import os
    import re
    import threading
    import time
    import uuid
    from speech_engine import speak
    import config

    def _load():
        if not os.path.exists(config.ALARMS_FILE):
            return []
        try:
            with open(config.ALARMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(alarms):
        os.makedirs(os.path.dirname(config.ALARMS_FILE), exist_ok=True)
        with open(config.ALARMS_FILE, "w", encoding="utf-8") as f:
            json.dump(alarms, f, indent=2)

    def _watcher():
        while True:
            time.sleep(30)
            now = datetime.datetime.now()
            alarms = _load()
            left = []
            for a in alarms:
                if now >= datetime.datetime.fromisoformat(a["time"]):
                    speak(f"Alarm {a.get('label', '')} is going off!")
                else:
                    left.append(a)
            if len(left) != len(alarms):
                _save(left)

    _started = False

    def _ensure_thread():
        global _started
        if not _started:
            threading.Thread(target=_watcher, daemon=True).start()
            _started = True

    def set_alarm(hour, minute, label="alarm"):
        _ensure_thread()
        now = datetime.datetime.now()
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dt <= now:
            dt += datetime.timedelta(days=1)
        alarms = _load()
        alarms.append({"id": str(uuid.uuid4())[:8], "time": dt.isoformat(), "label": label})
        _save(alarms)
        speak(f"Alarm set for {dt.strftime('%I:%M %p')}.")

    def set_timer(seconds):
        def fire():
            time.sleep(seconds)
            speak("Timer done!")
        threading.Thread(target=fire, daemon=True).start()
        speak(f"Timer set for {seconds} seconds.")

    def _parse_time(text):
        m = re.search(r"(\\d{1,2})[:\\s](\\d{2})\\s*(am|pm)?", text)
        if m:
            h, mn, p = int(m.group(1)), int(m.group(2)), m.group(3)
            if p == "pm" and h != 12: h += 12
            elif p == "am" and h == 12: h = 0
            return h, mn
        m = re.search(r"(\\d{1,2})\\s*(am|pm)", text)
        if m:
            h, p = int(m.group(1)), m.group(2)
            if p == "pm" and h != 12: h += 12
            elif p == "am" and h == 12: h = 0
            return h, 0
        return None

    def handle(command):
        cmd = command.lower().strip()
        if "alarm" in cmd:
            part = re.sub(r".*alarm\\s*(at|for)?\\s*", "", cmd).strip()
            parsed = _parse_time(part)
            if parsed:
                set_alarm(parsed[0], parsed[1])
            else:
                speak("Say set alarm at 7 30 am")
            return True
        if "timer" in cmd or "countdown" in cmd:
            m = re.search(r"(\\d+)\\s*(minute|min|second|sec|hour|hr)", cmd)
            if m:
                n, unit = int(m.group(1)), m.group(2)
                mult = {"minute": 60, "min": 60, "second": 1, "sec": 1, "hour": 3600, "hr": 3600}
                set_timer(n * mult.get(unit, 60))
            else:
                speak("Say set timer for 5 minutes")
            return True
        return False
    ''')

_SCREENSHOT = textwrap.dedent('''\
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
    ''')

_COMMANDS = textwrap.dedent('''\
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
    ''')

_MAIN = textwrap.dedent('''\
    """Jarvis main loop."""
    import os
    import sys
    import time
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    import config
    from speech_engine import speak, listen_for_wake_word, listen_for_command, extract_command_from_wake
    from commands import dispatch

    def run():
        print(Fore.CYAN + "JARVIS AI Assistant" + Style.RESET_ALL)
        print(f'Wake word: "{config.WAKE_WORD}"\\n')
        speak("Jarvis online. Say hey jarvis to wake me.")
        errors = 0
        while True:
            try:
                heard = listen_for_wake_word()
                if not heard:
                    continue
                cmd = extract_command_from_wake(heard)
                if not cmd:
                    cmd = listen_for_command()
                if cmd:
                    dispatch(cmd)
                    errors = 0
                else:
                    errors += 1
                time.sleep(0.3)
            except KeyboardInterrupt:
                speak("Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
                errors += 1
                if errors > 5:
                    errors = 0
                    time.sleep(2)

    if __name__ == "__main__":
        run()
    ''')

_REQUIREMENTS = textwrap.dedent('''\
    SpeechRecognition>=3.10.0
    pyttsx3>=2.90
    pyautogui>=0.9.54
    psutil>=5.9.0
    requests>=2.31.0
    wikipedia>=1.4.0
    colorama>=0.4.6
    keyboard>=0.13.5
    Pillow>=10.0.0
    PyAudio>=0.2.14
    ''')

_RUN = textwrap.dedent('''\
    """Quick launcher."""
    import os
    import runpy
    import sys
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.getcwd())
    runpy.run_path("main.py", run_name="__main__")
    ''')


def main():
    if "--legacy" not in sys.argv:
        print("JARVIS is unified in the Jarvis/ folder (GUI + voice).")
        print(f"  cd \"{UNIFIED_DIR}\"")
        print("  python install_jarvis.py")
        print("  python assistant.py")
        print("\nTo build the old flat Jarvis_AI/ layout: python setup_jarvis.py --legacy")
        return

    print(f"Creating legacy Jarvis_AI project in:\n  {PROJECT_DIR}\n")
    os.makedirs(os.path.join(PROJECT_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_DIR, "screenshots"), exist_ok=True)

    for filename, content in _files().items():
        path = os.path.join(PROJECT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrote {filename}")

    print("\n" + "=" * 50)
    print("  Project created successfully!")
    print(f"\n  cd \"{PROJECT_DIR}\"")
    print("  pip install -r requirements.txt")
    print("  pip install PyAudio")
    print("  python main.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
