#!/usr/bin/env python3
"""Validate the research-findings TSV contract before aggregation.

Checks required columns, value-set membership, and basic well-formedness.
Exits non-zero on any error.

Usage:
    python3 validate_findings_tsv.py findings.tsv
"""

import argparse
import csv
import sys

REQUIRED = [
    "source_url", "source_type", "source_context", "paper_id",
    "title", "authors", "posted_at", "observed_at",
    "method_family", "idea_summary",
    "evidence_grade", "reproducibility", "lift",
    "trap_tags", "shape_tags", "quote", "window",
]
# Recommended (not required for backward compatibility). Missing or blank
# cluster_id degrades cross-source corroboration to unreliable paper_id keying.
RECOMMENDED = ["cluster_id"]
SOURCE_TYPES = {"arxiv", "hf_papers", "semantic_scholar", "papers_with_code",
                "conference", "industry_blog", "curator_newsletter"}
EVIDENCE_GRADES = {"A", "B", "C", "D", "F"}
REPRO_VALUES = {"code+benchmarks", "code_only", "paper_only", "proprietary"}
LIFT_VALUES = {"low", "medium", "high"}


def validate(path: str) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    rows_seen = 0
    paper_ids: set[str] = set()
    duplicate_count = 0

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            errors.append("Empty file or missing header.")
            print_report(errors, warnings, 0, 0)
            return 1
        missing = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing:
            errors.append(f"Missing required columns: {missing}")
        missing_rec = [c for c in RECOMMENDED if c not in reader.fieldnames]
        if missing_rec:
            warnings.append(
                f"Missing recommended column(s) {missing_rec}: cross-source "
                "corroboration will fall back to unreliable paper_id keying. "
                "Add a cluster_id column (see SKILL.md Step 2)."
            )
        has_cluster_id = "cluster_id" in (reader.fieldnames or [])

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
            url = row.get("source_url", "")
            if not (url.startswith("http://") or url.startswith("https://")):
                errors.append(f"row {i}: source_url must be http(s): {url!r}")
            if not row.get("idea_summary", "").strip():
                errors.append(f"row {i}: empty idea_summary")
            if has_cluster_id and not row.get("cluster_id", "").strip():
                warnings.append(
                    f"row {i}: blank cluster_id (corroboration for this row "
                    "falls back to unreliable paper_id keying)"
                )
            if not row.get("paper_id", "").strip():
                warnings.append(f"row {i}: missing paper_id (allowed but reduces dedupe quality)")
            else:
                pid = row["paper_id"].strip()
                if pid in paper_ids:
                    duplicate_count += 1
                    warnings.append(f"row {i}: duplicate paper_id {pid!r}")
                paper_ids.add(pid)

    print_report(errors, warnings, rows_seen, duplicate_count)
    return 1 if errors else 0


def print_report(errors, warnings, rows_seen, duplicate_count):
    print(f"Rows validated: {rows_seen}")
    print(f"Unique paper_ids: {rows_seen - duplicate_count}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  WARN: {w}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ERROR: {e}")
        print("\nValidation FAILED.")
    else:
        print("\nValidation PASSED.")


def main():
    p = argparse.ArgumentParser(description="Validate research-findings TSV")
    p.add_argument("path", help="Path to findings TSV")
    args = p.parse_args()
    sys.exit(validate(args.path))


if __name__ == "__main__":
    main()
