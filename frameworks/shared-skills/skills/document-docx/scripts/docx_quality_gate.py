#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from docx_inspect_ooxml import inspect_docx

JINJA_PATTERN = re.compile(r"(\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\})", re.DOTALL)
ALLOWED_SUFFIXES = {".docx", ".dotx", ".docm", ".dotm"}


def _collect_word_xml_matches(zip_file: zipfile.ZipFile) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for name in sorted(zip_file.namelist()):
        if not name.startswith("word/") or not name.endswith(".xml"):
            continue
        with zip_file.open(name) as file:
            text = file.read().decode("utf-8", errors="ignore")
        found = sorted({match.group(1).strip() for match in JINJA_PATTERN.finditer(text)})
        if found:
            matches.append({"part": name, "matches": found})
    return matches


def _validate_document_xml(zip_file: zipfile.ZipFile) -> str | None:
    try:
        with zip_file.open("word/document.xml") as file:
            ET.fromstring(file.read())
        return None
    except KeyError:
        return "Missing word/document.xml"
    except ET.ParseError as exc:
        return f"word/document.xml is not well-formed XML: {exc}"


def _run_libreoffice_smoke(path: Path) -> dict[str, Any]:
    binary = shutil.which("libreoffice") or shutil.which("soffice")
    if not binary:
        return {"available": False, "passed": None, "details": "LibreOffice not found in PATH"}

    with tempfile.TemporaryDirectory(prefix="docx-quality-") as temp_dir:
        command = [
            binary,
            "--headless",
            "--convert-to",
            "pdf",
            str(path),
            "--outdir",
            temp_dir,
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        output_pdf = Path(temp_dir) / f"{path.stem}.pdf"
        passed = result.returncode == 0 and output_pdf.exists()
        details = (result.stderr or result.stdout).strip() or None
        return {"available": True, "passed": passed, "details": details}


def quality_gate(path: Path, max_mb: float, check_libreoffice: bool) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return {
            "path": str(path),
            "passed": False,
            "issues": [f"File not found: {path}"],
            "warnings": [],
        }

    suffix = path.suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        warnings.append(
            f"Unexpected suffix {suffix or '<none>'}. Expected one of: {', '.join(sorted(ALLOWED_SUFFIXES))}"
        )
    if suffix in {".docm", ".dotm"}:
        warnings.append("Macro-enabled Office file detected. Treat as untrusted input by default.")

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        issues.append("File is empty.")
    if size_bytes / 1_048_576 > max_mb:
        issues.append(f"File exceeds {max_mb:.1f} MB.")

    unresolved_tags: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as zip_file:
            xml_issue = _validate_document_xml(zip_file)
            if xml_issue:
                issues.append(xml_issue)
            unresolved_tags = _collect_word_xml_matches(zip_file)
    except zipfile.BadZipFile:
        issues.append("Not a valid Office Open XML zip package.")

    if unresolved_tags:
        issues.append("Unresolved template tags detected in one or more Word XML parts.")

    inspection: dict[str, Any] | None = None
    try:
        inspect_result = inspect_docx(path)
        inspection = {"parts_present": inspect_result.parts_present, "counts": inspect_result.counts}
        if inspect_result.counts.get("w:ins", 0) or inspect_result.counts.get("w:del", 0):
            warnings.append("Tracked revision signals detected. Inspect before editing with high-level libraries.")
        if inspect_result.counts.get("comments:present", 0):
            warnings.append("Comments are present. Preserve review metadata intentionally.")
    except Exception as exc:  # pragma: no cover - defensive only
        warnings.append(f"OOXML inspection failed: {exc}")

    libreoffice_result = None
    if check_libreoffice:
        libreoffice_result = _run_libreoffice_smoke(path)
        if libreoffice_result["available"] and libreoffice_result["passed"] is False:
            issues.append("LibreOffice smoke conversion failed.")

    return {
        "path": str(path),
        "passed": not issues,
        "size_bytes": size_bytes,
        "issues": issues,
        "warnings": warnings,
        "unresolved_template_tags": unresolved_tags,
        "inspection": inspection,
        "libreoffice": libreoffice_result,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Run lightweight quality gates against a DOCX template or generated document."
    )
    parser.add_argument("docx", type=Path, help="Path to a DOCX/DOTX/DOCM/DOTM file")
    parser.add_argument("--max-mb", type=float, default=10.0, help="Maximum file size in MB")
    parser.add_argument(
        "--check-libreoffice",
        action="store_true",
        help="Attempt a LibreOffice headless conversion smoke test if LibreOffice is installed",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args(argv)

    result = quality_gate(args.docx, max_mb=args.max_mb, check_libreoffice=args.check_libreoffice)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"File: {result['path']}")
        print(f"Passed: {result['passed']}")
        if result.get("issues"):
            print("Issues:")
            for item in result["issues"]:
                print(f"- {item}")
        if result.get("warnings"):
            print("Warnings:")
            for item in result["warnings"]:
                print(f"- {item}")

    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
