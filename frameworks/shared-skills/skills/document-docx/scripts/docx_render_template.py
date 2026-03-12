#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _require_docxtpl():
    try:
        from docxtpl import DocxTemplate  # type: ignore

        return DocxTemplate
    except ImportError as exc:
        raise RuntimeError("Missing dependency: docxtpl. Install with: pip install docxtpl") from exc


def render_template(template_path: Path, context: dict[str, Any], output_path: Path) -> None:
    DocxTemplate = _require_docxtpl()
    doc = DocxTemplate(str(template_path))
    doc.render(context)
    doc.save(str(output_path))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render a docxtpl template (.docx) from a JSON context.")
    parser.add_argument("template", type=Path, help="Path to a .docx template file")
    parser.add_argument("context", type=Path, help="Path to a JSON file containing template variables")
    parser.add_argument("output", type=Path, help="Output .docx path")
    args = parser.parse_args(argv)

    if not args.template.exists():
        print(f"Template not found: {args.template}", file=sys.stderr)
        return 2
    if not args.context.exists():
        print(f"Context not found: {args.context}", file=sys.stderr)
        return 2

    try:
        context = json.loads(args.context.read_text(encoding="utf-8"))
        if not isinstance(context, dict):
            raise ValueError("Context JSON must be an object/dict at the top level.")
        render_template(args.template, context, args.output)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

