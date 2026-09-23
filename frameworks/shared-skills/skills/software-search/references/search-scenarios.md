<!-- Focused reference for search scenarios. -->

# Search Scenarios

## Scenarios

Recipes keyed to common search implementation moments. Each lists the shortest path using patterns above.

### S1 — Hybrid BM25 + vector with RRF for a product catalog

Target design: each product document lives in both a keyword (BM25) index and a vector index (pgvector, Qdrant, or Weaviate); a query runs both in parallel and merges the two ranked lists with Reciprocal Rank Fusion, scoring each document as `Σ 1/(k + rank)` with `k=60` as a safe default. Business boosts (popularity, recency) go on top of the fused score, not inside it.

Evaluation check: tune the relative weight of keyword vs. vector against a judged-query set, and monitor zero-result rate — hybrid rarely returns zero, so the thing to confirm is that semantic recall actually improves tail queries.

### S2 — Zero-downtime reindex via index alias swap

1. Create a new index with the updated schema (e.g., `products_v2`); leave the live alias pointing to `products_v1`.
2. Run the full reindex pipeline against `products_v2`; writes to `products_v1` continue serving production traffic.
3. Verify document count, spot-check relevance on representative queries against `products_v2` before swap.
4. Atomically update the alias: remove `products_v1`, add `products_v2` in a single alias-update call.
5. Confirm production traffic is now routing to `products_v2`; monitor error rate and latency for 10 minutes.
6. Delete `products_v1` only after the monitoring window is clean; keep it for one more deploy cycle if in doubt.

### S3 — Autocomplete debounce + per-user prefix prefetch

Target design: a 200ms client-side debounce before firing, with in-flight requests cancelled on each keystroke. On focus, serve popular empty-string completions from a cached endpoint; after the first two characters, shift to a live prefix query against a completion suggester or edge-ngram index. Return 5–8 suggestions at most — more options slow perceived response and add cognitive load. Log every prefix query with the user session and feed click data back into the popular-completion cache weekly.

Evaluation check: autocomplete holds a strict 100ms server-side latency budget, which usually means its own index or cache layer rather than the main search path.

### S4 — Faceted drill-down with cardinality limits

Target design: facet fields declared explicitly in the index schema, never on free-text or unbounded-cardinality fields. Cap returned values per field (e.g. top 20 by count) with a "show more" call for the long tail. Active facet filters go in filter context, not query context, so they do not perturb relevance scores; multi-select needs disjunctive faceting — recompute counts for each facet excluding its own active filter.

Evaluation check: measure aggregation latency at expected data scale and move expensive facets to a pre-computed cache if it does not hold; monitor facet click patterns and remove facets nobody interacts with.

### S5 — Zero-result rate dashboard + query rewrite trigger

1. Log every search query with its result count; compute the zero-result rate as a daily metric.
2. Build a dashboard showing the top 50 zero-result queries ordered by frequency; review weekly.
3. For each zero-result query, classify: missing content, synonym gap, tokenization mismatch, or indexing bug.
4. Add synonyms or query expansion rules for synonym-gap cases; update the index for indexing bugs.
5. Add a query-rewrite rule (fuzzy match, spell correction, or query relaxation) for tokenization mismatches.
6. Re-evaluate the top-50 list after each change.

---

Back to [software-search/SKILL.md](../SKILL.md).
