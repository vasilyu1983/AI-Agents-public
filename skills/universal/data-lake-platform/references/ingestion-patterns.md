# Data Ingestion Patterns

Choose ingestion around replay safety, delete handling, and operational ownership — not setup convenience. Code templates: [dlt](../assets/ingestion/dlt/template-dlt-pipeline.md), [Airbyte](../assets/ingestion/airbyte/template-airbyte-connection.md), [incremental loading](../assets/cross-platform/template-incremental-loading.md). Kafka/Flink stream semantics: `data-streaming` skill.

## Tool Selection

| Need | Default | Watch-outs |
|------|---------|------------|
| Durable CDC log for several consumers, replay from the log | Debezium + Kafka | Highest platform complexity; replication-slot and topic-retention management |
| Code-first ingestion owned by a Python team | dlt | You own runtime, retries, and connector logic |
| Broad connector catalog, UI-driven operations | Airbyte | Verify each connector's CDC and delete semantics; connector upgrades are operational work |
| Streaming-first CDC into mutable tables (Paimon/Hudi) | Flink CDC | Needs checkpoint/savepoint discipline and idempotent sinks |
| Small system, low-frequency, few mutations | Batch incremental or full refresh | Weakest freshness and delete semantics |

Prefer one ingestion standard per team unless a second path solves a named constraint.

## Incremental Strategy Rules

| Strategy | Use when | Silent failure it causes |
|----------|----------|--------------------------|
| Timestamp cursor (`updated_at`) + merge on key | Source has a reliable, indexed update timestamp | Misses hard deletes; misses rows committed late with an older timestamp (long transactions, clock skew) — re-read a lookback window and let the merge dedup |
| Monotonic ID + append | Immutable, insert-only data | Misses updates; sequence values can commit out of order, so a row with a lower ID can appear after the cursor passed it |
| API cursor/page token | Source exposes a change feed or cursor | Cursor expiry forces a full resync; persist the cursor only after the load commits |
| Full refresh (replace) | Small tables, or as a periodic delete-reconciliation pass | Cost grows with table size; readers can see an empty or partial table unless the swap is atomic |
| Log-based CDC | Deletes and every intermediate change matter | Operational weight (slots, offsets, schema history) |

Rules:

- The initial cursor value is a parameter (backfill start), never a hard-coded date in code.
- Ties at the cursor boundary: read `>=` the last value and dedup on the primary key, or rows sharing the boundary timestamp are dropped.
- Hard deletes are invisible to query-based incremental loads. Choose one: log-based CDC, a source soft-delete column mapped to a hard-delete hint at the destination, or a periodic full-key reconciliation.
- Treat cursors, checkpoints, and offsets as production state: back them up, and advance them only after the destination commit.

## Log-Based CDC Rules

- **Replication slots** (PostgreSQL) retain WAL until the consumer confirms it. A stopped connector keeps growing WAL on the source until the disk fills — alert on slot lag and have a drop-slot runbook.
- **Bootstrap**: initial snapshot + stream handoff must be consistent; verify row counts per table after the snapshot phase.
- **Deletes** arrive as delete events plus Kafka tombstones for compacted topics; the lake sink must turn them into row deletes, not ignore them.
- **Ordering**: apply changes per key in source-commit order (LSN/SCN/binlog position), not by event timestamp.
- **Schema changes**: define the policy (additive only, reviewed widening, contract-gated) before launch; a type change upstream can stall the connector or the sink.
- **Flink CDC** additionally needs a checkpoint/savepoint policy, sink idempotency, and a bootstrap/backfill plan.

## AI-Generated Connectors

Treat generated ingestion code as untrusted until it passes replay, backfill, and delete-handling tests. Review pagination, cursor logic, retry behavior, and auth by hand; test with small datasets and known edge cases (empty page, duplicate boundary rows, deleted rows).

## Before Rollout — Answer All Five

1. What is the replay source of truth: raw files, Kafka log, source database, or snapshots?
2. How are deletes represented and propagated?
3. What is the schema-change policy?
4. What is the bootstrap and backfill path?
5. What is the lag SLO, and what monitors it?
