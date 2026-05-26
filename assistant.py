# Run JARVIS from the parent folder (fixes "file not found" error)
import os
import runpy
import sys

_JARVIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Jarvis")

if not os.path.isdir(_JARVIS_DIR):
    print("Error: Jarvis folder not found next to this file.")
    print(f"Expected: {_JARVIS_DIR}")
    sys.exit(1)

os.chdir(_JARVIS_DIR)
sys.path.insert(0, _JARVIS_DIR)
runpy.run_path(os.path.join(_JARVIS_DIR, "assistant.py"), run_name="__main__")
