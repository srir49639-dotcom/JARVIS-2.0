# ============================================================
# JARVIS - System Controls Module
# ============================================================

import ctypes
import os
import subprocess
import time

import psutil
import pyautogui
import requests
import speedtest
from colorama import Fore, Style

import config
from modules.app_manager import AppManager


class SystemControls:
    """Windows system control operations."""

    # ---- Power Management ----

    @staticmethod
    def lock_screen():
        """Lock Windows screen using Win+L."""
        try:
            pyautogui.hotkey("win", "l")
            return True, "Screen locked, sir."
        except Exception as e:
            return False, f"Could not lock screen: {e}"

    @staticmethod
    def shutdown_system():
        """Shutdown Windows after 1 second delay."""
        try:
            subprocess.run(["shutdown", "/s", "/t", "1"], check=False)
            return True, "Shutting down the system. Goodbye, sir."
        except Exception as e:
            return False, f"Shutdown failed: {e}"

    @staticmethod
    def restart_system():
        """Restart Windows after 1 second delay."""
        try:
            subprocess.run(["shutdown", "/r", "/t", "1"], check=False)
            return True, "Restarting the system, sir."
        except Exception as e:
            return False, f"Restart failed: {e}"

    @staticmethod
    def cancel_shutdown():
        """Cancel pending shutdown."""
        try:
            subprocess.run(["shutdown", "/a"], check=False)
            return True, "Shutdown cancelled, sir."
        except Exception as e:
            return False, f"Could not cancel shutdown: {e}"

    @staticmethod
    def sleep_system():
        """Put system to sleep."""
        try:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return True, "Entering sleep mode, sir."
        except Exception as e:
            return False, f"Sleep failed: {e}"

    @staticmethod
    def hibernate_system():
        """Hibernate Windows."""
        try:
            subprocess.run(["shutdown", "/h"], check=False)
            return True, "Hibernating the system, sir."
        except Exception as e:
            return False, f"Hibernate failed: {e}"

    # ---- Application Control ----

    APP_MAP = config.APPLICATIONS

    CHROME_PATHS = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]

    @classmethod
    def _launch_executable(cls, cmd):
        """Launch app reliably on Windows."""
        if cmd == "chrome":
            for path in cls.CHROME_PATHS:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    return True
            subprocess.Popen("cmd /c start chrome", shell=True)
            return True
        if cmd in ("spotify", "discord", "firefox", "msedge", "code", "zoom", "slack", "telegram"):
            subprocess.Popen(f"cmd /c start {cmd}", shell=True)
            return True
        subprocess.Popen(cmd, shell=True)
        return True

    @classmethod
    def open_application(cls, app_name):
        """Open a Windows application."""
        app_name = app_name.lower().strip()
        for key, cmd in cls.APP_MAP.items():
            if key in app_name:
                try:
                    cls._launch_executable(cmd)
                    AppManager.register_open(key, kind="app", extra={"exe": cmd})
                    return True, f"Opening {key}, sir."
                except Exception as e:
                    return False, f"Could not open {key}: {e}"
        return False, f"Application '{app_name}' not found. Say help for list, sir."

    # ---- System Status ----

    @staticmethod
    def get_battery():
        """Return battery percentage and charging status."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "No battery detected. Desktop system, sir."
            status = "charging" if battery.power_plugged else "on battery"
            return f"Battery is at {battery.percent} percent, {status}, sir."
        except Exception as e:
            return f"Battery info unavailable: {e}"

    @staticmethod
    def get_battery_percent():
        """Return battery percent or None."""
        try:
            battery = psutil.sensors_battery()
            return battery.percent if battery else None
        except Exception:
            return None

    @staticmethod
    def get_cpu_usage():
        """Return CPU usage percentage."""
        try:
            usage = psutil.cpu_percent(interval=1)
            return f"CPU usage is at {usage} percent, sir."
        except Exception as e:
            return f"CPU info unavailable: {e}"

    @staticmethod
    def get_ram_usage():
        """Return RAM usage information."""
        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            return (
                f"RAM usage is {mem.percent} percent. "
                f"{used_gb:.1f} gigabytes used of {total_gb:.1f} gigabytes, sir."
            )
        except Exception as e:
            return f"RAM info unavailable: {e}"

    @staticmethod
    def get_uptime():
        """Return system uptime."""
        try:
            boot = psutil.boot_time()
            uptime_seconds = time.time() - boot
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"System uptime is {hours} hours and {minutes} minutes, sir."
        except Exception as e:
            return f"Uptime info unavailable: {e}"

    @staticmethod
    def check_internet():
        """Check internet connectivity."""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                return "Internet connection is active, sir."
            return "Internet connection may be unstable, sir."
        except Exception:
            return "No internet connection detected, sir."

    @staticmethod
    def run_speed_test():
        """Run internet speed test."""
        try:
            print(f"{Fore.CYAN}[JARVIS] Running speed test, please wait...{Style.RESET_ALL}")
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            return (
                f"Speed test complete. Download: {download:.2f} Mbps. "
                f"Upload: {upload:.2f} Mbps, sir."
            )
        except Exception as e:
            return f"Speed test failed: {e}"

    @staticmethod
    def get_system_stats():
        """Return dict of system stats for GUI."""
        try:
            battery = psutil.sensors_battery()
            mem = psutil.virtual_memory()
            return {
                "cpu": psutil.cpu_percent(interval=0.5),
                "ram": mem.percent,
                "battery": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
            }
        except Exception:
            return {"cpu": 0, "ram": 0, "battery": None, "battery_plugged": None}

    # ---- Phase 3: Advanced PC Controls & Diagnostics ----

    @staticmethod
    def kill_process(process_name):
        """Kill a frozen or misbehaving application."""
        process_name = process_name.lower().strip()
        killed = False
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name in proc.info['name'].lower():
                    proc.kill()
                    killed = True
            if killed:
                return True, f"Terminated processes matching {process_name}, sir."
            else:
                return False, f"Could not find any running process named {process_name}, sir."
        except Exception as e:
            return False, f"Error terminating process: {e}"

    @staticmethod
    def set_volume(level):
        """Set system volume (0-100). Requires third-party lib or simulated keystrokes."""
        try:
            # We use simulated keystrokes for pure python cross compatibility without pycaw
            # A more robust solution involves pycaw for Windows
            level = max(0, min(100, int(level)))
            # Approximate volume setting by pressing vol down 50 times (to 0), then vol up (level/2) times
            for _ in range(50):
                pyautogui.press("volumedown")
            for _ in range(level // 2):
                pyautogui.press("volumeup")
            return True, f"Volume set to {level} percent, sir."
        except Exception as e:
            return False, f"Could not set volume: {e}"

    @staticmethod
    def set_brightness(level):
        """Set screen brightness (0-100)."""
        try:
            import screen_brightness_control as sbc
            level = max(0, min(100, int(level)))
            sbc.set_brightness(level)
            return True, f"Brightness set to {level} percent, sir."
        except ImportError:
            return False, "Screen brightness control library is not installed, sir. Run pip install screen-brightness-control."
        except Exception as e:
            return False, f"Could not set brightness: {e}"

    @staticmethod
    def get_thermal_stats():
        """Get CPU temperature (Note: Windows often restricts this)."""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return "Thermal sensors are restricted by Windows or unsupported by the hardware, sir."
            
            # Find coretemp or similar
            for name, entries in temps.items():
                if name.startswith('coretemp'):
                    avg_temp = sum(entry.current for entry in entries) / len(entries)
                    return f"CPU temperature is averaging {avg_temp:.1f} degrees Celsius, sir."
            return "Could not read CPU temperature sensors, sir."
        except Exception as e:
            return f"Thermal diagnostics unavailable: {e}"
