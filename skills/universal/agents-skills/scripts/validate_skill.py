#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable


NAME_RE = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
PORTABILITY_CLAIM_RE = re.compile(r"\b(portable|cross-platform|all runtimes|all platforms)\b", re.IGNORECASE)
# Empty text allowed: stripping inline code turns [`x`](y) into [](y).
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
DEFAULT_IGNORED_DIRS = frozenset(
    {
        ".archive",
        ".git",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }
)
TRANSIENT_DIR_NAMES = frozenset({".pytest_cache", ".venv"})
EXTENSION_FIELDS = {
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "context",
    "agent",
    "model",
    "effort",
    "hooks",
    "paths",
    "shell",
    "when_to_use",
    "background",
    "disallowed-tools",
}
# Fields above that Codex does not parse. If `agents/openai.yaml` is present
# (dual-target skill) and any of these appear without a scoped `compatibility`
# note, escalate from warning to error: the skill silently degrades on Codex.
CLAUDE_ONLY_FIELDS = {
    "argument-hint",
    "arguments",
    "context",
    "agent",
    "effort",
    "hooks",
    "model",
    "paths",
    "shell",
    "when_to_use",
    "background",
    "disallowed-tools",
}
TOC_MARKERS = ("## table of contents", "## contents")
# Clean-code rule IDs (CC-NAM-01) must exist in the catalog. CC-BY / CC-MAIN
# and similar tokens are licence or dataset names, not rule IDs.
CC_RULE_CATALOG = Path("software-clean-code-standard") / "references" / "clean-code-standard.md"
CC_RULE_REF_RE = re.compile(r"\bCC-([A-Z]+)-\d+\b")
CC_RULE_DEF_RE = re.compile(r"^\|\s*`?(CC-[A-Z]+-\d+)`?\s*\|", re.MULTILINE)
CC_NON_RULE_PREFIXES = frozenset({"BY", "SA", "NC", "ND", "MAIN"})
# The Workflow pattern is intentionally loose (.*workflow) to accommodate
# existing heading variants: "## Default Workflow", "## Routing Workflow",
# "## Workflow: <domain>", and plain "## Workflow".
CORE_SECTION_PATTERNS = {
    "Quick Reference": re.compile(r"^##\s+quick reference\b", re.IGNORECASE | re.MULTILINE),
    "Workflow": re.compile(r"^##\s+.*workflow\b", re.IGNORECASE | re.MULTILINE),
    "Navigation": re.compile(r"^##\s+navigation\b", re.IGNORECASE | re.MULTILINE),
}


@dataclass
class Issue:
    severity: str
    path: Path
    message: str


# A grouped catalog keeps skills in group folders (skills/universal/<name>/,
# skills/client/<client>/<name>/); the repository's scripts/library_layout.py
# owns that walk. A flat catalog (runtime install folders, the public mirror)
# keeps every skill directly under the root.
CATALOG_GROUP_DIRS = ("universal", "project", "personal", "client")


def _library_layout():
    """Load the repository layout module, or None outside this repository."""
    try:
        scripts_dir = Path(__file__).resolve().parents[4] / "scripts"
    except IndexError:
        return None
    if not (scripts_dir / "library_layout.py").is_file():
        return None
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import library_layout

    return library_layout


def catalog_skill_dirs(catalog_root: Path) -> list[Path]:
    """Every non-hidden skill folder in a flat or grouped catalog, by name."""
    catalog_root = Path(catalog_root)
    layout = None
    if any((catalog_root / group).is_dir() for group in CATALOG_GROUP_DIRS):
        layout = _library_layout()
    if layout is None:
        return sorted(path for path in catalog_root.iterdir() if path.is_dir() and not path.name.startswith("."))
    # Keep stub folders without SKILL.md so the validators still report them.
    entries = (path for path in layout.candidate_dirs(catalog_root)
               if path.is_dir() and not path.name.startswith("."))
    return sorted(entries, key=lambda path: (path.name, str(path)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a skill bundle.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--check-urls", action="store_true", help="Attempt to fetch HTTPS URLs from sources.json")
    return parser.parse_args()


BLOCK_SCALAR_RE = re.compile(r"^([>|])([+-]?)\d*\s*(?:#.*)?$")


def fold_block_scalar(style: str, chomp: str, block_lines: list[str]) -> str:
    """Return the scalar value of a YAML block (`>`/`|`) from its indented lines.

    Folded (`>`) joins lines with spaces and keeps blank lines as newlines;
    literal (`|`) keeps every line break. `-` strips the trailing newline,
    `+` keeps all of them, and the default keeps exactly one.
    """
    while block_lines and not block_lines[-1].strip():
        block_lines.pop()
    indent = min((len(l) - len(l.lstrip(" ")) for l in block_lines if l.strip()), default=0)
    stripped = [l[indent:] if l.strip() else "" for l in block_lines]
    if style == "|":
        value = "\n".join(stripped)
    else:
        value = ""
        for text in stripped:
            if not text:
                value += "\n"
            elif not value or value.endswith("\n"):
                value += text
            else:
                value += " " + text
    if chomp == "+":
        return value + "\n"
    if chomp == "-":
        return value
    return value + "\n" if value else value


def normalize_frontmatter_value(raw: str) -> str:
    value = raw.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, str], list[str]]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith("﻿"):
        raise ValueError(
            "SKILL.md begins with a UTF-8 BOM; Codex silently skips skills with a BOM"
        )
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("missing closing frontmatter delimiter")

    frontmatter: dict[str, str] = {}
    has_tab_indent = False
    body = lines[1:end_index]
    index = 0
    while index < len(body):
        line = body[index]
        index += 1
        if not line.strip():
            continue
        if line.startswith("\t"):
            has_tab_indent = True
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        block = BLOCK_SCALAR_RE.match(raw_value.strip())
        if block:
            # Block scalar (`>-`, `|`, ...). The indented lines that follow
            # are the value; a line-based parser that skips indentation
            # would otherwise never see the description at all.
            block_lines: list[str] = []
            while index < len(body) and (not body[index].strip() or body[index].startswith((" ", "\t"))):
                if body[index].startswith("\t"):
                    has_tab_indent = True
                block_lines.append(body[index])
                index += 1
            frontmatter[key.strip()] = fold_block_scalar(block.group(1), block.group(2), block_lines)
            continue
        value = normalize_frontmatter_value(raw_value)
        if value:
            # A plain multi-line scalar continues on indented lines.
            while index < len(body) and body[index].strip() and body[index].startswith(" "):
                value = f"{value} {body[index].strip()}"
                index += 1
        frontmatter[key.strip()] = value
    if has_tab_indent:
        # Tabs are not valid YAML indentation. Codex parsers silently drop
        # tab-indented fields; Anthropic parsers vary. Surface as parse error.
        raise ValueError("frontmatter contains tab-indented lines; use spaces only")
    return frontmatter, lines


def add_issue(issues: list[Issue], severity: str, path: Path, message: str) -> None:
    issues.append(Issue(severity=severity, path=path, message=message))


def validate_frontmatter(skill_dir: Path, skill_md: Path, issues: list[Issue]) -> None:
    try:
        frontmatter, lines = parse_frontmatter(skill_md)
    except ValueError as exc:
        add_issue(issues, "error", skill_md, str(exc))
        return

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    compatibility = frontmatter.get("compatibility", "")

    if not name:
        add_issue(issues, "error", skill_md, "missing `name` in frontmatter")
    elif not NAME_RE.fullmatch(name):
        add_issue(issues, "error", skill_md, "`name` must be kebab-case, <= 64 chars, and must not start/end with `-` or contain `--`")
    elif name != skill_dir.name:
        add_issue(issues, "error", skill_md, f"`name` does not match folder name (`{skill_dir.name}`)")

    if not description:
        add_issue(issues, "error", skill_md, "missing `description` in frontmatter")
    else:
        if "\n" in description:
            add_issue(issues, "error", skill_md, "`description` must be single-line YAML")
        if len(description) > 1024:
            add_issue(issues, "error", skill_md, "`description` exceeds 1024 characters")
        if len(description) > 220:
            add_issue(issues, "warning", skill_md, "`description` is long; shared skill budgets usually reward shorter descriptions")
        first_word = description.split(" ", 1)[0].lower()
        if first_word in {"use", "help", "do", "build", "make"}:
            add_issue(issues, "warning", skill_md, "`description` does not look third-person")

    if len(lines) > 500:
        add_issue(issues, "warning", skill_md, f"`SKILL.md` has {len(lines)} lines; consider splitting references")

    # A hyphen/underscore variant of a known field (e.g. `when-to-use`) is
    # ignored by the runtime without an error, so the skill silently loses it.
    known_by_shape = {field.replace("_", "-"): field for field in EXTENSION_FIELDS}
    for key in frontmatter:
        canonical = known_by_shape.get(key.replace("_", "-"))
        if canonical and key != canonical:
            add_issue(
                issues,
                "warning",
                skill_md,
                f"`{key}` looks like a misspelling of `{canonical}`; the runtime ignores unknown fields",
            )

    present_extensions = sorted(field for field in EXTENSION_FIELDS if field in frontmatter)
    claude_only_present = sorted(field for field in CLAUDE_ONLY_FIELDS if field in frontmatter)
    has_codex_metadata = (skill_dir / "agents" / "openai.yaml").exists()

    if present_extensions and not compatibility:
        add_issue(
            issues,
            "warning",
            skill_md,
            "runtime-specific extension fields are present without a scoped `compatibility` note",
        )
    if present_extensions and compatibility and PORTABILITY_CLAIM_RE.search(compatibility):
        add_issue(
            issues,
            "error",
            skill_md,
            "runtime-specific extension fields appear alongside a portability claim in `compatibility`",
        )
    if has_codex_metadata and claude_only_present and not compatibility:
        add_issue(
            issues,
            "error",
            skill_md,
            f"`agents/openai.yaml` is present but Claude-only fields ({', '.join(claude_only_present)}) "
            "have no `compatibility` note; Codex will silently ignore them",
        )


def validate_core_sections(skill_md: Path, issues: list[Issue]) -> None:
    text = skill_md.read_text(encoding="utf-8")
    for section_name, pattern in CORE_SECTION_PATTERNS.items():
        if not pattern.search(text):
            add_issue(issues, "warning", skill_md, f"missing canonical `{section_name}` section")


def markdown_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*.md")):
        if any(part in DEFAULT_IGNORED_DIRS for part in path.parts):
            continue
        yield path


def strip_code_examples(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in text.splitlines():
        stripped = line.lstrip()
        match = re.match(r"^([`~]{3,})", stripped)
        if match:
            marker = match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                in_fence = False
                fence_char = ""
                fence_len = 0
            lines.append("")
            continue

        lines.append("" if in_fence else line)

    return INLINE_CODE_RE.sub("", "\n".join(lines))


def validate_links(skill_dir: Path, issues: list[Issue]) -> None:
    for md_path in markdown_files(skill_dir):
        text = strip_code_examples(md_path.read_text(encoding="utf-8"))
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_only = target.split("#", 1)[0]
            resolved = (md_path.parent / path_only).resolve()
            if not resolved.exists():
                add_issue(issues, "error", md_path, f"broken local link: {target}")


def validate_reference_tocs(skill_dir: Path, issues: list[Issue]) -> None:
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return

    for ref_path in sorted(references_dir.glob("*.md")):
        lines = ref_path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= 100:
            continue
        window = "\n".join(lines[:40]).lower()
        if not any(marker in window for marker in TOC_MARKERS):
            add_issue(issues, "error", ref_path, "reference files over 100 lines must include a table of contents near the top")


def validate_cc_rule_ids(skill_dir: Path, issues: list[Issue]) -> None:
    # Sibling in a flat catalog; in a grouped one the rule catalog sits in the
    # universal group, one or two levels above a project or client skill.
    candidates = (skill_dir.parent / CC_RULE_CATALOG,
                  skill_dir.parent.parent / "universal" / CC_RULE_CATALOG,
                  skill_dir.parent.parent.parent / "universal" / CC_RULE_CATALOG)
    catalog = next((path for path in candidates if path.is_file()), None)
    if catalog is None:
        return
    defined = set(CC_RULE_DEF_RE.findall(catalog.read_text(encoding="utf-8")))
    for md_path in markdown_files(skill_dir):
        # learnings.md records retired IDs on purpose.
        if md_path.name == "learnings.md":
            continue
        text = md_path.read_text(encoding="utf-8")
        unknown = sorted(
            {
                match.group(0)
                for match in CC_RULE_REF_RE.finditer(text)
                if match.group(1) not in CC_NON_RULE_PREFIXES and match.group(0) not in defined
            }
        )
        if unknown:
            add_issue(issues, "error", md_path, f"unknown clean-code rule IDs (not in {CC_RULE_CATALOG}): {', '.join(unknown)}")


def validate_sources(skill_dir: Path, issues: list[Issue], check_urls: bool) -> None:
    sources_path = skill_dir / "data" / "sources.json"
    if not sources_path.exists():
        return

    try:
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_issue(issues, "error", sources_path, f"invalid JSON: {exc}")
        return

    metadata = sources.get("metadata")
    if not isinstance(metadata, dict):
        add_issue(issues, "error", sources_path, "missing `metadata` object")
        return

    for key in ("title", "description", "last_updated", "skill"):
        if not metadata.get(key):
            add_issue(issues, "error", sources_path, f"missing `metadata.{key}`")

    if metadata.get("skill") and metadata["skill"] != skill_dir.name:
        add_issue(issues, "error", sources_path, f"`metadata.skill` does not match folder name (`{skill_dir.name}`)")

    last_updated = metadata.get("last_updated")
    if last_updated:
        try:
            updated_date = date.fromisoformat(last_updated)
        except ValueError:
            add_issue(issues, "error", sources_path, "`metadata.last_updated` must use YYYY-MM-DD")
        else:
            if date.today() - updated_date > timedelta(days=183):
                add_issue(issues, "warning", sources_path, "`metadata.last_updated` is older than 6 months")

    url_fields: list[tuple[str, str, str]] = []
    for section_name, section_value in sources.items():
        if section_name == "metadata":
            continue
        validate_source_section(sources_path, section_name, section_value, issues, url_fields)

    if check_urls:
        for name, url, url_check in url_fields:
            if url_check in {"manual", "skip"}:
                continue
            validate_url(sources_path, name, url, issues)


def find_transient_dirs(skill_dir: Path) -> list[Path]:
    transient_dirs: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_dir():
            continue
        if path.name in TRANSIENT_DIR_NAMES:
            transient_dirs.append(path)
    return transient_dirs


def validate_source_section(
    sources_path: Path,
    section_name: str,
    section_value: object,
    issues: list[Issue],
    url_fields: list[tuple[str, str, str]],
) -> None:
    if isinstance(section_value, list):
        if not any(isinstance(item, dict) for item in section_value):
            return
        validate_source_array(sources_path, section_name, section_value, issues, url_fields)
        return

    if isinstance(section_value, dict):
        # Support richer source registries such as `categories: { ...arrays }`
        # and metadata-like taxonomies that may mix scalar fields with nested
        # lists or dicts.
        for child_name, child_value in section_value.items():
            if not isinstance(child_value, (list, dict)):
                continue
            validate_source_section(
                sources_path,
                f"{section_name}.{child_name}",
                child_value,
                issues,
                url_fields,
            )
        return

    add_issue(issues, "error", sources_path, f"`{section_name}` must be an array or object")


def validate_source_array(
    sources_path: Path,
    section_name: str,
    section_value: list[object],
    issues: list[Issue],
    url_fields: list[tuple[str, str, str]],
) -> None:
    for index, item in enumerate(section_value):
        if not isinstance(item, dict):
            add_issue(issues, "error", sources_path, f"`{section_name}[{index}]` must be an object")
            continue
        url = item.get("url")
        url_template = item.get("url_template")
        name = item.get("name", f"{section_name}[{index}]")
        url_check = item.get("url_check", "auto")
        if not url and not url_template:
            add_issue(issues, "error", sources_path, f"`{section_name}[{index}].url` is required")
            continue
        if url_check not in {"auto", "manual", "skip"}:
            add_issue(issues, "error", sources_path, f"`{name}` has invalid `url_check` value `{url_check}`")
        if url and item.get("type") == "internal_reference":
            resolved = (sources_path.parent / url).resolve()
            if not resolved.exists():
                add_issue(issues, "error", sources_path, f"`{name}` internal reference does not exist: {url}")
        elif url and not url.startswith("https://"):
            add_issue(issues, "error", sources_path, f"`{name}` must use HTTPS")
        if url and url.startswith("https://"):
            url_fields.append((name, url, url_check))


# Servers that reject HEAD (405, sometimes 403) usually serve GET; retry
# before reporting the URL as broken.
HEAD_RETRY_WITH_GET = frozenset({403, 405})


def validate_url(sources_path: Path, name: str, url: str, issues: list[Issue]) -> None:
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status = getattr(response, "status", 200)
                if status >= 400:
                    add_issue(issues, "error", sources_path, f"`{name}` returned HTTP {status}: {url}")
            return
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in HEAD_RETRY_WITH_GET:
                continue
            add_issue(issues, "error", sources_path, f"`{name}` returned HTTP {exc.code}: {url}")
            return
        except urllib.error.URLError as exc:
            add_issue(issues, "warning", sources_path, f"could not reach `{name}`: {exc.reason}")
            return


# --- Learnings entries and support-file reachability --------------------------
# Severity is set from a library-wide measurement; see the report of step 3.4.
LEARNINGS_SEVERITY = "warning"
SUPPORT_FILES_SEVERITY = "warning"
SUPPORT_DIRS = ("references", "assets", "templates")
LEARNINGS_RAW_NAME = "learnings.md"
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def load_learning_writer():
    """Import the feedback-loop writer for its entry shape, cap, and redaction.

    Resolved from the real file location so a symlinked skill still finds its
    sibling skill. Returns None when the writer is not installed beside this one.
    """
    scripts_dir = (Path(__file__).resolve().parents[2] / "agents-skills-feedback-loop" / "scripts")
    if not (scripts_dir / "append_learning.py").is_file():
        return None
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import append_learning

    return append_learning


def validate_learnings(skill_dir: Path, issues: list[Issue]) -> None:
    files = sorted(skill_dir.glob("learnings*.md"))
    if not files:
        return
    writer = load_learning_writer()
    entry_re = writer.ENTRY_RE if writer else re.compile(r"^- \[\d{4}-\d{2}-\d{2}\] ")
    cap = writer.RAW_CAP if writer else 150
    if writer is None:
        add_issue(issues, "warning", files[0], "append_learning.py not found; learnings redaction check skipped")
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            add_issue(issues, LEARNINGS_SEVERITY, path, f"unreadable learnings file: {exc}")
            continue
        entries = 0
        fence = ""
        for number, line in enumerate(lines, 1):
            match = _FENCE_RE.match(line)
            if match:
                marker = match.group(1)
                fence = "" if fence and marker[0] == fence else (fence or marker[0])
                continue
            if fence or not line.startswith("- "):
                continue
            if not entry_re.match(line):
                add_issue(issues, LEARNINGS_SEVERITY, path, f"line {number}: learnings entry must start with `- [YYYY-MM-DD] `")
                continue
            entries += 1
            if writer is not None:
                redacted, _tags = writer.redact(line)
                if redacted != line:
                    add_issue(issues, LEARNINGS_SEVERITY, path, f"line {number}: entry holds a secret or personal data (writer redaction changes it)")
        if path.name == LEARNINGS_RAW_NAME and entries > cap:
            add_issue(issues, LEARNINGS_SEVERITY, path, f"{entries} entries exceed the raw cap of {cap}")


def _local_link_targets(md_path: Path) -> set[Path]:
    """Resolved local file targets of the markdown links in one file."""
    text = strip_code_examples(md_path.read_text(encoding="utf-8"))
    targets: set[Path] = set()
    for raw in LINK_RE.findall(text):
        target = raw.strip().split("#", 1)[0].split(" ", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        targets.add((md_path.parent / target).resolve())
    return targets


def validate_support_files(skill_dir: Path, issues: list[Issue]) -> None:
    """One hop: SKILL.md links each support file directly (hub and leaves).

    A cross-link between references is fine when SKILL.md also links the target:
    the target stays one hop from the hub. A link to a reference that only other
    references reach is reported, because the model then has to follow a chain.
    """
    skill_md = skill_dir / "SKILL.md"
    try:
        linked = _local_link_targets(skill_md)
    except (OSError, UnicodeDecodeError) as exc:
        add_issue(issues, SUPPORT_FILES_SEVERITY, skill_md, f"cannot read SKILL.md links: {exc}")
        return
    skill_root = skill_dir.resolve()
    for folder in SUPPORT_DIRS:
        base = skill_dir / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or any(part in DEFAULT_IGNORED_DIRS for part in path.parts):
                continue
            if path.name.startswith("."):
                continue
            if path.resolve() not in linked:
                add_issue(issues, SUPPORT_FILES_SEVERITY, path, "support file is not linked from SKILL.md")
    refs = skill_dir / "references"
    if not refs.is_dir():
        return
    ref_root = refs.resolve()
    for path in sorted(refs.rglob("*.md")):
        if any(part in DEFAULT_IGNORED_DIRS for part in path.parts):
            continue
        try:
            targets = _local_link_targets(path)
        except (OSError, UnicodeDecodeError):
            continue
        for target in sorted(targets):
            if (target != path.resolve() and target.is_file() and ref_root in target.parents
                    and skill_root in target.parents and target not in linked):
                add_issue(issues, SUPPORT_FILES_SEVERITY, path,
                          f"reference links to a reference that SKILL.md does not link: {target.name}")


def print_report(skill_dir: Path, issues: list[Issue]) -> int:
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]

    status = "FAIL" if errors else "WARN" if warnings else "PASS"
    print("## Validation Summary")
    print()
    print(f"- Status: {status}")
    print(f"- Skill: `{skill_dir.name}`")
    print(f"- Errors: {len(errors)}")
    print(f"- Warnings: {len(warnings)}")
    print()

    print("## Errors")
    if errors:
        for issue in errors:
            print(f"- {issue.path}: {issue.message}")
    else:
        print("- None")
    print()

    print("## Warnings")
    if warnings:
        for issue in warnings:
            print(f"- {issue.path}: {issue.message}")
    else:
        print("- None")

    return 1 if errors else 0


def validate_skill_dir(skill_dir: Path, check_urls: bool = False) -> list[Issue]:
    skill_md = skill_dir / "SKILL.md"
    issues: list[Issue] = []

    if not skill_md.exists():
        add_issue(issues, "error", skill_md, "missing SKILL.md")
        return issues

    validate_frontmatter(skill_dir, skill_md, issues)
    validate_core_sections(skill_md, issues)
    validate_links(skill_dir, issues)
    validate_reference_tocs(skill_dir, issues)
    validate_cc_rule_ids(skill_dir, issues)
    validate_sources(skill_dir, issues, check_urls)
    validate_learnings(skill_dir, issues)
    validate_support_files(skill_dir, issues)
    return issues


def main() -> int:
    args = parse_args()
    skill_dir = Path(args.skill_dir).resolve()
    issues = validate_skill_dir(skill_dir, check_urls=args.check_urls)
    return print_report(skill_dir, issues)


if __name__ == "__main__":
    sys.exit(main())
