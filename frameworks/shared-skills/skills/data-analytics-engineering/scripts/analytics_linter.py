#!/usr/bin/env python3
"""
analytics_linter.py — Metric Dictionary Validation and Linting CLI

Stdlib-only tool for validating, linting, and reporting on analytics metric
dictionaries. Deterministic scoring — no API or LLM calls.

Usage:
    python analytics_linter.py validate --input data/sample-metric-dictionary.json
    python analytics_linter.py lint --input data/sample-metric-dictionary.json
    python analytics_linter.py report --input data/sample-metric-dictionary.json --output report.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from typing import List, Optional


# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

USE_COLOR = True


def _c(code: str, text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(t):  return _c("32;1", t)
def yellow(t): return _c("33;1", t)
def red(t):    return _c("31;1", t)
def bold(t):   return _c("1", t)
def dim(t):    return _c("2", t)
def cyan(t):   return _c("36", t)


# ---------------------------------------------------------------------------
# Required fields and scoring constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "name",
    "description",
    "owner",
    "formula",
    "data_source",
    "refresh_cadence",
]

SCORE_WEIGHTS = {
    "description":     20,
    "owner":           20,
    "formula":         20,
    "data_source":     15,
    "refresh_cadence": 10,
    "dimensions":      10,
    "example_value":    5,
}
# total = 100

PRODUCTION_READY_THRESHOLD = 85
NEEDS_WORK_THRESHOLD       = 60

VALID_CATEGORIES = {"revenue", "product", "marketing", "support", "finance", "operations"}

NAMING_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_metric(metric: dict) -> int:
    """Return quality score 0-100 for a single metric."""
    score = 0
    if metric.get("description", "").strip():
        score += SCORE_WEIGHTS["description"]
    if metric.get("owner", "").strip():
        score += SCORE_WEIGHTS["owner"]
    if metric.get("formula", "").strip():
        score += SCORE_WEIGHTS["formula"]
    if metric.get("data_source", "").strip():
        score += SCORE_WEIGHTS["data_source"]
    if metric.get("refresh_cadence", "").strip():
        score += SCORE_WEIGHTS["refresh_cadence"]
    dims = metric.get("dimensions", [])
    if isinstance(dims, list) and len(dims) > 0:
        score += SCORE_WEIGHTS["dimensions"]
    ex = metric.get("example_value")
    if ex is not None and str(ex).strip():
        score += SCORE_WEIGHTS["example_value"]
    return score


def tier_label(avg_score: float) -> str:
    if avg_score >= PRODUCTION_READY_THRESHOLD:
        return "PRODUCTION_READY"
    if avg_score >= NEEDS_WORK_THRESHOLD:
        return "NEEDS_WORK"
    return "CRITICAL_GAPS"


def colorize_tier(tier: str) -> str:
    if tier == "PRODUCTION_READY":
        return green(tier)
    if tier == "NEEDS_WORK":
        return yellow(tier)
    return red(tier)


def colorize_score(score: int) -> str:
    if score >= PRODUCTION_READY_THRESHOLD:
        return green(str(score))
    if score >= NEEDS_WORK_THRESHOLD:
        return yellow(str(score))
    return red(str(score))


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_dictionary(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, dict):
        print(f"ERROR: {path} must be a JSON object, not an array.", file=sys.stderr)
        sys.exit(1)
    if "metrics" not in data:
        print(f"ERROR: {path} must contain a top-level 'metrics' array.", file=sys.stderr)
        sys.exit(1)
    return data


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def check_required_fields(metric: dict, idx: int) -> List[str]:
    """Return list of error strings for missing required fields."""
    errors = []
    name = metric.get("name") or f"<metric #{idx}>"
    for field in REQUIRED_FIELDS:
        val = metric.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"  [{name}] missing required field: '{field}'")
    return errors


def check_duplicate_names(metrics: list) -> List[str]:
    """Return error strings for duplicate metric names."""
    counts = Counter(m.get("name", "") for m in metrics)
    errors = []
    for name, count in counts.items():
        if count > 1:
            errors.append(f"  duplicate metric name: '{name}' appears {count} times")
    return errors


def check_undefined_sources(metrics: list) -> List[str]:
    """Flag metrics whose data_source is an empty string or looks like a placeholder."""
    warnings = []
    placeholder_pattern = re.compile(r"^\s*(tbd|todo|unknown|n/a|placeholder|\?\?\?)\s*$", re.I)
    for m in metrics:
        src = m.get("data_source", "")
        if placeholder_pattern.match(str(src)):
            warnings.append(f"  [{m.get('name', '?')}] data_source looks like a placeholder: '{src}'")
    return warnings


# ---------------------------------------------------------------------------
# Lint helpers
# ---------------------------------------------------------------------------

def lint_missing_owners(metrics: list) -> List[str]:
    issues = []
    for m in metrics:
        owner = m.get("owner", "")
        if not owner or not owner.strip():
            issues.append(f"  [{m.get('name', '?')}] no owner assigned")
    return issues


def lint_undocumented_dimensions(metrics: list) -> List[str]:
    issues = []
    for m in metrics:
        dims = m.get("dimensions", [])
        if not isinstance(dims, list) or len(dims) == 0:
            issues.append(f"  [{m.get('name', '?')}] no dimensions listed — add at least one slice dimension")
    return issues


def lint_naming_conventions(metrics: list) -> List[str]:
    issues = []
    for m in metrics:
        name = m.get("name", "")
        if name and not NAMING_PATTERN.match(name):
            issues.append(
                f"  [{name}] name does not follow snake_case convention "
                f"(expected lowercase letters, digits, underscores only)"
            )
    return issues


def lint_missing_slas(metrics: list) -> List[str]:
    """Flag metrics with no SLA-related information (no sla field and no refresh_cadence)."""
    issues = []
    for m in metrics:
        has_sla = bool(m.get("sla", "").strip()) if isinstance(m.get("sla"), str) else bool(m.get("sla"))
        has_cadence = bool(m.get("refresh_cadence", "").strip())
        if not has_sla and not has_cadence:
            issues.append(f"  [{m.get('name', '?')}] no SLA or refresh_cadence defined")
    return issues


def lint_short_descriptions(metrics: list) -> List[str]:
    """Flag metrics whose description is suspiciously short (< 20 chars)."""
    issues = []
    for m in metrics:
        desc = m.get("description", "")
        if desc and len(desc.strip()) < 20:
            issues.append(
                f"  [{m.get('name', '?')}] description is very short ({len(desc.strip())} chars) — "
                "consider expanding it"
            )
    return issues


def lint_unknown_category(metrics: list) -> List[str]:
    issues = []
    for m in metrics:
        cat = m.get("category", "")
        if cat and cat.lower() not in VALID_CATEGORIES:
            issues.append(
                f"  [{m.get('name', '?')}] unrecognized category: '{cat}' "
                f"(known: {', '.join(sorted(VALID_CATEGORIES))})"
            )
    return issues


# ---------------------------------------------------------------------------
# Subcommand: validate
# ---------------------------------------------------------------------------

def cmd_validate(args: argparse.Namespace) -> int:
    data = load_dictionary(args.input)
    metrics = data["metrics"]

    print()
    print(bold(f"  METRIC DICTIONARY VALIDATION"))
    print(bold(f"  File:    {args.input}"))
    print(bold(f"  Company: {data.get('company_name', 'N/A')}"))
    print(bold(f"  Updated: {data.get('last_updated', 'N/A')}"))
    print(bold(f"  Metrics: {len(metrics)}"))
    print()

    all_errors: List[str] = []

    # Required fields check
    field_errors = []
    for idx, metric in enumerate(metrics, 1):
        field_errors.extend(check_required_fields(metric, idx))

    if field_errors:
        print(red("  [FAIL] Required fields — missing values detected:"))
        for e in field_errors:
            print(e)
        all_errors.extend(field_errors)
    else:
        print(green("  [PASS] Required fields — all metrics have required fields"))
    print()

    # Duplicate names
    dup_errors = check_duplicate_names(metrics)
    if dup_errors:
        print(red("  [FAIL] Duplicate metric names:"))
        for e in dup_errors:
            print(e)
        all_errors.extend(dup_errors)
    else:
        print(green("  [PASS] Metric names — no duplicates found"))
    print()

    # Undefined sources
    src_warnings = check_undefined_sources(metrics)
    if src_warnings:
        print(yellow("  [WARN] Placeholder data sources:"))
        for w in src_warnings:
            print(w)
    else:
        print(green("  [PASS] Data sources — no placeholders detected"))
    print()

    # Summary
    if all_errors:
        print(red(f"  RESULT: VALIDATION FAILED — {len(all_errors)} error(s), {len(src_warnings)} warning(s)"))
        return 1
    elif src_warnings:
        print(yellow(f"  RESULT: VALIDATION PASSED WITH WARNINGS — {len(src_warnings)} warning(s)"))
        return 0
    else:
        print(green("  RESULT: VALIDATION PASSED — dictionary is structurally sound"))
        return 0


# ---------------------------------------------------------------------------
# Subcommand: lint
# ---------------------------------------------------------------------------

def cmd_lint(args: argparse.Namespace) -> int:
    data = load_dictionary(args.input)
    metrics = data["metrics"]

    print()
    print(bold(f"  METRIC QUALITY LINT"))
    print(bold(f"  File:    {args.input}"))
    print(bold(f"  Company: {data.get('company_name', 'N/A')}"))
    print(bold(f"  Metrics: {len(metrics)}"))
    print()

    checks = [
        ("Missing owners",            lint_missing_owners(metrics),         "WARN"),
        ("Undocumented dimensions",    lint_undocumented_dimensions(metrics), "WARN"),
        ("Naming convention issues",   lint_naming_conventions(metrics),     "WARN"),
        ("Missing SLAs",              lint_missing_slas(metrics),           "WARN"),
        ("Short descriptions",        lint_short_descriptions(metrics),     "INFO"),
        ("Unknown categories",        lint_unknown_category(metrics),       "WARN"),
    ]

    total_issues = 0
    for check_name, issues, severity in checks:
        if issues:
            color_fn = yellow if severity == "WARN" else dim
            print(color_fn(f"  [{severity}] {check_name} — {len(issues)} issue(s):"))
            for issue in issues:
                print(issue)
            total_issues += len(issues)
        else:
            print(green(f"  [ OK ] {check_name}"))
        print()

    # Per-metric quality scores
    print(bold("  METRIC QUALITY SCORES"))
    print()
    print(f"  {'Metric':<35} {'Score':>5}  {'Tier':<18}  Category")
    print("  " + "-" * 75)

    scores = []
    for m in metrics:
        s = score_metric(m)
        scores.append(s)
        t = tier_label(s)
        name = m.get("name", "?")[:34]
        cat = m.get("category", "")
        print(f"  {name:<35} {colorize_score(s):>5}  {colorize_tier(t):<18}  {cat}")

    avg = sum(scores) / len(scores) if scores else 0
    overall_tier = tier_label(avg)
    print()
    print(bold(f"  OVERALL DICTIONARY HEALTH: {colorize_score(int(avg))} / 100  →  {colorize_tier(overall_tier)}"))
    print()

    if total_issues:
        print(yellow(f"  {total_issues} lint issue(s) found. Review and address flagged items."))
        return 1
    else:
        print(green("  No lint issues found."))
        return 0


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> int:
    data = load_dictionary(args.input)
    metrics = data["metrics"]
    today = date.today().isoformat()

    # Compute scores
    metric_scores = [(m, score_metric(m)) for m in metrics]
    avg_score = sum(s for _, s in metric_scores) / len(metric_scores) if metric_scores else 0
    overall_tier = tier_label(avg_score)

    # Category breakdown
    cat_scores: dict[str, List[int]] = {}
    for m, s in metric_scores:
        cat = m.get("category", "uncategorized")
        cat_scores.setdefault(cat, []).append(s)

    # Lint issues
    all_lint_issues: List[str] = []
    all_lint_issues.extend(lint_missing_owners(metrics))
    all_lint_issues.extend(lint_undocumented_dimensions(metrics))
    all_lint_issues.extend(lint_naming_conventions(metrics))
    all_lint_issues.extend(lint_missing_slas(metrics))
    all_lint_issues.extend(lint_short_descriptions(metrics))
    all_lint_issues.extend(lint_unknown_category(metrics))

    # Validation issues
    val_errors: List[str] = []
    for idx, m in enumerate(metrics, 1):
        val_errors.extend(check_required_fields(m, idx))
    val_errors.extend(check_duplicate_names(metrics))
    val_warnings = check_undefined_sources(metrics)

    lines = []
    add = lines.append

    add(f"# Metric Dictionary Health Report")
    add(f"")
    add(f"**Company:** {data.get('company_name', 'N/A')}  ")
    add(f"**Last updated:** {data.get('last_updated', 'N/A')}  ")
    add(f"**Report generated:** {today}  ")
    add(f"**Source file:** `{os.path.basename(args.input)}`  ")
    add(f"**Total metrics:** {len(metrics)}  ")
    add(f"")

    add(f"## Executive Summary")
    add(f"")
    add(f"| Metric | Value |")
    add(f"|--------|-------|")
    add(f"| Overall health score | **{avg_score:.1f} / 100** |")
    add(f"| Health tier | **{overall_tier}** |")
    add(f"| Validation errors | {len(val_errors)} |")
    add(f"| Validation warnings | {len(val_warnings)} |")
    add(f"| Lint issues | {len(all_lint_issues)} |")
    add(f"| Metrics scored PRODUCTION_READY (≥{PRODUCTION_READY_THRESHOLD}) | {sum(1 for _, s in metric_scores if s >= PRODUCTION_READY_THRESHOLD)} |")
    add(f"| Metrics scored NEEDS_WORK ({NEEDS_WORK_THRESHOLD}–{PRODUCTION_READY_THRESHOLD - 1}) | {sum(1 for _, s in metric_scores if NEEDS_WORK_THRESHOLD <= s < PRODUCTION_READY_THRESHOLD)} |")
    add(f"| Metrics scored CRITICAL_GAPS (<{NEEDS_WORK_THRESHOLD}) | {sum(1 for _, s in metric_scores if s < NEEDS_WORK_THRESHOLD)} |")
    add(f"")

    add(f"## Scoring Methodology")
    add(f"")
    add(f"Each metric is scored 0–100 based on documentation completeness:")
    add(f"")
    add(f"| Field | Points |")
    add(f"|-------|-------:|")
    for field, pts in SCORE_WEIGHTS.items():
        add(f"| `{field}` | +{pts} |")
    add(f"")
    add(f"**Health tiers:**")
    add(f"- PRODUCTION_READY: ≥{PRODUCTION_READY_THRESHOLD}")
    add(f"- NEEDS_WORK: {NEEDS_WORK_THRESHOLD}–{PRODUCTION_READY_THRESHOLD - 1}")
    add(f"- CRITICAL_GAPS: <{NEEDS_WORK_THRESHOLD}")
    add(f"")

    add(f"## Category Breakdown")
    add(f"")
    add(f"| Category | Metrics | Avg Score | Tier |")
    add(f"|----------|--------:|----------:|------|")
    for cat in sorted(cat_scores.keys()):
        cat_avg = sum(cat_scores[cat]) / len(cat_scores[cat])
        add(f"| {cat} | {len(cat_scores[cat])} | {cat_avg:.1f} | {tier_label(cat_avg)} |")
    add(f"")

    add(f"## Per-Metric Scorecard")
    add(f"")
    add(f"| Metric | Category | Score | Tier | Owner | Cadence |")
    add(f"|--------|----------|------:|------|-------|---------|")
    for m, s in metric_scores:
        t = tier_label(s)
        add(
            f"| `{m.get('name', '?')}` "
            f"| {m.get('category', '')} "
            f"| {s} "
            f"| {t} "
            f"| {m.get('owner', '_missing_')} "
            f"| {m.get('refresh_cadence', '_missing_')} |"
        )
    add(f"")

    # Per-metric detail for CRITICAL_GAPS and NEEDS_WORK
    add(f"## Metrics Requiring Attention")
    add(f"")
    attention = [(m, s) for m, s in metric_scores if s < PRODUCTION_READY_THRESHOLD]
    attention.sort(key=lambda x: x[1])

    if not attention:
        add(f"_All metrics are PRODUCTION_READY. No attention required._")
    else:
        for m, s in attention:
            t = tier_label(s)
            add(f"### `{m.get('name', '?')}` — Score: {s} [{t}]")
            add(f"")
            add(f"- **Category:** {m.get('category', '_missing_')}")
            add(f"- **Owner:** {m.get('owner', '_missing_')}")
            add(f"- **Description:** {m.get('description', '_missing_')}")
            add(f"- **Formula:** {m.get('formula', '_missing_')}")
            add(f"- **Data source:** {m.get('data_source', '_missing_')}")
            add(f"- **Cadence:** {m.get('refresh_cadence', '_missing_')}")
            dims = m.get("dimensions", [])
            add(f"- **Dimensions:** {', '.join(dims) if dims else '_none listed_'}")
            add(f"")
            # What's missing
            missing = [f for f in SCORE_WEIGHTS if not _field_present(m, f)]
            if missing:
                add(f"**Missing fields** (would add {sum(SCORE_WEIGHTS[f] for f in missing)} points): "
                    f"{', '.join(missing)}")
                add(f"")

    add(f"## Validation Results")
    add(f"")
    if val_errors:
        add(f"### Errors ({len(val_errors)})")
        add(f"")
        for e in val_errors:
            add(f"- {e.strip()}")
        add(f"")
    else:
        add(f"No validation errors.")
        add(f"")

    if val_warnings:
        add(f"### Warnings ({len(val_warnings)})")
        add(f"")
        for w in val_warnings:
            add(f"- {w.strip()}")
        add(f"")

    add(f"## Lint Results")
    add(f"")
    if all_lint_issues:
        add(f"{len(all_lint_issues)} issue(s) found:")
        add(f"")
        for issue in all_lint_issues:
            add(f"- {issue.strip()}")
    else:
        add(f"No lint issues found.")
    add(f"")

    add(f"---")
    add(f"_Report generated by analytics_linter.py — data-analytics-engineering skill_")

    report_text = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Report written to: {args.output}")
    else:
        print(report_text)

    return 0


def _field_present(metric: dict, field: str) -> bool:
    """Return True if a scoreable field has a meaningful value."""
    if field == "dimensions":
        dims = metric.get("dimensions", [])
        return isinstance(dims, list) and len(dims) > 0
    if field == "example_value":
        ex = metric.get("example_value")
        return ex is not None and str(ex).strip() != ""
    val = metric.get(field, "")
    return bool(val and str(val).strip())


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analytics_linter.py",
        description="Metric Dictionary Validation and Linting CLI (stdlib only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analytics_linter.py validate --input data/sample-metric-dictionary.json
  python analytics_linter.py lint --input data/sample-metric-dictionary.json
  python analytics_linter.py report --input data/sample-metric-dictionary.json
  python analytics_linter.py report --input data/sample-metric-dictionary.json --output report.md
        """.strip(),
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # --- validate ---
    p_validate = sub.add_parser(
        "validate",
        help="Validate required fields, duplicate names, and undefined sources",
        description=(
            "Structural validation: check required fields (name, description, owner, "
            "formula, data_source, refresh_cadence), flag duplicate metric names, "
            "and detect undefined source references."
        ),
    )
    p_validate.add_argument(
        "--input", "-i",
        required=True,
        metavar="JSON_FILE",
        help="Path to metric dictionary JSON file",
    )

    # --- lint ---
    p_lint = sub.add_parser(
        "lint",
        help="Lint metric quality: owners, dimensions, naming, SLAs",
        description=(
            "Quality lint: flag missing owners, undocumented dimensions, "
            "inconsistent naming conventions, metrics without SLAs, "
            "short descriptions, and unrecognized categories."
        ),
    )
    p_lint.add_argument(
        "--input", "-i",
        required=True,
        metavar="JSON_FILE",
        help="Path to metric dictionary JSON file",
    )

    # --- report ---
    p_report = sub.add_parser(
        "report",
        help="Generate a full Markdown metric dictionary health report",
        description=(
            "Full health report: per-metric quality scores, category breakdown, "
            "validation results, lint results, and attention list."
        ),
    )
    p_report.add_argument(
        "--input", "-i",
        required=True,
        metavar="JSON_FILE",
        help="Path to metric dictionary JSON file",
    )
    p_report.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write Markdown report to this file (default: stdout)",
    )

    return parser


def main() -> int:
    global USE_COLOR

    if "--no-color" in sys.argv:
        USE_COLOR = False
        sys.argv.remove("--no-color")

    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "no_color", False):
        USE_COLOR = False

    dispatch = {
        "validate": cmd_validate,
        "lint":     cmd_lint,
        "report":   cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
