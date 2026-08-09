# Wiki-Grounded Retrieval

> Purpose: Read-path pattern for an LLM that grounds answers in a P7 LLM Wiki
> built per `../../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md`.
> The May 2026 default is **entity-page-first, synthesis-second, vector-last**.
> Pure-vector retrieval is the wrong default for a wiki use case.

Pairs with:
- `../../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md` — the write-side page model this pattern reads from
- `../../ai-context-layer/references/multi-source-wiki-ingestion.md` — the ingest pipeline that produces the wiki

---

## Table of Contents

- [When this pattern is the right answer](#when-this-pattern-is-the-right-answer)
- [The routing rule](#the-routing-rule)
- [Named-entity extraction (NER for routing)](#named-entity-extraction-ner-for-routing)
- [Synthesis-page routing](#synthesis-page-routing)
- [Vector fallback (last resort)](#vector-fallback-last-resort)
- [Citation contract](#citation-contract)
- [Missing-entity handling](#missing-entity-handling)
- [Supersede-aware reads](#supersede-aware-reads)
- [Composition with existing RAG patterns](#composition-with-existing-rag-patterns)
- [Eval-set shape](#eval-set-shape)
- [Anti-pattern catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [Reference implementations](#reference-implementations)
- [Check](#check)

---

## When this pattern is the right answer

Use when ALL hold:

- A P7 LLM Wiki exists (entity, concept, synthesis, source-summary, index, log pages)
- The wiki carries provenance and supersede records (claims trace to source episodes with stable ids)
- The agent must answer with citations the human reviewer can click through

Do not use when:

- The corpus is unstructured docs only — use standard hybrid RAG (see `hybrid-fusion-patterns.md`)
- The wiki is shape-only (no provenance, no supersede) — fix the wiki first, then add this read path
- Freshness latency exceeds the query SLA — vector over source pages is faster; accept the precision loss

---

## The routing rule

```
incoming query
   |
   +-- extract named entities (people, projects, repos, customers, etc.)
   |
   +-- entities found? -- yes --> fetch entity page(s) directly by stable id
   |                                 |
   |                                 +-- enough to answer? -- yes --> answer + cite entity page
   |                                 |                       no  --> next stage
   |                                 +-- (always carry supersede-aware version pointer)
   |
   +-- classify query into synthesis-page category (e.g. "team-X status", "topic-Y summary")
   |
   +-- synthesis page exists for category? -- yes --> fetch synthesis page
   |                                                    |
   |                                                    +-- enough? -- yes --> answer + cite synthesis page
   |                                                    |              no  --> next stage
   |
   +-- vector retrieval over source pages (fallback)
          |
          +-- relevant results found? -- yes --> answer + cite source pages
          |                                       + flag "vector-only: no entity/synthesis match"
          |                              no  --> return "not in wiki"
          |                                       + offer stub-creation for missing entity/topic
```

Three guarantees this enforces:

1. Named-entity queries hit the entity page — high precision, high freshness.
2. Recurring-question queries hit the synthesis page — the wiki's accumulated-knowledge value.
3. Long-tail queries fall through to vector — and the answer carries a `path=vector` tag so the reviewer knows retrieval was unguided by wiki structure.

---

## Named-entity extraction (NER for routing)

Approach choice (in order of preference):

- **Wiki-index-anchored matcher** — the wiki's index page lists all entity slugs; match query tokens against the index. Zero-shot, no model, deterministic.
- **Org-dictionary NER** — maintained list of entity types + known names (people, projects, repos, customers). Refresh from wiki index daily.
- **LLM NER as a tool call** — extract entities with confidence scores. Use only if dictionary is missing or query is ambiguous. Tag every extraction with `extraction_method=llm` for audit.

Anti-pattern: train a custom NER model. The wiki's own index is the dictionary — keep them in sync.

When multiple entity candidates match, fetch all entity pages and merge before answering. Track `page_version_id` for each.

---

## Synthesis-page routing

Synthesis pages answer recurring query *classes*, not specific facts. Pattern:

- Each synthesis page declares `serves_query_class: [..]` in its frontmatter.
- Router classifies the query against those class descriptors — keyword match or a small embedding lookup over class description strings is sufficient.
- When a synthesis page is hit, the response cites the synthesis page slug AND the source pages listed in the synthesis page's own provenance block. Do not re-derive provenance at query time.

When to skip synthesis routing: if the query is entity-specific and the entity page already has the answer, do not additionally fetch the synthesis page for the entity's domain. Synthesis pages are for class-level queries, not entity lookups.

---

## Vector fallback (last resort)

Vector retrieval reads from **source pages and source-summary pages only** — not from entity or synthesis pages.

Reasoning: entity and synthesis pages are derived artifacts. Vector hits on derived pages are circular — they reproduce what earlier wiki passes concluded rather than grounding in primary evidence. Source pages are atomic and immutable: the correct retrieval substrate.

Vector index scope: source pages + source-summary pages. Embedding and chunking: apply `contextual-retrieval-guide.md` to source-page chunks. Source pages are typically short enough to read whole; source-summary pages benefit from chunk context augmentation.

When the vector fallback fires, the response MUST carry `path=vector` and a `wiki_miss` flag. This is a signal for the wiki maintainer — `wiki_miss` events are the highest-value backlog item for adding stubs or triggering a new ingest pass.

---

## Citation contract

Every claim in the response carries a citation tuple:

```
(wiki_page_slug, page_version_id, retrieved_at)
```

Where:

- `wiki_page_slug` — stable, resolvable, matches the wiki's index
- `page_version_id` — supersede-aware; clicking through must show the version the LLM read, even after the page has changed
- `retrieved_at` — read timestamp

Citation rendering: human-readable link + version pointer in a footnote or sidecar. The reviewer can always reconstruct what the wiki said at the moment the LLM read it.

Citation contract violations (catch in eval):

- Claim without citation — reject
- Citation to a slug that does not exist in the index — reject
- Citation to a version that contradicts the current version — flag as supersede signal, not necessarily wrong

Applies to all three retrieval paths (entity, synthesis, vector). The vector path additionally includes the source-page chunk id.

---

## Missing-entity handling

When NER finds an entity reference but no entity page exists in the wiki:

DO NOT:

- Hallucinate the entity
- Answer from vector only as if the entity is unimportant
- Silently drop the entity from the query

DO:

- Return: "The wiki has no entry for `<entity>`. I can: (a) answer from related source pages with a `path=vector` flag, or (b) draft a stub entity page for review."
- Log a `missing_entity` event with the entity string and query id — these are first-priority backlog items for the wiki maintainer.

Missing-entity events should be queryable separately from `wiki_miss` events (missing-entity = specific name extracted but no page; wiki_miss = no structural match at any level).

---

## Supersede-aware reads

When fetching any wiki page:

- Read the current version — never cache a page beyond its `valid_to` window.
- ALWAYS include a one-line note in the response if a fact pulled into the answer has a supersede record within the last N days (N is system-configurable; default 14).
- Format: "Note: this fact was updated on `<date>` — an earlier version said `<old_value>`."

How to detect: page carries `page_version_id` + a supersede sidecar (`supersedes_id`, `valid_to`, `invalidated_at`). Read both. If any fact in the response has a recent sidecar, surface it.

Supersede transparency is what makes a P7 wiki useful over static documents. An answer that silently uses a superseded fact is a citation-correctness failure.

---

## Composition with existing RAG patterns

| Pattern | Role in wiki-grounded retrieval |
|---|---|
| `grounding-checklists.md` | Applies to the vector-fallback path: compression, citation enforcement, hallucination suppression |
| `hybrid-fusion-patterns.md` | Used inside the vector fallback over source pages (BM25 + dense + RRF) |
| `chunking-strategies.md` | Source-page chunking only — entity and synthesis pages are read whole |
| `contextual-retrieval-guide.md` | Applied to source-page chunk augmentation before indexing |
| `agentic-rag-patterns.md` | When the agent decides multi-hop reads across linked entity pages (follow wikilinks up to a traversal budget) |
| `graph-rag-patterns.md` | When entity pages link to each other; link traversal supplements direct fetch for relationship queries |
| `rag-evaluation-guide.md` | Eval framework; extend with the five wiki-grounded query classes below |

Do not apply context compression (`grounding-checklists.md` Section 1) to entity or synthesis pages — they are sized for whole-page reads. Apply it only to vector-fallback chunks when the context budget is tight.

---

## Eval-set shape

A minimum-viable eval for wiki-grounded retrieval needs five query classes:

1. **Named-entity factual** — single entity, single hop. Expected path: entity page. Metrics: entity-page-hit-rate, citation-tuple correctness.
2. **Named-entity multi-hop** — query spans 2+ linked entity pages. Expected path: entity page + link traversal. Metrics: hop coverage, citation correctness across all hops.
3. **Recurring class (synthesis)** — maps to a known synthesis-page category. Expected path: synthesis page. Metrics: synthesis-hit-rate, synthesis-page freshness vs source-page age.
4. **Long-tail (vector fallback)** — no entity match, no synthesis category match. Expected path: source pages. Metrics: `path=vector` flag set correctly, source-page citation correctness, missing-entity-suggestion quality.
5. **Supersede transparency (regression class)** — facts that recently superseded. Expected: response surfaces the supersede note. Metrics: supersede-note presence rate, correct old-vs-new value in note.

Run class 5 on every release. Supersede regressions are silent — the answer looks correct but the reviewer cannot detect staleness.

---

## Anti-pattern catalog

| Anti-pattern | Consequence | Corrective recipe |
|---|---|---|
| Vector-first over everything including entity pages | Entity facts mediated by similarity — wrong-page hits, confidence leakage | Entity-page-first routing |
| Indexing entity or synthesis pages in the vector store | Circular hits — derived-content retrieval amplifies existing wiki biases | Vector scope = source pages only |
| Hallucinating missing entities | Confident wrong answers with plausible-sounding citations | Missing-entity handler + stub offer |
| Citing without `page_version_id` | Reviewer cannot reproduce the LLM's read | Citation tuple requires version id |
| Ignoring supersede records | Stale facts surfaced as current with no warning | Supersede-aware read + recent-change note |
| LLM NER without dictionary fallback | Entity drift over time; novel-entity inflation | Wiki-index-anchored matcher as primary |
| Mixing vector and entity results without path tagging | Reviewer cannot tell which path answered | Tag each item with `path=entity/synthesis/vector` |
| Applying context compression to entity/synthesis pages | Loses provenance and supersede metadata embedded in full page | Compress only vector-fallback chunks |
| Skipping the supersede eval class | Freshness regressions go undetected | Include class 5 in every release eval |
| Treating `wiki_miss` and `missing_entity` as one event type | Maintainer cannot prioritize stub creation vs ingest pass | Log them as distinct event types with separate counters |

---

## Recipes

### R1 — Stand up wiki-grounded retrieval on an existing P7 wiki

1. Confirm the wiki has provenance, supersede records, and an index page with all entity slugs.
2. Build the wiki-index-anchored NER matcher — read the index page; tokenize slugs; match against query tokens.
3. Implement entity-page direct fetch by slug. Read `page_version_id` and supersede sidecar on every fetch.
4. Implement synthesis-page routing — read `serves_query_class` frontmatter; classify incoming queries against class descriptors.
5. Set up vector index over source pages and source-summary pages only. Apply `contextual-retrieval-guide.md` chunking to source pages.
6. Implement missing-entity handler: surface offer, log `missing_entity` event.
7. Wire citation tuple `(wiki_page_slug, page_version_id, retrieved_at)` for all three paths.
8. Build eval set with all five query classes. Baseline before shipping.

### R2 — Add multi-hop entity traversal

1. Define link types in entity page frontmatter (e.g. `related_to`, `member_of`, `owns`).
2. Set traversal budget: max hops (default 2), max pages per hop (default 3).
3. Add loop detection — track visited slugs; do not re-fetch within a query.
4. Merge retrieved pages; composite citation tuple per hop.
5. Emit traversal trace as a sidecar so the reviewer sees which path the agent walked.
6. Add class 2 (multi-hop) to the eval set and gate on hop-coverage metric.

### R3 — Migrate a vector-only RAG to wiki-grounded

1. Keep the existing vector path running — do not remove it during migration.
2. Add the wiki-index NER matcher in front of the vector path as a pre-filter.
3. Route entity-matching queries to entity-page fetch; pass non-matching queries to vector as before.
4. A/B by query class: measure entity-page-hit-rate and citation correctness improvement vs vector-only baseline.
5. Add synthesis routing after entity routing is stable.
6. Narrow the vector index scope to source pages only once synthesis routing is live.
7. Cut over when all five eval classes pass.

### R4 — Add supersede-aware reads to an existing wiki retrieval path

1. Confirm the wiki page schema includes `page_version_id`, `supersedes_id`, `valid_to`, and `invalidated_at`.
2. On every page fetch, read the supersede sidecar alongside the main page body.
3. For each fact pulled into the response, check if the sidecar has a `valid_to` within the last N days.
4. If yes, prepend the supersede note to the relevant claim: "Note: updated `<date>` — earlier value: `<old_value>`."
5. Add class 5 (supersede transparency) to the eval set. Run it on every release.

---

## Reference implementations

- **Karpathy LLM Wiki v2 writeup (April 2026)** — architectural description of the three-layer pattern (raw sources, wiki pages, typed schema), confidence decay, and the ingest-extract-reconcile pipeline. The synthesis-page pattern and entity-first read priority originate here.
- **SamurAIGPT/llm-wiki-agent** — open-source reference for the ingest pipeline and the `graph.html` inspection UI (wikilink graph with community detection). The entity slug index pattern is derived from this implementation.
- **Ar9av/obsidian-wiki** — reference targeting Obsidian as the storage and UI surface. The `serves_query_class` frontmatter convention maps to Obsidian's dataview metadata model.

---

## Check

Your wiki-grounded retrieval is right if:

- Named-entity queries hit the entity page first — vector is never the first stop for a known entity.
- Synthesis pages are hit for recurring query classes — the agent is not re-running retrieval for questions the wiki has already compiled answers to.
- Vector retrieval is scoped to source pages only — entity and synthesis pages are not in the vector index.
- Every response carries `(wiki_page_slug, page_version_id, retrieved_at)` — no claim is uncited, no citation is unversioned.
- Supersede events within the last N days produce a visible note in the response — stale facts cannot silently pass as current.
- Missing-entity queries return the stub-creation offer and log a `missing_entity` event — they do not hallucinate or silently drop the entity.
- The eval set covers all five query classes including the supersede regression class — freshness regressions are caught before release.
- Each retrieved item is tagged `path=entity`, `path=synthesis`, or `path=vector` — the reviewer always knows which retrieval path answered.
