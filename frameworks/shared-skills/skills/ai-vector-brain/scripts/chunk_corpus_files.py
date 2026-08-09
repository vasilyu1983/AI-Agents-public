#!/usr/bin/env python3
"""Chunk mixed repo/context corpus files with stable path and line anchors.

Markdown uses heading-aware parent-child chunks by delegating to
`chunk_markdown.py`. Structured files, SQL, and source files use line-bounded
chunks so repo/context vector brains can index generated profiles, manifests,
schema files, and selected source without pretending everything is Markdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from chunk_markdown import chunk_file as chunk_markdown_file

DEFAULT_SUFFIXES = {
    ".md",
    ".mdx",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".sql",
}
SKIP_PARTS = {".git", "node_modules", ".venv", "dist", "build", ".archive"}
MARKDOWN_SUFFIXES = {".md", ".mdx"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def token_estimate(text: str) -> int:
    return max(1, len(text.split()))


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in MARKDOWN_SUFFIXES:
        return "markdown"
    if suffix in {".json", ".yaml", ".yml"}:
        return "structured"
    if suffix == ".sql":
        return "sql"
    if suffix in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return "code"
    return "text"


def line_anchor(start: int, end: int) -> str:
    return f"L{start}-L{end}"


def emit_line_chunk(
    *,
    source_path: str,
    index: int,
    start: int,
    end: int,
    content: str,
    doc_type: str,
) -> dict:
    anchor = line_anchor(start, end)
    return {
        "source_path": source_path,
        "chunk_index": index,
        "content": content,
        "section_path": f"{source_path}:{anchor}",
        "anchor": anchor,
        "citation_anchor": f"{source_path}#{anchor}",
        "chunk_ref": f"{source_path}#{anchor}",
        "parent_chunk_ref": None,
        "unit_type": "chunk",
        "token_count": token_estimate(content),
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "metadata": {
            "doc_type": doc_type,
            "line_start": start,
            "line_end": end,
            "chunking": "line_bounded",
        },
    }


def chunk_line_bounded(path: Path, source_path: str, max_tokens: int):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    current: list[str] = []
    start_line = 1
    index = 0
    doc_type = classify(path)

    for offset, line in enumerate(lines, start=1):
        if not current:
            start_line = offset
        current.append(line)
        if token_estimate("\n".join(current)) >= max_tokens:
            content = "\n".join(current).strip()
            if content:
                yield emit_line_chunk(
                    source_path=source_path,
                    index=index,
                    start=start_line,
                    end=offset,
                    content=content,
                    doc_type=doc_type,
                )
                index += 1
            current = []

    content = "\n".join(current).strip()
    if content:
        yield emit_line_chunk(
            source_path=source_path,
            index=index,
            start=start_line,
            end=len(lines),
            content=content,
            doc_type=doc_type,
        )


def iter_files(root: Path, suffixes: set[str]):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() in suffixes:
            yield path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--suffix", action="append", dest="suffixes")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument(
        "--unit",
        choices=("chunk", "parent_child"),
        default="parent_child",
        help="Markdown chunk unit. Non-Markdown files always use line-bounded chunks.",
    )
    parser.add_argument("--parent-depth", type=int, default=2)
    args = parser.parse_args()

    root = args.root.resolve()
    suffixes = set(args.suffixes or DEFAULT_SUFFIXES)
    for path in iter_files(root, suffixes):
        source_path = path.relative_to(root).as_posix()
        if path.suffix.lower() in MARKDOWN_SUFFIXES:
            for record in chunk_markdown_file(path, args.max_tokens, args.unit, args.parent_depth):
                anchor = record.get("citation_anchor") or "root"
                record["source_path"] = source_path
                record["citation_anchor"] = f"{source_path}#{anchor}"
                record["chunk_ref"] = f"{source_path}#{anchor}"
                if record.get("parent_chunk_ref"):
                    _, _, parent_anchor = record["parent_chunk_ref"].partition("#")
                    record["parent_chunk_ref"] = f"{source_path}#{parent_anchor}"
                record.setdefault("metadata", {})["doc_type"] = "markdown"
                print(json.dumps(record, ensure_ascii=False))
            continue

        for record in chunk_line_bounded(path, source_path, args.max_tokens):
            print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
