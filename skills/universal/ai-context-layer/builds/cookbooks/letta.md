# Cookbook: Letta (formerly MemGPT)

Adapter file: `reference_app/adapters/letta_adapter.py`.
Check the `letta-client` SDK's current release notes before relying on its
shape; Letta is agent-centric — the adapter is bound to one agent per
`owner_scope`.

## When to pick Letta

- You are building a **long-running agent** (assistant, ops bot, research
  agent) where the same conversation thread continues for weeks or months.
- You want OS-style **tiered memory**: a small RAM-analog block always in
  context, plus on-demand retrieval from a disk-analog archive.
- You want the **agent itself to edit memory** through tool calls (Letta's
  defining feature) rather than your application managing writes externally.

## When to pick something else

- You have many short-lived sessions per user — Letta's per-agent overhead
  doesn't pay back; pick Mem0 or pgvector.
- You need cross-agent memory sharing — Letta isolates per agent by design.
- You need bi-temporal queries — Letta has no first-class fact-time model.
- Your scale is many tenants × many entities — agent count grows fast,
  hosted Letta costs scale with it.

## Schema mapping

| Contract field | Letta location | Notes |
|---|---|---|
| `LearnedMemory` (whole record) | JSON in either core block or archival memory | Tier chosen by `memory_type` + confidence |
| Preferences, procedural, conf ≥ 0.7 | `core_memory.blocks["context_layer_facts"]` | Always visible to the agent |
| Facts, episodic, low confidence | `archival_memory` | Retrieved on demand |
| `LearnedMemory.owner_scope` | The agent's identity itself | One agent per scope |
| `forget` (invalidation) | Tombstone record in archival | Recall filters tombstones out |

## Lifecycle support

| Verb | Native? | Cost of emulation |
|------|---------|-------------------|
| `remember` | Yes (core append or archival insert) | None |
| `recall` | Yes (read core + archival list) | Two round-trips per call |
| `forget` | **No** (no non-destructive update) | Tombstone insertion + filter — adds an archival row, recall must skip them |
| `improve` | **No** (no atomic update) | Feedback log row — confidence aggregator runs offline |
| `find_contradictions` | Yes (archival semantic search) | One round-trip; over-fetch + filter |

The forget/improve emulation is heavier than for Mem0 because Letta's core
block is append-only text (no row updates) and archival inserts are billable
operations. **If your write volume is high (≥10 writes/sec/agent), pick a
different vendor.**

## Tenant isolation

One Letta agent per `owner_scope`. The adapter is constructed with a fixed
scope and rejects any operation whose `LearnedMemory.owner_scope` does not
match. This makes A10 structural — the adapter cannot read or write across
scopes even if the calling code passes the wrong one.

```python
store = LettaMemoryStore(
    client=letta_client,
    agent_id="agent_org_42_main",
    owner_scope={"organization_id": "org_42"},
)
```

For multi-tenant deployments you instantiate one adapter per active scope
and route at the application boundary.

## Gotchas

1. **Core block budget is small (~2k tokens default).** Append carelessly
   and the agent stops fitting useful info in window. The adapter only
   promotes to core when `memory_type ∈ {PREFERENCE, PROCEDURAL}` and
   `confidence ≥ 0.7` — tune the threshold per tenant if you outgrow it.
2. **Archival inserts are not transactional with feedback writes.** A
   crash between insert and feedback log can leave drift. Acceptable for
   memory; fatal for billing. Don't conflate the two stores.
3. **Letta's "self-editing memory" is a feature you can't fully disable.**
   The agent may rewrite core blocks during normal operation. If your app
   logic depends on a memory's exact value, watch for silent edits — log
   the core block diff after every agent turn.
4. **Tombstones accumulate.** Without a cleanup job, archival grows
   linearly with your forget rate. Ship a nightly job that compacts
   tombstones older than your audit window.
5. **No bi-temporal model.** If you need to answer "what did we believe
   on date X," you must keep your own episode log alongside Letta. The
   reference app's `EpisodeLog` adapter does exactly this.

## Smoke test

```bash
LETTA_TOKEN=... LETTA_BASE_URL=... LETTA_AGENT_ID=... \
  PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/letta -v
```

## Switching to/from Letta

Because Letta binds an agent to a scope, migration to/from Letta requires
a per-tenant agent provisioning step. The adapter Protocol is the same;
the *instantiation pattern* changes:

```python
# pgvector — one process-wide store, per-request scope
memory = PostgresMemoryStore(conn)
memory.recall(entity_id=..., owner_scope=scope)

# Letta — one store per scope (built once, reused per request)
memory = LettaMemoryStore(client, agent_id=lookup(scope), owner_scope=scope)
memory.recall(entity_id=..., owner_scope=scope)  # owner_scope must match
```

Plan for the agent provisioning step before you commit to Letta.
