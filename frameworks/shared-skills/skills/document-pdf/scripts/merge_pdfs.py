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


def main() -> int:
    args = parse_args()

    from pypdf import PdfMerger

    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)

    merger = PdfMerger()
    try:
        for pdf_path in args.input_pdfs:
            merger.append(str(pdf_path))
        merger.write(str(args.output_pdf))
    finally:
        merger.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
