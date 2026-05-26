# ============================================================
# JARVIS - Notes & Todo Module (Python persistence)
# ============================================================

from datetime import datetime

from memory.persistence import DataStore


class NotesManager:
    """Manage notes and todos via Python DataStore."""

    @classmethod
    def save_note(cls, content):
        """Save a note with timestamp."""
        try:
            if not content:
                return False, "Note content is empty, sir."
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            DataStore.add_note(content, timestamp)
            return True, "Note saved successfully, sir."
        except Exception as e:
            return False, f"Could not save note: {e}"

    @classmethod
    def read_notes(cls):
        """Read all saved notes."""
        try:
            notes = DataStore.get_notes()
            if not notes:
                return "You have no saved notes, sir."
            lines = [f"[{n['time']}] {n['text']}" for n in notes]
            if len(lines) > 5:
                recent = "\n".join(lines[-5:])
                return f"Your recent notes, sir:\n{recent}"
            return f"Your notes, sir:\n" + "\n".join(lines)
        except Exception as e:
            return f"Could not read notes: {e}"

    @classmethod
    def clear_notes(cls):
        """Clear all notes."""
        try:
            DataStore.clear_notes()
            return True, "All notes cleared, sir."
        except Exception as e:
            return False, f"Could not clear notes: {e}"

    @classmethod
    def add_task(cls, task):
        """Add a todo task."""
        try:
            if not task:
                return False, "Task description is empty, sir."
            DataStore.add_todo(task)
            return True, f"Task added: {task}, sir."
        except Exception as e:
            return False, f"Could not add task: {e}"

    @classmethod
    def show_tasks(cls):
        """Show all todo tasks."""
        try:
            todos = DataStore.get_todos()
            if not todos:
                return "Your task list is empty, sir."
            lines = []
            for i, t in enumerate(todos, 1):
                mark = "x" if t.get("done") else " "
                lines.append(f"{i}. [{mark}] {t['text']}")
            return "Your tasks, sir:\n" + "\n".join(lines)
        except Exception as e:
            return f"Could not read tasks: {e}"

    @classmethod
    def clear_tasks(cls):
        """Clear all todo tasks."""
        try:
            DataStore.clear_tasks()
            return True, "All tasks cleared, sir."
        except Exception as e:
            return False, f"Could not clear tasks: {e}"

    @classmethod
    def complete_task(cls, task_number):
        """Mark a task as complete by line number."""
        try:
            idx = int(task_number) - 1
            if DataStore.complete_todo(idx):
                return True, f"Task {task_number} marked complete, sir."
            return False, "Invalid task number, sir."
        except Exception as e:
            return False, f"Could not complete task: {e}"
