# CDC And Schema Governance

Use this reference when the user is building CDC pipelines or asking about schema evolution and registry policy.

## CDC Default Model

Prefer log-based CDC over trigger-based CDC when the source system supports it.

Why:

- Lower write-path overhead on the source
- More complete ordering and delete visibility
- Better fit for replay and catch-up workflows

## CDC Design Checklist

Confirm these before launch:

- Source log retention is long enough for connector lag and recovery
- Snapshot mode is chosen intentionally
- Delete handling is explicit
- Primary keys or stable business keys exist for downstream upserts
- Downstream consumers understand before/after semantics where applicable
- Schema changes are versioned and tested

## Snapshot Strategy

### Initial Snapshot

Use when:

- The sink needs a complete starting state
- Historical rows matter, not just future changes

Guardrails:

- Plan source load impact
- Define the cutover point from snapshot to streaming
- Verify duplicate handling during overlap

### Incremental Snapshot Or Backfill

Use when:

- Large tables make one-time snapshots too risky
- You need staged catch-up or rehydration

Guardrails:

- Bound the backfill by key or time range
- Track progress explicitly
- Keep replay and CDC streams consistent

## Delete Semantics

Do not assume every downstream consumer interprets deletes the same way.

Choose one of:

- Tombstone and compaction semantics
- Soft-delete flag
- Hard delete at sink
- Separate delete stream for downstream consumers

Document the choice in the topic contract.

## Schema Registry Policy

Use registry-backed schemas for long-lived or shared topics.

Practical defaults:

- Backward-compatible evolution for most consumer-facing event topics
- Stronger compatibility rules for high-risk shared contracts
- Pre-deploy compatibility checks in CI for producer changes

Prefer explicit owners and review paths for:

- Removing fields
- Changing meaning without changing field names
- Reusing topics for new business semantics

## CDC-Specific Failure Modes

Watch for:

- Source failover breaking connector offsets or privileges
- Tombstones being dropped by downstream transforms
- Snapshot overlap causing duplicate upserts
- Schema history corruption or registry drift
- Downstream sinks that cannot represent deletes or nullability correctly
