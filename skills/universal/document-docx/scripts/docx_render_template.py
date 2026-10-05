#!/usr/bin/env python3
"""Render a docxtpl template from a JSON context, failing closed.

docxtpl's defaults fail open: a variable missing from the context renders as an
empty string (exit 0, no tag left for a quality gate to find), and values
containing XML metacharacters (&, <, >) are inserted unescaped, which drops text
or corrupts the part. This script renders with StrictUndefined and autoescape so
both cases either render correctly or stop with a non-zero exit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _require_docxtpl():
    try:
        from docxtpl import DocxTemplate  # type: ignore
        from jinja2 import Environment, StrictUndefined

        return DocxTemplate, Environment, StrictUndefined
    except ImportError as exc:
        raise RuntimeError("Missing dependency: docxtpl. Install with: pip install docxtpl") from exc


def render_template(
    template_path: Path, context: dict[str, Any], output_path: Path, allow_missing: bool = False
) -> None:
    DocxTemplate, Environment, StrictUndefined = _require_docxtpl()
    doc = DocxTemplate(str(template_path))
    if not allow_missing:
        missing = sorted(doc.get_undeclared_template_variables(context=context))
        if missing:
            raise ValueError(
                "Template variables missing from context: "
                + ", ".join(missing)
                + ". Add them to the JSON (use \"\" for an intentional blank) or pass --allow-missing."
            )
    env = Environment() if allow_missing else Environment(undefined=StrictUndefined)
    doc.render(context, jinja_env=env, autoescape=True)
    doc.save(str(output_path))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Render a docxtpl template (.docx) from a JSON context.")
    parser.add_argument("template", type=Path, help="Path to a .docx template file")
    parser.add_argument("context", type=Path, help="Path to a JSON file containing template variables")
    parser.add_argument("output", type=Path, help="Output .docx path")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Render variables absent from the context as empty strings (docxtpl default). Off by default.",
    )
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
        render_template(args.template, context, args.output, allow_missing=args.allow_missing)
    except Exception as exc:
        print(f"Render failed: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
