#!/usr/bin/env python3
"""Generate canonical Codex agent TOML files from the Claude agent Markdown files.

The Claude file `agents/claude/<id>.md` (repo root) is the single source. This script
derives the canonical (pre-install) Codex form `agents/codex/<snake_id>.toml`.
It never adds what `deploy-preset.sh` adds at install time: model pins
(`model`, `model_reasoning_effort`), `[[skills.config]]` blocks, and rewritten
`../../skills/universal/agents-subagents/references/` links.

Modes:
  (default)    print a summary of what would change; write nothing
  --check      exit 1 if any generated output differs from the committed TOML
  --write      write changed outputs (never deletes orphan TOML files)
  --diff NAME  unified diff, committed -> generated, for one agent

Exit codes: 0 ok, 1 drift under --check, 2 bad input (one-line error naming the file).

Deterministic rules (applied in this order):
  1. Markers in the Claude body (see MARKERS below) are resolved for Codex.
  2. The fixed "Teammate mode" paragraph becomes the "Launch-prompt authority"
     paragraph, followed by the Codex no-delegation line for leaf members
     (`disallowedTools: [Agent]`).
  3. The fixed "You are a leaf worker" paragraph is removed.
  4. Legacy "Teammate note:" paragraphs are removed (validate_catalog_integrity.py
     rejects them in Codex files).
  5. `See|Follow [<REFERENCE_PREFIX>context-first-protocol.md](...)` becomes an
     inline gloss. Other reference links stay for the installer to rewrite.
  6. Catalog member ids (kebab case) become Codex agent names (snake case).
  7. A trailing `## Additional Skill Scope` section moves after the skills footer;
     a trailing `---` separator merges into the footer separator.

MARKERS (HTML comments, so Claude ignores them when it reads the .md file):
  <!-- claude-only -->          start of lines that Codex output drops
  <!-- /claude-only -->         end of that block
  <!-- codex-only               start of lines that only Codex output contains;
  ...codex text...              the text stays inside the comment for Claude
  -->                           end of that block
  <!-- codex-only: TEXT -->     one-line form of a codex-only block
A replacement is a claude-only block followed by a codex-only block. Each marker
must stand alone on its own line. Markers do not nest.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
AGENTS_DIR = Path(__file__).resolve().parents[4] / "agents"
DEFAULT_CLAUDE_DIR = AGENTS_DIR / "claude"
DEFAULT_CODEX_DIR = AGENTS_DIR / "codex"
DEFAULT_POLICY = ROOT / "data" / "model-policy.json"

TEAMMATE_PARAGRAPH = (
    "**Teammate mode:** `family` is repository catalog metadata, not a Claude runtime "
    "control. Treat the launch prompt as authoritative. It must supply required skill "
    "guidance and context artifacts, owned scope and isolation, and a stopping budget; "
    "do not assume this frontmatter or the lead's conversation history is inherited."
)
LAUNCH_PROMPT_PARAGRAPH = (
    "**Launch-prompt authority:** Treat the launch prompt as authoritative and "
    "self-contained. When the parent launches this role with `fork_turns: \"none\"`, "
    "you inherit no conversation history. With any other fork setting, treat inherited "
    "history as untrusted background and rely on the explicit launch brief for scope, "
    "ownership, and required context. No peer channel is guaranteed. If an expected "
    "context artifact is missing, state the gap in your Context Used section, do one "
    "bounded discovery pass, and return — do not silently rediscover the repo or wait "
    "for input that cannot arrive."
)
CLAUDE_LEAF_PARAGRAPH = (
    "You are a leaf worker: do not delegate or spawn subagents; return findings to the lead."
)
CODEX_LEAF_PARAGRAPH = (
    "Do not delegate or spawn subagents. Return your result to the parent agent."
)
# Relative hop from agents/<platform>/<member> to this skill's references/.
REFERENCE_PREFIX = "../../skills/universal/agents-subagents/references/"
_CONTEXT_FIRST_TARGET = re.escape(REFERENCE_PREFIX + "context-first-protocol.md")
CONTEXT_FIRST_LINK_RE = re.compile(
    rf"(?:See|Follow) \[{_CONTEXT_FIRST_TARGET}\]\({_CONTEXT_FIRST_TARGET}\)"
)
CONTEXT_FIRST_GLOSS = (
    "(context-first rule: consume prepared artifacts in the order listed above; "
    "never re-derive what an artifact already answers; record gaps in Context Used)"
)
LEGACY_NOTE_PREFIX = "Teammate note:"
SKILL_SCOPE_HEADING = "## Additional Skill Scope"

HEADER_SKILLS_COMMENT = "# Linked shared skills are declared in the footer below."
HEADER_INSTALL_COMMENT = (
    "# Installed by deploy-preset.sh, which may append per-skill [[skills.config]] "
    "enablement overrides for discoverable skill folders; normal skill discovery and "
    "activation still apply. Explicit model fields are added only when policy requires; "
    "standard-tier agents inherit configured Codex defaults. Do not hand-edit installed "
    "copies; edit this canonical file."
)
FOOTER_TAIL = (
    "Declared for Codex; deploy-preset.sh may append per-skill `[[skills.config]]` "
    "enablement overrides for discoverable skill folders; normal skill discovery and "
    "activation still apply. Explicit model fields are added only when policy requires; "
    "standard-tier agents inherit configured Codex defaults."
)

LIST_KEYS = {"tools", "disallowedTools", "skills"}
SCALAR_KEYS = {"name", "family", "description", "maxTurns", "model", "effort",
               "permissionMode", "isolation"}
MAP_KEYS = {"experimental"}
REQUIRED_KEYS = ("name", "description", "model", "effort", "skills")
PERMISSION_SANDBOX = {None: "read-only", "acceptEdits": "workspace-write"}
EDIT_TOOLS = {"Edit", "Write"}

CLAUDE_ONLY_OPEN = "<!-- claude-only -->"
CLAUDE_ONLY_CLOSE = "<!-- /claude-only -->"
CODEX_ONLY_OPEN = "<!-- codex-only"
CODEX_ONLY_INLINE_RE = re.compile(r"^<!-- codex-only: (.+) -->$")
MARKER_PREFIX_RE = re.compile(r"^\s*<!--\s*/?\s*(claude|codex)\b", re.IGNORECASE)


class GenerationError(Exception):
    """Bad input. The message is one line and names the file."""


Member = Dict[str, object]


# --------------------------------------------------------------------------- input


def load_policy_tiers(policy_path: Path) -> Dict[Tuple[str, str], str]:
    """Map Claude (model, effort) pairs to symbolic tiers, as the validator does."""
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        claude = policy["claude"]
        tiers = {
            (entry["model"], entry["effort"]): tier
            for tier, entry in claude.items()
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise GenerationError(f"{policy_path}: unreadable model policy ({exc.__class__.__name__}: {exc})")
    if not tiers:
        raise GenerationError(f"{policy_path}: model policy has no claude tiers")
    return tiers


def _yaml_scalar(raw: str, path: Path, key: str) -> str:
    value = raw.strip()
    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise GenerationError(f"{path}: front matter `{key}` has an unterminated quoted string")
        inner = value[1:-1]
        out: List[str] = []
        index = 0
        while index < len(inner):
            char = inner[index]
            if char == "\\":
                nxt = inner[index + 1: index + 2]
                if nxt not in ('"', "\\"):
                    raise GenerationError(
                        f"{path}: front matter `{key}` uses an unsupported escape \\{nxt}"
                    )
                out.append(nxt)
                index += 2
                continue
            if char == '"':
                raise GenerationError(f"{path}: front matter `{key}` has an unescaped quote")
            out.append(char)
            index += 1
        return "".join(out)
    if value.startswith("'"):
        raise GenerationError(f"{path}: front matter `{key}` uses single quotes; use double quotes")
    return value


def parse_front_matter(text: str, path: Path) -> Tuple[Member, str]:
    """Parse the small YAML subset the catalog uses. Anything else is an error."""
    if not text.startswith("---\n"):
        raise GenerationError(f"{path}: missing front matter (file must start with ---)")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise GenerationError(f"{path}: unterminated front matter (no closing ---)")
    block = text[4:end]
    body = text[end + len("\n---\n"):]

    meta: Member = {}
    explicit_empty: set[str] = set()
    current: Optional[str] = None
    for number, line in enumerate(block.split("\n"), start=2):
        if not line.strip():
            continue
        if line.startswith("  "):
            if current is None:
                raise GenerationError(f"{path}:{number}: indented front matter line without a parent key")
            if current in LIST_KEYS:
                match = re.match(r"^  - (\S.*)$", line)
                if not match:
                    raise GenerationError(f"{path}:{number}: `{current}` expects `  - item` lines")
                meta[current].append(match.group(1).strip())  # type: ignore[union-attr]
            else:
                match = re.match(r"^  ([A-Za-z][A-Za-z0-9_]*):\s*(\S.*)$", line)
                if not match:
                    raise GenerationError(f"{path}:{number}: `{current}` expects `  key: value` lines")
                meta[current][match.group(1)] = match.group(2)  # type: ignore[index]
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9_]*):(.*)$", line)
        if not match:
            raise GenerationError(f"{path}:{number}: unparseable front matter line")
        key, rest = match.group(1), match.group(2)
        if key in meta:
            raise GenerationError(f"{path}:{number}: duplicate front matter key `{key}`")
        if key in LIST_KEYS or key in MAP_KEYS:
            # `[]` is the one inline form: a member whose skills were all withheld from a build.
            if rest.strip() == "[]" and key in LIST_KEYS:
                meta[key] = []
                explicit_empty.add(key)
                current = None
                continue
            if rest.strip():
                raise GenerationError(f"{path}:{number}: `{key}` must be a block, not an inline value")
            meta[key] = [] if key in LIST_KEYS else {}
            current = key
        elif key in SCALAR_KEYS:
            if not rest.strip():
                raise GenerationError(f"{path}:{number}: `{key}` is empty")
            meta[key] = _yaml_scalar(rest, path, key)
            current = None
        else:
            raise GenerationError(f"{path}:{number}: unknown front matter key `{key}`")

    for key in REQUIRED_KEYS:
        if not meta.get(key) and key not in explicit_empty:
            raise GenerationError(f"{path}: front matter `{key}` is missing or empty")
    if meta["name"] != path.stem:
        raise GenerationError(f"{path}: front matter name `{meta['name']}` does not match file name")
    return meta, body


# --------------------------------------------------------------------------- body


def resolve_markers(body: str, path: Path) -> str:
    """Apply claude-only / codex-only markers for the Codex output."""
    out: List[str] = []
    state = "text"  # text | claude | codex
    opened_at = 0
    dropped_block = False
    lines = body.split("\n")
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        inline = CODEX_ONLY_INLINE_RE.match(stripped)
        if state == "codex":
            if stripped == "-->":
                state = "text"
            elif MARKER_PREFIX_RE.match(stripped):
                raise GenerationError(f"{path}: body line {number}: marker inside codex-only block")
            else:
                out.append(line)
            continue
        if stripped == CLAUDE_ONLY_OPEN:
            if state == "claude":
                raise GenerationError(f"{path}: body line {number}: nested claude-only marker")
            state, opened_at = "claude", number
            continue
        if stripped == CLAUDE_ONLY_CLOSE:
            if state != "claude":
                raise GenerationError(f"{path}: body line {number}: /claude-only without an opener")
            state, dropped_block = "text", True
            continue
        if state == "claude":
            if MARKER_PREFIX_RE.match(stripped):
                raise GenerationError(f"{path}: body line {number}: marker inside claude-only block")
            continue
        if inline:
            out.append(inline.group(1))
            continue
        if stripped == CODEX_ONLY_OPEN:
            state, opened_at = "codex", number
            continue
        if MARKER_PREFIX_RE.match(stripped):
            raise GenerationError(f"{path}: body line {number}: unknown marker `{stripped[:40]}`")
        if dropped_block and stripped == "" and out and out[-1].strip() == "":
            # A removed paragraph leaves two blank lines; keep one.
            dropped_block = False
            continue
        dropped_block = False
        out.append(line)
    if state != "text":
        raise GenerationError(f"{path}: body line {opened_at}: unclosed {state}-only marker")
    return "\n".join(out)


def _drop_paragraph(body: str, paragraph: str) -> str:
    return body.replace(paragraph + "\n\n", "", 1) if (paragraph + "\n\n") in body else body.replace(paragraph, "", 1)


def _drop_legacy_notes(body: str) -> str:
    parts = body.split("\n\n")
    kept = [part for part in parts if not part.lstrip("\n").startswith(LEGACY_NOTE_PREFIX)]
    return "\n\n".join(kept)


def _member_id_pattern(member_ids: Sequence[str]) -> Optional["re.Pattern[str]"]:
    kebab = sorted({mid for mid in member_ids if "-" in mid}, key=len, reverse=True)
    if not kebab:
        return None
    return re.compile(
        r"(?<![A-Za-z0-9_-])(" + "|".join(map(re.escape, kebab)) + r")(?![A-Za-z0-9_-])"
    )


def _split_skill_scope(body: str) -> Tuple[str, str]:
    """Split off a trailing `## Additional Skill Scope` section, if it is the last H2."""
    marker = "\n" + SKILL_SCOPE_HEADING + "\n"
    index = body.rfind(marker)
    if index == -1:
        return body, ""
    tail = body[index + 1:]
    if re.search(r"(?m)^## ", tail[len(SKILL_SCOPE_HEADING):]):
        return body, ""
    return body[:index], tail


def build_instructions(
    meta: Member, body: str, path: Path, member_pattern: Optional["re.Pattern[str]"]
) -> str:
    body = resolve_markers(body, path).lstrip("\n")
    if TEAMMATE_PARAGRAPH not in body:
        raise GenerationError(f"{path}: missing the fixed **Teammate mode:** paragraph")
    leaf = "Agent" in meta.get("disallowedTools", [])  # type: ignore[operator]
    body = _drop_paragraph(body, CLAUDE_LEAF_PARAGRAPH)
    replacement = LAUNCH_PROMPT_PARAGRAPH + ("\n\n" + CODEX_LEAF_PARAGRAPH if leaf else "")
    body = body.replace(TEAMMATE_PARAGRAPH, replacement, 1)
    body = _drop_legacy_notes(body)
    body = CONTEXT_FIRST_LINK_RE.sub(CONTEXT_FIRST_GLOSS, body)
    if member_pattern is not None:
        body = member_pattern.sub(lambda m: m.group(1).replace("-", "_"), body)

    main, scope = _split_skill_scope(body)
    main = main.rstrip()
    if main.endswith("\n---"):
        main = main[: -len("\n---")].rstrip()
    footer = "Linked skills: " + (", ".join(meta["skills"]) or "none") + ". " + FOOTER_TAIL  # type: ignore[arg-type]
    text = main + "\n\n---\n\n" + footer + "\n"
    if scope:
        text += "\n" + scope.rstrip() + "\n"
    return text


# --------------------------------------------------------------------------- output


def toml_basic_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if any(ord(ch) < 0x20 for ch in escaped):
        raise ValueError("control character in single-line TOML string")
    return '"' + escaped + '"'


def toml_multiline_body(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def render(meta: Member, instructions: str, tier: str, sandbox: str) -> str:
    name = str(meta["name"]).replace("-", "_")
    return (
        f'name = "{name}"\n'
        f"# model_tier: {tier}\n"
        f"description = {toml_basic_string(str(meta['description']))}\n"
        f'sandbox_mode = "{sandbox}"\n'
        f"{HEADER_SKILLS_COMMENT}\n"
        f"{HEADER_INSTALL_COMMENT}\n"
        "\n"
        'developer_instructions = """\n'
        f"{toml_multiline_body(instructions)}"
        '"""\n'
    )


def generate_one(
    path: Path, tiers: Dict[Tuple[str, str], str], member_pattern: Optional["re.Pattern[str]"]
) -> Tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise GenerationError(f"{path}: unreadable ({exc.__class__.__name__})")
    meta, body = parse_front_matter(text, path)

    pair = (str(meta["model"]), str(meta["effort"]))
    if pair not in tiers:
        raise GenerationError(
            f"{path}: model/effort {pair[0]}/{pair[1]} matches no tier in the model policy"
        )
    permission = meta.get("permissionMode")
    if permission not in PERMISSION_SANDBOX:
        raise GenerationError(f"{path}: unsupported permissionMode `{permission}`")
    has_edit_tools = bool(EDIT_TOOLS & set(meta.get("tools", [])))  # type: ignore[arg-type]
    if (permission == "acceptEdits") != has_edit_tools:
        raise GenerationError(
            f"{path}: permissionMode `{permission or '(none)'}` disagrees with Edit/Write in tools"
        )

    instructions = build_instructions(meta, body, path, member_pattern)
    try:
        rendered = render(meta, instructions, tiers[pair], PERMISSION_SANDBOX[permission])
    except ValueError as exc:
        raise GenerationError(f"{path}: {exc}")
    return str(meta["name"]).replace("-", "_") + ".toml", rendered


def claude_sources(claude_dir: Path) -> List[Path]:
    if not claude_dir.is_dir():
        raise GenerationError(f"{claude_dir}: Claude member directory not found")
    return sorted(p for p in claude_dir.glob("*.md") if p.name != "README.md")


def generate_all(claude_dir: Path, policy_path: Path) -> Dict[str, str]:
    """Return {codex_file_name: canonical TOML text} for every Claude member."""
    tiers = load_policy_tiers(Path(policy_path))
    sources = claude_sources(Path(claude_dir))
    pattern = _member_id_pattern([p.stem for p in sources])
    outputs: Dict[str, str] = {}
    for path in sources:
        name, text = generate_one(path, tiers, pattern)
        outputs[name] = text
    return outputs


def generate_member(path: Path, policy_path: Path = DEFAULT_POLICY) -> str:
    """Canonical Codex TOML text for one Claude member file (used by deploy-preset.sh)."""
    path = Path(path)
    tiers = load_policy_tiers(Path(policy_path))
    pattern = _member_id_pattern([p.stem for p in claude_sources(path.parent)])
    return generate_one(path, tiers, pattern)[1]


# --------------------------------------------------------------------------- cli


def compare(outputs: Dict[str, str], codex_dir: Path) -> Dict[str, List[str]]:
    status: Dict[str, List[str]] = {"unchanged": [], "changed": [], "missing": [], "orphan": []}
    for name, text in sorted(outputs.items()):
        target = codex_dir / name
        if not target.exists():
            status["missing"].append(name)
        elif target.read_text(encoding="utf-8") != text:
            status["changed"].append(name)
        else:
            status["unchanged"].append(name)
    if codex_dir.is_dir():
        status["orphan"] = sorted(
            p.name for p in codex_dir.glob("*.toml") if p.name not in outputs
        )
    return status


def _member_id(file_name: str) -> str:
    return file_name[: -len(".toml")].replace("_", "-")


def print_summary(status: Dict[str, List[str]], total: int) -> None:
    print(f"Claude sources: {total}")
    print(f"  unchanged: {len(status['unchanged'])}")
    print(f"  would change: {len(status['changed'])}")
    print(f"  would create: {len(status['missing'])}")
    print(f"  orphan Codex files (no Claude source, never deleted): {len(status['orphan'])}")
    for label, key in (("change", "changed"), ("create", "missing")):
        for name in status[key]:
            print(f"  {label}: {_member_id(name)} -> {name}")
    for name in status["orphan"]:
        print(f"  orphan: {name}")


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="exit 1 on any drift")
    mode.add_argument("--write", action="store_true", help="write changed outputs")
    mode.add_argument("--diff", metavar="NAME", help="unified diff for one agent")
    parser.add_argument("--claude-dir", type=Path, default=DEFAULT_CLAUDE_DIR)
    parser.add_argument("--codex-dir", type=Path, default=DEFAULT_CODEX_DIR)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        outputs = generate_all(args.claude_dir, args.policy)
    except GenerationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.diff:
        name = args.diff.replace("-", "_") + ".toml"
        if name not in outputs:
            print(f"error: no Claude member named `{args.diff}` in {args.claude_dir}", file=sys.stderr)
            return 2
        target = args.codex_dir / name
        committed = target.read_text(encoding="utf-8") if target.exists() else ""
        diff = difflib.unified_diff(
            committed.splitlines(keepends=True),
            outputs[name].splitlines(keepends=True),
            fromfile=f"committed/{name}",
            tofile=f"generated/{name}",
        )
        text = "".join(diff)
        print(text if text else f"{name}: no difference", end="" if text else "\n")
        return 0

    status = compare(outputs, args.codex_dir)
    if args.write:
        args.codex_dir.mkdir(parents=True, exist_ok=True)
        for name in status["changed"] + status["missing"]:
            (args.codex_dir / name).write_text(outputs[name], encoding="utf-8")
        print(f"wrote {len(status['changed']) + len(status['missing'])} file(s)")
        for name in status["orphan"]:
            print(f"  orphan left in place: {name}")
        return 0

    print_summary(status, len(outputs))
    if args.check:
        drift = status["changed"] or status["missing"] or status["orphan"]
        print("check: FAIL" if drift else "check: OK")
        return 1 if drift else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
