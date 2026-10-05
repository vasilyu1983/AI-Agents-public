# dlt Database Source Template

Use when replicating tables from a relational or document database with dlt. Pipeline identity and dispositions: [template-dlt-pipeline.md](template-dlt-pipeline.md). Cursor, merge and delete rules: [template-dlt-incremental.md](template-dlt-incremental.md).

## Choose the Replication Method First

| Need | Method | Why |
|---|---|---|
| Small tables, or no reliable cursor | `sql_table` / `sql_database` with `replace` | Simple and correct; cost grows with table size |
| Large tables, deletes out of scope or soft-deleted | `sql_table` + incremental cursor + `merge` | Reads only changed rows |
| Hard deletes must propagate, or no trustworthy `updated_at` | CDC from the database log | A cursor query cannot see a row that no longer exists |

For CDC: dlt has a Postgres logical-replication source (check the dlt sources catalog for its current scope); for other engines or streaming latency, use Debezium via the `data-streaming` skill. Engine-agnostic comparison: [template-incremental-loading.md](../../cross-platform/template-incremental-loading.md).

## Skeleton: Incremental Table

```python
from dlt.sources.sql_database import sql_table

orders = sql_table(
    credentials=dlt.secrets["sources.sql_database.credentials"],
    table="orders",
    backend="pyarrow",                     # columnar: much faster than row-by-row for big tables
    chunk_size=50_000,                     # rows per fetch; tune by measuring memory
    reflection_level="full_with_precision",  # keep decimal precision and string lengths
    incremental=dlt.sources.incremental("updated_at", initial_value="<history_start>"),
)
orders.apply_hints(primary_key="order_id", write_disposition="merge")
```

## Extraction Rules

- **Backend**: the default SQLAlchemy backend yields Python rows and is slow on large tables. Use a columnar backend (`pyarrow`, `pandas`, or `connectorx`) for bulk loads; check type mapping for decimals, timezones, and JSON on the first run.
- **Precision**: without precision reflection, `NUMERIC(18,4)` money columns can land with default precision. Use `full_with_precision` for financial or exact numeric data.
- **Filter at the source**: restrict rows with `query_adapter_callback` and drop columns (for example PII not needed downstream) with `table_adapter_callback`, so they never leave the database.
- **Cursor column needs an index** at the source; otherwise every incremental run is a full table scan on production.
- **No hand-written `LIMIT/OFFSET` loops**: offset scans slow down as the offset grows and return unstable pages without `ORDER BY`. The built-in backends stream with `chunk_size`; if you must page manually, use keyset paging (`WHERE id > :last ORDER BY id LIMIT :n`).
- **No f-string SQL** with cursor values: use bound parameters or the built-in incremental.
- **Joins across databases**: do not join in Python inside a resource. Load each table raw and join in the transformation layer (`data-analytics-engineering` skill), where the join is testable and re-runnable.

## Protect the Source Database

- Read from a replica where one exists. Long snapshot reads on a primary hold back vacuum/purge and can bloat tables; on a replica they can be cancelled by replication conflicts, so size `chunk_size` and run windows to keep each query short.
- Use a read-only database user limited to the replicated schemas.
- Cap concurrent table extraction to what the source can serve; parallel full scans of large tables compete with production traffic.
- Schedule initial full loads outside peak hours and in chunks (see [backfill](template-dlt-incremental.md#backfill-and-replay)).

## Document Databases (MongoDB and similar)

- Documents with varying shapes produce variant columns and child tables; set `schema_contract` and `max_table_nesting` before the first load (see [schema traps](template-dlt-pipeline.md#schema-evolution-traps)).
- Convert non-JSON types (ObjectId, Decimal128, binary) explicitly and consistently, or the same field lands as different types.
- Incremental on a field requires that field to be indexed and set on every write; `_id` order is insertion order only for default ObjectIds and never reflects updates.

## Verify

- [ ] Per-table source count equals destination count for the loaded range.
- [ ] Spot-check numeric precision, timezone, and null handling on a few columns against the source.
- [ ] Source query plan for the incremental filter uses the cursor index (`EXPLAIN`).
- [ ] If deletes are in scope: delete a test row and confirm it disappears or is flagged after the next run.
