#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
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


def _evidence_ids(row: dict) -> set[str]:
    evidence = row.get("evidence", [])
    ids: set[str] = set()
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, dict) and "id" in item:
                ids.add(str(item["id"]))
    retrieved = row.get("retrieved_evidence_ids", [])
    if isinstance(retrieved, list):
        ids.update(str(item) for item in retrieved)
    return ids


def _validate_row(row: dict) -> None:
    def ids(value: object, field: str) -> None:
        if not isinstance(value, list) or any(not isinstance(i, str) or not i.strip() for i in value):
            raise ValueError(f"'{field}' must be a list of nonempty string IDs")

    ids(row.get("citations"), "citations")
    if "evidence" not in row and "retrieved_evidence_ids" not in row:
        raise ValueError("missing 'evidence' or 'retrieved_evidence_ids'")
    if "retrieved_evidence_ids" in row:
        ids(row["retrieved_evidence_ids"], "retrieved_evidence_ids")
    if "evidence" in row:
        evidence = row["evidence"]
        if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
            raise ValueError("'evidence' must be a list of objects with IDs")
        ids([item.get("id") for item in evidence], "evidence[].id")
    if "claims" in row:
        claims = row["claims"]
        if not isinstance(claims, list) or any(not isinstance(claim, dict) for claim in claims):
            raise ValueError("'claims' must be a list of objects")
        for claim in claims:
            ids(claim.get("citations"), "claims[].citations")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check citation IDs against available evidence objects.",
    )
    parser.add_argument("path", help="JSONL file with citations and evidence fields.")
    parser.add_argument(
        "--require-claim-citations",
        action="store_true",
        help="Fail rows where claims exist but have no citations.",
    )
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        rows = _load_rows(path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print(f"ERROR: no rows found in {path}; nothing was checked", file=sys.stderr)
        return 2
    bad = [i for i, row in enumerate(rows, start=1) if not isinstance(row, dict)]
    if bad:
        print(f"ERROR: rows {bad[:10]} are not JSON objects", file=sys.stderr)
        return 2
    for row_number, row in enumerate(rows, start=1):
        try:
            _validate_row(row)
        except ValueError as exc:
            print(f"ERROR: row {row_number}: {exc}; nothing checked", file=sys.stderr)
            return 2

    missing_reference_rows = 0
    uncited_claim_rows = 0

    for row in rows:
        available_ids = _evidence_ids(row)
        citations = [str(item) for item in row.get("citations", [])]
        citations.extend(citation for claim in row.get("claims", []) for citation in claim["citations"])
        if any(citation not in available_ids for citation in citations):
            missing_reference_rows += 1

        if args.require_claim_citations:
            claims = row.get("claims", [])
            for claim in claims:
                if not isinstance(claim, dict):
                    continue
                claim_citations = claim.get("citations", [])
                if not claim_citations:
                    uncited_claim_rows += 1
                    break

    total_rows = len(rows)
    print(f"rows={total_rows}")
    print(f"rows_with_missing_citation_targets={missing_reference_rows}")
    if args.require_claim_citations:
        print(f"rows_with_uncited_claims={uncited_claim_rows}")

    if missing_reference_rows or uncited_claim_rows:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
