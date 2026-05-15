#!/usr/bin/env python3
"""Discover Git repositories under one or more roots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_EXCLUDES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "vendor",
    ".archive",
    "__pycache__",
}


def iter_repos(root: Path):
    seen = set()
    for git_dir in root.rglob(".git"):
        repo = git_dir.parent
        if any(part in DEFAULT_EXCLUDES for part in repo.parts):
            continue
        if repo in seen:
            continue
        seen.add(repo)
        yield repo


def classify_repo(repo: Path) -> str:
    if any((repo / name).exists() for name in ("pnpm-workspace.yaml", "nx.json", "turbo.json", "lerna.json")):
        return "monorepo-root"
    if (repo / "docs").is_dir() and not any((repo / name).exists() for name in ("package.json", "pyproject.toml", "go.mod", "Cargo.toml")):
        return "docs"
    return "repo"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="Root directories to scan")
    args = parser.parse_args()

    repos = []
    for root_str in args.roots:
        root = Path(root_str).expanduser().resolve()
        for repo in sorted(iter_repos(root)):
            repos.append(
                {
                    "repo_id": repo.name.lower().replace(" ", "-"),
                    "repo_name": repo.name,
                    "repo_path": str(repo),
                    "repo_group": root.name,
                    "shape": classify_repo(repo),
                }
            )

    print(json.dumps(repos, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
