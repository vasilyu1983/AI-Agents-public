# Multivector Retrieval Template

Use when single-vector retrieval misses subtle relevance and token-level or field-level matching matters.

```yaml
retrieval_mode: multivector

encoder:
  family: "late_interaction_or_named_vectors"
  query_representation: "multi_vector"
  document_representation: "multi_vector"

candidate_generation:
  baseline:
    - bm25
    - dense
  candidate_k: 50

multivector_stage:
  enabled: true
  technique: "late_interaction|named_vectors|multivectors"
  score_aggregation: "maxsim_or_vendor_equivalent"
  rerank_top_k: 20

filters:
  tenant_id: required
  acl: required
  language: optional
  source_type: optional

output:
  final_k: 5
  return_fields: [evidence_id, score, source, snippet, metadata]
```

Checklist:

- [ ] Baseline hybrid path measured before enabling multivectors
- [ ] Candidate set large enough for reranking to matter
- [ ] Latency budget measured with real documents
- [ ] Fallback path exists if multivector stage times out
