#!/usr/bin/env python3
"""Generate the saved expert-board workflow. A shim over generate_workflows.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_workflows as workflows  # noqa: E402

AGENTS_DIR = workflows.AGENTS_DIR
MANIFEST = workflows.EXPERT_BOARD_MANIFEST
OUTPUT = workflows.WORKFLOW_DIR / "expert-board.js"
member_skills = workflows.member_skills


def resolved_manifest() -> dict:
    return workflows.resolved_manifest(MANIFEST)


def render() -> str:
    return workflows.render_js(MANIFEST, *workflows.load(MANIFEST))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when expert-board.js is stale")
    args = parser.parse_args()
    try:
        expected = render()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 2
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print(f"STALE: {OUTPUT.relative_to(AGENTS_DIR.parent)}")
            return 1
        print("expert-board workflow generation: PASS")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(AGENTS_DIR.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
