# ============================================================
# JARVIS - Alarm & Timer Service (from Jarvis_AI)
# ============================================================

import datetime
import json
import os
import re
import threading
import time
import uuid

import config


class AlarmService:
    """Persistent alarms + countdown timers."""

    _started = False
    _lock = threading.Lock()

    def __init__(self, speak_callback):
        self._speak = speak_callback
        self._ensure_watcher()

    def _path(self):
        return config.ALARMS_FILE

    def _load(self):
        if not os.path.exists(self._path()):
            return []
        try:
            with open(self._path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, alarms):
        os.makedirs(os.path.dirname(self._path()), exist_ok=True)
        with open(self._path(), "w", encoding="utf-8") as f:
            json.dump(alarms, f, indent=2)

    def _ensure_watcher(self):
        if AlarmService._started:
            return
        AlarmService._started = True

        def watch():
            while True:
                time.sleep(30)
                now = datetime.datetime.now()
                with AlarmService._lock:
                    alarms = self._load()
                    left = []
                    for a in alarms:
                        if now >= datetime.datetime.fromisoformat(a["time"]):
                            self._speak(f"Alarm {a.get('label', '')} is going off, sir!")
                        else:
                            left.append(a)
                    if len(left) != len(alarms):
                        self._save(left)

        threading.Thread(target=watch, daemon=True).start()

    def set_alarm(self, hour, minute, label="alarm"):
        now = datetime.datetime.now()
        dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if dt <= now:
            dt += datetime.timedelta(days=1)
        with AlarmService._lock:
            alarms = self._load()
            alarms.append({
                "id": str(uuid.uuid4())[:8],
                "time": dt.isoformat(),
                "label": label,
            })
            self._save(alarms)
        return True, f"Alarm set for {dt.strftime('%I:%M %p')}, sir."

    def set_timer_seconds(self, seconds, label="timer"):
        if seconds <= 0:
            return False, "Timer must be positive, sir."

        def fire():
            time.sleep(seconds)
            self._speak(f"Your {label} is complete, sir!")

        threading.Thread(target=fire, daemon=True).start()
        return True, f"Timer set for {seconds} seconds, sir."

    @staticmethod
    def parse_time(text):
        text = text.lower().strip()
        m = re.search(r"(\d{1,2})[:\s](\d{2})\s*(am|pm)?", text)
        if m:
            h, mn, p = int(m.group(1)), int(m.group(2)), m.group(3)
            if p == "pm" and h != 12:
                h += 12
            elif p == "am" and h == 12:
                h = 0
            return h, mn
        m = re.search(r"(\d{1,2})\s*(am|pm)", text)
        if m:
            h, p = int(m.group(1)), m.group(2)
            if p == "pm" and h != 12:
                h += 12
            elif p == "am" and h == 12:
                h = 0
            return h, 0
        return None

    @staticmethod
    def parse_duration_seconds(text):
        total = 0
        for pattern, mult in [
            (r"(\d+)\s*hour", 3600), (r"(\d+)\s*hr", 3600),
            (r"(\d+)\s*minute", 60), (r"(\d+)\s*min", 60),
            (r"(\d+)\s*second", 1), (r"(\d+)\s*sec", 1),
        ]:
            m = re.search(pattern, text)
            if m:
                total += int(m.group(1)) * mult
        if total == 0:
            m = re.search(r"\b(\d+)\b", text)
            if m:
                total = int(m.group(1)) * 60
        return total

    def handle(self, cmd):
        if "alarm" in cmd:
            part = re.sub(r".*alarm\s*(at|for)?\s*", "", cmd).strip()
            parsed = self.parse_time(part)
            if parsed:
                return self.set_alarm(parsed[0], parsed[1])
            return False, "Say set alarm at 7 30 am, sir."
        if "timer" in cmd or "countdown" in cmd:
            sec = self.parse_duration_seconds(cmd)
            if sec > 0:
                return self.set_timer_seconds(sec)
            return False, "Say set timer for 5 minutes, sir."
        return None
