#!/usr/bin/env python3
"""validate_manifest.py — Static validator for plugin.manifest.json files.

Uses Python standard library only (json, pathlib, sys, re, argparse).
No third-party dependencies required.

Usage:
    python validate_manifest.py path/to/plugin.manifest.json
    python validate_manifest.py .          # scans current dir for manifest files
    python validate_manifest.py --strict   # exit 1 on warnings too

Exit codes:
    0 — all checks passed (or passed with warnings in non-strict mode)
    1 — one or more errors (or warnings in strict mode)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

REQUIRED_TOP_LEVEL = ["id", "name", "version", "description", "runtime", "entry"]
REQUIRED_RUNTIME = ["min_agent_version", "platform"]
REQUIRED_TOOL = ["name", "description", "schema_path", "side_effects", "requires_approval"]
REQUIRED_COMMAND = ["name", "description", "prompt_path"]

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,79}$")
TOOL_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z_]+\}\}")

VALID_SIDE_EFFECTS = {
    "file_read", "file_write", "file_delete",
    "process_exec", "network_outbound", "network_inbound",
    "env_read", "env_write",
}

VALID_PLATFORMS = {"claude-code", "codex", "agent-sdk", "goose"}

# ── Result collectors ─────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(f"ERROR: {msg}")

    def warn(self, msg):
        self.warnings.append(f"WARN:  {msg}")

    @property
    def passed(self):
        return len(self.errors) == 0

    def print_report(self, path):
        label = str(path)
        all_messages = self.errors + self.warnings
        if not all_messages:
            print(f"  [PASS] {label} — no issues found")
        else:
            for msg in all_messages:
                print(f"  {msg}  ({label})")

# ── Field validators ──────────────────────────────────────────────────────────

def _check_placeholders(value, field, result):
    """Warn when a template placeholder like {{TOOL_NAME}} was not replaced."""
    if isinstance(value, str) and PLACEHOLDER_RE.search(value):
        result.warn(f"'{field}' contains unreplaced placeholder: {value!r}")


def _check_semver(value, field, result):
    if not SEMVER_RE.match(value):
        result.error(f"'{field}' must be a valid semver string (got {value!r})")


def _validate_tool(tool, idx, result):
    prefix = f"tools[{idx}]"
    for key in REQUIRED_TOOL:
        if key not in tool:
            result.error(f"{prefix} missing required field '{key}'")

    name = tool.get("name", "")
    if name and not TOOL_NAME_RE.match(name):
        result.error(f"{prefix}.name must match [A-Za-z][A-Za-z0-9_-]{{0,63}} (got {name!r})")
    if name:
        _check_placeholders(name, f"{prefix}.name", result)

    for effect in tool.get("side_effects", []):
        if effect not in VALID_SIDE_EFFECTS:
            result.error(f"{prefix}.side_effects contains unknown value {effect!r}; valid: {sorted(VALID_SIDE_EFFECTS)}")

    requires = tool.get("requires_approval")
    if requires is not None and not isinstance(requires, bool):
        result.error(f"{prefix}.requires_approval must be a boolean")

    schema_path = tool.get("schema_path", "")
    _check_placeholders(schema_path, f"{prefix}.schema_path", result)


def _validate_command(cmd, idx, result):
    prefix = f"commands[{idx}]"
    for key in REQUIRED_COMMAND:
        if key not in cmd:
            result.error(f"{prefix} missing required field '{key}'")

    name = cmd.get("name", "")
    _check_placeholders(name, f"{prefix}.name", result)
    prompt_path = cmd.get("prompt_path", "")
    _check_placeholders(prompt_path, f"{prefix}.prompt_path", result)


# ── Main validator ────────────────────────────────────────────────────────────

def validate(manifest_path: Path) -> ValidationResult:
    result = ValidationResult()

    # 1. Parse JSON
    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        result.error(f"Invalid JSON: {exc}")
        return result
    except OSError as exc:
        result.error(f"Cannot read file: {exc}")
        return result

    if not isinstance(data, dict):
        result.error("Manifest must be a JSON object at the top level")
        return result

    # 2. Required top-level fields
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            result.error(f"Missing required top-level field '{key}'")

    # 3. id format
    manifest_id = data.get("id", "")
    if manifest_id and not ID_RE.match(manifest_id):
        result.error(f"'id' must be lowercase kebab-case 2–80 chars (got {manifest_id!r})")
    if manifest_id:
        _check_placeholders(manifest_id, "id", result)

    # 4. version semver
    version = data.get("version", "")
    if version:
        _check_semver(version, "version", result)
        _check_placeholders(version, "version", result)

    # 5. description not empty and no placeholders
    desc = data.get("description", "")
    if desc:
        _check_placeholders(desc, "description", result)
    elif "description" in data:
        result.error("'description' must not be empty")

    # 6. runtime block
    runtime = data.get("runtime", {})
    if isinstance(runtime, dict):
        for key in REQUIRED_RUNTIME:
            if key not in runtime:
                result.error(f"'runtime' missing required field '{key}'")

        min_ver = runtime.get("min_agent_version", "")
        if min_ver:
            _check_semver(min_ver, "runtime.min_agent_version", result)

        max_ver = runtime.get("max_agent_version")
        if max_ver:
            _check_semver(max_ver, "runtime.max_agent_version", result)

        for platform in runtime.get("platform", []):
            if platform not in VALID_PLATFORMS:
                result.warn(f"'runtime.platform' contains unrecognised value {platform!r}; known: {sorted(VALID_PLATFORMS)}")
    elif "runtime" in data:
        result.error("'runtime' must be an object")

    # 7. entry block — at least one language entry
    entry = data.get("entry", {})
    if isinstance(entry, dict):
        if not entry:
            result.error("'entry' must contain at least one language entry")
        for lang, path in entry.items():
            _check_placeholders(path, f"entry.{lang}", result)
    elif "entry" in data:
        result.error("'entry' must be an object")

    # 8. tools
    for idx, tool in enumerate(data.get("tools", [])):
        if not isinstance(tool, dict):
            result.error(f"tools[{idx}] must be an object")
        else:
            _validate_tool(tool, idx, result)

    # 9. commands
    for idx, cmd in enumerate(data.get("commands", [])):
        if not isinstance(cmd, dict):
            result.error(f"commands[{idx}] must be an object")
        else:
            _validate_command(cmd, idx, result)

    # 10. permissions
    perms = data.get("permissions", {})
    if isinstance(perms, dict):
        for perm in perms.get("required", []) + perms.get("optional", []):
            if perm not in VALID_SIDE_EFFECTS:
                result.warn(f"'permissions' references unknown side-effect {perm!r}; valid: {sorted(VALID_SIDE_EFFECTS)}")

    # 11. Warn on unreplaced placeholders in name, author, repository
    for field in ["name", "author", "repository", "homepage"]:
        _check_placeholders(data.get(field, ""), field, result)

    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate plugin.manifest.json files (stdlib-only)."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a manifest file or directory to scan (default: current dir)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on warnings as well as errors",
    )
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_dir():
        manifest_files = list(target.rglob("plugin.manifest.json"))
        if not manifest_files:
            # Also accept *.manifest.json patterns
            manifest_files = list(target.rglob("*.manifest.json"))
        if not manifest_files:
            print(f"No manifest files found under {target}")
            sys.exit(0)
    elif target.is_file():
        manifest_files = [target]
    else:
        print(f"Path not found: {target}")
        sys.exit(1)

    all_passed = True
    print(f"\nValidating {len(manifest_files)} manifest file(s):\n")
    for mf in sorted(manifest_files):
        result = validate(mf)
        result.print_report(mf)
        if not result.passed:
            all_passed = False
        if args.strict and result.warnings:
            all_passed = False

    print()
    if all_passed:
        print("All manifests passed validation.")
        sys.exit(0)
    else:
        print("One or more manifests failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
