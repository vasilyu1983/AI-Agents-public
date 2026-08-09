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


def find_matches(path: Path, pattern: re.Pattern[str]):
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines, start=1):
        if pattern.search(line):
            yield index, line.strip()


def main() -> int:
    failed = False
    for path, pattern, message in RULES:
        for line_no, line in find_matches(path, pattern):
            failed = True
            print(f"{path.relative_to(ROOT)}:{line_no}: {message}")
            print(f"  {line}")

    if failed:
        return 1

    print("No stale example patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
