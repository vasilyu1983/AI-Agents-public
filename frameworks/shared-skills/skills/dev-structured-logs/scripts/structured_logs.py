#!/usr/bin/env python3
"""Structured logs migration utility for Codex skill.

This script performs conservative, mostly line-based rewrites for:
- Legacy string-based ILogger calls to message-template logging
- CommandHandler method scope insertion
- Serilog File sink appsettings updates
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import fnmatch
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple


LOG_METHOD_RE = re.compile(
    r"(?P<prefix>\b(?P<logger>[A-Za-z_][A-Za-z0-9_]*)\s*\.\s*(?P<method>Log(?:Trace|Debug|Information|Warning|Error|Critical))\s*\()(?P<args>.*)\)\s*;\s*$"
)
STRING_LITERAL_RE = re.compile(r'^(?:@?"(?:""|[^\"])*"|\$@?".*"|@?\$".*")$', re.DOTALL)
FORMAT_INDEX_RE = re.compile(r"\{(\d+)(:[^}]*)?\}")
HANDLE_METHOD_RE = re.compile(r"^\s*public\s+.*\b(Handle|HandleAsync)\s*\((?P<params>[^)]*)\)")
IMPLEMENTS_COMMAND_HANDLER_RE = re.compile(r"ICommandHandler\s*<")
CS_PROJ_SERILOG_RE = re.compile(
    r'<PackageReference[^>]*Include="(?:Serilog(?:\.[^"]+)?|Sc\.Infrastructure\.Serilog)"',
    re.IGNORECASE,
)


DEFAULT_EXCLUDES = {
    "bin/**",
    "obj/**",
    "node_modules/**",
    "packages/**",
    ".git/**",
    ".idea/**",
    ".vs/**",
}


@dataclasses.dataclass
class ChangeEntry:
    file: str
    line: int
    original: str
    transformed: str
    risk_level: str
    reason: str


@dataclasses.dataclass
class FilePatch:
    rel_path: str
    original_text: str
    transformed_text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate .NET logs to structured logging")
    parser.add_argument("--path", required=True, help="Path to repository")
    parser.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--preview-file", help="Limit C# preview to a single file path")
    parser.add_argument("--backup-dir", help="Backup directory for --apply")
    parser.add_argument(
        "--enable-handler-scope",
        action="store_true",
        help="Enable CommandHandler BeginScope insertion (disabled by default)",
    )
    parser.add_argument("--handler-pattern", default="Handle|HandleAsync", help="Regex for handler methods")
    parser.add_argument("--log-framework", choices=["serilog", "microsoft", "auto"], default="auto")
    parser.add_argument("--exclude", action="append", default=[], help="Extra glob exclusion (repeatable)")
    parser.add_argument("--commit-msg", help="Optional commit message when applying")
    return parser.parse_args()


def to_pascal(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", name).strip()
    if not cleaned:
        return "Value"
    parts = [p for p in cleaned.split(" ") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "Value"


def infer_property_name(expr: str, idx: int) -> str:
    expr = expr.strip()
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr):
        return to_pascal(expr)
    tail = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", expr)
    if tail:
        return to_pascal(tail.group(1))
    return f"Value{idx}"


def split_top_level(text: str, sep: str) -> List[str]:
    out: List[str] = []
    buf: List[str] = []
    depth_paren = depth_brack = depth_brace = 0
    in_string = False
    string_char = ""
    escape = False
    for ch in text:
        if in_string:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == string_char:
                in_string = False
            continue

        if ch in ('"', "'"):
            in_string = True
            string_char = ch
            buf.append(ch)
            continue

        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "[":
            depth_brack += 1
        elif ch == "]":
            depth_brack -= 1
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1

        if ch == sep and depth_paren == 0 and depth_brack == 0 and depth_brace == 0:
            out.append("".join(buf).strip())
            buf = []
            continue

        buf.append(ch)

    if buf:
        out.append("".join(buf).strip())
    return out


def unquote_cs_string(value: str) -> str:
    value = value.strip()
    if value.startswith('@"') and value.endswith('"'):
        return value[2:-1].replace('""', '"')
    if value.startswith('"') and value.endswith('"'):
        inner = value[1:-1]
        return bytes(inner, "utf-8").decode("unicode_escape")
    return value


def quote_cs_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def has_potential_side_effect(expr: str) -> bool:
    expr = expr.strip()
    if re.search(r"\bnew\s+[A-Za-z_]", expr):
        return True
    if re.search(r"[A-Za-z_][A-Za-z0-9_]*\s*\(", expr):
        return True
    if "++" in expr or "--" in expr:
        return True
    if "+=" in expr or "-=" in expr or "*=" in expr or "/=" in expr:
        return True
    return False


def convert_interpolation(message_expr: str) -> Optional[Tuple[str, List[str]]]:
    stripped = message_expr.strip()
    if not stripped.startswith('$"') and not stripped.startswith('$@"') and not stripped.startswith('@$"'):
        return None
    inner = stripped[stripped.find('"') + 1 : -1]
    args: List[str] = []
    out: List[str] = []

    def split_interpolation_hole(content: str) -> Tuple[str, str]:
        # Split "{expr[,alignment][:format]}" into expression and suffix, while
        # treating ternary ':' as part of the expression.
        in_string = False
        string_char = ""
        escape = False
        depth_paren = depth_brack = depth_brace = 0
        ternary_depth = 0
        split_idx: Optional[int] = None
        i = 0
        while i < len(content):
            ch = content[i]
            nxt = content[i + 1] if i + 1 < len(content) else ""
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == string_char:
                    in_string = False
                i += 1
                continue

            if ch in ('"', "'"):
                in_string = True
                string_char = ch
                i += 1
                continue

            if ch == "(":
                depth_paren += 1
            elif ch == ")" and depth_paren > 0:
                depth_paren -= 1
            elif ch == "[":
                depth_brack += 1
            elif ch == "]" and depth_brack > 0:
                depth_brack -= 1
            elif ch == "{":
                depth_brace += 1
            elif ch == "}" and depth_brace > 0:
                depth_brace -= 1
            elif depth_paren == 0 and depth_brack == 0 and depth_brace == 0:
                if ch == "?" and nxt != "?":
                    ternary_depth += 1
                elif ch == ":" and ternary_depth > 0:
                    ternary_depth -= 1
                elif ternary_depth == 0 and ch in {",", ":"}:
                    split_idx = i
                    break
            i += 1

        if split_idx is None:
            return content.strip(), ""
        return content[:split_idx].strip(), content[split_idx:]

    i = 0
    while i < len(inner):
        ch = inner[i]
        nxt = inner[i + 1] if i + 1 < len(inner) else ""
        if ch == "{" and nxt == "{":
            out.append("{")
            i += 2
            continue
        if ch == "}" and nxt == "}":
            out.append("}")
            i += 2
            continue
        if ch != "{":
            out.append(ch)
            i += 1
            continue

        # Parse interpolation hole.
        j = i + 1
        in_string = False
        string_char = ""
        escape = False
        depth_paren = depth_brack = depth_brace = 0
        while j < len(inner):
            c = inner[j]
            if in_string:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == string_char:
                    in_string = False
                j += 1
                continue

            if c in ('"', "'"):
                in_string = True
                string_char = c
                j += 1
                continue

            if c == "(":
                depth_paren += 1
            elif c == ")" and depth_paren > 0:
                depth_paren -= 1
            elif c == "[":
                depth_brack += 1
            elif c == "]" and depth_brack > 0:
                depth_brack -= 1
            elif c == "{":
                depth_brace += 1
            elif c == "}" and depth_brace > 0:
                depth_brace -= 1
            elif c == "}" and depth_paren == 0 and depth_brack == 0 and depth_brace == 0:
                break
            j += 1

        if j >= len(inner) or inner[j] != "}":
            return None

        hole = inner[i + 1 : j]
        expr, suffix = split_interpolation_hole(hole)
        if not expr:
            return None
        prop = f"Value{len(args)}" if "?" in expr else infer_property_name(expr, len(args))
        args.append(expr)
        out.append("{" + prop + suffix + "}")
        i = j + 1

    template = "".join(out)
    return quote_cs_string(template), args


def convert_string_format(message_expr: str) -> Optional[Tuple[str, List[str]]]:
    m = re.match(r"^String\.Format\s*\((.*)\)$", message_expr.strip(), flags=re.DOTALL)
    if not m:
        return None
    parts = split_top_level(m.group(1), ",")
    if len(parts) < 2:
        return None
    format_literal = parts[0].strip()
    if not STRING_LITERAL_RE.match(format_literal):
        return None
    fmt = unquote_cs_string(format_literal)
    args = [p.strip() for p in parts[1:]]

    def repl(match: re.Match[str]) -> str:
        idx = int(match.group(1))
        if idx >= len(args):
            return match.group(0)
        prop = infer_property_name(args[idx], idx)
        return "{" + prop + "}"

    return quote_cs_string(FORMAT_INDEX_RE.sub(repl, fmt)), args


def convert_concat(message_expr: str) -> Optional[Tuple[str, List[str]]]:
    pieces = split_top_level(message_expr, "+")
    if len(pieces) < 2:
        return None
    template_parts: List[str] = []
    args: List[str] = []
    has_string = False

    for piece in pieces:
        p = piece.strip()
        if STRING_LITERAL_RE.match(p):
            has_string = True
            template_parts.append(unquote_cs_string(p))
        else:
            prop = infer_property_name(p, len(args))
            template_parts.append("{" + prop + "}")
            args.append(p)

    if not has_string:
        return None

    template = "".join(template_parts)
    return quote_cs_string(template), args


def transform_message_expression(message_expr: str) -> Optional[Tuple[str, List[str], bool]]:
    converted = convert_interpolation(message_expr)
    if converted:
        template, args = converted
        side_effect = any(has_potential_side_effect(a) for a in args)
        return template, args, side_effect

    converted = convert_string_format(message_expr)
    if converted:
        template, args = converted
        side_effect = any(has_potential_side_effect(a) for a in args)
        return template, args, side_effect

    converted = convert_concat(message_expr)
    if converted:
        template, args = converted
        side_effect = any(has_potential_side_effect(a) for a in args)
        return template, args, side_effect

    return None


def split_logger_args(arg_text: str) -> List[str]:
    return split_top_level(arg_text, ",")


def rewrite_log_calls(text: str, rel_path: str) -> Tuple[str, List[ChangeEntry]]:
    lines = text.splitlines(keepends=True)
    out: List[str] = []
    changes: List[ChangeEntry] = []
    tmp_counter = 0

    for line_no, line in enumerate(lines, start=1):
        match = LOG_METHOD_RE.search(line.rstrip("\r\n"))
        if not match:
            out.append(line)
            continue

        indent = re.match(r"^\s*", line).group(0)
        args = split_logger_args(match.group("args"))
        if not args:
            out.append(line)
            continue

        msg_idx = 0
        exception_arg: Optional[str] = None
        first = args[0].strip()
        if not STRING_LITERAL_RE.match(first) and not first.startswith("$") and len(args) > 1:
            msg_idx = 1
            exception_arg = first

        original_msg = args[msg_idx].strip()
        transformed = transform_message_expression(original_msg)
        if not transformed:
            out.append(line)
            continue

        template, msg_args, has_side_effects = transformed

        prelude_lines: List[str] = []
        safe_args: List[str] = []
        for arg in msg_args:
            if has_potential_side_effect(arg):
                tmp_name = f"__tmp{tmp_counter}"
                tmp_counter += 1
                prelude_lines.append(f"{indent}var {tmp_name} = {arg};\n")
                safe_args.append(tmp_name)
            else:
                safe_args.append(arg)

        rebuilt_args: List[str] = []
        if exception_arg is not None:
            rebuilt_args.append(exception_arg)
        rebuilt_args.append(template)
        rebuilt_args.extend(safe_args)

        method = match.group("method")
        logger_name = match.group("logger")
        new_line = f"{indent}{logger_name}.{method}({', '.join(rebuilt_args)});\n"

        out.extend(prelude_lines)
        out.append(new_line)

        risk = "medium" if has_side_effects else "low"
        reason = (
            "Side-effect expression extracted to temp variable; requires manual review"
            if has_side_effects
            else "Converted string-based log message to structured template"
        )
        changes.append(
            ChangeEntry(
                file=rel_path,
                line=line_no,
                original=line.rstrip("\r\n"),
                transformed=("".join(prelude_lines) + new_line).rstrip("\r\n"),
                risk_level=risk,
                reason=reason,
            )
        )

    return "".join(out), changes


def get_method_param(params_text: str) -> Optional[Tuple[str, str]]:
    parts = split_top_level(params_text, ",")
    if not parts:
        return None
    first = parts[0].strip()
    # Handles "CreateOrder command" and "CreateOrder command, CancellationToken ct"
    m = re.match(r"(?P<type>[A-Za-z_][A-Za-z0-9_<>.?]*)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)", first)
    if not m:
        return None
    return m.group("type"), m.group("name")


def property_exists_nearby(lines: List[str], start_idx: int, end_idx: int, param_name: str, prop: str) -> bool:
    needle = re.compile(rf"\b{re.escape(param_name)}\s*\?*\.\s*{re.escape(prop)}\b")
    for i in range(start_idx, min(end_idx, len(lines))):
        if needle.search(lines[i]):
            return True
    return False


def rewrite_handler_scopes(text: str, rel_path: str, handler_pattern: str) -> Tuple[str, List[ChangeEntry]]:
    lines = text.splitlines(keepends=True)
    out = list(lines)
    changes: List[ChangeEntry] = []

    try:
        name_pattern = re.compile(handler_pattern)
    except re.error:
        name_pattern = re.compile("Handle|HandleAsync")

    has_interface = bool(IMPLEMENTS_COMMAND_HANDLER_RE.search(text))
    idx = 0
    while idx < len(out):
        line = out[idx]
        m = HANDLE_METHOD_RE.match(line)
        if not m:
            idx += 1
            continue
        method_name = m.group(1)
        if not name_pattern.search(method_name):
            idx += 1
            continue

        param = get_method_param(m.group("params"))
        if not param:
            idx += 1
            continue
        command_type, command_name = param

        if not has_interface and not command_type.lower().endswith("command"):
            idx += 1
            continue

        # Locate method open brace.
        brace_idx = idx
        while brace_idx < len(out) and "{" not in out[brace_idx]:
            brace_idx += 1
        if brace_idx >= len(out):
            break

        lookahead = "".join(out[brace_idx : min(brace_idx + 20, len(out))])
        if "BeginScope" in lookahead and "__scopeItems" in lookahead:
            idx = brace_idx + 1
            continue

        base_indent = re.match(r"^\s*", out[brace_idx]).group(0)
        body_indent = base_indent + "    "

        props = ["UserId", "TransactionId", "TransferId", "VerificationId", "SessionId", "Id"]
        detected_props = [p for p in props if property_exists_nearby(out, brace_idx, brace_idx + 120, command_name, p)]
        if not detected_props:
            idx = brace_idx + 1
            continue

        snippet: List[str] = [
            f"{body_indent}var __scopeItems = new Dictionary<string, object>\n",
            f"{body_indent}{{\n",
        ]
        for prop in detected_props:
            snippet.append(f'{body_indent}    ["{prop}"] = {command_name}.{prop},\n')
        snippet.append(f"{body_indent}}};\n")
        snippet.append(f"{body_indent}using var _scope = _logger.BeginScope(__scopeItems);\n")

        insert_at = brace_idx + 1
        out[insert_at:insert_at] = snippet
        changes.append(
            ChangeEntry(
                file=rel_path,
                line=brace_idx + 2,
                original="",
                transformed="".join(snippet).rstrip("\r\n"),
                risk_level="medium",
                reason="Inserted CommandHandler scope with command key properties. Verify logger variable and command properties",
            )
        )

        idx = insert_at + len(snippet)

    return "".join(out), changes


def strip_json_comments(text: str) -> str:
    # Conservative comment stripper for // and /* */ outside strings.
    out: List[str] = []
    i = 0
    in_string = False
    escape = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == "/" and nxt == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def detect_serilog(repo: pathlib.Path, excludes: List[str]) -> bool:
    for path in repo.rglob("*.csproj"):
        if is_excluded(path, repo, excludes):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if CS_PROJ_SERILOG_RE.search(text):
            return True
    return False


def update_serilog_json(text: str, rel_path: str) -> Tuple[str, List[ChangeEntry]]:
    cleaned = strip_json_comments(text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return text, [
            ChangeEntry(
                file=rel_path,
                line=1,
                original="<invalid json>",
                transformed="<unchanged>",
                risk_level="high",
                reason="Unable to parse JSON/JSONC safely; skipped",
            )
        ]

    serilog = data.get("Serilog")
    if not isinstance(serilog, dict):
        return text, []
    def iter_file_sink_args(node):
        if isinstance(node, dict):
            name = node.get("Name")
            args = node.get("Args")
            if isinstance(name, str) and name.lower() == "file" and isinstance(args, dict):
                yield args
            for value in node.values():
                yield from iter_file_sink_args(value)
        elif isinstance(node, list):
            for item in node:
                yield from iter_file_sink_args(item)

    changed = False
    entries: List[ChangeEntry] = []

    for args in iter_file_sink_args(serilog):

        old_path = args.get("path")
        if isinstance(old_path, str):
            new_path = old_path
            lower_path = old_path.lower()
            if lower_path.endswith(".debug.json"):
                new_path = old_path
            elif lower_path.endswith(".debug.log"):
                new_path = f"{old_path[:-10]}.debug.json"
            elif lower_path.endswith(".log.debug"):
                new_path = f"{old_path[:-10]}.debug.json"
            elif lower_path.endswith(".debug"):
                base = old_path[:-6]
                if base.lower().endswith(".debug.json"):
                    new_path = old_path
                else:
                    new_path = f"{base}.debug.json"
            elif lower_path.endswith(".json"):
                new_path = old_path
            elif lower_path.endswith(".log"):
                new_path = f"{old_path[:-4]}.json"
            else:
                root, ext = os.path.splitext(old_path)
                new_path = f"{root}.json" if ext else f"{old_path}.json"

            if new_path != old_path:
                args["path"] = new_path
                changed = True
                entries.append(
                    ChangeEntry(
                        file=rel_path,
                        line=1,
                        original=f"path: {old_path}",
                        transformed=f"path: {new_path}",
                        risk_level="low",
                        reason="Updated Serilog File sink path to .json/.debug.json convention",
                    )
                )

        formatter = "Sc.Infrastructure.Serilog.CustomJsonFormatter, Sc.Infrastructure.Serilog"
        if args.get("formatter") != formatter:
            old = args.get("formatter")
            args["formatter"] = formatter
            changed = True
            entries.append(
                ChangeEntry(
                    file=rel_path,
                    line=1,
                    original=f"formatter: {old}",
                    transformed=f"formatter: {formatter}",
                    risk_level="low",
                    reason="Enforced custom JSON formatter for File sink",
                )
            )

        if "outputTemplate" in args:
            old_template = args.get("outputTemplate")
            del args["outputTemplate"]
            changed = True
            entries.append(
                ChangeEntry(
                    file=rel_path,
                    line=1,
                    original=f"outputTemplate: {old_template}",
                    transformed="outputTemplate: <removed>",
                    risk_level="low",
                    reason="Removed outputTemplate for JSON formatter compatibility",
                )
            )

    if not changed:
        return text, []

    new_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return new_text, entries


def is_excluded(path: pathlib.Path, root: pathlib.Path, excludes: List[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    for pat in excludes:
        if fnmatch.fnmatch(rel, pat):
            return True
    return False


def collect_files(repo: pathlib.Path, preview_file: Optional[str], excludes: List[str]) -> Tuple[List[pathlib.Path], List[pathlib.Path]]:
    cs_files: List[pathlib.Path] = []
    json_files: List[pathlib.Path] = []

    if preview_file:
        target = (repo / preview_file).resolve() if not os.path.isabs(preview_file) else pathlib.Path(preview_file)
        if target.suffix.lower() == ".cs" and target.exists():
            cs_files = [target]
        return cs_files, json_files

    for path in repo.rglob("*.cs"):
        if is_excluded(path, repo, excludes):
            continue
        cs_files.append(path)

    for path in repo.rglob("appsettings.json"):
        if is_excluded(path, repo, excludes):
            continue
        json_files.append(path)

    return cs_files, json_files


def build_unified_diff(patches: Iterable[FilePatch]) -> str:
    chunks: List[str] = []
    for patch in patches:
        if patch.original_text == patch.transformed_text:
            continue
        diff = difflib.unified_diff(
            patch.original_text.splitlines(keepends=True),
            patch.transformed_text.splitlines(keepends=True),
            fromfile=patch.rel_path,
            tofile=patch.rel_path,
        )
        chunks.extend(diff)
    return "".join(chunks)


def backup_and_write(repo: pathlib.Path, patches: List[FilePatch], backup_dir: pathlib.Path) -> List[pathlib.Path]:
    changed_paths: List[pathlib.Path] = []
    backup_dir.mkdir(parents=True, exist_ok=True)

    for p in patches:
        if p.original_text == p.transformed_text:
            continue
        src = repo / p.rel_path
        dst = backup_dir / p.rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        src.write_text(p.transformed_text, encoding="utf-8")
        changed_paths.append(src)
    return changed_paths


def maybe_commit(repo: pathlib.Path, changed_paths: List[pathlib.Path], message: str) -> None:
    if not changed_paths:
        return
    rels = [str(p.relative_to(repo)).replace("\\", "/") for p in changed_paths]
    subprocess.run(["git", "-C", str(repo), "add", "--", *rels], check=False)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", message], check=False)


def first_diff_line(original: str, updated: str) -> int:
    o = original.splitlines()
    n = updated.splitlines()
    m = min(len(o), len(n))
    for i in range(m):
        if o[i] != n[i]:
            return i + 1
    if len(o) != len(n):
        return m + 1
    return 1


def main() -> int:
    args = parse_args()
    if args.apply and args.dry_run:
        print("Cannot use --apply and --dry-run together", file=sys.stderr)
        return 2

    dry_run = not args.apply if not args.dry_run else True
    repo = pathlib.Path(args.path).resolve()
    if not repo.exists() or not repo.is_dir():
        print(f"Repository path does not exist: {repo}", file=sys.stderr)
        return 2

    excludes = sorted(set(DEFAULT_EXCLUDES | set(args.exclude)))
    cs_files, json_files = collect_files(repo, args.preview_file, excludes)

    patches: List[FilePatch] = []
    report: List[ChangeEntry] = []

    # Part 1 + 2 (C#)
    for path in cs_files:
        rel = path.relative_to(repo).as_posix()
        original = path.read_text(encoding="utf-8", errors="ignore")

        transformed, part1_changes = rewrite_log_calls(original, rel)
        transformed2 = transformed
        part2_changes: List[ChangeEntry] = []
        if args.enable_handler_scope:
            transformed2, part2_changes = rewrite_handler_scopes(transformed, rel, args.handler_pattern)

        if transformed2 != original:
            patches.append(FilePatch(rel_path=rel, original_text=original, transformed_text=transformed2))
            if transformed2 != transformed:
                line = first_diff_line(transformed, transformed2)
                report.append(
                    ChangeEntry(
                        file=rel,
                        line=line,
                        original="<handler body>",
                        transformed="<scope inserted>",
                        risk_level="medium",
                        reason="CommandHandler scope insertion",
                    )
                )
        report.extend(part1_changes)
        report.extend(part2_changes)

    # Part 3 (Serilog appsettings)
    serilog_enabled = detect_serilog(repo, excludes)
    if serilog_enabled:
        for path in json_files:
            rel = path.relative_to(repo).as_posix()
            original = path.read_text(encoding="utf-8", errors="ignore")
            updated, entries = update_serilog_json(original, rel)
            report.extend(entries)
            if updated != original:
                patches.append(FilePatch(rel_path=rel, original_text=original, transformed_text=updated))

    diff_text = build_unified_diff(patches)
    patch_path = repo / "patch.diff"
    preview_path = repo / "preview-report.json"
    patch_path.write_text(diff_text, encoding="utf-8")
    preview_path.write_text(
        json.dumps([dataclasses.asdict(c) for c in report], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    changed_count = sum(1 for p in patches if p.original_text != p.transformed_text)
    print(f"Mode: {'dry-run' if dry_run else 'apply'}")
    print(f"C# files scanned: {len(cs_files)}")
    print(f"JSON files scanned: {len(json_files) if serilog_enabled else 0}")
    print(f"Files changed: {changed_count}")
    print(f"Patch: {patch_path}")
    print(f"Preview report: {preview_path}")

    if not dry_run:
        backup_default = pathlib.Path(".codex/skills/structured-logs/backups")
        backup_dir = pathlib.Path(args.backup_dir).resolve() if args.backup_dir else backup_default.resolve()
        changed_paths = backup_and_write(repo, patches, backup_dir)
        print(f"Backups: {backup_dir}")
        if args.commit_msg:
            maybe_commit(repo, changed_paths, args.commit_msg)
            print("Commit attempted")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
