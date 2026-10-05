#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge PDFs in order.",
        epilog="Dependencies: pip install pypdf",
    )
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("input_pdfs", nargs="+", type=Path)
    return parser.parse_args()


def open_reader(path: Path):
    """Open a PDF with pypdf or exit 2 with an actionable message (no traceback)."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    if not path.is_file():
        raise SystemExit(f"Input not found: {path}")
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise SystemExit(f"{path} is encrypted; decrypt it first (qpdf --decrypt) and retry.")
        _ = len(reader.pages)
    except (PdfReadError, ValueError, OSError) as exc:
        raise SystemExit(f"Cannot read {path} as a PDF ({exc}). Check it is a real, undamaged PDF.")
    return reader


def main() -> int:
    args = parse_args()

    from pypdf import PdfWriter

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)

    readers = [open_reader(pdf_path) for pdf_path in args.input_pdfs]
    writer = PdfWriter()
    for reader in readers:
        writer.append(reader)

    with args.output_pdf.open("wb") as f:
        writer.write(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
