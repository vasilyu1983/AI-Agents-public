#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class InspectionResult:
    path: str
    parts_present: list[str]
    counts: dict[str, int]


def _read_zip_member(zip_file: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        with zip_file.open(name) as file:
            return file.read()
    except KeyError:
        return None


def inspect_docx(docx_path: Path) -> InspectionResult:
    with zipfile.ZipFile(docx_path) as zip_file:
        parts_present = sorted(zip_file.namelist())

        document_xml = _read_zip_member(zip_file, "word/document.xml") or b""
        comments_xml = _read_zip_member(zip_file, "word/comments.xml") or b""
        track_changes_xml = _read_zip_member(zip_file, "word/trackRevisions.xml") or b""

        def count(tag: bytes) -> int:
            return document_xml.count(tag) + comments_xml.count(tag) + track_changes_xml.count(tag)

        counts = {
            "w:ins": count(b"<w:ins"),
            "w:del": count(b"<w:del"),
            "w:moveFrom": count(b"<w:moveFrom"),
            "w:moveTo": count(b"<w:moveTo"),
            "comments:present": 1 if comments_xml else 0,
            "comments:references": document_xml.count(b"commentRangeStart")
            + document_xml.count(b"commentRangeEnd")
            + document_xml.count(b"commentReference"),
        }

        return InspectionResult(path=str(docx_path), parts_present=parts_present, counts=counts)


def _to_json(result: InspectionResult) -> dict[str, Any]:
    return {
        "path": result.path,
        "parts_present": result.parts_present,
        "counts": result.counts,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a .docx (OOXML zip) for common signals like tracked changes and comments."
    )
    parser.add_argument("docx", type=Path, help="Path to a .docx file")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    parser.add_argument("--list-parts", action="store_true", help="List all zip members (OOXML parts)")
    args = parser.parse_args(argv)

    if not args.docx.exists():
        print(f"File not found: {args.docx}", file=sys.stderr)
        return 2

    if args.docx.suffix.lower() != ".docx":
        print("Expected a .docx file. For .doc, convert to .docx first.", file=sys.stderr)
        return 2

    try:
        result = inspect_docx(args.docx)
    except zipfile.BadZipFile:
        print("Not a valid .docx (zip) file.", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(_to_json(result), indent=2, ensure_ascii=False))
        return 0

    print(f"File: {result.path}")
    for key in sorted(result.counts.keys()):
        print(f"{key}: {result.counts[key]}")

    if args.list_parts:
        print("\nOOXML parts:")
        for name in result.parts_present:
            print(f"- {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

