#!/usr/bin/env python3
"""Validate curated URLs for the software-localisation skill."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.json"


def iter_urls(node):
    if isinstance(node, dict):
        if "url" in node and isinstance(node["url"], str):
            yield node.get("name", "<unnamed>"), node["url"]
        for value in node.values():
            yield from iter_urls(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_urls(item)


def main() -> int:
    data = json.loads(SOURCES.read_text())
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
    errors = []
    redirects = []

    for name, url in iter_urls(data):
        request = urllib.request.Request(url, headers={"User-Agent": "codex-url-check/1.0"})
        try:
            with opener.open(request, timeout=15) as response:
                final_url = response.geturl()
                if final_url.rstrip("/") != url.rstrip("/"):
                    redirects.append((name, url, final_url))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            errors.append((name, url, str(exc)))

    if redirects:
        print("Redirects:")
        for name, src, dest in redirects:
            print(f"- {name}: {src} -> {dest}")

    if errors:
        print("Errors:")
        for name, url, exc in errors:
            print(f"- {name}: {url} ({exc})")

    if redirects or errors:
        return 1

    print(f"Validated {sum(1 for _ in iter_urls(data))} source URLs with no redirects or errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
