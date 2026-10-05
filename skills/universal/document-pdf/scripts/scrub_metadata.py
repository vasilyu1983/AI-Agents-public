#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite a PDF while scrubbing common non-content metadata and active content.",
        epilog=(
            "Dependencies: pip install pymupdf\n"
            "Scrubs common non-content data such as Info/XMP metadata, attachments, "
            "embedded files, JavaScript, and thumbnails before rewriting the PDF.\n"
            "Content is preserved by default: invisible text layers (e.g. OCRmyPDF "
            "searchable text on scans) and hyperlinks are kept unless you opt in.\n\n"
            "Optional flags extend scrubbing to filesystem dates and macOS xattrs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument(
        "--remove-hidden-text",
        action="store_true",
        help=(
            "DESTRUCTIVE: also delete invisible (render-mode 3) text. This removes the "
            "searchable OCR layer of scanned PDFs; only use when hidden text is itself the leak."
        ),
    )
    parser.add_argument(
        "--remove-links",
        action="store_true",
        help="DESTRUCTIVE: also delete all link annotations (URLs and internal navigation).",
    )
    parser.add_argument(
        "--filesystem-date",
        type=str,
        metavar="YYYY-MM-DD",
        help=(
            "Normalise the output file's creation/modification timestamps (e.g. to a release "
            "or reproducible-build date). Never use it to misrepresent when a record was "
            "created: backdating evidence, contracts, or regulated records can be fraud."
        ),
    )
    parser.add_argument(
        "--strip-xattrs",
        action="store_true",
        help="Remove all extended attributes from the output on macOS (requires xattr)",
    )
    return parser.parse_args()


def strip_macos_xattrs(path: Path) -> None:
    """Use the native tool; Python's os xattr APIs are not available on macOS."""
    subprocess.run(["xattr", "-c", str(path)], check=True, capture_output=True)
    remaining = subprocess.run(["xattr", str(path)], check=True, capture_output=True, text=True).stdout.strip()
    if remaining:
        raise OSError(f"Extended attributes remain after xattr -c: {remaining.replace(chr(10), ', ')}")


def set_filesystem_dates(path: Path, date_str: str) -> None:
    """Set creation (macOS) and modification dates on the file."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=12)
    timestamp = dt.timestamp()
    os.utime(str(path), (timestamp, timestamp))

    if platform.system() == "Darwin":
        formatted = dt.strftime("%m/%d/%Y %H:%M:%S")
        subprocess.run(
            ["SetFile", "-d", formatted, str(path)],
            check=True, capture_output=True,
        )


def run() -> int:
    args = parse_args()

    if args.filesystem_date:
        try:
            datetime.strptime(args.filesystem_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("--filesystem-date must be a valid YYYY-MM-DD date") from None
    if args.strip_xattrs and platform.system() != "Darwin":
        raise ValueError("--strip-xattrs requires macOS and the xattr command")
    if args.input_pdf.resolve() == args.output_pdf.resolve():
        raise ValueError("Input and output must be different paths; keep the source PDF")

    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required. Install it with: pip install pymupdf") from exc

    if args.remove_hidden_text:
        print(
            "WARNING: --remove-hidden-text deletes invisible text, including OCR layers; "
            "the output may no longer be searchable or accessible.",
            file=sys.stderr,
        )
    if args.remove_links:
        print("WARNING: --remove-links deletes every hyperlink and internal link.", file=sys.stderr)

    if not args.input_pdf.is_file():
        raise SystemExit(f"Input not found: {args.input_pdf}")
    try:
        doc = pymupdf.open(str(args.input_pdf), filetype="pdf")
    except Exception as exc:
        raise SystemExit(f"Cannot read {args.input_pdf} as a PDF ({exc}). Check it is a real, undamaged PDF.")
    temporary_path = None
    try:
        if not doc.is_pdf:
            raise ValueError(f"{args.input_pdf} is not a PDF")
        if doc.needs_pass:
            raise ValueError(f"{args.input_pdf} is encrypted; decrypt it first (qpdf --decrypt) and retry.")
        doc.scrub(
            metadata=True,
            xml_metadata=True,
            attached_files=True,
            embedded_files=True,
            javascript=True,
            thumbnails=True,
            # PyMuPDF defaults both of these to True, which silently destroys content.
            hidden_text=args.remove_hidden_text,
            remove_links=args.remove_links,
            reset_fields=False,
            reset_responses=False,
            redactions=False,
        )
        args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=args.output_pdf.parent, suffix=".pdf", delete=False) as temp:
            temporary_path = Path(temp.name)
        doc.save(str(temporary_path), garbage=4, deflate=True)
        if args.filesystem_date:
            set_filesystem_dates(temporary_path, args.filesystem_date)
        if args.strip_xattrs:
            strip_macos_xattrs(temporary_path)
        os.replace(temporary_path, args.output_pdf)
    finally:
        doc.close()
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return 0


def main() -> int:
    try:
        return run()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"PDF scrub failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
