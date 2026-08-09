#!/usr/bin/env python3
"""Aggregate, gate, and rank research-finding ideas.

Design (locked decision): the GATE is decided by a deterministic rule ladder.
The numeric SCORE never gates — it only orders rows *within* a gate bucket.
This removes the prior failure mode where a subjective applicability guess
(default 3) flipped promote/kill across a reverse-fit threshold.

Cross-source corroboration is keyed on `cluster_id` (a stable method-identity
slug shared across source types), NOT paper_id. If cluster_id is absent it
falls back to paper_id and the row is flagged corroboration=unreliable.

Rule ladder (first match wins for the gate):
    1. hard-kill trap (proprietary-component / benchmark-gaming) .. kill
    2. >=3 trap tags ............................................ kill
    3. evidence_grade == F ..................................... kill
    4. shape in {negative-result, survey-or-taxonomy} .......... background
    5. corroboration < 2 distinct source_type / one cluster_id . validate
    6. reproducibility == proprietary .......................... validate
    7. evidence_grade == D ..................................... validate
    8. any of traps {1,5,6,8} present .......................... validate
    9. else .................................................... promote

Ranking score (ordering only): (A * E * R) / (lift * trap_penalty), with
per-trap numeric adjustments from known-traps.md (evidence -1 for trap 2,
applicability -1 for trap 3, -2 for trap 9, lift +1 tier for trap 4).

Usage:
    python3 aggregate_research_ideas.py findings.tsv --output scored.tsv \\
        --target "ai-rag skill"
"""

import argparse
import csv
import sys
from collections import defaultdict

EVIDENCE_SCORE = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
EVIDENCE_ORDER = ["F", "D", "C", "B", "A"]
REPRO_SCORE = {"code+benchmarks": 5, "code_only": 4, "paper_only": 2, "proprietary": 1}
LIFT_ORDER = ["low", "medium", "high"]
LIFT_WEIGHT = {"low": 1, "medium": 3, "high": 5}

HARD_KILL_TRAPS = {"proprietary-component", "benchmark-gaming"}
VALIDATE_CAP_TRAPS = {
    "irreproducibility",            # trap 1
    "data-leakage-suspicion",       # trap 5
    "preprint-only-no-corroboration",  # trap 6
    "hype-bubble",                  # trap 8
}
BACKGROUND_SHAPES = {"negative-result", "survey-or-taxonomy"}

# Gate bucket order for report-friendly sorting (best first).
GATE_RANK = {"promote": 0, "validate": 1, "background": 2, "kill": 3}


def parse_tags(s: str) -> list[str]:
    return [t.strip() for t in (s or "").split(",") if t.strip()]


def downgrade_evidence(grade: str, steps: int) -> str:
    if grade not in EVIDENCE_ORDER:
        grade = "C"
    idx = max(0, EVIDENCE_ORDER.index(grade) - steps)
    return EVIDENCE_ORDER[idx]


def raise_lift(lift: str, steps: int) -> str:
    if lift not in LIFT_ORDER:
        lift = "medium"
    idx = min(len(LIFT_ORDER) - 1, LIFT_ORDER.index(lift) + steps)
    return LIFT_ORDER[idx]


def trap_penalty(tags: list[str]) -> float:
    non_hard = [t for t in tags if t not in HARD_KILL_TRAPS]
    return 1.0 + 0.5 * len(non_hard)


def ranking_score(row: dict, applicability: int, traps: list[str]) -> float:
    """Ordering-only score. Never gates. Applies per-trap numeric adjustments."""
    grade = row.get("evidence_grade", "C")
    repro = row.get("reproducibility", "paper_only")
    lift = row.get("lift", "medium")
    a = applicability

    if "cherry-picked-baselines" in traps:      # trap 2
        grade = downgrade_evidence(grade, 1)
    if "benchmark-overfit" in traps:            # trap 3
        a -= 1
    if "narrow-applicability" in traps:         # trap 9
        a -= 2
    if "compute-asymmetry" in traps:            # trap 4
        lift = raise_lift(lift, 1)

    a = max(1, a)
    e = EVIDENCE_SCORE.get(grade, 3)
    r = REPRO_SCORE.get(repro, 2)
    lw = LIFT_WEIGHT.get(lift, 3)
    return (a * e * r) / (lw * trap_penalty(traps))


def gate_row(row: dict, corroborated: bool) -> tuple[str, str]:
    """Deterministic rule ladder. Returns (gate_status, gate_reason)."""
    grade = row.get("evidence_grade", "C")
    repro = row.get("reproducibility", "paper_only")
    traps = parse_tags(row.get("trap_tags", ""))
    shapes = parse_tags(row.get("shape_tags", ""))

    hard = sorted(t for t in traps if t in HARD_KILL_TRAPS)
    if hard:
        return "kill", f"hard-kill trap: {','.join(hard)}"
    if len(traps) >= 3:
        return "kill", f"3+ traps: {','.join(traps)}"
    if grade == "F":
        return "kill", "evidence_grade F"
    bg = sorted(s for s in shapes if s in BACKGROUND_SHAPES)
    if bg:
        return "background", f"non-stealable/falsifying shape: {','.join(bg)} (kept as context, not killed)"
    if not corroborated:
        return "validate", "uncorroborated: <2 distinct source_type sharing cluster_id"
    if repro == "proprietary":
        return "validate", "proprietary reproducibility caps at validate"
    if grade == "D":
        return "validate", "evidence_grade D caps at validate"
    soft = sorted(t for t in traps if t in VALIDATE_CAP_TRAPS)
    if soft:
        return "validate", f"validate-cap trap(s): {','.join(soft)}"
    return "promote", "passed all gate rules"


def main():
    p = argparse.ArgumentParser(description="Gate and rank research-finding ideas")
    p.add_argument("findings", help="Path to validated findings TSV")
    p.add_argument("--output", required=True, help="Output scored TSV path")
    p.add_argument("--target", help="Target application label (recorded in output)")
    p.add_argument("--default-applicability", type=int, default=3,
                   help="Default applicability when not in findings TSV (1-5; default 3)")
    args = p.parse_args()

    with open(args.findings, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    if not rows:
        print("No rows to score.", file=sys.stderr)
        sys.exit(1)

    has_cluster_col = "cluster_id" in rows[0]

    # Corroboration is keyed on cluster_id (method identity across artifacts).
    # Fall back to paper_id only when cluster_id is absent/blank, and flag it.
    def cluster_key(row: dict) -> tuple[str, bool]:
        cid = (row.get("cluster_id") or "").strip()
        if cid:
            return cid, True
        return (row.get("paper_id") or "").strip(), False

    sources_by_cluster: dict[str, set] = defaultdict(set)
    for row in rows:
        key, _reliable = cluster_key(row)
        if key:
            sources_by_cluster[key].add((row.get("source_type") or "").strip())

    any_unreliable = False
    out_rows = []
    for row in rows:
        key, reliable = cluster_key(row)
        distinct_sources = sorted(s for s in sources_by_cluster.get(key, set()) if s)
        corroborated = len(distinct_sources) >= 2
        if not reliable or not has_cluster_col:
            corro_flag = "unreliable-no-cluster_id"
            any_unreliable = True
        else:
            corro_flag = "yes" if corroborated else "no"

        applicability = int(row.get("applicability", args.default_applicability)
                            or args.default_applicability)
        gate, reason = gate_row(row, corroborated)
        score = ranking_score(row, applicability, parse_tags(row.get("trap_tags", "")))

        out_rows.append({
            **row,
            "applicability": applicability,
            "score": f"{score:.1f}",
            "gate_status": gate,
            "gate_reason": reason,
            "corroboration": corro_flag,
            "source_count": len(distinct_sources),
            "sources_seen": ",".join(distinct_sources),
            "target": args.target or "",
        })

    # Sort by gate bucket (best first), then score desc within the bucket.
    out_rows.sort(key=lambda r: (GATE_RANK.get(r["gate_status"], 9),
                                 -float(r["score"])))

    fieldnames = list(out_rows[0].keys())
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    counts = defaultdict(int)
    for r in out_rows:
        counts[r["gate_status"]] += 1
    print(f"Wrote {len(out_rows)} rows to {args.output}")
    print(f"  promote: {counts['promote']}  validate: {counts['validate']}  "
          f"background: {counts['background']}  kill: {counts['kill']}")
    if any_unreliable:
        print("  WARNING: one or more rows lacked cluster_id — cross-source "
              "corroboration is UNRELIABLE for those rows (paper_id fallback). "
              "Add cluster_id to promote with confidence.", file=sys.stderr)


if __name__ == "__main__":
    main()
