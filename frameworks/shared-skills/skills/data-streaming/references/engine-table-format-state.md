# Engine and Table-Format State

---
last_validated: 2026-07-11
---

Use sources.json entries for URLs.

## Apache Iceberg v3

Spec is ratified. v3 additions:

- **Deletion vectors** — efficient row-level deletes without full file rewrites (up to ~10x faster DML)
- **Row lineage** — `_row_id` and `_last_updated_sequence_number` system columns for native CDC
- **Variant/semi-structured data** — native support in the spec
- **Default column values, geometry/geography types, nanosecond timestamps, multi-argument partition transforms**
- **Native encryption** — foundations added (not full coverage yet)

Platform GA status (July 2026): Snowflake GA (May 7, 2026); Databricks Runtime 18.0+ GA across AWS/Azure/GCP with Unity Catalog. AWS support announced.

**Engine gap to verify before committing:** Trino is not v3-ready as of mid-2026. In a multi-engine stack (e.g., Snowflake/Databricks plus Trino for federated queries), confirm each engine's v3 read/write support before relying on v3-only features like deletion vectors or row lineage — writing v3 tables that a non-v3 engine must also read is a common rollout failure mode.

Spec: https://iceberg.apache.org/spec/

## Iceberg Streaming Ingestion Pattern (June 2026)

Standard stack: Kafka -> Flink (Dynamic Iceberg Sink) -> Iceberg table -> compaction job.

```
checkpoint.interval = 5 min           # drives commit/file frequency
write.target-file-size-bytes = 128MB  # reduces small-file overhead
write.fanout.enabled = true           # unordered writes across partitions
```

- 5-minute checkpoint produces ~90% fewer small files vs 1-minute intervals.
- Always run a compaction job on cold partitions; skip the hot (current) partition.
- Dynamic Iceberg Sink handles multi-table writes and automatic schema evolution.
- Flink's checkpoint mechanism provides exactly-once delivery to Iceberg.

## Kafka KIP-1150 — Diskless Topics

Accepted March 2, 2026. This is an **umbrella/motivational KIP** for storage-compute separation: data flows direct to object storage, bypassing broker-local disks. Implementation proceeds via sub-KIPs (e.g. KIP-1163). **Not yet production-ready upstream.** WarpStream and AutoMQ implement this architecture today as commercial/OSS alternatives. Treat KIP-1150 as design intent for self-managed Kafka tiered-storage roadmap.

## Kafka Version State (July 2026)

| Version | Released | Key change |
|---|---|---|
| 4.0 | March 2025 | ZooKeeper removed; KRaft-only; KIP-848 consumer rebalance |
| 4.2 | Feb 2026 | KIP-932 (share groups / queues) GA |
| 4.3.0 | May 22 2026 | 25 KIPs, 600+ commits |
| 4.3.1 | Jun 25 2026 | Patch release; ~15 fixes incl. a critical Kafka Streams RocksDB native memory leak — latest stable |

KRaft controller quorum sizing differs from ZooKeeper ensemble sizing. Migrate non-production before cutting over production. Kafka Streams users on 4.3.0 should upgrade to 4.3.1 promptly.

## Flink Version State (July 2026)

| Version | Released | Key features |
|---|---|---|
| 2.3.0 | Jun 25 2026 | Latest stable; changelog conversion SQL operators (`FROM_CHANGELOG`/`TO_CHANGELOG`), redesigned native S3 filesystem on AWS SDK v2, adaptive partition selection for backpressure, ordered late-data handling for Process Table Functions |
| 2.2.0 | Dec 2025 | Real-time data + AI integrations, Paimon native integration |
| 2.0.2 | May 11 2026 | Latest 2.0.x maintenance; 34 fixes; disaggregated state, async execution, Materialized Tables |

Savepoints from Flink 1.x are not forward-compatible with 2.x state backends without explicit migration. Audit savepoints, review connector compatibility, and validate SQL Gateway behavior before upgrading.

## Apache Paimon

Streaming lakehouse table format under the Apache umbrella. Designed for streaming-first mutations (upserts, CDC merge) without full-file rewrites. Integrated natively in Flink 2.2.0. Always fetch current docs at https://paimon.apache.org/ — version numbers and benchmarks not fixed here.
