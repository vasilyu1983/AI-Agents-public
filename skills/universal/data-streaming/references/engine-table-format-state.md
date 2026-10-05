# Engine and Table-Format State

---
last_validated: 2026-07-11
---

Use sources.json entries for URLs.

## Apache Iceberg v3

Spec is ratified. v3 additions:

- **Deletion vectors** — efficient row-level deletes without full file rewrites
- **Row lineage** — `_row_id` and `_last_updated_sequence_number` system columns for native CDC
- **Variant/semi-structured data** — native support in the spec
- **Default column values, geometry/geography types, nanosecond timestamps, multi-argument partition transforms**
- **Native encryption** — foundations added (not full coverage yet)

**Per-engine v3 status: look it up, do not copy it.** Vendor status moves from preview to GA faster than this file changes. For each engine in the stack, check the vendor's current docs or release notes for three separate things: can it read v3 tables, can it write them, and which maintenance and row-level operations (updates, deletes, `OPTIMIZE`/compaction) work on v3. Record the answer with the date you checked in the design doc, not here.

- Snowflake, Databricks, AWS: check the vendor's Iceberg documentation and release notes.
- Trino: check the Iceberg connector page for the v3 support statement and the list of unsupported operations.

**Engine gap to verify before committing:** in a multi-engine stack (for example Snowflake or Databricks plus Trino for federated queries), confirm each engine's v3 read/write support before relying on v3-only features like deletion vectors or row lineage. Writing v3 tables that a non-v3 engine must also read is a common rollout failure mode. "The spec feature is ratified" does not mean "this client supports it".

Spec: https://iceberg.apache.org/spec/

## Iceberg Streaming Ingestion Pattern

Standard stack: Kafka -> Flink (Dynamic Iceberg Sink) -> Iceberg table -> compaction job.

```
# Illustrative starting point, not from the Flink blog — tune on the real workload
execution.checkpointing.interval = 5 min   # drives commit frequency
write.target-file-size-bytes = 536870912   # Iceberg table default (512 MB); smaller values mean more files
```

- With one commit opportunity per checkpoint and all else equal, a 5-minute interval yields 80% fewer commit opportunities than a 1-minute interval. Treat file-count reduction as a workload measurement because partitions, writers, rollover, traffic shape, and compaction also determine output files.
- Always run a compaction job on cold partitions; skip the hot (current) partition.
- Dynamic Iceberg Sink handles multi-table writes and automatic schema evolution.
- Flink's checkpoint mechanism provides exactly-once commits to Iceberg; downstream exactly-once still depends on how readers and later sinks behave.

## Kafka KIP-1150 — Diskless Topics

An accepted **umbrella/motivational KIP** for storage-compute separation: data flows directly to object storage, bypassing broker-local disks. Implementation proceeds through sub-KIPs (for example KIP-1163). Check the KIP page and the Kafka release notes for which sub-KIPs have shipped before treating any of it as production-ready upstream. Commercial and OSS Kafka-compatible services already implement this architecture; check their current docs for durability and latency trade-offs.

## Kafka and Flink Versions

This file keeps no version table. Look up the target release, patch regressions, and feature status (for example KIP-932 share groups, Flink experimental features) in the Apache Kafka and Apache Flink release announcements. Kafka 4.0 removed ZooKeeper and 4.x is KRaft-only. Flink 2.0 removed the legacy `SinkFunction` and `AssignerWith*Watermarks` APIs; a 1.x upgrade needs a tested savepoint restore under the [Flink upgrade guide](https://nightlies.apache.org/flink/flink-docs-release-2.0/docs/ops/upgrading/), with compatible state and operator IDs.

## Apache Paimon

Streaming lakehouse table format under the Apache umbrella. Designed for streaming-first mutations (upserts, CDC merge) without full-file rewrites. Check the Flink and Paimon docs for the current integration. Always fetch current docs at https://paimon.apache.org/ — version numbers and benchmarks not fixed here.
