#!/usr/bin/env python3
"""Validate the research-findings TSV contract before aggregation.

Checks required columns, value-set membership, and basic well-formedness.
Exits non-zero on any error. aggregate_research_ideas.py runs the same
checks and refuses to score a file that fails them.

Usage:
    python3 validate_findings_tsv.py findings.tsv
"""

import argparse
import csv
import sys

REQUIRED = [
    "source_url", "source_type", "source_context", "paper_id", "origin_id",
    "title", "authors", "posted_at", "observed_at",
    "method_family", "idea_summary",
    "evidence_grade", "reproducibility", "lift",
    "trap_tags", "shape_tags", "quote", "window",
]
# Recommended (not required for backward compatibility). Missing or blank
# cluster_id means the row can never count as corroborated.
RECOMMENDED = ["cluster_id"]
# papers_with_code is retired (see references/papers-with-code-strategy.md);
# re-source the row from HF Papers or GitHub instead of keeping the old type.
SOURCE_TYPES = {"arxiv", "hf_papers", "semantic_scholar",
                "conference", "industry_blog", "curator_newsletter"}
EVIDENCE_GRADES = {"A", "B", "C", "D", "F"}
REPRO_VALUES = {"code+benchmarks", "code_only", "paper_only", "proprietary"}
LIFT_VALUES = {"low", "medium", "high"}
APPLICABILITY_RANGE = range(1, 6)
# Comma-separated tag columns. The aggregator's gate keys on these exact
# strings, so a numeric ("11") or misspelled ("proprietary_component") tag
# would silently pass the hard-kill rule. Unknown tags fail validation.
TRAP_TAGS = {
    "irreproducibility", "cherry-picked-baselines", "benchmark-overfit",
    "compute-asymmetry", "data-leakage-suspicion",
    "preprint-only-no-corroboration", "corporate-selection-bias",
    "hype-bubble", "narrow-applicability", "negative-trade-off-hidden",
    "proprietary-component", "benchmark-gaming",
}  # references/known-traps.md, traps 1-12 in order
SHAPE_TAGS = {
    "prompting-pattern", "architecture-tweak", "training-recipe",
    "evaluation-method", "data-construction-recipe", "inference-time-method",
    "system-design-pattern", "theoretical-bound", "negative-result",
    "survey-or-taxonomy", "monetizable-feature-pattern",
}  # references/idea-extraction-framework.md#method-shapes


def split_tags(s: str) -> list[str]:
    return [t.strip() for t in (s or "").split(",") if t.strip()]


def collect(path: str):
    """Return (errors, warnings, rows_seen, duplicate_count) for a findings TSV."""
    errors: list[str] = []
    warnings: list[str] = []
    rows_seen = 0
    paper_ids: set[str] = set()
    duplicate_count = 0

    try:
        f = open(path, newline="", encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"], warnings, 0, 0

    with f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            return ["Empty file or missing header."], warnings, 0, 0
        missing = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing:
            errors.append(f"Missing required columns: {missing}")
        missing_rec = [c for c in RECOMMENDED if c not in reader.fieldnames]
        if missing_rec:
            warnings.append(
                f"Missing recommended column(s) {missing_rec}: no row can be "
                "corroborated, so every row caps at validate. Add a cluster_id "
                "column (see references/source-mix-and-compliance.md)."
            )
        has_cluster_id = "cluster_id" in reader.fieldnames
        has_applicability = "applicability" in reader.fieldnames

        for i, row in enumerate(reader, start=2):
            rows_seen += 1
            if row.get("source_type") not in SOURCE_TYPES:
                errors.append(f"row {i}: invalid source_type {row.get('source_type')!r}")
            if row.get("evidence_grade") not in EVIDENCE_GRADES:
                errors.append(f"row {i}: invalid evidence_grade {row.get('evidence_grade')!r}")
            if row.get("reproducibility") not in REPRO_VALUES:
                errors.append(f"row {i}: invalid reproducibility {row.get('reproducibility')!r}")
            if row.get("lift") not in LIFT_VALUES:
                errors.append(f"row {i}: invalid lift {row.get('lift')!r}")
            for col, vocab, ref in (("trap_tags", TRAP_TAGS, "known-traps.md"),
                                    ("shape_tags", SHAPE_TAGS, "idea-extraction-framework.md")):
                bad = [t for t in split_tags(row.get(col)) if t not in vocab]
                if bad:
                    errors.append(f"row {i}: unknown {col} {bad} (use the slugs in references/{ref})")
            url = row.get("source_url") or ""
            if not (url.startswith("http://") or url.startswith("https://")):
                errors.append(f"row {i}: source_url must be http(s): {url!r}")
            if not (row.get("idea_summary") or "").strip():
                errors.append(f"row {i}: empty idea_summary")
            if "origin_id" in reader.fieldnames and not (row.get("origin_id") or "").strip():
                errors.append(f"row {i}: blank origin_id (name the study or team the evidence comes from)")
            if has_applicability:
                raw = (row.get("applicability") or "").strip()
                if raw and (not raw.isdigit() or int(raw) not in APPLICABILITY_RANGE):
                    errors.append(f"row {i}: applicability must be an integer 1-5, got {raw!r}")
            if has_cluster_id and not (row.get("cluster_id") or "").strip():
                warnings.append(
                    f"row {i}: blank cluster_id (this row cannot be corroborated "
                    "and caps at validate)"
                )
            pid = (row.get("paper_id") or "").strip()
            if not pid:
                warnings.append(f"row {i}: missing paper_id (allowed but reduces dedupe quality)")
            else:
                if pid in paper_ids:
                    duplicate_count += 1
                    warnings.append(f"row {i}: duplicate paper_id {pid!r}")
                paper_ids.add(pid)

    if rows_seen == 0 and not errors:
        errors.append("No data rows.")
    return errors, warnings, rows_seen, duplicate_count


def validate(path: str) -> int:
    errors, warnings, rows_seen, duplicate_count = collect(path)
    print_report(errors, warnings, rows_seen, duplicate_count)
    return 1 if errors else 0


def print_report(errors, warnings, rows_seen, duplicate_count, stream=None):
    stream = stream or sys.stdout
    print(f"Rows validated: {rows_seen}", file=stream)
    print(f"Unique paper_ids: {rows_seen - duplicate_count}", file=stream)
    if warnings:
        print(f"\n{len(warnings)} warning(s):", file=stream)
        for w in warnings:
            print(f"  WARN: {w}", file=stream)
    if errors:
        print(f"\n{len(errors)} error(s):", file=stream)
        for e in errors:
            print(f"  ERROR: {e}", file=stream)
        print("\nValidation FAILED.", file=stream)
    else:
        print("\nValidation PASSED.", file=stream)


def main():
    p = argparse.ArgumentParser(description="Validate research-findings TSV")
    p.add_argument("path", help="Path to findings TSV")
    args = p.parse_args()
    sys.exit(validate(args.path))


if __name__ == "__main__":
    main()
