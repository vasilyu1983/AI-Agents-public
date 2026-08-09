#!/usr/bin/env python3
"""
ML Toolkit — stdlib-only CLI for model quality and leakage checks.

Subcommands:
  card     — Generate a structured model card in Markdown from a model spec JSON
  leakage  — Run a leakage checklist and emit PASS/WARN/FAIL per check
  report   — Full model quality report combining card + leakage analysis

Usage:
  python scripts/ml_toolkit.py card    --input data/sample-model-spec.json
  python scripts/ml_toolkit.py leakage --input data/sample-model-spec.json
  python scripts/ml_toolkit.py report  --input data/sample-model-spec.json
  python scripts/ml_toolkit.py report  --input data/sample-model-spec.json --output report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FUTURE_LEAK_KEYWORDS = [
    "future_", "next_", "post_", "after_label",
    "_future", "_next", "_post", "_afterlabel",
]

TARGET_DERIVED_KEYWORDS = [
    "churn_", "target_", "label_", "y_", "_churn", "_target",
]

LEAKAGE_STATUS_ORDER = {"FAIL": 0, "WARN": 1, "PASS": 2}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class LeakageCheck:
    name: str
    status: str        # PASS | WARN | FAIL
    detail: str


@dataclass
class LeakageResult:
    checks: list[LeakageCheck] = field(default_factory=list)

    @property
    def overall(self) -> str:
        """Aggregate status: worst of all checks."""
        if not self.checks:
            return "PASS"
        return min(self.checks, key=lambda c: LEAKAGE_STATUS_ORDER[c.status]).status


# ---------------------------------------------------------------------------
# Core logic: leakage checks
# ---------------------------------------------------------------------------

def check_prediction_timestamp(spec: dict) -> LeakageCheck:
    """Prediction timestamp must be defined and precede the label timestamp."""
    defined = spec.get("prediction_timestamp_defined", False)
    pred_field = spec.get("prediction_timestamp_field", "")
    label_field = spec.get("label_timestamp_field", "")

    if not defined or not pred_field:
        return LeakageCheck(
            name="Prediction timestamp defined",
            status="FAIL",
            detail=(
                "prediction_timestamp_defined is false or prediction_timestamp_field is missing. "
                "Define the exact point-in-time at which scoring occurs before any feature engineering."
            ),
        )

    if not label_field:
        return LeakageCheck(
            name="Prediction timestamp defined",
            status="WARN",
            detail=(
                f"prediction_timestamp_field is '{pred_field}' but label_timestamp_field is not set. "
                "Cannot verify temporal ordering between prediction and label timestamps."
            ),
        )

    # Field names are different (required); we cannot compare actual dates from
    # field names alone, but we can confirm they are distinct fields.
    if pred_field == label_field:
        return LeakageCheck(
            name="Prediction timestamp defined",
            status="FAIL",
            detail=(
                f"prediction_timestamp_field and label_timestamp_field are both '{pred_field}'. "
                "They must be different fields: one for scoring time, one for when the outcome is known."
            ),
        )

    return LeakageCheck(
        name="Prediction timestamp defined",
        status="PASS",
        detail=(
            f"prediction_timestamp_field='{pred_field}', label_timestamp_field='{label_field}'. "
            "Fields are distinct — verify in code that pred_ts < label_ts for every training row."
        ),
    )


def check_future_leaking_features(spec: dict) -> LeakageCheck:
    """Flag feature names that contain future-leaking keyword patterns."""
    features = spec.get("features", [])
    flagged = [
        f["name"]
        for f in features
        if any(kw in f["name"].lower() for kw in FUTURE_LEAK_KEYWORDS)
    ]

    if flagged:
        return LeakageCheck(
            name="No future-leaking features",
            status="WARN",
            detail=(
                f"Feature name(s) contain future-leaking patterns ({', '.join(FUTURE_LEAK_KEYWORDS)}): "
                f"{', '.join(flagged)}. "
                "Review each to confirm values are available at prediction time."
            ),
        )

    return LeakageCheck(
        name="No future-leaking features",
        status="PASS",
        detail=(
            f"None of the {len(features)} feature(s) matched future-leaking keyword patterns. "
            "Keyword scan is a heuristic — also validate feature availability by deployment walkthrough."
        ),
    )


def check_split_temporal_discipline(spec: dict) -> LeakageCheck:
    """Train/val/test must use temporal ordering, not random split, for time-ordered data."""
    split_method = spec.get("train_val_test_split_method", "").lower()
    temporal_col = (spec.get("training_data") or {}).get("temporal_column", "")
    split_config = spec.get("split_config", {})

    if split_method == "random" and temporal_col:
        return LeakageCheck(
            name="Temporal split discipline",
            status="FAIL",
            detail=(
                f"train_val_test_split_method is 'random' but training_data.temporal_column is '{temporal_col}'. "
                "Random splits on time-ordered data cause future-to-past leakage. Switch to temporal cutoffs."
            ),
        )

    if split_method not in ("temporal", "time-based", "chronological"):
        return LeakageCheck(
            name="Temporal split discipline",
            status="WARN",
            detail=(
                f"train_val_test_split_method is '{split_method}' — expected 'temporal'. "
                "If the data has a time dimension, verify that the split strategy prevents future leakage."
            ),
        )

    if split_config:
        train_end = split_config.get("train_end", "")
        val_end = split_config.get("val_end", "")
        test_end = split_config.get("test_end", "")

        if train_end and val_end and test_end:
            # String comparison works for ISO dates (YYYY-MM-DD).
            if not (train_end <= val_end <= test_end):
                return LeakageCheck(
                    name="Temporal split discipline",
                    status="FAIL",
                    detail=(
                        f"split_config dates are not in ascending order: "
                        f"train_end={train_end}, val_end={val_end}, test_end={test_end}. "
                        "Correct the split boundaries."
                    ),
                )
            return LeakageCheck(
                name="Temporal split discipline",
                status="PASS",
                detail=(
                    f"Temporal splits in order: train_end={train_end}, val_end={val_end}, test_end={test_end}."
                ),
            )

    return LeakageCheck(
        name="Temporal split discipline",
        status="PASS",
        detail=(
            "split_method is temporal. No split_config provided to validate date boundaries — "
            "verify cutoff dates manually."
        ),
    )


def check_target_leakage(spec: dict) -> LeakageCheck:
    """Check if any feature name looks derived from the target variable."""
    target = (spec.get("training_data") or {}).get("target_variable", "").lower()
    features = spec.get("features", [])
    flagged = []

    for f in features:
        fname = f["name"].lower()
        # Check generic target-derived keywords.
        if any(kw in fname for kw in TARGET_DERIVED_KEYWORDS):
            flagged.append(f["name"])
            continue
        # Check if the feature name contains the target variable name as a substring.
        if target and len(target) >= 4 and target in fname:
            flagged.append(f["name"])

    if flagged:
        return LeakageCheck(
            name="Target leakage",
            status="WARN",
            detail=(
                f"Feature name(s) may be derived from the target ('{target}'): "
                f"{', '.join(flagged)}. "
                "Confirm these features are not computed using the label or any post-event data."
            ),
        )

    return LeakageCheck(
        name="Target leakage",
        status="PASS",
        detail=(
            f"No features matched target-derived keyword patterns for target='{target}'. "
            "This is a heuristic check — review engineered features by hand, especially aggregates."
        ),
    )


def check_data_collection_date(spec: dict) -> LeakageCheck:
    """Training data metadata must include the data collection / extraction date."""
    td = spec.get("training_data") or {}
    collection_date = td.get("data_collection_date", "")

    if not collection_date:
        return LeakageCheck(
            name="Data collection date in metadata",
            status="FAIL",
            detail=(
                "training_data.data_collection_date is missing. "
                "Record when the training dataset was extracted to support reproducibility and staleness checks."
            ),
        )

    return LeakageCheck(
        name="Data collection date in metadata",
        status="PASS",
        detail=f"training_data.data_collection_date='{collection_date}'.",
    )


def run_leakage_checks(spec: dict) -> LeakageResult:
    result = LeakageResult()
    result.checks.append(check_prediction_timestamp(spec))
    result.checks.append(check_future_leaking_features(spec))
    result.checks.append(check_split_temporal_discipline(spec))
    result.checks.append(check_target_leakage(spec))
    result.checks.append(check_data_collection_date(spec))
    return result


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_status_badge(status: str) -> str:
    badges = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}
    return badges.get(status, f"[{status}]")


def _md_table_row(cols: list[str]) -> str:
    return "| " + " | ".join(cols) + " |"


def _md_table_sep(col_count: int) -> str:
    return "|" + "|".join(["---"] * col_count) + "|"


# ---------------------------------------------------------------------------
# Model card builder
# ---------------------------------------------------------------------------

def build_model_card(spec: dict) -> list[str]:
    lines: list[str] = []
    a = lines.append

    model_name = spec.get("model_name", "unnamed-model")
    version = spec.get("version", "n/a")
    model_type = spec.get("model_type", "n/a")
    task_description = spec.get("task_description", "")
    intended_use = spec.get("intended_use", "")
    td = spec.get("training_data") or {}
    features = spec.get("features", [])
    metrics = spec.get("performance_metrics", [])
    limitations = spec.get("limitations", [])
    ethical = spec.get("ethical_considerations", [])
    lineage = spec.get("lineage") or {}

    # --- Header ---
    a(f"# Model Card: {model_name}")
    a("")
    a(f"**Version:** {version}  ")
    a(f"**Model type:** {model_type}  ")
    a(f"**Generated:** 2026-03-21  ")
    a("")

    # --- Model Overview ---
    a("---")
    a("")
    a("## Model Overview")
    a("")
    if task_description:
        a(task_description)
    a("")

    # --- Intended Use ---
    a("---")
    a("")
    a("## Intended Use")
    a("")
    if intended_use:
        a(intended_use)
    else:
        a("_Not specified._")
    a("")

    # --- Training Data ---
    a("---")
    a("")
    a("## Training Data")
    a("")

    td_rows = [
        ("Source",              td.get("source", "n/a")),
        ("Date range",          f"{td.get('date_range', {}).get('start', '?')} — {td.get('date_range', {}).get('end', '?')}"),
        ("Row count",           f"{td.get('row_count', 'n/a'):,}" if isinstance(td.get("row_count"), int) else str(td.get("row_count", "n/a"))),
        ("Feature count",       str(td.get("feature_count", len(features)))),
        ("Target variable",     td.get("target_variable", "n/a")),
        ("Temporal column",     td.get("temporal_column", "n/a")),
        ("Data collection date",td.get("data_collection_date", "n/a")),
    ]
    a(_md_table_row(["Field", "Value"]))
    a(_md_table_sep(2))
    for k, v in td_rows:
        a(_md_table_row([k, v]))
    a("")

    if features:
        a(f"**Features ({len(features)} total):**")
        a("")
        a(_md_table_row(["Name", "Type", "Description"]))
        a(_md_table_sep(3))
        for f in features:
            a(_md_table_row([
                f.get("name", ""),
                f.get("type", ""),
                f.get("description", ""),
            ]))
        a("")

    # --- Performance Metrics ---
    a("---")
    a("")
    a("## Performance Metrics")
    a("")

    if metrics:
        a(_md_table_row(["Metric", "Value", "Benchmark", "Gap", "Split"]))
        a(_md_table_sep(5))
        for m in metrics:
            val = m.get("value")
            bench = m.get("benchmark")
            if val is not None and bench is not None:
                try:
                    gap = float(val) - float(bench)
                    gap_str = f"{gap:+.3f}"
                except (TypeError, ValueError):
                    gap_str = "n/a"
            else:
                gap_str = "n/a"
            a(_md_table_row([
                m.get("metric", ""),
                str(val) if val is not None else "n/a",
                str(bench) if bench is not None else "n/a",
                gap_str,
                m.get("split", ""),
            ]))
        a("")
    else:
        a("_No performance metrics provided._")
        a("")

    # --- Known Limitations ---
    a("---")
    a("")
    a("## Known Limitations")
    a("")
    if limitations:
        for lim in limitations:
            a(f"- {lim}")
    else:
        a("_No limitations documented._")
    a("")

    # --- Ethical Considerations ---
    a("---")
    a("")
    a("## Ethical Considerations")
    a("")
    if ethical:
        for item in ethical:
            a(f"- {item}")
    else:
        a("_No ethical considerations documented._")
    a("")

    # --- Versioning and Lineage ---
    a("---")
    a("")
    a("## Versioning and Lineage")
    a("")
    split_method = spec.get("train_val_test_split_method", "n/a")
    split_cfg = spec.get("split_config") or {}
    pred_ts = spec.get("prediction_timestamp_field", "n/a")
    label_ts = spec.get("label_timestamp_field", "n/a")

    lineage_rows = [
        ("Model version",            version),
        ("Experiment ID",            lineage.get("experiment_id", "n/a")),
        ("Git commit",               lineage.get("git_commit", "n/a")),
        ("MLflow run ID",            lineage.get("mlflow_run_id", "n/a")),
        ("Feature store version",    lineage.get("feature_store_version", "n/a")),
        ("Model artifact",           lineage.get("model_artifact", "n/a")),
        ("Split method",             split_method),
        ("Train end",                split_cfg.get("train_end", "n/a")),
        ("Val end",                  split_cfg.get("val_end", "n/a")),
        ("Test end",                 split_cfg.get("test_end", "n/a")),
        ("Prediction timestamp field", pred_ts),
        ("Label timestamp field",    label_ts),
    ]

    a(_md_table_row(["Field", "Value"]))
    a(_md_table_sep(2))
    for k, v in lineage_rows:
        a(_md_table_row([k, v]))
    a("")

    return lines


# ---------------------------------------------------------------------------
# Leakage report builder
# ---------------------------------------------------------------------------

def build_leakage_report(spec: dict, result: LeakageResult) -> list[str]:
    lines: list[str] = []
    a = lines.append

    model_name = spec.get("model_name", "unnamed-model")
    version = spec.get("version", "n/a")

    a(f"# Leakage Checklist: {model_name} v{version}")
    a("")
    a(f"**Overall:** {fmt_status_badge(result.overall)}  ")
    a(f"**Checks run:** {len(result.checks)}  ")
    a(f"**Generated:** 2026-03-21  ")
    a("")
    a("---")
    a("")
    a(_md_table_row(["Check", "Status", "Detail"]))
    a(_md_table_sep(3))
    for check in result.checks:
        a(_md_table_row([check.name, fmt_status_badge(check.status), check.detail]))
    a("")

    fails = [c for c in result.checks if c.status == "FAIL"]
    warns = [c for c in result.checks if c.status == "WARN"]

    if fails:
        a("---")
        a("")
        a(f"## FAIL Items ({len(fails)})")
        a("")
        for c in fails:
            a(f"### {c.name}")
            a("")
            a(c.detail)
            a("")

    if warns:
        a("---")
        a("")
        a(f"## WARN Items ({len(warns)})")
        a("")
        for c in warns:
            a(f"### {c.name}")
            a("")
            a(c.detail)
            a("")

    if not fails and not warns:
        a("> All leakage checks passed. Perform a manual feature-availability walkthrough before final sign-off.")
        a("")

    return lines


# ---------------------------------------------------------------------------
# Subcommand: card
# ---------------------------------------------------------------------------

def cmd_card(args: argparse.Namespace) -> None:
    spec = _load_json(args.input)
    lines = build_model_card(spec)
    output = "\n".join(lines)

    output_path = getattr(args, "output", None)
    if output_path:
        Path(output_path).write_text(output, encoding="utf-8")
        print(f"Model card written to: {output_path}")
    else:
        print(output)


# ---------------------------------------------------------------------------
# Subcommand: leakage
# ---------------------------------------------------------------------------

def cmd_leakage(args: argparse.Namespace) -> None:
    spec = _load_json(args.input)
    result = run_leakage_checks(spec)

    output_path = getattr(args, "output", None)

    if output_path:
        lines = build_leakage_report(spec, result)
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
        print(f"Leakage report written to: {output_path}")
        return

    # Console output (non-Markdown).
    model_name = spec.get("model_name", "unnamed-model")
    version = spec.get("version", "n/a")
    print()
    print(f"=== LEAKAGE CHECKLIST: {model_name} v{version} ===")
    print("-" * 60)

    col_w_name = 38
    col_w_status = 8

    for check in result.checks:
        badge = fmt_status_badge(check.status)
        print(f"  {check.name:<{col_w_name}} {badge:<{col_w_status}}")
        # Wrap detail at 70 chars indented.
        detail_words = check.detail.split()
        line_buf: list[str] = []
        line_len = 0
        for word in detail_words:
            if line_len + len(word) + 1 > 70:
                print(f"      {'  '.join(line_buf)}")
                line_buf = [word]
                line_len = len(word)
            else:
                line_buf.append(word)
                line_len += len(word) + 1
        if line_buf:
            print(f"      {' '.join(line_buf)}")
        print()

    print("-" * 60)
    overall = result.overall
    print(f"  Overall result: {fmt_status_badge(overall)}")
    fails = sum(1 for c in result.checks if c.status == "FAIL")
    warns = sum(1 for c in result.checks if c.status == "WARN")
    print(f"  FAIL: {fails}  WARN: {warns}  PASS: {len(result.checks) - fails - warns}")
    print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    spec = _load_json(args.input)
    leakage_result = run_leakage_checks(spec)

    card_lines = build_model_card(spec)
    leakage_lines = build_leakage_report(spec, leakage_result)

    divider = ["", "---", "", "# Leakage Analysis", ""]
    all_lines = card_lines + divider + leakage_lines
    report_text = "\n".join(all_lines)

    output_path = getattr(args, "output", None)
    if output_path:
        Path(output_path).write_text(report_text, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print(report_text)


# ---------------------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ml_toolkit",
        description="ML Toolkit — stdlib only. Model card generation and leakage checks. No pip install required.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")
    subparsers.required = True

    # --- card ---
    p_card = subparsers.add_parser(
        "card",
        help="Generate a structured model card in Markdown from a model spec JSON.",
        description=(
            "Reads a model spec JSON and produces a Markdown model card with sections: "
            "Model Overview, Intended Use, Training Data, Performance Metrics, "
            "Known Limitations, Ethical Considerations, Versioning/Lineage."
        ),
    )
    p_card.add_argument(
        "--input", metavar="JSON_FILE", required=True,
        help="Path to model spec JSON (e.g. data/sample-model-spec.json).",
    )
    p_card.add_argument(
        "--output", metavar="OUTPUT_FILE",
        help="Write model card to this file instead of stdout.",
    )
    p_card.set_defaults(func=cmd_card)

    # --- leakage ---
    p_leakage = subparsers.add_parser(
        "leakage",
        help="Run a leakage checklist and emit PASS/WARN/FAIL per check.",
        description=(
            "Checks: prediction timestamp discipline, future-leaking feature names, "
            "temporal split ordering, target leakage patterns, and data collection date. "
            "Prints results to console; use --output to write a Markdown report."
        ),
    )
    p_leakage.add_argument(
        "--input", metavar="JSON_FILE", required=True,
        help="Path to model spec JSON (e.g. data/sample-model-spec.json).",
    )
    p_leakage.add_argument(
        "--output", metavar="OUTPUT_FILE",
        help="Write Markdown leakage report to this file instead of console output.",
    )
    p_leakage.set_defaults(func=cmd_leakage)

    # --- report ---
    p_report = subparsers.add_parser(
        "report",
        help="Full model quality report combining model card and leakage analysis.",
        description=(
            "Reads a model spec JSON and produces a single Markdown report "
            "that includes the full model card followed by the leakage checklist."
        ),
    )
    p_report.add_argument(
        "--input", metavar="JSON_FILE", required=True,
        help="Path to model spec JSON (e.g. data/sample-model-spec.json).",
    )
    p_report.add_argument(
        "--output", metavar="OUTPUT_FILE",
        help="Write report to this file instead of stdout (e.g. report.md).",
    )
    p_report.set_defaults(func=cmd_report)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
