"""
scan_vault.py — Obsidian / generic markdown vault scanner.

Usage:
    python scan_vault.py inventory /path/to/vault [--format json|csv]
    python scan_vault.py tags      /path/to/vault [--format json|csv]
    python scan_vault.py orphans   /path/to/vault [--format json|csv]
    python scan_vault.py broken-links /path/to/vault [--format json|csv]

Subcommands:
    inventory   Emit one record per .md file with path, title, frontmatter,
                wikilinks, tags, word count, mtime, and inbound wikilink count.
    tags        Aggregate all tags across the vault with per-tag note counts.
    orphans     Find notes with no inbound wikilinks AND no outbound wikilinks.
    broken-links
                List wikilinks whose target does not resolve to a file in the
                vault (by note name, vault-relative path, or attachment name).

Wikilinks and #tags inside fenced code blocks and inline code spans are ignored.

Malformed notes (not valid UTF-8, frontmatter opened with '---' but never
closed, or unreadable) fail the run: their metadata cannot be trusted, and a
lost `status: superseded` would silently pass downstream filters. Pass
--allow-malformed to skip them with a warning instead.

Exit codes: 0 report written; 1 vault missing, no .md files, or malformed notes.

Output formats:
    json (default)  Newline-delimited JSON array to stdout.
    csv             CSV rows to stdout (frontmatter collapsed to key=value pairs).

Stdlib-only. Requires Python 3.8+. Tested on macOS and Linux.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---[ \t]*\r?\n(?:(.*?)\r?\n)?---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Very-light YAML-subset parser for common frontmatter patterns.

    Supports:
      - key: scalar value
      - key: [list, items]
      - key:\n  - item\n  - item
    Does NOT require PyYAML.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1) or ""
    result: dict[str, Any] = {}
    current_key: str | None = None
    list_items: list[str] = []

    def _flush_list() -> None:
        if current_key and list_items:
            result[current_key] = list_items.copy()

    for line in block.splitlines():
        # List item continuation
        stripped = line.strip()
        if stripped.startswith("- ") and current_key is not None:
            list_items.append(stripped[2:].strip())
            continue

        # New key
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            _flush_list()
            list_items = []
            kv = line.split(":", 1)
            key = kv[0].strip()
            value = kv[1].strip() if len(kv) > 1 else ""
            current_key = key
            if value.startswith("[") and value.endswith("]"):
                # Inline list: [a, b, c]
                inner = value[1:-1]
                result[key] = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
            elif value:
                result[key] = value.strip('"').strip("'")
            # else: empty value, wait for list continuation
        # Else: indented continuation we don't parse further

    _flush_list()
    return result


# ---------------------------------------------------------------------------
# Wikilink and tag extraction
# ---------------------------------------------------------------------------

_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]")
_TAG_INLINE_RE = re.compile(r"(?<!\S)#([A-Za-z][A-Za-z0-9_/-]*)")
# Fenced blocks (``` or ~~~, up to 3 spaces of indent; an unclosed fence runs
# to EOF). A closing fence may be longer than its opener.
_FENCE_START_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})[^\r\n]*$")
_INLINE_CODE_RE = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)")


def strip_code(body: str) -> str:
    """Remove fenced code blocks and inline code spans before link/tag extraction."""
    visible: list[str] = []
    marker = ""
    for line in body.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if marker:
            if re.fullmatch(rf"[ ]{{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*", content):
                marker = ""
            visible.append("\n")
            continue
        opening = _FENCE_START_RE.match(content)
        if opening:
            marker = opening.group(1)
            visible.append("\n")
        else:
            visible.append(line)
    return _INLINE_CODE_RE.sub(" ", "".join(visible))


def _extract_wikilinks(body: str) -> list[str]:
    return list(dict.fromkeys(m.strip() for m in _WIKILINK_RE.findall(strip_code(body))))


def _extract_inline_tags(body: str) -> list[str]:
    return list(dict.fromkeys(_TAG_INLINE_RE.findall(strip_code(body))))


def build_link_index(vault: Path) -> set[str]:
    """Return lowercase keys a wikilink may resolve to.

    Obsidian resolves ``[[Name]]`` by file name, ``[[Folder/Name]]`` by
    vault-relative path, and ``[[image.png]]`` by attachment file name.
    """
    keys: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(vault):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            rel = (Path(dirpath) / fname).relative_to(vault).as_posix().lower()
            keys.add(fname.lower())
            keys.add(rel)
            if fname.lower().endswith(".md"):
                keys.add(fname[:-3].lower())
                keys.add(rel[:-3])
    return keys


def resolves(link: str, index: set[str]) -> bool:
    target = link.strip().lstrip("/").lower()
    return target in index or f"{target}.md" in index


def _extract_frontmatter_tags(fm: dict[str, Any]) -> list[str]:
    raw = fm.get("tags") or fm.get("tag") or []
    if isinstance(raw, str):
        raw = [raw]
    return [t.lstrip("#") for t in raw if t]


# ---------------------------------------------------------------------------
# Per-file extraction
# ---------------------------------------------------------------------------

def malformed_reason(raw: bytes) -> str | None:
    """Return why a note's metadata cannot be trusted, or None if it parses."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return f"not valid UTF-8 (byte {exc.start}); re-save the file as UTF-8"
    if text.lstrip("\ufeff").split("\n", 1)[0].strip() == "---" and not _FRONTMATTER_RE.match(text.lstrip("\ufeff")):
        return "frontmatter opened with '---' but never closed; add the closing '---' line"
    return None


def _get_title(text: str, path: Path) -> str:
    """Return H1 title from note body, or fall back to filename stem."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return path.stem


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1)


def _word_count(text: str) -> int:
    return len(text.split())


def _mtime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def scan_file(path: Path, vault_root: Path) -> dict[str, Any]:
    """Return a structured record for a single .md file."""
    try:
        path.resolve().relative_to(vault_root.resolve())
    except ValueError:
        return {"path": str(path.relative_to(vault_root)), "error": "note path resolves outside the vault"}
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"path": str(path.relative_to(vault_root)), "error": str(exc)}
    reason = malformed_reason(raw)
    if reason:
        return {"path": str(path.relative_to(vault_root)), "error": reason}
    text = raw.decode("utf-8").lstrip("\ufeff")

    fm = _parse_frontmatter(text)
    body = _strip_frontmatter(text)
    title = _get_title(body, path)
    wikilinks = _extract_wikilinks(body)
    fm_tags = _extract_frontmatter_tags(fm)
    inline_tags = _extract_inline_tags(body)
    all_tags = list(dict.fromkeys(fm_tags + inline_tags))

    return {
        "path": str(path.relative_to(vault_root)),
        "title": title,
        "frontmatter": fm,
        "wikilinks": wikilinks,
        "tags": all_tags,
        "word_count": _word_count(body),
        "mtime": _mtime_iso(path),
    }


# ---------------------------------------------------------------------------
# Vault walk
# ---------------------------------------------------------------------------

_SKIP_DIRS = {".obsidian", ".trash", ".git", "__pycache__", "node_modules"}


def iter_md_files(vault: Path):
    """Yield all .md files under vault, skipping hidden / system dirs."""
    for dirpath, dirnames, filenames in os.walk(vault):
        # Prune unwanted directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in _SKIP_DIRS and not d.startswith(".")
        ]
        for fname in filenames:
            if fname.lower().endswith(".md"):
                yield Path(dirpath) / fname


def scan_vault(vault: Path) -> list[dict[str, Any]]:
    """Records for parseable notes; main() has already failed or warned on the rest."""
    records = [scan_file(md, vault) for md in iter_md_files(vault)]
    return [r for r in records if "error" not in r]


def find_malformed(vault: Path) -> list[tuple[str, str]]:
    bad = []
    for md in iter_md_files(vault):
        rec = scan_file(md, vault)
        if "error" in rec:
            bad.append((rec["path"], rec["error"]))
    return bad


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def _inbound_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        for link in rec.get("wikilinks", []):
            target = Path(link).stem.lower()
            counts[target] = counts.get(target, 0) + 1
    return counts


def cmd_inventory(vault: Path) -> list[Any]:
    records = scan_vault(vault)
    counts = _inbound_counts(records)
    for rec in records:
        if "error" not in rec:
            rec["inbound_count"] = counts.get(Path(rec["path"]).stem.lower(), 0)
    return records


def cmd_broken_links(vault: Path) -> list[dict[str, Any]]:
    """Return one row per (source note, wikilink target) that resolves to no file."""
    index = build_link_index(vault)
    broken = []
    for rec in scan_vault(vault):
        for link in rec.get("wikilinks", []):
            if not resolves(link, index):
                broken.append({"source": rec["path"], "target": link})
    return sorted(broken, key=lambda r: (r["source"], r["target"]))


def cmd_tags(vault: Path) -> list[dict[str, Any]]:
    """Return tags sorted by note count descending."""
    tag_map: dict[str, list[str]] = {}
    for record in scan_vault(vault):
        note_path = record.get("path", "")
        for tag in record.get("tags", []):
            tag_map.setdefault(tag, []).append(note_path)
    return [
        {"tag": tag, "count": len(notes), "notes": notes}
        for tag, notes in sorted(tag_map.items(), key=lambda x: -len(x[1]))
    ]


def cmd_orphans(vault: Path) -> list[dict[str, Any]]:
    """Find notes that have no outbound wikilinks AND receive no inbound wikilinks."""
    records = scan_vault(vault)

    # Build inbound map: target stem → list of source paths
    inbound: dict[str, list[str]] = {}
    for rec in records:
        for link in rec.get("wikilinks", []):
            # Normalize: strip path separators, use stem only (Obsidian shortlink style)
            target = Path(link).stem.lower()
            inbound.setdefault(target, []).append(rec["path"])

    orphans = []
    for rec in records:
        stem = Path(rec["path"]).stem.lower()
        has_outbound = bool(rec.get("wikilinks"))
        has_inbound = bool(inbound.get(stem))
        if not has_outbound and not has_inbound:
            orphans.append({
                "path": rec["path"],
                "title": rec["title"],
                "word_count": rec.get("word_count", 0),
                "mtime": rec.get("mtime", ""),
            })

    return sorted(orphans, key=lambda r: r["path"])


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _flatten_record(record: dict[str, Any]) -> dict[str, str]:
    """Flatten a nested record to string values for CSV output."""
    flat: dict[str, str] = {}
    for k, v in record.items():
        if isinstance(v, dict):
            flat[k] = "; ".join(f"{dk}={dv}" for dk, dv in v.items())
        elif isinstance(v, list):
            flat[k] = "; ".join(str(i) for i in v)
        else:
            flat[k] = str(v) if v is not None else ""
    return flat


def output_json(data: list[Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def output_csv(data: list[Any]) -> None:
    if not data:
        return
    rows = [_flatten_record(r) if isinstance(r, dict) else r for r in data]
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)
    writer = csv.DictWriter(sys.stdout, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan a markdown vault and extract structured metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "subcommand",
        choices=["inventory", "tags", "orphans", "broken-links"],
        help="inventory=all notes, tags=tag counts, orphans=disconnected notes, "
        "broken-links=wikilinks with no target file",
    )
    parser.add_argument("vault", help="Path to the vault root directory")
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--allow-malformed",
        action="store_true",
        help="Skip malformed notes with a warning instead of failing",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()

    if not vault.is_dir():
        print(f"error: vault path is not a directory: {vault}", file=sys.stderr)
        return 1

    if next(iter_md_files(vault), None) is None:
        print(f"error: no .md files found under {vault}; check the vault path", file=sys.stderr)
        return 1

    bad = find_malformed(vault)
    for rel, reason in bad:
        level = "warning: skipping" if args.allow_malformed else "error:"
        print(f"{level} {rel}: {reason}", file=sys.stderr)
    if bad and not args.allow_malformed:
        print(
            f"error: {len(bad)} malformed note(s); fix them or rerun with --allow-malformed to skip them",
            file=sys.stderr,
        )
        return 1

    subcommand = args.subcommand
    if subcommand == "inventory":
        data = cmd_inventory(vault)
    elif subcommand == "tags":
        data = cmd_tags(vault)
    elif subcommand == "orphans":
        data = cmd_orphans(vault)
    elif subcommand == "broken-links":
        data = cmd_broken_links(vault)
    else:
        print(f"error: unknown subcommand: {subcommand}", file=sys.stderr)
        return 1

    if args.format == "csv":
        output_csv(data)
    else:
        output_json(data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
