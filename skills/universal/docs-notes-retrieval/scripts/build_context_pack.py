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
    --max-chars INT         Approximate character budget for selected sections
                            (default: 40000; footer adds more). This is not a
                            token limit; count the final pack with
                            the target model's tokenizer or API before use.
    --chunk-strategy        whole    — include the full note body (default for small vaults)
                            heading  — split at H2 boundaries, include only matching chunks
                            paragraph— split at blank-line boundaries
    --order-by              relevance (default) — keyword-hit density first
                            recency  — most recently modified first
    --status S [S...]       Keep only notes whose frontmatter `status` is in the list
                            (case-insensitive). Add `none` to also keep notes with no
                            status. Filtering happens before ordering.
    --exclude-status S [S...]
                            Drop notes whose `status` is in the list (e.g. superseded
                            archived draft).
    --out PATH              Write to file instead of stdout.

Conflicts: notes that declare `conflicts_with: [[Other Note]]` in frontmatter, or
included notes that share a title under different paths, are kept side by side
under a conflict block with each note's path, status, and mtime. The group is
included or omitted as a unit, never split by the budget. The script does not
detect contradictions in prose; that stays a human or model judgment.

Footer: lists wikilinks in included notes that resolve to no file in the vault.
Wikilinks inside fenced or inline code are ignored.

Malformed notes (not valid UTF-8, frontmatter opened with '---' but never
closed, unreadable, or resolving outside the vault) among scanned or listed
notes fail the run, because a lost `status` would slip past filters.
--allow-malformed skips malformed notes with a warning; paths resolving
outside the vault are always rejected.

Exit codes: 0 pack written; 1 bad arguments, vault, a --notes path not found or
outside the vault, or malformed notes; 2 no notes included (nothing matched, all filtered by status, or all over budget).

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

_FRONTMATTER_RE = re.compile(r"^---[ \t]*\r?\n(?:(.*?)\r?\n)?---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
_SKIP_DIRS = {".obsidian", ".trash", ".git", "__pycache__", "node_modules"}

# Link helpers live in scan_vault.py next to this file. Resolve the directory
# from __file__ so the pair works when the skill is copied or symlinked alone.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from scan_vault import _extract_wikilinks, build_link_index, malformed_reason, resolves
except ImportError:  # pragma: no cover - fallback when copied without scan_vault.py
    def malformed_reason(raw: bytes) -> str | None:
        try:
            text = raw.decode("utf-8").lstrip("\ufeff")
        except UnicodeDecodeError as exc:
            return f"not valid UTF-8 (byte {exc.start}); re-save the file as UTF-8"
        if text.split("\n", 1)[0].strip() == "---" and not _FRONTMATTER_RE.match(text):
            return "frontmatter opened with '---' but never closed; add the closing '---' line"
        return None

    _WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]")
    _FENCE_START_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})[^\r\n]*$")
    _INLINE_CODE_RE = re.compile(r"(`+)(.+?)(?<!`)\1(?!`)")

    def _extract_wikilinks(body: str) -> list[str]:
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
        clean = _INLINE_CODE_RE.sub(" ", "".join(visible))
        return list(dict.fromkeys(m.strip() for m in _WIKILINK_RE.findall(clean)))

    def build_link_index(vault: Path) -> set[str]:
        keys: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(vault):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
            for fname in filenames:
                rel = (Path(dirpath) / fname).relative_to(vault).as_posix().lower()
                keys.update({fname.lower(), rel})
                if fname.lower().endswith(".md"):
                    keys.update({fname[:-3].lower(), rel[:-3]})
        return keys

    def resolves(link: str, index: set[str]) -> bool:
        target = link.strip().lstrip("/").lower()
        return target in index or f"{target}.md" in index


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def _parse_frontmatter_block(text: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body_without_frontmatter)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    block = m.group(1) or ""
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


def _scalar(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value or "").strip()


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
        include_status: list[str] | None = None,
        exclude_status: list[str] | None = None,
        allow_malformed: bool = False,
    ) -> None:
        self.vault = vault
        self.keywords = keywords
        self.explicit_notes = explicit_notes
        self.max_chars = max_chars
        self.chunk_strategy = chunk_strategy if chunk_strategy in _CHUNK_FNS else "whole"
        self.chunk_fn = _CHUNK_FNS[self.chunk_strategy]
        self.order_by = order_by
        self.include_status = {s.lower() for s in (include_status or [])}
        self.exclude_status = {s.lower() for s in (exclude_status or [])}
        self.status_filtered = 0
        self.missing_notes: list[str] = []
        self.malformed: list[tuple[str, str]] = []
        self.allow_malformed = allow_malformed
        self.included_count = 0

    def _load_note(self, path: Path) -> dict[str, Any]:
        try:
            path.resolve().relative_to(self.vault)
        except ValueError:
            return {
                "rel": str(path.relative_to(self.vault)),
                "body": "",
                "error": "note path resolves outside the vault",
            }
        try:
            raw = path.read_bytes()
            error = malformed_reason(raw)
        except OSError as exc:
            raw, error = b"", f"unreadable: {exc}"
        text = raw.decode("utf-8", errors="replace").lstrip("\ufeff")
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
            "status": _scalar(fm.get("status")).lower(),
            "wikilinks": _extract_wikilinks(body),
            "error": error,
        }

    def _usable(self, note: dict[str, Any]) -> bool:
        """Record a malformed note; main() fails the run unless --allow-malformed."""
        if not note["error"]:
            return True
        if "outside the vault" in note["error"]:
            self.missing_notes.append(note["rel"])
        self.malformed.append((note["rel"], note["error"]))
        level = "warning: skipping" if self.allow_malformed else "error:"
        sys.stderr.write(f"{level} {note['rel']}: {note['error']}\n")
        return False

    def _status_ok(self, note: dict[str, Any]) -> bool:
        status = note["status"] or "none"
        if self.include_status and status not in self.include_status:
            return False
        return status not in self.exclude_status

    def _collect_candidates(self) -> list[dict[str, Any]]:
        if self.explicit_notes:
            candidates = []
            for rel in self.explicit_notes:
                p = (self.vault / rel).resolve()
                try:
                    p.relative_to(self.vault)
                except ValueError:
                    self.missing_notes.append(rel)
                    sys.stderr.write(f"error: note path is outside the vault: {rel}\n")
                    continue
                if p.is_file():
                    note = self._load_note(p)
                    if self._usable(note):
                        candidates.append(note)
                else:
                    self.missing_notes.append(rel)
                    sys.stderr.write(f"error: note not found: {rel}\n")
            return candidates

        candidates = []
        for md in iter_md_files(self.vault):
            note = self._load_note(md)
            if self._usable(note) and _note_matches(note["body"], note["rel"], self.keywords):
                candidates.append(note)
        return candidates

    def _filter_status(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        kept = [n for n in candidates if self._status_ok(n)]
        self.status_filtered = len(candidates) - len(kept)
        return kept

    def _conflict_groups(self, notes: list[dict[str, Any]]) -> list[tuple[list[dict[str, Any]], list[str]]]:
        """Group notes that declare `conflicts_with` each other or share a title.

        Returns (members in input order, reasons) for each group of 2+ notes.
        """
        parent = list(range(len(notes)))
        reasons: dict[int, list[str]] = {}

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int, why: str) -> None:
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[rj] = ri
                reasons.setdefault(ri, []).extend(reasons.pop(rj, []))
            reasons.setdefault(ri, [])
            if why not in reasons[ri]:
                reasons[ri].append(why)

        keys: dict[str, int] = {}
        for i, n in enumerate(notes):
            for k in {Path(n["rel"]).stem.lower(), n["rel"].lower(), n["rel"][:-3].lower()}:
                keys.setdefault(k, i)
        by_title: dict[str, int] = {}
        for i, n in enumerate(notes):
            t = n["title"].strip().lower()
            if t in by_title:
                union(by_title[t], i, f"same title \"{n['title']}\"")
            else:
                by_title[t] = i
            raw = n["fm"].get("conflicts_with") or []
            for target in ([raw] if isinstance(raw, str) else raw):
                name = re.sub(r"^\[+|\]+$", "", str(target)).split("|")[0].strip().lower()
                j = keys.get(name, keys.get(Path(name).stem))
                if j is not None and j != i:
                    union(i, j, f"`{n['rel']}` declares conflicts_with `{notes[j]['rel']}`")

        groups: dict[int, list[int]] = {}
        for i in range(len(notes)):
            groups.setdefault(find(i), []).append(i)
        return [
            ([notes[i] for i in members], reasons.get(root, []))
            for root, members in groups.items()
            if len(members) > 1
        ]

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

    def _render_conflict_block(self, members: list[dict[str, Any]], reasons: list[str]) -> str:
        lines = [
            f"## Conflict: {' vs '.join(m['title'] for m in members)}",
            "",
            "> These notes may disagree. All are included below, side by side, with provenance.",
            "> Do not merge them into one claim; resolve by the canonical status, the owner,",
            "> or a verification step, and say which one you relied on.",
            "",
            f"Reason: {'; '.join(reasons) or 'grouped'}",
            "",
            "| Note | Path | Status | Modified |",
            "|---|---|---|---|",
        ]
        for m in members:
            lines.append(f"| {m['title']} | `{m['rel']}` | {m['status'] or '(none)'} | {m['mtime_iso']} |")
        lines += ["", ""]
        return "\n".join(lines)

    def _render_sections(self, note: dict[str, Any]) -> list[str]:
        if self.chunk_fn is _chunk_whole:
            return [self._render_note_section(note)]
        chunks = self.chunk_fn(note["body"])
        if self.keywords:
            chunks = [c for c in chunks if _note_matches(c, note["rel"], self.keywords)] or chunks[:1]
        return [self._render_chunk_section(note, c) for c in chunks]

    def build(self) -> str:
        candidates = self._sort_candidates(self._filter_status(self._collect_candidates()))

        # Pull each conflict group together at the position of its best-ranked member.
        groups = self._conflict_groups(candidates)
        group_of = {id(m): g for g in groups for m in g[0]}
        units: list[tuple[list[dict[str, Any]], list[str] | None]] = []
        seen: set[int] = set()
        for note in candidates:
            if id(note) in seen:
                continue
            g = group_of.get(id(note))
            if g:
                units.append(g)
                seen.update(id(m) for m in g[0])
            else:
                units.append(([note], None))
                seen.add(id(note))

        header_lines = [
            "# Context Pack",
            "",
            f"**Generated:** {datetime.now(tz=timezone.utc).isoformat()}",
            f"**Vault:** `{self.vault}`",
            f"**Query:** {', '.join(self.keywords) if self.keywords else '(explicit note list)'}",
            f"**Notes found:** {len(candidates)}",
            f"**Chunk strategy:** {self.chunk_strategy}",
            f"**Status filter:** include={sorted(self.include_status) or 'all'}, "
            f"exclude={sorted(self.exclude_status) or 'none'} ({self.status_filtered} notes dropped)",
            f"**Conflict groups:** {len(groups)}",
            f"**Budget:** {self.max_chars:,} chars",
            "",
            "> **Token budget note:** This script budgets selected sections in characters, not tokens; the footer adds more.",
            "> Count the complete prompt with the target model's tokenizer or API before use.",
            "",
            "---",
            "",
        ]
        output_parts = ["".join(l + "\n" for l in header_lines)]
        used = sum(len(p) for p in output_parts)
        included: list[dict[str, Any]] = []
        truncated = 0
        omitted_groups: list[str] = []

        for members, reasons in units:
            if reasons is not None:
                # Conflict group: include every member or none, never one side only.
                sections = [self._render_conflict_block(members, reasons)]
                for m in members:
                    sections += self._render_sections(m)
                size = sum(len(x) for x in sections)
                if used + size > self.max_chars:
                    truncated += len(members)
                    omitted_groups.append(", ".join(f"`{m['rel']}`" for m in members))
                    continue
                output_parts += sections
                used += size
                included += members
                continue
            note = members[0]
            sections = self._render_sections(note)
            if self.chunk_fn is _chunk_whole:
                if used + len(sections[0]) > self.max_chars:
                    truncated += 1
                    continue
                output_parts.append(sections[0])
                used += len(sections[0])
            else:
                emitted = False
                for section in sections:
                    if used + len(section) > self.max_chars:
                        truncated += 1
                        break
                    output_parts.append(section)
                    used += len(section)
                    emitted = True
                if not emitted:
                    continue
            included.append(note)

        index = build_link_index(self.vault)
        unresolved = [
            (n["rel"], link) for n in included for link in n["wikilinks"] if not resolves(link, index)
        ]

        footer = [
            "\n---\n",
            f"_Pack summary: {len(included)} notes included, {truncated} notes/chunks omitted "
            f"(budget: {self.max_chars:,} chars, used: {used:,} chars)._",
        ]
        if omitted_groups:
            footer.append("\n**Conflict groups omitted for budget (kept whole, not split):**")
            footer += [f"- {g}" for g in omitted_groups]
        if unresolved:
            footer.append("\n**Unresolved wikilinks (no matching file; fix before citing):**")
            footer += [f"- `{src}` -> [[{target}]]" for src, target in unresolved]
        else:
            footer.append("\n_Unresolved wikilinks: none._")
        output_parts.append("\n".join(footer) + "\n")
        self.included_count = len(included)
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
    p.add_argument(
        "--status",
        nargs="+",
        default=[],
        metavar="STATUS",
        help="Keep only notes with these frontmatter status values; 'none' keeps notes without status.",
    )
    p.add_argument(
        "--exclude-status",
        nargs="+",
        default=[],
        metavar="STATUS",
        help="Drop notes with these frontmatter status values (e.g. superseded archived).",
    )
    p.add_argument(
        "--allow-malformed",
        action="store_true",
        help="Skip malformed notes with a warning instead of failing.",
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
        include_status=args.status,
        exclude_status=args.exclude_status,
        allow_malformed=args.allow_malformed,
    )
    pack = builder.build()

    # Fail loud: an empty pack or a missing explicit note must not look like success.
    if builder.missing_notes:
        return 1
    if builder.malformed and not args.allow_malformed:
        print(
            f"error: {len(builder.malformed)} malformed note(s); fix them or rerun with --allow-malformed to skip them",
            file=sys.stderr,
        )
        return 1
    if builder.included_count == 0:
        print("error: no notes included (no match, all filtered by status, or over budget)", file=sys.stderr)
        return 2

    if args.out:
        Path(args.out).write_text(pack, encoding="utf-8")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(pack)

    return 0


if __name__ == "__main__":
    sys.exit(main())
