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


def _skip_reason(row: object) -> str | None:
    """Return why a row cannot be scored, or None if it can."""
    if not isinstance(row, dict):
        return "not a JSON object"
    expected = row.get("expected_ids")
    if not isinstance(expected, list):
        return "missing 'expected_ids' list"
    if not expected:
        return "empty 'expected_ids' (no-answer case: recall/MRR/nDCG are undefined; score abstention separately)"
    if not isinstance(row.get("retrieved_ids"), list):
        return "missing 'retrieved_ids' list (use [] when retrieval returned nothing)"
    return None


def _validate_row(row: object) -> None:
    if not isinstance(row, dict):
        raise ValueError("not a JSON object")
    for field in ("expected_ids", "retrieved_ids"):
        ids = row.get(field)
        if not isinstance(ids, list) or any(not isinstance(i, str) or not i.strip() for i in ids):
            raise ValueError(f"'{field}' must be a list of nonempty string IDs")
        if len(set(ids)) != len(ids):
            raise ValueError(f"'{field}' contains duplicate IDs")
    if "forbidden_ids" in row:
        forbidden = row["forbidden_ids"]
        if not isinstance(forbidden, list) or any(not isinstance(i, str) or not i.strip() for i in forbidden):
            raise ValueError("'forbidden_ids' must be a list of nonempty string IDs")
        if set(forbidden) & set(row["expected_ids"]):
            raise ValueError("an ID cannot be both expected and forbidden")
    if "graded_relevance" in row:
        graded = row["graded_relevance"]
        if not isinstance(graded, dict) or any(
            not isinstance(key, str) or not key.strip()
            or isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0
            for key, value in graded.items()
        ):
            raise ValueError("'graded_relevance' must map nonempty IDs to finite nonnegative numbers")
        if any(graded.get(item, 0) <= 0 for item in row["expected_ids"]):
            raise ValueError("every expected ID must have positive graded relevance")


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
        if not cutoffs or any(cutoff <= 0 for cutoff in cutoffs):
            raise ValueError("--k requires positive integer cutoffs")
        cutoffs = sorted(set(cutoffs))
        rows = _load_rows(path)
        for row_number, row in enumerate(rows, start=1):
            try:
                _validate_row(row)
            except ValueError as exc:
                raise ValueError(f"row {row_number}: {exc}; nothing scored") from exc
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print("ERROR: no rows found", file=sys.stderr)
        return 2

    totals: dict[int, dict[str, float]] = {
        cutoff: {"recall": 0.0, "mrr": 0.0, "ndcg": 0.0}
        for cutoff in cutoffs
    }

    # Forbidden IDs (superseded, out-of-scope, above caller clearance) are checked on every
    # row, including no-answer rows that recall/MRR/nDCG skip.
    forbidden_rows = 0
    forbidden_hits = {cutoff: 0 for cutoff in cutoffs}
    for row in rows:
        forbidden = set(row.get("forbidden_ids") or [])
        if forbidden:
            forbidden_rows += 1
            for cutoff in cutoffs:
                if forbidden & set(row["retrieved_ids"][:cutoff]):
                    forbidden_hits[cutoff] += 1

    scored_rows = 0
    skipped_rows = 0
    for line_index, row in enumerate(rows, start=1):
        reason = _skip_reason(row)
        if reason:
            skipped_rows += 1
            print(f"WARNING: skipping row {line_index}: {reason}", file=sys.stderr)
            continue
        scored_rows += 1
        expected = {str(item) for item in row["expected_ids"]}
        retrieved = [str(item) for item in row["retrieved_ids"]]
        graded = row.get("graded_relevance")
        if isinstance(graded, dict):
            relevance = {str(key): float(value) for key, value in graded.items()}
        else:
            relevance = {item: 1.0 for item in expected}

        for cutoff in cutoffs:
            totals[cutoff]["recall"] += _recall_at_k(retrieved, expected, cutoff)
            totals[cutoff]["mrr"] += _mrr_at_k(retrieved, expected, cutoff)
            totals[cutoff]["ndcg"] += _ndcg_at_k(retrieved, relevance, cutoff)

    if scored_rows == 0 and forbidden_rows == 0:
        print(f"ERROR: all {skipped_rows} rows were skipped; nothing was scored", file=sys.stderr)
        return 2

    row_count = scored_rows
    print(f"rows={len(rows)} scored={scored_rows} skipped={skipped_rows} forbidden_rows={forbidden_rows}")
    for cutoff in cutoffs:
        line = f"k={cutoff}"
        if row_count:
            line += (
                f" recall={totals[cutoff]['recall'] / row_count:.4f}"
                f" mrr={totals[cutoff]['mrr'] / row_count:.4f}"
                f" ndcg={totals[cutoff]['ndcg'] / row_count:.4f}"
            )
        if forbidden_rows:
            line += f" forbidden_hit_rows={forbidden_hits[cutoff]}"
        print(line)
    if forbidden_rows and any(forbidden_hits.values()):
        print("FAIL: a forbidden ID was retrieved", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
