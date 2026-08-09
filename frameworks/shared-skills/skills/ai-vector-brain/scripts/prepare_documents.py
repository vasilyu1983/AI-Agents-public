#!/usr/bin/env python3
"""Normalize inventory JSONL into document JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def read_jsonl(path: Path | None):
    stream = path.open() if path else sys.stdin
    with stream:
        for line in stream:
            line = line.strip()
            if line:
                yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", nargs="?", type=Path)
    parser.add_argument("--corpus-type", required=True)
    parser.add_argument("--default-language", default="en")
    args = parser.parse_args()

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


if __name__ == "__main__":
    main()

