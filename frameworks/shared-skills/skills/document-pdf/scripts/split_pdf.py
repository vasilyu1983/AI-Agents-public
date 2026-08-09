#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split a PDF into one PDF per page (default) or extract a page range.",
        epilog="Dependencies: pip install pypdf",
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--each-page", action="store_true", help="Write one file per page.")
    parser.add_argument(
        "--range",
        dest="page_range",
        default=None,
        help="1-based inclusive range like 3-10 (writes a single PDF).",
    )
    parser.add_argument(
        "--prefix",
        default="page",
        help="Filename prefix when using --each-page (default: page).",
    )
    return parser.parse_args()


def parse_range(page_range: str, num_pages: int) -> tuple[int, int]:
    start_str, end_str = page_range.split("-", 1)
    start = max(1, int(start_str))
    end = min(num_pages, int(end_str))
    if start > end:
        raise ValueError("Invalid --range; start must be <= end.")
    return start - 1, end - 1


def main() -> int:
    args = parse_args()

    if (args.page_range is None) == (not args.each_page):
        raise SystemExit("Choose exactly one of: --each-page OR --range 3-10")

    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(args.input_pdf))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.each_page:
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)
            out_path = args.output_dir / f"{args.prefix}_{i:03d}.pdf"
            with out_path.open("wb") as f:
                writer.write(f)
        return 0

    start_idx, end_idx = parse_range(args.page_range, len(reader.pages))
    writer = PdfWriter()
    for i in range(start_idx, end_idx + 1):
        writer.add_page(reader.pages[i])

    out_path = args.output_dir / f"{args.prefix}_{start_idx + 1:03d}-{end_idx + 1:03d}.pdf"
    with out_path.open("wb") as f:
        writer.write(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
