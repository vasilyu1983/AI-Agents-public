# Retrieval Choice Framework

Use this reference before tuning embeddings or vector indexes.

## 1. Choose The Authority Source First

```text
Where does truth live?
  - Static or slowly changing files -> long-context or hosted file search may be enough
  - Live records behind APIs, SQL, or SaaS -> tool-first or MCP retrieval
  - Entity relationships or aggregations -> SQL or graph retrieval
  - Large prose corpus with fuzzy queries -> hybrid sparse+dense retrieval
  - Visual documents or layout-sensitive data -> multimodal document retrieval
```

## 2. Retrieval Modes And When They Fit

| Mode | Best for | Main tradeoff |
|------|----------|---------------|
| Long-context only | Small corpora, low update rate | Context cost rises fast; weak provenance unless designed carefully |
| Hosted file search | Fast delivery with provider-managed indexing | Less control over ranking internals and storage shape |
| Tool-first / MCP | Live system-of-record data | Requires strong routing and schema normalization |
| SQL / graph retrieval | Counts, joins, relationship questions | Does not replace text evidence for explanations or quotes |
| Hybrid sparse+dense | General-purpose document retrieval | Needs evaluation and metadata discipline |
| Late interaction / multivectors | High precision and subtle matching | Higher latency and operational complexity |
| Multimodal retrieval | PDFs, scans, tables, diagrams | More expensive ingestion and evaluation |

## 3. Baseline Order

1. Try the simplest non-vector option if it satisfies freshness and traceability.
2. If you need document retrieval, start with BM25 + dense + reranker.
3. Add late interaction or multimodal retrieval only when baseline evals show a real gap.
4. Add agentic loops only for ambiguity, multi-hop, or verification-sensitive workflows.

## 4. Long-Context Retrieval Degradation When Hard Negatives Are Present (grade B)

**Evidence grade B** — peer-reviewed: SIGIR 2025 (DOI 10.1145/3726302.3731690) + ICLR 2025; independently replicated: arXiv 2501.01880.

Increasing retrieved top-k improves output quality up to a point, then **degrades it** when hard negatives (plausible but incorrect passages) are included in the context window. The pattern holds across multiple LLMs and retrieval settings.

**Fix:** Filter or rerank retrieved candidates before packing context. Do not assume that retrieving more and stuffing a larger context window is always better.

| Context packing strategy | Quality trajectory as k grows |
|---|---|
| Raw top-k (no filtering) | Rises then degrades when hard negatives appear |
| Hard-negative filtered / reranked first | Remains high or continues to improve |

**Decision rule:** Always rerank before context packing in production. The reranking stage is not optional if you are packing >10 documents.

## 5. Long-Context vs RAG Cost (2026 Production Data)

~1M-token context requests cost roughly three orders of magnitude more per query than a tuned RAG pipeline (2026 production data). Long-context also adds 30-60s latency vs ~1s for a well-tuned RAG path.

**Decision rule:** Do not default to long-context stuffing as a substitute for retrieval design when the corpus exceeds what fits cheaply. Verify current model pricing before finalizing the cost comparison — prices change frequently.

| Approach | Relative cost per query | Typical latency |
|---|---|---|
| ~1M-token context (long-context only) | ~1000x a tuned RAG pipeline | 30-60s |
| Tuned RAG pipeline | Baseline | ~1s |

Source: 2026 production data. Verify against current pricing before citing.

## 6. Anti-Patterns

- Starting with a vector database before defining authority source and evidence contract
- Using document retrieval for problems that are really SQL or API lookup
- Moving to agentic RAG before you have a stable baseline retrieval eval
- Treating rankings, prices, and benchmark leaderboards as durable documentation
- Packing the full top-k into context without reranking — hard negatives degrade output quality at high k

> Thank you to arXiv for use of its open access interoperability.

## 7. Verification Checklist

- [ ] Retrieval mode chosen explicitly
- [ ] Freshness and deletion path defined
- [ ] Citation granularity defined
- [ ] Offline eval set created before tuning
- [ ] Rollback path defined
