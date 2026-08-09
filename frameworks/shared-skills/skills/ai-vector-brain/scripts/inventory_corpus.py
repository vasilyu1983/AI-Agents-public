#!/usr/bin/env python3
"""Inventory a corpus into JSONL records."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_SUFFIXES = {".md", ".mdx", ".txt", ".json", ".yaml", ".yml", ".py", ".ts", ".tsx", ".js", ".jsx", ".sql"}
SKIP_PARTS = {".git", "node_modules", ".venv", "dist", "build", ".archive"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
      for chunk in iter(lambda: f.read(1024 * 1024), b""):
          h.update(chunk)
    return h.hexdigest()


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".mdx"}:
        return "markdown"
    if suffix in {".json", ".yaml", ".yml"}:
        return "structured"
    if suffix == ".sql":
        return "sql"
    if suffix in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return "code"
    return "text"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--source-id", default=None)
    parser.add_argument("--suffix", action="append", dest="suffixes")
    args = parser.parse_args()

    root = args.root.resolve()
    suffixes = set(args.suffixes or DEFAULT_SUFFIXES)
    source_id = args.source_id or root.name

    for path in sorted(root.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() not in suffixes:
            continue
        rel = path.relative_to(root).as_posix()
        record = {
            "source_id": source_id,
            "source_uri": f"file://{path}",
            "source_path": rel,
            "doc_type": classify(path),
            "content_hash": hash_file(path),
            "size_bytes": path.stat().st_size,
        }
        print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()

