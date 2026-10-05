#!/usr/bin/env python3
"""Append one dated learning entry to a skill's raw learnings.md.

Validates shape, enforces the 150-entry cap, redacts secret- and PII-shaped
substrings, and warns on filter-override violations. Refuses rather than
truncates.
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

# Redaction: these files are committed and, for some skills, published to a
# public mirror (scripts/distribution/sync-repo-into-public.sh). Never let a captured or
# hand-typed entry carry a live secret, bearer token, email address, or a
# home-directory path with a username. Order matters: specific vendor-key
# patterns first, then bearer tokens, then email, then generic high-entropy
# tokens, then home paths. Each pattern replaces its match with a fixed
# placeholder — never with a truncated fragment of the original.
REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Anthropic API keys.
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"), "[REDACTED-API-KEY]"),
    # GitHub personal access tokens.
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "[REDACTED-API-KEY]"),
    # AWS access key IDs.
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED-AWS-KEY]"),
    # Generic OpenAI-shaped / sk- prefixed API keys (checked after the more
    # specific sk-ant- pattern above so that one wins first).
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED-API-KEY]"),
    # Bearer tokens in an Authorization-header-shaped string.
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{10,}"), "[REDACTED-BEARER-TOKEN]"),
    # Email addresses.
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED-EMAIL]"),
    # Home-directory paths (macOS/Linux) — strip the username, keep the rest
    # of the path shape so the entry stays useful.
    (re.compile(r"/Users/[^/\s]+"), "/Users/[REDACTED-USER]"),
    (re.compile(r"/home/[^/\s]+"), "/home/[REDACTED-USER]"),
)

# Generic high-entropy token catch-all, applied last: a run of 32+
# base64url/hex-alphabet characters that mixes letters and digits (so plain
# words or dates don't trip it). Named-vendor patterns above take priority
# because they run first and shrink what's left to scan.
_TOKEN_RUN_RE = re.compile(r"[A-Za-z0-9+/_=-]{32,}")

# An explicit credential assignment is sensitive regardless of value shape.
# Consume the whole value: a length cap could leave the secret's tail intact.
# Quoted values can contain spaces and escaped quotes. If a closing quote is
# missing, redact to the line end. Never consume the next line. Unquoted values
# end at whitespace or a field delimiter. Keep redaction markers unchanged.
_KEY_CONTEXT_RE = re.compile(
    r"(?im)\b(api[_-]?key|access[_-]?token|token|secret|password|passwd|credentials?)"
    r"""(["']?[ \t]*[:=][ \t]*)"""
    r"((?:bearer|basic|token)[ \t]+)?"
    r"""("(?:\\[^\r\n]|[^"\\\r\n])*(?:\\)?(?:"|(?=\r?$))|"""
    r"""'(?:\\[^\r\n]|[^'\\\r\n])*(?:\\)?(?:'|(?=\r?$))|"""
    r"""(?:\[REDACTED-[A-Z-]+\]|[^\s"',;)\]}])+)"""
)
_REDACTED_VALUE_RE = re.compile(r"\[REDACTED-[A-Z-]+\]")


def _looks_like_token(candidate: str) -> bool:
    has_digit = any(c.isdigit() for c in candidate)
    has_alpha = any(c.isalpha() for c in candidate)
    return has_digit and has_alpha


def redact(text: str) -> tuple[str, list[str]]:
    """Return (redacted_text, list of placeholder tags applied)."""
    applied: list[str] = []

    def _key_sub(m: re.Match[str]) -> str:
        value = m.group(4)
        quote = value[0] if value[0] in "\"'" else ""
        inner = value[1:-1] if quote else value
        if _REDACTED_VALUE_RE.fullmatch(inner):
            return m.group(0)
        applied.append("[REDACTED-SECRET]")
        return m.group(1) + m.group(2) + (m.group(3) or "") + quote + "[REDACTED-SECRET]" + quote

    # Redact complete assignments before shape matches can replace just a
    # prefix and leave a credential suffix outside its placeholder.
    text = _KEY_CONTEXT_RE.sub(_key_sub, text)

    for pattern, placeholder in REDACTIONS:
        new_text, n = pattern.subn(placeholder, text)
        if n:
            applied.append(placeholder)
            text = new_text

    def _token_sub(m: re.Match[str]) -> str:
        if _looks_like_token(m.group(0)):
            applied.append("[REDACTED-TOKEN]")
            return "[REDACTED-TOKEN]"
        return m.group(0)

    text = _TOKEN_RUN_RE.sub(_token_sub, text)
    return text, applied


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
    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        die(f"invalid calendar date: {args.date}")

    text = args.text.strip()
    if not text:
        die("empty --text")
    if "\n" in text:
        die("entry must be a single line — split it")

    text, redactions = redact(text)
    if redactions:
        print(
            "append_learning: redacted before writing "
            f"({', '.join(sorted(set(redactions)))}). "
            "Verify the entry still reads correctly.",
            file=sys.stderr,
        )

    if len(text) > 240:
        die(f"entry too long ({len(text)} > 240) — make it more atomic")

    current = ensure_file(raw_path, skill_name)
    if count_entries(current) >= RAW_CAP:
        die(
            f"raw cap reached ({RAW_CAP}). Review consolidation proposals:\n"
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
