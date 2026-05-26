# ============================================================
# JARVIS - Utilities Module
# ============================================================

import datetime
import os
import random
import re
import threading
import time
import pyautogui
import pyperclip
import qrcode
from colorama import Fore, Style
from PIL import Image
from plyer import notification

import config

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


# ---- Quotes & Jokes ----

MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "Stay hungry, stay foolish. - Steve Jobs",
    "Genius is one percent inspiration and ninety-nine percent perspiration. - Thomas Edison",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Churchill",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why did the developer go broke? Because he used up all his cache.",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "Why do Java developers wear glasses? Because they don't C sharp.",
    "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "I would tell you a UDP joke, but you might not get it.",
    "Why did Python break up with Java? Because Python found C++ more attractive.",
    "Knock knock. Who's there? Recursion. Recursion who? Knock knock.",
]


class Utilities:
    """Screenshots, alarms, timers, notifications, QR codes, clipboard, effects."""

    _alarms = []
    _timers = []
    _alarm_lock = threading.Lock()

    # ---- Screenshot ----

    @staticmethod
    def take_screenshot():
        """Take screenshot and save to Desktop."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_screenshot_{timestamp}.png"
            filepath = os.path.join(config.SCREENSHOT_DIR, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            return True, f"Screenshot saved to Desktop as {filename}, sir."
        except Exception as e:
            return False, f"Screenshot failed: {e}"

    # ---- Clipboard ----

    @staticmethod
    def read_clipboard():
        """Read clipboard contents."""
        try:
            content = pyperclip.paste()
            if content:
                preview = content[:200] + ("..." if len(content) > 200 else "")
                return f"Clipboard contains: {preview}, sir."
            return "Clipboard is empty, sir."
        except Exception as e:
            return f"Clipboard read failed: {e}"

    # ---- QR Code ----

    @staticmethod
    def generate_qr_code(data):
        """Generate QR code image on Desktop."""
        try:
            if not data:
                return False, "Please provide data for the QR code, sir."
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_qr_{timestamp}.png"
            filepath = os.path.join(config.SCREENSHOT_DIR, filename)
            img = qrcode.make(data)
            img.save(filepath)
            return True, f"QR code saved to Desktop as {filename}, sir."
        except Exception as e:
            return False, f"QR code generation failed: {e}"

    # ---- Quotes & Jokes ----

    @staticmethod
    def get_quote():
        return random.choice(MOTIVATIONAL_QUOTES) + ", sir."

    @staticmethod
    def get_joke():
        return random.choice(JOKES)

    # ---- Desktop Notifications ----

    @staticmethod
    def send_notification(title, message, timeout=10):
        """Send desktop notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=config.ASSISTANT_NAME,
                timeout=timeout,
            )
            return True
        except Exception as e:
            print(f"{Fore.RED}[Notification Error] {e}{Style.RESET_ALL}")
            return False

    # ---- Alarm ----

    @classmethod
    def set_alarm(cls, time_str, callback_speak):
        """
        Set voice alarm. time_str format: HH:MM or H:MM AM/PM
        """
        try:
            alarm_time = cls._parse_time(time_str)
            if alarm_time is None:
                return False, "Could not parse alarm time. Use format like 7:30 AM, sir."

            def alarm_thread():
                while True:
                    now = datetime.datetime.now()
                    if now.hour == alarm_time.hour and now.minute == alarm_time.minute:
                        callback_speak(f"Alarm! It is {time_str}, sir.")
                        cls.send_notification("JARVIS Alarm", f"Alarm for {time_str}")
                        break
                    time.sleep(20)

            thread = threading.Thread(target=alarm_thread, daemon=True)
            thread.start()
            with cls._alarm_lock:
                cls._alarms.append(time_str)
            return True, f"Alarm set for {time_str}, sir."
        except Exception as e:
            return False, f"Alarm failed: {e}"

    @staticmethod
    def _parse_time(time_str):
        """Parse time string to datetime.time."""
        time_str = time_str.strip().upper()
        formats = ["%I:%M %p", "%I:%M%p", "%H:%M", "%I %p", "%H:%M:%S"]
        for fmt in formats:
            try:
                parsed = datetime.datetime.strptime(time_str, fmt)
                return parsed.time()
            except ValueError:
                continue
        match = re.search(r"(\d{1,2}):?(\d{2})?\s*(am|pm)?", time_str, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            ampm = (match.group(3) or "").upper()
            if ampm == "PM" and hour < 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0
            return datetime.time(hour=hour, minute=minute)
        return None

    # ---- Timer ----

    @classmethod
    def set_timer(cls, minutes, callback_speak):
        """Set countdown timer in minutes."""
        try:
            minutes = int(minutes)
            if minutes <= 0:
                return False, "Timer must be at least 1 minute, sir."

            def timer_thread():
                time.sleep(minutes * 60)
                callback_speak(f"Timer complete. {minutes} minutes have passed, sir.")
                cls.send_notification("JARVIS Timer", f"{minutes} minute timer finished")

            thread = threading.Thread(target=timer_thread, daemon=True)
            thread.start()
            return True, f"Timer set for {minutes} minutes, sir."
        except ValueError:
            return False, "Please specify timer duration in minutes, sir."
        except Exception as e:
            return False, f"Timer failed: {e}"

    # ---- Visual Effects ----

    @staticmethod
    def typing_effect(text, delay=0.02):
        """Print text with typing animation in terminal."""
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()

    @staticmethod
    def animated_loading(message="Loading", duration=2, steps=20):
        """Display animated loading spinner."""
        chars = "|/-\\"
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Fore.CYAN}{message} {chars[i % len(chars)]}{Style.RESET_ALL}", end="", flush=True)
            time.sleep(duration / steps)
            i += 1
        print(f"\r{Fore.GREEN}{message} complete!{Style.RESET_ALL}      ")

    # ---- Startup Sound ----

    @staticmethod
    def play_startup_sound():
        """Play startup sound (generated in Python via assets.sounds or winsound)."""
        try:
            from assets.sounds import play_startup_sound
            play_startup_sound()
        except Exception:
            try:
                import winsound
                # Futuristic multi-tone boot sequence
                winsound.Beep(523, 150) # C5
                winsound.Beep(659, 150) # E5
                winsound.Beep(784, 150) # G5
                winsound.Beep(1046, 300) # C6
            except Exception:
                pass

    # ---- Battery Warning ----

    @staticmethod
    def check_battery_warning(get_battery_func, threshold=None):
        """Check if battery is low and return warning message."""
        threshold = threshold or config.BATTERY_LOW_THRESHOLD
        try:
            percent = get_battery_func()
            if percent is not None and percent <= threshold:
                return f"Warning: Battery is critically low at {percent} percent, sir."
        except Exception:
            pass
        return None

    # ---- Banner ----

    @staticmethod
    def load_banner():
        """Load ASCII banner from Python assets module."""
        try:
            import sys
            from assets.banner import BANNER, BANNER_ASCII
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            try:
                BANNER.encode(encoding or "utf-8")
                return BANNER
            except (UnicodeEncodeError, LookupError):
                return BANNER_ASCII
        except Exception:
            return "JARVIS - Just A Rather Very Intelligent System\n"
