"""
recipe_scanner.py

Static validator for Goose-style recipe blueprint YAML files.
Python stdlib only — no external dependencies required.

A recipe blueprint must pass all checks before it can be promoted to a
typed task blueprint in the agent runtime. This validator is the
reference implementation of the "recipe-scanner" check mentioned in
SKILL.md.

Usage:
    python recipe_scanner.py recipe.yaml              # validate one file
    python recipe_scanner.py recipes/                 # validate all .yaml in dir
    python recipe_scanner.py --strict recipe.yaml     # treat warnings as errors

Exit codes:
    0  — all files passed (or only warnings in non-strict mode)
    1  — one or more errors found
"""

from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Minimal YAML parser (stdlib only)
# ---------------------------------------------------------------------------


def _parse_yaml_simple(text: str) -> dict:
    """
    Extremely minimal YAML parser that handles the flat and one-level-nested
    structures used in recipe blueprints. Supports:
      - top-level key: value pairs
      - top-level key: followed by indented list items (- item)
      - top-level key: followed by indented key: value pairs
      - multi-line values using | (block literal) — stored as raw string
      - inline lists: [a, b, c]
      - quoted strings: "..." and '...'
      - comments (#)

    Not a general YAML parser. For production use, add PyYAML.
    """
    result: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0

    def strip_comment(s: str) -> str:
        # Remove inline comments (outside quotes)
        in_quote: str | None = None
        for idx, ch in enumerate(s):
            if in_quote:
                if ch == in_quote:
                    in_quote = None
            elif ch in ('"', "'"):
                in_quote = ch
            elif ch == "#":
                return s[:idx].rstrip()
        return s

    def unquote(s: str) -> str:
        s = s.strip()
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            return s[1:-1]
        return s

    while i < len(lines):
        line = lines[i]
        stripped = strip_comment(line)
        if not stripped.strip() or stripped.strip().startswith("#"):
            i += 1
            continue

        # Top-level key
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_\-]*):\s*(.*)', stripped)
        if not m:
            i += 1
            continue

        key = m.group(1)
        rest = m.group(2).strip()

        # Inline list: key: [a, b, c]
        if rest.startswith("[") and rest.endswith("]"):
            items = [unquote(x) for x in rest[1:-1].split(",") if x.strip()]
            result[key] = items
            i += 1
            continue

        # Block literal: key: |
        if rest == "|":
            block_lines = []
            i += 1
            while i < len(lines):
                bl = lines[i]
                if bl and not bl[0].isspace():
                    break
                block_lines.append(bl.rstrip())
                i += 1
            result[key] = "\n".join(block_lines)
            continue

        # Scalar value on same line
        if rest:
            result[key] = unquote(rest)
            i += 1
            continue

        # Multi-line: collect indented children
        children_lines = []
        i += 1
        while i < len(lines):
            cl = lines[i]
            if cl and not cl[0].isspace():
                break
            children_lines.append(cl)
            i += 1

        # Determine if children are a list or a mapping
        is_list = any(re.match(r'^\s+-\s+', c) for c in children_lines if c.strip())
        if is_list:
            items = []
            for cl in children_lines:
                m2 = re.match(r'^\s+-\s+(.*)', cl)
                if m2:
                    items.append(unquote(m2.group(1).strip()))
            result[key] = items
        else:
            sub: dict[str, str] = {}
            for cl in children_lines:
                sm = re.match(r'^\s+([A-Za-z_][A-Za-z0-9_\-]*):\s*(.*)', cl)
                if sm:
                    sub[sm.group(1)] = unquote(sm.group(2).strip())
            if sub:
                result[key] = sub

    return result


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


REQUIRED_FIELDS = ["version", "title", "description", "instructions"]
OPTIONAL_FIELDS = ["author", "extensions", "activities", "prompt", "parameters"]
KNOWN_FIELDS = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)

# Parameters are declared as a list of objects with these sub-keys
PARAM_REQUIRED_KEYS = {"key", "input_type", "requirement", "description"}
PARAM_OPTIONAL_KEYS = {"default"}
VALID_INPUT_TYPES = {"string", "boolean", "integer", "float", "list"}
VALID_REQUIREMENTS = {"required", "optional"}

# Security gate: extensions that touch the network or filesystem
HIGH_RISK_EXTENSIONS = {
    "network", "web_search", "filesystem_write", "shell", "bash",
    "code_execution", "docker", "container", "mcp__github", "mcp__slack",
}


def _check(errors: list, warnings: list, condition: bool, message: str, is_error: bool = True) -> None:
    if not condition:
        (errors if is_error else warnings).append(message)


def validate_recipe(path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    """
    Returns (errors, warnings). errors is non-empty if the recipe is invalid.
    warnings are non-fatal unless strict=True.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # --- Read file ---
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        errors.append(f"Cannot read file: {e}")
        return errors, warnings

    # --- Parse ---
    try:
        recipe = _parse_yaml_simple(text)
    except Exception as e:  # noqa: BLE001
        errors.append(f"YAML parse error: {e}")
        return errors, warnings

    if not recipe:
        errors.append("File parsed to empty dict — check YAML syntax")
        return errors, warnings

    # --- Required fields ---
    for field in REQUIRED_FIELDS:
        if field not in recipe or not recipe[field]:
            errors.append(f"Missing required field: '{field}'")

    # --- Version format (must be semver-like: N.N or N.N.N) ---
    version = recipe.get("version", "")
    if version and not re.match(r'^\d+\.\d+(\.\d+)?$', str(version)):
        errors.append(f"'version' must be semver-like (e.g. 1.0 or 1.0.0), got: '{version}'")

    # --- Title length ---
    title = recipe.get("title", "")
    if title and len(str(title)) > 120:
        warnings.append(f"'title' is very long ({len(str(title))} chars); keep under 120")

    # --- Instructions non-trivial ---
    instructions = recipe.get("instructions", "")
    if instructions and len(str(instructions).split()) < 5:
        warnings.append("'instructions' appears too short; verify it is not a placeholder")

    # --- Unknown top-level fields ---
    for key in recipe:
        if key not in KNOWN_FIELDS:
            warnings.append(f"Unknown top-level field: '{key}' (known: {sorted(KNOWN_FIELDS)})")

    # --- Parameters validation ---
    params = recipe.get("parameters")
    if params is not None:
        if not isinstance(params, list):
            errors.append("'parameters' must be a list of parameter objects")
        else:
            for idx, param in enumerate(params):
                if not isinstance(param, dict):
                    errors.append(f"parameters[{idx}] must be a mapping, got: {type(param).__name__}")
                    continue
                for req_key in PARAM_REQUIRED_KEYS:
                    if req_key not in param or not param[req_key]:
                        errors.append(f"parameters[{idx}] missing required sub-key: '{req_key}'")
                input_type = param.get("input_type", "")
                if input_type and input_type not in VALID_INPUT_TYPES:
                    errors.append(
                        f"parameters[{idx}].input_type '{input_type}' is not valid "
                        f"(valid: {sorted(VALID_INPUT_TYPES)})"
                    )
                requirement = param.get("requirement", "")
                if requirement and requirement not in VALID_REQUIREMENTS:
                    errors.append(
                        f"parameters[{idx}].requirement '{requirement}' is not valid "
                        f"(valid: {sorted(VALID_REQUIREMENTS)})"
                    )
                unknown_param_keys = set(param.keys()) - PARAM_REQUIRED_KEYS - PARAM_OPTIONAL_KEYS
                for uk in sorted(unknown_param_keys):
                    warnings.append(f"parameters[{idx}] has unknown sub-key: '{uk}'")

    # --- Extensions validation ---
    extensions = recipe.get("extensions")
    if extensions is not None:
        if not isinstance(extensions, list):
            errors.append("'extensions' must be a list of extension names or references")
        else:
            for ext in extensions:
                ext_lower = str(ext).lower()
                for risky in HIGH_RISK_EXTENSIONS:
                    if risky in ext_lower:
                        warnings.append(
                            f"Extension '{ext}' looks high-risk (matches '{risky}'). "
                            "Verify this recipe is allowed to use network/filesystem/shell tools."
                        )
                        break

    # --- Activities validation ---
    activities = recipe.get("activities")
    if activities is not None and not isinstance(activities, list):
        errors.append("'activities' must be a list")

    # --- Unresolved placeholders ---
    placeholder_re = re.compile(r'\{\{[^}]+\}\}')
    for field_name in REQUIRED_FIELDS + OPTIONAL_FIELDS:
        value = recipe.get(field_name, "")
        if isinstance(value, str) and placeholder_re.search(value):
            warnings.append(f"Field '{field_name}' contains unresolved placeholder: {placeholder_re.findall(value)}")

    return errors, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _collect_paths(target: str) -> list[Path]:
    p = Path(target)
    if p.is_dir():
        return sorted(p.glob("**/*.yaml")) + sorted(p.glob("**/*.yml"))
    return [p]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Static validator for recipe blueprint YAML files (stdlib only)."
    )
    parser.add_argument("targets", nargs="+", help="Recipe file(s) or directory")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    paths: list[Path] = []
    for t in args.targets:
        paths.extend(_collect_paths(t))

    if not paths:
        print("No .yaml or .yml files found.", file=sys.stderr)
        return 1

    total_errors = 0
    total_warnings = 0

    for path in paths:
        errors, warnings = validate_recipe(path, strict=args.strict)
        if args.strict:
            errors = errors + warnings
            warnings = []

        if errors or warnings:
            print(f"\n{'[FAIL]' if errors else '[WARN]'} {path}")
            for e in errors:
                print(f"  ERROR: {e}")
            for w in warnings:
                print(f"  WARN:  {w}")
        else:
            print(f"  [OK]  {path}")

        total_errors += len(errors)
        total_warnings += len(warnings)

    print(
        f"\nSummary: {len(paths)} file(s) — "
        f"{total_errors} error(s), {total_warnings} warning(s)"
    )

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
