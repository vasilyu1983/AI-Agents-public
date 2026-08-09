#!/usr/bin/env python3
"""
product_scorer.py — Product prioritization and PMF scoring CLI (stdlib only).

Subcommands:
  rice    — RICE score features from a JSON backlog and rank by score descending
  pmf     — Score product-market fit across 5 dimensions and return a PMF verdict
  report  — Full product health report combining RICE backlog + PMF scoring

Run with --help or <subcommand> --help for usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

VALID_IMPACT_VALUES = {0.25, 0.5, 1.0, 2.0, 3.0}
VALID_CONFIDENCE_VALUES = {0.5, 0.8, 1.0}
EFFORT_MIN = 0.5
EFFORT_MAX = 26.0

PMF_DIMENSIONS = [
    "problem_severity",
    "solution_quality",
    "market_timing",
    "team_market_fit",
    "economic_viability",
]

# Weights for PMF dimensions (must sum to 1.0)
PMF_WEIGHTS = {
    "problem_severity":   0.25,
    "solution_quality":   0.30,
    "market_timing":      0.20,
    "team_market_fit":    0.10,
    "economic_viability": 0.15,
}

PMF_MAX_RAW = sum(PMF_WEIGHTS[d] * 5 for d in PMF_DIMENSIONS) * 4  # scale to 25

# PMF verdict thresholds (based on raw weighted score out of 5.0, mapped to /25)
# STRONG >=20, SIGNALS 14-19, WEAK 8-13, NO_SIGNAL <8
PMF_VERDICTS = [
    (20, "STRONG"),
    (14, "SIGNALS"),
    (8,  "WEAK"),
    (0,  "NO_SIGNAL"),
]

VALID_THEMES = {"growth", "retention", "monetization", "infra"}

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def print_divider(char: str = "-", width: int = 72) -> None:
    print(char * width)


def print_header(title: str, width: int = 72) -> None:
    print_divider("=", width)
    print(f"  {title}")
    print_divider("=", width)


def wrap_text(text: str, width: int = 68, indent: str = "    ") -> str:
    """Simple word-wrap returning indented lines."""
    words = text.split()
    lines, line = [], []
    for word in words:
        if sum(len(x) + 1 for x in line) + len(word) > width:
            lines.append(indent + " ".join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(indent + " ".join(line))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# RICE scoring
# ---------------------------------------------------------------------------

def compute_rice(reach: float, impact: float, confidence: float, effort_weeks: float) -> float:
    """RICE = (Reach × Impact × Confidence) / Effort."""
    if effort_weeks <= 0:
        return 0.0
    return (reach * impact * confidence) / effort_weeks


def validate_feature(feat: dict, idx: int) -> list[str]:
    """Return a list of validation error strings for a feature dict."""
    errors = []
    for field in ("id", "name", "reach", "impact", "confidence", "effort_weeks"):
        if field not in feat:
            errors.append(f"Feature[{idx}]: missing required field '{field}'")

    impact = feat.get("impact")
    if impact is not None and impact not in VALID_IMPACT_VALUES:
        errors.append(
            f"Feature[{idx}] '{feat.get('name', '?')}': "
            f"impact={impact} not in {sorted(VALID_IMPACT_VALUES)}"
        )

    confidence = feat.get("confidence")
    if confidence is not None and confidence not in VALID_CONFIDENCE_VALUES:
        errors.append(
            f"Feature[{idx}] '{feat.get('name', '?')}': "
            f"confidence={confidence} not in {sorted(VALID_CONFIDENCE_VALUES)}"
        )

    effort = feat.get("effort_weeks")
    if effort is not None and not (EFFORT_MIN <= effort <= EFFORT_MAX):
        errors.append(
            f"Feature[{idx}] '{feat.get('name', '?')}': "
            f"effort_weeks={effort} must be {EFFORT_MIN}–{EFFORT_MAX}"
        )

    theme = feat.get("theme")
    if theme is not None and theme not in VALID_THEMES:
        errors.append(
            f"Feature[{idx}] '{feat.get('name', '?')}': "
            f"theme='{theme}' not in {sorted(VALID_THEMES)}"
        )

    return errors


def cmd_rice(args) -> None:
    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    with path.open() as f:
        features = json.load(f)

    if not isinstance(features, list):
        print("ERROR: Input JSON must be a list of feature objects.")
        sys.exit(1)

    # Validate
    all_errors = []
    for i, feat in enumerate(features):
        all_errors.extend(validate_feature(feat, i))

    if all_errors:
        print("VALIDATION ERRORS:")
        for e in all_errors:
            print(f"  {e}")
        sys.exit(1)

    # Score
    scored = []
    for feat in features:
        rice = compute_rice(
            feat["reach"], feat["impact"], feat["confidence"], feat["effort_weeks"]
        )
        scored.append({**feat, "rice_score": round(rice, 1)})

    # Sort descending
    scored.sort(key=lambda x: x["rice_score"], reverse=True)

    # Filter by theme
    if args.theme:
        scored = [f for f in scored if f.get("theme") == args.theme]
        if not scored:
            print(f"No features found for theme '{args.theme}'.")
            return

    # Display
    print()
    print_header(f"RICE PRIORITIZATION — {path.name}  [{len(scored)} features]")

    col_rank  =  4
    col_id    =  5
    col_name  = 30
    col_reach =  8
    col_imp   =  7
    col_conf  =  7
    col_eff   =  7
    col_rice  =  9
    col_theme = 12

    header = (
        f"  {'#':<{col_rank}} {'ID':<{col_id}} {'Feature':<{col_name}} "
        f"{'Reach':>{col_reach}} {'Impact':>{col_imp}} {'Conf':>{col_conf}} "
        f"{'Effort':>{col_eff}} {'RICE':>{col_rice}} {'Theme':<{col_theme}}"
    )
    print(header)
    print_divider("-")

    for rank, feat in enumerate(scored, 1):
        name_display = feat["name"]
        if len(name_display) > col_name - 1:
            name_display = name_display[: col_name - 4] + "..."
        print(
            f"  {rank:<{col_rank}} {feat['id']:<{col_id}} {name_display:<{col_name}} "
            f"{feat['reach']:>{col_reach},} {feat['impact']:>{col_imp}.2f} "
            f"{feat['confidence']:>{col_conf}.2f} {feat['effort_weeks']:>{col_eff}.1f}w "
            f"{feat['rice_score']:>{col_rice}.1f} {feat.get('theme', ''):<{col_theme}}"
        )

    print_divider("=")
    top = scored[0]
    print(
        f"  Top item: [{top['id']}] {top['name']}  RICE={top['rice_score']:,.1f}"
    )
    if args.top:
        top_n = scored[: args.top]
        total = sum(f["rice_score"] for f in top_n)
        print(f"  Top-{args.top} cumulative RICE score: {total:,.1f}")
    print_divider("=")
    print()

    # Optionally write JSON output
    if args.output:
        out = Path(args.output)
        with out.open("w") as f:
            json.dump(scored, f, indent=2)
        print(f"  Ranked list written to: {out.resolve()}")
        print()


# ---------------------------------------------------------------------------
# PMF scoring
# ---------------------------------------------------------------------------

def pmf_weighted_score(dimensions: dict) -> float:
    """Return weighted score (0.0–5.0) from dimension scores."""
    total = 0.0
    for dim, weight in PMF_WEIGHTS.items():
        score = dimensions.get(dim, {}).get("score", 0)
        total += score * weight
    return round(total, 4)


def pmf_raw_to_25(weighted_score: float) -> float:
    """Map weighted 0–5 score to 0–25 scale for verdict lookup."""
    return round(weighted_score * 5, 2)


def pmf_verdict(score_25: float) -> str:
    for threshold, label in PMF_VERDICTS:
        if score_25 >= threshold:
            return label
    return "NO_SIGNAL"


def cmd_pmf(args) -> None:
    path = Path(args.input)
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    with path.open() as f:
        data = json.load(f)

    dims = data.get("dimensions", {})

    # Validate scores
    errors = []
    for dim in PMF_DIMENSIONS:
        if dim not in dims:
            errors.append(f"Missing dimension: '{dim}'")
        else:
            score = dims[dim].get("score")
            if score is None:
                errors.append(f"Dimension '{dim}' missing 'score'")
            elif not isinstance(score, (int, float)) or not (1 <= score <= 5):
                errors.append(f"Dimension '{dim}' score={score} must be 1–5")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    weighted = pmf_weighted_score(dims)
    score_25 = pmf_raw_to_25(weighted)
    verdict  = pmf_verdict(score_25)

    product  = data.get("product_name", "Unknown Product")
    segment  = data.get("segment", "")
    date_str = data.get("assessment_date", "")

    print()
    print_header(f"PMF ASSESSMENT — {product}")
    if segment:
        print(f"  Segment  : {segment}")
    if date_str:
        print(f"  Date     : {date_str}")
    print_divider("-")

    # Per-dimension breakdown
    col_dim  = 22
    col_sc   =  7
    col_wt   =  8
    col_wtsc = 10

    header = (
        f"  {'Dimension':<{col_dim}} {'Score':>{col_sc}} {'Weight':>{col_wt}} "
        f"{'Wtd Score':>{col_wtsc}}  Evidence"
    )
    print(header)
    print_divider("-")

    DIM_LABELS = {
        "problem_severity":   "Problem Severity",
        "solution_quality":   "Solution Quality",
        "market_timing":      "Market Timing",
        "team_market_fit":    "Team–Market Fit",
        "economic_viability": "Economic Viability",
    }

    for dim in PMF_DIMENSIONS:
        entry  = dims[dim]
        score  = entry["score"]
        weight = PMF_WEIGHTS[dim]
        wt_sc  = round(score * weight, 3)
        label  = DIM_LABELS.get(dim, dim)
        evidence = entry.get("evidence", "")
        # Truncate evidence for table display
        ev_short = (evidence[:55] + "…") if len(evidence) > 56 else evidence
        print(
            f"  {label:<{col_dim}} {score:>{col_sc}}/5  {weight*100:>{col_wt}.0f}%  "
            f"{wt_sc:>{col_wtsc}.3f}  {ev_short}"
        )

    print_divider("-")
    print(f"  {'WEIGHTED SCORE (0–5)':<{col_dim}} {weighted:>{col_sc}.3f}")
    print(f"  {'SCALED SCORE (0–25)':<{col_dim}} {score_25:>{col_sc}.2f}")
    print_divider("=")

    verdict_line = f"  PMF VERDICT: {verdict}"
    if verdict == "STRONG":
        verdict_line += "  (score ≥20 — strong signal across dimensions)"
    elif verdict == "SIGNALS":
        verdict_line += "  (score 14–19 — signals present; strengthen weak dimensions)"
    elif verdict == "WEAK":
        verdict_line += "  (score 8–13 — early signal only; re-run after iteration)"
    else:
        verdict_line += "  (score <8 — no durable PMF signal; revisit fundamentals)"

    print(verdict_line)
    print_divider("=")

    # Weakest dimensions as focus areas
    dim_scores = [(dim, dims[dim]["score"]) for dim in PMF_DIMENSIONS]
    dim_scores.sort(key=lambda x: x[1])
    weak = [d for d in dim_scores if d[1] <= 2]

    if weak:
        print()
        print("  FOCUS AREAS (score ≤ 2):")
        print_divider("-")
        for dim, score in weak:
            label    = DIM_LABELS.get(dim, dim)
            evidence = dims[dim].get("evidence", "")
            print(f"  [{score}/5] {label}")
            if evidence:
                print(wrap_text(evidence, width=66, indent="      "))
        print_divider("=")

    print()


# ---------------------------------------------------------------------------
# Report subcommand
# ---------------------------------------------------------------------------

def cmd_report(args) -> None:
    # Load features
    feat_path = Path(args.input)
    if not feat_path.exists():
        print(f"ERROR: Features file not found: {feat_path}")
        sys.exit(1)

    with feat_path.open() as f:
        features = json.load(f)

    if not isinstance(features, list):
        print("ERROR: Features JSON must be a list.")
        sys.exit(1)

    # Load PMF data
    pmf_path = Path(args.pmf)
    if not pmf_path.exists():
        print(f"ERROR: PMF data file not found: {pmf_path}")
        sys.exit(1)

    with pmf_path.open() as f:
        pmf_data = json.load(f)

    # Validate features
    all_errors = []
    for i, feat in enumerate(features):
        all_errors.extend(validate_feature(feat, i))
    if all_errors:
        print("VALIDATION ERRORS (features):")
        for e in all_errors:
            print(f"  {e}")
        sys.exit(1)

    # Score features
    scored = []
    for feat in features:
        rice = compute_rice(
            feat["reach"], feat["impact"], feat["confidence"], feat["effort_weeks"]
        )
        scored.append({**feat, "rice_score": round(rice, 1)})
    scored.sort(key=lambda x: x["rice_score"], reverse=True)

    # Score PMF
    dims = pmf_data.get("dimensions", {})
    pmf_errors = []
    for dim in PMF_DIMENSIONS:
        if dim not in dims:
            pmf_errors.append(f"Missing dimension: '{dim}'")
        else:
            score = dims[dim].get("score")
            if score is None or not (1 <= score <= 5):
                pmf_errors.append(f"Dimension '{dim}' score must be 1–5")
    if pmf_errors:
        print("VALIDATION ERRORS (PMF):")
        for e in pmf_errors:
            print(f"  {e}")
        sys.exit(1)

    weighted = pmf_weighted_score(dims)
    score_25 = pmf_raw_to_25(weighted)
    verdict  = pmf_verdict(score_25)

    product  = pmf_data.get("product_name", "Product")
    segment  = pmf_data.get("segment", "")
    today    = datetime.now().strftime("%Y-%m-%d")

    # Theme breakdown
    theme_counts: dict = {}
    theme_rice: dict = {}
    for feat in scored:
        t = feat.get("theme", "other")
        theme_counts[t] = theme_counts.get(t, 0) + 1
        theme_rice[t] = theme_rice.get(t, 0.0) + feat["rice_score"]

    # Build Markdown report
    DIM_LABELS = {
        "problem_severity":   "Problem Severity",
        "solution_quality":   "Solution Quality",
        "market_timing":      "Market Timing",
        "team_market_fit":    "Team–Market Fit",
        "economic_viability": "Economic Viability",
    }

    lines = [
        f"# Product Health Report — {product}",
        f"",
        f"**Generated**: {today}  ",
        f"**Segment**: {segment}  ",
        f"**Features scored**: {len(scored)}  ",
        f"**PMF Verdict**: {verdict} ({score_25:.1f}/25)",
        f"",
        f"---",
        f"",
        f"## PMF Assessment",
        f"",
        f"| Dimension | Score | Weight | Wtd Score |",
        f"|-----------|------:|-------:|----------:|",
    ]

    for dim in PMF_DIMENSIONS:
        entry  = dims[dim]
        score  = entry["score"]
        weight = PMF_WEIGHTS[dim]
        wt_sc  = round(score * weight, 3)
        label  = DIM_LABELS.get(dim, dim)
        lines.append(f"| {label} | {score}/5 | {weight*100:.0f}% | {wt_sc:.3f} |")

    lines += [
        f"",
        f"**Weighted Score**: {weighted:.3f}/5.00  ",
        f"**Scaled Score**: {score_25:.2f}/25  ",
        f"**Verdict**: **{verdict}**",
        f"",
    ]

    # Verdict description
    if verdict == "STRONG":
        lines.append("> Strong PMF signal across dimensions. Focus on scaling and hardening retention.")
    elif verdict == "SIGNALS":
        lines.append("> PMF signals present. Strengthen the weakest dimension before scaling acquisition.")
    elif verdict == "WEAK":
        lines.append("> Early signal only. Run focused discovery and iteration before scaling.")
    else:
        lines.append("> No durable PMF signal. Revisit problem/solution fundamentals.")

    # Evidence per dimension
    lines += [
        f"",
        f"### Dimension Evidence",
        f"",
    ]
    for dim in PMF_DIMENSIONS:
        entry    = dims[dim]
        label    = DIM_LABELS.get(dim, dim)
        evidence = entry.get("evidence", "")
        lines.append(f"**{label}** ({entry['score']}/5): {evidence}")
        lines.append("")

    # RICE backlog
    lines += [
        f"---",
        f"",
        f"## RICE Backlog (ranked)",
        f"",
        f"| # | ID | Feature | Reach | Impact | Conf | Effort | RICE | Theme |",
        f"|---|-----|---------|------:|-------:|-----:|-------:|-----:|-------|",
    ]

    for rank, feat in enumerate(scored, 1):
        lines.append(
            f"| {rank} | {feat['id']} | {feat['name']} | "
            f"{feat['reach']:,} | {feat['impact']} | {feat['confidence']} | "
            f"{feat['effort_weeks']}w | **{feat['rice_score']:,.1f}** | {feat.get('theme', '')} |"
        )

    # Theme summary
    lines += [
        f"",
        f"### Theme Summary",
        f"",
        f"| Theme | Count | Cumulative RICE |",
        f"|-------|------:|----------------:|",
    ]
    for theme, count in sorted(theme_counts.items()):
        lines.append(
            f"| {theme} | {count} | {theme_rice[theme]:,.1f} |"
        )

    # Top 3 recommendations
    lines += [
        f"",
        f"---",
        f"",
        f"## Recommendations",
        f"",
    ]

    top3 = scored[:3]
    for i, feat in enumerate(top3, 1):
        lines.append(
            f"{i}. **[{feat['id']}] {feat['name']}** (RICE {feat['rice_score']:,.1f}) — "
            f"{feat.get('description', '')}"
        )

    # PMF-informed priority note
    if verdict in ("WEAK", "NO_SIGNAL"):
        lines += [
            f"",
            f"> **PMF note**: With a {verdict} verdict, prioritise retention and core-loop "
            f"improvements over growth or monetisation initiatives until PMF strengthens.",
        ]
    elif verdict == "SIGNALS":
        lines += [
            f"",
            f"> **PMF note**: Signals are present. Validate the top RICE items against "
            f"the weakest PMF dimension before committing to full build.",
        ]

    report_md = "\n".join(lines) + "\n"

    # Output
    if args.output:
        out = Path(args.output)
        out.write_text(report_md)
        print(f"Report written to: {out.resolve()}")
    else:
        print(report_md)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="product_scorer.py",
        description=(
            "Product prioritization and PMF scoring CLI (stdlib only, no pip required).\n"
            "Subcommands: rice, pmf, report"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # RICE prioritization
  python scripts/product_scorer.py rice --input data/sample-features.json
  python scripts/product_scorer.py rice --input data/sample-features.json --theme retention --top 3

  # PMF scoring
  python scripts/product_scorer.py pmf --input data/sample-pmf-data.json

  # Full health report
  python scripts/product_scorer.py report \\
      --input data/sample-features.json \\
      --pmf data/sample-pmf-data.json \\
      --output report.md
        """,
    )
    sub = parser.add_subparsers(dest="command", metavar="subcommand")
    sub.required = True

    # --- rice ---
    p_rice = sub.add_parser(
        "rice",
        help="RICE score a feature backlog and rank descending",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Score each feature: RICE = (Reach × Impact × Confidence) / Effort.\n"
            "Reach: users/quarter (0–10000)\n"
            "Impact: 0.25 / 0.5 / 1 / 2 / 3\n"
            "Confidence: 0.5 / 0.8 / 1.0\n"
            "Effort: person-weeks (0.5–26)"
        ),
    )
    p_rice.add_argument(
        "--input", required=True,
        help="Path to features JSON (array of feature objects)"
    )
    p_rice.add_argument(
        "--theme", choices=sorted(VALID_THEMES), default=None,
        help="Filter output to a single theme"
    )
    p_rice.add_argument(
        "--top", type=int, default=None, metavar="N",
        help="Show top N features and their cumulative RICE score"
    )
    p_rice.add_argument(
        "--output", default=None,
        help="Optional: write ranked JSON to this file path"
    )
    p_rice.set_defaults(func=cmd_rice)

    # --- pmf ---
    p_pmf = sub.add_parser(
        "pmf",
        help="Score PMF signal across 5 dimensions and return a verdict",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Dimensions (each scored 1–5):\n"
            "  problem_severity   (weight 25%)\n"
            "  solution_quality   (weight 30%)\n"
            "  market_timing      (weight 20%)\n"
            "  team_market_fit    (weight 10%)\n"
            "  economic_viability (weight 15%)\n\n"
            "Verdicts (0–25 scaled score):\n"
            "  STRONG ≥20 | SIGNALS 14–19 | WEAK 8–13 | NO_SIGNAL <8"
        ),
    )
    p_pmf.add_argument(
        "--input", required=True,
        help="Path to PMF assessment JSON (see sample-pmf-data.json)"
    )
    p_pmf.set_defaults(func=cmd_pmf)

    # --- report ---
    p_report = sub.add_parser(
        "report",
        help="Full product health report: RICE backlog + PMF scoring",
    )
    p_report.add_argument(
        "--input", required=True,
        help="Path to features JSON"
    )
    p_report.add_argument(
        "--pmf", required=True,
        help="Path to PMF assessment JSON"
    )
    p_report.add_argument(
        "--output", default=None,
        help="Write Markdown report to this file (default: print to stdout)"
    )
    p_report.set_defaults(func=cmd_report)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
