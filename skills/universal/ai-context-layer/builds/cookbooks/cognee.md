# Cookbook: Cognee

Adapter file: `reference_app/adapters/cognee_adapter.py` (ships
`CogneeRetrievalStore` and a thin `CogneeMemoryStore`).

## When to pick Cognee

- You want **graph + vector hybrid retrieval** out of the box. Cognee
  builds an ontology from your documents and lets you traverse
  relationships at query time — useful when the answer depends on how
  entities relate, not just what each one says.
- You are willing to run an ingest pipeline (Cognee's `cognify` step is
  not free) in exchange for richer retrieval.
- You already maintain a separate typed-memory store and want Cognee to
  own the retrieval layer (P8) only — this is the most common production
  split.

## When to pick something else

- You want one vendor for both memory and retrieval — Cognee's memory
  side is thin (lifecycle support is partial). Pair with pgvector or
  use Mem0/Letta for memory.
- Your corpus changes constantly — `cognify` is batchy by design;
  near-real-time invalidation is awkward.
- You don't need graph traversal — pgvector is faster, cheaper, and has
  better lifecycle semantics.

## Schema mapping

| Contract field | Cognee location | Notes |
|---|---|---|
| `RetrievalResult.snippet` | Search result `text`/`payload` | Truncated to 2000 chars |
| `RetrievalResult.evidence_id` | Search result `id` | Stable per cognify run |
| `RetrievalResult.metadata.graph` | Search result `graph_context` | Populated when query_type=INSIGHTS |
| `LearnedMemory` (whole) | JSON-encoded document in dataset | Memory store mode only |
| `owner_scope` | `dataset_name` via `_scope_to_dataset` | Structural A10 |

## Lifecycle support

| Verb | Native? | Cost of emulation |
|------|---------|-------------------|
| `index` (retrieval) | Yes (`add` + `cognify`) | None |
| `retrieve` | Yes (`search`) | None — supports vector + graph + hybrid |
| `invalidate` (per source_id) | **No** | Requires you to maintain a source_id → node_id map at index time. The adapter raises `NotImplementedError` rather than silently drifting |
| `remember` (memory mode) | Yes (`add`) | Cognification is batchy; recently-written memories are not searchable until next `cognify` |
| `recall` (memory mode) | Yes (`search`) | One round-trip per call |
| `forget` (memory mode) | **No** | Adapter raises explicitly — use the dual-vendor split instead |
| `improve` | **No** | Adapter raises explicitly |
| `find_contradictions` | Yes (semantic) | Over-fetch + filter, same shape as Mem0 |

## Tenant isolation

`_scope_to_dataset` flattens `owner_scope` into a stable Cognee dataset
name. All operations are scoped to that dataset. This is structural A10
— a query against one dataset cannot return rows from another.

```
{"organization_id": "org_42"}
  → dataset name "ctx-organization_id-org_42"
```

For multi-tenant deployments at scale, watch the dataset count — Cognee's
operational footprint grows with active datasets.

## Gotchas

1. **`cognify` is the slow step.** Adding a document is fast; building
   the graph + embeddings on it can take seconds to minutes. Treat
   `index()` as eventual — never assume a chunk is searchable
   immediately after `index()` returns.
2. **The async API churns.** Across recent SDK versions, `cognee.add` /
   `cognify` / `search` have all changed signatures (sync vs async,
   `dataset_name` vs `datasets=[...]`). Pin the version, run the smoke
   test on upgrade, and prefer adapter changes over conditional code.
3. **Per-source invalidation is not first-class.** The adapter raises
   `NotImplementedError` rather than silently failing. To support it,
   maintain a `source_id → cognee_node_ids` table at index time and
   call `delete_nodes(...)` on invalidation. Most teams do not need
   this and re-cognify the dataset instead.
4. **The graph view is powerful but not always "right."** Cognee infers
   the ontology automatically; the inferred relationships are usually
   useful but occasionally surprising. Treat graph traversals as
   suggestions, not source-of-truth — never inject a graph-derived
   "fact" into memory without P9 review.
5. **Search result shapes vary by `query_type`.** `CHUNKS`, `INSIGHTS`,
   `GRAPH_COMPLETION` return different fields. The adapter handles the
   common case (`CHUNKS`); add branches if you use the others.

## Recommended pattern: dual-vendor split

In production, most teams use Cognee for retrieval (P8) and a separate
memory store (P2/P5/P6) — pgvector or Mem0 — for typed memory. The Protocol
abstraction makes this clean:

```python
memory = PostgresMemoryStore(conn)              # owns LearnedMemory
retrieval = CogneeRetrievalStore(cognee_module) # owns KnowledgeSource + KG

bundle = assemble(
    memory_store=memory,
    retrieval_store=retrieval,
    ...
)
```

The runtime verbs don't care that they hit two different vendors.

## Smoke test

```bash
COGNEE_LLM_API_KEY=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/cognee -v
```

The smoke suite tests the dataset isolation invariant (writes to scope A
do not appear in scope B's search results) and round-trip serialization.
