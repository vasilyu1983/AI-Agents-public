"""
recipe_scanner.py

Static validator for Goose-style recipe blueprint YAML files.

Parsing: uses PyYAML (`yaml.safe_load`) when it is importable. Otherwise it
falls back to a small stdlib parser that understands only the shapes recipe
blueprints use (top-level scalars, block scalars, inline lists, one level of
lists or mappings, and lists of flat mappings). The fallback FAILS CLOSED:
any construct it cannot represent exactly is a parse error, never a silently
flattened value.

A recipe blueprint must pass all checks before it can be promoted to a
typed task blueprint in the agent runtime. This validator is the
reference implementation of the "recipe-scanner" check mentioned in
SKILL.md.

Security gate: a high-risk extension (network, shell, filesystem-write, a
`stdio` extension that launches a local command, or a pipe-to-shell command)
is an ERROR unless `--allow-high-risk` is passed, which downgrades the
risk-name matches to warnings. A pipe-to-shell command is always an error.

Usage:
    python recipe_scanner.py recipe.yaml              # validate one file
    python recipe_scanner.py recipes/                 # validate all .yaml in dir
    python recipe_scanner.py --strict recipe.yaml     # treat warnings as errors
    python recipe_scanner.py --allow-high-risk r.yaml # acknowledge risky extensions

Exit codes:
    0  — all files passed (or only warnings in non-strict mode)
    1  — one or more errors found (including unparseable input)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


class RecipeParseError(ValueError):
    """Raised when the recipe cannot be parsed exactly."""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_KEY_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_\-]*):(?:\s+(.*)|\s*)$')
_BLOCK_INDICATORS = {"|", "|-", "|+", ">", ">-", ">+"}


def _strip_comment(s: str) -> str:
    """Remove a YAML comment: '#' at line start or after whitespace, outside quotes."""
    in_quote: str | None = None
    for idx, ch in enumerate(s):
        if in_quote:
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
        elif ch == "#" and (idx == 0 or s[idx - 1].isspace()):
            return s[:idx].rstrip()
    return s.rstrip()


def _indent(s: str) -> int:
    return len(s) - len(s.lstrip(" "))


def _scalar(raw: str, lineno: int) -> Any:
    """Parse an inline value: quoted string, inline list, or plain scalar."""
    s = raw.strip()
    if not s:
        return ""
    if s[0] in "{&*!" or s in _BLOCK_INDICATORS:
        raise RecipeParseError(
            f"line {lineno}: unsupported YAML construct {s[:20]!r} "
            "(install PyYAML for full YAML support)"
        )
    if s.startswith("["):
        if not s.endswith("]"):
            raise RecipeParseError(f"line {lineno}: unterminated inline list")
        inner = s[1:-1]
        if any(ch in inner for ch in "[]{}"):
            raise RecipeParseError(f"line {lineno}: nested inline collections are unsupported")
        return [_unquote(x) for x in inner.split(",") if x.strip()]
    return _unquote(s)


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _parse_yaml_simple(text: str) -> dict:
    """Fail-closed stdlib parser for the recipe subset described in the module docstring."""
    result: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = _strip_comment(raw)
        if not line.strip():
            i += 1
            continue
        if line.strip() in ("---", "..."):
            i += 1
            continue
        if _indent(line) != 0 or raw.startswith("\t"):
            raise RecipeParseError(f"line {i + 1}: unexpected indentation at top level")
        m = _KEY_RE.match(line)
        if not m:
            raise RecipeParseError(f"line {i + 1}: expected 'key: value', got {line.strip()[:40]!r}")
        key, rest = m.group(1), (m.group(2) or "").strip()
        if key in result:
            raise RecipeParseError(f"line {i + 1}: duplicate top-level key {key!r}")

        if rest in _BLOCK_INDICATORS:
            i += 1
            block: list[str] = []
            while i < n and (not lines[i].strip() or lines[i][0].isspace()):
                block.append(lines[i].strip())
                i += 1
            joiner = "\n" if rest.startswith("|") else " "
            result[key] = joiner.join(block).strip()
            continue

        if rest:
            result[key] = _scalar(rest, i + 1)
            i += 1
            continue

        # Indented children
        i += 1
        children: list[tuple[int, str]] = []
        while i < n:
            cl = lines[i]
            stripped = _strip_comment(cl)
            if stripped.strip() and not cl[0].isspace():
                break
            if stripped.strip():
                if "\t" in cl[: _indent(cl) + 1]:
                    raise RecipeParseError(f"line {i + 1}: tab indentation is unsupported")
                children.append((i + 1, stripped))
            i += 1
        if not children:
            result[key] = None
            continue
        if children[0][1].lstrip().startswith("- ") or children[0][1].strip() == "-":
            result[key] = _parse_list(children)
        else:
            result[key] = _parse_flat_mapping(children, _indent(children[0][1]))

    return result


def _parse_flat_mapping(children: list[tuple[int, str]], base: int) -> dict:
    out: dict[str, Any] = {}
    for lineno, text in children:
        if _indent(text) != base:
            raise RecipeParseError(
                f"line {lineno}: nested structure deeper than one level is unsupported "
                "(install PyYAML)"
            )
        m = _KEY_RE.match(text.strip())
        if not m:
            raise RecipeParseError(f"line {lineno}: expected 'key: value' in mapping")
        val = (m.group(2) or "").strip()
        if not val:
            raise RecipeParseError(f"line {lineno}: nested mapping or list is unsupported (install PyYAML)")
        out[m.group(1)] = _scalar(val, lineno)
    return out


def _parse_list(children: list[tuple[int, str]]) -> list:
    dash_indent = _indent(children[0][1])
    items: list[Any] = []
    current: dict[str, Any] | None = None
    content_indent = dash_indent + 2
    for lineno, text in children:
        ind = _indent(text)
        body = text.strip()
        if ind == dash_indent and (body.startswith("- ") or body == "-"):
            item = body[1:].strip()
            if not item:
                raise RecipeParseError(f"line {lineno}: empty list item or nested block is unsupported")
            if item.startswith("- "):
                raise RecipeParseError(f"line {lineno}: nested lists are unsupported (install PyYAML)")
            m = _KEY_RE.match(item) if item[0] not in "\"'" else None
            if m:
                val = (m.group(2) or "").strip()
                if not val:
                    raise RecipeParseError(
                        f"line {lineno}: nested value under list-item key is unsupported (install PyYAML)"
                    )
                current = {m.group(1): _scalar(val, lineno)}
                items.append(current)
            else:
                current = None
                items.append(_scalar(item, lineno))
            continue
        if ind == content_indent and current is not None:
            m = _KEY_RE.match(body)
            if not m:
                raise RecipeParseError(f"line {lineno}: expected 'key: value' inside list item")
            val = (m.group(2) or "").strip()
            if not val:
                raise RecipeParseError(
                    f"line {lineno}: nested value under list-item key is unsupported (install PyYAML)"
                )
            if m.group(1) in current:
                raise RecipeParseError(f"line {lineno}: duplicate key {m.group(1)!r} in list item")
            current[m.group(1)] = _scalar(val, lineno)
            continue
        raise RecipeParseError(
            f"line {lineno}: indentation does not match a list item or its fields (install PyYAML)"
        )
    return items


def parse_recipe_text(text: str, use_pyyaml: bool | None = None) -> dict:
    """Parse recipe text. use_pyyaml=None means 'use PyYAML if importable'."""
    if use_pyyaml is not False:
        try:
            import yaml  # type: ignore
        except ImportError:
            if use_pyyaml:
                raise RecipeParseError("PyYAML requested but not installed")
        else:
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as e:
                raise RecipeParseError(str(e)) from e
            if data is None:
                return {}
            if not isinstance(data, dict):
                raise RecipeParseError(f"top level must be a mapping, got {type(data).__name__}")
            return data
    return _parse_yaml_simple(text)


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

# Security gate: extensions that touch the network, shell, or filesystem
HIGH_RISK_EXTENSIONS = {
    "network", "web_search", "filesystem_write", "shell", "bash",
    "code_execution", "docker", "container", "mcp__github", "mcp__slack",
}
# Extension types that launch an arbitrary local process
HIGH_RISK_EXTENSION_TYPES = {"stdio"}
PIPE_TO_SHELL_RE = re.compile(
    r'(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b|\b(ba|z|da)?sh\s+-c\b', re.IGNORECASE
)


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{k} {_flatten_text(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten_text(v) for v in value)
    return "" if value is None else str(value)


def _check_extension(ext: Any, idx: int, allow_high_risk: bool,
                     errors: list[str], warnings: list[str]) -> None:
    if isinstance(ext, str):
        label, blob, ext_type = ext, ext, ""
    elif isinstance(ext, dict):
        if not ext.get("type") and not ext.get("name"):
            errors.append(f"extensions[{idx}] mapping must declare 'type' or 'name'")
        label = str(ext.get("name") or ext.get("type") or f"extensions[{idx}]")
        blob = _flatten_text(ext)
        ext_type = str(ext.get("type", "")).lower()
    else:
        errors.append(f"extensions[{idx}] must be a name or a mapping, got: {type(ext).__name__}")
        return

    if PIPE_TO_SHELL_RE.search(blob):
        errors.append(
            f"Extension '{label}' runs a shell/pipe-to-shell command; recipes must not "
            "download-and-execute code."
        )
        return

    reasons: list[str] = []
    if ext_type in HIGH_RISK_EXTENSION_TYPES:
        reasons.append(f"type '{ext_type}' launches a local process")
    lower = blob.lower()
    reasons.extend(f"matches '{r}'" for r in sorted(HIGH_RISK_EXTENSIONS) if r in lower)
    if reasons:
        msg = (
            f"Extension '{label}' looks high-risk ({'; '.join(reasons)}). "
            "Verify this recipe is allowed to use network/filesystem/shell tools"
        )
        if allow_high_risk:
            warnings.append(msg + " (acknowledged via --allow-high-risk).")
        else:
            errors.append(msg + "; pass --allow-high-risk to acknowledge.")


def validate_recipe(path: Path, strict: bool = False, allow_high_risk: bool = False,
                    use_pyyaml: bool | None = None) -> tuple[list[str], list[str]]:
    """
    Returns (errors, warnings). errors is non-empty if the recipe is invalid.
    warnings are non-fatal unless strict=True (applied by the caller).
    """
    errors: list[str] = []
    warnings: list[str] = []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        errors.append(f"Cannot read file: {e}")
        return errors, warnings

    try:
        recipe = parse_recipe_text(text, use_pyyaml=use_pyyaml)
    except RecipeParseError as e:
        errors.append(f"YAML parse error: {e}")
        return errors, warnings

    if not recipe:
        errors.append("File parsed to empty dict — check YAML syntax")
        return errors, warnings

    for field in REQUIRED_FIELDS:
        if field not in recipe or not recipe[field]:
            errors.append(f"Missing required field: '{field}'")

    version = recipe.get("version", "")
    if version and not re.match(r'^\d+\.\d+(\.\d+)?$', str(version)):
        errors.append(f"'version' must be semver-like (e.g. 1.0 or 1.0.0), got: '{version}'")

    title = recipe.get("title", "")
    if title and len(str(title)) > 120:
        warnings.append(f"'title' is very long ({len(str(title))} chars); keep under 120")

    instructions = recipe.get("instructions", "")
    if instructions and len(str(instructions).split()) < 5:
        warnings.append("'instructions' appears too short; verify it is not a placeholder")

    for key in recipe:
        if key not in KNOWN_FIELDS:
            warnings.append(f"Unknown top-level field: '{key}' (known: {sorted(KNOWN_FIELDS)})")

    params = recipe.get("parameters")
    if params is not None:
        if not isinstance(params, list):
            errors.append("'parameters' must be a list of parameter objects")
        else:
            for idx, param in enumerate(params):
                if not isinstance(param, dict):
                    errors.append(f"parameters[{idx}] must be a mapping, got: {type(param).__name__}")
                    continue
                for req_key in sorted(PARAM_REQUIRED_KEYS):
                    if req_key not in param or param[req_key] in (None, ""):
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

    extensions = recipe.get("extensions")
    if extensions is not None:
        if not isinstance(extensions, list):
            errors.append("'extensions' must be a list of extension names or mappings")
        else:
            for idx, ext in enumerate(extensions):
                _check_extension(ext, idx, allow_high_risk, errors, warnings)

    activities = recipe.get("activities")
    if activities is not None and not isinstance(activities, list):
        errors.append("'activities' must be a list")

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Static validator for recipe blueprint YAML files (fails closed)."
    )
    parser.add_argument("targets", nargs="+", help="Recipe file(s) or directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument(
        "--allow-high-risk",
        action="store_true",
        help="Downgrade high-risk extension matches to warnings (pipe-to-shell stays an error)",
    )
    args = parser.parse_args(argv)

    paths: list[Path] = []
    for t in args.targets:
        paths.extend(_collect_paths(t))

    if not paths:
        print("No .yaml or .yml files found.", file=sys.stderr)
        return 1

    total_errors = 0
    total_warnings = 0

    for path in paths:
        errors, warnings = validate_recipe(path, strict=args.strict,
                                          allow_high_risk=args.allow_high_risk)
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
