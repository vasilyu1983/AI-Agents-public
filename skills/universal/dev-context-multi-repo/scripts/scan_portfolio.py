#!/usr/bin/env python3
"""Scan a portfolio of repos and emit normalized profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from subprocess import check_output


def discover(roots: list[str]) -> list[dict]:
    cmd = ["python3", str(Path(__file__).with_name("discover_repos.py")), *roots]
    return json.loads(check_output(cmd, text=True))


def scan_repo(repo_path: str) -> dict:
    cmd = ["python3", str(Path(__file__).with_name("scan_repo.py")), repo_path]
    return json.loads(check_output(cmd, text=True))


def resolve_profiles_out(out: str | None, artifact_root: str | None) -> Path:
    if out:
        return Path(out)
    if artifact_root:
        return Path(artifact_root) / "profiles"
    return Path("profiles")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="Root directories containing repos")
    parser.add_argument(
        "--artifact-root",
        help="Artifact root for standard outputs. When set, profiles are written to <artifact-root>/profiles unless --out is provided.",
    )
    parser.add_argument("--out", help="Output directory for JSON profiles")
    args = parser.parse_args()

    out_dir = resolve_profiles_out(args.out, args.artifact_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    for repo in discover(args.roots):
        profile = scan_repo(repo["repo_path"])
        (out_dir / f"{profile['repo_id']}.json").write_text(json.dumps(profile, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
