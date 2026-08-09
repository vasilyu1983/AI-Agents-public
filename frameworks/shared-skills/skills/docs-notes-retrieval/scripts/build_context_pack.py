"""
build_context_pack.py — Bundle vault notes into an LLM-ready markdown context pack.

Usage:
    # Keyword query — include all notes matching any keyword
    python build_context_pack.py /path/to/vault --query "project planning" --max-chars 40000

    # Specific note paths (relative to vault root)
    python build_context_pack.py /path/to/vault \
        --notes "Projects/Alpha.md" "Projects/Beta.md" \
        --chunk-strategy heading --max-chars 60000

    # Pipe into a file
    python build_context_pack.py /vault --query "weekly review" > context.md

Options:
    --query TEXT            Space-separated keywords; include notes matching any keyword
                            (case-insensitive, searches title + body + tags).
    --notes PATH [PATH...]  Explicit relative note paths instead of keyword search.
    --max-chars INT         Approximate character budget for the output (default: 40000).
                            Limitation: char count, not real token count. Rough ratio:
                            ~4 chars/token for English prose; ~3.5 for code-heavy notes.
                            Add ~20% margin to be safe under model context windows.
    --chunk-strategy        whole    — include the full note body (default for small vaults)
                            heading  — split at H2 boundaries, include only matching chunks
                            paragraph— split at blank-line boundaries
    --order-by              relevance (default) — keyword-hit density first
                            recency  — most recently modified first
    --out PATH              Write to file instead of stdout.

Stdlib-only. Requires Python 3.8+.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse frontmatter/wikilink helpers from scan_vault if available in same dir,
# otherwise inline minimal versions to keep this script self-contained.

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]")
_TAG_INLINE_RE = re.compile(r"(?<!\S)#([A-Za-z][A-Za-z0-9_/-]*)")
_SKIP_DIRS = {".obsidian", ".trash", ".git", "__pycache__", "node_modules"}


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def _parse_frontmatter_block(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body_without_frontmatter)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1)
    body = text[m.end():]
    fm: dict[str, Any] = {}
    current_key: str | None = None
    list_items: list[str] = []

    def flush() -> None:
        if current_key and list_items:
            fm[current_key] = list_items.copy()

    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and current_key:
            list_items.append(stripped[2:].strip())
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            flush()
            list_items = []
            k, _, v = line.partition(":")
            current_key = k.strip()
            v = v.strip().strip('"').strip("'")
            if v.startswith("[") and v.endswith("]"):
                fm[current_key] = [i.strip().strip('"').strip("'") for i in v[1:-1].split(",") if i.strip()]
            elif v:
                fm[current_key] = v
    flush()
    return fm, body


def _fm_to_md(fm: dict[str, Any]) -> str:
    """Render frontmatter as a compact markdown metadata block."""
    if not fm:
        return ""
    lines = ["**Metadata:**"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"- **{k}**: {', '.join(str(i) for i in v)}")
        else:
            lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Vault scanning
# ---------------------------------------------------------------------------

def _mtime(path: Path) -> float:
    return path.stat().st_mtime


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(_mtime(path), tz=timezone.utc).isoformat()


def iter_md_files(vault: Path):
    for dirpath, dirnames, filenames in os.walk(vault):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname.lower().endswith(".md"):
                yield Path(dirpath) / fname


# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def _chunk_whole(body: str) -> list[str]:
    return [body.strip()]


def _chunk_heading(body: str) -> list[str]:
    """Split at H2 (##) boundaries. First chunk = pre-H2 intro."""
    parts = re.split(r"(?m)^(?=## )", body)
    return [p.strip() for p in parts if p.strip()]


def _chunk_paragraph(body: str) -> list[str]:
    """Split on two or more consecutive blank lines."""
    parts = re.split(r"\n{2,}", body)
    return [p.strip() for p in parts if p.strip()]


_CHUNK_FNS = {
    "whole": _chunk_whole,
    "heading": _chunk_heading,
    "paragraph": _chunk_paragraph,
}


# ---------------------------------------------------------------------------
# Keyword matching
# ---------------------------------------------------------------------------

def _relevance_score(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(lower.count(kw.lower()) for kw in keywords)


def _note_matches(note_text: str, note_path: str, keywords: list[str]) -> bool:
    if not keywords:
        return True
    combined = (note_path + " " + note_text).lower()
    return any(kw.lower() in combined for kw in keywords)


# ---------------------------------------------------------------------------
# Context pack builder
# ---------------------------------------------------------------------------

class ContextPackBuilder:
    def __init__(
        self,
        vault: Path,
        keywords: list[str],
        explicit_notes: list[str],
        max_chars: int,
        chunk_strategy: str,
        order_by: str,
    ) -> None:
        self.vault = vault
        self.keywords = keywords
        self.explicit_notes = explicit_notes
        self.max_chars = max_chars
        self.chunk_fn = _CHUNK_FNS.get(chunk_strategy, _chunk_whole)
        self.order_by = order_by

    def _load_note(self, path: Path) -> dict[str, Any]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        fm, body = _parse_frontmatter_block(text)
        h1_match = re.match(r"^# (.+)", body.strip())
        title = h1_match.group(1).strip() if h1_match else path.stem
        return {
            "path": path,
            "rel": str(path.relative_to(self.vault)),
            "title": title,
            "fm": fm,
            "body": body,
            "mtime": _mtime(path),
            "mtime_iso": _mtime_iso(path),
        }

    def _collect_candidates(self) -> list[dict[str, Any]]:
        if self.explicit_notes:
            candidates = []
            for rel in self.explicit_notes:
                p = self.vault / rel
                if p.exists():
                    candidates.append(self._load_note(p))
                else:
                    sys.stderr.write(f"warning: note not found: {rel}\n")
            return candidates

        candidates = []
        for md in iter_md_files(self.vault):
            note = self._load_note(md)
            if _note_matches(note["body"], note["rel"], self.keywords):
                candidates.append(note)
        return candidates

    def _sort_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self.order_by == "recency":
            return sorted(candidates, key=lambda n: -n["mtime"])
        # Default: relevance (keyword density)
        if self.keywords:
            return sorted(
                candidates,
                key=lambda n: -_relevance_score(n["body"] + " " + n["rel"], self.keywords),
            )
        return candidates

    def _render_note_section(self, note: dict[str, Any]) -> str:
        lines = [
            f"## {note['title']}",
            f"",
            f"> **Source:** `{note['rel']}` | **Modified:** {note['mtime_iso']}",
            "",
        ]
        fm_block = _fm_to_md(note["fm"])
        if fm_block:
            lines += [fm_block, ""]
        # Body (strip leading H1 to avoid duplication)
        body = re.sub(r"^# .+\n?", "", note["body"].strip(), count=1).strip()
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")
        return "\n".join(lines)

    def _render_chunk_section(self, note: dict[str, Any], chunk: str) -> str:
        lines = [
            f"## {note['title']} _(excerpt)_",
            f"",
            f"> **Source:** `{note['rel']}` | **Modified:** {note['mtime_iso']}",
            "",
            chunk,
            "",
            "---",
            "",
        ]
        return "\n".join(lines)

    def build(self) -> str:
        candidates = self._sort_candidates(self._collect_candidates())

        header_lines = [
            "# Context Pack",
            "",
            f"**Generated:** {datetime.now(tz=timezone.utc).isoformat()}",
            f"**Vault:** `{self.vault}`",
            f"**Query:** {', '.join(self.keywords) if self.keywords else '(explicit note list)'}",
            f"**Notes found:** {len(candidates)}",
            f"**Chunk strategy:** {self.chunk_fn.__name__.lstrip('_chunk_')}",
            f"**Budget:** {self.max_chars:,} chars",
            "",
            "> **Token budget note:** This pack uses character count as a proxy for tokens.",
            "> Rough ratios: ~4 chars/token (English prose), ~3.5 chars/token (code-heavy).",
            "> Add 20% margin relative to your model's context window limit.",
            "",
            "---",
            "",
        ]
        output_parts = ["".join(l + "\n" for l in header_lines)]
        used = sum(len(p) for p in output_parts)
        included = 0
        truncated = 0

        for note in candidates:
            if self.chunk_fn is _chunk_whole:
                section = self._render_note_section(note)
                if used + len(section) > self.max_chars:
                    truncated += 1
                    continue
                output_parts.append(section)
                used += len(section)
                included += 1
            else:
                chunks = self.chunk_fn(note["body"])
                if self.keywords:
                    chunks = [c for c in chunks if _note_matches(c, note["rel"], self.keywords)] or chunks[:1]
                for chunk in chunks:
                    section = self._render_chunk_section(note, chunk)
                    if used + len(section) > self.max_chars:
                        truncated += 1
                        break
                    output_parts.append(section)
                    used += len(section)
                included += 1

        footer = (
            f"\n---\n\n"
            f"_Pack summary: {included} notes included, {truncated} notes/chunks omitted "
            f"(budget: {self.max_chars:,} chars, used: {used:,} chars)._\n"
        )
        output_parts.append(footer)
        return "".join(output_parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bundle vault notes into an LLM-ready markdown context pack.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("vault", help="Path to the vault root directory")
    p.add_argument(
        "--query",
        nargs="+",
        default=[],
        metavar="KEYWORD",
        help="Keywords to match notes (OR logic). Omit to use --notes.",
    )
    p.add_argument(
        "--notes",
        nargs="+",
        default=[],
        metavar="PATH",
        help="Explicit relative note paths (overrides --query).",
    )
    p.add_argument(
        "--max-chars",
        type=int,
        default=40_000,
        metavar="N",
        help="Character budget for output (default: 40000). See token note in docs.",
    )
    p.add_argument(
        "--chunk-strategy",
        choices=["whole", "heading", "paragraph"],
        default="whole",
        help="How to split note bodies (default: whole).",
    )
    p.add_argument(
        "--order-by",
        choices=["relevance", "recency"],
        default="relevance",
        help="Sort order for included notes (default: relevance).",
    )
    p.add_argument("--out", default=None, metavar="FILE", help="Write output to file instead of stdout.")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    vault = Path(args.vault).expanduser().resolve()

    if not vault.is_dir():
        print(f"error: vault path is not a directory: {vault}", file=sys.stderr)
        return 1

    if not args.query and not args.notes:
        print("error: provide --query KEYWORDS or --notes PATHS", file=sys.stderr)
        return 1

    builder = ContextPackBuilder(
        vault=vault,
        keywords=args.query,
        explicit_notes=args.notes,
        max_chars=args.max_chars,
        chunk_strategy=args.chunk_strategy,
        order_by=args.order_by,
    )
    pack = builder.build()

    if args.out:
        Path(args.out).write_text(pack, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(pack)

    return 0


if __name__ == "__main__":
    sys.exit(main())
