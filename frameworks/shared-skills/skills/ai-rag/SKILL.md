---
name: ai-rag
description: Complete RAG and search engineering skill. Covers chunking strategies, hybrid retrieval (BM25 + vector), cross-encoder reranking, query rewriting, ranking pipelines, nDCG/MRR evaluation, and production search systems. Modern patterns for retrieval-augmented generation and semantic search.
---

# RAG & Search Engineering — Complete Reference

Build production-grade retrieval systems with **hybrid search**, **grounded generation**, and **measurable quality**.

This skill covers:

- **RAG**: Chunking, contextual retrieval, grounding, adaptive/self-correcting systems
- **Search**: BM25, vector search, hybrid fusion, ranking pipelines
- **Evaluation**: recall@k, nDCG, MRR, groundedness metrics

**Modern Best Practices (Jan 2026)**:

- Separate **retrieval quality** from **answer quality**; evaluate both (RAG: https://arxiv.org/abs/2005.11401).
- Default to **hybrid retrieval** (sparse + dense) with **reranking** when precision matters (DPR: https://arxiv.org/abs/2004.04906).
- Use a failure taxonomy to debug systematically (Seven Failure Points in RAG: https://arxiv.org/abs/2401.05856).
- Treat **freshness/invalidation** as first-class; staleness is a correctness bug, not a UX issue.
- Add **grounding gates**: answerability checks, citation coverage checks, and refusal-on-missing-context defaults.
- Threat-model RAG: retrieved text is untrusted input (OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/).

**Default posture**: deterministic pipeline, bounded context, explicit failure handling, and telemetry for every stage.

**Scope note**: For prompt structure and output contracts used in the generation phase, see [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md).

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Decide RAG vs alternatives | Decision framework | RAG if: freshness + citations + corpus size; else: fine-tune/caching | Avoid unnecessary retrieval latency/complexity |
| Chunking & parsing | Chunker + parser | Start simple; add structure-aware chunking per doc type | Ingestion for docs, code, tables, PDFs |
| Retrieval | Sparse + dense (hybrid) | Fusion (e.g., RRF) + metadata filters + top-k tuning | Mixed query styles; high recall requirements |
| Precision boost | Reranker | Cross-encoder/LLM rerank of top-k candidates | When top-k contains near-misses/noise |
| Grounding | Output contract + citations | Quote/ID citations; answerability gate; refuse on missing evidence | Compliance, trust, and auditability |
| Evaluation | Offline + online eval | Retrieval metrics + answer metrics + regression tests | Prevent silent regressions and staleness failures |

## Decision Tree: RAG Architecture Selection

```text
Building RAG system: [Architecture Path]
    ├─ Document type?
    │   ├─ Page/section-structured? → Structure-aware chunking (pages/sections + metadata)
    │   ├─ Technical docs/code? → Structure-aware + code-aware chunking (symbols, headers)
    │   └─ Simple content? → Fixed-size token chunking with overlap (baseline)
    │
    ├─ Retrieval accuracy low?
    │   ├─ Query ambiguity? → Query rewriting + multi-query expansion + filters
    │   ├─ Noisy results? → Add reranker + better metadata filters
    │   └─ Mixed queries? → Hybrid retrieval (sparse + dense) + reranking
    │
    ├─ Dataset size?
    │   ├─ <100k chunks? → Flat index (exact search)
    │   ├─ 100k-10M? → HNSW (low latency)
    │   └─ >10M? → IVF/ScaNN/DiskANN (scalable)
    │
    └─ Production quality?
        └─ Add: ACLs, freshness/invalidation, eval gates, and telemetry (end-to-end)
```

## Core Concepts (Vendor-Agnostic)

- **Pipeline stages**: ingest → chunk → embed → index → retrieve → rerank → pack context → generate → verify.
- **Two evaluation planes**: retrieval relevance (did we fetch the right evidence?) vs generation fidelity (did we use it correctly?).
- **Freshness model**: staleness budget, invalidation triggers, and rebuild strategy (incremental vs full).
- **Trust boundaries**: retrieved content is untrusted; apply the same rigor as user input (OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## Implementation Practices (Tooling Examples)

- Use a **retrieval API contract**: query, filters, top_k, trace_id, and returned evidence IDs.
- Instrument each stage with tracing/metrics (OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- Add **caches** deliberately: embeddings cache, retrieval cache (query+filters), and response cache (with invalidation).

## Do / Avoid

**Do**
- Do keep retrieval deterministic: fixed top_k, stable ranking, explicit filters.
- Do enforce document-level ACLs at retrieval time (not only at generation time).
- Do include citations with stable IDs and verify citation coverage in tests.

**Avoid**
- Avoid shipping RAG without a test set and regression gate.
- Avoid "stuff everything" context packing; it increases cost and can reduce accuracy.
- Avoid mixing corpora without metadata and tenant isolation.

## When to Use This Skill

Use this skill when the user asks:

- "Help me design a RAG pipeline."
- "How should I chunk this document?"
- "Optimize retrieval for my use case."
- "My RAG system is hallucinating — fix it."
- "Choose the right vector database / index type."
- "Create a RAG evaluation framework."
- "Debug why retrieval gives irrelevant results."

## Tool/Model Recommendation Protocol

When users ask for vendor/model/framework recommendations, validate claims against current primary sources.

### Triggers

- "What's the best vector database for [use case]?"
- "What should I use for [chunking/embedding/reranking]?"
- "What's the latest in RAG development?"
- "Current best practices for [retrieval/grounding/evaluation]?"
- "Is [Pinecone/Qdrant/Chroma] still relevant in 2026?"
- "[Vector DB A] vs [Vector DB B]?"
- "Best embedding model for [use case]?"
- "What RAG framework should I use?"

### Required Checks

1. Read `data/sources.json` and start from sources with `"add_as_web_search": true`.
2. Verify 1-2 primary docs per recommendation (release notes, benchmarks, docs).
3. If browsing isn't available, state assumptions and give a verification checklist.

### What to Report

After checking, provide:

- **Current landscape**: What vector DBs/embeddings are popular NOW (not 6 months ago)
- **Emerging trends**: Techniques gaining traction (late interaction, agentic RAG, graph RAG)
- **Deprecated/declining**: Approaches or tools losing relevance
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with current sources)

- Vector databases (Pinecone, Qdrant, Weaviate, Milvus, pgvector, LanceDB)
- Embedding models (OpenAI, Cohere, Voyage AI, Jina, Sentence Transformers)
- Reranking (Cohere Rerank, Jina Reranker, FlashRank, RankGPT)
- RAG frameworks (LlamaIndex, LangChain, Haystack, txtai)
- Advanced RAG (contextual retrieval, agentic RAG, graph RAG, CRAG)
- Evaluation (RAGAS, TruLens, DeepEval, BEIR)

## Related Skills

For adjacent topics, reference these skills:

- **[ai-llm](../ai-llm/SKILL.md)** - Prompting, fine-tuning, instruction datasets
- **[ai-agents](../ai-agents/SKILL.md)** - Agentic RAG workflows and tool routing
- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Serving performance, quantization, batching
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment, monitoring, security, privacy, and governance
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Prompt patterns for RAG generation phase

## Templates

### System Design (Start Here)

- [RAG System Design](assets/design/rag-system-design.md)

### Chunking & Ingestion

- [Basic Chunking](assets/chunking/template-basic-chunking.md)
- [Code Chunking](assets/chunking/template-code-chunking.md)
- [Long Document Chunking](assets/chunking/template-long-doc-chunking.md)

### Embedding & Indexing

- [Index Configuration](assets/indexing/template-index-config.md)
- [Metadata Schema](assets/indexing/template-metadata-schema.md)

### Retrieval & Reranking

- [Retrieval Pipeline](assets/retrieval/template-retrieval-pipeline.md)
- [Hybrid Search](assets/retrieval/template-hybrid-search.md)
- [Reranking](assets/retrieval/template-reranking.md)
- [Ranking Pipeline](assets/ranking/template-ranking-pipeline.md)
- [Reranker](assets/ranking/template-reranker.md)

### Context Packaging & Grounding

- [Context Packing](assets/context/template-context-packing.md)
- [Grounding](assets/context/template-grounding.md)

### Evaluation

- [RAG Evaluation](assets/eval/template-rag-eval.md)
- [RAG Test Set](assets/eval/template-rag-testset.jsonl)
- [Search Evaluation](assets/eval/template-search-eval.md)
- [Search Test Set](assets/eval/template-search-testset.jsonl)

### Search Configuration

- [BM25 Configuration](assets/search/template-bm25-config.md)
- [HNSW Configuration](assets/search/template-hnsw-config.md)
- [IVF Configuration](assets/search/template-ivf-config.md)
- [Hybrid Configuration](assets/search/template-hybrid-config.md)

### Query Rewriting

- [Query Rewrite](assets/query/template-query-rewrite.md)

## Navigation

**Resources**

- [references/advanced-rag-patterns.md](references/advanced-rag-patterns.md)
- [references/agentic-rag-patterns.md](references/agentic-rag-patterns.md)
- [references/bm25-tuning.md](references/bm25-tuning.md)
- [references/chunking-patterns.md](references/chunking-patterns.md)
- [references/chunking-strategies.md](references/chunking-strategies.md)
- [references/rag-evaluation-guide.md](references/rag-evaluation-guide.md)
- [references/rag-troubleshooting.md](references/rag-troubleshooting.md)
- [references/contextual-retrieval-guide.md](references/contextual-retrieval-guide.md)
- [references/distributed-search-slos.md](references/distributed-search-slos.md)
- [references/grounding-checklists.md](references/grounding-checklists.md)
- [references/hybrid-fusion-patterns.md](references/hybrid-fusion-patterns.md)
- [references/index-selection-guide.md](references/index-selection-guide.md)
- [references/multilingual-domain-patterns.md](references/multilingual-domain-patterns.md)
- [references/pipeline-architecture.md](references/pipeline-architecture.md)
- [references/query-rewriting-patterns.md](references/query-rewriting-patterns.md)
- [references/ranking-pipeline-guide.md](references/ranking-pipeline-guide.md)
- [references/retrieval-patterns.md](references/retrieval-patterns.md)
- [references/search-debugging.md](references/search-debugging.md)
- [references/search-evaluation-guide.md](references/search-evaluation-guide.md)
- [references/user-feedback-learning.md](references/user-feedback-learning.md)
- [references/vector-search-patterns.md](references/vector-search-patterns.md)

**Templates**
- [assets/context/template-context-packing.md](assets/context/template-context-packing.md)
- [assets/context/template-grounding.md](assets/context/template-grounding.md)
- [assets/design/rag-system-design.md](assets/design/rag-system-design.md)
- [assets/chunking/template-basic-chunking.md](assets/chunking/template-basic-chunking.md)
- [assets/chunking/template-code-chunking.md](assets/chunking/template-code-chunking.md)
- [assets/chunking/template-long-doc-chunking.md](assets/chunking/template-long-doc-chunking.md)
- [assets/retrieval/template-retrieval-pipeline.md](assets/retrieval/template-retrieval-pipeline.md)
- [assets/retrieval/template-hybrid-search.md](assets/retrieval/template-hybrid-search.md)
- [assets/retrieval/template-reranking.md](assets/retrieval/template-reranking.md)
- [assets/eval/template-rag-eval.md](assets/eval/template-rag-eval.md)
- [assets/eval/template-rag-testset.jsonl](assets/eval/template-rag-testset.jsonl)
- [assets/eval/template-search-eval.md](assets/eval/template-search-eval.md)
- [assets/eval/template-search-testset.jsonl](assets/eval/template-search-testset.jsonl)
- [assets/indexing/template-index-config.md](assets/indexing/template-index-config.md)
- [assets/indexing/template-metadata-schema.md](assets/indexing/template-metadata-schema.md)
- [assets/query/template-query-rewrite.md](assets/query/template-query-rewrite.md)
- [assets/ranking/template-ranking-pipeline.md](assets/ranking/template-ranking-pipeline.md)
- [assets/ranking/template-reranker.md](assets/ranking/template-reranker.md)
- [assets/search/template-bm25-config.md](assets/search/template-bm25-config.md)
- [assets/search/template-hnsw-config.md](assets/search/template-hnsw-config.md)
- [assets/search/template-ivf-config.md](assets/search/template-ivf-config.md)
- [assets/search/template-hybrid-config.md](assets/search/template-hybrid-config.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

Use this skill whenever the user needs **retrieval-augmented system design or debugging**, not prompt work or deployment.
