# ============================================================
# VS Code: set this file as entry and press F5 to run JARVIS
# (Python-only — no launch.json needed)
# ============================================================

import os
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.getcwd())
    from assistant import main
    main()
