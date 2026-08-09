#!/usr/bin/env python3
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

        broken_targets = []
        external_target_count = 0

        for rel_path in [name for name in names if name.endswith(".rels")]:
            rel_xml = _read_zip_member(zip_file, rel_path)
            if not rel_xml:
                continue

            root = ET.fromstring(rel_xml)
            base_dir = _relationship_base_dir(rel_path)

            for rel in root.findall(f"{OOXML_REL_NS}Relationship"):
                target = rel.attrib.get("Target")
                if not target:
                    continue

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

        counts = {
            "slides": len([name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml")]),
            "notes_slides": len(
                [name for name in names if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")]
            ),
            "charts": len([name for name in names if name.startswith("ppt/charts/")]),
            "media": len([name for name in names if name.startswith("ppt/media/")]),
            "embeddings": len([name for name in names if name.startswith("ppt/embeddings/")]),
            "comments": len([name for name in names if name.startswith("ppt/comments/")]),
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

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
