# RAG Quick Start Guide

Companion to [SKILL.md](../SKILL.md). Covers the step-by-step workflow, full template index, and verbose anti-pattern detail that belongs in a reference rather than the top-level skill file.

## Contents

- [Quick Start Workflow](#quick-start-workflow)
- [Template Index](#template-index)
- [Common Anti-Patterns (Detailed)](#common-anti-patterns-detailed)

---

## Quick Start Workflow

1. Use [RAG System Design](../assets/design/rag-system-design.md) to choose the retrieval mode.
2. Pick one ingestion baseline from `assets/chunking/` and one retrieval baseline from `assets/retrieval/`.
3. Define metadata, ACL, and freshness requirements before indexing.
4. Create a small eval set in `assets/eval/` and baseline retrieval metrics before tuning.
5. Add grounding checks and a citation-support pass before shipping.

---

## Template Index

### System Design

- [RAG System Design](../assets/design/rag-system-design.md)

### Chunking & Ingestion

- [Basic Chunking](../assets/chunking/template-basic-chunking.md)
- [Code Chunking](../assets/chunking/template-code-chunking.md)
- [Long Document Chunking](../assets/chunking/template-long-doc-chunking.md)
- [Metadata Schema](../assets/indexing/template-metadata-schema.md)
- [Index Configuration](../assets/indexing/template-index-config.md)

### Retrieval

- [Retrieval Pipeline](../assets/retrieval/template-retrieval-pipeline.md)
- [Hybrid Search](../assets/retrieval/template-hybrid-search.md)
- [Tool-First Retrieval](../assets/retrieval/template-tool-first-retrieval.md)
- [Multivector Retrieval](../assets/retrieval/template-multivector-retrieval.md)
- [Multimodal Document Retrieval](../assets/retrieval/template-multimodal-document-retrieval.md)
- [Graph + Vector Retrieval](../assets/retrieval/template-graph-hybrid-retrieval.md)
- [Reranking](../assets/retrieval/template-reranking.md)
- [Ranking Pipeline](../assets/ranking/template-ranking-pipeline.md)
- [Reranker](../assets/ranking/template-reranker.md)

### Grounding & Evaluation

- [Context Packing](../assets/context/template-context-packing.md)
- [Grounding](../assets/context/template-grounding.md)
- [RAG Evaluation](../assets/eval/template-rag-eval.md)
- [RAG Test Set](../assets/eval/template-rag-testset.jsonl)
- [Search Evaluation](../assets/eval/template-search-eval.md)
- [Search Test Set](../assets/eval/template-search-testset.jsonl)
- [Golden Retrieval Cases](../assets/eval/golden-retrieval-cases.jsonl)
- [Golden Predictions Example](../assets/eval/golden-retrieval-predictions.example.jsonl)
- [Security Red-Team Cases](../assets/eval/security-redteam-cases.jsonl)
- [Backend Comparison Template](../assets/eval/backend-comparison-template.json)
- [Query Rewrite](../assets/query/template-query-rewrite.md)

---

## Common Anti-Patterns (Detailed)

These expand the one-liners in SKILL.md with root-cause context.

**A2 — Vector database first, source-of-truth model later**
Indexing before deciding what constitutes authoritative evidence causes retrieval pipelines to embed the wrong content. Define the authority source and corpus contract (metadata, ACL, freshness, deletion path) before choosing a vector store. See also [ai-context-layer/references/anti-patterns-catalog.md](../../ai-context-layer/references/anti-patterns-catalog.md).

**Agentic retrieval loops for straightforward lookup tasks**
Multi-hop agentic loops add latency and token cost. Evidence for gains is query-distribution-dependent (strongest on multi-hop chemistry; not confirmed on general QA). Baseline with a fixed BM25+dense+rerank pipeline first; add the loop only where eval shows a failure mode that justifies it.

**No freshness or invalidation model for mutable corpora**
Indexed documents without deletion propagation or staleness budgets silently serve outdated content. Set staleness budget, invalidation triggers, and a deletion path before indexing anything that changes.

**A13 — Citation formatting without evidence-ID verification**
Emitting inline citations from chunk text without checking that the evidence ID exists and maps to a real source chunk causes fabricated references. Enforce an evidence contract: stable IDs, source metadata, and a citation-support check before generation.

**A10 — Cross-tenant or cross-sensitivity indexing with retrieval-time filtering bolted on later**
Mixing corpora at index time and filtering at query time is fragile. Residency and isolation decisions must be made before the first index write, not patched post-hoc.

**A15 — RAG re-run per turn instead of compiled knowledge**
When the same queries keep re-running the retrieve-chunk-embed loop with no accumulating artifact, the system is burning tokens and latency to answer the same question repeatedly. Fix: switch to knowledge compilation (P7 pattern in [ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md](../../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md)) when the consumer needs a reviewable or reusable asset.

**Pre-2026 chunk-size or token-budget heuristics with Opus 4.7**
The Opus 4.7 tokenizer encodes ~1.0–1.35× more tokens for the same text than pre-2026 tokenizers. Old chunk-size tables are invalid. Re-measure on your own corpus with the current tokenizer.

**Reindexing synthesized reports or summaries as authoritative primary evidence**
Derived content (summaries, research reports) fed back into the primary index without a `derived` tag contaminates provenance. Tag all derived chunks explicitly and weight them below primary evidence in ranking.

**Treating retrieval recall problems and answer-faithfulness problems as one metric**
Retrieval relevance and answer faithfulness are separate failure modes requiring separate eval planes. A high-recall retriever with a hallucinating generator fails at faithfulness; a faithful generator fed low-recall chunks fails at retrieval. Measure both independently.
