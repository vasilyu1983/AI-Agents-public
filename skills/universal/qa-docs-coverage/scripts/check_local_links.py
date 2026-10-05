#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html.parser
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_DEF_RE = re.compile(r"^[ \t]{0,3}\[([^\]]+)\]:\s+(\S+)", re.MULTILINE)
REFERENCE_USE_RE = re.compile(r"!?\[([^\]]+)\]\[([^\]]*)\]")
AUTOLINK_RE = re.compile(r"<((?:https?://|mailto:)[^>]+)>")

# Fenced code blocks (``` or ~~~, with optional language) and inline-code spans.
# Stripping these before link extraction prevents false positives from prose like
# `res.get(...)`, JS destructuring `[...args]`, or task-list checkboxes `[x]`.
FENCED_CODE_RE = re.compile(
    r"(?ms)^([ \t]{0,3})(`{3,}|~{3,})[^\n]*\n.*?^\1\2\s*$"
)
INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
INDENTED_CODE_RE = re.compile(r"(?m)^(?: {4,}|\t)[^\n]*$")


def _strip_code(text: str) -> str:
    """Remove fenced, indented, and inline code so link regexes don't match code snippets.

    Preserves line numbers by replacing matches with blank-line equivalents — the
    output is only fed to regex-based link extraction, never re-rendered.
    """
    def blank(match: re.Match) -> str:
        return "\n" * match.group(0).count("\n")

    text = FENCED_CODE_RE.sub(blank, text)
    text = INDENTED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


@dataclass(frozen=True)
class MissingLink:
    source_file: Path
    target: str


class _HtmlLinkExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            if tag == "a" and name == "href":
                self.targets.append(value)
            elif tag in {"img", "source"} and name in {"src", "srcset"}:
                self.targets.append(value.split(" ", 1)[0])


def _is_external_link(target: str) -> bool:
    target = target.strip()
    return (
        not target
        or target.startswith("#")
        or target.startswith("mailto:")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("data:")
    )


def _normalize_target(target: str) -> str:
    target = target.strip()
    target = target.split("#", 1)[0]
    target = target.split("?", 1)[0]
    return target.strip().strip("<>")


def _iter_markdown_files(root: Path) -> list[Path]:
    markdown_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        if "/.archive/" in dirpath:
            continue
        dirnames[:] = [
            d
            for d in dirnames
            if d not in {".git", "node_modules", ".venv", "dist", "build"}
        ]
        for filename in filenames:
            if filename.endswith(".md"):
                markdown_files.append(Path(dirpath) / filename)
    return markdown_files


def _collect_targets(text: str) -> list[str]:
    # Strip code first; matches inside code blocks are not links.
    text = _strip_code(text)

    targets: list[str] = []

    # Inline markdown links and images: [label](target), ![alt](target)
    targets.extend(INLINE_LINK_RE.findall(text))

    # Reference-style links: [label][ref] and [ref][]
    reference_defs = {
        key.strip().lower(): value.strip()
        for key, value in REFERENCE_DEF_RE.findall(text)
    }
    for label, ref in REFERENCE_USE_RE.findall(text):
        key = (ref or label).strip().lower()
        if key in reference_defs:
            targets.append(reference_defs[key])

    # HTML links/images embedded in markdown
    parser = _HtmlLinkExtractor()
    parser.feed(text)
    targets.extend(parser.targets)

    # Autolinks are always external if present, so keep them out of local checks
    for external_target in AUTOLINK_RE.findall(text):
        targets.append(external_target)

    return targets


def find_missing_local_links(root: Path) -> list[MissingLink]:
    missing: list[MissingLink] = []
    for markdown_file in _iter_markdown_files(root):
        try:
            text = markdown_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = markdown_file.read_text(encoding="utf-8", errors="replace")

        for raw_target in _collect_targets(text):
            if _is_external_link(raw_target):
                continue
            target = _normalize_target(raw_target)
            if not target:
                continue
            full_target = (markdown_file.parent / target).resolve()
            if not full_target.exists():
                missing.append(MissingLink(source_file=markdown_file, target=raw_target))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown files for missing local link and asset targets."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root path not found: {root}", file=sys.stderr)
        return 2

    missing = find_missing_local_links(root)
    if missing:
        print("Missing local link targets:")
        for item in missing:
            print(f"- {item.source_file}: {item.target}")
        return 1

    markdown_count = len(_iter_markdown_files(root))
    print(f"OK: {markdown_count} markdown files; no missing local link targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
