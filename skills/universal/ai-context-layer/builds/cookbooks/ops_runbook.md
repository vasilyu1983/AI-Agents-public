# Cookbook: Operations Runbook

Day-2 operations for a context layer in production. Treat this as a
starter — your platform team owns the final shape — but the mechanics
below survive most tooling choices.

## Pre-launch checklist

- [ ] Schema migration applied in every environment (`migrations/0001_initial.sql`)
- [ ] Eval harness runs in CI on every PR (`evals/suites/smoke` mandatory; suites with credentials gate cleanly)
- [ ] Anti-pattern sweep documented per surface (`references/anti-patterns-catalog.md`) — every applicable A entry is `BLOCKED` or `NOT BLOCKED (accepted: ...)`
- [ ] Token-budget assertions wired into integration tests
- [ ] Per-surface tool allowlists configured (F4 mitigation)
- [ ] Confidence floor for `recall` set per surface
- [ ] `forget` audit log shipped to your retention store
- [ ] Cache hit ratio dashboard live with alert at <40% sustained
- [ ] Sub-agent dispatch rate dashboard live with alert at >2× rolling baseline
- [ ] Kill-switch flag for the memory layer (see below) tested in staging
- [ ] Rollback plan documented and rehearsed once

## Schema migrations without downtime

Adding columns to `learned_memory` is the most common ongoing migration.
The reference schema avoids the worst pitfalls (no destructive updates,
non-NULL only on insert), but every new column needs a careful sequence:

```sql
-- 1. Add nullable column. Safe; no rewrite.
ALTER TABLE learned_memory ADD COLUMN trust_tier text;

-- 2. Backfill in batches (don't lock the table).
UPDATE learned_memory
SET trust_tier = 'standard'
WHERE id IN (
  SELECT id FROM learned_memory WHERE trust_tier IS NULL LIMIT 10000
);
-- repeat until 0 rows updated

-- 3. Once 100% backfilled, add NOT NULL + default.
ALTER TABLE learned_memory ALTER COLUMN trust_tier SET DEFAULT 'standard';
ALTER TABLE learned_memory ALTER COLUMN trust_tier SET NOT NULL;
```

**Never `DROP COLUMN`** on `learned_memory` directly. Memory rows are
audit records — once written, they are part of your history. If you
must remove a column, write a migration that copies the table without
it, audited as a one-time event.

For pgvector embedding-dim changes, see `traps.md` §
embedding-model migration.

## Backfill: extracting memories from existing chat history

Common scenario: you've had chats running for months without a memory
layer. Switch on the layer, then backfill.

```python
from reference_app.runtime import write
from reference_app.contracts import LearnedMemory, MemoryType

for episode in episode_log.iterate(scope=org_scope):
    extracted = your_extractor(episode.text)  # P5 extraction pipeline
    for fact in extracted:
        write(
            fact=LearnedMemory(
                id="",
                entity_id=episode.user_id,
                entity_type="user",
                memory_type=MemoryType(fact["type"]),
                value=fact["value"],
                source="backfill",
                source_episode_id=episode.id,
                confidence=fact["confidence"],
                created_at=episode.timestamp,
                updated_at=now(),
                owner_scope=org_scope,
                inferred=True,  # backfill is by definition inferred
            ),
            memory_store=memory,
        )
```

Backfill rules:

- **Always set `inferred=True`** for backfill rows. They were not
  user-stated. A26 (mode-collapse loop) defenses depend on the
  inferred flag being honest.
- **Cap confidence at 0.6** for backfill — the extractor is working
  on stale text without context cues.
- **Run in batches with rate limits** — extraction is LLM-driven and
  can blow your provider budget overnight.
- **Test on one tenant first** — extraction quality varies wildly by
  domain. A bad extractor poisons the memory layer (F1) before you
  notice.
- **Keep the source episodes** — backfill is reversible only if you
  can re-extract from the originals.

## A/B switching memory adapters (Mem0 → pgvector, etc.)

The Protocol abstraction makes this safe. Pattern:

```python
from reference_app.adapters import Mem0MemoryStore, PostgresMemoryStore
from reference_app.runtime import UnionMemoryStore

# Phase 1: dual-write, single-read.
old = Mem0MemoryStore(client=mem0_client)
new = PostgresMemoryStore(conn=pg)
memory = DualWriteMemory(primary=old, mirror=new)  # custom — see below

# Phase 2: dual-read with old as primary (sanity check).
memory = UnionMemoryStore(primary=old, readers=[new])

# Phase 3: cutover — new as primary, old as fallback.
memory = UnionMemoryStore(primary=new, readers=[old])

# Phase 4: drop old.
memory = new
```

`DualWriteMemory` is ~30 lines: `remember` writes to both, `recall`
returns from the primary. It is intentionally not in the kit because
the right shape depends on your error semantics — does a mirror write
failure block the primary? Almost always no for memory; for
operational truth, almost always yes.

Each phase should run for at least one full feedback cycle (typically
1–2 weeks) before advancing. Phase 2 is the longest because it's the
phase that catches schema-translation bugs.

## Kill switch: turning the memory layer off without breaking the app

Wire a feature flag at the assembly layer, not the adapter layer:

```python
def assemble_with_killswitch(...):
    if flag("memory_layer_enabled", scope=org_scope):
        return assemble(...)
    # Graceful degradation: empty memory + evidence, live_facts only.
    return ContextBundle(
        surface=request.surface,
        actor=request.actor,
        owner_scope=request.owner_scope,
        live_facts=toolkit.fetch_live_facts(entity=entity, request=request),
        memory=[], domain_evidence=[],
        # ...
    )
```

This is not "no memory" — it's "no derived memory." Operational truth
(P1 tools) keeps working, so the app still functions. Use this when:

- F1 poisoning is detected and you need to quarantine memory while you
  investigate.
- A new memory adapter has a regression and you need to roll back fast.
- A compliance request requires you to disable derived storage for
  one tenant temporarily.

## Observability: what to log, what to alert on

### Log on every assembled bundle

```json
{
  "bundle_id": "bndl_...",
  "surface": "chat",
  "owner_scope": {...},
  "memory_count": 4,
  "evidence_count": 3,
  "live_fact_count": 2,
  "token_estimate": 5832,
  "compress_invoked": false,
  "compress_strategy": null,
  "subagent_count": 0,
  "elapsed_ms": 78
}
```

### Log on every `forget`

```json
{
  "memory_id": "mem_...",
  "actor": "user",
  "reason": "user_correction",
  "owner_scope": {...},
  "at": "2026-04-22T12:34:56Z"
}
```

### Alert on

| Signal | Threshold | Why |
|--------|-----------|-----|
| Cache hit ratio | <40% sustained 15min | Prefix invariance broken |
| Bundle p95 token count | >2× rolling 7-day | Bundle bloat (F2 risk) |
| Subagent dispatch rate | >2× rolling baseline | F2 escape hatch overused |
| `compress` invocation rate | >50% requests | Budgets too tight |
| `find_contradictions` returns >0 rate | >5× baseline | Ingest pipeline regression |
| Empty bundle rate | >1% | Adapter outage masquerading as success |
| Sub-agent `rejected_ids` non-empty | any | F1 detector — investigate |

### Trace

Every `assemble()` call should produce one span per runtime verb
(`select`, `compress`, `order`, etc.) so a slow request decomposes
without a debugger.

## Incident: F1 poisoning detected in prod

Sub-agent rejected_ids non-empty, or a memory cites a nonexistent
episode_id. Steps:

1. Disable the memory layer for the affected tenant via kill switch.
2. Pull the bundle id from the log; trace which memories it included.
3. For each suspect memory id, run:
   ```sql
   SELECT id, source_episode_id, source, inferred, confidence,
          created_at, supersedes_id
   FROM learned_memory WHERE id = '...';
   SELECT * FROM episode_log WHERE id = (
     SELECT source_episode_id FROM learned_memory WHERE id = '...'
   );
   ```
4. If the episode is missing or doesn't substantiate the memory:
   `forget` the memory with `reason="poisoning_incident_<ticket>"`.
5. Re-enable the memory layer.
6. Add a regression case to your eval suite that catches the same
   poisoning mode.

## Incident: memory adapter throwing on every `recall`

Most likely an adapter-level issue (DB pool, vendor outage). Steps:

1. Kill switch ON for affected scope. App degrades to live_facts only.
2. Verify operational layer (P1 tools) still healthy — they are
   independent and should be fine.
3. Diagnose adapter: connection pool exhausted, vendor 5xx rate, etc.
4. If vendor outage: switch `UnionMemoryStore(primary=...)` to the
   secondary store via config.
5. Once primary is healthy, mirror back any writes that happened
   during the cutover (use the episode log as the source of truth).
6. Kill switch OFF.

The whole point of the Protocol abstraction is that step 4 is a
config change, not a code change.

## Backups and retention

| Table | Backup | Retention |
|-------|--------|-----------|
| `episode_log` | Daily, encrypted, off-region | Forever (or per-tenant policy) |
| `learned_memory` | Daily | Forever |
| `knowledge_source` | Daily | Until source is removed |
| `knowledge_chunk` | Skip (re-embeddable from sources) | Match source |

The episode log is the one table you cannot lose. Memory is
reconstructable from it via the backfill recipe above; chunks are
reconstructable from sources. Episode loss is data loss.
