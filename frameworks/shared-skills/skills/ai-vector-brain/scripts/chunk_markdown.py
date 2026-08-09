#!/usr/bin/env python3
"""Chunk Markdown files by headings, with optional parent-child emission.

Default mode (`--unit chunk`): one chunk per leaf section, anchor-stable.

Parent-child mode (`--unit parent_child`): each leaf chunk also has a parent
chunk covering the broader containing section (depth = `--parent-depth`).
Emit order is parent-first so the consumer can resolve `parent_chunk_ref`
against an earlier line.

Output is JSONL on stdout. Each record carries a stable string `chunk_ref`
(`source_path#anchor`) so consumers can wire `parent_chunk_id` after they
assign DB IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-") or "section"


def token_estimate(text: str) -> int:
    return max(1, len(text.split()))


def anchor_for(headings: list[str]) -> str:
    return "#".join(slug(h) for h in headings) if headings else "root"


def chunk_ref(source_path: str, anchor: str) -> str:
    return f"{source_path}#{anchor}"


def emit(
    *,
    source_path: str,
    index: int,
    headings: list[str],
    lines: list[str],
    unit_type: str,
    parent_ref: str | None = None,
) -> dict:
    content = "\n".join(lines).strip()
    section_path = " > ".join(headings) if headings else source_path
    anchor = anchor_for(headings)
    return {
        "source_path": source_path,
        "chunk_index": index,
        "content": content,
        "section_path": section_path,
        "citation_anchor": anchor,
        "chunk_ref": chunk_ref(source_path, anchor),
        "parent_chunk_ref": parent_ref,
        "unit_type": unit_type,
        "token_count": token_estimate(content),
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def chunk_leaves(path: Path, max_tokens: int):
    """Yield (headings, lines) pairs for each leaf section."""
    headings: list[str] = []
    current: list[str] = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING_RE.match(line)
        if match and current:
            yield list(headings), list(current)
            current = []
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings = headings[: level - 1] + [title]
        current.append(line)
        if token_estimate("\n".join(current)) >= max_tokens and not line.startswith("```"):
            yield list(headings), list(current)
            current = []

    if current:
        yield list(headings), list(current)


def chunk_file(path: Path, max_tokens: int, unit: str, parent_depth: int):
    source_path = path.as_posix()

    if unit == "chunk":
        for index, (headings, lines) in enumerate(chunk_leaves(path, max_tokens)):
            yield emit(
                source_path=source_path,
                index=index,
                headings=headings,
                lines=lines,
                unit_type="chunk",
            )
        return

    # parent_child: emit a parent for each distinct ancestor at parent_depth,
    # then the leaf chunks pointing back to it.
    parents_emitted: dict[str, int] = {}
    pending_parents: dict[str, list[str]] = {}
    leaves: list[tuple[list[str], list[str]]] = list(chunk_leaves(path, max_tokens))

    # First pass: collect parent line buffers (concatenated leaf lines under
    # the same ancestor anchor at depth = parent_depth).
    for headings, lines in leaves:
        if len(headings) >= parent_depth:
            parent_headings = headings[:parent_depth]
            parent_anchor = anchor_for(parent_headings)
            pending_parents.setdefault(parent_anchor, []).extend(lines)

    # Second pass: stable index assignment, parent-first.
    next_index = 0
    parent_index_by_anchor: dict[str, int] = {}
    for headings, _ in leaves:
        if len(headings) < parent_depth:
            continue
        parent_headings = headings[:parent_depth]
        parent_anchor = anchor_for(parent_headings)
        if parent_anchor in parent_index_by_anchor:
            continue
        parent_index_by_anchor[parent_anchor] = next_index
        next_index += 1
        yield emit(
            source_path=source_path,
            index=parent_index_by_anchor[parent_anchor],
            headings=parent_headings,
            lines=pending_parents[parent_anchor],
            unit_type="parent",
        )

    for headings, lines in leaves:
        parent_ref = None
        if len(headings) >= parent_depth:
            parent_anchor = anchor_for(headings[:parent_depth])
            parent_ref = chunk_ref(source_path, parent_anchor)
        yield emit(
            source_path=source_path,
            index=next_index,
            headings=headings,
            lines=lines,
            unit_type="chunk",
            parent_ref=parent_ref,
        )
        next_index += 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument(
        "--unit",
        choices=("chunk", "parent_child"),
        default="chunk",
        help="Emit single chunks or parent+child pairs (matches manifest preserve_parents).",
    )
    parser.add_argument(
        "--parent-depth",
        type=int,
        default=2,
        help="Heading depth at which parents are anchored (1 = H1, 2 = H2, ...).",
    )
    args = parser.parse_args()

    for path in args.paths:
        for record in chunk_file(path, args.max_tokens, args.unit, args.parent_depth):
            print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
