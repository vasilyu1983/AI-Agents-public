# ClickHouse Ingestion

Use when choosing how data gets into ClickHouse and making loads idempotent. Loader-side patterns (dlt, Airbyte) are in [assets/ingestion/](../../ingestion/); cursor and late-data rules in [template-incremental-loading.md](../../cross-platform/template-incremental-loading.md).

## Choose the Path

| Source shape | Default | Why / when not |
|--------------|---------|----------------|
| Files in object storage (Parquet) | `INSERT INTO t SELECT ... FROM s3(...)` (or `s3Cluster` to spread across nodes) | Server-side, parallel, no client hop. Keep credentials in named collections or instance roles, never inline in SQL that ends up in `query_log` |
| Batch pipeline (dlt, Spark, custom loader) | Client batches through the native or HTTP interface | Loader controls batch size and retries |
| Many small writers (apps, agents, per-event producers) | Async inserts with `wait_for_async_insert = 1` | The server buffers and batches, so parts stay few. See the durability note below |
| Kafka topic | Kafka table engine + MV, or an external consumer (Kafka Connect sink, loader) | Engine is simplest; an external consumer gives better error handling and back-pressure control |
| Legacy `Buffer` table | Avoid for new designs | Data sits in RAM: lost on crash, not replicated, invisible to some queries. Async inserts replace it |

## Part Count and Insert Batching

Every `INSERT` creates at least one new part **per partition it touches**. Background merges must keep up, or inserts are delayed and then rejected ("Too many parts"; limits in `system.merge_tree_settings`).

- Batch client inserts. ClickHouse guidance is at least ~1,000 rows per insert, ideally 10k-100k, and about one insert per second per table rather than many tiny ones. Tune by watching active parts per partition, not by hitting a row number.
- One batch should touch few partitions. A batch spread across 50 daily partitions creates 50 parts. `max_partitions_per_insert_block` rejects extreme cases on purpose; sort or split batches by partition instead of raising it.
- Backfills spanning many months: load one partition per statement, or through a staging table plus `REPLACE PARTITION`.
- More MVs on the target means more parts per insert (one per MV target), so batch harder.

## Async Inserts: Durability Trade-off

- `async_insert = 1, wait_for_async_insert = 1`: the client is acknowledged after the buffered batch is flushed to a part. This is the safe default.
- `wait_for_async_insert = 0`: fire-and-forget. The client gets success before the data is written; a server crash or a type error in the flush loses rows **silently**. Use it only for data you can lose (sampled telemetry).
- Deduplication of retried async inserts is off by default (`async_insert_deduplicate`). Retries can therefore duplicate rows unless you enable it or dedup downstream.

## Idempotent Retries

Replicated tables deduplicate an inserted block that is **byte-identical** (same rows, same order, same batch boundaries) to one of the recent blocks (`replicated_deduplication_window`). Non-replicated `MergeTree` needs `non_replicated_deduplication_window > 0` for the same behavior. Therefore:

- Retry the exact same batch after a timeout, never a re-assembled one. Or set `insert_deduplication_token` to a deterministic batch id, e.g. `<pipeline>:<source_file>:<offset_range>`.
- Block dedup covers retries only. For replayed or overlapping source data, dedup by key downstream with `ReplacingMergeTree` or `argMax`.

## Kafka Table Engine

```sql
CREATE TABLE ingest.events_queue ( ... )
ENGINE = Kafka
SETTINGS kafka_broker_list = '<brokers>', kafka_topic_list = 'events',
         kafka_group_name = 'ch_events', kafka_format = 'JSONEachRow',
         kafka_num_consumers = 1,            -- raise up to the topic's partition count, never above it
         kafka_handle_error_mode = 'stream'; -- bad messages go to _error instead of stalling the consumer

CREATE MATERIALIZED VIEW ingest.events_consumer TO silver.events AS
SELECT * FROM ingest.events_queue WHERE length(_error) = 0;  -- virtual _error is not part of *
```

- Delivery is **at-least-once**: rebalances and restarts can redeliver, so the target needs key-based dedup.
- Route `_error` rows to a dead-letter table with a second MV; without error handling, one malformed message stops the whole consumer.
- To change the schema: `DETACH` the consumer MV (consumption stops, offsets hold), alter the queue table, target and MV, then `ATTACH`.
- Consumer lag is not in ClickHouse tables by default. Monitor it on the Kafka side (consumer group lag) and alert.

## Incremental Loads Inside ClickHouse (Bronze to Silver)

- A `> max(loaded_at)` watermark drops rows that share the boundary timestamp and rows that arrive late. Reprocess an overlap window (`>= watermark - <lateness allowance>`) into a `ReplacingMergeTree` keyed on the business key, so reprocessing is idempotent.
- Store the watermark only after the insert succeeds. Advance it to the max of what was actually loaded, not to `now()`, which loses rows still in flight.

## Verify

- Active parts per partition stay flat during peak load (query in [template-clickhouse-optimization.md](template-clickhouse-optimization.md#part-count-and-merges)).
- `system.query_log` (`query_kind = 'Insert'`, `exception != ''`) is empty or alerting; async-insert flush errors appear in `system.asynchronous_insert_log` if enabled.
- Source row count per load window equals the target count after dedup (`uniqExact(key)` or `FINAL` count).
- Kill a loader mid-batch and retry it: the target count does not change.
