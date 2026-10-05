#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


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
        if "word/document.xml" not in parts_present:
            # A renamed .pptx/.xlsx is a valid zip; without this check it reports 0 revisions.
            raise ValueError("Not a Word package: word/document.xml is missing")

        def parse_part(name: str, expected_root: str) -> ET.Element | None:
            xml = _read_zip_member(zip_file, name)
            if xml is None:
                return None
            try:
                root = ET.fromstring(xml)
            except ET.ParseError as exc:
                raise ValueError(f"Malformed {name}: {exc}") from exc
            if root.tag != f"{{{W_NS}}}{expected_root}":
                raise ValueError(f"Unexpected root element in {name}: {root.tag}")
            return root

        document = parse_part("word/document.xml", "document")
        comments = parse_part("word/comments.xml", "comments")
        # Revision tracking is a flag in settings.xml (<w:trackRevisions/>), not a part.
        settings = parse_part("word/settings.xml", "settings")

        def count_element(root: ET.Element | None, local_name: str) -> int:
            return 0 if root is None else sum(element.tag == f"{{{W_NS}}}{local_name}" for element in root.iter())

        def count(local_name: str) -> int:
            return count_element(document, local_name) + count_element(comments, local_name)

        counts = {
            "w:ins": count("ins"),
            "w:del": count("del"),
            "w:moveFrom": count("moveFrom"),
            "w:moveTo": count("moveTo"),
            "comments:present": 1 if comments is not None else 0,
            # One <w:comment> per comment in comments.xml; one <w:commentReference>
            # per anchored comment in the body. Range start/end markers are not counted.
            "comments:count": count_element(comments, "comment"),
            "comments:references": count_element(document, "commentReference"),
            "settings:trackRevisions": 1 if count_element(settings, "trackRevisions") else 0,
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
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
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
