# Migrations

Numbered SQL files applied in order. No down-migrations on purpose — context-layer
schemas are append-only by design (memory is non-destructive, episodes are
append-only). Roll forward with new migrations; never roll back.

## Apply

```bash
psql "$POSTGRES_DSN" -f 0001_initial.sql
```

## What blocks what

| Migration | Blocks | How |
|-----------|--------|-----|
| 0001 | A2 (vector DB as system of record) | KnowledgeChunk holds prose only; entity state is not modeled |
| 0001 | A3 (destructive overwrite) | `invalidated_at` + `supersedes_id` instead of UPDATE in place |
| 0001 | A7 (hard delete) | No `DELETE` path in adapter API; invalidate only |
| 0001 | A10 (no tenant scope) | Every table has `owner_scope jsonb NOT NULL` |
| 0001 | A11 (no lifecycle) | Schema supports `remember/recall/forget/improve` natively |
| 0001 | A13 (provenance) | `source_episode_id` is `NOT NULL REFERENCES episode_log(id)` |
| 0001 | A14 (no confidence) | `confidence double precision NOT NULL CHECK (...)` |

## Known limitations (Phase 2)

- Vector dimension is hard-coded to 1536. To use a different embedding model,
  edit the column type before running. Phase 5 ships a re-embedding cookbook.
- `ivfflat` works fine to ~1M chunks. Switch to `hnsw` for larger corpora —
  same vector ops, different index build.
- No partition strategy yet. For multi-tenant deployments above ~10M memory
  rows, partition `learned_memory` by `(owner_scope ->> 'organization_id')`.
