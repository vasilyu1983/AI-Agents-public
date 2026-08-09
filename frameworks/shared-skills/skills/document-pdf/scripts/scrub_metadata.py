#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite a PDF while scrubbing common non-content metadata and active content.",
        epilog=(
            "Dependencies: pip install pymupdf\n"
            "Scrubs common non-content data such as Info/XMP metadata, attachments, "
            "embedded files, JavaScript, and thumbnails before rewriting the PDF.\n\n"
            "Optional flags extend scrubbing to filesystem dates and macOS xattrs."
        ),
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument(
        "--filesystem-date",
        type=str,
        metavar="YYYY-MM-DD",
        help="Set creation and modification dates on the output file (e.g. 2025-09-20)",
    )
    parser.add_argument(
        "--strip-xattrs",
        action="store_true",
        help="Remove macOS extended attributes that leak provenance (quarantine, lastuseddate, screenshot markers)",
    )
    return parser.parse_args()


def strip_macos_xattrs(path: Path) -> None:
    """Remove macOS xattrs that reveal provenance and timestamps."""
    xattrs_to_remove = [
        "com.apple.quarantine",
        "com.apple.lastuseddate#PS",
        "com.apple.metadata:kMDItemIsScreenCapture",
        "com.apple.metadata:kMDItemScreenCaptureType",
        "com.apple.metadata:kMDItemScreenCaptureGlobalRect",
    ]
    for attr in xattrs_to_remove:
        try:
            os.removexattr(str(path), attr)
        except OSError:
            pass


def set_filesystem_dates(path: Path, date_str: str) -> None:
    """Set creation (macOS) and modification dates on the file."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=12)
    timestamp = dt.timestamp()
    os.utime(str(path), (timestamp, timestamp))

    if platform.system() == "Darwin":
        formatted = dt.strftime("%m/%d/%Y %H:%M:%S")
        subprocess.run(
            ["SetFile", "-d", formatted, str(path)],
            check=False, capture_output=True,
        )


def main() -> int:
    args = parse_args()

    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required. Install it with: pip install pymupdf") from exc

    doc = fitz.open(str(args.input_pdf))
    doc.scrub(
        metadata=True,
        xml_metadata=True,
        attached_files=True,
        embedded_files=True,
        javascript=True,
        thumbnails=True,
        reset_fields=False,
        reset_responses=False,
        redactions=False,
    )

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(args.output_pdf), garbage=4, deflate=True)
    doc.close()

    if args.strip_xattrs and platform.system() == "Darwin":
        strip_macos_xattrs(args.output_pdf)

    if args.filesystem_date:
        set_filesystem_dates(args.output_pdf, args.filesystem_date)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
