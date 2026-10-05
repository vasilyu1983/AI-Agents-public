# Cookbook: Supermemory

Adapter file: `reference_app/adapters/supermemory_adapter.py`.
Check the Supermemory REST API's current docs before relying on its shape.

## When to pick Supermemory

- You want a **hosted universal memory layer** that works across multiple
  apps (browser extension, native app, server) sharing one user's memory.
- You want **zero ops** — no schema, no embeddings, no rerankers to run.
- You are okay with a **HTTP-only surface** (no native client lock-in)
  and the latency floor that comes with it.

## When to pick something else

- Your data must stay on-prem — Supermemory is hosted; check current docs
  for any self-host option before ruling this out.
- You need bi-temporal queries or strict provenance audits — Supermemory
  treats memory as opaque content + metadata.
- You need sub-50ms recall — hosted REST adds 50–150ms minimum.

## Schema mapping

| Contract field | Supermemory location | Notes |
|---|---|---|
| `LearnedMemory.value` | `memory.content` (JSON-encoded string) | Round-trips cleanly |
| `LearnedMemory.confidence` | `memory.metadata.confidence` | Not first-class, lives in metadata |
| `LearnedMemory.source_episode_id` | `memory.metadata.source_episode_id` | Required; adapter rejects writes without it (A13) |
| `LearnedMemory.invalidated_at` | `memory.metadata.invalidated_at` | Soft-delete pattern |
| `owner_scope` | `containerTags` (sorted `key:value` list) | Structural A10 |

## Lifecycle support

| Verb | Native? | Cost of emulation |
|------|---------|-------------------|
| `remember` | Yes (`POST /v1/memories`) | None |
| `recall` | Yes (`POST /v1/memories/search`) | One round-trip |
| `forget` | **No** non-destructive option | Metadata patch + tag (Mem0-style emulation) |
| `improve` | **No** atomic update | Read-modify-write — racey at high feedback volume |
| `find_contradictions` | Emulated via search | Over-fetch + client-side filter |

## Tenant isolation

Supermemory's `containerTags` are server-side filterable. The adapter
flattens `owner_scope` into a stable sorted tag list and includes the
entity. Cross-tenant queries are structurally blocked — a search with a
different tag set cannot return rows tagged with the original.

```
{"organization_id": "org_42"} + entity "usr_5"
  → containerTags = ["entity:usr_5", "organization_id:org_42"]
```

## Gotchas

1. **The HTTP client is your responsibility.** The adapter takes a
   `HttpClient` Protocol — `httpx.Client`, `requests.Session`, or a test
   double. Don't share one client across threads if you need
   cancellation guarantees; check the underlying lib's docs.
2. **Endpoint paths shift across versions.** This adapter pins
   `/v1/memories` and `/v1/memories/search`. If Supermemory ships a v2,
   re-map the paths in one place rather than spreading the change
   through callers.
3. **Server-side dedup may merge writes silently.** Two memories with
   similar content under the same containerTags may collapse into one.
   If your downstream logic depends on exact write count, request
   `dedup=false` (if available) or assert post-write that the IDs you
   passed survived.
4. **Rate limits are per API key, not per tenant.** A noisy multi-tenant
   deployment can throttle other tenants. Add per-`owner_scope` token
   bucket on your side.
5. **No bi-temporal model.** "What did we believe on date X" requires a
   parallel episode log on your side. The reference app's `EpisodeLog`
   adapter does exactly this.

## Smoke test

```bash
SUPERMEMORY_API_KEY=... SUPERMEMORY_BASE_URL=https://api.supermemory.ai \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/supermemory -v
```

## When to combine Supermemory with other vendors

The most common production split:

- **Supermemory**: cross-device user-level memory (preferences, long-
  running personal facts).
- **pgvector**: domain-specific retrieval and operational memory inside
  your own app boundary.

The runtime can call both — `assemble()` happily takes one
`MemoryStore` per concern if you compose them with a thin
`UnionMemoryStore` wrapper. Phase 5 ships an example.
