#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


QUESTION_TEMPLATES = [
    "What does {title} cover?",
    "Summarize the key point of {title}.",
    "When should someone use {title}?",
]


def _load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return rows


def _normalize_title(row: dict) -> str:
    for key in ("title", "name", "heading", "id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "this document"


def _summary_text(row: dict) -> str:
    for key in ("summary", "abstract", "text", "content"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            normalized = re.sub(r"\s+", " ", value.strip())
            return normalized[:320]
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a heuristic JSONL testset scaffold from document JSONL.",
    )
    parser.add_argument("input_path", help="Input JSONL with document records.")
    parser.add_argument("output_path", help="Output JSONL path.")
    parser.add_argument(
        "--questions-per-doc",
        type=int,
        default=2,
        help="How many template questions to emit per document (default: 2).",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()
    output_path = Path(args.output_path).resolve()

    if not input_path.exists():
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        rows = _load_rows(input_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    questions_per_doc = max(1, min(args.questions_per_doc, len(QUESTION_TEMPLATES)))
    emitted = 0
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            doc_id = str(row.get("id") or row.get("document_id") or f"doc-{emitted + 1}")
            title = _normalize_title(row)
            summary = _summary_text(row)
            for template in QUESTION_TEMPLATES[:questions_per_doc]:
                result = {
                    "query_id": f"{doc_id}-q{emitted + 1}",
                    "query": template.format(title=title),
                    "expected_ids": [doc_id],
                    "notes": {
                        "generated_from": title,
                        "summary_hint": summary,
                    },
                }
                handle.write(json.dumps(result, ensure_ascii=True) + "\n")
                emitted += 1

    print(f"OK: wrote {emitted} synthetic rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
