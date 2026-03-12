#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _require_python_docx():
    try:
        from docx import Document  # type: ignore

        return Document
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: python-docx. Install with: pip install python-docx"
        ) from exc


def extract_docx(docx_path: Path) -> dict[str, Any]:
    Document = _require_python_docx()
    doc = Document(str(docx_path))

    paragraphs = [p.text for p in doc.paragraphs]
    tables: list[list[list[str]]] = []
    for table in doc.tables:
        tables.append([[cell.text for cell in row.cells] for row in table.rows])

    props = doc.core_properties
    core_properties = {
        "title": props.title,
        "subject": props.subject,
        "author": props.author,
        "category": props.category,
        "comments": props.comments,
        "created": props.created.isoformat() if props.created else None,
        "modified": props.modified.isoformat() if props.modified else None,
    }

    return {
        "path": str(docx_path),
        "core_properties": core_properties,
        "paragraphs": paragraphs,
        "tables": tables,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract text and tables from a .docx into JSON.")
    parser.add_argument("docx", type=Path, help="Path to a .docx file")
    parser.add_argument("--out", type=Path, help="Output JSON path (defaults to stdout)")
    args = parser.parse_args(argv)

    if not args.docx.exists():
        print(f"File not found: {args.docx}", file=sys.stderr)
        return 2

    try:
        payload = extract_docx(args.docx)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    output = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

