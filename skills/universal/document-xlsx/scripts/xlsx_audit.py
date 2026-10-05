#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "table": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}

DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")

# Heuristic regex checks over raw formula text. These are best-effort signals,
# not a full formula parser -- false positives/negatives are expected on
# unusual formula shapes.
HARDCODED_CONSTANT_RE = re.compile(r"[+\-*/^]\s*-?\d+(\.\d+)?(?!\s*[A-Za-z(])")
HYPERLINK_FN_RE = re.compile(r"\bHYPERLINK\s*\(", re.IGNORECASE)
# The selected functions below have prefixed spellings in XlsxWriter's future-
# function reference; function age alone does not establish that requirement.
# The negative lookbehind skips prefixed occurrences, so a formula mixing a
# prefixed and an unprefixed call is still flagged.
NON_PORTABLE_FN_RE = re.compile(
    r"(?<![.\w])(XLOOKUP|XMATCH|FILTER|UNIQUE|SORT|SORTBY|SEQUENCE|IFS|LET|LAMBDA|TEXTJOIN|TEXTSPLIT)\s*\(",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SheetAudit:
    name: str
    path: str | None
    state: str
    formula_count: int
    table_names: list[str]
    inline_dangerous_strings: int
    hardcoded_constant_count: int = 0
    hardcoded_constant_samples: list[str] | None = None
    hyperlink_formula_count: int = 0
    missing_cached_value_count: int = 0
    non_portable_unprefixed_count: int = 0
    non_portable_unprefixed_samples: list[str] | None = None
    error_value_count: int = 0
    error_value_samples: list[str] | None = None


def _read_xml(zip_file: zipfile.ZipFile, name: str) -> ET.Element | None:
    try:
        with zip_file.open(name) as file:
            return ET.parse(file).getroot()
    except KeyError:
        return None


def _read_text(zip_file: zipfile.ZipFile, name: str) -> bytes:
    try:
        with zip_file.open(name) as file:
            return file.read()
    except KeyError:
        return b""


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _package_target(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    base = Path(base_part).parent
    return posixpath.normpath((base / target).as_posix())


def _load_shared_strings(zip_file: zipfile.ZipFile) -> tuple[int, list[str]]:
    root = _read_xml(zip_file, "xl/sharedStrings.xml")
    if root is None:
        return 0, []

    count = 0
    samples: list[str] = []
    for si in root.findall("main:si", NS):
        text = "".join(node.text or "" for node in si.iterfind(".//main:t", NS))
        if text.startswith(DANGEROUS_PREFIXES):
            count += 1
            if len(samples) < 5:
                samples.append(text[:120])
    return count, samples


def _load_table_map(zip_file: zipfile.ZipFile) -> dict[str, str]:
    table_map: dict[str, str] = {}
    for name in zip_file.namelist():
        if not name.startswith("xl/tables/") or not name.endswith(".xml"):
            continue
        root = _read_xml(zip_file, name)
        if root is None:
            continue
        display_name = root.attrib.get("displayName") or root.attrib.get("name")
        if display_name:
            table_map[name] = display_name
    return table_map


def _load_sheet_targets(zip_file: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    workbook_root = _read_xml(zip_file, "xl/workbook.xml")
    rels_root = _read_xml(zip_file, "xl/_rels/workbook.xml.rels")
    if workbook_root is None or rels_root is None:
        return []

    rels = {
        rel.attrib.get("Id"): rel.attrib.get("Target")
        for rel in rels_root.findall("pkgrel:Relationship", NS)
        if rel.attrib.get("Id") and rel.attrib.get("Target")
    }

    sheets: list[tuple[str, str, str]] = []
    for sheet in workbook_root.findall("main:sheets/main:sheet", NS):
        rid = sheet.attrib.get(f"{{{NS['rel']}}}id")
        if not rid or rid not in rels:
            continue
        target = _package_target("xl/workbook.xml", rels[rid])
        sheets.append(
            (
                sheet.attrib.get("name", "Unnamed"),
                target,
                sheet.attrib.get("state", "visible"),
            )
        )
    return sheets


def _sheet_table_names(zip_file: zipfile.ZipFile, sheet_path: str, table_map: dict[str, str]) -> list[str]:
    rels_path = f"{Path(sheet_path).parent.as_posix()}/_rels/{Path(sheet_path).name}.rels"
    rels_root = _read_xml(zip_file, rels_path)
    if rels_root is None:
        return []

    tables: list[str] = []
    for rel in rels_root.findall("pkgrel:Relationship", NS):
        rel_type = rel.attrib.get("Type", "")
        if not rel_type.endswith("/table"):
            continue
        target = rel.attrib.get("Target")
        if not target:
            continue
        table_path = _package_target(sheet_path, target)
        display_name = table_map.get(table_path)
        if display_name:
            tables.append(display_name)
    return tables


def _sheet_formula_count(zip_file: zipfile.ZipFile, sheet_path: str) -> dict[str, Any]:
    root = _read_xml(zip_file, sheet_path)
    if root is None:
        return {
            "formulas": 0,
            "dangerous_inline": 0,
            "hardcoded_constant_count": 0,
            "hardcoded_constant_samples": [],
            "hyperlink_formula_count": 0,
            "missing_cached_value_count": 0,
            "non_portable_unprefixed_count": 0,
            "non_portable_unprefixed_samples": [],
            "error_value_count": 0,
            "error_value_samples": [],
        }

    dangerous_inline = 0
    for inline_str in root.iterfind(".//main:is", NS):
        text = "".join(node.text or "" for node in inline_str.iterfind(".//main:t", NS))
        if text.startswith(DANGEROUS_PREFIXES):
            dangerous_inline += 1

    formulas = 0
    hardcoded_constant_count = 0
    hardcoded_constant_samples: list[str] = []
    hyperlink_formula_count = 0
    missing_cached_value_count = 0
    non_portable_unprefixed_count = 0
    non_portable_unprefixed_samples: list[str] = []
    error_value_count = 0
    error_value_samples: list[str] = []

    for cell in root.iterfind(".//main:c", NS):
        # t="e" marks a cached error value (#REF!, #DIV/0!, #NAME?, ...).
        if cell.get("t") == "e":
            error_value_count += 1
            if len(error_value_samples) < 5:
                cached = cell.find("main:v", NS)
                error_value_samples.append(f"{cell.get('r')}: {cached.text if cached is not None else '?'}")
        f_node = cell.find("main:f", NS)
        if f_node is None:
            continue
        formulas += 1
        formula_text = f_node.text or ""

        if HARDCODED_CONSTANT_RE.search(formula_text):
            hardcoded_constant_count += 1
            if len(hardcoded_constant_samples) < 5:
                hardcoded_constant_samples.append(formula_text[:120])

        if HYPERLINK_FN_RE.search(formula_text):
            hyperlink_formula_count += 1

        # A formula cell with no cached value (missing <v>, or an empty <v/>
        # as openpyxl writes for a never-recalculated formula) means the file
        # was never recalculated by a calculation engine, or a recalculation
        # error dropped the cache. Heuristic: some shared-formula follower
        # cells legitimately omit <v> too, so treat this as a signal, not proof.
        v_node = cell.find("main:v", NS)
        if v_node is None or not (v_node.text or "").strip():
            missing_cached_value_count += 1

        if NON_PORTABLE_FN_RE.search(formula_text):
            non_portable_unprefixed_count += 1
            if len(non_portable_unprefixed_samples) < 5:
                non_portable_unprefixed_samples.append(formula_text[:120])

    return {
        "formulas": formulas,
        "dangerous_inline": dangerous_inline,
        "hardcoded_constant_count": hardcoded_constant_count,
        "hardcoded_constant_samples": hardcoded_constant_samples,
        "hyperlink_formula_count": hyperlink_formula_count,
        "missing_cached_value_count": missing_cached_value_count,
        "non_portable_unprefixed_count": non_portable_unprefixed_count,
        "non_portable_unprefixed_samples": non_portable_unprefixed_samples,
        "error_value_count": error_value_count,
        "error_value_samples": error_value_samples,
    }


def _defined_names(zip_file: zipfile.ZipFile) -> list[str]:
    workbook_root = _read_xml(zip_file, "xl/workbook.xml")
    if workbook_root is None:
        return []
    names: list[str] = []
    for node in workbook_root.findall("main:definedNames/main:definedName", NS):
        name = node.attrib.get("name")
        if name:
            names.append(name)
    return names


def _core_properties(zip_file: zipfile.ZipFile) -> dict[str, str | None]:
    root = _read_xml(zip_file, "docProps/core.xml")
    if root is None:
        return {}
    return {
        "title": root.findtext("dc:title", default=None, namespaces=NS),
        "subject": root.findtext("dc:subject", default=None, namespaces=NS),
        "creator": root.findtext("dc:creator", default=None, namespaces=NS),
        "description": root.findtext("dc:description", default=None, namespaces=NS),
        "created": root.findtext("dcterms:created", default=None, namespaces=NS),
        "modified": root.findtext("dcterms:modified", default=None, namespaces=NS),
    }


def audit_workbook(path: Path) -> dict[str, Any]:
    if path.suffix.lower() not in {".xlsx", ".xlsm"}:
        raise ValueError("Expected a .xlsx or .xlsm file.")

    with zipfile.ZipFile(path) as zip_file:
        if "xl/workbook.xml" not in zip_file.namelist():
            raise ValueError(
                "No xl/workbook.xml in the package: this is not a SpreadsheetML workbook "
                "(e.g. a .docx/.pptx renamed to .xlsx). Nothing was audited."
            )
        shared_dangerous_count, shared_samples = _load_shared_strings(zip_file)
        table_map = _load_table_map(zip_file)
        sheet_targets = _load_sheet_targets(zip_file)
        if not sheet_targets:
            raise ValueError(
                "No worksheets could be resolved from xl/workbook.xml and its relationships; "
                "the package is damaged. Nothing was audited."
            )
        defined_names = _defined_names(zip_file)
        core_props = _core_properties(zip_file)
        sheets: list[SheetAudit] = []
        total_formulas = 0
        total_inline_dangerous = 0
        total_hardcoded_constants = 0
        total_hyperlink_formulas = 0
        total_missing_cached_values = 0
        total_non_portable_unprefixed = 0
        total_error_values = 0
        hidden_sheets = 0
        for sheet_name, sheet_path, state in sheet_targets:
            stats = _sheet_formula_count(zip_file, sheet_path)
            total_formulas += stats["formulas"]
            total_inline_dangerous += stats["dangerous_inline"]
            total_hardcoded_constants += stats["hardcoded_constant_count"]
            total_hyperlink_formulas += stats["hyperlink_formula_count"]
            total_missing_cached_values += stats["missing_cached_value_count"]
            total_non_portable_unprefixed += stats["non_portable_unprefixed_count"]
            total_error_values += stats["error_value_count"]
            if state != "visible":
                hidden_sheets += 1
            sheets.append(
                SheetAudit(
                    name=sheet_name,
                    path=sheet_path,
                    state=state,
                    formula_count=stats["formulas"],
                    table_names=_sheet_table_names(zip_file, sheet_path, table_map),
                    inline_dangerous_strings=stats["dangerous_inline"],
                    hardcoded_constant_count=stats["hardcoded_constant_count"],
                    hardcoded_constant_samples=stats["hardcoded_constant_samples"],
                    hyperlink_formula_count=stats["hyperlink_formula_count"],
                    missing_cached_value_count=stats["missing_cached_value_count"],
                    non_portable_unprefixed_count=stats["non_portable_unprefixed_count"],
                    non_portable_unprefixed_samples=stats["non_portable_unprefixed_samples"],
                    error_value_count=stats["error_value_count"],
                    error_value_samples=stats["error_value_samples"],
                )
            )

        external_link_parts = sorted(
            name for name in zip_file.namelist() if name.startswith("xl/externalLinks/")
        )
        calc_mode = None
        workbook_root = _read_xml(zip_file, "xl/workbook.xml")
        workbook_protection = False
        if workbook_root is not None:
            calc_pr = workbook_root.find("main:calcPr", NS)
            if calc_pr is not None:
                calc_mode = calc_pr.attrib.get("calcMode")
            protection = workbook_root.find("main:workbookProtection", NS)
            if protection is not None:
                workbook_protection = any(
                    protection.attrib.get(key) in {"1", "true", "True"}
                    for key in ("lockStructure", "lockWindows", "lockRevision")
                )

        return {
            "path": str(path),
            "core_properties": core_props,
            "macros_present": "xl/vbaProject.bin" in zip_file.namelist(),
            "workbook_protection": workbook_protection,
            "calc_mode": calc_mode,
            "defined_names": defined_names,
            "external_link_parts": external_link_parts,
            "shared_string_dangerous_count": shared_dangerous_count,
            "shared_string_samples": shared_samples,
            "totals": {
                "sheet_count": len(sheets),
                "hidden_sheet_count": hidden_sheets,
                "formula_count": total_formulas,
                "table_count": sum(len(sheet.table_names) for sheet in sheets),
                "dangerous_text_count": shared_dangerous_count + total_inline_dangerous,
                "hardcoded_constant_count": total_hardcoded_constants,
                "hyperlink_formula_count": total_hyperlink_formulas,
                "missing_cached_value_count": total_missing_cached_values,
                "non_portable_unprefixed_count": total_non_portable_unprefixed,
                "error_value_count": total_error_values,
            },
            "sheets": [asdict(sheet) for sheet in sheets],
        }


def blocking_findings(payload: dict[str, Any]) -> list[str]:
    """Findings that must be resolved (or explicitly accepted) before a workbook is shared.

    Heuristic signals (hardcoded constants, hidden sheets, HYPERLINK formulas, missing
    cached values) are reported but do not block: they have legitimate uses and false
    positives, so a human decides.
    """
    totals = payload["totals"]
    found: list[str] = []
    if totals["error_value_count"]:
        found.append(f"{totals['error_value_count']} cell(s) hold cached error values (#REF!, #DIV/0!, #NAME?, ...)")
    if totals["non_portable_unprefixed_count"]:
        found.append(
            f"{totals['non_portable_unprefixed_count']} formula(s) call a selected future function without its documented prefix "
            "(check stored spelling and recipient support before release)"
        )
    if totals["dangerous_text_count"]:
        found.append(
            f"{totals['dangerous_text_count']} text value(s) start with = + - @ or a control character "
            "(formula-injection risk on CSV export); run xlsx_sanitize.py"
        )
    if payload["external_link_parts"]:
        found.append(f"{len(payload['external_link_parts'])} external link part(s); strip or document them")
    if payload["macros_present"]:
        found.append("VBA project present (xl/vbaProject.bin); treat as untrusted")
    return found


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# XLSX Audit: {payload['path']}",
        "",
        "## Summary",
        f"- Sheets: {payload['totals']['sheet_count']}",
        f"- Hidden sheets: {payload['totals']['hidden_sheet_count']}",
        f"- Formulas: {payload['totals']['formula_count']}",
        f"- Tables: {payload['totals']['table_count']}",
        f"- Dangerous text values: {payload['totals']['dangerous_text_count']}",
        f"- Hardcoded constants embedded in formulas: {payload['totals']['hardcoded_constant_count']}",
        f"- HYPERLINK() formulas: {payload['totals']['hyperlink_formula_count']}",
        f"- Formula cells with no cached value: {payload['totals']['missing_cached_value_count']}",
        f"- Non-portable functions missing _xlfn. prefix: {payload['totals']['non_portable_unprefixed_count']}",
        f"- Cells with cached error values: {payload['totals']['error_value_count']}",
        f"- Macros present: {'yes' if payload['macros_present'] else 'no'}",
        f"- Workbook protection: {'yes' if payload['workbook_protection'] else 'no'}",
    ]
    if payload.get("calc_mode"):
        lines.append(f"- Calc mode: {payload['calc_mode']}")

    lines.extend(["", "## Sheets"])
    for sheet in payload["sheets"]:
        tables = ", ".join(sheet["table_names"]) if sheet["table_names"] else "none"
        lines.append(
            f"- {sheet['name']}: state={sheet['state']}, formulas={sheet['formula_count']}, "
            f"tables={tables}, dangerous_inline_strings={sheet['inline_dangerous_strings']}"
        )

    findings = []
    for sheet in payload["sheets"]:
        for label, key in (
            ("hardcoded constant", "hardcoded_constant_samples"),
            ("unprefixed newer function", "non_portable_unprefixed_samples"),
            ("cached error", "error_value_samples"),
        ):
            for sample in sheet.get(key) or []:
                findings.append(f"- {sheet['name']} ({label}): `{sample}`")
    if findings:
        lines.extend(["", "## Formula Findings (samples)"])
        lines.extend(findings)

    lines.extend(["", "## Names And Links"])
    lines.append(
        f"- Defined names: {', '.join(payload['defined_names']) if payload['defined_names'] else 'none'}"
    )
    lines.append(
        f"- External link parts: {', '.join(payload['external_link_parts']) if payload['external_link_parts'] else 'none'}"
    )
    if payload["shared_string_samples"]:
        lines.extend(["", "## Dangerous Text Samples"])
        for sample in payload["shared_string_samples"]:
            lines.append(f"- {sample}")
    lines.extend(["", "## Verdict"])
    if payload["blocking_findings"]:
        lines.append("FAIL - resolve or explicitly accept before sharing:")
        lines.extend(f"- {item}" for item in payload["blocking_findings"])
    else:
        lines.append("PASS - no blocking findings (heuristic signals above still need a human read).")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Audit a .xlsx/.xlsm workbook for formulas, links, hidden sheets, tables, and risky strings."
    )
    parser.add_argument("workbook", type=Path, help="Path to a .xlsx or .xlsm workbook")
    parser.add_argument("--format", choices=("md", "json"), default="md", help="Output format")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Exit 0 even when blocking findings exist (inventory use). Default: exit 1 on blocking findings.",
    )
    args = parser.parse_args(argv)

    if not args.workbook.exists():
        print(f"File not found: {args.workbook}", file=sys.stderr)
        return 2

    try:
        payload = audit_workbook(args.workbook)
    except zipfile.BadZipFile:
        print(f"Cannot read {args.workbook}: not a zip/OOXML package. Re-export it as .xlsx and retry.", file=sys.stderr)
        return 2
    except (ValueError, ET.ParseError) as exc:
        print(f"Cannot audit {args.workbook}: {exc}", file=sys.stderr)
        return 2

    payload["blocking_findings"] = blocking_findings(payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(payload))
    if payload["blocking_findings"] and not args.report_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
