<!-- Focused reference for search features and diagnostics. -->

# Search Features and Diagnostics

## Common Misdiagnoses

Symptoms that get the wrong fix more often than the right one:

- **"Search is slow" → jumping straight to a dedicated engine.** Check for a
  missing GIN index, an N+1 hydration query per result, or an unbounded
  `LIKE '%term%'` scan first. Many "we need Elasticsearch" tickets are fixed by
  an index that was never created.
- **"Relevance is bad" → adding vector search.** Verify analyzers, stemming,
  and field boosting are configured correctly before assuming lexical search
  is semantically incapable. A missing stemmer or unboosted title field often
  looks identical to "BM25 can't understand meaning."
- **"Zero-result spike" → assumed content gap.** Check first whether a recent
  synonym, analyzer, or tokenizer change caused a regression. Content gaps and
  indexing regressions produce the same symptom but need opposite fixes.
- **"Hybrid search will fix our recall" → skipping the judged-query set.**
  Hybrid retrieval reduces but does not eliminate poor recall if the underlying
  embedding model was never validated against the domain's vocabulary.
- **"Facets are slow" → blaming the engine instead of cardinality.** Faceting
  on a free-text or unbounded-cardinality field is usually the actual cause,
  not an engine limitation.
- **"Autocomplete is laggy" → tuning the main index.** Autocomplete usually
  needs its own latency budget and often its own lightweight index or cache;
  it should not share load or latency budget with full search.

## Faceted Search and Filtering

**Aggregation queries** — compute filter counts alongside search results. Show users how many results match each filter value before they click. This is where PostgreSQL struggles and dedicated engines shine.

**Hierarchical facets** — nested categories (e.g., Electronics > Phones > Smartphones). Implement with path-based tokens or nested aggregations. Allow drill-down and drill-up navigation.

**Range facets** — numeric or date ranges (price $0-50, $50-100; last 24 hours, last week). Pre-define meaningful ranges or use dynamic bucketing.

**Multi-select vs. single-select** — multi-select filters use OR within a facet and AND across facets. Single-select uses exclusive selection. Multi-select requires disjunctive faceting (count all values, not just those matching current filter).

**Performance** — apply filters before scoring when possible (filter context vs. query context in Elasticsearch). Cache frequently used filter combinations. Pre-compute facet counts for high-traffic pages.

## Autocomplete and Search-as-You-Type

**Prefix matching** — match documents where a field starts with the typed characters. Fast but limited to prefix positions.

**Edge n-gram indexing** — at index time, generate token prefixes ("search" → "s", "se", "sea", "sear", "searc", "search"). Converts prefix queries into exact match lookups, which are faster.

**Completion suggesters** — dedicated data structures optimized for prefix completion. Elasticsearch has a built-in completion suggester. Algolia and Typesense handle this natively.

**Client-side debouncing** — wait 150-300ms after the user stops typing before sending the query. Reduces server load and prevents UI flicker. 200ms is a good default.

**Highlight matching terms** — show users why a result matched by bolding the matching portion. Most search engines provide highlighting out of the box.

**Zero-state and popular suggestions** — before the user types, show trending queries, recent searches, or popular categories. Pre-compute these from search analytics data.

## Search Analytics

**What to track**: every query (with timestamp, user ID, session), every click (which result, position clicked), conversions (did the user complete their goal after clicking), zero-result queries, query refinements (user searched again after seeing results).

**Zero-result queries** — the most actionable metric. These reveal content gaps (you don't have what users want) or search quality issues (you have it but search can't find it). Review weekly and take action: add content, add synonyms, or fix indexing.

**Click position** — which position users click in search results. If users consistently click result #4 instead of #1, your relevance ranking is wrong. Use mean reciprocal rank (MRR) as a quality metric.

**Build the feedback loop**: search query → user clicks result → click signals feed back into relevance tuning (boost documents that get clicked, demote documents that get skipped). This is the core mechanism for search quality improvement over time.

---

Back to [software-search/SKILL.md](../SKILL.md).
