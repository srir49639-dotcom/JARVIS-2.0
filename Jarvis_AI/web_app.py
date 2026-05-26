"""Deployable web server for the Jarvis HUD.

This server intentionally avoids desktop-only features such as microphone
access, text-to-speech engines, screenshots, and app launching. It gives the
existing HUD a small HTTP API that works on hosts like Render or Railway.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import random
import sys
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
WEB_DIR = PROJECT_DIR / "Jarvis" / "gui" / "web"
DATA_DIR = BASE_DIR / "data"
NOTES_FILE = DATA_DIR / "jarvis_notes.txt"
TODO_FILE = DATA_DIR / "jarvis_todo.txt"

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why do Java developers wear glasses? Because they do not C sharp.",
    "A SQL query walks into a bar and asks: Can I join you?",
]


def _json_response(handler: SimpleHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: SimpleHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def _ensure_data_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def _append_line(path: Path, line: str) -> None:
    _ensure_data_file(path)
    with path.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


def _read_lines(path: Path) -> list[str]:
    _ensure_data_file(path)
    with path.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def _system_status() -> dict:
    status = {
        "cpu": 0,
        "ram": 0,
        "battery": None,
        "plugged": False,
        "mode": "ONLINE",
        "serverTime": _dt.datetime.now().isoformat(),
    }
    try:
        import psutil  # type: ignore

        status["cpu"] = psutil.cpu_percent(interval=0)
        status["ram"] = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        if battery:
            status["battery"] = battery.percent
            status["plugged"] = battery.power_plugged
    except Exception:
        status["mode"] = "ONLINE"
    return status


def _weather(city: str) -> str:
    city = city.strip() or "London"
    url = "https://wttr.in/" + urllib.parse.quote(city) + "?format=3"
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            return response.read().decode("utf-8").strip()
    except Exception:
        return f"Weather service is unavailable for {city}."


def process_command(command: str) -> dict:
    original = command.strip()
    cmd = original.lower()
    now = _dt.datetime.now()

    if not cmd:
        return {"reply": "Enter a command.", "actions": []}

    if any(word in cmd for word in ("hello", "hi", "hey jarvis")):
        return {"reply": "Hello. Jarvis web core is online.", "actions": []}

    if "help" in cmd or "what can you do" in cmd:
        return {
            "reply": "Try time, date, weather in London, joke, note, show notes, todo, show tasks, search cats, or youtube lo-fi.",
            "actions": [],
        }

    if any(phrase in cmd for phrase in ("what time", "current time", "tell me the time", "time")):
        return {"reply": f"The time is {now.strftime('%I:%M %p')}.", "actions": []}

    if any(phrase in cmd for phrase in ("what date", "current date", "what day", "today")):
        return {"reply": f"Today is {now.strftime('%A, %B %d, %Y')}.", "actions": []}

    if "weather" in cmd or "temperature" in cmd or "forecast" in cmd:
        city = ""
        for phrase in ("weather in ", "weather for ", "temperature in "):
            if phrase in cmd:
                city = cmd.split(phrase, 1)[-1].strip()
                break
        return {"reply": _weather(city), "actions": []}

    if "joke" in cmd or "funny" in cmd:
        return {"reply": random.choice(JOKES), "actions": []}

    for prefix in ("note ", "remember ", "save note "):
        if cmd.startswith(prefix):
            note = original[len(prefix) :].strip()
            if not note:
                return {"reply": "What should I note?", "actions": []}
            timestamp = now.strftime("%Y-%m-%d %H:%M")
            _append_line(NOTES_FILE, f"[{timestamp}] {note}")
            return {"reply": f"Noted: {note}", "actions": []}

    if any(phrase in cmd for phrase in ("read notes", "show notes", "my notes")):
        notes = _read_lines(NOTES_FILE)[-5:]
        return {"reply": "\n".join(notes) if notes else "No notes yet.", "actions": []}

    for prefix in ("add task ", "todo ", "add to todo "):
        if cmd.startswith(prefix):
            task = original[len(prefix) :].strip()
            if not task:
                return {"reply": "What task should I add?", "actions": []}
            _append_line(TODO_FILE, f"[ ] {task}")
            return {"reply": f"Added task: {task}", "actions": []}

    if any(phrase in cmd for phrase in ("show tasks", "read todo", "my tasks")):
        tasks = [line[4:] for line in _read_lines(TODO_FILE) if line.startswith("[ ]")]
        return {"reply": "\n".join(tasks[:5]) if tasks else "Todo list is empty.", "actions": []}

    for prefix in ("search youtube for ", "youtube search ", "play on youtube ", "youtube "):
        if cmd.startswith(prefix):
            query = original[len(prefix) :].strip()
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
            return {"reply": f"Opening YouTube results for {query}.", "actions": [{"type": "open", "url": url}]}

    for prefix in ("search for ", "search ", "google search ", "google for ", "look up ", "find "):
        if cmd.startswith(prefix):
            query = original[len(prefix) :].strip()
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            return {"reply": f"Opening Google results for {query}.", "actions": [{"type": "open", "url": url}]}

    return {
        "reply": f"I can handle web-safe commands only from deployment. You said: {original}",
        "actions": [],
    }


class JarvisHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            _json_response(self, {"ok": True, "service": "jarvis-web"})
            return
        if self.path == "/api/status":
            _json_response(self, _system_status())
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/api/command":
            payload = _read_json(self)
            _json_response(self, process_command(str(payload.get("command", ""))))
            return
        _json_response(self, {"error": "Not found"}, status=404)

    def log_message(self, format: str, *args) -> None:
        sys.stdout.write("[jarvis-web] " + format % args + "\n")


def main() -> None:
    if not WEB_DIR.exists():
        raise RuntimeError(f"Web assets not found: {WEB_DIR}")
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), JarvisHandler)
    print(f"Jarvis web server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
