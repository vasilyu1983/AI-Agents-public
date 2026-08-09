#!/usr/bin/env python3
"""Validate the product-help-center source catalog.

Checks:
- required metadata fields
- metadata.skill alignment
- duplicate URLs
- stale year labels in category names and resource names
- required per-entry fields
- optional network reachability when --check-urls is enabled
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


REQUIRED_METADATA_FIELDS = {
    "title",
    "description",
    "last_updated",
    "last_verified",
    "version",
    "skill",
}

REQUIRED_ENTRY_FIELDS = {
    "name",
    "url",
    "description",
    "source_type",
    "authority",
    "volatility",
    "status",
    "add_as_web_search",
}

STALE_YEAR_TOKENS = ("2023", "2024", "2025")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def validate_metadata(data: dict, errors: list[str]) -> None:
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
        return

    missing = sorted(REQUIRED_METADATA_FIELDS - metadata.keys())
    if missing:
        errors.append(f"metadata missing fields: {', '.join(missing)}")

    if metadata.get("skill") != "product-help-center":
        errors.append("metadata.skill must equal 'product-help-center'")


def validate_entries(data: dict, errors: list[str], warnings: list[str]) -> None:
    seen_urls: dict[str, str] = {}

    for category, items in data.items():
        if category == "metadata":
            continue

        if any(token in category for token in STALE_YEAR_TOKENS):
            warnings.append(f"category name includes stale year token: {category}")

        if not isinstance(items, list):
            errors.append(f"{category} must be a list")
            continue

        for index, entry in enumerate(items, start=1):
            label = f"{category}[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{label} must be an object")
                continue

            missing = sorted(REQUIRED_ENTRY_FIELDS - entry.keys())
            if missing:
                errors.append(f"{label} missing fields: {', '.join(missing)}")
                continue

            url = entry["url"]
            if url in seen_urls:
                warnings.append(f"duplicate url: {url} used by {seen_urls[url]} and {label}")
            else:
                seen_urls[url] = label

            name = entry["name"]
            if any(token in name for token in STALE_YEAR_TOKENS):
                warnings.append(f"{label} name includes stale year token: {name}")

            if not isinstance(entry["add_as_web_search"], bool):
                errors.append(f"{label} add_as_web_search must be true or false")


def check_urls(data: dict, warnings: list[str]) -> None:
    headers = {"User-Agent": "Mozilla/5.0"}
    for category, items in data.items():
        if category == "metadata":
            continue
        for index, entry in enumerate(items, start=1):
            url = entry["url"]
            label = f"{category}[{index}]"
            request = urllib.request.Request(url, headers=headers, method="HEAD")
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    status = response.status
                if status >= 400:
                    warnings.append(f"{label} returned status {status}: {url}")
            except urllib.error.HTTPError as exc:
                warnings.append(f"{label} returned HTTP {exc.code}: {url}")
            except urllib.error.URLError as exc:
                warnings.append(f"{label} unreachable: {url} ({exc.reason})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default="frameworks/shared-skills/skills/product-help-center/data/sources.json",
        help="Path to the sources.json file.",
    )
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="Run network reachability checks for URLs.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Missing file: {path}", file=sys.stderr)
        return 1

    data = load_json(path)
    errors: list[str] = []
    warnings: list[str] = []

    validate_metadata(data, errors)
    validate_entries(data, errors, warnings)

    if args.check_urls:
        check_urls(data, warnings)

    for warning in warnings:
        print(f"WARN: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: sources catalog validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
