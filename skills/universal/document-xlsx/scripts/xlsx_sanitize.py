#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
PKGREL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
ET.register_namespace("", MAIN_NS)
ET.register_namespace("", CONTENT_NS)
ET.register_namespace("", PKGREL_NS)

DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


def _read_xml(zip_file: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        with zip_file.open(name) as file:
            return ET.parse(file).getroot()
    except KeyError:
        return None


def _sanitize_text(text: str) -> str:
    if text.startswith(DANGEROUS_PREFIXES):
        return "'" + text
    return text


# LIMITATION: this script quotes dangerous-looking cell text by writing a
# literal leading apostrophe into the XML <t> content. That apostrophe
# becomes visibly part of the string in Excel/LibreOffice/Sheets (readers do
# not treat it as a hidden "text prefix" marker the way Excel's own quotePrefix
# UI feature does) -- it is a poor, cosmetically-lossy fix, not a security
# control. XLSX string cells also do not execute on their own; the real
# CSV-injection risk exists when a spreadsheet tool later exports this data to
# CSV and a different application (e.g. a shell, or a spreadsheet opening the
# CSV) interprets a leading =/+/-/@ as a formula or command. If CSV export is
# in the pipeline, sanitize at that export step instead of (or in addition to)
# here. A cleaner in-workbook fix would set the cell's `quotePrefix` style
# (stored in styles.xml, not the string content), which openpyxl and Excel
# both render without leaking a visible character -- this script does not
# implement that today because it requires rewriting styles.xml and the cell's
# style index, not just sharedStrings.xml/inline strings.


def _sanitize_shared_strings(data: bytes) -> tuple[bytes, int]:
    root = ET.fromstring(data)
    changed = 0
    for si in root.findall(f"{{{MAIN_NS}}}si"):
        text_nodes = list(si.iterfind(f".//{{{MAIN_NS}}}t"))
        if not text_nodes:
            continue
        current = "".join(node.text or "" for node in text_nodes)
        updated = _sanitize_text(current)
        if updated == current:
            continue
        first_node = text_nodes[0]
        first_node.text = "'" + (first_node.text or "")
        changed += 1
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changed


def _sanitize_inline_strings(data: bytes) -> tuple[bytes, int]:
    root = ET.fromstring(data)
    changed = 0
    for inline_str in root.iterfind(f".//{{{MAIN_NS}}}is"):
        text_nodes = list(inline_str.iterfind(f".//{{{MAIN_NS}}}t"))
        if not text_nodes:
            continue
        current = "".join(node.text or "" for node in text_nodes)
        updated = _sanitize_text(current)
        if updated == current:
            continue
        text_nodes[0].text = "'" + (text_nodes[0].text or "")
        changed += 1
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changed


def _strip_external_links_from_workbook(data: bytes) -> bytes:
    root = ET.fromstring(data)
    for node in list(root):
        if node.tag == f"{{{MAIN_NS}}}externalReferences":
            root.remove(node)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _strip_external_link_relationships(data: bytes) -> bytes:
    root = ET.fromstring(data)
    for rel in list(root):
        rel_type = rel.attrib.get("Type", "")
        if rel_type.endswith("/externalLink"):
            root.remove(rel)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _strip_external_link_content_types(data: bytes) -> bytes:
    root = ET.fromstring(data)
    for override in list(root):
        part_name = override.attrib.get("PartName", "")
        if part_name.startswith("/xl/externalLinks/"):
            root.remove(override)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def sanitize_workbook(input_path: Path, output_path: Path, strip_external_links: bool) -> tuple[int, int]:
    if input_path.resolve() == output_path.resolve() or (
        output_path.exists() and input_path.samefile(output_path)
    ):
        raise ValueError("Output path must differ from input path, including aliases.")
    dangerous_changes = 0
    stripped_parts = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_path) as source:
        workbook = _read_xml(source, "xl/workbook.xml")
        if workbook is None or workbook.tag != f"{{{MAIN_NS}}}workbook":
            raise ValueError("No SpreadsheetML xl/workbook.xml; nothing was sanitized.")
        fd, tmp_name = tempfile.mkstemp(suffix=".xlsx", dir=output_path.parent)
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as dest:
                for info in source.infolist():
                    data = source.read(info.filename)
                    filename = info.filename

                    if strip_external_links and filename.startswith("xl/externalLinks/"):
                        stripped_parts += 1
                        continue

                    if filename == "xl/sharedStrings.xml":
                        data, changes = _sanitize_shared_strings(data)
                        dangerous_changes += changes
                    elif filename.startswith("xl/worksheets/") and filename.endswith(".xml"):
                        data, changes = _sanitize_inline_strings(data)
                        dangerous_changes += changes
                    elif strip_external_links and filename == "xl/workbook.xml":
                        data = _strip_external_links_from_workbook(data)
                    elif strip_external_links and filename == "xl/_rels/workbook.xml.rels":
                        data = _strip_external_link_relationships(data)
                    elif strip_external_links and filename == "[Content_Types].xml":
                        data = _strip_external_link_content_types(data)

                    dest.writestr(info, data)
            os.replace(tmp_path, output_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    return dangerous_changes, stripped_parts


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Copy and sanitize a .xlsx/.xlsm workbook by quoting dangerous text prefixes and optionally stripping external links."
    )
    parser.add_argument("input_path", type=Path, help="Input .xlsx or .xlsm workbook")
    parser.add_argument("output_path", type=Path, help="Output workbook path")
    parser.add_argument(
        "--strip-external-links",
        action="store_true",
        help="Remove workbook externalLinks parts and workbook references.",
    )
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"File not found: {args.input_path}", file=sys.stderr)
        return 2
    if args.input_path.suffix.lower() not in {".xlsx", ".xlsm"}:
        print("Expected a .xlsx or .xlsm file.", file=sys.stderr)
        return 2
    if args.output_path == args.input_path:
        print("Output path must differ from input path.", file=sys.stderr)
        return 2

    try:
        dangerous_changes, stripped_parts = sanitize_workbook(
            args.input_path, args.output_path, args.strip_external_links
        )
    except (ET.ParseError, zipfile.BadZipFile, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(
        f"Sanitized workbook written to {args.output_path} "
        f"(dangerous text entries quoted: {dangerous_changes}, external link parts removed: {stripped_parts})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
