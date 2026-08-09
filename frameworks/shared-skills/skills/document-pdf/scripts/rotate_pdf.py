#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rotate all pages of a PDF by 90/180/270 degrees.",
        epilog="Dependencies: pip install pypdf",
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--degrees", type=int, choices=(90, 180, 270), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(args.input_pdf))
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(args.degrees)
        writer.add_page(page)

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    with args.output_pdf.open("wb") as f:
        writer.write(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
