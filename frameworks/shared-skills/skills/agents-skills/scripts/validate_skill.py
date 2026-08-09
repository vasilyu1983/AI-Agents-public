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
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
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
}
TOC_MARKERS = ("## table of contents", "## contents")
# The Workflow pattern is intentionally loose (.*workflow) to accommodate
# existing heading variants: "## Default Workflow", "## Routing Workflow",
# "## Workflow: <domain>", and plain "## Workflow".
CORE_SECTION_PATTERNS = {
    "Quick Reference": re.compile(r"^##\s+quick reference\b", re.IGNORECASE | re.MULTILINE),
    "Workflow": re.compile(r"^##\s+.*workflow\b", re.IGNORECASE | re.MULTILINE),
    "Navigation": re.compile(r"^##\s+navigation\b", re.IGNORECASE | re.MULTILINE),
    "Fact-Checking": re.compile(r"^##\s+fact-?checking\b", re.IGNORECASE | re.MULTILINE),
}


@dataclass
class Issue:
    severity: str
    path: Path
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a skill bundle.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument("--check-urls", action="store_true", help="Attempt to fetch HTTPS URLs from sources.json")
    return parser.parse_args()


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
    for line in lines[1:end_index]:
        if not line.strip():
            continue
        if line.startswith("\t"):
            has_tab_indent = True
        if line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = normalize_frontmatter_value(value)
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


def validate_url(sources_path: Path, name: str, url: str, issues: list[Issue]) -> None:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = getattr(response, "status", 200)
            if status >= 400:
                add_issue(issues, "error", sources_path, f"`{name}` returned HTTP {status}: {url}")
    except urllib.error.HTTPError as exc:
        add_issue(issues, "error", sources_path, f"`{name}` returned HTTP {exc.code}: {url}")
    except urllib.error.URLError as exc:
        add_issue(issues, "warning", sources_path, f"could not reach `{name}`: {exc.reason}")


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
    validate_sources(skill_dir, issues, check_urls)
    return issues


def main() -> int:
    args = parse_args()
    skill_dir = Path(args.skill_dir).resolve()
    issues = validate_skill_dir(skill_dir, check_urls=args.check_urls)
    return print_report(skill_dir, issues)


if __name__ == "__main__":
    sys.exit(main())
