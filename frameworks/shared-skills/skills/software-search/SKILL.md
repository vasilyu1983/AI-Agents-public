---
name: software-search
description: "Designs application search systems. Use when choosing engines, indexing, relevance tuning, facets, autocomplete, or search analytics."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-08-24
---

# Search Engineering

Build search features that return the right results, fast.

## Quick Reference

| Need | Recommended Options |
|---|---|
| Full-text search (managed) | Algolia (fastest DX), Elasticsearch/OpenSearch (most flexible) |
| Full-text search (lightweight) | Typesense (simple), Meilisearch (developer-friendly) |
| Full-text search (embedded) | SQLite FTS5, Tantivy (Rust), Lunr.js (client-side) |
| PostgreSQL built-in | pg_trgm + tsvector/tsquery (good enough for many apps) |
| Vector search | pgvector, Pinecone, Weaviate, Qdrant |
| Hybrid search | Keyword + vector, reciprocal rank fusion |
| Autocomplete | Prefix matching, search-as-you-type index, debounced queries |
| Faceted search | Aggregation queries, filter counts, hierarchical facets |
| Search analytics | Click-through rate, zero-result queries, query refinement patterns |
| Search UI | InstantSearch.js (Algolia), SearchKit, custom |

## When to Use This Skill

- Choosing a search engine or evaluating whether PostgreSQL search is sufficient
- Building full-text search, autocomplete, or faceted filtering
- Designing an indexing pipeline from source data to search index
- Tuning relevance scoring, synonyms, or ranking signals
- Implementing search analytics to measure and improve quality
- Debugging search quality issues (missing results, poor ranking, slow queries)

## When NOT to Use This Skill

- **RAG and retrieval for LLM context augmentation** → [ai-rag](../ai-rag/SKILL.md)
- **Database query optimization (SQL performance)** → [data-sql-optimization](../data-sql-optimization/SKILL.md)
- **Marketing SEO and search visibility** → `marketing-seo`
- **Product analytics and event tracking** → `marketing-product-analytics`
- **Backend API design and architecture** → [software-backend](../software-backend/SKILL.md)

## Workflow

1. Define the corpus, query intents, filters, freshness target, latency budget, and display fields.
2. Confirm that this is product search; route RAG, database tuning, SEO, generic product-analytics or event-tracking work, or API-architecture work to the adjacent skill.
3. Choose PostgreSQL, a dedicated engine, vector, or hybrid retrieval with the decision tree.
4. Load only the focused reference needed for the chosen path from the navigation map.
5. Add instrumentation and a judged-query evaluation before changing ranking, analyzers, synonyms, or business boosts.
6. Verify current engine capabilities and hosted-service behavior from primary sources, then return tradeoffs, assumptions, and a rollout or rollback plan.

## ASCII Flow

```text
Search task
  -> Define corpus, query intent, filters, and freshness needs
  -> Choose database search, dedicated engine, vector, or hybrid retrieval
  -> Design indexing, schema, ranking, synonyms, and hydration strategy
  -> Add relevance evals, analytics, and regression checks
  -> Verify engine-specific behavior and limits
  -> Report quality tradeoffs and rollout plan
```

## Decision Tree

```text
Which search engine?
├── Small dataset (<100K docs), PostgreSQL already in stack?
│   └── YES → PostgreSQL full-text search (pg_trgm + tsvector)
│       └── Outgrowing it? (facets, typo tolerance, sub-50ms at scale)
│           └── YES → Move to dedicated search engine (below)
├── Need instant search-as-you-type with zero ops?
│   └── YES → Algolia (managed, fastest DX)
├── Need full control, complex queries, large scale?
│   └── YES → Elasticsearch or OpenSearch
├── Developer-friendly, simpler than Elastic?
│   └── YES → Typesense or Meilisearch
├── Client-side search (static site, small dataset)?
│   └── YES → Lunr.js, Pagefind, or FlexSearch
├── Need semantic/meaning-based search?
│   └── YES → Vector search (pgvector, Pinecone, Qdrant, Weaviate)
└── Need both keyword AND semantic?
    └── YES → Hybrid search (keyword + vector + reciprocal rank fusion)
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

- **`LIKE '%query%'` at scale** — full table scan, no index usage, gets slower linearly with data growth. Use proper full-text search instead.
- **No analyzers configured** — raw text matching misses stemming, case folding, and accent normalization. Users searching "running" won't find "run."
- **Ignoring zero-result queries** — the cheapest way to improve search quality, and most teams never look at them.
- **Re-indexing full dataset on every change** — use incremental updates (upsert by document ID) for individual changes and reserve full reindex for schema changes.
- **Coupling search schema to database schema** — search documents should be denormalized and optimized for query patterns, not mirror your relational schema.
- **Not measuring search quality** — if you don't track click-through rate, zero-result rate, and query refinement rate, you cannot improve search. Instrument from day one.
- **Over-engineering early** — starting with Elasticsearch when PostgreSQL `tsvector` would handle the workload for the next two years.

## Known Traps

- Semantic or vector retrieval added as a replacement for lexical recall instead of a complement to it.
- Faceting on fields with unbounded cardinality, leading to expensive aggregations and unusable filter UX.
- Synonym expansion shipped without governance, creating silent relevance regressions and impossible-to-debug ranking changes.
- Index freshness assumed to be real-time when ingestion pipelines are actually batched or eventually consistent.

## Verification Gate

Before calling a search design or implementation ready:

- [ ] Engine matches current corpus size, query shape, and latency budget
- [ ] Latency budgets defined separately for full search (≤200ms p95) and autocomplete (≤100ms p95)
- [ ] Index freshness mechanism documented and measured (real-time, near-real-time, or scheduled batch)
- [ ] Zero-result rate instrumented and baseline established (target below 5% for mature catalog)
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

### Related Skills

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- [ai-rag](../ai-rag/SKILL.md) — Retrieval-augmented generation and vector retrieval for LLM context
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — Database query performance and indexing
- [software-backend](../software-backend/SKILL.md) — Backend API design and service architecture
- [software-frontend](../software-frontend/SKILL.md) — Frontend implementation including search UI components
- [software-architecture-design](../software-architecture-design/SKILL.md) — System design and component boundaries
- [foundations-information-theory](../foundations-information-theory/SKILL.md) — Entropy, mutual information, and KL divergence are the math behind BM25, TF-IDF, and the relevance-tuning section

## Freshness Protocol

Search engines, managed services, and client libraries evolve frequently. Verify current information before recommending specific versions or providers.

### Trigger Conditions

- "Which search engine should I use?"
- "Is Algolia/Typesense/Meilisearch still the best option for...?"
- "What's new in Elasticsearch/OpenSearch?"
- "Should I use PostgreSQL search or a dedicated engine?"
- "How does pgvector compare to Pinecone/Weaviate?"

### How to Freshness-Check

1. Start from [data/sources.json](data/sources.json) for official documentation links.
2. Run a targeted web search for the specific engine or library.
3. Prefer official docs and release notes over blog posts for version and feature claims.
4. Prefer official engine docs for rank-evaluation APIs, relevance-debugging tools, and analyzer behavior.

### What to Report

- **Current landscape**: what is stable and widely used now
- **Emerging trends**: what is gaining traction (and why)
- **Deprecated/declining**: what is falling out of favor (and why)
- **Recommendation**: default choice + 1-2 alternatives, with trade-offs

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.

## Learnings Loop

Read relevant entries from learnings.consolidated.md only when continuing prior work, investigating a known pitfall, or debugging. Read raw learnings.md only when the consolidated entry points to it or dated detail is needed.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
