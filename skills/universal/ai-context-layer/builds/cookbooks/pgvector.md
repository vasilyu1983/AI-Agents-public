# Cookbook: Postgres + pgvector (Default)

The reference adapter set. Choose this when you want one durable store for
operational truth, derived memory, episode logs, and retrieval, and you would
rather scale Postgres than learn a new vendor's failure modes.

## When to pick this vendor

- You already run Postgres in production and have ops muscle for it.
- You want a single backup, ACL, and migration story across all four layers.
- Your scale is up to ~10–50M memory rows and ~1–5M retrieval chunks.
- You can tolerate query-time embedding generation latency (≈30–80ms with a
  hosted embedder, near-zero with a local one).

## When to pick something else

- **>50M memory rows or >10M chunks** → look at a dedicated vector DB plus
  Postgres for memory (Vespa, Vertex Matching Engine, Turbopuffer).
- **You want a managed memory layer with extraction built-in** → Mem0
  (cookbook entry pending Phase 3).
- **You want OS-style tiered context for long-running agents** → Letta
  (cookbook entry pending Phase 3).
- **You want a graph-first model** → Cognee (cookbook entry pending Phase 3).

## Schema mapping

| Contract field | Postgres column | Notes |
|---|---|---|
| `LearnedMemory.id` | `learned_memory.id text PRIMARY KEY` | App-generated UUID |
| `LearnedMemory.value` | `value jsonb` | Keep small; raw prose belongs in chunks |
| `LearnedMemory.confidence` | `confidence double precision CHECK (0..1)` | Type-level A14 |
| `LearnedMemory.source_episode_id` | `source_episode_id text REFERENCES episode_log(id)` | Type-level A13 |
| `LearnedMemory.invalidated_at` | `invalidated_at timestamptz` | Set by `forget`, never DELETE |
| `LearnedMemory.supersedes_id` | `supersedes_id text REFERENCES learned_memory(id)` | Correction chain |
| `LearnedMemory.owner_scope` | `owner_scope jsonb NOT NULL` | Every read filters on this (A10) |
| `RetrievalResult.snippet` | `knowledge_chunk.snippet text` | The text the model sees |
| `RetrievalResult.evidence_id` | `knowledge_chunk.id text` | Stable across runs |
| (embedding) | see `ai-vector-brain` | Vector schema, dim choice, HNSW/halfvec tuning, and model migration are owned by the `ai-vector-brain` skill — do not duplicate the canonical schema here |

## Lifecycle support

| Verb | Native? | How |
|------|---------|-----|
| `remember` | Yes | INSERT with full provenance + confidence |
| `recall` | Yes | Bi-temporal SELECT, ACL-scoped, partial active index |
| `forget` | Yes (non-destructive) | UPDATE invalidated_at + tag |
| `improve` | Yes | UPDATE confidence with `LEAST(1, GREATEST(0, ...))` |

## Tenant isolation

Adapter API is scope-mandatory: every read takes `owner_scope: dict[str, str]`
and the WHERE clause uses `owner_scope = %s::jsonb` (exact match). For Row
Level Security:

```sql
ALTER TABLE learned_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY scope_policy ON learned_memory USING (
  owner_scope @> current_setting('app.owner_scope')::jsonb
);
```

Then `SET LOCAL app.owner_scope = '{"organization_id": "..."}'` per request.
RLS is belt-and-suspenders — the adapter already filters, but RLS makes it
unforgeable from app code.

## Gotchas

1. **`vector` dim is hard-coded at the column level.** Switching embedding
   models requires re-embedding the whole corpus. The `model_id` shadow-column
   migration pattern is owned by the `ai-vector-brain` skill — see
   `references/postgres-pgvector-default.md` (Embedding Migration) and
   `assets/sql/001_schema.sql` (`embeddings.model_id`).
2. **Index choice (HNSW vs IVFFlat vs pgvectorscale), `iterative_scan` for
   filtered queries, `halfvec` for >2000-dim models, and per-session
   `ef_search` tuning** are owned by `ai-vector-brain`. This cookbook only
   tells you when Postgres+pgvector is the right substrate for the
   ai-context-layer reference architecture; for the canonical operational
   recipe see `ai-vector-brain/references/postgres-pgvector-default.md`.
3. **JSONB equality on `owner_scope` is exact match, not subset.**
   `{"a": 1}` does not match `{"a": 1, "b": 2}`. If you need hierarchical
   tenancy (org > workspace > project), normalize the scope shape *before*
   passing it to the adapter, or switch the WHERE clause to `@>`.
4. **`vector` columns serialize as PostgreSQL strings**, not Python lists.
   The adapter handles this with its embedding-literal helper. If you query
   directly, register the pgvector psycopg adapter on the connection so list
   round-trips work.
5. **Connection-per-request is fine to ~200 RPS**, beyond which switch to
   `psycopg_pool.AsyncConnectionPool`. The adapter doesn't own pooling on
   purpose — let your app frame the connection lifecycle.

## Smoke test

Env-gated tests live in `../evals/suites/postgres/`:

```bash
POSTGRES_DSN=postgresql://user:pass@localhost/contextlayer_test \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/postgres -v
```

Without `POSTGRES_DSN`, the suite is skipped at collection time so CI on
machines without Postgres still runs the smoke suite cleanly.
