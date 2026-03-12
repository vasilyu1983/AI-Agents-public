#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
GLOB_CHARS_RE = re.compile(r"[*?\[]")


@dataclass(frozen=True)
class DocMeta:
    path: Path
    priority: str | None
    owner: str | None
    last_verified: dt.date | None
    review_cadence: str | None
    code_paths: list[str]


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


def _parse_frontmatter(doc_text: str) -> dict[str, object]:
    match = FRONTMATTER_RE.match(doc_text)
    if not match:
        return {}

    raw = match.group(1)
    meta: dict[str, object] = {}
    current_list_key: str | None = None

    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        if line.startswith("- ") and current_list_key:
            meta.setdefault(current_list_key, [])
            if isinstance(meta[current_list_key], list):
                meta[current_list_key].append(line[2:].strip())
            continue

        current_list_key = None
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue

        if value == "":
            current_list_key = key
            meta[key] = []
            continue

        meta[key] = value

    return meta


def _parse_date(value: str) -> dt.date | None:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = dt.datetime.strptime(value, fmt)
            return parsed.date()
        except ValueError:
            continue
    return None


def _git_last_commit_epoch(repo_root: Path, paths: list[Path]) -> int | None:
    if not paths:
        return None
    rel_paths = [str(p.relative_to(repo_root)) for p in paths if p.exists()]
    if not rel_paths:
        return None
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%ct", "--", *rel_paths],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return int(output) if output else None
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def _expand_code_paths(repo_root: Path, patterns: list[str]) -> list[Path]:
    results: list[Path] = []
    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue

        if pattern.endswith("/**"):
            base = pattern[: -len("/**")]
            candidate = (repo_root / base).resolve()
            if candidate.exists():
                results.append(candidate)
            continue

        if GLOB_CHARS_RE.search(pattern):
            matches = list(repo_root.glob(pattern))
            results.extend(matches)
            continue

        results.append((repo_root / pattern).resolve())
    return results


def _read_doc_meta(path: Path) -> DocMeta:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    frontmatter = _parse_frontmatter(text)

    last_verified_raw = frontmatter.get("last_verified")
    last_verified = (
        _parse_date(str(last_verified_raw)) if isinstance(last_verified_raw, str) else None
    )

    code_paths_raw = frontmatter.get("code_paths")
    code_paths: list[str] = []
    if isinstance(code_paths_raw, list):
        code_paths = [str(v) for v in code_paths_raw if str(v).strip()]

    priority = frontmatter.get("priority")
    owner = frontmatter.get("owner")
    review_cadence = frontmatter.get("review_cadence")

    return DocMeta(
        path=path,
        priority=str(priority) if isinstance(priority, str) and priority.strip() else None,
        owner=str(owner) if isinstance(owner, str) and owner.strip() else None,
        last_verified=last_verified,
        review_cadence=str(review_cadence)
        if isinstance(review_cadence, str) and review_cadence.strip()
        else None,
        code_paths=code_paths,
    )


def _normalize_priority(priority: str | None) -> str:
    if not priority:
        return "P3"
    p = priority.strip().upper()
    if p in {"P1", "P2", "P3"}:
        return p
    if p in {"1", "PRIORITY1", "PRIORITY_1", "PRIORITY-1"}:
        return "P1"
    if p in {"2", "PRIORITY2", "PRIORITY_2", "PRIORITY-2"}:
        return "P2"
    if p in {"3", "PRIORITY3", "PRIORITY_3", "PRIORITY-3"}:
        return "P3"
    return "P3"


def _format_date(date_value: dt.date | None) -> str:
    return date_value.isoformat() if date_value else "N/A"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a documentation freshness report from Markdown frontmatter."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Git repository root (default: current directory).",
    )
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Directory containing documentation to scan (default: docs).",
    )
    parser.add_argument("--p1-days", type=int, default=30)
    parser.add_argument("--p2-days", type=int, default=60)
    parser.add_argument("--p3-days", type=int, default=90)
    parser.add_argument("--out", help="Write report to a file (Markdown).")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    docs_root = (repo_root / args.docs_root).resolve()
    if not docs_root.exists():
        print(f"ERROR: docs root not found: {docs_root}", file=sys.stderr)
        return 2

    thresholds = {"P1": args.p1_days, "P2": args.p2_days, "P3": args.p3_days}
    today = dt.date.today()

    entries: list[DocMeta] = [_read_doc_meta(p) for p in sorted(_iter_markdown_files(docs_root))]

    rows: list[str] = []
    rows.append(f"# Documentation Freshness Report\n\nGenerated: {today.isoformat()}\n")
    rows.append(
        "| Document | Priority | Owner | Last verified | Age (days) | Threshold | Drift (days) | Status |"
    )
    rows.append("|---|---|---|---|---:|---:|---:|---|")

    stale_count = 0
    no_meta_count = 0
    for entry in entries:
        priority = _normalize_priority(entry.priority)
        threshold = thresholds[priority]

        age_days: int | None = None
        if entry.last_verified:
            age_days = (today - entry.last_verified).days

        code_drift_days: int | None = None
        if entry.code_paths:
            code_path_candidates = _expand_code_paths(repo_root, entry.code_paths)
            code_last = _git_last_commit_epoch(repo_root, code_path_candidates)
            doc_last = _git_last_commit_epoch(repo_root, [entry.path])
            if code_last and doc_last and code_last > doc_last:
                code_drift_days = (code_last - doc_last) // 86400
            else:
                code_drift_days = 0

        if age_days is None:
            status = "NO_METADATA"
            no_meta_count += 1
        elif age_days > threshold:
            status = "STALE"
            stale_count += 1
        elif age_days > max(0, threshold - 7):
            status = "WARNING"
        else:
            status = "OK"

        rows.append(
            "| "
            + " | ".join(
                [
                    str(entry.path.relative_to(repo_root)),
                    priority,
                    entry.owner or "N/A",
                    _format_date(entry.last_verified),
                    str(age_days) if age_days is not None else "N/A",
                    str(threshold),
                    str(code_drift_days) if code_drift_days is not None else "N/A",
                    status,
                ]
            )
            + " |"
        )

    rows.append("")
    rows.append(f"Summary: {len(entries)} docs scanned; {stale_count} stale; {no_meta_count} missing metadata.\n")

    report = "\n".join(rows)
    if args.out:
        out_path = (repo_root / args.out).resolve()
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote report: {out_path}")
    else:
        print(report)

    return 1 if stale_count else 0


if __name__ == "__main__":
    raise SystemExit(main())

