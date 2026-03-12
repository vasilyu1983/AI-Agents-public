# RAG System Design Template

**Purpose**: Document architecture decisions, define evaluation criteria, plan for production operation.

---

## Template Contract

### Goals
- Deliver correct, grounded answers with measurable retrieval and generation quality.
- Meet latency/cost SLOs with a predictable, observable pipeline.
- Ensure security, privacy, and governance for the corpus and queries.

### Inputs
- Use case, query distribution, and acceptance criteria.
- Corpus characteristics (types, size, update frequency, sensitivity, ACLs).
- Platform constraints (latency, QPS, budget, residency, retention).

### Decisions
- Whether to use RAG vs alternatives, and the retrieval architecture (sparse/dense/hybrid, reranking).
- Chunking/parsing strategy and metadata schema.
- Freshness/invalidation strategy and failure fallbacks.

### Risks
- Staleness, incorrect ACL enforcement, and prompt injection via retrieved text.
- Poor retrieval recall/precision leading to hallucinations or "missing evidence."
- Cost blowups from oversized contexts or unbounded retries.

### Metrics
- Retrieval: recall@k, nDCG/MRR, empty-result rate, latency.
- Answer: groundedness/faithfulness, citation coverage, refusal correctness, hallucination rate.
- Ops: cost per request, error rate, cache hit rates, rebuild time.

## 1. Problem Definition

### Use Case
- **Domain**: _______________
- **Query types**: [ ] Factual [ ] Analytical [ ] Conversational [ ] Multi-hop
- **Expected QPS**: ___
- **Latency budget (total)**: ___ms
- **Latency budget (retrieval)**: ___ms

### Data Characteristics
- **Corpus size**: ___ documents / ___ chunks
- **Update frequency**: [ ] Real-time [ ] Hourly [ ] Daily [ ] Weekly [ ] Static
- **Document types**: [ ] Text [ ] Tables [ ] Code [ ] PDFs [ ] Images [ ] Mixed
- **Average doc length**: ___ tokens
- **Languages**: _______________
- **Sensitive data**: [ ] PII [ ] Confidential [ ] Public only

---

## 2. Decision: Is RAG the Right Approach?

### RAG Decision Tree

```
All data fits in context window?
  -> YES: Consider direct prompting (simpler, faster)
  -> NO: Continue...

Data changes frequently?
  -> YES: RAG preferred (vs fine-tuning)
  -> NO: Consider fine-tuning if data is stable

Need citations/traceability?
  -> YES: RAG required
  -> NO: Fine-tuning acceptable

Latency budget <100ms?
  -> YES: Pre-compute or fine-tune
  -> NO: RAG acceptable

Query requires reasoning over multiple docs?
  -> YES: RAG with multi-hop retrieval
  -> NO: Standard RAG or hybrid
```

### Decision
- [ ] RAG is appropriate for this use case
- [ ] Alternative considered: _______________
- [ ] Rationale: _______________

---

## 3. Architecture Decisions

### Chunking Strategy

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Fixed-size (token) | Simple, predictable | May break semantics | [ ] |
| Semantic | Preserves meaning | More complex | [ ] |
| Hierarchical | Multi-granularity | Storage overhead | [ ] |
| Sentence-based | Natural boundaries | Variable sizes | [ ] |

**Selected approach**: _______________
- Chunk size: ___ tokens
- Overlap: ___ tokens
- Rationale: _______________

### Embedding Model

| Candidate | Type | Dimensions | Max Length | Multilingual | Decision |
|----------|------|------------|------------|--------------|----------|
| Candidate 1 | Managed API | ___ | ___ | ___ | [ ] |
| Candidate 2 | Open-weight | ___ | ___ | ___ | [ ] |
| Candidate 3 | Hybrid | ___ | ___ | ___ | [ ] |

**Selected model**: _______________
- Rationale: _______________

### Retrieval Method

| Method | When to Use | Decision |
|--------|-------------|----------|
| Dense only | Semantic understanding primary | [ ] |
| Sparse only (BM25) | Exact keyword matching needed | [ ] |
| Hybrid | Best of both (recommended default) | [ ] |

**Selected method**: _______________
- Hybrid weights (if applicable): Dense=___, Sparse=___
- Top-K: ___

### Reranking

- [ ] Reranking enabled
- Reranker model: _______________
- Rerank top-K: ___
- Final top-K after rerank: ___

### Vector Store

| Option | Type | Best For | Decision |
|--------|------|----------|----------|
| Managed vector DB | Managed | Low ops, scale | [ ] |
| Self-hosted vector DB | Self-hosted | Control, customization | [ ] |
| SQL vector extension | Self-managed | Existing SQL infra | [ ] |
| Embedded/local index | Embedded | Dev, small corpora | [ ] |

**Selected store**: _______________
- Index type: [ ] HNSW [ ] IVF [ ] Flat
- Distance metric: [ ] Cosine [ ] L2 [ ] Inner Product

---

## 4. Contextual Retrieval (Recommended)

### Chunk Context Augmentation
- [ ] Add lightweight context to chunks before embedding (document title/section summary)
- Context generation method: _______________
- Context length: ___ tokens per chunk

### Implementation
```yaml
chunk_format:
  context: "{document_summary}. {section_context}"
  content: "{chunk_text}"
  metadata: {source, page, section, timestamp}
```

---

## 5. Evaluation Plan

### Retrieval Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Recall@K | >=___ | Golden dataset |
| Precision@K | >=___ | Human annotation |
| MRR | >=___ | Ranked relevance |
| NDCG@K | >=___ | Graded relevance |

### Answer Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Faithfulness | >=___ | LLM-as-judge |
| Relevance | >=___ | LLM-as-judge |
| Citation coverage | >=___% | Automated check |
| Hallucination rate | <___% | Human review |

### Test Set Requirements
- [ ] Minimum 100 test queries
- [ ] Ground truth documents identified
- [ ] Adversarial queries included (edge cases)
- [ ] Multi-hop queries included (if applicable)

---

## 6. Production Considerations

### Index Freshness

| Strategy | Trigger | Implementation |
|----------|---------|----------------|
| Full rebuild | Schedule | Every ___ hours/days |
| Incremental | Event | On document change |
| Real-time | Stream | Pub/sub pipeline |

**Selected strategy**: _______________
- Staleness tolerance: ___ hours
- Invalidation approach: _______________

### Failure Modes & Fallbacks

| Failure | Detection | Fallback |
|---------|-----------|----------|
| No relevant chunks | Max similarity < ___ | Broader search / admit uncertainty |
| Stale data | Timestamp > ___ days | Force refresh / warn user |
| Embedding service down | Health check | Cached embeddings / keyword search |
| Vector store unavailable | Connection timeout | Read replica / graceful degradation |
| Reranker timeout | >___ms | Skip reranking, use initial results |

### Monitoring

| Metric | Alert Threshold |
|--------|-----------------|
| Retrieval latency P95 | >___ms |
| Embedding latency P95 | >___ms |
| Average retrieval score | <___ |
| Empty result rate | >___% |
| Citation coverage | <___% |

---

## 7. Security & Privacy

- [ ] PII detection in chunks
- [ ] Access control per document/chunk
- [ ] Audit logging for queries
- [ ] Data retention policy defined
- [ ] Encryption at rest and in transit

---

## 8. Cost Estimation

| Component | Unit Cost | Volume | Monthly Cost |
|-----------|-----------|--------|--------------|
| Embedding API | $/1K tokens | ___ | $___ |
| Vector store | $/GB/month | ___GB | $___ |
| Reranker API | $/1K queries | ___ | $___ |
| LLM generation | $/1K tokens | ___ | $___ |
| **Total** | | | $___ |

---

## 9. Implementation Checklist

### Phase 1: Data Pipeline
- [ ] Document ingestion implemented
- [ ] Chunking strategy implemented
- [ ] Embedding pipeline working
- [ ] Vector store provisioned and indexed

### Phase 2: Retrieval
- [ ] Query embedding working
- [ ] Vector search working
- [ ] Hybrid search configured (if applicable)
- [ ] Reranking integrated (if applicable)

### Phase 3: Generation
- [ ] Context injection working
- [ ] Citation extraction implemented
- [ ] Grounding validation active

### Phase 4: Evaluation
- [ ] Test set created
- [ ] Retrieval metrics baseline established
- [ ] Answer quality metrics baseline established
- [ ] Regression tests automated

### Phase 5: Production
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Index refresh automated
- [ ] Failover tested

---

## 10. Sign-Off

| Role | Name | Date |
|------|------|------|
| ML Engineer | | |
| Data Engineer | | |
| Platform Engineer | | |
| Product Owner | | |
