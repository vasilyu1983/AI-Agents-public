#!/usr/bin/env python3
"""Report profiles that are older than the repo files they summarize."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def latest_mtime(repo: Path) -> float:
    latest = 0.0
    for path in repo.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        latest = max(latest, path.stat().st_mtime)
    return latest


def collect_stale_profiles(profiles_dir: Path) -> list[dict]:
    stale = []

    for profile_path in sorted(profiles_dir.glob("*.json")):
        data = json.loads(profile_path.read_text())
        repo = Path(data["repo_path"])
        scanned_at = datetime.fromisoformat(data["last_scanned_at"].replace("Z", "+00:00")).timestamp()
        repo_mtime = latest_mtime(repo)
        if repo.exists() and repo_mtime > scanned_at:
            stale.append(
                {
                    "repo": data["repo_name"],
                    "last_scanned_at": data["last_scanned_at"],
                    "latest_source_change_ts": repo_mtime,
                }
            )

    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles_dir")
    parser.add_argument("--output", help="Optional path to write the JSON drift report")
    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    stale = collect_stale_profiles(profiles_dir)
    rendered = json.dumps(stale, indent=2)
    print(rendered)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
