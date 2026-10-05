#!/usr/bin/env python3
"""Backend-neutral BM25 + vector + RRF demo for retrieval experiments.

This is a portable teaching and smoke-test script, not a replacement for a real
search engine. The lexical leg is Okapi BM25 (Lucene-style IDF, k1 term-frequency
saturation, b length normalisation) so --k1/--b line up with the grid in
references/bm25-tuning.md. It accepts the same JSONL shape as exact_search_baseline.py and
emits predictions compatible with retrieval_eval.py.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from exact_search_baseline import as_vector, cosine, load_jsonl


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_:-]+", text.lower())


def idf(doc_tokens: list[list[str]]) -> dict[str, float]:
    total = len(doc_tokens)
    df: Counter[str] = Counter()
    for doc in doc_tokens:
        df.update(set(doc))
    return {term: math.log(1 + (total - count + 0.5) / (count + 0.5)) for term, count in df.items()}


def lexical_scores(
    query_terms: list[str],
    doc_tokens: list[list[str]],
    idf_map: dict[str, float],
    k1: float = 1.2,
    b: float = 0.75,
) -> list[float]:
    """Okapi BM25. k1 caps how much repeated terms count; b scales the length penalty."""
    avg_len = sum(len(doc) for doc in doc_tokens) / max(len(doc_tokens), 1)
    scores: list[float] = []
    for doc in doc_tokens:
        counts = Counter(doc)
        norm = k1 * (1.0 - b + b * len(doc) / max(avg_len, 1e-9))
        score = 0.0
        for term in query_terms:
            tf = counts[term]
            if tf:
                score += idf_map.get(term, 0.0) * tf * (k1 + 1.0) / (tf + norm)
        scores.append(score)
    return scores


def rank_map(scores: list[float], ids: list[str], limit: int) -> dict[str, int]:
    ranked = sorted(zip(ids, scores), key=lambda item: item[1], reverse=True)
    return {doc_id: rank for rank, (doc_id, _) in enumerate(ranked[:limit], start=1)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents")
    parser.add_argument("queries")
    parser.add_argument("--doc-id-field", default="id")
    parser.add_argument("--doc-text-field", default="text")
    parser.add_argument("--query-id-field", default="case_id")
    parser.add_argument("--query-text-field", default="query")
    parser.add_argument("--embedding-field", default="embedding")
    parser.add_argument("--hash-embed", action="store_true")
    parser.add_argument("--hash-dim", type=int, default=512)
    parser.add_argument("--candidate-k", type=int, default=50)
    parser.add_argument("--return-k", type=int, default=10)
    parser.add_argument("--rrf-k", type=float, default=60.0)
    parser.add_argument("--k1", type=float, default=1.2, help="BM25 term-frequency saturation")
    parser.add_argument("--b", type=float, default=0.75, help="BM25 length normalisation (0=off, 1=full)")
    args = parser.parse_args()

    try:
        docs = load_jsonl(Path(args.documents))
        queries = load_jsonl(Path(args.queries))
        ids = [str(doc[args.doc_id_field]) for doc in docs]
        doc_texts = [str(doc.get(args.doc_text_field, "")) for doc in docs]
        doc_tokens = [tokens(text) for text in doc_texts]
        idf_map = idf(doc_tokens)
        doc_vectors = [
            as_vector(doc, args.embedding_field, args.doc_text_field, args.hash_embed, args.hash_dim)
            for doc in docs
        ]

        for query in queries:
            q_text = str(query.get(args.query_text_field, ""))
            q_terms = tokens(q_text)
            q_vec = as_vector(query, args.embedding_field, args.query_text_field, args.hash_embed, args.hash_dim)
            sparse = lexical_scores(q_terms, doc_tokens, idf_map, args.k1, args.b)
            dense = [cosine(q_vec, doc_vec) for doc_vec in doc_vectors]
            sparse_ranks = rank_map(sparse, ids, args.candidate_k)
            dense_ranks = rank_map(dense, ids, args.candidate_k)
            fused: dict[str, float] = {}
            for doc_id, rank in sparse_ranks.items():
                fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (args.rrf_k + rank)
            for doc_id, rank in dense_ranks.items():
                fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (args.rrf_k + rank)
            ranked = sorted(fused.items(), key=lambda item: item[1], reverse=True)[: args.return_k]
            print(json.dumps({
                "case_id": query.get(args.query_id_field),
                "query": q_text,
                "expected_ids": query.get("expected_ids", []),
                "retrieved_ids": [doc_id for doc_id, _ in ranked],
                "scores": {doc_id: score for doc_id, score in ranked},
                "retrieval_method": "bm25_vector_rrf",
            }, ensure_ascii=True))
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
