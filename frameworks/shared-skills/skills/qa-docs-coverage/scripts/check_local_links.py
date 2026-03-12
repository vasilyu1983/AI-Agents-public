#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LINK_RE = re.compile(r"\]\(([^)]+)\)")


@dataclass(frozen=True)
class MissingLink:
    source_file: Path
    target: str


def _is_external_link(target: str) -> bool:
    target = target.strip()
    return (
        target.startswith("#")
        or target.startswith("mailto:")
        or target.startswith("http://")
        or target.startswith("https://")
    )


def _normalize_target(target: str) -> str:
    target = target.strip()
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    return target.strip()


def _iter_markdown_files(root: Path) -> list[Path]:
    markdown_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        if "/.archive/" in dirpath:
            continue
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {".git", "node_modules", ".venv", "dist", "build"}
        ]
        for filename in filenames:
            if filename.endswith(".md"):
                markdown_files.append(Path(dirpath) / filename)
    return markdown_files


def find_missing_local_links(root: Path) -> list[MissingLink]:
    missing: list[MissingLink] = []
    for markdown_file in _iter_markdown_files(root):
        try:
            text = markdown_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = markdown_file.read_text(encoding="utf-8", errors="replace")

        for raw_target in LINK_RE.findall(text):
            if _is_external_link(raw_target):
                continue
            target = _normalize_target(raw_target)
            if not target:
                continue
            full_target = (markdown_file.parent / target).resolve()
            if not full_target.exists():
                missing.append(MissingLink(source_file=markdown_file, target=raw_target))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown files for missing local link targets."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root path not found: {root}", file=sys.stderr)
        return 2

    missing = find_missing_local_links(root)
    if missing:
        print("Missing local link targets:")
        for item in missing:
            print(f"- {item.source_file}: {item.target}")
        return 1

    markdown_count = len(_iter_markdown_files(root))
    print(f"OK: {markdown_count} markdown files; no missing local link targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

