#!/usr/bin/env python3
"""Backend-neutral BM25-lite + vector + RRF demo for retrieval experiments.

This is a portable teaching and smoke-test script, not a replacement for a real
search engine. It accepts the same JSONL shape as exact_search_baseline.py and
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


def lexical_scores(query_terms: list[str], doc_tokens: list[list[str]], idf_map: dict[str, float]) -> list[float]:
    scores: list[float] = []
    for doc in doc_tokens:
        counts = Counter(doc)
        length_norm = 1.0 / math.sqrt(max(len(doc), 1))
        scores.append(sum(counts[term] * idf_map.get(term, 0.0) for term in query_terms) * length_norm)
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
            sparse = lexical_scores(q_terms, doc_tokens, idf_map)
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
                "retrieval_method": "bm25_lite_vector_rrf",
            }, ensure_ascii=True))
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
