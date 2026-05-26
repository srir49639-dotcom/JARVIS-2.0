# Run: python setup_guide.py
SETUP_TEXT = """
JARVIS Unified Assistant (GUI + Voice)

ONE FOLDER: Jarvis/
  assistant.py     Main entry (GUI + microphone)
  config.py          Settings & API keys
  install_jarvis.py  Install packages
  gui/dashboard.py   Dark dashboard
  modules/           All features

INSTALL:
  cd Jarvis
  python install_jarvis.py
  pip install PyAudio

RUN:
  python assistant.py          GUI + voice (recommended)
  python assistant.py --no-gui   Console + voice
  python launch_jarvis.py

VOICE:
  1. Say "hey jarvis"
  2. Say your command (or say both: "hey jarvis open chrome")
  3. For 30 seconds, more commands work without "jarvis"

EXAMPLES:
  hey jarvis what is the time
  hey jarvis open chrome
  hey jarvis search python
  hey jarvis battery
  hey jarvis help
  hey jarvis set timer 5 minutes

From parent folder:
  python assistant.py
  (uses launcher in jarvis the start/)
"""


def main():
    print(SETUP_TEXT)
    print(f"\nProject path: {os.path.dirname(os.path.abspath(__file__))}")


if __name__ == "__main__":
    import os
    main()
