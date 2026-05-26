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
    m = re.search(r"(\d{1,2})[:\s](\d{2})\s*(am|pm)?", text)
    if m:
        h, mn, p = int(m.group(1)), int(m.group(2)), m.group(3)
        if p == "pm" and h != 12: h += 12
        elif p == "am" and h == 12: h = 0
        return h, mn
    m = re.search(r"(\d{1,2})\s*(am|pm)", text)
    if m:
        h, p = int(m.group(1)), m.group(2)
        if p == "pm" and h != 12: h += 12
        elif p == "am" and h == 12: h = 0
        return h, 0
    return None

def handle(command):
    cmd = command.lower().strip()
    if "alarm" in cmd:
        part = re.sub(r".*alarm\s*(at|for)?\s*", "", cmd).strip()
        parsed = _parse_time(part)
        if parsed:
            set_alarm(parsed[0], parsed[1])
        else:
            speak("Say set alarm at 7 30 am")
        return True
    if "timer" in cmd or "countdown" in cmd:
        m = re.search(r"(\d+)\s*(minute|min|second|sec|hour|hr)", cmd)
        if m:
            n, unit = int(m.group(1)), m.group(2)
            mult = {"minute": 60, "min": 60, "second": 1, "sec": 1, "hour": 3600, "hr": 3600}
            set_timer(n * mult.get(unit, 60))
        else:
            speak("Say set timer for 5 minutes")
        return True
    return False
