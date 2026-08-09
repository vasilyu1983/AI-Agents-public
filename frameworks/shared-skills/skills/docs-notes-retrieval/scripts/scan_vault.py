"""
scan_vault.py — Obsidian / generic markdown vault scanner.

Usage:
    python scan_vault.py inventory /path/to/vault [--format json|csv]
    python scan_vault.py tags      /path/to/vault [--format json|csv]
    python scan_vault.py orphans   /path/to/vault [--format json|csv]

Subcommands:
    inventory   Emit one record per .md file with path, title, frontmatter,
                wikilinks, tags, word count, and mtime.
    tags        Aggregate all tags across the vault with per-tag note counts.
    orphans     Find notes with no inbound wikilinks AND no outbound wikilinks.

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

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


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
    block = m.group(1)
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


def _extract_wikilinks(body: str) -> list[str]:
    return list(dict.fromkeys(m.strip() for m in _WIKILINK_RE.findall(body)))


def _extract_inline_tags(body: str) -> list[str]:
    return list(dict.fromkeys(_TAG_INLINE_RE.findall(body)))


def _extract_frontmatter_tags(fm: dict[str, Any]) -> list[str]:
    raw = fm.get("tags") or fm.get("tag") or []
    if isinstance(raw, str):
        raw = [raw]
    return [t.lstrip("#") for t in raw if t]


# ---------------------------------------------------------------------------
# Per-file extraction
# ---------------------------------------------------------------------------

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
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"path": str(path.relative_to(vault_root)), "error": str(exc)}

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
    records = []
    for md in iter_md_files(vault):
        records.append(scan_file(md, vault))
    return records


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_inventory(vault: Path) -> list[Any]:
    return scan_vault(vault)


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
        choices=["inventory", "tags", "orphans"],
        help="inventory=all notes, tags=tag counts, orphans=disconnected notes",
    )
    parser.add_argument("vault", help="Path to the vault root directory")
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()

    if not vault.is_dir():
        print(f"error: vault path is not a directory: {vault}", file=sys.stderr)
        return 1

    subcommand = args.subcommand
    if subcommand == "inventory":
        data = cmd_inventory(vault)
    elif subcommand == "tags":
        data = cmd_tags(vault)
    elif subcommand == "orphans":
        data = cmd_orphans(vault)
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
