<!-- Focused reference for engine and relevance details. -->

# Engine and Relevance Details

## Contents

- [Engine Capability Matrix](#engine-capability-matrix)
- [PostgreSQL Search](#postgresql-search-start-here)
- [Search Engine Architecture](#search-engine-architecture)
- [Relevance Tuning](#relevance-tuning)
- [Query Classification](#query-classification-without-a-trained-classifier)

## Engine Capability Matrix

| Engine | Typo tolerance | Facets | Geo | Vector | Self-host | Managed |
|--------|---------------|--------|-----|--------|-----------|---------|
| PostgreSQL (tsvector + pg_trgm) | Partial (pg_trgm) | Manual aggregation | PostGIS | pgvector | Yes | RDS/Supabase |
| Algolia | Built-in | Native | Native | Yes — native hybrid (NeuralSearch merges keyword + vector per query) | No | Yes |
| Elasticsearch / OpenSearch | Built-in | Native | Native | Dense vector, native RRF retriever/fusion | Yes | AWS/Elastic |
| Typesense | Built-in | Native | Native | Yes, built-in (rank-fusion hybrid; verify current default fusion weights) | Yes | Typesense Cloud |
| Meilisearch | Built-in | Native | Limited | Yes, built-in hybrid (BM25 + embeddings) since v1.6+ | Yes | Meilisearch Cloud |
| Lunr.js / Pagefind | No | No | No | No | Client-side | N/A |
| Pinecone / Qdrant / Weaviate | N/A (Qdrant/Weaviate: native BM25 sparse-vector support) | Filter | No | Yes | Qdrant/Weaviate yes | Yes |

Capability availability shifts release to release (Algolia added native vector fusion; Qdrant and Weaviate added native BM25). Reverify each engine's `current` docs before finalizing a recommendation — do not rely on this table's exact wording beyond "capability exists in some form."

## PostgreSQL Search (Start Here)

For most applications, PostgreSQL is good enough. Evaluate dedicated engines only when you hit real limits.

**tsvector/tsquery** — full-text search with language-aware stemming, ranking, and phrase matching. Create a `tsvector` column, build a GIN index, query with `tsquery`. Supports `ts_rank` for relevance scoring and `ts_headline` for result highlighting.

**pg_trgm** — trigram-based fuzzy matching. Handles typos and partial matches. Create a GIN index with `gin_trgm_ops`. Use `similarity()` or `word_similarity()` for ranking. Combine with `tsvector` for both exact and fuzzy results.

**GIN indexes** — generalized inverted indexes that make full-text and trigram queries fast. Essential for any non-trivial search workload in PostgreSQL.

**When to outgrow PostgreSQL search:**
- You need faceted search with filter counts (aggregation queries are expensive in PG)
- Sub-50ms latency requirements at scale (>1M docs with complex queries)
- Complex relevance tuning with field boosting, custom scoring, decay functions
- Search-as-you-type with typo tolerance and instant feedback
- You need synonyms, stemming, and language analysis beyond what `tsvector` provides

## Search Engine Architecture

**Indexing pipeline**: Extract data from source (database, CMS, API) → transform into search documents (flatten, denormalize, enrich) → push to search index. Keep the pipeline idempotent — re-running should produce the same index state.

**Index schema design**: Define fields, types, and which fields are searchable vs. filterable vs. stored-only. Denormalize aggressively — search indexes are not relational databases. Include all data needed for display in search results to avoid hydration round-trips.

**Analyzers and tokenizers**: Control how text is broken into searchable tokens. Standard analyzer handles most Western languages. Configure language-specific analyzers for stemming. Add custom analyzers for domain-specific tokenization (email addresses, part numbers, code identifiers).

**Synonyms and stop words**: Maintain a synonym list for domain terms (e.g., "laptop" = "notebook"). Remove low-value stop words from indexing but keep them in phrase queries. Synonym expansion happens at index time or query time — query-time is more flexible, index-time is faster.

**Index lifecycle**: Never mutate a live index schema in production. Use index aliases: build new index → swap alias → delete old index. This gives zero-downtime reindexing. For incremental updates, use upsert operations keyed on document ID.

## Relevance Tuning

**BM25 scoring** — the default ranking algorithm in most search engines. Balances term frequency (how often the term appears in a document) against inverse document frequency (how rare the term is across all documents). Handles document length normalization automatically.

**Field boosting** — weight fields differently. Title matches are typically 3-5x more important than body matches. Boost exact matches over partial matches. Common hierarchy: title > headings > tags > description > body.

**Custom ranking signals** — layer business logic onto relevance scores. Common signals: popularity (views, purchases), recency (newer content ranked higher via decay function), editorial boost (curated/featured content), user behavior (personalized ranking from click history).

**Query understanding** — improve what the user meant, not just what they typed. Spell correction (did-you-mean). Intent detection (navigational vs. informational queries). Query expansion (add related terms). Query relaxation (broaden if too few results).

**Relevance tuning loop** — ship a baseline, measure with analytics, tune iteratively, repeat. Each iteration should move a measurable metric (zero-result rate, MRR, CTR at position 1) not just "feel better."

### Query Classification Without a Trained Classifier

Before reaching for a trained intent classifier or an LLM call, check whether the index
itself can classify the query. If documents already carry a category or classification
field, a semantic-knowledge-graph (SKG) traversal runs a k-nearest-neighbour search
against that field and returns the categories most related to the query — no training
set, no model to serve. Grainger et al. describe this as asking the graph to "find the
category with the highest relatedness to my starting node," where the starting node is
the user's query.

**What it buys you**: classification at index-lookup latency and index-lookup cost,
using the corpus you already have. Because the score is computed per query against
whatever terms the query actually contains, added context shifts the classification
without any retraining — the book's worked example moves `driver` from a travel
reading to a devops reading once `install` is added to the query.

**A second traversal disambiguates.** Traverse query → category → keywords and you get
a contextualised related-terms list per sense, which separates polysemous terms
("server" as restaurant staff vs. as a machine) into distinct meanings. Grainger et al.
warn against the lazy fallback here: given multiple plausible senses, group results by
meaning, pick the most likely one, interleave deliberately, or offer alternative query
suggestions — an intentional choice beats lumping the senses together.

**Where to apply the classification**: as an auto-applied filter, as a relevance boost,
as a route to a context-specific ranking algorithm or landing page, or as input to term
disambiguation.

**Limits and guardrails**:

- The graph is statistical, not curated — relationships exist only because terms
  co-occur in the corpus, so expect noise. Set a minimum-occurrence threshold above 1
  to suppress false positives.
- Efficacy depends on how well user queries overlap the indexed content. If most
  queries are for a vocabulary your corpus barely covers, content-derived
  classification will misread them; user-signal-derived relationships are the
  complement for that case.
- Scores are comparative, not calibrated probabilities. Treat a negative or
  near-zero relatedness score as "this category is not the sense," and prefer the
  known user context over the top score whenever context is available.

**The 2026 alternative**: an LLM call classifies query intent with no category field
and no corpus overlap requirement, and handles queries whose vocabulary the index has
never seen. It costs a model call on the query path. Where the latency budget is tight
(autocomplete, high-QPS product search) or per-query cost matters, the index-side
traversal is the cheaper leg; where budget permits and query vocabulary is open-ended,
an LLM classifier is the more capable one. Measure both against the same judged-query
set before choosing.

---

Back to [software-search/SKILL.md](../SKILL.md).
