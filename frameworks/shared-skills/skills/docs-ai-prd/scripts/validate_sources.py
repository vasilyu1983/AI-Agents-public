#!/usr/bin/env python3
"""Validate URL references used by the docs-ai-prd skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Iterable

URL_RE = re.compile(r"https?://[^\s)>\"']+")
MARKDOWN_GLOBS = ("**/*.md", "**/*.json")
DEFAULT_TIMEOUT = 10.0
ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan markdown/json files for URLs and optionally check HTTP status."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Skill root to scan (defaults to docs-ai-prd root).",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only inventory URLs without making network requests.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of text.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Network timeout in seconds for live checks.",
    )
    return parser.parse_args()


def iter_files(root: Path) -> Iterable[Path]:
    for pattern in MARKDOWN_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                yield path


def extract_urls(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return URL_RE.findall(text)


def inventory(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in iter_files(root):
        rel = path.relative_to(root).as_posix()
        for url in extract_urls(path):
            rows.append({"path": rel, "url": url})
    return rows


def should_skip_live_check(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    placeholder_hosts = {
        "localhost",
        "test",
        "api.example.com",
        "api-staging.example.com",
        "example.com",
        "example.org",
        "example.net",
    }
    if host in placeholder_hosts:
        return True
    if host.endswith(".local"):
        return True
    if "." not in host:
        return True
    return False


def fetch(url: str, timeout: float) -> dict[str, str | int]:
    headers = {"User-Agent": "docs-ai-prd-source-validator/1.0"}
    methods = ("HEAD", "GET")

    last_error = None
    for method in methods:
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", response.getcode())
                return {
                    "status_code": int(status),
                    "final_url": response.geturl(),
                    "result": "redirected" if response.geturl() != url else "live",
                }
        except urllib.error.HTTPError as exc:
            last_error = exc
            if method == "HEAD" and exc.code in {400, 403, 405, 501}:
                continue
            return {
                "status_code": int(exc.code),
                "final_url": exc.geturl() or url,
                "result": "error",
                "error": str(exc),
            }
        except urllib.error.URLError as exc:
            last_error = exc
            if method == "HEAD":
                continue
            return {
                "status_code": 0,
                "final_url": url,
                "result": "error",
                "error": str(exc.reason),
            }

    return {
        "status_code": 0,
        "final_url": url,
        "result": "error",
        "error": str(last_error) if last_error else "unknown error",
    }


def check_rows(rows: list[dict[str, str]], timeout: float) -> list[dict[str, str | int]]:
    results: list[dict[str, str | int]] = []
    cache: dict[str, dict[str, str | int]] = {}
    for row in rows:
        if row["url"] not in cache:
            if should_skip_live_check(row["url"]):
                cache[row["url"]] = {
                    "status_code": 0,
                    "final_url": row["url"],
                    "result": "skipped",
                }
            else:
                cache[row["url"]] = fetch(row["url"], timeout)
        status = cache[row["url"]]
        results.append({**row, **status})
    return results


def emit_text(rows: list[dict[str, str | int]], scan_only: bool) -> None:
    unique_urls = {row["url"] for row in rows}
    print(f"Scanned {len(rows)} URL references across {len(unique_urls)} unique URLs.")
    if scan_only:
        for row in rows:
            print(f"{row['path']}: {row['url']}")
        return

    counts = Counter(str(row["result"]) for row in rows)
    print(
        "Results: "
        + ", ".join(
            f"{name}={counts.get(name, 0)}" for name in ("live", "redirected", "skipped", "error")
        )
    )
    for row in rows:
        final_url = row.get("final_url", row["url"])
        status = row.get("status_code", "")
        extra = ""
        if row.get("result") == "redirected":
            extra = f" -> {final_url}"
        if row.get("result") == "error" and row.get("error"):
            extra = f" ({row['error']})"
        print(f"[{row['result']}] {status} {row['path']}: {row['url']}{extra}")


def main() -> int:
    args = parse_args()
    rows = inventory(args.root)
    if args.scan_only:
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            emit_text(rows, scan_only=True)
        return 0

    checked = check_rows(rows, args.timeout)
    if args.json:
        print(json.dumps(checked, indent=2))
    else:
        emit_text(checked, scan_only=False)

    return 1 if any(row["result"] == "error" for row in checked) else 0


if __name__ == "__main__":
    sys.exit(main())
