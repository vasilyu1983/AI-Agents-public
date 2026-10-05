# Retrieval Choice Framework

Use this reference before tuning embeddings or vector indexes.

## Contents

1. Authority source · 2. Retrieval modes · 3. Baseline order · 4. Long-context degradation · 5. Long-context vs RAG cost · 6. Anti-patterns · 7. Verification checklist · 8. Retrieval legs and post-retrieval mode (incl. FTS5 upgrade)

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

**Evidence grade B** — peer-reviewed: SIGIR 2025 (DOI 10.1145/3726302.3731690) + ICLR 2025; related finding: arXiv 2410.05983 (Jin, Yoon, Han, "Long-Context LLMs Meet RAG", 2024-10-08).

Note: arXiv 2501.01880 (Li, Cao, Ma, "Long Context vs. RAG for LLMs: An Evaluation and Revisits", 2024-12-27) is a separate long-context-vs-RAG comparison, not a replication of this hard-negatives finding — it generally finds long-context outperforming RAG and cuts against, rather than for, this section's framing. Do not cite it as a replication.

Increasing retrieved top-k improves output quality up to a point, then **degrades it** when hard negatives (plausible but incorrect passages) are included in the context window. The pattern holds across multiple LLMs and retrieval settings.

**Fix:** Filter or rerank retrieved candidates before packing context. Do not assume that retrieving more and stuffing a larger context window is always better.

| Context packing strategy | Quality trajectory as k grows |
|---|---|
| Raw top-k (no filtering) | Rises then degrades when hard negatives appear |
| Hard-negative filtered / reranked first | Remains high or continues to improve |

**Decision rule:** Always rerank before context packing in production. The reranking stage is not optional if you are packing >10 documents.

## 5. Long-Context vs RAG Cost

The cost ratio is not a fixed multiple — it is `(context tokens × input price × cache multiplier) / (RAG context tokens × input price)`, which collapses to `context tokens / RAG tokens × cache multiplier`. Look up the model's input, cache-read and long-context rates before citing a number (see [ai-api-cost-guide.md#pricing-overview](../../ops-cost-optimization/references/ai-api-cost-guide.md#pricing-overview), which says where the dated rates live and how to re-verify them), and always price the cached-prefix option before assuming an uncached comparison is the relevant one.

**Worked example (labelled assumptions: input price P per MTok, cache-read multiplier m = 0.1, one rate for the whole context length; replace both with the looked-up rates):**

| Approach | Tokens | Input cost per query | Ratio vs 8k RAG |
|---|---|---|---|
| 1M-token context, uncached | 1,000,000 | 1.0 × P | ~125x |
| 1M-token context, cached prefix | 1,000,000 | 0.1 × P | ~12.5x |
| 8k-token RAG context (baseline) | 8,000 | 0.008 × P | 1x |

The ratios do not depend on P. They move with m, and with any long-context surcharge that bills the long prompt at a higher rate than the short one.

A claim of "~1000x" only holds for an uncached comparison against a much smaller (~1k-token) RAG context — it is not the general case, and it ignores prompt caching entirely. For a corpus that is stable and fits in context, price the **cached long-context crossover** first: if the corpus rarely changes and the cache TTL covers the request rate, a cached long-context prefix can beat a RAG pipeline's infrastructure and maintenance cost even though it still costs more per query in raw tokens (~12.5x here) — the crossover depends on request volume, cache hit rate, corpus-change frequency (each change invalidates the cached prefix and forces a full-price re-read), and the RAG pipeline's own fixed costs (index, reranker calls, eval maintenance). Re-run this comparison whenever the corpus changes materially or pricing changes.

Latency figures for either approach are workload- and infra-dependent; do not carry a fixed number here — measure on your own deployment.

**Decision rule:** Do not default to long-context stuffing as a substitute for retrieval design when the corpus exceeds what fits cheaply, and do not default to RAG when the corpus is small, stable, and cache-friendly — compute the crossover, don't assume either direction.

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

## 8. Retrieval Legs And Post-Retrieval Mode

Route each query to the leg that owns it; fuse only legs that apply.

| Leg | Owns | Note |
|---|---|---|
| Semantic (dense) | Paraphrase, cross-language, vague intent | Weak on identifiers |
| Lexical (BM25 + exact match) | Document IDs, clause numbers, ticket IDs, product codes | An identifier must hit by exact string match; never rely on the dense leg for it |
| Relational (graph) | "What depends on / implements / is owned by X" | Count only evidence-backed edges; keep candidate edges out of answers |
| Structured (registry / SQL) | Metadata questions: current version, owner, approver, in force | Answer from the registry, then attach supporting text as evidence |

Post-retrieval is a decision, not a default:

| Mode | Use when | Risk |
|---|---|---|
| Return evidence (dedup + rerank) | Consumer is an agent or human who can reason; regulated or audited corpus | Interpretation is left to the consumer |
| Compute a result (aggregates, temporal predicates, as-of joins) | Question is a count, join or point-in-time state | Needs typed fields; fails on prose-only corpora |
| Synthesise (LLM, iterative retrieval) | Consumer needs one answer and cannot read evidence | Detail loss and new errors |

Default for compliance and regulated corpora: return cited evidence, let the calling agent synthesise, and run a citation-support check. Deviate to synthesis only with that check gating the output.

### Upgrading a lexical-only FTS5/BM25 KB

1. Freeze a golden set with paraphrase and multilingual slices, plus an identifier slice. Record the baseline per slice.
2. Add a dense leg, fuse with RRF ([hybrid-fusion-patterns.md](hybrid-fusion-patterns.md)), then add a cross-encoder rerank over the fused top-N.
3. Keep the lexical leg: identifier queries must not regress. Gate on the identifier slice, not the average.
4. Re-measure the same slices after each added stage. Keep a stage only if its target slice improves and no other slice drops. Numbers: not yet measured for any specific corpus; measure yours.
5. Apply scope and clearance filters at candidate generation in every leg, including the new dense index.
