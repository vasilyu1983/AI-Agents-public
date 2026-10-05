# Cookbook: Mem0 / Mem0g

Adapter file: `reference_app/adapters/mem0_adapter.py`.
Check the `mem0ai` SDK's current release notes before relying on its shape.
Pin the version in your `requirements.txt` and re-run the gated smoke test
on upgrade.

## When to pick Mem0

- You want a managed memory layer with extraction and vector storage already
  wired together, and you do not want to operate Postgres + pgvector + an
  ingest pipeline yourself.
- Your scale is up to ~10M memories per tenant and you can tolerate the
  hosted-API latency floor (~80–200ms p50).
- Your memory shape is mostly **preferences** and **facts** — Mem0's
  extraction is tuned for these.

## When to pick something else

- You need bi-temporal `as_of` queries — Mem0 stores updated_at but does not
  expose first-class fact-time validity windows. Emulating it costs you the
  managed-extraction benefit.
- You need hard provenance (every memory traces to an exact episode row).
  Mem0 supports it via metadata, but the FK guarantee in pgvector is stronger.
- You need >50M memories or sub-50ms latency — switch to pgvector.

## Schema mapping

| Contract field | Mem0 location | Notes |
|---|---|---|
| `LearnedMemory.id` | `memory.id` | We pre-allocate so caller controls IDs |
| `LearnedMemory.value` | `memory.memory` (JSON-encoded) | Bypasses Mem0's extraction; we already extracted upstream |
| `LearnedMemory.confidence` | `memory.metadata.confidence` | Not first-class; in metadata |
| `LearnedMemory.source_episode_id` | `memory.metadata.source_episode_id` | Required; adapter rejects writes without it (A13) |
| `LearnedMemory.invalidated_at` | `memory.metadata.invalidated_at` | Soft-delete pattern (A3 emulation) |
| `LearnedMemory.owner_scope` | Encoded into `user_id` via `_scope_to_user_id` | Structural A10 block |
| `LearnedMemory.supersedes_id` | `memory.metadata.supersedes_id` | Correction chain, not enforced by Mem0 |

## Lifecycle support

| Verb | Native? | Cost of emulation |
|------|---------|-------------------|
| `remember` | Yes (`add`) | None |
| `recall` | Yes (`get_all` + filter) | One round-trip per call; no server-side filtering by metadata in older SDK versions |
| `forget` | **No** (only destructive `delete`) | We emulate via metadata patch + tag — adds one round-trip and leaves the row visible to admin queries until you also call `delete` post-audit |
| `improve` | **No** (no atomic increment) | Read-modify-write — race on concurrent feedback. Acceptable at low feedback volumes; switch to a separate confidence store if you exceed ~10 updates/sec/memory |

## Tenant isolation

Mem0 scopes by `user_id` (and optionally `agent_id`, `run_id`). The adapter
encodes the entire `owner_scope` dict into a deterministic `user_id` string:

```
{"organization_id": "org_42"} + entity "usr_5"
  → "organization_id=org_42|ent=usr_5"
```

This makes cross-tenant leakage structurally impossible — a query for one
scope cannot return rows written under another. The cost is that you cannot
use Mem0's per-org analytics dashboards directly; you have to parse the
encoded `user_id` to reconstruct the scope.

## Gotchas

1. **`add` triggers extraction by default.** We pass JSON strings to
   bypass it, but the SDK still runs LLM-based dedup against existing
   memories on every write. Set `infer=False` if available in your SDK
   version, or expect occasional silent merges.
2. **`get_all` returns paginated results.** Default page size is small
   (~100). For large tenants, paginate explicitly — naive callers will
   see truncated recall results.
3. **Metadata indexing is eventual.** A memory written at T may not be
   filterable by `metadata.confidence` until T+seconds. Smoke tests that
   write then read immediately can flake.
4. **The hosted API has rate limits per workspace, not per tenant.** A
   noisy multi-tenant deployment can throttle other tenants. Add a
   per-`user_id` token bucket on your side, or run self-hosted Mem0.
5. **`update` semantics vary by version.** Some versions replace the
   memory, some merge. Read the SDK changelog before upgrading; the
   adapter assumes merge semantics for metadata.
6. **There is no native bi-temporal store.** If your domain requires
   "what did we believe on date X," you must layer it yourself or pick
   pgvector.

## Smoke test

Env-gated tests should live in `../evals/suites/mem0/` (Phase 3 ships the
adapter; the runnable suite lands when we wire a Mem0-backed CI environment
in Phase 5).

```bash
MEM0_API_KEY=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/mem0 -v
```

## Switching from Mem0 to pgvector

The adapter Protocols make this a one-line wiring change at app startup:

```python
# Before
memory = Mem0MemoryStore(client=mem0.Client())

# After
memory = PostgresMemoryStore(conn=psycopg.connect(POSTGRES_DSN))
```

You will need a one-shot migration script: read every memory via
`Mem0MemoryStore.recall()` for each tenant, write each via
`PostgresMemoryStore.remember()`. Because both satisfy the same Protocol,
the migration script does not depend on either vendor's internals.
