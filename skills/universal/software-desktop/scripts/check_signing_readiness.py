#!/usr/bin/env python3
"""
check_signing_readiness.py — Validate a signing-config.json for desktop distribution readiness.

Exits 0 if the configuration passes all checks.
Exits 1 if any required field is missing or invalid.
This is static configuration validation; it never reads keys or verifies artifacts.
Windows signing_mode: certificate (thumbprint + signing tool), store (MSIX),
or artifact (account_name + certificate_profile + endpoint).

Usage:
    python3 check_signing_readiness.py signing-config.json [--strict]
    python3 check_signing_readiness.py --help

Expected signing-config.json shape:
    {
        "platforms": ["macos", "windows", "linux"],
        "macos": {
            "cert_path": "/path/to/certificate.p12",
            "notarization_profile": "MY_PROFILE",
            "entitlements_file": "entitlements.plist",
            "bundle_id": "com.example.myapp"
        },
        "windows": {
            "signing_mode": "certificate",
            "cert_thumbprint": "ABCDEF1234567890",
            "sign_tool_path": "/path/to/signtool.exe"
        },
        "linux": {
            "gpg_key_id": "YOUR_KEY_ID"
        }
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_PLATFORMS = {"macos", "windows", "linux"}

MACOS_REQUIRED_FIELDS = ["cert_path", "notarization_profile", "entitlements_file", "bundle_id"]
WINDOWS_REQUIRED_FIELDS = ["cert_thumbprint"]
LINUX_REQUIRED_FIELDS = ["gpg_key_id"]


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    message: str


def add_error(issues: list[Issue], message: str) -> None:
    issues.append(Issue(severity="error", message=message))


def add_warning(issues: list[Issue], message: str) -> None:
    issues.append(Issue(severity="warning", message=message))


def validate_macos(config: dict[str, Any], issues: list[Issue], strict: bool) -> None:
    macos = config.get("macos")
    if not isinstance(macos, dict):
        add_error(issues, "macos platform listed but 'macos' section is missing from config")
        return

    for field_name in MACOS_REQUIRED_FIELDS:
        if not isinstance(macos.get(field_name), str) or not macos[field_name].strip():
            add_error(issues, f"macos.{field_name} is required but missing or empty")

    cert_path = macos.get("cert_path", "")
    if isinstance(cert_path, str) and cert_path and strict and not Path(cert_path).is_file():
        add_error(issues, "macos.cert_path must be an existing file under --strict")

    entitlements = macos.get("entitlements_file", "")
    if isinstance(entitlements, str) and entitlements and strict and not Path(entitlements).is_file():
        add_error(issues, "macos.entitlements_file must be an existing file under --strict")

    bundle_id = macos.get("bundle_id", "")
    if isinstance(bundle_id, str) and bundle_id and not _looks_like_bundle_id(bundle_id):
        add_error(issues, f"macos.bundle_id '{bundle_id}' does not look like a reverse-DNS bundle identifier (e.g. com.example.myapp)")

    notarization_profile = macos.get("notarization_profile", "")
    if not notarization_profile:
        add_error(issues, "macos.notarization_profile must not be empty — notarytool requires a named keychain profile")


def validate_windows(config: dict[str, Any], issues: list[Issue], strict: bool) -> None:
    windows = config.get("windows")
    if not isinstance(windows, dict):
        add_error(issues, "windows platform listed but 'windows' section is missing from config")
        return

    mode = windows.get("signing_mode", "certificate")
    if not isinstance(mode, str) or mode not in {"certificate", "store", "artifact"}:
        add_error(issues, "windows.signing_mode must be certificate, store, or artifact")
        return
    if mode == "store":
        required = ["package_type"]
        if windows.get("package_type") != "msix":
            add_error(issues, "windows Store signing applies only to MSIX submissions")
    elif mode == "artifact":
        required = ["account_name", "certificate_profile", "endpoint"]
    else:
        required = WINDOWS_REQUIRED_FIELDS + ["sign_tool_path"]
    for field_name in required:
        value = windows.get(field_name)
        if not isinstance(value, str) or not value.strip():
            add_error(issues, f"windows.{field_name} is required and must be a non-empty string")
    if mode == "certificate" and strict:
        tool = windows.get("sign_tool_path")
        if isinstance(tool, str) and tool and not Path(tool).is_file():
            add_error(issues, "windows.sign_tool_path must be an existing file under --strict")
    # A thumbprint selects the hardware-backed certificate from the Windows store;
    # config schema validation does not establish key custody or signing success.


def validate_linux(config: dict[str, Any], issues: list[Issue], strict: bool) -> None:
    linux = config.get("linux")
    if not isinstance(linux, dict):
        add_error(issues, "linux platform listed but 'linux' section is missing from config")
        return

    for field_name in LINUX_REQUIRED_FIELDS:
        if not isinstance(linux.get(field_name), str) or not linux[field_name].strip():
            add_error(issues, f"linux.{field_name} is required but missing or empty")


def validate_platforms(config: dict[str, Any], issues: list[Issue]) -> list[str]:
    platforms = config.get("platforms")
    if not platforms:
        add_error(issues, "'platforms' key is required and must be a non-empty list")
        return []

    if not isinstance(platforms, list):
        add_error(issues, "'platforms' must be a JSON array of strings")
        return []

    valid = []
    for p in platforms:
        if not isinstance(p, str) or p not in SUPPORTED_PLATFORMS:
            add_error(issues, f"unknown platform '{p}'; supported values are: {', '.join(sorted(SUPPORTED_PLATFORMS))}")
        else:
            valid.append(p)

    if not valid:
        add_error(issues, "no valid platforms found in 'platforms' list")

    return valid


def _looks_like_bundle_id(value: str) -> bool:
    parts = value.split(".")
    return len(parts) >= 2 and all(part.replace("-", "").replace("_", "").isalnum() for part in parts)


def load_config(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        print(f"error: config file not found: {path}", file=sys.stderr)
        return None

    try:
        with path.open(encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                print("error: signing config must be a JSON object", file=sys.stderr)
                return None
            return config
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        return None


def print_issues(issues: list[Issue]) -> None:
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    for issue in errors:
        print(f"  ERROR   {issue.message}")
    for issue in warnings:
        print(f"  WARNING {issue.message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate static signing configuration; this does not verify signed artifacts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "config",
        nargs="?",
        default="signing-config.json",
        help="Path to signing-config.json (default: signing-config.json in current directory)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require referenced certificate, entitlements, and signing-tool files on this filesystem",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    if config is None:
        return 1

    issues: list[Issue] = []

    valid_platforms = validate_platforms(config, issues)

    for platform in valid_platforms:
        if platform == "macos":
            validate_macos(config, issues, strict=args.strict)
        elif platform == "windows":
            validate_windows(config, issues, strict=args.strict)
        elif platform == "linux":
            validate_linux(config, issues, strict=args.strict)

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if issues:
        print(f"\nSigning config validation: {config_path}")
        print_issues(issues)
        print()

    if errors:
        print(f"FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"PASSED — {config_path} ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
