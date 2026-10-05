# Operational Brain Pattern

Portable pattern for a living agent-maintained knowledge base inspired by
`garrytan/gbrain`. Use this when a product needs accumulating, reviewable
knowledge about people, organizations, projects, decisions, meetings, or other
entities that change over time.

This is a context-layer pattern, not a requirement to adopt GBrain's personal
taxonomy or runtime.

## Table of Contents

- [When To Use](#when-to-use)
- [Core Shape](#core-shape)
- [Four Structured Primitives](#four-structured-primitives)
- [Page Contract](#page-contract)
- [Routing Rules](#routing-rules)
- [Maintenance Loop](#maintenance-loop)
- [Brain And Source Boundaries](#brain-and-source-boundaries)
- [Anti-Patterns](#anti-patterns)
- [Relationship To Existing Patterns](#relationship-to-existing-patterns)
- [Source Notes](#source-notes)

## When To Use

Use an operational brain when all of these are true:

- New signals arrive continuously: meetings, messages, files, emails, events,
  customer notes, tickets, transcripts, or repo changes.
- Humans and agents both need a readable current picture, not only raw search
  results.
- Entity identity, contradictions, relationship traversal, and historical state
  affect decisions.
- The same synthesis would otherwise be recomputed by RAG on every query.

Prefer normal evidence-bearing retrieval when the corpus is static, the consumer
is only an LLM, or no human will review compiled pages.

## Core Shape

```text
raw signals
  -> extract entities, events, claims, and relations
  -> reconcile identity and aliases
  -> upsert structured facts with provenance
  -> append immutable events
  -> refresh compiled pages
  -> index chunks and graph edges for retrieval
```

An operational brain has two synchronized views:

- **Human view:** markdown or wiki pages with current compiled truth at the top
  and an append-only timeline below it.
- **Machine view:** structured primitives for identity, events, facts,
  relationships, chunks, embeddings, and query logs.

Markdown is the review and editing surface. The structured layer is the source
for identity resolution, as-of queries, contradiction checks, and graph
traversal.

## Four Structured Primitives

| Primitive | Purpose | Required behavior |
|---|---|---|
| Entity registry | Canonical identity, aliases, external IDs, merge history | Slugs or IDs stay stable; aliases prevent split-brain pages. |
| Event ledger | Immutable signal history | Every meeting, correction, ingest, enrichment, or source update carries provenance and time. |
| Fact store | Current and historical claims | Facts carry source, confidence, validity window, and supersession state. |
| Relationship graph | Typed edges between entities and artifacts | Edges support questions that search cannot answer, such as who worked with whom or what implements a policy. |

These primitives can live in Postgres, SQLite/PGLite, a graph store, or a
converged app database. The design requirement is logical separation, not a
specific vendor.

## Page Contract

Each compiled page should separate current synthesis from evidence:

```text
# Entity or Concept Name

## Compiled Truth
- Current summary
- State fields
- Open threads
- See also / related entities

---

## Timeline
- YYYY-MM-DD | Source | What changed | Citation or raw pointer
```

Rules:

- The top section can be rewritten as evidence changes.
- The timeline is append-only except for explicit correction records.
- Claims in compiled truth cite source events, facts, or source chunks.
- Contradictions are shown as unresolved facts, not silently collapsed.
- User corrections and direct system-of-record updates outrank inferred facts.

## Routing Rules

Use retrieval mode based on the question:

| Question type | First route | Why |
|---|---|---|
| "What do we know about X?" | Compiled page + recent timeline | The answer needs current synthesis plus freshness. |
| "Who is connected to X?" | Relationship graph | Text similarity cannot reliably traverse typed edges. |
| "Where did this claim come from?" | Fact store -> event ledger -> raw source | Citation needs provenance, not nearest-neighbor text. |
| "Find relevant docs about X" | Hybrid lexical + vector retrieval | This is corpus lookup, not entity state. |
| "What changed since date D?" | Event ledger or as-of facts | Temporal questions need time-bounded records. |

Graph-first is for relationship traversal. Hybrid retrieval is still the default
for evidence text, explanations, and open-ended document lookup.

## Maintenance Loop

Run a periodic health loop for any operational brain:

1. **Stale compiled truth:** pages where timeline/facts changed after the last
   compiled-page refresh.
2. **Orphans:** important pages with no inbound links or graph edges.
3. **Dead links:** page links, fact references, or source pointers that no
   longer resolve.
4. **Missing cross-references:** text mentions of canonical entities without
   graph edges.
5. **Citation gaps:** compiled claims without event, fact, or chunk support.
6. **Identity splits:** similar names, aliases, external IDs, or emails attached
   to multiple entities.
7. **Embedding freshness:** chunks missing embeddings or carrying old model IDs.
8. **Open threads:** unresolved actions or contradictions past their review SLA.
9. **Access boundaries:** tenant, source, or brain boundaries still enforced in
   retrieval and write paths.

The loop can run as a nightly job, but writes must be idempotent. Re-running on
unchanged input should not create duplicate facts, events, pages, or edges.

## Brain And Source Boundaries

Use two independent routing axes:

- **Brain:** the database or trust boundary. Move brains when the data owner,
  retention policy, access model, or deployment lifecycle changes.
- **Source:** a corpus, repo, vault, team folder, or channel inside a brain.
  Move sources when the owner stays the same but the content stream changes.

Cross-brain federation should be agent-directed and explicit. Do not hide access
control or ownership decisions inside a single global vector index.

## Anti-Patterns

- Treating the markdown page as the only source of truth when identity merges,
  contradictions, or concurrency matter.
- Re-indexing model-written summaries as primary evidence.
- Using vector search for relationship questions that need typed graph edges.
- Creating duplicate pages because alias and external-ID lookup was skipped.
- Letting maintenance rewrite timelines instead of appending correction records.
- Running a sleep-time consolidator that re-ingests its own summaries as facts.
- Collapsing personal, team, and customer brains into one index with filters
  added later.

## Relationship To Existing Patterns

- P7 knowledge compilation is the human-readable wiki layer.
- P14 sleep-time consolidation is the maintenance loop.
- P17 schema-grounded writes protect the fact store from poisoning and mode
  collapse.
- `ai-vector-brain` owns the serving index and manifest for chunks, embeddings,
  and retrieval tools.
- `ai-rag` owns retrieval mode choice, graph-vs-vector routing, evals, and
  answer faithfulness checks.

## Source Notes

`garrytan/gbrain` is an MIT-licensed reference for this pattern:
markdown pages as the readable layer, Postgres/PGLite + pgvector as a structured
projection, hybrid search, typed graph edges, skill-driven operations, and
maintenance loops. Reuse the architecture shape, not its personal domain
taxonomy.
