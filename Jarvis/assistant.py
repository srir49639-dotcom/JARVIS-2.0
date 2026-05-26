# ============================================================
# JARVIS - Main Assistant Entry Point (100% Python project)
# Unified GUI + Voice | install: python install_jarvis.py | help: python setup_guide.py
# ============================================================

import os
import sys
import threading
import time

from colorama import Fore, Back, Style, init as colorama_init

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from modules.speech import SpeechEngine
from modules.system_controls import SystemControls
from modules.browser import BrowserModule
from modules.media import MediaControls
from modules.utilities import Utilities
from modules.ai_chat import AIChat
from modules.notes import NotesManager
from modules.camera import CameraModule
from modules.command_router import CommandRouter
from modules.shutdown import is_shutdown_command

colorama_init(autoreset=True)


class JarvisAssistant:
    """Main JARVIS assistant controller."""

    def __init__(self, dashboard=None):
        self.speech = SpeechEngine()
        self.dashboard = dashboard
        self.router = CommandRouter(self)
        self._running = False
        self._listen_thread = None
        self._pending_confirmation = None
        self._command_history = []
        self._active_listen_until = 0.0
        self._exit_requested = False
        self._shutting_down = False

    # ---- Lifecycle ----

    @staticmethod
    def is_shutdown_command(command):
        return is_shutdown_command(command)

    def start(self):
        """Start the listening loop."""
        if self._running:
            return
        self._running = True
        self._listen_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._listen_thread.start()
        self._activate_listen_window()
        self._respond(
            "JARVIS online, sir. Say hey jarvis, then your command. "
            "You may give more commands for 30 seconds without the wake word."
        )

    def stop_listening(self):
        """Pause voice loop only (GUI stays open)."""
        self._running = False
        self._active_listen_until = 0
        AIChat.disable_chat_mode()
        if self.dashboard:
            self.dashboard.set_status("PAUSED", "#888888")
            self.dashboard.set_listen_mode(False)

    def shutdown(self, speak_goodbye=True):
        """Fully stop JARVIS and close the app."""
        if self._shutting_down:
            return
        self._shutting_down = True
        self._exit_requested = True
        self._running = False
        self._active_listen_until = 0
        AIChat.disable_chat_mode()

        goodbye = "Goodbye sir. JARVIS shutting down."
        print(f"{Fore.CYAN}JARVIS: {goodbye}{Style.RESET_ALL}")
        if self.dashboard:
            self.dashboard.on_assistant_response(goodbye)
            self.dashboard.set_status("OFFLINE", "#ff4444")
            self.dashboard.set_listen_mode(False)
            try:
                self.dashboard.after(300, self._quit_gui)
            except Exception:
                pass

        if speak_goodbye:
            try:
                self.speech.speak(goodbye)
            except Exception:
                pass

    def _quit_gui(self):
        """Close dashboard window from Tk main thread."""
        if not self.dashboard:
            return
        try:
            self.dashboard.quit()
        except Exception:
            pass
        try:
            self.dashboard.destroy()
        except Exception:
            pass

    def stop(self):
        """Alias: pause listening (used by GUI stop button)."""
        self.stop_listening()

    def _activate_listen_window(self):
        """Open window for follow-up commands without wake word."""
        self._active_listen_until = time.time() + config.ACTIVE_LISTEN_SECONDS
        if self.dashboard:
            self.dashboard.set_listen_mode(True)

    def _is_active_listen(self):
        return time.time() < self._active_listen_until

    def _main_loop(self):
        """Wake word loop + 30s follow-up (merged Jarvis_AI voice + GUI)."""
        while self._running:
            try:
                if self.speech.is_speaking():
                    time.sleep(0.2)
                    continue

                if self.dashboard:
                    self.dashboard.set_status("WAITING", "#888888")

                heard = self.speech.listen_for_wake(stop_check=lambda: not self._running)
                if not heard or not self._running:
                    continue

                self._activate_listen_window()
                if self.dashboard:
                    self.dashboard.set_status("ACTIVE", "#00ff88")

                command = SpeechEngine.extract_command_from_wake(heard)
                if not command:
                    command = self.speech.listen_for_command(speak_prompt=True)

                if command:
                    self.process_command(command)
                    if self._exit_requested:
                        break

                while self._running and self._is_active_listen() and not self._exit_requested:
                    if self.speech.is_speaking():
                        time.sleep(0.2)
                        continue
                    text = self.speech.listen(show_prompt=True)
                    if not text:
                        continue
                    if self._pending_confirmation:
                        self._handle_confirmation(text)
                        continue
                    if AIChat.is_chat_mode():
                        if any(w in text for w in ("exit chat", "stop chat", "disable chat")):
                            self._respond(AIChat.disable_chat_mode())
                        else:
                            self._respond(AIChat.ask(text))
                        continue
                    if SpeechEngine.contains_wake_word(text):
                        text = SpeechEngine.extract_command_from_wake(text) or text
                    self.process_command(text)
                    if self._exit_requested:
                        break

                if self._exit_requested:
                    break

                if self.dashboard:
                    self.dashboard.set_status("IDLE", "#888888")
                    self.dashboard.set_listen_mode(False)

            except Exception as e:
                print(f"{Fore.RED}[Loop Error] {e}{Style.RESET_ALL}")
                time.sleep(0.5)

    # ---- Response Helpers ----

    def _respond(self, message):
        """Speak and log response."""
        if not message:
            return
        print(f"{Fore.CYAN}JARVIS: {message}{Style.RESET_ALL}")
        if self.dashboard:
            self.dashboard.on_assistant_response(message)
        self.speech.speak(message)

    def _log_command(self, command):
        """Log user command."""
        print(f"{Fore.GREEN}Command: {command}{Style.RESET_ALL}")
        self._command_history.append(command)
        if self.dashboard:
            self.dashboard.add_history(f"You: {command}")

    # ---- Confirmation Handler ----

    def _handle_confirmation(self, text):
        """Handle yes/no confirmation."""
        text = text.lower().strip()
        action = self._pending_confirmation
        self._pending_confirmation = None

        if any(w in text for w in config.CONFIRM_WORDS):
            if action == "shutdown":
                ok, msg = SystemControls.shutdown_system()
                self._respond(msg)
            elif action == "restart":
                ok, msg = SystemControls.restart_system()
                self._respond(msg)
        elif any(w in text for w in config.CANCEL_WORDS):
            self._respond("Action cancelled, sir.")
        else:
            self._pending_confirmation = action
            self._respond("Please say yes or no, sir.")

    def _ask_confirmation(self, action, question):
        """Set pending confirmation state."""
        self._pending_confirmation = action
        self._respond(question)

    # ---- Command Processor ----

    def process_command(self, command):
        """Process a voice or text command."""
        if not command:
            return

        try:
            cmd = command.lower().strip()
            self._log_command(cmd)

            if self.is_shutdown_command(cmd):
                self.shutdown()
                return

            self._activate_listen_window()

            if self.router.process(cmd):
                return

            self._respond(
                "I did not understand that, sir. Say help for commands, "
                "or try: Jarvis open chrome, Jarvis what time, Jarvis search python."
            )

        except Exception as e:
            print(f"{Fore.RED}[Command Error] {e}{Style.RESET_ALL}")
            self._respond("An error occurred, sir, but I remain operational.")


# ============================================================
# Startup & Main
# ============================================================

def setup_console_encoding():
    """Fix Windows console Unicode errors (cp1252)."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def print_banner():
    """Display JARVIS ASCII banner."""
    os.system("")  # Enable ANSI on Windows
    banner = Utilities.load_banner()
    text = f"{Fore.CYAN}{Style.BRIGHT}{banner}{Style.RESET_ALL}"
    try:
        print(text)
    except UnicodeEncodeError:
        from assets.banner import BANNER_ASCII
        print(f"{Fore.CYAN}{Style.BRIGHT}{BANNER_ASCII}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'=' * 55}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  JARVIS Desktop Assistant - Windows Edition{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'=' * 55}{Style.RESET_ALL}\n")


def run_console_mode(assistant):
    """Run assistant in console-only mode."""
    assistant.start()
    print(f"{Fore.GREEN}Say 'Hey Jarvis' followed by your command.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Type commands below or press Ctrl+C to exit.{Style.RESET_ALL}\n")
    try:
        while True:
            try:
                cmd = input(f"{Fore.MAGENTA}You> {Style.RESET_ALL}").strip()
                if JarvisAssistant.is_shutdown_command(cmd):
                    assistant.shutdown()
                    break
                if cmd:
                    assistant.process_command(cmd)
            except EOFError:
                break
    except KeyboardInterrupt:
        assistant.shutdown(speak_goodbye=False)
        print(f"\n{Fore.YELLOW}JARVIS shutting down. Goodbye, sir.{Style.RESET_ALL}")


def run_gui_mode(assistant):
    """Run assistant with GUI dashboard."""
    from gui.dashboard import JarvisDashboard

    assistant.dashboard = JarvisDashboard(assistant_ref=assistant)
    assistant.dashboard.set_mic_status(assistant.speech.mic_available)

    def battery_monitor():
        while True:
            try:
                warning = Utilities.check_battery_warning(SystemControls.get_battery_percent)
                if warning:
                    Utilities.send_notification("JARVIS Battery Alert", warning)
                    if assistant.dashboard:
                        assistant.dashboard.add_history(f"⚠ {warning}")
            except Exception:
                pass
            time.sleep(300)

    threading.Thread(target=battery_monitor, daemon=True).start()
    assistant.dashboard.mainloop()


def main():
    """Main entry point."""
    setup_console_encoding()
    print_banner()
    Utilities.animated_loading("Initializing JARVIS", duration=2)
    Utilities.play_startup_sound()

    assistant = JarvisAssistant()

    use_gui = "--no-gui" not in sys.argv
    if use_gui:
        try:
            run_gui_mode(assistant)
        except Exception as e:
            print(f"{Fore.RED}[GUI Error] {e}. Falling back to console mode.{Style.RESET_ALL}")
            run_console_mode(assistant)
    else:
        run_console_mode(assistant)


if __name__ == "__main__":
    main()
