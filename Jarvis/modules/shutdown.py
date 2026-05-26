# ============================================================
# JARVIS - Shutdown command detection
# ============================================================

import config


def is_shutdown_command(command):
    """True if user wants to stop JARVIS (not close another app)."""
    if not command:
        return False
    cmd = command.lower().strip()
    for wake in config.WAKE_WORDS:
        cmd = cmd.replace(wake, "")
    cmd = cmd.strip()

    if cmd in ("exit chat", "stop chat", "disable chat", "exit chat mode"):
        return False

    if cmd in config.EXIT_COMMANDS:
        return True

    for prefix in (
        "stop jarvis", "exit jarvis", "quit jarvis", "shutdown jarvis",
        "turn off jarvis", "deactivate jarvis", "close jarvis",
    ):
        if cmd.startswith(prefix):
            return True

    if cmd in ("stop", "exit", "quit", "bye", "goodbye"):
        return True

    return False
