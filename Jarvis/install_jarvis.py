# ============================================================
# JARVIS - Install dependencies (Python only)
# Run: python install_jarvis.py
# ============================================================

import subprocess
import sys

from dependencies import REQUIRED_PACKAGES


def main():
    print("Installing JARVIS dependencies...\n")
    for package in REQUIRED_PACKAGES:
        print(f"  -> {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("\nDone. Run: python assistant.py")


if __name__ == "__main__":
    main()
