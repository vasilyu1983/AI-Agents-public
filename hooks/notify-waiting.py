#!/usr/bin/env python3
"""Notification (Claude, matcher permission_prompt|idle_prompt): desktop alert when Claude waits.

The message is fixed on purpose. The notification text can carry file paths or command
content, and a lock screen shows it, so this hook never reads or forwards it.
Template: skills/universal/agents-hooks/references/hook-templates.md, "Claude: Desktop
Notification When Claude Waits". Notification cannot block, so every path exits 0.
"""
import shutil
import subprocess
import sys

TITLE = "Claude Code"
MESSAGE = "Claude is waiting for you"


def main() -> int:
    if sys.platform == "darwin":
        cmd = ["osascript", "-e", f'display notification "{MESSAGE}" with title "{TITLE}"']
    elif shutil.which("notify-send"):
        cmd = ["notify-send", TITLE, MESSAGE]
    else:
        return 0
    try:
        subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"notify-waiting: {type(exc).__name__}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
