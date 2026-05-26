# ============================================================
# JARVIS - Notes & Todo persistence (Python json module)
# ============================================================

import json
import os

import config


class DataStore:
    """Store notes and todos using Python json — file auto-created at runtime."""

    @staticmethod
    def _store_path():
        return os.path.join(config.MEMORY_DIR, "jarvis_store.json")

    @classmethod
    def _load(cls):
        path = cls._store_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data.setdefault("notes", [])
                    data.setdefault("todos", [])
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"notes": [], "todos": []}

    @classmethod
    def _save(cls, data):
        os.makedirs(config.MEMORY_DIR, exist_ok=True)
        with open(cls._store_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def add_note(cls, content, timestamp):
        data = cls._load()
        data["notes"].append({"time": timestamp, "text": content})
        cls._save(data)

    @classmethod
    def get_notes(cls):
        return cls._load()["notes"]

    @classmethod
    def clear_notes(cls):
        data = cls._load()
        data["notes"] = []
        cls._save(data)

    @classmethod
    def add_todo(cls, task):
        data = cls._load()
        data["todos"].append({"done": False, "text": task})
        cls._save(data)

    @classmethod
    def get_todos(cls):
        return cls._load()["todos"]

    @classmethod
    def clear_todos(cls):
        data = cls._load()
        data["todos"] = []
        cls._save(data)

    @classmethod
    def complete_todo(cls, index):
        data = cls._load()
        todos = data["todos"]
        if 0 <= index < len(todos):
            todos[index]["done"] = True
            cls._save(data)
            return True
        return False
