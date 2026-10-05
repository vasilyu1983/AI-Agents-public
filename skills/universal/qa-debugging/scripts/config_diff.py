#!/usr/bin/env python3
"""
config_diff.py — Diff two config files and report added/removed/changed keys.

Supports: .env (KEY=VALUE), .json, .yaml / .yml. Nested keys are flattened to
dot paths and list items to `key[i]`, so key ordering never shows as a change.

Exit codes (same convention as diff(1)):
    0 = no differences, 1 = differences found, 2 = error (missing file or a
    file that could not be parsed).

Fails closed: a line the parser does not understand is an error, never a
silent skip, because a skipped line reads as "no difference" and hides the
config drift you are looking for.

Values of secret-looking keys (password, token, secret, api key, credential,
auth) are redacted in the output unless --show-secrets is passed; the
added/removed/changed classification is still computed on the real values.

Usage:
    python3 config_diff.py file_a file_b [--show-secrets]

Stdlib only. Uses PyYAML for .yaml files when it is installed; otherwise a
strict minimal reader handles nested mappings, scalars, and `- scalar` lists
and rejects anything else (anchors, block scalars, flow collections, lists of
mappings) with an error that names the line.
"""

import argparse
import json
import os
import re
import sys
from typing import Any

_SECRET_KEY_RE = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?key|private[_-]?key|credential|auth)",
    re.IGNORECASE,
)


class ParseError(Exception):
    """Raised when a config file cannot be parsed without guessing."""


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_env(text: str) -> dict[str, str]:
    """Parse a .env / shell-style KEY=VALUE file.

    - Ignores blank lines and lines starting with '#'; accepts `export KEY=V`.
    - Strips optional surrounding quotes from values.
    - Last occurrence of a duplicate key wins (matches dotenv behaviour).
    - Any other line is a ParseError.
    """
    result: dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.\-]*", key):
            raise ParseError(f"line {lineno}: not a KEY=VALUE line: {raw.strip()[:80]!r}")
        value = value.strip()
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        result[key] = value
    return result


def _parse_json(text: str) -> dict[str, Any]:
    """Parse a JSON file; must be a top-level object."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError(str(exc)) from exc
    if not isinstance(data, dict):
        raise ParseError("JSON root must be an object")
    return data


def _yaml_scalar(raw: str, lineno: int) -> Any:
    if raw[:1] in ("&", "*", "!", "|", ">", "{", "["):
        raise ParseError(
            f"line {lineno}: unsupported YAML construct {raw[:20]!r}; install PyYAML"
        )
    if raw == "" or raw.lower() in ("~", "null"):
        return None
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if len(raw) >= 2 and raw[0] in ('"', "'") and raw[-1] == raw[0]:
        return raw[1:-1]
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            pass
    return raw


def _strip_comment(content: str) -> str:
    if content.startswith("#"):
        return ""
    if "'" in content or '"' in content:
        return content
    return re.sub(r"\s+#.*$", "", content)


def _minimal_yaml_parse(text: str) -> dict[str, Any]:
    """Strict indentation-based reader for mappings, scalars, and scalar lists."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = []  # (indent, container)
    pending: tuple[dict, str, int] | None = None  # key awaiting a child block
    seen_doc_start = False

    for lineno, raw in enumerate(text.splitlines(), start=1):
        body = raw.rstrip()
        if not body.strip():
            continue
        leading = body[: len(body) - len(body.lstrip())]
        if "\t" in leading:
            raise ParseError(f"line {lineno}: tab indentation is not valid YAML")
        indent = len(leading)
        content = _strip_comment(body.strip())
        if not content:
            continue
        if content == "---":
            if seen_doc_start or stack:
                raise ParseError(f"line {lineno}: multi-document YAML is not supported")
            seen_doc_start = True
            continue

        is_item = content == "-" or content.startswith("- ")
        if pending is not None:
            parent, key, pindent = pending
            if indent > pindent or (is_item and indent == pindent):
                child: Any = [] if is_item else {}
                parent[key] = child
                stack.append((indent, child))
            else:
                parent[key] = None
            pending = None
        if not stack:
            stack.append((indent, root))
        while len(stack) > 1 and (
            indent < stack[-1][0]
            or (not is_item and indent == stack[-1][0] and isinstance(stack[-1][1], list))
        ):
            stack.pop()
        if indent != stack[-1][0]:
            raise ParseError(f"line {lineno}: inconsistent indentation")
        container = stack[-1][1]

        if is_item:
            if not isinstance(container, list):
                raise ParseError(f"line {lineno}: list item where a mapping key was expected")
            item = content[1:].strip()
            if re.match(r"^[^'\"]+?:(\s|$)", item):
                raise ParseError(f"line {lineno}: list of mappings is not supported; install PyYAML")
            container.append(_yaml_scalar(item, lineno))
            continue

        m = re.match(r"^(?P<key>[^:]+?|\"[^\"]+\"|'[^']+'):(?:\s+(?P<value>.*))?$", content)
        if not m:
            raise ParseError(f"line {lineno}: not a 'key: value' line: {content[:80]!r}")
        if not isinstance(container, dict):
            raise ParseError(f"line {lineno}: mapping key inside a list is not supported")
        key = m.group("key").strip().strip("'\"")
        value = (m.group("value") or "").strip()
        if value == "":
            pending = (container, key, indent)
        else:
            container[key] = _yaml_scalar(value, lineno)

    if pending is not None:
        parent, key, _ = pending
        parent[key] = None
    return root


def _parse_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return _minimal_yaml_parse(text)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ParseError(str(exc)) from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ParseError("YAML root must be a mapping")
    return data


def load_config(path: str) -> dict[str, Any]:
    """Load a config file; exit 2 on any read or parse failure."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError:
        print(f"error: is a directory: {path}", file=sys.stderr)
        sys.exit(2)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {path} as UTF-8 text: {exc}", file=sys.stderr)
        sys.exit(2)

    _, ext = os.path.splitext(path.lower())
    try:
        if ext == ".json":
            return _parse_json(text)
        if ext in (".yaml", ".yml"):
            return _parse_yaml(text)
        return _parse_env(text)
    except ParseError as exc:
        kind = {".json": "JSON", ".yaml": "YAML", ".yml": "YAML"}.get(ext, "KEY=VALUE")
        print(f"error: could not parse {path} as {kind}: {exc}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------

def _flatten(data: Any, prefix: str = "") -> dict[str, str]:
    """Flatten paths without conflating key syntax or scalar types."""
    out: dict[str, str] = {}
    if isinstance(data, dict):
        if not data and prefix:
            out[prefix] = "{}"
        for k, v in data.items():
            if not isinstance(k, str):
                raise ParseError("mapping keys must be strings")
            # Escape path punctuation so {"a.b": 1} differs from {"a": {"b": 1}}.
            key = re.sub(r"([\\.\[\]])", r"\\\1", k) if k else r"\e"
            out.update(_flatten(v, f"{prefix}.{key}" if prefix else key))
    elif isinstance(data, list):
        if not data:
            out[prefix] = "[]"
        for i, v in enumerate(data):
            out.update(_flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = json.dumps(data)
    return out


def _show(key: str, value: str, show_secrets: bool) -> str:
    if not show_secrets and _SECRET_KEY_RE.search(key):
        return "<redacted>"
    return value


def diff_configs(
    a: dict[str, Any],
    b: dict[str, Any],
    label_a: str,
    label_b: str,
    show_secrets: bool = False,
) -> bool:
    """Print a human-readable diff. Returns True if any differences found."""
    flat_a = _flatten(a)
    flat_b = _flatten(b)

    removed = sorted(set(flat_a) - set(flat_b))
    added = sorted(set(flat_b) - set(flat_a))
    changed = [k for k in sorted(set(flat_a) & set(flat_b)) if flat_a[k] != flat_b[k]]

    if not removed and not added and not changed:
        print(f"No differences found ({len(flat_a)} keys compared).")
        return False

    print(f"{'='*64}")
    print(f"Config diff:  {label_a}  ->  {label_b}")
    print(f"{'='*64}")

    if added:
        print(f"\nAdded ({len(added)}):")
        for k in added:
            print(f"  + {k} = {_show(k, flat_b[k], show_secrets)}")

    if removed:
        print(f"\nRemoved ({len(removed)}):")
        for k in removed:
            print(f"  - {k} = {_show(k, flat_a[k], show_secrets)}")

    if changed:
        print(f"\nChanged ({len(changed)}):")
        for k in changed:
            print(f"  ~ {k}")
            print(f"      was : {_show(k, flat_a[k], show_secrets)}")
            print(f"      now : {_show(k, flat_b[k], show_secrets)}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Diff two config files (.env, .json, .yaml/.yml) and report "
            "added, removed, and changed keys. Exit 0 = same, 1 = differ, 2 = error."
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
    parser.add_argument(
        "--show-secrets",
        action="store_true",
        help="Print values of secret-looking keys instead of <redacted>.",
    )
    args = parser.parse_args()

    config_a = load_config(args.file_a)
    config_b = load_config(args.file_b)
    try:
        had_diff = diff_configs(config_a, config_b, args.file_a, args.file_b, args.show_secrets)
    except (ParseError, TypeError, ValueError) as exc:
        print(f"error: cannot compare configuration: {exc}", file=sys.stderr)
        sys.exit(2)
    sys.exit(1 if had_diff else 0)


if __name__ == "__main__":
    main()
