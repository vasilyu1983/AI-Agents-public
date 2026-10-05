#!/usr/bin/env python3
"""Validate agents-subagents catalog integrity.

This is the cheap regression harness for the data-heavy parts of the skill:
template counts, stale count prose, duplicate template titles, member parity,
team context fields, context-first coverage, and duplicate team-coverage skill
references.
"""

from __future__ import annotations

import argparse
from datetime import date
import difflib
import importlib.util
import json
import re
import subprocess
try:
    import tomllib
except ImportError:  # Python 3.10 and older
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "TOML support unavailable: run with Python 3.11+ (this file needs "
            "the stdlib tomllib) or install the 'tomli' backport."
        ) from exc
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# The agent catalog lives outside this skill, at <repo>/agents (see scripts/library_layout.py).
REPO = Path(__file__).resolve().parents[4]
AGENTS_DIR = REPO / "agents"
CLAUDE_MEMBERS = AGENTS_DIR / "claude"
CODEX_MEMBERS = AGENTS_DIR / "codex"
TEAMS_DIR = AGENTS_DIR / "teams"
TEMPLATES_DIR = AGENTS_DIR / "templates"
WORKFLOWS_DIR = AGENTS_DIR / "workflows"
TEAM_COVERAGE = ROOT / "references" / "team-coverage.md"
MODEL_POLICY_FILE = ROOT / "data" / "model-policy.json"
TEAM_MEMBER_MATRIX = ROOT / "references" / "team-member-matrix.md"
TEAM_MEMBER_MATRIX_GENERATOR = ROOT / "scripts" / "generate_team_member_matrix.py"
# Claude Code injects every installed agent's description into the system prompt and warns
# past 15k tokens. At ~3.9 chars/token plus per-agent name and tools overhead, 48k chars of
# description across the catalog keeps a full install under the ceiling.
MEMBER_DESCRIPTION_MAX_CHARS = 420
CATALOG_DESCRIPTION_BUDGET_CHARS = 48_000
WORKFLOWS_GENERATOR = ROOT / "scripts" / "generate_workflows.py"

# Expected count is `int` to enforce, or `None` to audit-only (count reported but
# no error raised). Use `None` for directories that are tracked but still in
# progress or intentionally empty.
EXPECTED_TEMPLATE_COUNTS: dict[str, tuple[Path, int | None]] = {
    "debate_methods": (TEMPLATES_DIR / "debate-methods", 10),
    "decision_masks": (TEMPLATES_DIR / "decision-masks", 7),
    "game_theory_mechanisms": (TEMPLATES_DIR / "game-theory", None),
}

STALE_COUNT_PATTERNS = {
    "stale_decision_mask_counts": re.compile(
        r"\b(4 decision masks|4 mask overlays|Decision Masks \(4\)|10 methods \+ 4 masks|"
        r"6 decision masks|6 mask overlays|Decision Masks \(6\)|10 methods \+ 6 masks|"
        r"6 cognitive frames)\b",
        re.IGNORECASE,
    ),
    "stale_game_mechanism_counts": re.compile(
        r"\b(12 game-theory mechanisms|12 mechanisms|hub for 12|game theory layer provides 12|"
        r"16 game-theory mechanisms|hub for 16|game theory layer provides 16|"
        r"17 game-theory mechanisms|hub for 17|game theory layer provides 17|"
        r"Game Theory Mechanisms \(12\)|Game Theory Mechanisms \(16\)|Game Theory Mechanisms \(17\))\b",
        re.IGNORECASE,
    ),
}

# Count-bearing catalog prose is validated against the filesystem rather than a
# list of historical values. Keep these patterns narrow: ordinary domain prose
# legitimately contains numbers such as Companies Act section 141.
CATALOG_COUNT_PATTERNS: dict[str, tuple[re.Pattern[str], str]] = {
    "claude_members": (
        re.compile(r"\b(\d+)\s+Claude members\b", re.I),
        "members",
    ),
    "claude_canonical_members": (
        re.compile(r"\bClaude canonical members:\s*(\d+)\b", re.I),
        "members",
    ),
    "codex_members": (
        re.compile(r"\b(\d+)\s+Codex members\b", re.I),
        "members",
    ),
    "codex_canonical_members": (
        re.compile(r"\bCodex canonical members:\s*(\d+)\b", re.I),
        "members",
    ),
    "canonical_members": (
        re.compile(r"\b(?:all\s+)?(\d+)\s+canonical members\b", re.I),
        "members",
    ),
    "member_denominator": (
        re.compile(r"\bcurrently\s+\d+\s+of\s+(\d+)\s+members\b", re.I),
        "members",
    ),
    "shared_teams": (
        re.compile(r"\bShared teams:\s*(\d+)\b", re.I),
        "teams",
    ),
    "team_recipes": (
        re.compile(r"\b(\d+)\s+(?:installable\s+)?team recipes\b", re.I),
        "teams",
    ),
    "debate_enabled_teams": (
        re.compile(r"\b(\d+)\s+debate-enabled(?:\s+teams)?\b", re.I),
        "debate_teams",
    ),
}

CONTEXT_PATTERN = re.compile(
    r"context packet|prepared context|portfolio context|docs/context|context artifact|"
    r"provided context|context inputs|context-first|context-first-protocol",
    re.IGNORECASE,
)

# Canonical Codex assets carry symbolic tiers, never executable model IDs. The
# installer resolves these through data/model-policy.json when it materializes
# user or project agent files.
MODEL_TIERS = {"critical", "mechanical", "standard"}
MODEL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
EFFORTS = {"low", "medium", "high", "xhigh", "max"}

CONTEXT_EXEMPT = {
    "dev-portfolio-mapper",
    "dev-repo-context-curator",
    "dev-code-graph-builder",
    "dev-context-packet-synthesizer",
    "docs-codebase-architect",
    "docs-notes-retrieval-curator",
}

CHECKED_EXTENSIONS = {".md", ".yaml", ".yml", ".toml", ".json"}

REFERENCES_DIR = ROOT / "references"
# Member files sit in <repo>/agents/<platform>/; this is the one relative hop the
# installer rewrites (deploy-preset.sh rewrite_member_reference_links).
RELATIVE_REFERENCE_RE = re.compile(
    r"\.\./\.\./skills/universal/agents-subagents/references/([A-Za-z0-9._-]+)"
)

# Codex bodies legitimately diverge from their Claude sibling by a TOML preamble
# and, for some members, an inlined protocol. This is a drift signal, not a
# contract: below the floor the pair is worth a human look, never a build break.
# 0.75, not 0.90: canonical Codex bodies legitimately diverge from Claude
# siblings by the launch-prompt-authority preamble and the inlined
# context-first rule; at 0.90 the floor flagged 89/141 healthy pairs.
BODY_SIMILARITY_FLOOR = 0.75

URL_RE = re.compile(r"https?://[^\s<>\")\]]+")

# Deliberately small and conservative. Each entry is a provenance marker whose
# loss in the Codex sibling means a citation silently vanished between runtimes.
# Substring matching keeps false positives near zero; broadening this list trades
# that away, so add only markers that are unambiguous on their own.
CITATION_MARKERS = (
    "arXiv",
    "doi.org",
    "DOI:",
)

# These identifiers name Claude Code tools, not portable capabilities. Keep the
# list to distinctive identifiers: words such as Read, Write, and Task occur in
# ordinary prose and would create false positives if matched as bare tokens.
CLAUDE_ONLY_TOOL_IDENTIFIERS = (
    "AskUserQuestion",
    "EnterPlanMode",
    "ExitPlanMode",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskUpdate",
    "TodoWrite",
    "WebFetch",
    "WebSearch",
)

CURRENT_CODEX_FOOTER_RE = re.compile(
    r"^Linked skills: ([^.\n]*)\. Declared for Codex; .+$",
    re.MULTILINE,
)
LEGACY_CODEX_FOOTER_RE = re.compile(
    r"^(?:\*\*)?Teammate note|Linked shared skills \([^)]*\) "
    r"(?:are resolved independently for Codex|are declared for Codex)",
    re.MULTILINE,
)
CODEX_LEAF_BOUNDARY = "do not delegate or spawn subagents"


def member_body(text: str) -> str:
    """Claude markdown body, frontmatter stripped."""
    _frontmatter, body = frontmatter_and_body(text)
    return body


def codex_body(text: str) -> str:
    """Codex developer_instructions, or raw text when the TOML will not parse."""
    try:
        instructions = tomllib.loads(text).get("developer_instructions", "")
    except tomllib.TOMLDecodeError:
        return text
    return instructions if isinstance(instructions, str) else ""


_CODEX_ONLY_BLOCK_RE = re.compile(r"^[ \t]*<!-- codex-only[ \t]*\n.*?^[ \t]*-->[ \t]*$", re.MULTILINE | re.DOTALL)
_MARKER_LINE_RE = re.compile(r"^[ \t]*<!--[ \t]*(?:/?claude-only|codex-only:.*?)[ \t]*-->[ \t]*$", re.MULTILINE)


def claude_view(body: str) -> str:
    """Claude body as Claude reads it: codex-only text and marker lines removed.

    generate_codex_agents.py keeps Codex-only text inside HTML comments in the
    Claude file; comparing that raw text would count it as drift.
    """
    return _MARKER_LINE_RE.sub("", _CODEX_ONLY_BLOCK_RE.sub("", body))


def normalize_body(text: str) -> str:
    """Collapse whitespace so formatting differences do not read as drift."""
    return re.sub(r"\s+", " ", text).strip().lower()


REFERENCES_DIR = ROOT / "references"
_FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
_LAST_VERIFIED_RE = re.compile(r"^last_verified:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?\s*$", re.MULTILINE)


def _frontmatter_last_verified(text: str) -> str | None:
    """Return the `last_verified` date from a markdown file's YAML frontmatter."""
    block = _FRONTMATTER_RE.match(text)
    if not block:
        return None
    found = _LAST_VERIFIED_RE.search(block.group(1))
    return found.group(1) if found else None


def _git_last_commit_date(path: Path) -> str | None:
    """Return the committer date (YYYY-MM-DD) of the last commit touching `path`.

    Returns None when git is unavailable, the tree is not a repository, or the
    file has never been committed (a brand-new file cannot be stale).
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path.name],
            cwd=path.parent,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, ValueError):
        return None
    if result.returncode != 0:
        return None
    stamp = result.stdout.strip()
    return stamp if re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp) else None


def check_reference_stamp_freshness(
    summary: dict[str, object],
    errors: list[str],
    warnings: list[str],
    strict: bool = False,
) -> None:
    """Flag references whose `last_verified` predates their last git commit.

    A stamp older than the file's last commit means the file was edited after it
    was last cross-checked, so the stamp asserts a verification that never
    covered the current bytes. Advisory by default (a `STALE STAMP` list);
    blocking under `--strict-freshness`.
    """
    stale: list[dict[str, str]] = []
    unstamped: list[str] = []
    for path in sorted(REFERENCES_DIR.rglob("*.md")):
        if ".archive" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        verified = _frontmatter_last_verified(path.read_text(encoding="utf-8"))
        if verified is None:
            unstamped.append(rel)
            continue
        committed = _git_last_commit_date(path)
        if committed is not None and verified < committed:
            stale.append({"file": rel, "last_verified": verified, "last_commit": committed})

    summary["reference_stamp_stale"] = stale
    summary["reference_stamp_unstamped"] = unstamped
    for entry in stale:
        message = (
            f"STALE STAMP {entry['file']}: last_verified {entry['last_verified']} "
            f"predates last commit {entry['last_commit']}"
        )
        (errors if strict else warnings).append(message)


def check_body_similarity(summary: dict[str, object], warnings: list[str]) -> None:
    """WARN when a Claude/Codex pair's bodies have diverged past the floor."""
    low_pairs: dict[str, float] = {}
    for claude_path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        if claude_path.name == "README.md":
            continue
        member_id = claude_path.stem
        codex_path = CODEX_MEMBERS / f"{member_id.replace('-', '_')}.toml"
        if not codex_path.exists():
            continue
        claude_text = normalize_body(claude_view(member_body(claude_path.read_text(encoding="utf-8"))))
        codex_text = normalize_body(codex_body(codex_path.read_text(encoding="utf-8")))
        if not claude_text or not codex_text:
            continue
        ratio = difflib.SequenceMatcher(None, claude_text, codex_text).ratio()
        if ratio < BODY_SIMILARITY_FLOOR:
            low_pairs[member_id] = round(ratio, 3)
    summary["body_similarity_below_floor"] = low_pairs
    for member_id, ratio in sorted(low_pairs.items()):
        warnings.append(
            f"body similarity {ratio:.3f} < {BODY_SIMILARITY_FLOOR} for {member_id} "
            "(Claude vs Codex)"
        )


def check_citation_loss(summary: dict[str, object], warnings: list[str]) -> None:
    """WARN when a Claude body cites a source its Codex sibling drops."""
    losses: dict[str, list[str]] = {}
    for claude_path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        if claude_path.name == "README.md":
            continue
        member_id = claude_path.stem
        codex_path = CODEX_MEMBERS / f"{member_id.replace('-', '_')}.toml"
        if not codex_path.exists():
            continue
        claude_text = member_body(claude_path.read_text(encoding="utf-8"))
        codex_text = codex_path.read_text(encoding="utf-8")
        dropped = sorted(
            {url for url in URL_RE.findall(claude_text) if url not in codex_text}
        )
        dropped += [
            marker
            for marker in CITATION_MARKERS
            if marker in claude_text and marker not in codex_text
        ]
        if dropped:
            losses[member_id] = dropped
    summary["codex_citation_losses"] = losses
    for member_id, dropped in sorted(losses.items()):
        for item in dropped:
            warnings.append(f"citation dropped in Codex sibling of {member_id}: {item}")


def rel(path: Path) -> Path:
    """Path relative to the skill folder, or to the repo for catalog files under agents/."""
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path.relative_to(REPO)


def check_reference_links(summary: dict[str, object], errors: list[str]) -> None:
    """Every ../../skills/universal/agents-subagents/references/<file> link must resolve."""
    broken: list[str] = []
    for path in checked_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name in sorted(set(RELATIVE_REFERENCE_RE.findall(text))):
            if not (REFERENCES_DIR / name).is_file():
                broken.append(f"{rel(path)} -> references/{name}")
    summary["broken_reference_links"] = broken
    if broken:
        errors.append(
            f"broken ../../skills/universal/agents-subagents/references/ links ({len(broken)}): "
            + ", ".join(broken[:5])
            + (" ..." if len(broken) > 5 else "")
        )


def check_installable_relative_links(summary: dict[str, object], errors: list[str]) -> None:
    """Every escaping `../` link in a member body must be one the installer rewrites.

    Member files are installed by verbatim copy into an agents/ directory, so any
    relative link with a `../` hop leaves the installed file's directory and
    dangles. deploy-preset.sh repairs exactly one shape —
    `../../skills/universal/agents-subagents/references/<file>`, via
    rewrite_member_reference_links, for both the
    Claude and Codex paths. Any other escaping hop has no rewrite rule and would
    ship broken, so it fails here rather than in a user's agents directory.
    """
    unrewritable: list[str] = []
    for path in sorted(CLAUDE_MEMBERS.glob("*.md")) + sorted(CODEX_MEMBERS.glob("*.toml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in sorted(set(re.findall(r"\]\((\.\./[^)\s]*)", text))):
            if not RELATIVE_REFERENCE_RE.match(target):
                unrewritable.append(f"{rel(path)} -> {target}")
    summary["unrewritable_relative_links"] = unrewritable
    if unrewritable:
        errors.append(
            f"member links with ../ hops the installer cannot rewrite "
            f"({len(unrewritable)}): "
            + ", ".join(unrewritable[:5])
            + (" ..." if len(unrewritable) > 5 else "")
        )


def markdown_files_without_readme(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*.md") if path.name != "README.md")


def first_heading(path: Path) -> str:
    match = re.search(r"^#\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    return match.group(1).strip() if match else path.stem


def canonical_codex_id(path: Path) -> str:
    return path.stem.replace("_", "-")


def frontmatter_and_body(text: str) -> tuple[str, str]:
    parts = text.split("---", 2)
    if len(parts) >= 3:
        return parts[1], parts[2]
    return "", text


def frontmatter_list(frontmatter: str, key: str) -> list[str]:
    values: list[str] = []
    capture = False
    for line in frontmatter.splitlines():
        if re.match(rf"^{re.escape(key)}:\s*$", line):
            capture = True
            continue
        if not capture:
            continue
        if re.match(r"^\s*-\s+", line):
            values.append(re.sub(r"^\s*-\s+", "", line).strip())
            continue
        if line.strip() == "":
            continue
        break
    return values


def codex_linked_skills(text: str) -> list[str]:
    try:
        instructions = tomllib.loads(text).get("developer_instructions", "")
    except tomllib.TOMLDecodeError:
        return []
    match = CURRENT_CODEX_FOOTER_RE.search(instructions)
    if not match:
        return []
    return [skill_id.strip() for skill_id in match.group(1).split(",") if skill_id.strip()]


def check_codex_runtime_contracts(summary: dict[str, object], errors: list[str]) -> None:
    """Enforce Codex-only footer, tool, and recursive-delegation contracts."""
    invalid_toml: list[str] = []
    missing_current_footer: list[str] = []
    legacy_footers: list[str] = []
    forbidden_tools: list[str] = []
    leaf_members: set[str] = set()
    leaf_members_missing_boundary: list[str] = []

    for claude_path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        if claude_path.name == "README.md":
            continue
        frontmatter, _body = frontmatter_and_body(
            claude_path.read_text(encoding="utf-8")
        )
        if "Agent" in frontmatter_list(frontmatter, "disallowedTools"):
            leaf_members.add(claude_path.stem)

    for path in sorted(CODEX_MEMBERS.glob("*.toml")):
        member_id = canonical_codex_id(path)
        text = path.read_text(encoding="utf-8")
        try:
            member = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            invalid_toml.append(f"{path.name}: {exc}")
            continue
        instructions = member.get("developer_instructions", "")
        if not isinstance(instructions, str):
            invalid_toml.append(f"{path.name}: developer_instructions must be a string")
            continue

        if not CURRENT_CODEX_FOOTER_RE.search(instructions):
            missing_current_footer.append(member_id)
        if LEGACY_CODEX_FOOTER_RE.search(instructions):
            legacy_footers.append(member_id)

        for identifier in CLAUDE_ONLY_TOOL_IDENTIFIERS:
            if re.search(rf"\b{re.escape(identifier)}\b", instructions):
                forbidden_tools.append(f"{member_id}: {identifier}")

        if (
            member_id in leaf_members
            and CODEX_LEAF_BOUNDARY not in instructions.lower()
        ):
            leaf_members_missing_boundary.append(member_id)

    summary["invalid_codex_member_toml"] = invalid_toml
    summary["codex_members_missing_current_footer"] = missing_current_footer
    summary["codex_members_with_legacy_footer"] = legacy_footers
    summary["codex_forbidden_claude_tool_identifiers"] = forbidden_tools
    summary["codex_leaf_member_count"] = len(leaf_members)
    summary["codex_leaf_members_missing_no_delegation_boundary"] = (
        leaf_members_missing_boundary
    )

    if invalid_toml:
        errors.append("invalid Codex member TOML: " + ", ".join(invalid_toml[:5]))
    if missing_current_footer:
        errors.append(
            "Codex members missing current linked-skills footer: "
            + ", ".join(missing_current_footer[:10])
        )
    if legacy_footers:
        errors.append(
            "Codex members retain legacy footer text: "
            + ", ".join(legacy_footers[:10])
        )
    if forbidden_tools:
        errors.append(
            "Codex instructions name Claude-only tool identifiers: "
            + ", ".join(forbidden_tools[:10])
        )
    if leaf_members_missing_boundary:
        errors.append(
            "Codex leaf members missing no-delegation boundary: "
            + ", ".join(leaf_members_missing_boundary[:10])
            + (" ..." if len(leaf_members_missing_boundary) > 10 else "")
        )


def checked_files() -> list[Path]:
    return sorted(
        path
        for base in (ROOT, AGENTS_DIR)
        for path in base.rglob("*")
        if path.is_file()
        and path.suffix in CHECKED_EXTENSIONS
        and ".archive" not in path.parts
    )


def check_template_counts(summary: dict[str, object], errors: list[str]) -> None:
    counts: dict[str, int] = {}
    for key, (directory, expected) in EXPECTED_TEMPLATE_COUNTS.items():
        actual = len(markdown_files_without_readme(directory)) if directory.exists() else 0
        counts[key] = actual
        if expected is not None and actual != expected:
            errors.append(f"{key}: expected {expected}, found {actual}")
    summary["template_counts"] = counts


def check_duplicate_template_titles(summary: dict[str, object], errors: list[str]) -> None:
    seen: dict[str, list[str]] = {}
    for directory, _expected in EXPECTED_TEMPLATE_COUNTS.values():
        if not directory.exists():
            continue
        for path in markdown_files_without_readme(directory):
            seen.setdefault(first_heading(path), []).append(str(rel(path)))
    duplicates = {title: paths for title, paths in seen.items() if len(paths) > 1}
    summary["duplicate_template_titles"] = duplicates
    for title, paths in sorted(duplicates.items()):
        errors.append(f"duplicate template title {title!r}: {', '.join(paths)}")


def check_stale_count_text(summary: dict[str, object], errors: list[str]) -> None:
    hits: dict[str, list[str]] = {key: [] for key in STALE_COUNT_PATTERNS}
    for path in checked_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for key, pattern in STALE_COUNT_PATTERNS.items():
            if pattern.search(text):
                hits[key].append(str(rel(path)))
    summary["stale_count_hits"] = {key: value for key, value in hits.items() if value}
    for key, paths in sorted(summary["stale_count_hits"].items()):
        errors.append(f"{key}: stale count text in {', '.join(paths)}")


def debate_enabled_team_count() -> int:
    count = 0
    for path in sorted(TEAMS_DIR.glob("*/team.yaml")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        block = re.search(r"^debate:\s*$\n((?:^[ \t].*(?:\n|$))*)", text, re.MULTILINE)
        if block and re.search(r"^\s+enabled:\s*true\s*$", block.group(1), re.MULTILINE):
            count += 1
    return count


def find_catalog_count_mismatches(
    text: str, *, members: int, teams: int, debate_teams: int
) -> list[str]:
    expected = {
        "members": members,
        "teams": teams,
        "debate_teams": debate_teams,
    }
    mismatches: list[str] = []
    for label, (pattern, kind) in CATALOG_COUNT_PATTERNS.items():
        for match in pattern.finditer(text):
            observed = int(match.group(1))
            if observed != expected[kind]:
                mismatches.append(
                    f"{label}: found {observed}, expected {expected[kind]}"
                )
    return mismatches


def check_catalog_count_text(summary: dict[str, object], errors: list[str]) -> None:
    member_count = len(list(CLAUDE_MEMBERS.glob("*.md")))
    team_count = len(list(TEAMS_DIR.glob("*/team.yaml")))
    debate_count = debate_enabled_team_count()
    hits: dict[str, list[str]] = {}
    for path in checked_files():
        mismatches = find_catalog_count_mismatches(
            path.read_text(encoding="utf-8", errors="ignore"),
            members=member_count,
            teams=team_count,
            debate_teams=debate_count,
        )
        if mismatches:
            hits[str(rel(path))] = mismatches
    summary["catalog_count_expectations"] = {
        "members": member_count,
        "teams": team_count,
        "debate_enabled_teams": debate_count,
    }
    summary["catalog_count_mismatches"] = hits
    for path, mismatches in sorted(hits.items()):
        errors.append(f"catalog count drift in {path}: " + "; ".join(mismatches))


def member_description(text: str) -> str:
    frontmatter, _ = frontmatter_and_body(text)
    match = re.search(r"^description:\s*(.*?)(?=\n\w+:|\Z)", frontmatter, re.S | re.M)
    return match.group(1).strip().strip('"') if match else ""


def check_description_budget(summary: dict[str, object], errors: list[str]) -> None:
    """Keep the routing catalog under Claude Code's agent-description token ceiling."""
    total = 0
    too_long: list[str] = []
    for path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        length = len(member_description(path.read_text(encoding="utf-8")))
        total += length
        if length > MEMBER_DESCRIPTION_MAX_CHARS:
            too_long.append(f"{path.stem} ({length})")
    summary["description_chars_total"] = total
    summary["description_chars_budget"] = CATALOG_DESCRIPTION_BUDGET_CHARS
    if too_long:
        errors.append(
            f"member descriptions over {MEMBER_DESCRIPTION_MAX_CHARS} chars: " + ", ".join(too_long)
        )
    if total > CATALOG_DESCRIPTION_BUDGET_CHARS:
        errors.append(
            f"catalog description total {total} chars exceeds budget "
            f"{CATALOG_DESCRIPTION_BUDGET_CHARS}; trim descriptions or the install set"
        )


def check_member_parity(summary: dict[str, object], errors: list[str]) -> None:
    claude_ids = {path.stem for path in CLAUDE_MEMBERS.glob("*.md")}
    codex_ids = {canonical_codex_id(path) for path in CODEX_MEMBERS.glob("*.toml")}
    missing_codex = sorted(claude_ids - codex_ids)
    orphan_codex = sorted(codex_ids - claude_ids)
    summary["claude_member_count"] = len(claude_ids)
    summary["codex_member_count"] = len(codex_ids)
    summary["missing_codex_members"] = missing_codex
    summary["orphan_codex_members"] = orphan_codex
    if missing_codex:
        errors.append("missing Codex members: " + ", ".join(missing_codex))
    if orphan_codex:
        errors.append("Codex members without Claude source: " + ", ".join(orphan_codex))


def check_codex_skill_footer_parity(summary: dict[str, object], errors: list[str]) -> None:
    mismatches: dict[str, dict[str, list[str]]] = {}
    for claude_path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        if claude_path.name == "README.md":
            continue
        member_id = claude_path.stem
        codex_path = CODEX_MEMBERS / f"{member_id.replace('-', '_')}.toml"
        if not codex_path.exists():
            continue
        frontmatter, _body = frontmatter_and_body(claude_path.read_text(encoding="utf-8"))
        claude_skills = sorted(frontmatter_list(frontmatter, "skills"))
        codex_skills = sorted(codex_linked_skills(codex_path.read_text(encoding="utf-8")))
        if claude_skills != codex_skills:
            mismatches[member_id] = {
                "claude": claude_skills,
                "codex": codex_skills,
            }
    summary["codex_skill_footer_mismatches"] = mismatches
    if mismatches:
        errors.append(
            "Codex linked-skill footers differ from Claude skills: "
            + ", ".join(sorted(mismatches))
        )


def check_codex_member_references(summary: dict[str, object], errors: list[str]) -> None:
    """Reject Claude-style aliases for known Codex custom-agent names.

    Codex registers the exact ``name`` value from each TOML file. Shared-skill
    IDs remain hyphenated, but a handoff to another catalog member must use its
    underscore-delimited Codex name. Restricting the check to aliases derived
    from registered names avoids treating ordinary hyphenated prose or unrelated
    shared-skill IDs as agent references.
    """
    parsed_members: list[tuple[Path, dict[str, object]]] = []
    registered_names: set[str] = set()
    for path in sorted(CODEX_MEMBERS.glob("*.toml")):
        try:
            member = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            # Other catalog checks surface malformed TOML; there is no reliable
            # developer_instructions value to inspect in that case.
            continue
        parsed_members.append((path, member))
        name = member.get("name")
        if isinstance(name, str):
            registered_names.add(name)

    legacy_aliases = {
        name.replace("_", "-"): name
        for name in registered_names
        if "_" in name
    }
    stale_references: list[str] = []
    for path, member in parsed_members:
        instructions = member.get("developer_instructions", "")
        if not isinstance(instructions, str):
            continue
        for alias, canonical_name in legacy_aliases.items():
            pattern = re.compile(
                rf"(?<![A-Za-z0-9_-]){re.escape(alias)}(?![A-Za-z0-9_-])"
            )
            for match in pattern.finditer(instructions):
                line = instructions.count("\n", 0, match.start()) + 1
                stale_references.append(
                    f"{path.name}:{line}: {alias} -> {canonical_name}"
                )

    summary["codex_hyphenated_member_references"] = stale_references
    if stale_references:
        errors.append(
            "Codex instructions use Claude-style member aliases "
            f"({len(stale_references)}): "
            + ", ".join(stale_references[:10])
            + (" ..." if len(stale_references) > 10 else "")
        )


def check_team_context_fields(summary: dict[str, object], errors: list[str]) -> None:
    missing: list[str] = []
    for path in sorted(TEAMS_DIR.glob("*/team.yaml")):
        text = path.read_text(encoding="utf-8")
        if "required_context:" not in text or "optional_context:" not in text:
            missing.append(path.parent.name)
    summary["team_count"] = len(list(TEAMS_DIR.glob("*/team.yaml")))
    summary["teams_missing_context_fields"] = missing
    if missing:
        errors.append("teams missing context fields: " + ", ".join(missing))


def check_team_design_rationales(summary: dict[str, object], errors: list[str]) -> None:
    """Every recipe must point from its own directory to a real rationale anchor."""
    invalid: list[str] = []
    for path in sorted(TEAMS_DIR.glob("*/team.yaml")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^design_rationale:\s*(\S+)\s*$", text, re.MULTILINE)
        if not match:
            invalid.append(f"{path.parent.name}: missing design_rationale")
            continue
        target = match.group(1)
        relative_path, separator, anchor = target.partition("#")
        resolved = (path.parent / relative_path).resolve()
        if not resolved.is_file():
            invalid.append(f"{path.parent.name}: missing {target}")
            continue
        if not separator or not anchor:
            invalid.append(f"{path.parent.name}: rationale has no anchor: {target}")
            continue
        rationale = resolved.read_text(encoding="utf-8")
        headings = {
            re.sub(r"[^a-z0-9 -]", "", heading.lower()).strip().replace(" ", "-")
            for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", rationale, re.MULTILINE)
        }
        if anchor not in headings:
            invalid.append(f"{path.parent.name}: missing anchor #{anchor}")
    summary["invalid_team_design_rationales"] = invalid
    if invalid:
        errors.append("invalid team design_rationale fields: " + "; ".join(invalid))


def check_team_member_matrix(summary: dict[str, object], errors: list[str]) -> None:
    """Regenerate the matrix in memory and fail if the checked-in snapshot drifts."""
    spec = importlib.util.spec_from_file_location(
        "generate_team_member_matrix", TEAM_MEMBER_MATRIX_GENERATOR
    )
    if not spec or not spec.loader:
        errors.append("could not load team-member matrix generator")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        members, teams = module.load_catalog()
        expected = module.render_matrix(members, teams)
    except ValueError as exc:
        errors.append(f"team/member catalog is invalid: {exc}")
        return
    actual = TEAM_MEMBER_MATRIX.read_text(encoding="utf-8") if TEAM_MEMBER_MATRIX.exists() else ""
    current = actual == expected
    summary["team_member_matrix_current"] = current
    if not current:
        errors.append(
            "references/team-member-matrix.md is stale; run "
            "scripts/generate_team_member_matrix.py"
        )


def check_context_first(summary: dict[str, object], errors: list[str]) -> None:
    missing_claude: list[str] = []
    missing_codex: list[str] = []
    for path in sorted(CLAUDE_MEMBERS.glob("*.md")):
        member_id = path.stem
        if member_id in CONTEXT_EXEMPT:
            continue
        if not CONTEXT_PATTERN.search(path.read_text(encoding="utf-8")):
            missing_claude.append(member_id)
    for path in sorted(CODEX_MEMBERS.glob("*.toml")):
        member_id = canonical_codex_id(path)
        if member_id in CONTEXT_EXEMPT:
            continue
        if not CONTEXT_PATTERN.search(path.read_text(encoding="utf-8")):
            missing_codex.append(member_id)
    summary["context_first_missing_claude"] = missing_claude
    summary["context_first_missing_codex"] = missing_codex
    if missing_claude:
        errors.append("Claude members missing context-first language: " + ", ".join(missing_claude))
    if missing_codex:
        errors.append("Codex members missing context-first language: " + ", ".join(missing_codex))


def check_team_coverage_duplicates(summary: dict[str, object], errors: list[str]) -> None:
    duplicate_rows: list[str] = []
    if not TEAM_COVERAGE.exists():
        errors.append("missing references/team-coverage.md")
        return

    for line_number, line in enumerate(TEAM_COVERAGE.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("|") or "`" not in line:
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) < 3 or columns[0].lower() in {"scenario", "---"}:
            continue
        skill_ids = re.findall(r"`([^`]+)`", columns[2])
        duplicates = sorted({skill_id for skill_id in skill_ids if skill_ids.count(skill_id) > 1})
        if duplicates:
            duplicate_rows.append(f"line {line_number}: {columns[0]} duplicates {', '.join(duplicates)}")

    summary["team_coverage_duplicate_skill_rows"] = duplicate_rows
    if duplicate_rows:
        errors.append("duplicate skill references in team coverage: " + "; ".join(duplicate_rows))


def validate_model_policy(policy: object) -> list[str]:
    complaints: list[str] = []
    if not isinstance(policy, dict):
        return ["model policy must be a JSON object"]
    if type(policy.get("schema_version")) is not int or policy.get("schema_version") != 1:
        complaints.append("model policy schema_version must be integer 1")
    try:
        date.fromisoformat(policy.get("last_verified", ""))
    except (TypeError, ValueError):
        complaints.append("model policy last_verified must be a real ISO date")

    expected_root_keys = {
        "schema_version",
        "last_verified",
        "codex",
        "claude",
        "claude_global_subagent_override",
    }
    unknown_root_keys = sorted(set(policy) - expected_root_keys)
    missing_root_keys = sorted(expected_root_keys - set(policy))
    if unknown_root_keys:
        complaints.append("model policy has unknown keys: " + ", ".join(unknown_root_keys))
    if missing_root_keys:
        complaints.append("model policy is missing keys: " + ", ".join(missing_root_keys))

    override = policy.get("claude_global_subagent_override")
    if not isinstance(override, dict):
        complaints.append("model policy claude_global_subagent_override must be an object")
    else:
        allowed_override_keys = {"allowed_models"}
        unknown_override_keys = sorted(set(override) - allowed_override_keys)
        missing_override_keys = sorted(allowed_override_keys - set(override))
        if unknown_override_keys:
            complaints.append(
                "model policy claude_global_subagent_override has unknown keys: "
                + ", ".join(unknown_override_keys)
            )
        if missing_override_keys:
            complaints.append("model policy claude_global_subagent_override is missing keys: allowed_models")
        allowed_models = override.get("allowed_models")
        if not isinstance(allowed_models, list) or not allowed_models:
            complaints.append(
                "model policy claude_global_subagent_override allowed_models must be a non-empty list"
            )
        elif any(
            not isinstance(model, str) or not MODEL_NAME_RE.fullmatch(model)
            for model in allowed_models
        ) or len(set(allowed_models)) != len(allowed_models):
            complaints.append(
                "model policy claude_global_subagent_override allowed_models must contain unique safe model IDs"
            )

    expected_runtime_keys = {"codex", "claude"}
    runtime_keys = {key for key in policy if key in expected_runtime_keys}
    if runtime_keys != expected_runtime_keys:
        complaints.append("model policy must contain codex and claude runtime maps")
    for runtime in sorted(expected_runtime_keys):
        tiers = policy.get(runtime)
        if not isinstance(tiers, dict):
            complaints.append(f"model policy {runtime} must be an object")
            continue
        if set(tiers) != MODEL_TIERS:
            complaints.append(f"model policy {runtime} tiers must be exactly {sorted(MODEL_TIERS)}")
        for tier in sorted(MODEL_TIERS & set(tiers)):
            entry = tiers[tier]
            if not isinstance(entry, dict):
                complaints.append(f"model policy {runtime}/{tier} must be an object")
                continue
            model = entry.get("model")
            if not isinstance(model, str) or not MODEL_NAME_RE.fullmatch(model):
                complaints.append(f"model policy {runtime}/{tier} has unsafe model value")
            effort_key = "model_reasoning_effort" if runtime == "codex" else "effort"
            if entry.get(effort_key) not in EFFORTS:
                complaints.append(f"model policy {runtime}/{tier} has invalid {effort_key}")
            allowed = {"model", effort_key} | ({"materialize"} if runtime == "codex" else set())
            if set(entry) - allowed:
                complaints.append(f"model policy {runtime}/{tier} has unknown keys")
            if runtime == "codex":
                materialize = entry.get("materialize", True)
                if not isinstance(materialize, bool):
                    complaints.append(f"model policy codex/{tier} materialize must be boolean")
                expected_materialize = tier != "standard"
                if materialize is not expected_materialize:
                    complaints.append(
                        f"model policy codex/{tier} materialize must be {str(expected_materialize).lower()}"
                    )
    return complaints


def load_model_policy(summary: dict[str, object], errors: list[str]) -> dict:
    try:
        policy = json.loads(MODEL_POLICY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"model policy could not be loaded: {exc}")
        summary["model_policy"] = {"status": "FAIL"}
        return {}
    complaints = validate_model_policy(policy)
    summary["model_policy"] = {
        "status": "PASS" if not complaints else "FAIL",
        "path": str(MODEL_POLICY_FILE),
        "errors": complaints,
    }
    errors.extend(complaints)
    return policy if not complaints else {}


def check_codex_model_pins(summary: dict[str, object], errors: list[str], policy: dict) -> None:
    """Reject executable pins and verify symbolic Claude/Codex tier parity."""
    pinned: list[str] = []
    invalid_tiers: list[str] = []
    parity_errors: list[str] = []
    for path in sorted(CODEX_MEMBERS.glob("*.toml")):
        member_id = canonical_codex_id(path)
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if re.match(r"^\s*(model|model_reasoning_effort)\s*=", line):
                pinned.append(f"{member_id}: {line.strip()}")
                break

        tier_match = re.search(r"^# model_tier: ([a-z-]+)$", text, re.MULTILINE)
        tier = tier_match.group(1) if tier_match else "standard"
        if tier not in MODEL_TIERS:
            invalid_tiers.append(f"{member_id}: {tier}")
            continue

        claude_path = CLAUDE_MEMBERS / f"{member_id}.md"
        claude_text = claude_path.read_text(encoding="utf-8") if claude_path.exists() else ""
        model_match = re.search(r"^model:\s*(\S+)$", claude_text, re.MULTILINE)
        effort_match = re.search(r"^effort:\s*(\S+)$", claude_text, re.MULTILINE)
        claude_pair = (
            model_match.group(1) if model_match else "",
            effort_match.group(1) if effort_match else "",
        )
        expected_pairs = {
            (entry.get("model"), entry.get("effort")): policy_tier
            for policy_tier, entry in policy.get("claude", {}).items()
            if isinstance(entry, dict)
        }
        expected = expected_pairs.get(claude_pair)
        if expected is None:
            parity_errors.append(
                f"{member_id}: unknown Claude model/effort {claude_pair[0] or '(missing)'}/"
                f"{claude_pair[1] or '(missing)'}"
            )
        elif tier != expected:
            parity_errors.append(f"{member_id}: Claude={expected}, Codex={tier}")

    summary["codex_members_with_model_pins"] = pinned
    summary["codex_invalid_model_tiers"] = invalid_tiers
    summary["cross_runtime_model_tier_parity"] = parity_errors
    if pinned:
        errors.append(
            f"Codex canonical members contain executable model pins "
            f"({len(pinned)}): " + ", ".join(pinned[:5])
            + (" ..." if len(pinned) > 5 else "")
        )
    if invalid_tiers:
        errors.append("invalid Codex model tiers: " + ", ".join(invalid_tiers[:5]))
    if parity_errors:
        errors.append("Claude/Codex model tier drift: " + ", ".join(parity_errors[:5]))


def check_generated_workflow_assets(summary: dict[str, object], errors: list[str]) -> None:
    """Keep every generated Claude workflow and Codex plan on its canonical manifest."""
    status: dict[str, bool] = {}
    spec = importlib.util.spec_from_file_location("validate_generate_workflows", WORKFLOWS_GENERATOR)
    if not spec or not spec.loader:
        errors.append(f"could not load workflow generator: {WORKFLOWS_GENERATOR.name}")
        summary["generated_workflow_assets_current"] = status
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for manifest in sorted(WORKFLOWS_DIR.glob("*.manifest.json")):
        try:
            expected = module.outputs(manifest)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            errors.append(f"cannot generate workflow from {manifest.name}: {error}")
            status[manifest.name] = False
            continue
        for output_path, text in expected.items():
            current = output_path.read_text(encoding="utf-8") if output_path.is_file() else None
            status[output_path.name] = current == text
            if current != text:
                errors.append(
                    f"stale generated workflow asset: agents/workflows/{output_path.name} "
                    f"(regenerate with {WORKFLOWS_GENERATOR.name})"
                )
    summary["generated_workflow_assets_current"] = status


def build_summary(strict_freshness: bool = False) -> tuple[dict[str, object], list[str]]:
    summary: dict[str, object] = {}
    errors: list[str] = []
    warnings: list[str] = []
    check_template_counts(summary, errors)
    check_duplicate_template_titles(summary, errors)
    check_stale_count_text(summary, errors)
    check_catalog_count_text(summary, errors)
    check_member_parity(summary, errors)
    check_description_budget(summary, errors)
    check_codex_runtime_contracts(summary, errors)
    check_codex_skill_footer_parity(summary, errors)
    check_codex_member_references(summary, errors)
    check_team_context_fields(summary, errors)
    check_team_design_rationales(summary, errors)
    check_team_member_matrix(summary, errors)
    check_generated_workflow_assets(summary, errors)
    check_context_first(summary, errors)
    check_team_coverage_duplicates(summary, errors)
    check_reference_links(summary, errors)
    check_installable_relative_links(summary, errors)
    check_body_similarity(summary, warnings)
    check_reference_stamp_freshness(summary, errors, warnings, strict=strict_freshness)
    check_citation_loss(summary, warnings)
    policy = load_model_policy(summary, errors)
    check_codex_model_pins(summary, errors, policy)
    summary["status"] = "PASS" if not errors else "FAIL"
    summary["errors"] = errors
    summary["warnings"] = warnings
    return summary, errors


def print_text(summary: dict[str, object]) -> None:
    print("=== Agents Subagents Catalog Integrity ===")
    print(f"Status: {summary['status']}")
    print("")
    print("Template counts:")
    for key, value in summary["template_counts"].items():
        print(f"  {key}: {value}")
    print("")
    print(f"Claude members: {summary['claude_member_count']}")
    print(f"Codex members: {summary['codex_member_count']}")
    print(f"Teams: {summary['team_count']}")
    print("")
    stale = summary.get("reference_stamp_stale") or []
    if stale:
        print(f"STALE STAMP ({len(stale)}) — last_verified predates the file's last commit:")
        for entry in stale:
            print(f"  ~ {entry['file']}: verified {entry['last_verified']} < commit {entry['last_commit']}")
        print("")
    unstamped = summary.get("reference_stamp_unstamped") or []
    if unstamped:
        print(f"NO last_verified ({len(unstamped)}):")
        for rel in unstamped:
            print(f"  ? {rel}")
        print("")

    warnings = summary.get("warnings", [])
    if warnings:
        print(f"Warnings ({len(warnings)}) — advisory, do not fail the build:")
        for warning in warnings:
            print(f"  ! {warning}")
        print("")

    if summary["status"] == "PASS":
        print(
            "PASS: counts, duplicate titles, stale prose, parity, context-first, "
            "Codex runtime contracts/skill footers/member references, "
            "team rationales/inventory, reference links, and team-coverage duplicate checks are clean"
        )
        return
    print("Errors:")
    for error in summary["errors"]:
        print(f"  - {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--strict-freshness",
        action="store_true",
        help="Fail (rather than warn) when a reference's last_verified predates its last git commit",
    )
    args = parser.parse_args()

    summary, errors = build_summary(strict_freshness=args.strict_freshness)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_text(summary)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
