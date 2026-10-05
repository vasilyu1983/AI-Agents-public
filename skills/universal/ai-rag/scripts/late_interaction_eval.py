#!/usr/bin/env python3
"""
late_interaction_eval.py — Offline late-interaction retrieval eval harness (stdlib-only).

SCOPE: This script is an OFFLINE EVAL HARNESS, not an inference runner.
It accepts pre-computed similarity scores (from ColBERT, ColPali, or any
dense/late-interaction retriever) and computes nDCG and MRR over them.

WHY offline: ColBERT/ColPali require PyTorch and model weights. Running
inference here would add heavy non-stdlib dependencies. Instead, export
your retriever's ranked lists as JSONL (see format below) and pipe them
into this script for reproducible, lightweight evaluation.

Usage:
    python late_interaction_eval.py --input ranked_results.jsonl
    python late_interaction_eval.py --input results.jsonl --output report.json \\
        --k 10 20 --verbose
    python late_interaction_eval.py --help

Input JSONL format (one JSON object per line):
    {
      "query_id": "q001",
      "query": "What is attention mechanism?",
      "relevant_doc_ids": ["doc_42", "doc_17"],
      "ranked_results": [
        {"doc_id": "doc_42", "score": 0.92},
        {"doc_id": "doc_5",  "score": 0.88},
        {"doc_id": "doc_17", "score": 0.76}
      ]
    }

Fields:
    query_id        — unique query identifier
    query           — query text (stored for traceability)
    relevant_doc_ids — ground-truth relevant document IDs (any hit = relevant)
    ranked_results  — list of {doc_id, score} ordered by score descending

Metrics computed:
    nDCG@k  — Normalized Discounted Cumulative Gain at cutoff k
    MRR     — Mean Reciprocal Rank (first relevant doc position)
    Recall@k — fraction of relevant docs found in top-k

Exit codes:
    0 — every record was valid and scored (metric values do not imply pass/fail)
    2 — file missing, empty, or any line is malformed JSON or lacks a required
        field (query_id, query, relevant_doc_ids, ranked_results[].doc_id);
        each bad line is named on stderr and nothing is scored
"""

import argparse
import json
import math
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Metric implementations
# ---------------------------------------------------------------------------

def dcg(relevances: list[float], k: int) -> float:
    """Discounted Cumulative Gain at rank k."""
    result = 0.0
    for i, rel in enumerate(relevances[:k], 1):
        result += rel / math.log2(i + 1)
    return result


def ndcg_at_k(ranked_doc_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """nDCG@k: binary relevance (1 if in relevant_ids, 0 otherwise)."""
    rels = [1.0 if doc_id in relevant_ids else 0.0 for doc_id in ranked_doc_ids[:k]]
    # The ideal ranking includes gold documents missing from the retrieved list.
    ideal_rels = [1.0] * min(len(relevant_ids), k)
    actual = dcg(rels, k)
    ideal = dcg(ideal_rels, k)
    return actual / ideal if ideal > 0 else 0.0


def reciprocal_rank(ranked_doc_ids: list[str], relevant_ids: set[str]) -> float:
    """Reciprocal rank: 1/rank of first relevant document."""
    for i, doc_id in enumerate(ranked_doc_ids, 1):
        if doc_id in relevant_ids:
            return 1.0 / i
    return 0.0


def recall_at_k(ranked_doc_ids: list[str], relevant_ids: set[str], k: int) -> float:
    """Recall@k: fraction of relevant docs found in top-k."""
    if not relevant_ids:
        return 0.0
    found = sum(1 for doc_id in ranked_doc_ids[:k] if doc_id in relevant_ids)
    return found / len(relevant_ids)


# ---------------------------------------------------------------------------
# Input validation (fail closed: a malformed record must not score as 0)
# ---------------------------------------------------------------------------

def validate_record(record: object) -> list[str]:
    """Return a list of problems; empty means the record is scoreable."""
    if not isinstance(record, dict):
        return ["record is not a JSON object"]
    problems = []
    for key in ("query_id", "query"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            problems.append(f"missing or empty '{key}'")
    relevant = record.get("relevant_doc_ids")
    if not isinstance(relevant, list) or not relevant:
        problems.append("missing or empty 'relevant_doc_ids'")
    elif any(not isinstance(i, str) or not i.strip() for i in relevant):
        problems.append("'relevant_doc_ids' must contain nonempty string IDs")
    elif len(set(relevant)) != len(relevant):
        problems.append("duplicate relevant document IDs")
    ranked = record.get("ranked_results")
    if not isinstance(ranked, list):
        problems.append("missing 'ranked_results' list")
    else:
        for i, item in enumerate(ranked):
            if not isinstance(item, dict) or not isinstance(item.get("doc_id"), str) or not item["doc_id"].strip():
                problems.append(f"ranked_results[{i}] has no nonempty string 'doc_id'")
                break
            if "score" in item and (
                isinstance(item["score"], bool) or not isinstance(item["score"], (int, float))
                or not math.isfinite(item["score"])
            ):
                problems.append(f"ranked_results[{i}] has a non-finite or nonnumeric score")
        else:
            ids = [item["doc_id"] for item in ranked]
            if len(set(ids)) != len(ids):
                problems.append("duplicate ranked document IDs")
    return problems


# ---------------------------------------------------------------------------
# Main eval loop
# ---------------------------------------------------------------------------

def evaluate_record(record: dict, k_values: list[int]) -> dict:
    query_id = record["query_id"]
    relevant_ids = set(record["relevant_doc_ids"])
    ranked_doc_ids = [r["doc_id"] for r in record["ranked_results"]]

    result = {"query_id": query_id, "query": record["query"], "num_relevant": len(relevant_ids)}

    mrr = reciprocal_rank(ranked_doc_ids, relevant_ids)
    result["mrr"] = round(mrr, 4)

    for k in k_values:
        result[f"ndcg@{k}"] = round(ndcg_at_k(ranked_doc_ids, relevant_ids, k), 4)
        result[f"recall@{k}"] = round(recall_at_k(ranked_doc_ids, relevant_ids, k), 4)

    return result


def run(input_path: Path, output_path: Path | None, k_values: list[int], verbose: bool) -> int:
    if not k_values or any(k <= 0 for k in k_values):
        print("[ERROR] --k requires positive integer cutoffs", file=sys.stderr)
        return 2
    records: list[dict] = []
    bad_lines = 0
    try:
        with input_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] {input_path}:{lineno}: invalid JSON — {e}", file=sys.stderr)
                    bad_lines += 1
                    continue
                problems = validate_record(record)
                if problems:
                    print(f"[ERROR] {input_path}:{lineno}: {'; '.join(problems)}", file=sys.stderr)
                    bad_lines += 1
                    continue
                records.append(record)
    except (OSError, UnicodeError) as exc:
        print(f"[ERROR] Cannot read {input_path}: {exc}", file=sys.stderr)
        return 2

    if bad_lines:
        print(f"[ERROR] {bad_lines} malformed line(s); nothing scored.", file=sys.stderr)
        return 2

    if not records:
        print("[ERROR] No valid records.", file=sys.stderr)
        return 2

    results = [evaluate_record(r, k_values) for r in records]
    n = len(results)

    # Aggregate means
    agg: dict[str, float] = {"mrr": sum(r["mrr"] for r in results) / n}
    for k in k_values:
        agg[f"ndcg@{k}"] = sum(r[f"ndcg@{k}"] for r in results) / n
        agg[f"recall@{k}"] = sum(r[f"recall@{k}"] for r in results) / n

    if verbose:
        header = f"{'query_id':<25} {'MRR':>6}" + "".join(f" nDCG@{k:>2}" for k in k_values)
        print(header)
        print("-" * len(header))
        for r in results:
            row = f"{r['query_id']:<25} {r['mrr']:>6.4f}"
            for k in k_values:
                row += f" {r[f'ndcg@{k}']:>7.4f}"
            print(row)
        print()

    print(f"Evaluation summary — {n} queries, k={k_values}")
    print(f"  MRR:       {agg['mrr']:.4f}")
    for k in k_values:
        print(f"  nDCG@{k:<3}:  {agg[f'ndcg@{k}']:.4f}   Recall@{k}: {agg[f'recall@{k}']:.4f}")

    report = {
        "queries_evaluated": n,
        "k_values": k_values,
        "aggregate": {k: round(v, 4) for k, v in agg.items()},
        "per_query": results,
    }

    if output_path:
        try:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        except (OSError, UnicodeError) as exc:
            print(f"[ERROR] Cannot write {output_path}: {exc}", file=sys.stderr)
            return 2
        print(f"\nReport written to: {output_path}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline nDCG/MRR eval harness for late-interaction retrieval (pre-computed scores).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, type=Path, help="JSONL ranked results file")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON report")
    parser.add_argument(
        "--k", nargs="+", type=int, default=[5, 10, 20], dest="k_values",
        metavar="K", help="Rank cutoffs for nDCG/Recall (default: 5 10 20)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-query results")
    args = parser.parse_args()
    sys.exit(run(args.input, args.output, sorted(set(args.k_values)), args.verbose))


if __name__ == "__main__":
    main()
