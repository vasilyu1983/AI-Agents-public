# Backend Comparison Fixtures

Use this when comparing pgvector, Qdrant, Elasticsearch/OpenSearch, hosted file
search, or another retrieval backend. Compare prediction files, not vendor claims.

## Contents

- [Protocol](#protocol)
- [Prediction File Shape](#prediction-file-shape)
- [Report](#report)
- [Decision Rules](#decision-rules)

## Protocol

1. Freeze one corpus snapshot.
2. Freeze one golden query file.
3. Use the same expected evidence IDs for every backend.
4. Run each backend and emit one prediction JSONL file.
5. Evaluate each file with `scripts/retrieval_eval.py`.
6. Slice failures by tags: `policy`, `code`, `pdf`, `acl`, `unanswerable`,
   `lexical_required`, `multilingual`, `staleness`.
7. Record latency, index build time, memory/storage footprint, and reindex cost.

Start from `assets/eval/backend-comparison-template.json`.

## Prediction File Shape

```json
{
  "case_id": "generic_code_symbol_lookup",
  "expected_ids": ["repo:service-client:retry-config"],
  "retrieved_ids": ["repo:service-client:retry-config", "repo:service-client:call-wrapper"],
  "graded_relevance": {
    "repo:service-client:retry-config": 3,
    "repo:service-client:call-wrapper": 2
  },
  "latency_ms": 42,
  "retrieval_method": "hybrid_rrf"
}
```

## Report

Report at minimum:

- recall@5 and recall@10
- MRR@10
- nDCG@10
- empty-result rate
- P50/P95 latency
- index build time
- storage footprint
- re-embed or reindex cost
- failed critical slices

## Decision Rules

- Prefer the simplest backend that passes the critical slices.
- Do not choose a backend on unfiltered k-NN throughput if production queries
  are filter-heavy.
- Do not accept a backend that cannot enforce tenant or ACL isolation before
  returning candidates.
- Treat hosted retrieval defaults as unknown until freshness, deletion, ACL,
  and citation behavior are verified.
- Keep source truth outside the vector index unless the backend is also the
  system of record and logical separation is enforced.

## Sources

- Qdrant hybrid search and reranking:
  https://qdrant.tech/documentation/search-precision/reranking-hybrid-search/
