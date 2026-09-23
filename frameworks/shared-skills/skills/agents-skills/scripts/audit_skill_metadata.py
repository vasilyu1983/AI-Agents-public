#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_skill import normalize_frontmatter_value, parse_frontmatter


DESCRIPTION_WORD_LIMIT = 25
DESCRIPTION_CHAR_LIMIT = 180
SHORT_DESCRIPTION_CHAR_LIMIT = 80
DEFAULT_PROMPT_CHAR_LIMIT = 220
LONG_SKILL_LINE_LIMIT = 250
VERY_LONG_SKILL_LINE_LIMIT = 350
TOP_LONG_SKILLS_LIMIT = 10
DEFAULT_BENCHMARK_MANIFEST = Path("evals/tasks/pilot-router-and-long-skills.json")
DEFAULT_COMPACT_DISCOVERY = Path("graph/codex-discovery.md")
LOCAL_COMPACT_DISCOVERY_CHAR_LIMIT = 8000
# Repository-local review thresholds. These make inventory growth visible but
# are not provider defaults and do not predict what any installed runtime loads.
# Runtime discovery must be measured separately in the target installation.
LOCAL_INVENTORY_WARNING_CHARS = 8000
LOCAL_INVENTORY_CRITICAL_CHARS = 16000
LOCAL_PER_DESCRIPTION_REVIEW_CHARS = 1536
SHORT_COVERAGE_THRESHOLD = 0.5
PROMPT_COVERAGE_THRESHOLD = 0.4
STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "as",
    "at",
    "before",
    "by",
    "do",
    "for",
    "from",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "use",
    "when",
    "with",
    "work",
}
RELATED_SKILLS_RE = re.compile(r"^##\s+related skills\b|^related skills:", re.IGNORECASE | re.MULTILINE)
DEFAULTS_RE = re.compile(r"^##\s+defaults\b", re.IGNORECASE | re.MULTILINE)
VERIFICATION_GATE_RE = re.compile(r"^##\s+verification gate\b", re.IGNORECASE | re.MULTILINE)
# Splices look like "Use $skill-name for Designs ..." — the description was
# pasted after "for" instead of rewritten. Anchor on the invocation token so a
# legitimate "... for Zones 1-3" is not flagged.
TEMPLATE_SPLICE_RE = re.compile(r"\$[a-z0-9-]+ for [A-Z][a-z]+s\b")
# A short_description that is a hard prefix of the description and stops mid
# sentence was cut with a character budget, not written. Anchor on the sentence
# boundary so a short_description that ends a real sentence is not flagged.
TRUNCATED_PREFIX_END_RE = re.compile(r"^\.(\s|$)")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit shared-skill descriptions and Codex UI metadata.")
    parser.add_argument("catalog_root", help="Path to the skills catalog root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on metadata warnings or invalid compact-index structure",
    )
    parser.add_argument(
        "--runtime-discovery-report",
        type=Path,
        help="Optional JSON report from scripts/audit-codex-discovery.py",
    )
    return parser.parse_args()


def skill_dirs(catalog_root: Path) -> list[Path]:
    return sorted(path for path in catalog_root.iterdir() if path.is_dir() and not path.name.startswith("."))


def parse_openai_interface(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    interface: dict[str, str] = {}
    in_interface = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if not in_interface:
            if stripped == "interface:":
                in_interface = True
            continue

        if indent == 0:
            break
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        interface[key.strip()] = normalize_frontmatter_value(value)

    return interface


def semantic_tokens(text: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(text.lower()) if len(token) > 2 and token not in STOPWORDS}


def coverage(required_tokens: set[str], actual_tokens: set[str]) -> float:
    if not required_tokens:
        return 1.0
    return round(len(required_tokens.intersection(actual_tokens)) / len(required_tokens), 2)


def is_truncated_prefix(short_description: str, description: str) -> bool:
    """True when short_description is the description chopped mid-sentence."""
    if short_description.endswith("."):
        return False
    if not description.startswith(short_description):
        return False
    remainder = description[len(short_description):]
    if not remainder:
        return False
    return not TRUNCATED_PREFIX_END_RE.match(remainder)


def audit_skill(skill_dir: Path) -> dict[str, object]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {
            "skill": skill_dir.name,
            "description": "",
            "description_words": 0,
            "description_chars": 0,
            "skill_lines": 0,
            "short_description": "",
            "short_description_chars": 0,
            "default_prompt": "",
            "default_prompt_chars": 0,
            "short_coverage": 0.0,
            "prompt_coverage": 0.0,
            "warnings": ["missing SKILL.md (stub or in-progress skill directory)"],
        }
    frontmatter, lines = parse_frontmatter(skill_md)
    description = str(frontmatter.get("description", ""))
    words = len(description.split())
    chars = len(description)
    text = skill_md.read_text(encoding="utf-8")

    interface = parse_openai_interface(skill_dir / "agents" / "openai.yaml")
    short_description = interface.get("short_description", "")
    default_prompt = interface.get("default_prompt", "")

    description_tokens = semantic_tokens(description)
    short_tokens = semantic_tokens(short_description)
    prompt_tokens = semantic_tokens(default_prompt.replace(f"${skill_dir.name}", ""))

    short_coverage = coverage(short_tokens, description_tokens)
    prompt_coverage = coverage(description_tokens, prompt_tokens)

    warnings: list[str] = []
    if words > DESCRIPTION_WORD_LIMIT:
        warnings.append(f"description words {words} > {DESCRIPTION_WORD_LIMIT}")
    if chars > DESCRIPTION_CHAR_LIMIT:
        warnings.append(f"description chars {chars} > {DESCRIPTION_CHAR_LIMIT}")
    if "Use when " not in description:
        warnings.append("description missing `Use when` trigger clause")
    if not short_description:
        warnings.append("missing interface.short_description")
    elif len(short_description) > SHORT_DESCRIPTION_CHAR_LIMIT:
        warnings.append(f"short_description chars {len(short_description)} > {SHORT_DESCRIPTION_CHAR_LIMIT}")
    if short_description and is_truncated_prefix(short_description, description):
        warnings.append(
            "short_description is a hard prefix of the SKILL.md description cut "
            "mid-sentence; write a complete <=80-char sentence"
        )
    if short_description and short_coverage < SHORT_COVERAGE_THRESHOLD:
        warnings.append(f"short_description semantic coverage {short_coverage:.2f} < {SHORT_COVERAGE_THRESHOLD:.2f}")
    if not default_prompt:
        warnings.append("missing interface.default_prompt")
    else:
        if len(default_prompt) > DEFAULT_PROMPT_CHAR_LIMIT:
            warnings.append(f"default_prompt chars {len(default_prompt)} > {DEFAULT_PROMPT_CHAR_LIMIT}")
        if f"${skill_dir.name}" not in default_prompt:
            warnings.append("default_prompt missing `$skill-name` invocation token")
        if TEMPLATE_SPLICE_RE.search(default_prompt):
            warnings.append(
                'default_prompt reads as a template splice ("for <Verb>s ..."); '
                'rewrite as "Use $name to <verb> ..." or "... when ..."'
            )
        if prompt_coverage < PROMPT_COVERAGE_THRESHOLD:
            warnings.append(f"default_prompt semantic coverage {prompt_coverage:.2f} < {PROMPT_COVERAGE_THRESHOLD:.2f}")

    return {
        "skill": skill_dir.name,
        "description": description,
        "description_words": words,
        "description_chars": chars,
        "short_description": short_description,
        "short_description_chars": len(short_description),
        "default_prompt": default_prompt,
        "default_prompt_chars": len(default_prompt),
        "strings_differ": bool(short_description and short_description != description),
        "short_description_coverage": short_coverage,
        "default_prompt_coverage": prompt_coverage,
        "skill_lines": len(lines),
        "is_long_skill": len(lines) > LONG_SKILL_LINE_LIMIT,
        "has_related_skills": bool(RELATED_SKILLS_RE.search(text)),
        "has_defaults": bool(DEFAULTS_RE.search(text)),
        "has_verification_gate": bool(VERIFICATION_GATE_RE.search(text)),
        "warnings": warnings,
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, int]:
    return {
        "skills": len(rows),
        "skills_with_warnings": sum(1 for row in rows if row["warnings"]),
        "description_budget_warnings": sum(
            1
            for row in rows
            if any(str(item).startswith("description ") for item in row["warnings"])
        ),
        "ui_budget_warnings": sum(
            1
            for row in rows
            if any(
                str(item).startswith("short_description") or str(item).startswith("default_prompt")
                for item in row["warnings"]
            )
        ),
        "long_skills": sum(1 for row in rows if row["is_long_skill"]),
        "very_long_skills": sum(1 for row in rows if int(row["skill_lines"]) > VERY_LONG_SKILL_LINE_LIMIT),
        "with_defaults": sum(1 for row in rows if row["has_defaults"]),
        "with_verification_gate": sum(1 for row in rows if row["has_verification_gate"]),
    }


def compute_description_budget(rows: list[dict[str, object]]) -> dict[str, object]:
    """Measure source inventory against local review thresholds.

    This function does not know which skills an installed runtime discovers,
    which metadata it injects, or the runtime's effective context budget.
    """
    skills_with_description = [row for row in rows if int(row["description_chars"]) > 0]
    total_chars = sum(int(row["description_chars"]) for row in skills_with_description)
    over_per_entry_cap = sorted(
        (
            {"skill": str(row["skill"]), "chars": int(row["description_chars"])}
            for row in skills_with_description
            if int(row["description_chars"]) > LOCAL_PER_DESCRIPTION_REVIEW_CHARS
        ),
        key=lambda item: (-item["chars"], item["skill"]),
    )
    inventory_level = "ok"
    if total_chars > LOCAL_INVENTORY_CRITICAL_CHARS:
        inventory_level = "critical"
    elif total_chars > LOCAL_INVENTORY_WARNING_CHARS:
        inventory_level = "warning"
    return {
        "skills_counted": len(skills_with_description),
        "total_chars": total_chars,
        "average_chars": round(total_chars / max(1, len(skills_with_description)), 1),
        "scope": "repository_source_inventory",
        "threshold_basis": "repository-local review heuristics; not provider runtime limits",
        "local_warning_threshold": LOCAL_INVENTORY_WARNING_CHARS,
        "local_critical_threshold": LOCAL_INVENTORY_CRITICAL_CHARS,
        "local_per_description_review_threshold": LOCAL_PER_DESCRIPTION_REVIEW_CHARS,
        "inventory_level": inventory_level,
        "runtime_load_status": "unknown",
        "runtime_load_evidence": None,
        # Deprecated provider-named keys remain present so consumers can detect
        # the schema transition without receiving invented provider defaults.
        "codex_budget": None,
        "claude_code_budget": None,
        "legacy_anthropic_budget": None,
        "per_entry_cap": LOCAL_PER_DESCRIPTION_REVIEW_CHARS,
        "fits_codex_default": None,
        "fits_legacy_anthropic": None,
        "legacy_field_semantics": (
            "deprecated provider-named fields are intentionally null; use the explicit "
            "repository-local thresholds"
        ),
        "over_per_entry_cap": over_per_entry_cap,
        "risk_level": inventory_level,
    }


def compact_discovery_summary(catalog_root: Path) -> dict[str, object]:
    discovery_path = catalog_root.parent / DEFAULT_COMPACT_DISCOVERY
    if not discovery_path.exists():
        return {
            "path": str(discovery_path),
            "exists": False,
            "chars": 0,
            "budget": LOCAL_COMPACT_DISCOVERY_CHAR_LIMIT,
            "fits_budget": False,
            "generated": False,
            "structural_status": "missing",
            "structurally_valid": False,
            "runtime_load_status": "unknown",
            "runtime_load_evidence": None,
        }

    try:
        text = discovery_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {
            "path": str(discovery_path),
            "exists": True,
            "chars": 0,
            "budget": LOCAL_COMPACT_DISCOVERY_CHAR_LIMIT,
            "fits_budget": False,
            "generated": False,
            "structural_status": "unreadable",
            "structurally_valid": False,
            "read_error": f"{type(exc).__name__}: {exc}",
            "runtime_load_status": "unknown",
            "runtime_load_evidence": None,
        }

    fits_budget = len(text) <= LOCAL_COMPACT_DISCOVERY_CHAR_LIMIT
    generated = "Generated compact discovery map for Codex" in text
    structural_status = "valid"
    if not fits_budget:
        structural_status = "over_local_limit"
    elif not generated:
        structural_status = "unrecognized_format"
    return {
        "path": str(discovery_path),
        "exists": True,
        "chars": len(text),
        "budget": LOCAL_COMPACT_DISCOVERY_CHAR_LIMIT,
        "fits_budget": fits_budget,
        "generated": generated,
        "structural_status": structural_status,
        "structurally_valid": structural_status == "valid",
        "runtime_load_status": "unknown",
        "runtime_load_evidence": None,
    }


def runtime_discovery_summary(report_path: Path | None) -> dict[str, object]:
    """Read optional installed-runtime discovery evidence without overclaiming prompt load."""
    if report_path is None:
        return {
            "status": "not_provided",
            "discovery_observed": False,
            "model_prompt_inclusion_status": "unknown",
            "compact_index_use_status": "unknown",
        }

    resolved = report_path.resolve()
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise ValueError("expected an object with schema_version 1")
        entries = payload.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError("expected at least one entries item")
        if any(not isinstance(entry, dict) for entry in entries):
            raise ValueError("every entries item must be an object")
        for entry in entries:
            for key in ("missing_repository_skills", "shadowed_repository_skills", "errors"):
                if not isinstance(entry.get(key), list):
                    raise ValueError(f"entries.{key} must be a list")
            for key in ("repository_skill_count", "repository_enabled_count"):
                if not isinstance(entry.get(key), int):
                    raise ValueError(f"entries.{key} must be an integer")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return {
            "status": "invalid",
            "report": str(resolved),
            "error": f"{type(exc).__name__}: {exc}",
            "discovery_observed": False,
            "model_prompt_inclusion_status": "unknown",
            "compact_index_use_status": "unknown",
        }

    missing = sum(len(entry.get("missing_repository_skills", [])) for entry in entries)
    shadowed = sum(len(entry.get("shadowed_repository_skills", [])) for entry in entries)
    loader_errors = sum(len(entry.get("errors", [])) for entry in entries)
    prompt_observed = payload.get("model_visible_prompt_observed") is True
    return {
        "status": "observed",
        "report": str(resolved),
        "observation": str(payload.get("observation", "")),
        "observed_at_utc": str(payload.get("observed_at_utc", "")),
        "runtime_version": str(payload.get("codex_version", "")),
        "discovery_observed": True,
        "repository_skill_count": sum(int(entry.get("repository_skill_count", 0)) for entry in entries),
        "repository_enabled_count": sum(int(entry.get("repository_enabled_count", 0)) for entry in entries),
        "missing_repository_skills": missing,
        "shadowed_repository_skills": shadowed,
        "loader_errors": loader_errors,
        "model_prompt_inclusion_status": "observed" if prompt_observed else "unknown",
        "compact_index_use_status": "unknown",
        "caveat": str(payload.get("caveat", "")),
    }


def benchmark_manifest_for(catalog_root: Path) -> Path:
    return catalog_root.parent / DEFAULT_BENCHMARK_MANIFEST


def load_benchmark_skill_names(catalog_root: Path) -> tuple[Path | None, set[str]]:
    manifest_path = benchmark_manifest_for(catalog_root)
    if not manifest_path.exists():
        return None, set()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    benchmark_skills: set[str] = set()
    for task in payload.get("tasks", []):
        for path in task.get("curated_paths", []):
            if isinstance(path, str) and path.endswith("/SKILL.md"):
                benchmark_skills.add(Path(path).parent.name)
        for skill in task.get("expected_skills", []):
            if isinstance(skill, str) and skill:
                benchmark_skills.add(skill)
    return manifest_path, benchmark_skills


def summarize_benchmark_coverage(
    rows: list[dict[str, object]],
    manifest_path: Path | None,
    benchmark_skills: set[str],
) -> dict[str, object] | None:
    if manifest_path is None:
        return None

    long_rows = [row for row in rows if row["is_long_skill"]]
    long_with_benchmark = [row for row in long_rows if str(row["skill"]) in benchmark_skills]
    very_long_without_benchmark = sorted(
        (
            {"skill": str(row["skill"]), "skill_lines": int(row["skill_lines"])}
            for row in rows
            if int(row["skill_lines"]) > VERY_LONG_SKILL_LINE_LIMIT and str(row["skill"]) not in benchmark_skills
        ),
        key=lambda row: (row["skill_lines"], row["skill"]),
        reverse=True,
    )

    return {
        "manifest": str(manifest_path),
        "benchmarked_skills": len(benchmark_skills),
        "long_skills_with_benchmark": len(long_with_benchmark),
        "long_skills_without_benchmark": len(long_rows) - len(long_with_benchmark),
        "very_long_skills_without_benchmark": very_long_without_benchmark,
    }


def top_long_skills(
    rows: list[dict[str, object]],
    limit: int = TOP_LONG_SKILLS_LIMIT,
    benchmark_skills: set[str] | None = None,
) -> list[dict[str, object]]:
    ranked = sorted(rows, key=lambda row: (int(row["skill_lines"]), str(row["skill"])), reverse=True)
    output: list[dict[str, object]] = []
    for row in ranked[:limit]:
        item: dict[str, object] = {"skill": str(row["skill"]), "skill_lines": int(row["skill_lines"])}
        if benchmark_skills is not None:
            item["has_benchmark_task"] = str(row["skill"]) in benchmark_skills
        output.append(item)
    return output


def print_markdown(
    catalog_root: Path,
    rows: list[dict[str, object]],
    runtime_discovery: dict[str, object],
) -> None:
    summary = summarize(rows)
    manifest_path, benchmark_skills = load_benchmark_skill_names(catalog_root)
    benchmark_summary = summarize_benchmark_coverage(rows, manifest_path, benchmark_skills)
    longest = top_long_skills(rows, benchmark_skills=benchmark_skills if manifest_path else None)
    budget = compute_description_budget(rows)
    compact_discovery = compact_discovery_summary(catalog_root)
    print("## Skill Metadata Audit Summary")
    print()
    print(f"- Catalog: `{catalog_root}`")
    print(f"- Skills: {summary['skills']}")
    print(f"- Skills with warnings: {summary['skills_with_warnings']}")
    print(f"- Description budget warnings: {summary['description_budget_warnings']}")
    print(f"- UI budget warnings: {summary['ui_budget_warnings']}")
    print(f"- Long skills (> {LONG_SKILL_LINE_LIMIT} lines): {summary['long_skills']}")
    print(f"- Very long skills (> {VERY_LONG_SKILL_LINE_LIMIT} lines): {summary['very_long_skills']}")
    print(f"- Skills with `Defaults`: {summary['with_defaults']}")
    print(f"- Skills with `Verification Gate`: {summary['with_verification_gate']}")
    print()

    inventory_label = {
        "ok": "OK",
        "warning": "WARNING (over the local review threshold)",
        "critical": "CRITICAL (over the local critical review threshold)",
    }[str(budget["risk_level"])]
    print("## Description Inventory")
    print(
        f"- Total description chars: {budget['total_chars']:,} across "
        f"{budget['skills_counted']} skills (avg {budget['average_chars']})"
    )
    print(
        f"- Local review threshold: {budget['local_warning_threshold']:,} chars "
        f"({'fits' if budget['total_chars'] <= budget['local_warning_threshold'] else 'OVER'})"
    )
    print(
        f"- Local critical threshold: {budget['local_critical_threshold']:,} chars "
        f"({'fits' if budget['total_chars'] <= budget['local_critical_threshold'] else 'OVER'})"
    )
    print(f"- Local per-entry review threshold: {budget['per_entry_cap']:,} chars")
    print(f"- Inventory level: {inventory_label}")
    print("- Runtime loading evidence: UNKNOWN (this audit reads repository files only)")
    if budget["over_per_entry_cap"]:
        print("- Skills over the local per-entry review threshold:")
        for item in list(budget["over_per_entry_cap"])[:TOP_LONG_SKILLS_LIMIT]:
            print(f"  - `{item['skill']}`: {item['chars']} chars")
    print()

    print("## Compact Discovery")
    print(f"- Path: `{compact_discovery['path']}`")
    print(f"- Exists: {'yes' if compact_discovery['exists'] else 'no'}")
    print(
        f"- Size: {compact_discovery['chars']:,}/{compact_discovery['budget']:,} chars "
        f"({'fits' if compact_discovery['fits_budget'] else 'OVER'})"
    )
    print(f"- Generated artifact: {'yes' if compact_discovery['generated'] else 'no'}")
    print(f"- Local structural status: {str(compact_discovery['structural_status']).upper()}")
    print(
        "- Runtime use: UNKNOWN (file structure does not prove that a runtime loads "
        "or substitutes this index)"
    )
    print()

    print("## Runtime Discovery Evidence")
    if runtime_discovery["status"] == "observed":
        print(f"- Observation: {runtime_discovery['observation']}")
        print(f"- Runtime version: {runtime_discovery['runtime_version']}")
        print(
            f"- Repository skills: {runtime_discovery['repository_skill_count']} discovered; "
            f"{runtime_discovery['repository_enabled_count']} enabled"
        )
        print(
            f"- Missing: {runtime_discovery['missing_repository_skills']}; "
            f"shadowed: {runtime_discovery['shadowed_repository_skills']}; "
            f"loader errors: {runtime_discovery['loader_errors']}"
        )
    elif runtime_discovery["status"] == "invalid":
        print(f"- Status: INVALID ({runtime_discovery['error']})")
    else:
        print("- Status: NOT PROVIDED")
    print(
        "- Model prompt inclusion: "
        f"{str(runtime_discovery['model_prompt_inclusion_status']).upper()}"
    )
    print("- Compact-index use: UNKNOWN")
    print()

    if benchmark_summary:
        print("## Benchmark Coverage")
        print(f"- Manifest: `{benchmark_summary['manifest']}`")
        print(f"- Skills referenced by benchmark manifest: {benchmark_summary['benchmarked_skills']}")
        print(
            f"- Long skills with benchmark tasks: {benchmark_summary['long_skills_with_benchmark']}/{summary['long_skills']}"
        )
        print(
            f"- Long skills without benchmark tasks: {benchmark_summary['long_skills_without_benchmark']}"
        )
        print(
            "- Very long skills without benchmark tasks: "
            f"{len(benchmark_summary['very_long_skills_without_benchmark'])}"
        )
        print()

    if longest:
        print("## Top Long Skills")
        for row in longest:
            suffix = ""
            if "has_benchmark_task" in row:
                suffix = " (benchmarked)" if row["has_benchmark_task"] else " (no benchmark task)"
            print(f"- `{row['skill']}`: {row['skill_lines']} lines{suffix}")
        print()

    if benchmark_summary and benchmark_summary["very_long_skills_without_benchmark"]:
        print("## Very Long Skills Without Benchmark Tasks")
        for row in benchmark_summary["very_long_skills_without_benchmark"][:TOP_LONG_SKILLS_LIMIT]:
            print(f"- `{row['skill']}`: {row['skill_lines']} lines")
        print()

    flagged = [row for row in rows if row["warnings"]]
    if not flagged:
        print(
            "Status: PASS (repository metadata and compact-index structure; "
            "runtime prompt loading not evaluated)"
        )
        return

    print("## Flagged Skills")
    for row in flagged:
        warning_text = "; ".join(str(item) for item in row["warnings"])
        print(f"- `{row['skill']}`: {warning_text}")


def main() -> int:
    args = parse_args()
    catalog_root = Path(args.catalog_root).resolve()
    rows = [audit_skill(skill_dir) for skill_dir in skill_dirs(catalog_root)]
    warning_count = sum(1 for row in rows if row["warnings"])
    manifest_path, benchmark_skills = load_benchmark_skill_names(catalog_root)
    benchmark_summary = summarize_benchmark_coverage(rows, manifest_path, benchmark_skills)
    runtime_discovery = runtime_discovery_summary(args.runtime_discovery_report)

    if args.json:
        compact_discovery = compact_discovery_summary(catalog_root)
        payload = {
            "catalog_root": str(catalog_root),
            "summary": summarize(rows),
            "description_budget": compute_description_budget(rows),
            "compact_discovery": compact_discovery,
            "top_long_skills": top_long_skills(rows, benchmark_skills=benchmark_skills if manifest_path else None),
            "benchmark_coverage": benchmark_summary,
            "runtime_discovery": runtime_discovery,
            "strict_gate": {
                "scope": "repository_metadata_and_compact_index_structure",
                "passes": (
                    warning_count == 0
                    and bool(compact_discovery["structurally_valid"])
                    and runtime_discovery["status"] != "invalid"
                ),
                "runtime_loading_evaluated": False,
            },
            "results": rows,
        }
        print(json.dumps(payload, indent=2))
    else:
        print_markdown(catalog_root, rows, runtime_discovery)

    compact_discovery = compact_discovery_summary(catalog_root)
    compact_discovery_ok = bool(compact_discovery["structurally_valid"])
    runtime_report_invalid = runtime_discovery["status"] == "invalid"
    return 1 if args.strict and (warning_count or not compact_discovery_ok or runtime_report_invalid) else 0


if __name__ == "__main__":
    sys.exit(main())
