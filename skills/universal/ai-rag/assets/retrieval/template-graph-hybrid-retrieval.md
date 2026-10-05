# Graph + Vector Retrieval Template

Use when questions need both relationship traversal and unstructured evidence.

```yaml
retrieval_mode: graph_plus_vector

authority_sources:
  graph:
    type: "knowledge_graph"
    strengths: ["entity_relationships", "joins", "multi_hop"]
  vector:
    type: "hybrid_search"
    strengths: ["unstructured_context", "supporting_quotes"]

query_router:
  - if: "needs entity traversal or counts"
    use: "graph_first"
  - if: "needs explanatory prose or direct quotations"
    use: "vector_first"
  - if: "needs both"
    use: "graph_then_vector"

graph_stage:
  entity_extraction: true
  traversal_limit: 2
  return_fields: [entity_id, relation_path, confidence]

vector_stage:
  candidate_k: 20
  reranker: optional
  return_fields: [evidence_id, snippet, source]

merge:
  deduplicate_by: [entity_id, source]
  prefer_authority_for_facts: graph
  require_text_evidence_for_quotes: true
```

Checklist:

- [ ] Graph-only and vector-only baselines measured first
- [ ] Traversal depth bounded to control latency
- [ ] Merge policy defined for conflicting facts
- [ ] Final answer distinguishes structured facts from supporting prose
