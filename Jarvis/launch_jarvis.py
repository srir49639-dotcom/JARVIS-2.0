# ============================================================
# JARVIS - Launcher (Python only)
# Run: python launch_jarvis.py
# ============================================================

import os
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.getcwd())
    from assistant import main
    main()
