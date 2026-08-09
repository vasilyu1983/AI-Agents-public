# Deferred Extensions

Patterns the v1 skill consciously does not ship, with the trigger that should
make you reach for them. This file exists so the skill is honest about what
it does not yet cover and so users do not assume "not present" means "not
recommended."

## Table of Contents

- [Late Interaction (ColBERT, ColPali)](#late-interaction-colbert-colpali)
- [Query Rewriting (HyDE, Multi-Query, RAG-Fusion)](#query-rewriting-hyde-multi-query-rag-fusion)
- [Industry Eval Harnesses (RAGAS, DeepEval, TruLens)](#industry-eval-harnesses-ragas-deepeval-trulens)
- [Graph-Bounded Retrieval](#graph-bounded-retrieval)
- [Knowledge Graph Hybrid (GraphRAG, LightRAG)](#knowledge-graph-hybrid-graphrag-lightrag)
- [Late Chunking](#late-chunking)
- [Multimodal Retrieval](#multimodal-retrieval)

## Late Interaction (ColBERT, ColPali)

**What it is:** Token-level multi-vector retrieval. Each chunk produces N
vectors (one per token), each query produces M vectors, and matching is a
maxsim sum across token pairs. Captures fine-grained term interactions that
single-vector embedding compresses away.

**Why we deferred:** Storage cost is ~10–50× single-vector. pgvector cannot
store multi-vector tokens natively without app-side workarounds. The HNSW +
contextual + rerank stack covers most of the quality gap at one-tenth the
infra complexity.

**Reach for it when:**
- Recall@5 is stuck below 0.85 even after hybrid + contextual + rerank
- Query terms are highly specific and partial-overlap matters (legal clause
  language, regulatory references, scientific terminology)
- You can run Vespa, Qdrant multi-vector, or a dedicated ColBERT serving
  layer (RAGatouille, PLAID)
- Document corpus is also visual (ColPali for screenshots, slides, PDFs with
  diagrams)

**Anti-pattern to avoid:** "ColBERT = always better." It is better on
specific axes and worse on storage, indexing time, and operational
complexity. Measure on your eval set before adopting.

### MUVERA — multi-vector without the storage/latency penalty

MUVERA (Dhulipala et al., Google, NeurIPS 2024; arXiv 2405.19504) changes the
late-interaction deferral calculus. It collapses ColBERT-style multi-vectors
into a single Fixed Dimensional Encoding (FDE) that approximates MaxSim, so
a standard single-vector HNSW index can serve as the first pass. The Google
blog reports +10% recall / −90% latency vs PLAID on BEIR benchmarks. Qdrant
and Weaviate 1.31 ship MUVERA natively — no separate ColBERT serving layer required.

**Trigger to adopt MUVERA instead of raw ColBERT/PLAID:**
- Recall@5 < 0.85 with hybrid + rerank already deployed
- Team is willing to add Qdrant or Weaviate 1.31 to the stack
- Latency budget rules out PLAID's ~7–8× higher query time

When those conditions are not all met, stay on the v1 hybrid + rerank stack.

*Thank you to arXiv for use of its open access interoperability.*

## Query Rewriting (HyDE, Multi-Query, RAG-Fusion)

**What it is:**
- **HyDE** (Hypothetical Document Embeddings): LLM generates a hypothetical
  answer document; embed and retrieve against it instead of the query.
- **Multi-Query**: LLM rewrites the original query into K paraphrases; run
  retrieval K times; merge results (RRF).
- **RAG-Fusion**: Multi-Query + RRF on retrieval results, often with a
  reranker on the merged set.

**Why we deferred:** Adds 1 LLM call per query (latency + cost), value is
corpus-dependent, and the lift overlaps with hybrid + contextual retrieval.
The v1 baseline already pays for what most users need.

**Reach for it when:**
- Queries are short, ambiguous, or lack vocabulary the corpus uses (common
  in support search where users ask for "X stopped working" but docs say
  "X feature deprecated")
- Hybrid retrieval is already saturated and rerank is running
- Latency budget can absorb +200–500ms

**Reference implementation:** in app code, not in the brain. The brain's
`hybrid_retrieve_context` SQL stays the same; the rewriter sits one layer up
and calls it K times.

**Anti-pattern:** running HyDE and Multi-Query and RAG-Fusion together
without measurement — the latency stack compounds and the recall lift may be
zero on your specific corpus.

## Industry Eval Harnesses (RAGAS, DeepEval, TruLens)

**What we ship:** custom per-corpus metric definitions in
`eval-by-corpus-type.md` and a seed builder in `scripts/build_eval_seed.py`
that emits queries with `needs_human_label: True`.

**What we don't ship:** a wired harness that runs RAGAS / DeepEval / TruLens
end-to-end on the seed.

**Reach for them when:**
- You need standard metrics (faithfulness, answer-relevancy, context-recall,
  context-precision) for cross-team comparability or vendor reporting
- You want LLM-as-judge scoring without building your own grader
- You need observability/tracing (TruLens) baked into the eval harness

**Quick orientation:**

| Harness | Strength | Pick when |
|---|---|---|
| **RAGAS** | Most-cited metric library; faithfulness, context_recall, answer_relevancy | Standard reporting, academic comparability |
| **DeepEval** | pytest-style assertions, CI-first | You want eval gates in your test runner |
| **TruLens** | Tracing + feedback functions + dashboard | Observability across dev/staging/prod |
| **Phoenix (Arize)** | Tracing + evals + clustering | Production monitoring at scale |

The seed builder is harness-neutral on purpose — point any of these at the
JSONL output. A future v1.x increment will ship a thin RAGAS adapter in
`scripts/eval_run_ragas.py` once the metric set is stable.

## Graph-Bounded Retrieval

**What it is:** Constrain the candidate pool to a subgraph (e.g. "all
implementations of clause X under authority Y at date Z") *before* hybrid
RRF runs, instead of relying on metadata filters alone.

**Why we deferred:** Compliance brains can simulate it with the
`p_authority` + `p_as_of` filters in `hybrid_retrieve_context`. True
graph-bounded retrieval needs an explicit obligation graph in the schema and
an `ancestors_of`-style recursive CTE per query — worth building only when
that graph already exists as canonical data.

**Reach for it when:**
- The corpus has an explicit authority → policy → procedure → control →
  evidence graph
- You need to answer "what are all things that implement X" cleanly
- A regulator audit asks "show every artifact in scope for clause Y on
  date Z"

See `corpus-playbooks.md` (Compliance section, deferred-extension note) for
the additive parameter shape (`p_clause_graph_root`).

## Knowledge Graph Hybrid (GraphRAG, LightRAG)

**What it is:** Build a knowledge graph over the corpus (entities,
relations, communities). At retrieval time, walk the graph from query
entities to gather context that no chunk-level retrieval would assemble.

**Why we deferred:** Graph construction is itself an LLM-heavy pipeline,
maintenance is non-trivial, and v1's hybrid + contextual stack wins on
the explicit-fact-lookup queries that 80% of corpora actually receive.

**Reach for it when:**
- Queries are *synthesis-heavy* — "summarize how X relates to Y across the
  corpus" rather than "where is X defined"
- Corpus has clear entities and relationships worth materializing
- You can budget for graph build + maintenance separate from chunking

**Reference stacks:** Microsoft GraphRAG (community-summary index), LightRAG
(simpler, faster, dual-level retrieval), Neo4j-based pipelines.

## Late Chunking

**What it is:** Embed long sequences as a single forward pass through a
long-context embedding model, then mean-pool token spans into chunk vectors
*after* the embedding pass. The chunk embedding sees full-document context
even though it represents a chunk.

**Why we deferred:** Requires a long-context embedding model (Jina v3,
nomic-embed-text-v2, Voyage long-context) and changes the embedding pipeline
shape. Contextual Retrieval (which we do ship) achieves a comparable goal
through a different mechanism and is more model-agnostic.

**Reach for it when:**
- Already on a long-context embedder for unrelated reasons
- Cost-sensitive at scale where the per-chunk LLM call of Contextual
  Retrieval is too expensive
- Have empirical evidence on your eval set that late chunking outperforms
  contextual retrieval on this corpus

## Multimodal Retrieval

**What it is:** Embedding text and images (or PDFs/screenshots) into a
shared vector space; retrieving across modalities; passing image regions to
a multimodal generator.

**Why we deferred:** v1 corpus playbooks are text-first (repo, docs hub,
compliance). Multimodal needs different chunkers (page-image splitters,
OCR, layout-aware extractors), different embedders (CLIP, SigLIP, ColPali,
Voyage Multimodal), and different rerankers.

**Reach for it when:**
- Corpus is PDFs with critical content in figures, tables-as-images, or
  diagrams (engineering docs, scientific papers, slide decks)
- Users query visually ("find the diagram of X") or expect figure citations
- Generator is multimodal-capable (Claude Opus 4.7, GPT-5 with vision,
  Gemini 2.x)

**Hosted multimodal embedder now available:** `gemini-embedding-2` (GA March 2026)
maps text, images, video, audio, and PDFs into a single 3,072-dim space with
one API call per document. This reduces the multimodal pipeline complexity — no
separate CLIP/SigLIP serving stack required. For text-only corpora `gemini-embedding-001`
remains the better choice. See `references/embedding-runtime.md` for the
switch criteria. Source: `gemini-embedding-2` entry in `data/sources.json`.

**Anti-pattern:** OCR everything to text and then retrieve as text. Loses
layout signal, table structure, and figure semantics that the multimodal
embedders exist to preserve.

---

If you build any of these and the result is reusable, the increment belongs
in this skill (new reference + manifest fields + script). Open a PR with
eval evidence; do not promote a one-off to a recommended pattern.
