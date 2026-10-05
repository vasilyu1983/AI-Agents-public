#!/usr/bin/env python3
"""Normalize inventory JSONL into document JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from check_brain_manifest import CORPUS_TYPES

REQUIRED_KEYS = ("source_id", "source_uri", "content_hash")


def _fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def read_jsonl(path: Path | None):
    stream = path.open() if path else sys.stdin
    with stream:
        for lineno, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                _fail(f"invalid JSON on line {lineno}: {exc}")
            if not isinstance(item, dict):
                _fail(f"line {lineno} is not a JSON object")
            missing = [key for key in REQUIRED_KEYS if not item.get(key)]
            if missing:
                _fail(f"line {lineno} is missing {', '.join(missing)}")
            yield item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", nargs="?", type=Path)
    parser.add_argument("--corpus-type", required=True, choices=sorted(CORPUS_TYPES))
    parser.add_argument("--default-language", default="en")
    args = parser.parse_args()

    written = 0
    for item in read_jsonl(args.inventory):
        source_path = item.get("source_path") or ""
        title = Path(source_path).stem.replace("-", " ").replace("_", " ").strip() or source_path
        doc = {
            "source_id": item["source_id"],
            "source_uri": item["source_uri"],
            "source_path": source_path,
            "title": title,
            "doc_type": item.get("doc_type", "text"),
            "corpus_type": args.corpus_type,
            "language": item.get("language", args.default_language),
            "content_hash": item["content_hash"],
            "metadata": {"size_bytes": item.get("size_bytes"), **(item.get("metadata") or {})},
        }
        print(json.dumps(doc, ensure_ascii=False))
        written += 1

    if written == 0:
        _fail("no inventory rows read; nothing to prepare")


if __name__ == "__main__":
    main()

