#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
GLOB_CHARS_RE = re.compile(r"[*?\[]")
UTC = dt.timezone.utc


@dataclass(frozen=True)
class DocMeta:
    path: Path
    priority: str | None
    owner: str | None
    last_verified: dt.date | None
    review_cadence: str | None
    code_paths: list[str]
    metadata_errors: list[str]


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


def _parse_frontmatter(doc_text: str) -> tuple[dict[str, object], list[str]]:
    match = FRONTMATTER_RE.match(doc_text)
    if not match:
        return {}, []

    if yaml is None:
        return {}, ["PyYAML is required to parse frontmatter; install `pyyaml`"]

    try:
        data = yaml.safe_load(match.group(1)) or {}
    except Exception as exc:  # noqa: BLE001
        return {}, [f"invalid YAML frontmatter: {exc}"]

    if not isinstance(data, dict):
        return {}, ["frontmatter must parse to a mapping/object"]
    return data, []


def _parse_date(value: object) -> dt.date | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.astimezone(UTC).date()
    if isinstance(value, dt.date):
        return value

    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = dt.datetime.strptime(raw, fmt)
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
            candidate = (repo_root / pattern[: -len("/**")]).resolve()
            if candidate.exists():
                results.append(candidate)
            continue

        if GLOB_CHARS_RE.search(pattern):
            results.extend(repo_root.glob(pattern))
            continue

        results.append((repo_root / pattern).resolve())
    return results


def _as_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _read_doc_meta(path: Path) -> DocMeta:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    frontmatter, parse_errors = _parse_frontmatter(text)
    metadata_errors = list(parse_errors)

    priority_value = frontmatter.get("priority")
    owner_value = frontmatter.get("owner")
    review_cadence_value = frontmatter.get("review_cadence")
    last_verified = _parse_date(frontmatter.get("last_verified"))
    code_paths = _as_string_list(frontmatter.get("code_paths"))

    if "last_verified" in frontmatter and last_verified is None:
        metadata_errors.append("invalid last_verified date format")
    if "code_paths" in frontmatter and not isinstance(frontmatter.get("code_paths"), list):
        metadata_errors.append("code_paths must be a list")

    priority = str(priority_value).strip() if priority_value else None
    owner = str(owner_value).strip() if owner_value else None
    review_cadence = str(review_cadence_value).strip() if review_cadence_value else None

    return DocMeta(
        path=path,
        priority=priority or None,
        owner=owner or None,
        last_verified=last_verified,
        review_cadence=review_cadence or None,
        code_paths=code_paths,
        metadata_errors=metadata_errors,
    )


def _normalize_priority(priority: str | None) -> str:
    if not priority:
        return "P3"
    normalized = priority.strip().upper()
    if normalized in {"P1", "P2", "P3"}:
        return normalized
    if normalized in {"1", "PRIORITY1", "PRIORITY_1", "PRIORITY-1"}:
        return "P1"
    if normalized in {"2", "PRIORITY2", "PRIORITY_2", "PRIORITY-2"}:
        return "P2"
    if normalized in {"3", "PRIORITY3", "PRIORITY_3", "PRIORITY-3"}:
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
    parser.add_argument(
        "--fail-on-missing-metadata",
        action="store_true",
        help="Exit non-zero if any document is missing or has invalid critical metadata.",
    )
    parser.add_argument("--out", help="Write report to a file (Markdown).")
    parser.add_argument(
        "--json-out",
        help="Write machine-readable results to a JSON file.",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    docs_root = (repo_root / args.docs_root).resolve()
    if not docs_root.exists():
        print(f"ERROR: docs root not found: {docs_root}", file=sys.stderr)
        return 2

    thresholds = {"P1": args.p1_days, "P2": args.p2_days, "P3": args.p3_days}
    today = dt.datetime.now(UTC).date()
    entries = [_read_doc_meta(p) for p in sorted(_iter_markdown_files(docs_root))]

    rows: list[str] = []
    rows.append(f"# Documentation Freshness Report\n\nGenerated (UTC): {today.isoformat()}\n")
    rows.append(
        "| Document | Priority | Owner | Last verified | Age (days) | Threshold | Drift (days) | Status | Notes |"
    )
    rows.append("|---|---|---|---|---:|---:|---:|---|---|")

    stale_count = 0
    metadata_issue_count = 0
    json_rows: list[dict[str, object]] = []

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
            elif code_last and doc_last:
                code_drift_days = 0

        if entry.metadata_errors or age_days is None or not entry.owner:
            status = "METADATA_ISSUE"
            metadata_issue_count += 1
        elif age_days > threshold:
            status = "STALE"
            stale_count += 1
        elif age_days > max(0, threshold - 7):
            status = "WARNING"
        else:
            status = "OK"

        notes: list[str] = []
        if not entry.owner:
            notes.append("missing owner")
        if age_days is None:
            notes.append("missing last_verified")
        notes.extend(entry.metadata_errors)
        note_text = "; ".join(notes) if notes else ""

        rel_path = str(entry.path.relative_to(repo_root))
        rows.append(
            "| "
            + " | ".join(
                [
                    rel_path,
                    priority,
                    entry.owner or "N/A",
                    _format_date(entry.last_verified),
                    str(age_days) if age_days is not None else "N/A",
                    str(threshold),
                    str(code_drift_days) if code_drift_days is not None else "N/A",
                    status,
                    note_text or " ",
                ]
            )
            + " |"
        )

        json_rows.append(
            {
                "document": rel_path,
                "priority": priority,
                "owner": entry.owner,
                "last_verified": _format_date(entry.last_verified),
                "age_days": age_days,
                "threshold_days": threshold,
                "drift_days": code_drift_days,
                "status": status,
                "notes": notes,
            }
        )

    rows.append("")
    rows.append(
        "Summary: "
        f"{len(entries)} docs scanned; "
        f"{stale_count} stale; "
        f"{metadata_issue_count} metadata issues."
    )
    rows.append("")
    rows.append("Statuses:")
    rows.append("- `OK`: within threshold")
    rows.append("- `WARNING`: within 7 days of threshold")
    rows.append("- `STALE`: past threshold")
    rows.append("- `METADATA_ISSUE`: missing or invalid critical metadata")

    report = "\n".join(rows)
    if args.out:
        out_path = (repo_root / args.out).resolve()
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote report: {out_path}")
    else:
        print(report)

    if args.json_out:
        json_path = (repo_root / args.json_out).resolve()
        json_path.write_text(json.dumps(json_rows, indent=2), encoding="utf-8")
        print(f"Wrote JSON: {json_path}")

    if stale_count:
        return 1
    if metadata_issue_count and args.fail_on_missing_metadata:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
