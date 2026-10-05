# Apache Hudi Table Template

Use when choosing a Hudi table type, record key, ordering field, index, and write operation, or when tuning compaction, cleaning, and incremental reads.

Defaults, payload and merge-mode semantics, and the available index types have changed across Hudi releases. For what your release does, use [Version and support lookup](../../../SKILL.md#version-and-support-lookup).

## Table type: copy-on-write vs merge-on-read

| | Copy-on-write (CoW) | Merge-on-read (MoR) |
|---|---|---|
| Update cost | Rewrites each touched base file | Appends to log files |
| Read cost | Base files only | A snapshot query merges the logs; a read-optimized query reads base files only (stale until compaction) |
| Pick when | Read-heavy, batch updates, simple readers | High-frequency upserts or CDC, streaming ingest that needs low write latency |

- MoR is cheaper only if compaction keeps up. When compaction lags, snapshot reads slow down and log files pile up.
- Consumers of the read-optimized view see data only up to the last compaction. Document this, or it will be reported as "missing rows".

## Keys, ordering, and deletes

- **Record key:** the natural or business key, and composite keys are allowed. Not a generated UUID, because then every replay inserts a new row.
- **Ordering (precombine) field:** a monotonically increasing *source* version, such as a CDC log sequence number or a source commit timestamp. Never use ingestion time, because a replayed older event then wins.
- **Check the merge semantics.** Depending on the configured payload or merge mode, the ordering field either only deduplicates within the incoming batch (commit-time ordering) or is also compared against the stored record (event-time ordering). With commit-time semantics, a late-arriving older event overwrites newer state.
- **Partition path must be immutable per key.** If a record's partition value can change (for example, partitioning by status or `updated_at`), a non-global index writes a second copy in the new partition, which creates duplicates. Partition by an immutable attribute such as the creation date, or use a global index and accept the lookup cost across all partitions.
- **Deletes:** use the `delete` operation with key and partition-path fields. For CDC streams where upserts and deletes arrive in the same batch, use a `_hoodie_is_deleted = true` column instead.

## Write operation

| Operation | Use for | Trap |
|-----------|---------|------|
| `upsert` | Incremental and CDC loads (default) | Needs an index lookup per batch, so cost grows with the table and the key spread |
| `insert` | Append-only data whose keys never repeat | Skips the index lookup, so repeated keys become duplicates |
| `bulk_insert` | Initial load or large backfill | No small-file handling or deduplication by default; follow it with clustering |
| `insert_overwrite` | Idempotent partition replacement | Replaces every partition the batch touches |
| `delete` | Key-only frames | Needs the same key and partition-path fields as the writes |

**Index choice** follows update locality. Bloom-style indexes are cheap when updates hit recent, time-ordered keys. When updates hit random keys across the whole table (UUID keys, dimension-style updates), bloom lookups touch many files; consider a simple, bucket, or record-level index if your release provides one.

## Minimal writer config (the settings are the lesson)

```python
hudi_options = {
    "hoodie.table.name": "events",
    "hoodie.datasource.write.table.type": "MERGE_ON_READ",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.recordkey.field": "event_id",
    "hoodie.datasource.write.precombine.field": "source_lsn",       # source ordering, not ingest time
    "hoodie.datasource.write.partitionpath.field": "created_date",  # immutable per key
    "hoodie.compact.inline.max.delta.commits": "5",                  # freshness of base files vs write amplification
    "hoodie.cleaner.commits.retained": "<derived from incremental-consumer lag>",
}
```

## Compaction, clustering, cleaning

- **MoR compaction.** Inline compaction is simple but adds latency to every triggering write. Async compaction runs as a separate job and is required when write latency matters, as in streaming. Fewer delta commits per compaction give fresher base files at the cost of more rewriting.
- **Clustering.** Clustering rewrites small files from `insert` and `bulk_insert` and sorts by filter columns. Run it async, and start near the table's target file size.
- **Cleaning.** The cleaner keeps file versions for the last N commits (`hoodie.cleaner.commits.retained`). Incremental queries (`hoodie.datasource.query.type = incremental` from a begin instant) and time travel need the file versions of the commits they read. A consumer that falls behind the retained range misses changes or fails, depending on the release.
  - Size the retention as at least commits per hour × the slowest consumer's maximum lag in hours.
  - Alert when a consumer's checkpointed instant is older than the earliest retained commit.
  - Timeline archival settings (`hoodie.keep.min.commits`) must stay above the cleaner retention.
- **Incremental consumers** store the last processed instant and resume from it. Use the Hudi instant as the checkpoint, not the wall-clock time.

## Rollback

- Failed or inflight writes are rolled back automatically by the next writer. Do not delete `.hoodie/` files by hand.
- For a logical rollback, create a savepoint before a risky backfill and restore to it if needed. Savepointed file versions are exempt from cleaning. The CLI and SQL procedure names vary by release (use the version lookup).

## Verify

- [ ] No lingering `requested` or `inflight` instants after jobs finish (the timeline or the `show_commits` procedure).
- [ ] No duplicate keys: `SELECT event_id, count(*) FROM events GROUP BY 1 HAVING count(*) > 1` returns zero rows. With a non-global index, a key that appears in two partitions means its partition value changed (see Keys).
- [ ] MoR: the gap between snapshot and read-optimized row counts stays bounded, which shows compaction is keeping up.
- [ ] Each incremental consumer's checkpoint instant is within the cleaner's retained range.
