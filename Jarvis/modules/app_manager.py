# ============================================================
# JARVIS - Open / Close Apps & Websites
# ============================================================

import json
import os
import re
import time

import psutil
import pyautogui

import config

try:
    import pygetwindow as gw
    GW_AVAILABLE = True
except ImportError:
    GW_AVAILABLE = False


class AppManager:
    """Open tracking + close apps, browser tabs, and websites by name."""

    HISTORY_FILE = os.path.join(config.MEMORY_DIR, "opened_stack.json")
    MAX_HISTORY = 20

    # Website name -> words to find in browser window title
    WEBSITE_TITLES = {
        "youtube": ("youtube",),
        "google": ("google",),
        "gmail": ("gmail", "inbox"),
        "github": ("github",),
        "reddit": ("reddit",),
        "netflix": ("netflix",),
        "chatgpt": ("chatgpt", "chat.openai"),
        "instagram": ("instagram",),
        "facebook": ("facebook",),
        "twitter": ("twitter", "x.com"),
        "x": ("twitter", "/ x"),
        "linkedin": ("linkedin",),
        "stackoverflow": ("stackoverflow",),
        "wikipedia": ("wikipedia",),
        "amazon": ("amazon",),
        "whatsapp": ("whatsapp",),
    }

    # App/website name -> Windows process executable names
    PROCESS_NAMES = {
        "chrome": ("chrome.exe",),
        "google chrome": ("chrome.exe",),
        "edge": ("msedge.exe",),
        "microsoft edge": ("msedge.exe",),
        "firefox": ("firefox.exe",),
        "youtube": ("chrome.exe", "msedge.exe", "firefox.exe"),
        "spotify": ("spotify.exe",),
        "discord": ("discord.exe",),
        "vscode": ("code.exe",),
        "vs code": ("code.exe",),
        "visual studio code": ("code.exe",),
        "notepad": ("notepad.exe",),
        "calculator": ("calculatorapp.exe", "calc.exe"),
        "calc": ("calculatorapp.exe", "calc.exe"),
        "paint": ("mspaint.exe",),
        "word": ("winword.exe",),
        "excel": ("excel.exe",),
        "powerpoint": ("powerpnt.exe",),
        "outlook": ("outlook.exe",),
        "teams": ("ms-teams.exe", "msteams.exe"),
        "zoom": ("zoom.exe",),
        "telegram": ("telegram.exe",),
        "slack": ("slack.exe",),
        "vlc": ("vlc.exe",),
        "steam": ("steam.exe",),
        "cmd": ("cmd.exe",),
        "powershell": ("powershell.exe",),
        "task manager": ("taskmgr.exe",),
        "explorer": ("explorer.exe",),
        "file explorer": ("explorer.exe",),
    }

    @classmethod
    def _load_history(cls):
        try:
            if os.path.exists(cls.HISTORY_FILE):
                with open(cls.HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []

    @classmethod
    def _save_history(cls, stack):
        os.makedirs(config.MEMORY_DIR, exist_ok=True)
        with open(cls.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(stack[-cls.MAX_HISTORY :], f, indent=2)

    @classmethod
    def register_open(cls, name, kind="app", extra=None):
        """Remember what JARVIS opened (for close it / close that)."""
        name = name.lower().strip()
        entry = {"name": name, "kind": kind, "extra": extra or {}, "time": time.time()}
        stack = cls._load_history()
        stack.append(entry)
        cls._save_history(stack)

    @classmethod
    def _resolve_name(cls, target):
        """Match user speech to a known app or website key."""
        target = target.lower().strip()
        target = re.sub(r"^(the|a|an)\s+", "", target)

        for site in config.WEBSITES:
            if site in target or target in site:
                return site, "website"

        for site in cls.WEBSITE_TITLES:
            if site in target or target in site:
                return site, "website"

        for app in config.APPLICATIONS:
            if app in target or target in app:
                return app, "app"

        for key in cls.PROCESS_NAMES:
            if key in target or target in key:
                return key, "app"

        return target, "unknown"

    @classmethod
    def _close_windows_by_title(cls, keywords):
        """Close browser tabs/windows whose title contains keyword."""
        if not GW_AVAILABLE:
            return 0
        closed = 0
        try:
            for win in gw.getAllWindows():
                title = (win.title or "").lower()
                if not title or len(title) < 2:
                    continue
                if not any(k in title for k in keywords):
                    continue
                try:
                    if getattr(win, "isMinimized", False):
                        win.restore()
                    win.activate()
                    time.sleep(0.25)
                    pyautogui.hotkey("ctrl", "w")
                    closed += 1
                    time.sleep(0.2)
                except Exception:
                    try:
                        win.close()
                        closed += 1
                    except Exception:
                        pass
        except Exception:
            pass
        return closed

    @classmethod
    def _kill_processes(cls, exe_names):
        """Terminate processes by executable name."""
        killed = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info.get("name") or "").lower()
                if pname in exe_names:
                    proc.terminate()
                    killed.append(pname)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if killed:
            time.sleep(0.5)
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    pname = (proc.info.get("name") or "").lower()
                    if pname in exe_names and proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return killed

    @classmethod
    def close(cls, target):
        """Close app or website by name."""
        if not target:
            return False, "What should I close, sir?"

        name, kind = cls._resolve_name(target)
        closed_tabs = 0
        killed = []

        # 1) Websites: close matching browser tab/window first
        if kind == "website" or name in cls.WEBSITE_TITLES:
            keys = cls.WEBSITE_TITLES.get(name, (name,))
            closed_tabs = cls._close_windows_by_title(keys)

        # 2) Apps: close window by title (e.g. Spotify) then kill process
        if kind == "app" or name in cls.PROCESS_NAMES:
            title_keys = (name,)
            if name in ("vscode", "vs code", "visual studio code"):
                title_keys = ("visual studio code", "vscode", "- code")
            closed_tabs += cls._close_windows_by_title(title_keys)

            exe_set = set()
            if name in cls.PROCESS_NAMES:
                exe_set.update(n.lower() for n in cls.PROCESS_NAMES[name])
            for app_key, exe in config.APPLICATIONS.items():
                if app_key in name or name in app_key:
                    mapped = cls.PROCESS_NAMES.get(app_key, (f"{exe}.exe",))
                    exe_set.update(n.lower() for n in mapped)
            if exe_set:
                killed = cls._kill_processes(exe_set)

        # 3) Fallback: try title on raw target
        if closed_tabs == 0 and not killed:
            closed_tabs = cls._close_windows_by_title((name, target))

        cls._remove_from_history(name)

        if closed_tabs > 0:
            return True, f"Closed {name}, sir. Shut {closed_tabs} window(s)."
        if killed:
            return True, f"Closed {name}, sir. Stopped {len(killed)} process(es)."
        return False, f"I could not find {target} running, sir."

    @classmethod
    def close_last(cls):
        """Close the last thing JARVIS opened."""
        stack = cls._load_history()
        if not stack:
            return False, "Nothing to close, sir. I have no recent opens recorded."
        last = stack.pop()
        cls._save_history(stack)
        return cls.close(last["name"])

    @classmethod
    def _remove_from_history(cls, name):
        stack = cls._load_history()
        name = name.lower()
        stack = [e for e in stack if e.get("name") != name]
        cls._save_history(stack)

    @classmethod
    def close_all_browsers(cls):
        """Close all major browser processes."""
        exe = ("chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe")
        killed = cls._kill_processes(exe)
        if killed:
            return True, f"Closed all browsers, sir. Stopped {len(killed)} process(es)."
        return False, "No browsers were running, sir."
