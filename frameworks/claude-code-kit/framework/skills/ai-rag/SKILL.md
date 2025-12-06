---
name: ai-rag
description: Complete RAG and search engineering skill. Covers chunking strategies, hybrid retrieval (BM25 + vector), cross-encoder reranking, query rewriting, ranking pipelines, nDCG/MRR evaluation, and production search systems. Modern patterns for retrieval-augmented generation and semantic search.
---

# RAG & Search Engineering — Complete Reference

Build production-grade retrieval systems with **modern hybrid search patterns**.

This skill covers:

- **RAG**: Chunking, contextual retrieval, grounding, adaptive/self-correcting systems
- **Search**: BM25, vector search, hybrid fusion, ranking pipelines
- **Evaluation**: recall@k, nDCG, MRR, groundedness metrics

- **Chunking strategies:** Page-level chunking (0.648 accuracy, highest in NVIDIA benchmarks)
- **Contextual Retrieval:** Anthropic's 2024 technique (67% accuracy improvement with prompt caching)
- **Hybrid retrieval:** Lexical (BM25) + vector + cross-encoder reranking
- **Reranking:** Cross-encoder (ms-marco-TinyBERT-L-2-v2, 4.3M params, outperforms larger models)
- **RAG evaluation:** Recall@K, Precision@K, nDCG, groundedness, verbosity, instruction following
- **Modern paradigm shift:** Adaptive, multimodal, self-correcting systems (static RAG is over)

**Key Insights:**

- **Page-level chunking** achieved highest accuracy (0.648) with lowest variance
- **Contextual Retrieval** reduces retrieval failures by 67% when combined with reranking
- **Semantic chunking** improves recall by up to 9% over simpler methods
- **Hybrid retrieval + reranking** drastically improves accuracy
- **Era of static RAG is over** - adaptive, wise retrieval is mainstream

It focuses on **doing**, not explaining theory.

**Scope note:** Retrieval algorithm tuning (BM25/HNSW/hybrid, query rewriting) lives in [ai-rag](../ai-rag/SKILL.md); this skill covers RAG-specific packaging, context injection, and grounded generation.

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Chunking | Page-level, Semantic | RecursiveCharacterTextSplitter (400-512) | 0.648 accuracy, 85-90% recall |
| Contextual Retrieval | Anthropic Claude | Generate chunk context + prompt caching | 67% failure reduction, $1.02/M tokens |
| Hybrid Retrieval | BM25 + Vector | LlamaIndex, LangChain, Haystack | Significant relevance benefits (modern standard) |
| Reranking | Cross-encoder | ms-marco-TinyBERT-L-2-v2 (4.3M params) | Drastically improves accuracy, <100ms |
| Vector Index | HNSW, IVF | FAISS, Pinecone, Qdrant, Weaviate | <10M: HNSW, >10M: IVF/ScaNN |
| Evaluation | RAGAS, TruLens | Recall@K, nDCG, groundedness metrics | Quality validation, A/B testing |

---

## Decision Tree: RAG Architecture Selection

```text
Building RAG system: [Architecture Path]
    ├─ Document type?
    │   ├─ Page-structured? → Page-level chunking (0.648 accuracy, lowest variance)
    │   ├─ Technical docs? → Semantic chunking (9% recall improvement)
    │   └─ Simple content? → RecursiveCharacterTextSplitter (400-512, 85-90% recall)
    │
    ├─ Retrieval accuracy low?
    │   ├─ Multi-entity docs? → Contextual Retrieval (67% failure reduction)
    │   ├─ Noisy results? → Cross-encoder reranking (TinyBERT, <100ms)
    │   └─ Mixed queries? → Hybrid retrieval (BM25 + vector + reranking)
    │
    ├─ Dataset size?
    │   ├─ <100k chunks? → Flat index (exact search)
    │   ├─ 100k-10M? → HNSW (low latency)
    │   └─ >10M? → IVF/ScaNN/DiskANN (scalable)
    │
    └─ Production quality?
        └─ Full pipeline: Page-level + Contextual + Hybrid + Reranking → Optimal accuracy
```

---

## When to Use This Skill

Claude should invoke this skill when the user asks:

- "Help me design a RAG pipeline."
- "How should I chunk this document?"
- "Optimize retrieval for my use case."
- "My RAG system is hallucinating — fix it."
- "Choose the right vector database / index type."
- "Create a RAG evaluation framework."
- "Debug why retrieval gives irrelevant results."

---

## Related Skills

For adjacent topics, reference these skills:

- **[ai-llm](../ai-llm/SKILL.md)** - Prompting, fine-tuning, instruction datasets
- **[ai-llm](../ai-llm/SKILL.md)** - Agentic workflows, multi-agent systems, LLM orchestration
- **[ai-rag](../ai-rag/SKILL.md)** - BM25, hybrid search, ranking pipelines (complements RAG retrieval)
- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Serving performance, quantization, batching
- **[ai-mlops](../ai-mlops/SKILL.md)** - Security, privacy, PII handling
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment, monitoring, data pipelines
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Prompt patterns for RAG generation phase

---

## Detailed Guides

### Core RAG Architecture

- **[Pipeline Architecture](resources/pipeline-architecture.md)** - End-to-end RAG pipeline structure, ingestion, freshness, index hygiene, embedding selection
- **[Chunking Strategies](resources/chunking-strategies.md)** - Modern benchmarks (page-level 0.648 accuracy, semantic, RecursiveCharacterTextSplitter 400-512)
- **[Index Selection Guide](resources/index-selection-guide.md)** - Vector database configuration, HNSW/IVF/Flat selection, parameter tuning

### Advanced Retrieval Techniques

- **[Retrieval Patterns](resources/retrieval-patterns.md)** - Dense retrieval, hybrid search, query preprocessing, reranking workflow, metadata filtering
- **[Contextual Retrieval Guide](resources/contextual-retrieval-guide.md)** - Anthropic's 2024 technique (67% failure reduction), prompt caching, implementation
- **[Grounding Checklists](resources/grounding-checklists.md)** - Context compression, hallucination control, citation patterns, answerability validation

### Production & Evaluation

- **[RAG Evaluation Guide](resources/rag-evaluation-guide.md)** - Recall@K, nDCG, groundedness, RAGAS/TruLens, A/B testing, sliced evaluation
- **[Advanced RAG Patterns](resources/advanced-rag-patterns.md)** - Graph/multimodal RAG, online evaluation, telemetry, shadow/canary testing, adaptive retrieval
- **[RAG Troubleshooting](resources/rag-troubleshooting.md)** - Failure mode triage, debugging irrelevant results, hallucination fixes

### Existing Detailed Patterns

- **[Chunking Patterns](resources/chunking-patterns.md)** - Technical implementation details for all chunking approaches
- **[Retrieval Patterns](resources/retrieval-patterns.md)** - Low-level retrieval implementation patterns

---

## Templates

### Chunking & Ingestion

- [Basic Chunking](templates/chunking/template-basic-chunking.md)
- [Code Chunking](templates/chunking/template-code-chunking.md)
- [Long Document Chunking](templates/chunking/template-long-doc-chunking.md)

### Embedding & Indexing

- [Index Configuration](templates/indexing/template-index-config.md)
- [Metadata Schema](templates/indexing/template-metadata-schema.md)

### Retrieval & Reranking

- [Retrieval Pipeline](templates/retrieval/template-retrieval-pipeline.md)
- [Hybrid Search](templates/retrieval/template-hybrid-search.md)
- [Reranking](templates/retrieval/template-reranking.md)

### Context Packaging & Grounding

- [Context Packing](templates/context/template-context-packing.md)
- [Grounding](templates/context/template-grounding.md)

### Evaluation

- [RAG Evaluation](templates/eval/template-rag-eval.md)
- [RAG Test Set](templates/eval/template-rag-testset.jsonl)

## Navigation

**Resources**
- [resources/rag-evaluation-guide.md](resources/rag-evaluation-guide.md)
- [resources/rag-troubleshooting.md](resources/rag-troubleshooting.md)
- [resources/contextual-retrieval-guide.md](resources/contextual-retrieval-guide.md)
- [resources/pipeline-architecture.md](resources/pipeline-architecture.md)
- [resources/advanced-rag-patterns.md](resources/advanced-rag-patterns.md)
- [resources/chunking-strategies.md](resources/chunking-strategies.md)
- [resources/grounding-checklists.md](resources/grounding-checklists.md)
- [resources/index-selection-guide.md](resources/index-selection-guide.md)
- [resources/retrieval-patterns.md](resources/retrieval-patterns.md)
- [resources/chunking-patterns.md](resources/chunking-patterns.md)

**Templates**
- [templates/context/template-context-packing.md](templates/context/template-context-packing.md)
- [templates/context/template-grounding.md](templates/context/template-grounding.md)
- [templates/chunking/template-basic-chunking.md](templates/chunking/template-basic-chunking.md)
- [templates/chunking/template-code-chunking.md](templates/chunking/template-code-chunking.md)
- [templates/chunking/template-long-doc-chunking.md](templates/chunking/template-long-doc-chunking.md)
- [templates/retrieval/template-retrieval-pipeline.md](templates/retrieval/template-retrieval-pipeline.md)
- [templates/retrieval/template-hybrid-search.md](templates/retrieval/template-hybrid-search.md)
- [templates/retrieval/template-reranking.md](templates/retrieval/template-reranking.md)
- [templates/eval/template-rag-eval.md](templates/eval/template-rag-eval.md)
- [templates/eval/template-rag-testset.jsonl](templates/eval/template-rag-testset.jsonl)
- [templates/indexing/template-index-config.md](templates/indexing/template-index-config.md)
- [templates/indexing/template-metadata-schema.md](templates/indexing/template-metadata-schema.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## External Resources

See [data/sources.json](data/sources.json) for:

- Embedding models (OpenAI, Cohere, Sentence Transformers, Voyage AI, Jina)
- Vector DBs (FAISS, Pinecone, Qdrant, Weaviate, Milvus, Chroma, pgvector, LanceDB)
- Hybrid search libraries (Elasticsearch, OpenSearch, Typesense, Meilisearch)
- Reranking models (Cohere Rerank, Jina Reranker, RankGPT, Flashrank)
- Evaluation frameworks (RAGAS, TruLens, DeepEval, BEIR)
- RAG frameworks (LlamaIndex, LangChain, Haystack, txtai)
- Advanced techniques (RAG Fusion, CRAG, Self-RAG, Contextual Retrieval)
- Production platforms (Vectara, AWS Kendra)

---

Use this skill whenever the user needs **retrieval-augmented system design or debugging**, not prompt work or deployment.
