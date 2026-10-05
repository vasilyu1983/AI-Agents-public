# Cookbook: MongoDB Atlas (Converged Document + Vector + Memory)

The converged-datastore adapter. Choose this when one team owns the full stack,
operational documents already live in MongoDB, and you want operational state,
agent memory, and vector retrieval in one cluster with one ops story.

This is the substrate behind RA9 (Converged Datastore). It composes with
LangGraph Store for memory namespaces and the LangGraph MongoDB checkpointer
for short-term turn state.

## When to pick this vendor

- Operational data already lives in MongoDB; pulling agent memory into a
  separate database doubles your ops surface for marginal architectural gain.
- You want a single cluster, single backup, single ACL, single migration story
  across user state, conversation history, learned facts, and chunk retrieval.
- You want **`autoEmbed`** to remove the embedding pipeline entirely, and you
  accept the model-coupling tradeoff (Voyage 4 family today; switching providers
  means re-indexing).
- You need both JS and Python long-term memory parity — LangGraph.js Long-Term
  Memory Store on Atlas went GA in May 2026.
- Your scale is up to ~10–100M memory rows and ~1–10M retrieval chunks per
  database. Beyond that, separate retrieval onto Qdrant/Milvus/Vespa.

## When to pick something else

- **You already run Postgres** → use the pgvector cookbook. Atlas brings nothing
  decisive over Postgres + pgvector unless your team prefers documents over
  relations.
- **You need bi-temporal facts** (P4) → Graphiti/Zep on Neo4j. Atlas does not
  ship bi-temporal validity windows; you would model `valid_from / valid_to /
  recorded_at / invalidated_at` by hand.
- **You need RLS-style storage-layer tenant isolation** → Postgres + RLS or
  Supabase. Atlas relies on app-layer scope enforcement plus per-collection or
  per-cluster isolation; A2 is on you.
- **You need to swap embedding models freely** → autoEmbed is convenient but
  binds you to the configured Voyage model. If your roadmap includes embedding
  migration, generate embeddings outside the DB and store them as raw arrays.
- **>100M memory rows or >10M chunks per cluster** → look at sharded clusters
  with attention to vector index size, or split retrieval to a dedicated vector
  DB.

## Schema mapping

Memory collection (`learned_memory`):

| Contract field | Mongo field | Notes |
|---|---|---|
| `LearnedMemory.id` | `_id: string` | App-generated UUID |
| `LearnedMemory.value` | `value: object` | Keep small; raw prose belongs in chunks |
| `LearnedMemory.confidence` | `confidence: double` | App-validated 0..1 |
| `LearnedMemory.source_episode_id` | `source_episode_id: string` | Required (A13) |
| `LearnedMemory.invalidated_at` | `invalidated_at: Date \| null` | Set by `forget`; never `deleteOne` |
| `LearnedMemory.supersedes_id` | `supersedes_id: string \| null` | Correction chain |
| `LearnedMemory.owner_scope` | `owner_scope: object` | Indexed; every read filters on this (A10) |

Chunk collection (`knowledge_chunk`) with autoEmbed:

```js
db.knowledge_chunk.createIndex(
  { embedding: "vectorSearch" },
  {
    name: "kc_vec",
    type: "vectorSearch",
    vectorSearchConfig: {
      fields: [
        {
          path: "embedding",
          numDimensions: 1024,            // voyage-4 default
          similarity: "cosine",
          autoEmbed: {
            type: "autoEmbed",
            sourcePath: "snippet",        // text MongoDB will embed
            model: "voyage-4-large",
            credentials: "<your-voyage-key-secret>"
          }
        },
        { path: "owner_scope", type: "filter" }   // for tenant scoping
      ]
    }
  }
);
```

When you `insertOne({ snippet: "...", owner_scope: {...} })`, the embedding is
generated server-side and stored in a system collection alongside; reads via
`$vectorSearch` are transparent.

## Lifecycle support

| Verb | Native? | How |
|------|---------|-----|
| `remember` | Yes | `insertOne` with full provenance + confidence |
| `recall` | Yes | `find({ owner_scope, invalidated_at: null })` + `$vectorSearch` for chunk recall |
| `forget` | Yes (non-destructive) | `updateOne({ _id }, { $set: { invalidated_at: new Date() } })` |
| `improve` | Yes | `updateOne` with `$min`/`$max` to clamp confidence |

Short-term memory (turn-by-turn): use the **MongoDB LangGraph checkpointer**
(`@langchain/langgraph-checkpoint-mongodb`). Each thread gets its own checkpoint
documents; thread isolation comes from `thread_id` keys, not collections.

## Tenant isolation

Atlas does not have RLS. You enforce in three layers:

1. **Adapter API is scope-mandatory.** Every read takes
   `owner_scope: dict[str, str]` and the filter is constructed app-side.
2. **Collection-level mandatory filter index.** Compound index leading on
   `owner_scope.organization_id` or equivalent so query plans can't accidentally
   omit it.
3. **Per-tenant database (high isolation tier).** When tenants are large,
   high-trust, or regulated, isolate by database not collection. Pay the
   connection-pool cost; gain audit clarity.

Penetration test: attempt cross-tenant read by mutating the owner_scope filter
in a request. The adapter should reject before the query reaches Mongo.

## `autoEmbed` lock-in mitigation

The autoEmbed feature stores generated vectors in a *separate system collection*
on the same cluster. To survive a model switch:

1. Keep the `snippet` (source text) in the public collection — never throw it
   away. Re-embedding requires reading text, not vectors.
2. Document the rebuild path: drop the vector index, change the `model`, recreate
   the index. Atlas re-embeds existing rows; budget for re-index time at scale.
3. For pre-computed embeddings (you ran your own model), use a plain
   `vectorSearch` index without `autoEmbed`. autoEmbed is opt-in per index.

## Gotchas

1. **`autoEmbed` is bound to the index, not the document.** Changing the
   embedding model means dropping and recreating the index, not migrating data.
   Plan for an asynchronous re-embed window at large scale.
2. **`numDimensions` must match the chosen Voyage model.** voyage-4-large = 1024,
   voyage-4 = 1024, voyage-4-lite = 512, voyage-code-3 = 1024. Mismatched dims
   silently degrade recall; check on every model change.
3. **`$vectorSearch` and `find()` filters compose differently.** Pre-filter
   fields must be declared in the index `filter` section. Adding a new
   `owner_scope` shape requires an index update, not just a query change.
4. **System collection for autoEmbed embeddings counts toward storage cost.**
   At 4KB per 1024-dim float32 vector (1024 × 4 bytes), 10M chunks ≈ 40GB before compression.
5. **LangGraph checkpointer thread documents grow with each step.** Compact
   long threads with `compress` (six-verb runtime) before they balloon — see
   `references/context-hygiene.md`.
6. **Voyage 4 keys are stored encrypted in Atlas.** They are not exportable.
   Treat them as Atlas-bound credentials; for portability, generate embeddings
   in your app and store raw vectors instead.
7. **Compound indexes with vector path require Atlas Search M10+.** Free-tier
   shared clusters do not support `$vectorSearch`.

## Cross-cluster pattern

For converged stacks at scale, the pattern is:

- **Hot cluster (M30+):** operational documents, agent memory, short-term
  checkpointer.
- **Warm cluster or Atlas Search dedicated nodes:** chunk retrieval with
  autoEmbed.
- **Optional cold tier (Turbopuffer or S3):** rarely-accessed chunks beyond
  retention threshold.

This composes inside RA9 and stays inside the converged-datastore boundary.

## Smoke test

Env-gated tests live in `../evals/suites/mongodb/` (Phase 7, planned):

```bash
MONGODB_ATLAS_URI=mongodb+srv://... \
  VOYAGE_API_KEY=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/mongodb -v
```

Without `MONGODB_ATLAS_URI`, the suite is skipped at collection time.

## Primary sources

- `data/sources.json` → MongoDB Atlas Vector Search docs
- `data/sources.json` → MongoDB autoEmbed (Jan 2026 preview, May 2026 GA)
- `data/sources.json` → LangGraph.js Long-Term Memory Store on MongoDB
- `data/sources.json` → Voyage 4 model card

## See also

- `pgvector.md` — the relational alternative substrate
- `langgraph_store.md` — the framework layer above either substrate
- `references/managed-memory-boundaries.md` — autoEmbed boundary discussion (P13)
- `references/reference-architectures.md` → RA9 — the recipe this cookbook supports
