#!/usr/bin/env python3
"""Install the closed-loop Layer-1 capture hook for THIS machine.

Idempotent. Re-runnable. Works on any laptop / any username because every
path is resolved from Path.home() at install time — nothing is hardcoded.

What it does:
  1. Copies assets/learnings_capture.py -> $HOME/.agents/hooks/ (runtime-neutral)
  2. Registers it in Claude Code:  $HOME/.claude/settings.json  hooks.SessionEnd
  3. Registers it in Codex (if present): $HOME/.codex/hooks.json  hooks.Stop
  4. Validates both JSON files; never clobbers unrelated keys/hooks.

Usage:
  python3 install_capture_hook.py [--dry-run] [--uninstall]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HOME = Path.home()
HERE = Path(__file__).resolve().parent
ASSET = HERE.parent / "assets" / "learnings_capture.py"
DEST = HOME / ".agents" / "hooks" / "learnings_capture.py"
TAG = "learnings_capture.py"  # identity marker for idempotent re-registration

CLAUDE_SETTINGS = HOME / ".claude" / "settings.json"
CODEX_HOOKS = HOME / ".codex" / "hooks.json"
CLAUDE_EVENT = "SessionEnd"   # fires once per session
CODEX_EVENT = "Stop"          # Codex's session/turn stop (no SessionEnd event)


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _hook_entry() -> dict:
    # Absolute, machine-resolved path. Portable because the installer
    # regenerates it from Path.home() on every laptop.
    return {
        "matcher": "*",
        "hooks": [{
            "type": "command",
            "command": f"python3 {DEST}",
            "timeout": 200,
        }],
    }


def _strip_ours(groups: list) -> list:
    """Drop any prior registration of our script (idempotent re-install)."""
    out = []
    for g in groups or []:
        hs = [h for h in g.get("hooks", [])
              if TAG not in str(h.get("command", ""))]
        if hs:
            g = {**g, "hooks": hs}
            out.append(g)
        elif not g.get("hooks"):
            # group existed only for us and is now empty -> drop it
            if any(TAG in str(h.get("command", ""))
                   for h in (g.get("hooks") or [])):
                continue
            out.append(g)
    return out


def register(path: Path, event: str, dry: bool, remove: bool) -> str:
    cfg = _load(path)
    cfg.setdefault("hooks", {})
    groups = cfg["hooks"].get(event, [])
    groups = _strip_ours(groups)
    if not remove:
        groups.append(_hook_entry())
    if groups:
        cfg["hooks"][event] = groups
    else:
        cfg["hooks"].pop(event, None)
        if not cfg["hooks"]:
            cfg.pop("hooks", None)
    if dry:
        return f"DRY  would write {path} ({event})"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n")
    json.loads(path.read_text())  # fail loud if we produced invalid JSON
    return f"OK   {path} ({event}) {'removed' if remove else 'registered'}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()
    remove, dry = args.uninstall, args.dry_run

    if not ASSET.is_file():
        print(f"ERROR: asset not found: {ASSET}", file=sys.stderr)
        return 1

    # 1. script
    if remove:
        if not dry and DEST.exists():
            DEST.unlink()
        print(f"{'DRY  would remove' if dry else 'OK   removed'} {DEST}")
    else:
        if not dry:
            DEST.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ASSET, DEST)
            DEST.chmod(0o755)
        print(f"{'DRY  would copy' if dry else 'OK   copied'} -> {DEST}")

    # 2. Claude Code (always — settings.json is created if absent)
    print(register(CLAUDE_SETTINGS, CLAUDE_EVENT, dry, remove))

    # 3. Codex (only if Codex is present; don't create speculative dirs)
    codex_present = (HOME / ".codex").is_dir() or shutil.which("codex")
    if codex_present:
        print(register(CODEX_HOOKS, CODEX_EVENT, dry, remove))
    else:
        print("SKIP Codex not detected (no ~/.codex, no `codex` on PATH). "
              "Re-run this installer after installing Codex.")

    print("\nDone. Verify with:  cat ~/.agents/hooks/learnings_capture.log "
          "(after a session that used a wired skill).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
