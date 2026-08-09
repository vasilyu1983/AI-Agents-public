#!/usr/bin/env python3

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


URL_RE = re.compile(r"https?://[^\s)>\"']+")


@dataclass(frozen=True)
class LinkResult:
    source_file: Path
    url: str
    ok: bool
    detail: str


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


def _collect_urls(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return sorted(set(URL_RE.findall(text)))


def _is_allowed_host(hostname: str | None, allow_hosts: set[str]) -> bool:
    if not hostname:
        return False
    normalized = hostname.lower()
    if normalized in allow_hosts:
        return True
    return normalized.endswith(".local")


def _probe_url(url: str, timeout: float, retries: int) -> tuple[bool, str]:
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "qa-docs-coverage/1.0"},
    )

    last_error = "unknown error"
    for attempt in range(1, retries + 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if 200 <= status < 400:
                    return True, f"HTTP {status}"
                last_error = f"HTTP {status}"
        except urllib.error.HTTPError as exc:
            if exc.code in {403, 405}:
                try:
                    get_req = urllib.request.Request(
                        url,
                        method="GET",
                        headers={"User-Agent": "qa-docs-coverage/1.0"},
                    )
                    with urllib.request.urlopen(get_req, timeout=timeout) as response:
                        status = getattr(response, "status", 200)
                        if 200 <= status < 400:
                            return True, f"HTTP {status} via GET fallback"
                        last_error = f"HTTP {status} via GET fallback"
                except Exception as get_exc:  # noqa: BLE001
                    last_error = f"{type(get_exc).__name__}: {get_exc}"
            else:
                last_error = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"

        if attempt <= retries + 1:
            time.sleep(min(2.0, 0.25 * attempt))

    return False, last_error


def _check_url(
    source_file: Path,
    url: str,
    timeout: float,
    retries: int,
    allow_hosts: set[str],
    skip_hosts: set[str],
) -> LinkResult:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()

    if host in skip_hosts:
        return LinkResult(source_file=source_file, url=url, ok=True, detail="skipped host")
    if _is_allowed_host(host, allow_hosts):
        return LinkResult(source_file=source_file, url=url, ok=True, detail="allowed host")

    ok, detail = _probe_url(url, timeout=timeout, retries=retries)
    return LinkResult(source_file=source_file, url=url, ok=ok, detail=detail)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check external HTTP/HTTPS links in Markdown files."
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument(
        "--allow-host",
        action="append",
        default=[],
        help="Treat the hostname as allowed without probing (repeatable).",
    )
    parser.add_argument(
        "--skip-host",
        action="append",
        default=[],
        help="Skip checks for the hostname but keep it reported as skipped (repeatable).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root path not found: {root}", file=sys.stderr)
        return 2

    markdown_files = _iter_markdown_files(root)
    allow_hosts = {host.lower() for host in args.allow_host}
    skip_hosts = {host.lower() for host in args.skip_host}

    work: list[tuple[Path, str]] = []
    for path in markdown_files:
        for url in _collect_urls(path):
            work.append((path, url))

    if not work:
        print(f"OK: {len(markdown_files)} markdown files; no external URLs found")
        return 0

    results: list[LinkResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [
            pool.submit(
                _check_url,
                source_file,
                url,
                args.timeout,
                args.retries,
                allow_hosts,
                skip_hosts,
            )
            for source_file, url in work
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    failures = sorted(
        (result for result in results if not result.ok),
        key=lambda item: (str(item.source_file), item.url),
    )
    if failures:
        print("Broken external links:")
        for item in failures:
            print(f"- {item.source_file}: {item.url} [{item.detail}]")
        return 1

    print(
        f"OK: {len(markdown_files)} markdown files; checked {len(work)} external URLs with no failures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
