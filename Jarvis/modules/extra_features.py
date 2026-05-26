# ============================================================
# JARVIS - Extra Features Module
# ============================================================

import os
import re
import socket
import subprocess
import time
from datetime import datetime

import psutil
import pyautogui
import pyperclip
import requests

import config


class ExtraFeatures:
    """Additional desktop assistant capabilities."""

    @staticmethod
    def get_time():
        now = datetime.now().strftime("%I:%M %p")
        return f"The time is {now}, sir."

    @staticmethod
    def get_date():
        today = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}, sir."

    @staticmethod
    def get_disk_usage():
        try:
            usage = psutil.disk_usage("C:\\")
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)
            percent = usage.percent
            return (
                f"Disk C drive is {percent} percent full. "
                f"{free_gb:.1f} gigabytes free of {total_gb:.1f} gigabytes, sir."
            )
        except Exception as e:
            return f"Disk info unavailable: {e}"

    @staticmethod
    def get_ip_address():
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return f"Hostname {hostname}, IP address {ip}, sir."
        except Exception as e:
            return f"Could not get IP: {e}"

    @staticmethod
    def get_system_info():
        try:
            import platform
            return (
                f"System: {platform.system()} {platform.release()}, "
                f"Machine: {platform.machine()}, "
                f"Processor: {platform.processor() or 'Unknown'}, sir."
            )
        except Exception as e:
            return f"System info unavailable: {e}"

    @staticmethod
    def close_active_window():
        try:
            pyautogui.hotkey("alt", "f4")
            return True, "Closing active window, sir."
        except Exception as e:
            return False, f"Could not close window: {e}"

    @staticmethod
    def minimize_window():
        try:
            pyautogui.hotkey("win", "down")
            return True, "Window minimized, sir."
        except Exception as e:
            return False, f"Minimize failed: {e}"

    @staticmethod
    def maximize_window():
        try:
            pyautogui.hotkey("win", "up")
            return True, "Window maximized, sir."
        except Exception as e:
            return False, f"Maximize failed: {e}"

    @staticmethod
    def switch_window():
        try:
            pyautogui.hotkey("alt", "tab")
            return True, "Switching window, sir."
        except Exception as e:
            return False, f"Switch failed: {e}"

    @staticmethod
    def empty_recycle_bin():
        try:
            subprocess.run(
                ["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                check=False,
            )
            return True, "Recycle bin emptied, sir."
        except Exception as e:
            return False, f"Could not empty recycle bin: {e}"

    @staticmethod
    def open_folder(folder_name):
        folders = {
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "music": os.path.join(os.path.expanduser("~"), "Music"),
            "videos": os.path.join(os.path.expanduser("~"), "Videos"),
            "home": os.path.expanduser("~"),
        }
        key = folder_name.lower().strip()
        for name, path in folders.items():
            if name in key:
                try:
                    os.startfile(path)
                    return True, f"Opening {name} folder, sir."
                except Exception as e:
                    return False, f"Could not open folder: {e}"
        return False, f"Folder '{folder_name}' not found, sir."

    @staticmethod
    def type_text(text):
        try:
            if not text:
                return False, "Nothing to type, sir."
            time.sleep(0.5)
            pyautogui.write(text, interval=0.03)
            return True, f"Typed: {text[:50]}, sir."
        except Exception as e:
            return False, f"Type failed: {e}"

    @staticmethod
    def copy_to_clipboard(text):
        try:
            pyperclip.copy(text)
            return True, "Copied to clipboard, sir."
        except Exception as e:
            return False, f"Copy failed: {e}"

    @staticmethod
    def get_news_headline():
        try:
            url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            r = requests.get(url, timeout=8)
            titles = re.findall(r"<title>(.*?)</title>", r.text)
            if len(titles) > 1:
                return f"Top headline: {titles[1]}, sir."
            return "Could not fetch news, sir."
        except Exception as e:
            return f"News unavailable: {e}"

    @staticmethod
    def send_whatsapp_message(number, message):
        try:
            import pywhatkit
            pywhatkit.sendwhatmsg_instantly(
                phone_no=number,
                message=message,
                wait_time=15,
                tab_close=True,
            )
            return True, "WhatsApp message sent, sir."
        except Exception as e:
            return False, f"WhatsApp failed: {e}"

    @staticmethod
    def help_commands():
        return (
            "Commands sir. Say hey jarvis then: open chrome youtube github; "
            "close youtube close chrome close spotify close it; "
            "search python; what time; weather in London; battery cpu ram disk; "
            "lock screen shutdown restart sleep; volume up down mute; "
            "play pause next song; screenshot; note remember this; add task; "
            "set alarm at 7 30 am; set timer 5 minutes; joke; wikipedia AI; "
            "chat mode; webcam; help. "
            "After wake word, 30 seconds of follow-up commands without saying jarvis."
        )

    # ---- Phase 3: Productivity Tools ----

    @staticmethod
    def get_clipboard_content():
        """Read text currently in the clipboard."""
        try:
            content = pyperclip.paste()
            if not content:
                return "The clipboard is empty, sir."
            # Limit the output length in case it's huge
            if len(content) > 500:
                return f"Clipboard contains long text starting with: {content[:100]}..."
            return f"Clipboard contains: {content}"
        except Exception as e:
            return f"Could not read clipboard: {e}"

    @staticmethod
    def organize_desktop():
        """Sort desktop files into categorical folders."""
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            folders = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
                "Installers": [".exe", ".msi"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Shortcuts": [".lnk", ".url"]
            }
            
            moved_count = 0
            for filename in os.listdir(desktop_path):
                file_path = os.path.join(desktop_path, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    
                    for folder_name, extensions in folders.items():
                        if ext in extensions:
                            dest_dir = os.path.join(desktop_path, folder_name)
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                            
                            dest_path = os.path.join(dest_dir, filename)
                            # Avoid overwriting existing files
                            if not os.path.exists(dest_path):
                                os.rename(file_path, dest_path)
                                moved_count += 1
                            break
                            
            if moved_count > 0:
                return True, f"Organized {moved_count} files on your desktop, sir."
            else:
                return True, "Your desktop is already organized, sir."
        except Exception as e:
            return False, f"Could not organize desktop: {e}"
