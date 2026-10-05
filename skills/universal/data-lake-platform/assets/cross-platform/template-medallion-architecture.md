# Medallion Architecture Template

Use when laying out bronze/silver/gold tables for a new domain or source. Layer contracts and rationale: [architecture-patterns.md](../../references/architecture-patterns.md#medallion-bronze--silver--gold). Transformation code (dbt/SQLMesh models): `data-analytics-engineering`.

## Layout

```text
<warehouse>/
├── bronze/<source>/<entity>     # append-only, as received + ingestion metadata
├── silver/stg_<entity>          # typed, deduplicated, validated
└── gold/{fct_,dim_,mart_}<name> # business-aligned, rebuildable from silver
```

## Per-Layer Decisions

| Decision | Bronze | Silver | Gold |
|----------|--------|--------|------|
| Write mode | Append only | Idempotent merge on business key, or overwrite by partition | Full rebuild or incremental by time range |
| Partition by | Ingestion date (late data never rewrites old partitions) | Event date | Query grain (usually date) |
| Required columns | `_ingested_at`, `_source`, `_batch_id`/load id, raw payload | Business key, ordering column (`updated_at`), `_loaded_at` | Grain columns declared |
| Retention | Replay window: long enough to rebuild silver | Months-years | Per consumer |
| Quality gate on exit | Schema present, load id not null, row count > 0 | Key unique, required fields not null, types valid, quarantine rejects | Grain unique, reconciles to silver totals |

## Silver Dedup Rule

Keep one row per business key: the highest value of the source ordering column, tie-broken by ingestion time.

```sql
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY updated_at DESC, _ingested_at DESC) = 1
```

Ordering by ingestion time alone keeps the wrong version when an older change is re-delivered late (replays, CDC restarts).

## Traps

- Parsing JSON in bronze: a parse failure then loses the raw record. Parse in silver; route unparseable rows to a quarantine table with the error.
- Gold that cannot be rebuilt from silver (manual fixes, one-off loads): every fix goes through a versioned pipeline.
- Bronze TTL shorter than the silver rebuild window: you lose the ability to replay after a logic bug.
- Business segmentation thresholds (e.g. "VIP = 10+ orders") hard-coded in gold SQL: define them once in the semantic layer.

## Verify

- [ ] Rerunning any layer for the same interval yields identical row counts and checksums.
- [ ] Silver key uniqueness holds after a replay of the last N bronze loads.
- [ ] Gold totals reconcile to silver for a sampled date range.
