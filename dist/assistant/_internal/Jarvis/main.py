"""Jarvis main loop."""
import os
import sys
import time
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from speech_engine import speak, listen_for_wake_word, listen_for_command, extract_command_from_wake
from commands import dispatch

def run():
    print(Fore.CYAN + "JARVIS AI Assistant" + Style.RESET_ALL)
    print(f'Wake word: "{config.WAKE_WORD}"\n')
    speak("Jarvis online. Say hey jarvis to wake me.")
    errors = 0
    while True:
        try:
            heard = listen_for_wake_word()
            if not heard:
                continue
            cmd = extract_command_from_wake(heard)
            if not cmd:
                cmd = listen_for_command()
            if cmd:
                dispatch(cmd)
                errors = 0
            else:
                errors += 1
            time.sleep(0.3)
        except KeyboardInterrupt:
            speak("Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
            errors += 1
            if errors > 5:
                errors = 0
                time.sleep(2)

if __name__ == "__main__":
    run()
