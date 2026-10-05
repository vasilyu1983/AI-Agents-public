#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


REQUIRED_ITEM_KEYS = {
    "name",
    "url",
    "type",
    "relevance",
    "update_frequency",
    "access",
    "add_as_web_search",
}

REQUIRED_METADATA_KEYS = {"skill", "last_updated", "total_sources", "description", "version"}

# Fields that should not coexist in metadata
REDUNDANT_PAIRS = [("updated", "last_updated")]


def load_sources(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_shape(data: object) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["top-level document must be an object"], []
    metadata = data.get("metadata")
    categories = data.get("categories")

    if not isinstance(metadata, dict):
        return ["metadata must be an object"], []
    if not isinstance(categories, dict):
        return ["categories must be an object"], []

    for key in REQUIRED_METADATA_KEYS:
        if key not in metadata:
            errors.append(f"metadata missing key: {key}")

    # Check for redundant fields
    for field_a, field_b in REDUNDANT_PAIRS:
        if field_a in metadata and field_b in metadata:
            warnings.append(
                f"metadata has both '{field_a}' and '{field_b}' — "
                f"only '{field_b}' is required. Consider removing '{field_a}'."
            )

    # Check URLs are HTTPS
    seen_urls: set[str] = set()
    item_count = 0
    for category, items in categories.items():
        if not isinstance(items, list):
            errors.append(f"category '{category}' must be a list")
            continue
        for index, item in enumerate(items, start=1):
            item_count += 1
            if not isinstance(item, dict):
                errors.append(f"{category}[{index}] must be an object")
                continue
            missing = REQUIRED_ITEM_KEYS - set(item)
            if missing:
                errors.append(
                    f"{category}[{index}] missing keys: {', '.join(sorted(missing))}"
                )
            if not isinstance(item.get("add_as_web_search"), bool):
                errors.append(f"{category}[{index}] add_as_web_search must be boolean")
            url = item.get("url")
            if isinstance(url, str):
                if not url.startswith("https://"):
                    errors.append(f"{category}[{index}] url must use HTTPS: {url}")
                if url in seen_urls:
                    errors.append(f"duplicate url: {url}")
                seen_urls.add(url)
            else:
                errors.append(f"{category}[{index}] url must be string")

    if item_count == 0:
        errors.append("no sources listed: an empty catalog is not a valid catalog")

    expected_total = metadata.get("total_sources")
    if isinstance(expected_total, int) and expected_total != item_count:
        errors.append(
            f"metadata.total_sources={expected_total} does not match actual count={item_count}"
        )

    return errors, warnings


def check_urls(data: dict, timeout_seconds: float) -> list[str]:
    errors: list[str] = []
    for category, items in data["categories"].items():
        for item in items:
            url = item["url"]
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ai-context-layer-source-check/1.0"},
                method="HEAD",
            )
            try:
                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                    if response.status >= 400:
                        errors.append(f"{category}: {url} returned HTTP {response.status}")
            except urllib.error.HTTPError as exc:
                errors.append(f"{category}: {url} returned HTTP {exc.code}")
            except urllib.error.URLError as exc:
                errors.append(f"{category}: {url} failed ({exc.reason})")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate ai-context-layer sources.json structure and optionally test URLs.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "data" / "sources.json"),
        help="Path to sources.json (default: the skill's own data/sources.json)",
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Issue HEAD requests for each URL.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=8.0,
        help="Timeout for URL checks (default: 8s).",
    )
    args = parser.parse_args(argv)

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        data = load_sources(path)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate_shape(data)

    if args.check_urls and not errors:
        errors.extend(check_urls(data, timeout_seconds=args.timeout_seconds))

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    total_sources = data["metadata"]["total_sources"]
    print(f"OK: {path.name} validated ({total_sources} sources)")
    if args.check_urls:
        print("OK: URL checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
