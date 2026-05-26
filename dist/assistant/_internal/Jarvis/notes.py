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
        f.write(line + "\n")

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
