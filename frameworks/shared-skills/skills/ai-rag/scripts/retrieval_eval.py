#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def _load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return rows


def _recall_at_k(retrieved: list[str], expected: set[str], k: int) -> float:
    if not expected:
        return 0.0
    hits = sum(1 for item in retrieved[:k] if item in expected)
    return hits / len(expected)


def _mrr_at_k(retrieved: list[str], expected: set[str], k: int) -> float:
    for rank, item in enumerate(retrieved[:k], start=1):
        if item in expected:
            return 1.0 / rank
    return 0.0


def _ndcg_at_k(retrieved: list[str], relevance: dict[str, float], k: int) -> float:
    if not relevance:
        return 0.0
    dcg = 0.0
    for rank, item in enumerate(retrieved[:k], start=1):
        gain = relevance.get(item, 0.0)
        if gain <= 0:
            continue
        dcg += gain / math.log2(rank + 1)

    ideal = sorted(relevance.values(), reverse=True)[:k]
    idcg = 0.0
    for rank, gain in enumerate(ideal, start=1):
        idcg += gain / math.log2(rank + 1)
    if idcg == 0:
        return 0.0
    return dcg / idcg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute retrieval metrics from JSONL predictions.",
    )
    parser.add_argument("path", help="JSONL file with expected_ids and retrieved_ids fields.")
    parser.add_argument(
        "--k",
        default="5,10",
        help="Comma-separated cutoffs to report (default: 5,10).",
    )
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        cutoffs = [int(part) for part in args.k.split(",") if part.strip()]
        rows = _load_rows(path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print("ERROR: no rows found", file=sys.stderr)
        return 2

    totals: dict[int, dict[str, float]] = {
        cutoff: {"recall": 0.0, "mrr": 0.0, "ndcg": 0.0}
        for cutoff in cutoffs
    }

    for row in rows:
        expected = set(row.get("expected_ids", []))
        retrieved = list(row.get("retrieved_ids", []))
        graded = row.get("graded_relevance")
        if isinstance(graded, dict):
            relevance = {str(key): float(value) for key, value in graded.items()}
        else:
            relevance = {item: 1.0 for item in expected}

        for cutoff in cutoffs:
            totals[cutoff]["recall"] += _recall_at_k(retrieved, expected, cutoff)
            totals[cutoff]["mrr"] += _mrr_at_k(retrieved, expected, cutoff)
            totals[cutoff]["ndcg"] += _ndcg_at_k(retrieved, relevance, cutoff)

    row_count = len(rows)
    print(f"rows={row_count}")
    for cutoff in cutoffs:
        print(
            f"k={cutoff} "
            f"recall={totals[cutoff]['recall'] / row_count:.4f} "
            f"mrr={totals[cutoff]['mrr'] / row_count:.4f} "
            f"ndcg={totals[cutoff]['ndcg'] / row_count:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
