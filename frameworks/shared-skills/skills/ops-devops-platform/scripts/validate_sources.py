#!/usr/bin/env python3
"""Validate the ops-devops-platform source inventory."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


VALID_KINDS = {
    "docs",
    "release",
    "changelog",
    "reference",
    "guide",
    "spec",
}

RELEASE_OPTIONAL_CATEGORIES = {
    "aiops",
    "cloud_architecture_frameworks",
    "sre_and_incidents",
}

# Keep this aligned with the explicit product lists in SKILL.md.
REQUIRED_PRODUCTS = [
    "CloudFormation",
    "Bicep",
    "AWS CDK",
    "Jenkins",
    "Tekton",
    "Kafka",
    "Confluent",
    "Strimzi",
    "Datadog",
    "Jaeger",
    "Falco",
    "Gateway API",
    "Port",
    "Kratix",
    "Codefresh",
    "Dagger",
    "Terragrunt",
    "k9s",
    "stern",
]


def load_sources(path: Path) -> dict:
    return json.loads(path.read_text())


def iter_entries(data: dict):
    for category, value in data.items():
        if category == "metadata" or not isinstance(value, list):
            continue
        for entry in value:
            yield category, entry


def url_ok(url: str, timeout: float = 15.0) -> tuple[bool, str]:
    headers = {"User-Agent": "Mozilla/5.0"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return True, str(response.status)
        except urllib.error.HTTPError as exc:
            if exc.code == 405 and method == "HEAD":
                continue
            return False, f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001
            if method == "HEAD":
                continue
            return False, exc.__class__.__name__
    return False, "Unknown error"


def validate_schema(data: dict) -> list[str]:
    errors: list[str] = []
    for category, entry in iter_entries(data):
        for key in ("name", "url", "description", "kind"):
            if key not in entry:
                errors.append(f"{category}: missing {key} in {entry!r}")
        kind = entry.get("kind")
        if kind and kind not in VALID_KINDS:
            errors.append(f"{category}: invalid kind={kind!r} for {entry.get('name', '<unnamed>')}")
    return errors


def validate_coverage(data: dict) -> tuple[list[str], list[str]]:
    names = [entry["name"] for _, entry in iter_entries(data)]
    haystack = " ".join(names).lower()
    missing = [product for product in REQUIRED_PRODUCTS if product.lower() not in haystack]

    warnings: list[str] = []
    categories: dict[str, set[str]] = {}
    for category, entry in iter_entries(data):
        categories.setdefault(category, set()).add(entry["kind"])
    for category, kinds in sorted(categories.items()):
        if category in RELEASE_OPTIONAL_CATEGORIES:
            continue
        if "docs" in kinds and not ({"release", "changelog"} & kinds):
            warnings.append(f"{category}: docs entries present but no release/changelog source")
    return missing, warnings


def validate_urls(data: dict, skip_network: bool) -> tuple[list[str], list[str]]:
    if skip_network:
        return [], []
    errors: list[str] = []
    warnings: list[str] = []
    for category, entry in iter_entries(data):
        ok, detail = url_ok(entry["url"])
        if not ok:
            message = f"{category}: {entry['name']} -> {detail} ({entry['url']})"
            if entry.get("optional"):
                warnings.append(message)
            else:
                errors.append(message)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip outbound URL checks and validate only JSON structure/coverage.",
    )
    parser.add_argument(
        "--path",
        default=Path(__file__).resolve().parents[1] / "data" / "sources.json",
        type=Path,
        help="Path to sources.json",
    )
    args = parser.parse_args()

    data = load_sources(args.path)
    errors = validate_schema(data)
    missing, warnings = validate_coverage(data)
    if missing:
        errors.extend(f"coverage: missing product source for {product}" for product in missing)
    url_errors, url_warnings = validate_urls(data, skip_network=args.skip_network)
    warnings.extend(url_warnings)
    errors.extend(url_errors)

    for warning in warnings:
        print(f"WARN\t{warning}")

    if errors:
        for error in errors:
            print(f"ERR\t{error}")
        return 1

    print("OK\tSource inventory validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
