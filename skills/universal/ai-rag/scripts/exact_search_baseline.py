#!/usr/bin/env python3
"""Run exact vector search over JSONL docs and emit retrieval-eval predictions.

Inputs are intentionally backend-neutral. Documents need an id, text, and either
an embedding array or text for the deterministic hash embedder. Queries need a
case_id, query, expected_ids, and either an embedding array or text.

Examples:
    python scripts/exact_search_baseline.py docs.jsonl queries.jsonl --hash-embed > predictions.jsonl
    python scripts/exact_search_baseline.py docs.jsonl queries.jsonl --metric dot --k 20 > predictions.jsonl
    python scripts/retrieval_eval.py predictions.jsonl --k 5,10
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSON on line {line_number}: {exc}") from exc
    return rows


def hash_embedding(text: str, dim: int) -> list[float]:
    vector = [0.0] * dim
    tokens = re.findall(r"[A-Za-z0-9_:-]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign
    return normalize(vector)


def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def as_vector(row: dict[str, Any], field: str, text_field: str, use_hash: bool, dim: int) -> list[float]:
    raw = row.get(field)
    if isinstance(raw, list):
        return [float(value) for value in raw]
    if use_hash:
        return hash_embedding(str(row.get(text_field, "")), dim)
    raise ValueError(f"row missing embedding field {field!r}: {row.get('id') or row.get('case_id')}")


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} != {len(b)}")
    na = math.sqrt(sum(value * value for value in a))
    nb = math.sqrt(sum(value * value for value in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dimension mismatch: {len(a)} != {len(b)}")
    return sum(x * y for x, y in zip(a, b))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", help="JSONL docs with id, text, and embedding")
    parser.add_argument("queries", help="JSONL queries with case_id, query, expected_ids, and embedding")
    parser.add_argument("--doc-id-field", default="id")
    parser.add_argument("--doc-text-field", default="text")
    parser.add_argument("--query-id-field", default="case_id")
    parser.add_argument("--query-text-field", default="query")
    parser.add_argument("--embedding-field", default="embedding")
    parser.add_argument("--metric", choices=("cosine", "dot"), default="cosine")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--hash-embed", action="store_true", help="Use deterministic lexical hash vectors when embeddings are absent.")
    parser.add_argument("--hash-dim", type=int, default=512)
    args = parser.parse_args()

    try:
        docs = load_jsonl(Path(args.documents))
        queries = load_jsonl(Path(args.queries))
        doc_vectors = [
            (
                str(doc[args.doc_id_field]),
                as_vector(doc, args.embedding_field, args.doc_text_field, args.hash_embed, args.hash_dim),
            )
            for doc in docs
        ]
        score_fn = cosine if args.metric == "cosine" else dot
        for query in queries:
            q_vec = as_vector(query, args.embedding_field, args.query_text_field, args.hash_embed, args.hash_dim)
            scored = sorted(
                ((doc_id, score_fn(q_vec, d_vec)) for doc_id, d_vec in doc_vectors),
                key=lambda item: item[1],
                reverse=True,
            )[: args.k]
            print(json.dumps({
                "case_id": query.get(args.query_id_field),
                "query": query.get(args.query_text_field),
                "expected_ids": query.get("expected_ids", []),
                "retrieved_ids": [doc_id for doc_id, _ in scored],
                "scores": {doc_id: score for doc_id, score in scored},
                "retrieval_method": f"exact_{args.metric}",
            }, ensure_ascii=True))
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
