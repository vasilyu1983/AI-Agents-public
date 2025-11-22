---
name: ai-llm-search-retrieval
description: >
  Operational patterns for search systems (Modern hybrid advances): billion-scale HNSW-IF,
  multi-vector indexing, Reciprocal Rank Fusion (RRF), semantic search with embeddings,
  BM25 + vector hybrid, ranking pipelines, query rewriting, nDCG/MRR evaluation. Emphasizes
  Modern shift to hybrid retrieval with semantic ranker for significant relevance gains.
---

# Search & Retrieval Engineering – Quick Reference

This skill provides **practical patterns** with Modern hybrid search advances:

- **Hybrid search (Modern standard):** BM25 + vector with **significant relevance benefits**
- BM25 and lexical retrieval tuning
- Dense vector search (embeddings)
- **Billion-scale HNSW-IF** (hybrid hierarchical navigable small world + inverted file)
- **Multi-vector HNSW indexing** (multiple vectors per document)
- **ANN indexing:** HNSW (best performers in benchmarks), IVF, ScaNN, PQ
- **Reciprocal Rank Fusion (RRF)** for scoring final results
- Ranking pipelines (retrieval → rerank → fusion)
- Query rewriting and expansion
- Search quality evaluation (nDCG, MRR, recall@k)
- Debugging irrelevance, drift, and query mismatch
- Templates for search configurations

**Key Insights:**

- **Hybrid retrieval with semantic ranker** offers significant benefits in search relevance (benchmarks)
- **HNSW-based libraries** are among best performers in approximate nearest neighbors
- **RRF (Reciprocal Rank Fusion)** is standard for scoring parallel vector queries and hybrid search

This skill covers **general retrieval**, separate from RAG-specific workflows.

**Scope note:** Use this skill for retrieval/search tuning. For RAG context packaging, grounding, and generation prompts, see [ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md).

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Hybrid Search | BM25 + Vector + RRF | Elasticsearch, OpenSearch, Qdrant, Weaviate | Modern standard, significant relevance benefits |
| BM25 Tuning | Lucene/ES | k1=1.2-1.8, b=0.55-0.75 | Lexical retrieval optimization |
| Vector Search | HNSW, IVF | FAISS, Pinecone, Weaviate | Semantic search, <10M: HNSW, >10M: IVF |
| Reranking | Cross-encoder, LLM | MonoT5, MonoBERT, LLM reranker | Top-k candidates noisy, 5-10% nDCG improvement |
| Query Rewriting | LLM expansion | Claude, GPT prompt patterns | Ambiguous queries, synonym expansion |
| Evaluation | nDCG, MRR | Recall@K, Precision@K metrics | Search quality validation |

---

## Decision Tree: Search Architecture Selection

```text
Building search system: [Search Strategy]
    ├─ Query type?
    │   ├─ Keyword-based? → BM25 (fast, interpretable baseline)
    │   ├─ Semantic meaning? → Dense vector search (embeddings)
    │   └─ Mixed queries? → Hybrid (BM25 + Vector + RRF) → Modern standard
    │
    ├─ Dataset size?
    │   ├─ <100k documents? → Flat index (exact search)
    │   ├─ 100k-10M? → HNSW (best performer in ANN benchmarks)
    │   └─ >10M? → IVF/ScaNN/DiskANN (billion-scale HNSW-IF)
    │
    ├─ Results quality?
    │   ├─ Top results noisy? → Reranking (cross-encoder, 5-10% nDCG gain)
    │   ├─ Queries ambiguous? → Query rewriting (LLM expansion)
    │   └─ Need filtering? → Metadata + hybrid search
    │
    └─ Production quality?
        └─ Full pipeline: Hybrid + RRF + Reranking + Query expansion → Optimal relevance
```

---

## When to Use This Skill

Claude should invoke this skill when the user asks for:

- "Improve search relevance."
- "Design a BM25 or vector search index."
- "Hybrid search (BM25 + embeddings)."
- "Debug why search returns irrelevant results."
- "Tune HNSW parameters."
- "Create a ranking pipeline."
- "Build a query rewriting model."
- "Evaluate search results (nDCG, MRR)."

If the user asks for:

- **RAG retrieval design** → use `ai-llm-rag-engineering`
- **LLM generation / prompting** → use `ai-llm-development`
- **Inference optimization** → use `ai-llm-ops-inference`
- **Deployment / APIs** → use `ai-ml-ops-production`

## Related Skills

For adjacent topics, reference these skills:

- **[ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md)** - RAG pipelines, chunking strategies, context packaging (uses search-retrieval for candidate generation)
- **[ai-llm-engineering](../ai-llm-engineering/SKILL.md)** - Agentic workflows, multi-agent systems, LLM orchestration
- **[ai-llm-development](../ai-llm-development/SKILL.md)** - Prompting, fine-tuning, instruction datasets
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Prompt patterns for query rewriting and generation
- **[ai-llm-ops-inference](../ai-llm-ops-inference/SKILL.md)** - Serving performance, quantization, batching
- **[ai-ml-ops-production](../ai-ml-ops-production/SKILL.md)** - Deployment, monitoring, data pipelines

---

# Core Workflow

## Standard Retrieval Pipeline Structure

**Architecture:**

1. **Query preprocessing**
   - Tokenization
   - Normalization
   - Spell correction (optional)

2. **Candidate generation**
   - Sparse (BM25)
   - Dense (ANN vector search)
   - Hybrid (union or weighted fusion)

3. **Reranking**
   - Cross-encoder or gradient-boosted ranker
   - LLM reranker (optional)

4. **Result presentation**
   - Deduping
   - Highlighting
   - Pagination

**Checklist: retrieval pipeline ready**

- [ ] Lexical/dense retrieval combined or justified
- [ ] Reranking applied for top candidates
- [ ] Deduping enabled
- [ ] Query normalization rules documented

---

## Modern Hybrid Search (Best Practice)

**Key Finding:** Benchmark testing indicates that **hybrid retrieval with semantic ranker offers significant benefits in search relevance.**

### Fusion Strategies

1. **Reciprocal Rank Fusion (RRF) - Modern Standard**
   - Formula: score = Σ (1 / (k + rank_i))
   - **Used for:** Scoring final search results when running 2+ vector queries in parallel or combining vector + text queries
   - **HNSW ranking:** Keeps track of ordered set of most similar vectors, forms ranked result set

2. **Weighted sum**
   - score = α * bm25 + β * vector_similarity
   - Tune α/β on evaluation set

3. **Learning-to-Rank fusion**
   - Train model on combined features
   - Best for production systems with labeled data

**Modern Architectures:**

- **Billion-scale HNSW-IF:** Hybrid hierarchical navigable small world + inverted file for massive scale
- **Multi-vector HNSW:** Multiple vectors per document, retrieve by closest vector in each
- **Semantic search with embeddings:** Transformer-based vector mapping deployed to serving layer for runtime inference

**Checklist: hybrid tuned**

- [ ] Hybrid retrieval enabled as default (Modern best practice)
- [ ] RRF (Reciprocal Rank Fusion) implemented for final scoring
- [ ] Fusion strategy selected (RRF, weighted sum, or L2R)
- [ ] α/β weights validated on eval set (if using weighted sum)
- [ ] Semantic ranker integrated for relevance boost
- [ ] Latency measured for both branches (BM25 + vector)
- [ ] Billion-scale architecture evaluated (HNSW-IF) if dataset >10M

---

# Detailed Guides (Resources)

For comprehensive operational patterns, see:

## BM25 & Sparse Retrieval

- **[BM25 Tuning Guide](resources/bm25-tuning.md)** - Parameter optimization (k1, b), field weighting, query expansion, tokenization

## Vector & Dense Retrieval

- **[Vector Search Patterns](resources/vector-search-patterns.md)** - Embedding selection, ANN index patterns (HNSW, IVF, ScaNN), retrieval workflow, drift detection

## Hybrid Search & Fusion

- **[Hybrid Fusion Patterns](resources/hybrid-fusion-patterns.md)** - RRF implementation, weighted sum, two-stage fusion strategies, modern architectures

## Query Understanding

- **[Query Rewriting Patterns](resources/query-rewriting-patterns.md)** - Clarification, keyword expansion, semantic rewriting, multi-step decomposition, LLM prompts

## Ranking & Reranking

- **[Ranking Pipeline Guide](resources/ranking-pipeline-guide.md)** - Multi-stage ranking architecture, candidate generation, filtering, fusion, scoring

## Evaluation & Metrics

- **[Search Evaluation Guide](resources/search-evaluation-guide.md)** - nDCG, MRR, Recall@K, Precision@K metrics, statistical significance testing, A/B testing, monitoring

## Debugging & Troubleshooting

- **[Search Debugging Guide](resources/search-debugging.md)** - Troubleshooting irrelevance, low recall, latency issues, root cause analysis

## Advanced Patterns

- **[User Feedback & Relevance Learning](resources/user-feedback-learning.md)** - Signal capture, label generation, online experimentation, reranker training, continuous monitoring
- **[Multilingual & Domain Patterns](resources/multilingual-domain-patterns.md)** - Multilingual embeddings, language detection, cross-language retrieval, domain-specific models
- **[Distributed Search Operations & SLOs](resources/distributed-search-slos.md)** - Topology & consistency, resilience, backpressure, caching, performance runbooks, upgrades & rollbacks

---

# Templates

## Indexing & Search Configs

- [BM25 Configuration](templates/search/template-bm25-config.md) - Parameter tuning, field boosts
- [HNSW Configuration](templates/search/template-hnsw-config.md) - Vector index settings for <10M docs
- [IVF Configuration](templates/search/template-ivf-config.md) - Large-scale vector search >10M docs
- [Hybrid Search Configuration](templates/search/template-hybrid-config.md) - BM25 + vector fusion

## Ranking Pipelines

- [Ranking Pipeline Template](templates/ranking/template-ranking-pipeline.md) - Multi-stage ranking architecture
- [Reranker Template](templates/ranking/template-reranker.md) - Cross-encoder and LLM reranking

## Query Rewriting

- [Query Rewrite Template](templates/query/template-query-rewrite.md) - LLM-based query expansion and clarification

## Evaluation

- [Search Evaluation Template](templates/eval/template-search-eval.md) - nDCG, MRR, recall@k metrics
- [Search Test Set](templates/eval/template-search-testset.jsonl) - Example evaluation dataset format

## Navigation

**Resources**
- [resources/search-evaluation-guide.md](resources/search-evaluation-guide.md)
- [resources/user-feedback-learning.md](resources/user-feedback-learning.md)
- [resources/distributed-search-slos.md](resources/distributed-search-slos.md)
- [resources/ranking-pipeline-guide.md](resources/ranking-pipeline-guide.md)
- [resources/multilingual-domain-patterns.md](resources/multilingual-domain-patterns.md)
- [resources/vector-search-patterns.md](resources/vector-search-patterns.md)
- [resources/search-debugging.md](resources/search-debugging.md)
- [resources/hybrid-fusion-patterns.md](resources/hybrid-fusion-patterns.md)
- [resources/query-rewriting-patterns.md](resources/query-rewriting-patterns.md)
- [resources/bm25-tuning.md](resources/bm25-tuning.md)

**Templates**
- [templates/ranking/template-ranking-pipeline.md](templates/ranking/template-ranking-pipeline.md)
- [templates/ranking/template-reranker.md](templates/ranking/template-reranker.md)
- [templates/search/template-bm25-config.md](templates/search/template-bm25-config.md)
- [templates/search/template-ivf-config.md](templates/search/template-ivf-config.md)
- [templates/search/template-hybrid-config.md](templates/search/template-hybrid-config.md)
- [templates/search/template-hnsw-config.md](templates/search/template-hnsw-config.md)
- [templates/eval/template-search-eval.md](templates/eval/template-search-eval.md)
- [templates/eval/template-search-testset.jsonl](templates/eval/template-search-testset.jsonl)
- [templates/query/template-query-rewrite.md](templates/query/template-query-rewrite.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## External Resources

See [data/sources.json](data/sources.json) for curated web resources:

- **Search engines**: Elasticsearch, OpenSearch, Apache Solr, Typesense, Meilisearch, Lucene
- **Ranking algorithms**: BM25, Learning to Rank, RankNet
- **Hybrid search**: Qdrant, Weaviate, Pinecone sparse-dense implementations
- **Query understanding**: Query expansion, synonyms, query rewriting
- **Relevance tuning**: Boosting, function scoring, decay functions
- **Evaluation metrics**: Precision/Recall, MAP@K, NDCG, MRR
- **Benchmarks**: BEIR, MS MARCO, TREC datasets
- **Python libraries**: Pyserini, Rank-BM25, ir_datasets
- **Official guides**: Elasticsearch and OpenSearch search documentation

---

Use this skill whenever the user needs **search engine quality, indexing, retrieval, or ranking optimization**.
