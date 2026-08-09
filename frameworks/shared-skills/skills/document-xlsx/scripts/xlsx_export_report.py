#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _require_pandas():
    try:
        import pandas as pd  # type: ignore

        return pd
    except ImportError as exc:
        raise RuntimeError("Missing dependency: pandas. Install with: pip install pandas XlsxWriter") from exc


def load_dataframe(input_path: Path):
    pd = _require_pandas()
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path)
    if suffix == ".json":
        return pd.read_json(input_path)
    if suffix == ".parquet":
        return pd.read_parquet(input_path)
    raise ValueError("Supported input formats: .csv, .json, .parquet")


def export_report(input_path: Path, output_path: Path, sheet_name: str, table_name: str, title: str | None) -> None:
    pd = _require_pandas()
    try:
        import xlsxwriter  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Missing dependency: XlsxWriter. Install with: pip install pandas XlsxWriter") from exc

    df = load_dataframe(input_path)
    startrow = 1 if title else 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=startrow)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format({"bold": True, "bg_color": "#D9E2F3"})
        title_format = workbook.add_format({"bold": True, "font_size": 14})

        if title:
            worksheet.write("A1", title, title_format)

        freeze_row = startrow + 1
        worksheet.freeze_panes(freeze_row, 0)
        last_col = max(len(df.columns) - 1, 0)
        worksheet.autofilter(startrow, 0, max(startrow, startrow + len(df)), last_col)

        for idx, column in enumerate(df.columns):
            width = max(len(str(column)), 12)
            if not df.empty:
                width = min(40, max(width, df[column].astype(str).map(len).max()))
            worksheet.set_column(idx, idx, width + 2)

        if not df.empty:
            worksheet.add_table(
                startrow,
                0,
                startrow + len(df),
                len(df.columns) - 1,
                {
                    "name": table_name,
                    "style": "Table Style Medium 2",
                    "columns": [{"header": col, "header_format": header_format} for col in df.columns],
                    "autofilter": True,
                },
            )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Export CSV/JSON/Parquet data to a table-first .xlsx workbook."
    )
    parser.add_argument("input_path", type=Path, help="Input .csv, .json, or .parquet file")
    parser.add_argument("output_path", type=Path, help="Output .xlsx path")
    parser.add_argument("--sheet-name", default="Report", help="Worksheet name (default: Report)")
    parser.add_argument("--table-name", default="ReportTable", help="Excel table name (default: ReportTable)")
    parser.add_argument("--title", default=None, help="Optional title written to A1")
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"File not found: {args.input_path}", file=sys.stderr)
        return 2
    if args.output_path.suffix.lower() != ".xlsx":
        print("Output path must end in .xlsx", file=sys.stderr)
        return 2

    try:
        export_report(args.input_path, args.output_path, args.sheet_name, args.table_name, args.title)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
