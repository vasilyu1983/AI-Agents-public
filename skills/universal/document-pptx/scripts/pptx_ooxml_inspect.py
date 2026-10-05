#!/usr/bin/env python3
"""Inspect a .pptx package for broken internal targets and structure counts.

Exit codes: 0 no broken internal targets; 1 broken internal relationship
targets found (the deck is likely to trigger PowerPoint's repair dialog);
2 the file is missing, is not a PowerPoint package, or has malformed
relationship markup. --report-only exits 0 for a readable, well-formed
package with broken internal targets (inventory use).
"""
from __future__ import annotations

import argparse
import json
import posixpath
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET


OOXML_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
RELATIONSHIPS_TAG = f"{OOXML_REL_NS}Relationships"
RELATIONSHIP_TAG = f"{OOXML_REL_NS}Relationship"


def _read_zip_member(zip_file: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        with zip_file.open(name) as file:
            return file.read()
    except KeyError:
        return None


def _relationship_base_dir(rel_path: str) -> str:
    pure_path = PurePosixPath(rel_path)
    if pure_path.parent.name == "_rels":
        return pure_path.parent.parent.as_posix()
    return pure_path.parent.as_posix()


def _resolve_target(base_dir: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    if not base_dir or base_dir == ".":
        return posixpath.normpath(target)
    return posixpath.normpath(posixpath.join(base_dir, target))


def inspect_pptx(pptx_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(pptx_path) as zip_file:
        names = sorted(zip_file.namelist())
        name_set = set(names)
        if "ppt/presentation.xml" not in name_set:
            raise ValueError("Not a PowerPoint package: ppt/presentation.xml is missing")

        broken_targets = []
        external_target_count = 0

        for rel_path in [name for name in names if name.endswith(".rels")]:
            rel_xml = _read_zip_member(zip_file, rel_path)
            if not rel_xml:
                raise ValueError(f"Empty relationship part: {rel_path}")

            root = ET.fromstring(rel_xml)
            if root.tag != RELATIONSHIPS_TAG:
                raise ValueError(f"Invalid relationship root: {rel_path}")
            base_dir = _relationship_base_dir(rel_path)

            for rel in root:
                if rel.tag != RELATIONSHIP_TAG:
                    raise ValueError(f"Invalid relationship entry: {rel_path}")
                target = rel.attrib.get("Target")
                if not target or not target.strip():
                    raise ValueError(f"Missing relationship target: {rel_path}")

                if rel.attrib.get("TargetMode") == "External":
                    external_target_count += 1
                    continue

                resolved = _resolve_target(base_dir, target)
                if resolved not in name_set:
                    broken_targets.append(
                        {
                            "relationship_part": rel_path,
                            "relationship_id": rel.attrib.get("Id"),
                            "relationship_type": rel.attrib.get("Type"),
                            "target": target,
                            "resolved_target": resolved,
                        }
                    )

        slide_xml = b"".join(
            _read_zip_member(zip_file, name) or b""
            for name in names
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
        presentation_xml = _read_zip_member(zip_file, "ppt/presentation.xml") or b""

        # Count real parts only: skip zip directory entries (some writers emit them)
        # and _rels/ files, and count chart parts by name so chart style/color
        # parts (ppt/charts/style1.xml, colors1.xml) are not counted as charts.
        def _parts(prefix: str) -> list[str]:
            return [
                name for name in names
                if name.startswith(prefix) and not name.endswith("/") and "/_rels/" not in name
            ]

        counts = {
            "slides": len([name for name in _parts("ppt/slides/slide") if name.endswith(".xml")]),
            "notes_slides": len([name for name in _parts("ppt/notesSlides/notesSlide") if name.endswith(".xml")]),
            "charts": len([name for name in _parts("ppt/charts/chart") if name.endswith(".xml")]),
            "media": len(_parts("ppt/media/")),
            "embeddings": len(_parts("ppt/embeddings/")),
            "comments": len(_parts("ppt/comments/")),
            "transitions": slide_xml.count(b"<p:transition"),
            "timing_nodes": slide_xml.count(b"<p:timing"),
            "sections": presentation_xml.count(b"<p14:section") + presentation_xml.count(b"<p:sectionLst"),
            "external_relationships": external_target_count,
            "broken_internal_targets": len(broken_targets),
        }

        return {
            "path": str(pptx_path),
            "counts": counts,
            "parts_present": names,
            "broken_internal_targets": broken_targets,
        }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a .pptx (OOXML zip) for broken internal targets, transitions, timing, notes, charts, and media."
    )
    parser.add_argument("pptx", type=Path, help="Path to a .pptx file")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    parser.add_argument("--list-parts", action="store_true", help="List OOXML parts in plain-text mode")
    parser.add_argument(
        "--list-broken-targets",
        action="store_true",
        help="List broken internal relationship targets in plain-text mode",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Exit 0 for a well-formed package even when internal targets are broken; malformed relationships still exit 2.",
    )
    args = parser.parse_args(argv)

    if not args.pptx.exists():
        print(f"File not found: {args.pptx}", file=sys.stderr)
        return 2

    if args.pptx.suffix.lower() != ".pptx":
        print("Expected a .pptx file.", file=sys.stderr)
        return 2

    try:
        payload = inspect_pptx(args.pptx)
    except zipfile.BadZipFile:
        print("Not a valid .pptx (zip) file.", file=sys.stderr)
        return 2
    except ET.ParseError as exc:
        print(f"Failed to parse OOXML relationships: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    status = 1 if payload["broken_internal_targets"] and not args.report_only else 0

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return status

    print(f"File: {payload['path']}")
    for key, value in sorted(payload["counts"].items()):
        print(f"{key}: {value}")

    if args.list_parts:
        print("\nOOXML parts:")
        for part in payload["parts_present"]:
            print(f"- {part}")

    if args.list_broken_targets and payload["broken_internal_targets"]:
        print("\nBroken internal targets:")
        for item in payload["broken_internal_targets"]:
            print(
                f"- {item['relationship_part']} :: {item['relationship_id']} -> "
                f"{item['resolved_target']}"
            )
    elif args.list_broken_targets:
        print("\nBroken internal targets: none")

    if status:
        print(
            f"FAIL: {len(payload['broken_internal_targets'])} broken internal target(s); "
            "rerun with --list-broken-targets for details.",
            file=sys.stderr,
        )
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
