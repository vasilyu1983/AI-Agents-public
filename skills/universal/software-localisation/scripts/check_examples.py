#!/usr/bin/env python3
"""Flag stale example patterns in the software-localisation skill bundle."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RULES = [
    (
        ROOT / "assets" / "nextjs-i18n-setup.md",
        re.compile(r"^### middleware\.ts$|^// middleware\.ts$"),
        "Use `proxy.ts` for current Next.js examples.",
    ),
    (
        ROOT / "references" / "framework-guides.md",
        re.compile(r"^### middleware\.ts$|^// middleware\.ts$"),
        "Use `proxy.ts` for current Next.js examples.",
    ),
    (
        ROOT / "references" / "locale-handling.md",
        re.compile(r"^### Next\.js Middleware Detection$|^// middleware\.ts$|^export function middleware"),
        "Use `proxy.ts` for current Next.js examples.",
    ),
    (
        ROOT / "assets" / "nextjs-i18n-setup.md",
        re.compile(r"params:\s*\{\s*locale:\s*string\s*\}"),
        "App Router locale params should be Promise-based in current examples.",
    ),
    (
        ROOT / "references" / "framework-guides.md",
        re.compile(r"params:\s*\{\s*locale:\s*string\s*\}"),
        "App Router locale params should be Promise-based in current examples.",
    ),
    (
        ROOT / "assets" / "react-i18next-setup.md",
        re.compile(r"\{\{count,\s*number\}\}|\{count,\s*plural,"),
        "Do not use ICU syntax in the plain i18next starter unless an ICU plugin is installed.",
    ),
    (
        ROOT / "data" / "sources.json",
        re.compile(r"next-intl-docs\.vercel\.app"),
        "Use the canonical next-intl.dev docs URL.",
    ),
]

# Match imports rather than prose mentioning the migration. Handles multiline
# named imports as well as side-effect, dynamic, and CommonJS imports.
LINGUI_IMPORT = re.compile(
    r"\b(?:from\s*|import\s*(?:\(\s*)?|require\s*\(\s*)"
    r"['\"]@lingui/macro['\"]"
)


def lingui_matches(root: Path):
    for folder in ("assets", "references"):
        directory = root / folder
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing example directory: {directory}")
        for path in sorted(directory.rglob("*")):
            if path.suffix not in {".md", ".js", ".jsx", ".ts", ".tsx", ".vue"}:
                continue
            contents = path.read_text(encoding="utf-8")
            for match in LINGUI_IMPORT.finditer(contents):
                yield path, contents.count("\n", 0, match.start()) + 1


def find_matches(path: Path, pattern: re.Pattern[str]):
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines, start=1):
        if pattern.search(line):
            yield index, line.strip()


def main() -> int:
    failed = False
    try:
        for path, pattern, message in RULES:
            for line_no, line in find_matches(path, pattern):
                failed = True
                print(f"{path.relative_to(ROOT)}:{line_no}: {message}")
                print(f"  {line}")
        for path, line_no in lingui_matches(ROOT):
            failed = True
            print(f"{path.relative_to(ROOT)}:{line_no}: Replace the old Lingui macro import "
                  "with @lingui/core/macro or @lingui/react/macro.")
    except (OSError, UnicodeError) as exc:
        print(f"Example check could not complete: {exc}", file=sys.stderr)
        return 2

    if failed:
        return 1

    print("No stale example patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
