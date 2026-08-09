#!/usr/bin/env python3
"""
config_diff.py — Diff two config files and report added/removed/changed keys.

Supports: .env (KEY=VALUE), .json, .yaml / .yml (subset parsed via stdlib).
Key ordering is normalised before comparison so irrelevant reorderings are
not reported as changes.

Usage:
    python3 config_diff.py file_a file_b

Stdlib only. No third-party dependencies (yaml parsed with a minimal reader).
"""

import argparse
import json
import os
import re
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_env(text: str) -> dict[str, str]:
    """Parse a .env / shell-style KEY=VALUE file.

    - Ignores blank lines and lines starting with '#'.
    - Strips optional surrounding quotes from values.
    - Last occurrence of a duplicate key wins (matches dotenv behaviour).
    """
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip matching surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        result[key] = value
    return result


def _parse_json(text: str) -> dict[str, Any]:
    """Parse a JSON file; must be a top-level object."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object/dict.")
    return data


def _minimal_yaml_parse(text: str) -> dict[str, Any]:
    """Minimal YAML parser for flat and one-level-nested key:value files.

    Handles the common config file cases without PyYAML:
    - Scalar values (strings, numbers, booleans, null)
    - One level of nesting (section headers)
    - Inline comments

    Does NOT handle multi-line strings, anchors, or complex YAML.
    Falls back to treating the whole file as .env on parse failure.
    """
    result: dict[str, Any] = {}
    current_section: str | None = None

    _scalar = re.compile(
        r'^(?P<indent>\s*)'
        r'(?P<key>[^:#\s][^:]*?)\s*:\s*'
        r'(?P<value>.*?)(?:\s*#.*)?$'
    )

    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue
        m = _scalar.match(stripped)
        if not m:
            continue
        indent = m.group("indent")
        key = m.group("key").strip()
        raw_value = m.group("value").strip()

        # Parse scalar value
        if raw_value == "" or raw_value.lower() in ("~", "null"):
            value: Any = None
        elif raw_value.lower() == "true":
            value = True
        elif raw_value.lower() == "false":
            value = False
        else:
            try:
                value = int(raw_value)
            except ValueError:
                try:
                    value = float(raw_value)
                except ValueError:
                    # Strip surrounding quotes
                    if (len(raw_value) >= 2
                            and raw_value[0] in ('"', "'")
                            and raw_value[-1] == raw_value[0]):
                        value = raw_value[1:-1]
                    else:
                        value = raw_value

        if indent:
            # Nested key under current section
            if current_section is not None:
                section_dict = result.setdefault(current_section, {})
                if isinstance(section_dict, dict):
                    section_dict[key] = value
        else:
            if raw_value == "":
                # Section header (value is empty, will hold child dict)
                current_section = key
                result[key] = {}
            else:
                current_section = None
                result[key] = value

    return result


def load_config(path: str) -> dict[str, Any]:
    """Load a config file and return a normalised flat-or-nested dict."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"error: permission denied: {path}", file=sys.stderr)
        sys.exit(1)

    _, ext = os.path.splitext(path.lower())
    if ext == ".json":
        try:
            return _parse_json(text)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"error: could not parse {path} as JSON: {exc}", file=sys.stderr)
            sys.exit(1)
    elif ext in (".yaml", ".yml"):
        return _minimal_yaml_parse(text)
    else:
        # Default: treat as .env / KEY=VALUE
        return _parse_env(text)


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------

def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Flatten a potentially nested dict to dot-separated keys."""
    out: dict[str, str] = {}
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, full_key))
        else:
            out[full_key] = str(v)
    return out


def diff_configs(
    a: dict[str, Any],
    b: dict[str, Any],
    label_a: str,
    label_b: str,
) -> bool:
    """Print a human-readable diff. Returns True if any differences found."""
    flat_a = _flatten(a)
    flat_b = _flatten(b)

    keys_a = set(flat_a)
    keys_b = set(flat_b)

    removed = sorted(keys_a - keys_b)
    added = sorted(keys_b - keys_a)
    common = sorted(keys_a & keys_b)
    changed = [(k, flat_a[k], flat_b[k]) for k in common if flat_a[k] != flat_b[k]]

    if not removed and not added and not changed:
        print("No differences found.")
        return False

    print(f"{'='*64}")
    print(f"Config diff:  {label_a}  →  {label_b}")
    print(f"{'='*64}")

    if added:
        print(f"\nAdded ({len(added)}):")
        for k in added:
            print(f"  + {k} = {flat_b[k]}")

    if removed:
        print(f"\nRemoved ({len(removed)}):")
        for k in removed:
            print(f"  - {k} = {flat_a[k]}")

    if changed:
        print(f"\nChanged ({len(changed)}):")
        for k, va, vb in changed:
            print(f"  ~ {k}")
            print(f"      was : {va}")
            print(f"      now : {vb}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Diff two config files (.env, .json, .yaml/.yml) and report "
            "added, removed, and changed keys."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 config_diff.py .env.staging .env.production\n"
            "  python3 config_diff.py config.dev.json config.prod.json\n"
            "  python3 config_diff.py app.staging.yaml app.prod.yaml\n"
        ),
    )
    parser.add_argument("file_a", help="First config file (baseline).")
    parser.add_argument("file_b", help="Second config file (to compare against).")
    args = parser.parse_args()

    config_a = load_config(args.file_a)
    config_b = load_config(args.file_b)
    had_diff = diff_configs(config_a, config_b, args.file_a, args.file_b)
    sys.exit(1 if had_diff else 0)


if __name__ == "__main__":
    main()
