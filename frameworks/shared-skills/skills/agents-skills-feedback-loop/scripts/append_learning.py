#!/usr/bin/env python3
"""Append one dated learning entry to a skill's raw learnings.md.

Validates shape, enforces the 150-entry cap, and warns on filter-override violations.
Refuses rather than truncates.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

SECTIONS = (
    "Patterns That Work",
    "Mistakes to Avoid",
    "Domain Knowledge",
    "Open Questions",
    "Consolidated Principles",
)

RAW_CAP = 150
HEADER_TEMPLATE = "# {skill_name} — Learnings\n\n"
ENTRY_RE = re.compile(r"^- \[\d{4}-\d{2}-\d{2}\] ")


def die(msg: str, code: int = 1) -> None:
    print(f"append_learning: {msg}", file=sys.stderr)
    sys.exit(code)


def section_block(name: str) -> str:
    return f"## {name}\n\n"


def ensure_file(path: Path, skill_name: str) -> str:
    if path.exists():
        return path.read_text()
    body = HEADER_TEMPLATE.format(skill_name=skill_name)
    for s in SECTIONS:
        body += section_block(s)
    path.write_text(body)
    return body


def count_entries(text: str) -> int:
    return sum(1 for line in text.splitlines() if ENTRY_RE.match(line))


def read_filter_override(consolidated_path: Path) -> list[str]:
    if not consolidated_path.exists():
        return []
    text = consolidated_path.read_text()
    m = re.search(r"^## Filter Override\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    return [
        line.strip("- ").strip()
        for line in m.group(1).splitlines()
        if line.strip().startswith("- ")
    ]


def insert_entry(text: str, section: str, entry: str) -> str:
    pattern = re.compile(
        rf"^(## {re.escape(section)}\s*\n\n?)((?:.*\n)*?)(?=^## |\Z)",
        re.M,
    )
    m = pattern.search(text)
    if not m:
        die(f"section not found in file: {section!r}")
    head, body = m.group(1), m.group(2)
    body = re.sub(r"^<!--.*?-->\n?", "", body, flags=re.M)
    new_body = head + entry + "\n" + body
    return text[: m.start()] + new_body + text[m.end():]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skill_dir", type=Path, help="path to the host skill directory")
    p.add_argument("--section", required=True, choices=SECTIONS)
    p.add_argument("--text", required=True, help="one-sentence atomic insight")
    p.add_argument("--date", default=dt.date.today().isoformat())
    args = p.parse_args()

    if not args.skill_dir.is_dir():
        die(f"not a directory: {args.skill_dir}")

    skill_name = args.skill_dir.name
    raw_path = args.skill_dir / "learnings.md"
    consolidated_path = args.skill_dir / "learnings.consolidated.md"

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        die(f"bad date (need YYYY-MM-DD): {args.date}")

    text = args.text.strip()
    if not text:
        die("empty --text")
    if "\n" in text:
        die("entry must be a single line — split it")
    if len(text) > 240:
        die(f"entry too long ({len(text)} > 240) — make it more atomic")

    current = ensure_file(raw_path, skill_name)
    if count_entries(current) >= RAW_CAP:
        die(
            f"raw cap reached ({RAW_CAP}). Run consolidate.py before appending more:\n"
            f"  python3 {Path(__file__).parent}/consolidate.py {args.skill_dir}",
            code=2,
        )

    overrides = read_filter_override(consolidated_path)
    if overrides:
        print("append_learning: filter override active for this skill:", file=sys.stderr)
        for o in overrides:
            print(f"  - {o}", file=sys.stderr)
        print("append_learning: confirm the entry honors these. (advisory)", file=sys.stderr)

    entry = f"- [{args.date}] {text}"
    updated = insert_entry(current, args.section, entry)
    raw_path.write_text(updated)
    print(f"appended to {raw_path} under {args.section!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
