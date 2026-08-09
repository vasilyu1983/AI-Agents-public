#!/usr/bin/env python3
"""Validate generated repo profiles for required fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = {
    "repo_id",
    "repo_name",
    "repo_path",
    "status",
    "languages",
    "repo_kind",
    "architecture_style",
    "summary",
    "evidence",
    "confidence_score",
    "last_scanned_at",
}


def validate(profile_path: Path) -> list[str]:
    data = json.loads(profile_path.read_text())
    missing = sorted(REQUIRED_FIELDS - data.keys())
    problems = []
    if missing:
        problems.append(f"missing fields: {', '.join(missing)}")
    if not isinstance(data.get("evidence", []), list):
        problems.append("evidence must be a list")
    if not isinstance(data.get("confidence_score", 0), (int, float)):
        problems.append("confidence_score must be numeric")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles_dir", help="Directory containing JSON profiles")
    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    failures = 0
    for path in sorted(profiles_dir.glob("*.json")):
        problems = validate(path)
        if problems:
            failures += 1
            print(f"{path.name}: {'; '.join(problems)}")

    if failures == 0:
        print("All profiles passed basic validation.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
