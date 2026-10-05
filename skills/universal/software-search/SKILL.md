---
name: software-search
description: "Designs product and site search for end users. Use when choosing search engines, indexing, reindexing, relevance tuning, facets, autocomplete, merchandising, or search analytics."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-08-24
---

# Search Engineering

Build search features that return the right results, fast.

## Quick Reference

| Need | Default | Deviate when |
|---|---|---|
| Full-text search, PostgreSQL already in the stack | `tsvector`/`tsquery` plus `pg_trgm`, both on GIN indexes | Ranking quality is the gap (`ts_rank` is not BM25): add a BM25 extension if the host allows it and its licence fits. Facets with counts, typo tolerance, merchandising, or latency at scale: move to a dedicated engine |
| Dedicated engine | Managed service when no one owns search-cluster operations | Self-host when data residency, cost at volume, or query control requires it and someone owns the cluster |
| Embedded or client-side search | Embedded index (such as SQLite FTS5) or a static client-side index | The corpus or its update rate outgrows a shipped index |
| Semantic search | Vector retrieval as a complement to lexical recall, in the existing database first when it supports vectors | Judged-query evidence shows the in-database option misses the latency or recall target |
| Hybrid search | Keyword + vector, merged with reciprocal rank fusion | Native fusion is missing from the edition or licence tier you will run: fuse in the application |
| Autocomplete | Prefix matching, search-as-you-type index, debounced queries | |
| Faceted search | Aggregation queries, filter counts, hierarchical facets | |
| Search analytics | Click-through rate, zero-result queries, query refinement patterns | |
| Search UI | The chosen engine's client UI library, if it has one | Custom components when the library cannot express the UX |

**Lookup step before naming an engine.** Engine capabilities, licences, and managed-service limits change from release to release, so shortlist by the criteria above, then check each candidate's current documentation and licence. Start from [data/sources.json](data/sources.json); the capability matrix in [references/engine-and-relevance.md](references/engine-and-relevance.md#engine-capability-matrix) is a starting point, not current fact.

## When to Use This Skill

- Choosing a search engine or evaluating whether PostgreSQL search is sufficient
- Building full-text search, autocomplete, or faceted filtering
- Designing an indexing pipeline from source data to search index
- Tuning relevance scoring, synonyms, or ranking signals
- Implementing search analytics to measure and improve quality
- Debugging search quality issues (missing results, poor ranking, slow queries)

## When NOT to Use This Skill

- **RAG and retrieval for LLM context augmentation** → [ai-rag](../ai-rag/SKILL.md). Boundary: this skill owns user-facing product/site search (engine, facets, autocomplete, merchandising, reindex, relevance analytics); ai-rag owns retrieval that feeds an LLM.
- **Database query optimization (SQL performance)** → [data-sql-optimization](../data-sql-optimization/SKILL.md)
- **Marketing SEO and search visibility** → `marketing-seo`
- **Product analytics and event tracking** → `marketing-product-analytics`
- **Backend API design and architecture** → [software-backend](../software-backend/SKILL.md)

## Workflow

1. Define the corpus, query intents, filters, freshness target, latency budget, and display fields.
2. Confirm that this is product search; route RAG, database tuning, SEO, generic product-analytics or event-tracking work, or API-architecture work to the adjacent skill.
3. Choose PostgreSQL, a dedicated engine, vector, or hybrid retrieval with the decision tree.
4. Load the focused reference for the chosen path; design indexing, schema, ranking, synonyms, and result hydration.
5. Add instrumentation and a judged-query evaluation before changing ranking, analyzers, synonyms, or business boosts.
6. Verify current engine capabilities and hosted-service behavior from primary sources, then return tradeoffs, assumptions, and a rollout or rollback plan.

## Decision Tree

```text
Which search engine?
├── PostgreSQL already in the stack, and the workload is inside its limits?
│   (limits: "When to outgrow PostgreSQL search" in references/engine-and-relevance.md)
│   └── YES → PostgreSQL full-text search (tsvector + pg_trgm on GIN indexes)
│       ├── Ranking quality the gap? (ts_rank is not BM25)
│       │   └── YES → BM25 extension, if your host allows it and its licence fits
│       └── Outgrowing it? (facets with counts, typo tolerance, merchandising, latency at scale)
│           └── YES → Dedicated engine (below)
├── Dedicated engine: does anyone own search-cluster operations?
│   └── NO → Managed service. YES → self-hosted engine, if residency, cost, or control needs it
├── Static site or small, rarely changing corpus?
│   └── YES → Client-side index
├── Need semantic/meaning-based search?
│   └── YES → Vector retrieval, as a complement to lexical recall
└── Need both keyword AND semantic?
    └── YES → Hybrid search (keyword + vector + reciprocal rank fusion;
              check the edition or licence tier for native fusion)
Then run the lookup step: verify each shortlisted engine's current capabilities and licence.
```

## Decision and Safety Rules

- Start with the least operationally complex engine that meets the corpus, query, latency, and freshness requirements; verify capability claims at use time.
- Keep indexing idempotent, search documents explicit about searchable, filterable, and stored fields, and live schema changes behind an alias or equivalent rollback path.
- Allowlist filters, validate input before embedding or query construction, rate-limit by authenticated actor where applicable, and treat raw query logging as a data-governance decision.
- Treat vector retrieval as a complement to lexical recall until judged-query evidence shows otherwise; do not hand-pick ranking weights from intuition.
- Keep user consent and tenant or actor isolation explicit before using personalization or behavioral signals.

## Search Quality Evaluation

Analytics are not enough on their own. Keep a judged-query set for the product's most important search intents and re-run it whenever you change ranking, analyzers, synonyms, or business boosts.

**Minimum loop**:

- define representative queries across navigational, informational, autocomplete, and zero-result-recovery paths
- rate a small set of expected results for each query
- run the engine's native rank-evaluation API or an equivalent offline harness
- compare score deltas before and after relevance changes
- review failures manually before shipping boosts or synonym changes

Use click data to find candidates for the judged set, but do not let click-through alone define quality. Position bias, sparse traffic, and merchandising effects can hide bad ranking decisions.

### Ranking Release Gate

Require an offline win on the judged-query set with no unacceptable regression in protected query classes, then canary the candidate against the current ranker. Compare task completion or downstream conversion alongside latency, zero-result rate, abandonment, and reformulation. Log the ranker version with every impression so a bad release can be isolated and rolled back without rebuilding the index.

## Common Anti-Patterns

- **`LIKE '%query%'` at scale** — a leading wildcard cannot use a B-tree index, so the query scans and slows linearly with data growth. A `pg_trgm` GIN index can serve it, but still gives no ranking, stemming, or relevance; use full-text search for search features.
- **No analyzers configured** — raw text matching misses stemming, case folding, and accent normalization. Users searching "running" won't find "run."
- **Ignoring zero-result queries** — the cheapest way to improve search quality, and most teams never look at them.
- **Re-indexing full dataset on every change** — use incremental updates (upsert by document ID) for individual changes and reserve full reindex for schema changes.
- **Coupling search schema to database schema** — search documents should be denormalized and optimized for query patterns, not mirror your relational schema.
- **Not measuring search quality** — if you don't track click-through rate, zero-result rate, and query refinement rate, you cannot improve search. Instrument from day one.

## Known Traps

- Semantic or vector retrieval added as a replacement for lexical recall instead of a complement to it.
- Faceting on fields with unbounded cardinality, leading to expensive aggregations and unusable filter UX.
- Synonym expansion shipped without governance, creating silent relevance regressions and impossible-to-debug ranking changes.
- Index freshness assumed to be real-time when ingestion pipelines are actually batched or eventually consistent.

## Verification Gate

Before calling a search design or implementation ready:

- [ ] Engine matches current corpus size, query shape, and latency budget
- [ ] Latency budgets defined separately for full search and autocomplete, set from the product's own baseline and UX needs (illustrative starting targets, not universal thresholds: ~200ms p95 full search, ~100ms p95 autocomplete)
- [ ] Index freshness mechanism documented and measured (real-time, near-real-time, or scheduled batch)
- [ ] Zero-result rate instrumented and baseline established; set the target from that baseline and the catalog's coverage (an illustrative starting point for a mature catalog is below ~5%, not a universal threshold)
- [ ] Click position and refinement rate tracked from day one
- [ ] Judged-query evaluation covers navigational, informational, autocomplete, and zero-result-recovery paths
- [ ] Representative queries tested — not only happy-path keyword matches
- [ ] Synonym and analyzer changes logged with rollback plan

## Navigation

### Focused References

- [Engine and Relevance Details](references/engine-and-relevance.md) — capability classes, PostgreSQL, indexing architecture, relevance tuning, and query classification.
- [Vector Search API and Sizing](references/vector-search-api-and-sizing.md) — request/response contracts, operational rules, ranking signals, and memory math.
- [Search Features and Diagnostics](references/search-features-and-diagnostics.md) — common misdiagnoses, facets, autocomplete, and search analytics.
- [Hybrid Search and Reranking](references/hybrid-search-and-reranking.md) — BM25 plus dense retrieval, rank fusion, reranking, and engine capability classes.
- [Search Scenarios](references/search-scenarios.md) — worked paths for hybrid search, reindexing, autocomplete, facets, and zero-result recovery.
- [Skill Sources](data/sources.json) — curated primary sources for search engineering guidance.

### Relevance Measurement, Ranking, and Operations (owned here)

- [Search evaluation](references/search-evaluation-guide.md) — graded judgments, nDCG/MRR, significance testing.
- [Click models and bias correction](references/click-models-and-bias-correction.md) — position-bias-corrected labels from click logs.
- [Learning to rank pipeline](references/learning-to-rank-pipeline.md) — LTR features, training, and rollout.
- [User feedback learning](references/user-feedback-learning.md) — signal capture, interleaving, reranker retraining, monitoring.
- [Distributed search SLOs](references/distributed-search-slos.md) — latency, availability, and capacity targets for search clusters.
- [Search debugging](references/search-debugging.md) and [search diagnostics](references/search-features-and-diagnostics.md).
- Fusion method, `k`, and weights: [ai-rag hybrid-fusion-patterns.md](../ai-rag/references/hybrid-fusion-patterns.md); reranker candidate budget: [ai-rag ranking-pipeline-guide.md](../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage).

### Related Skills

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- [ai-rag](../ai-rag/SKILL.md) — Retrieval-augmented generation and vector retrieval for LLM context
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — Database query performance and indexing
- [software-backend](../software-backend/SKILL.md) — Backend API design and service architecture
- [software-frontend](../software-frontend/SKILL.md) — Frontend implementation including search UI components
- [software-architecture-design](../software-architecture-design/SKILL.md) — System design and component boundaries
- [foundations-information-theory](../foundations-information-theory/SKILL.md) — Information-theoretic readings of IDF term weighting and KL-divergence (query-likelihood) scoring; load only when reasoning about term weights from first principles

For engine capabilities, licences, and hosted-service limits, use the lookup step above the workflow.
Record the consulted primary documentation and any unresolved capability in the recommendation.

## Learnings Loop

Read relevant entries from learnings.consolidated.md only when continuing prior work, investigating a known pitfall, or debugging. Read raw learnings.md only when the consolidated entry points to it or dated detail is needed.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
