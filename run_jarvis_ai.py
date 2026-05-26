# Unified JARVIS launcher (redirects to Jarvis/)
import os
import runpy
import sys

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Jarvis")
os.chdir(_ROOT)
sys.path.insert(0, _ROOT)
runpy.run_path(os.path.join(_ROOT, "assistant.py"), run_name="__main__")
