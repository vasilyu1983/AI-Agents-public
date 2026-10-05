# Schema Evolution Template

Use when changing a lake or warehouse table's schema without breaking readers, or when choosing a pipeline's schema-contract mode.

Which type promotions and column defaults a given table-format spec version or engine supports: use [Version and support lookup](../../SKILL.md#version-and-support-lookup). Format-specific mechanics are in [Iceberg](../storage/iceberg/template-iceberg-table.md), [Delta](../storage/delta/template-delta-table.md#schema-changes-delta-specifics) and [ClickHouse optimization](../query-engines/clickhouse/template-clickhouse-optimization.md).

## Compatibility rules

Iceberg tracks columns by field ID. Delta tracks them by name unless column mapping is enabled, and then by ID. Raw Parquet and Hive-style tables, and most downstream SQL, resolve columns **by name**. Most breakages come from that difference.

| Change | Safe when | Breaks |
|--------|-----------|--------|
| Add a nullable column | Always; old files read as null | Positional consumers (`INSERT INTO t SELECT *`, CSV exports, fixed-width targets) |
| Add a required (NOT NULL) column | Only with a default for existing rows. Iceberg treats it as incompatible unless the spec and engine support column defaults. | Writers that do not send it |
| Rename | Iceberg; Delta with column mapping | Downstream SQL, views, and dashboards using the old name. In raw Parquet the renamed column reads as null for old files. Delta without column mapping rejects the rename. |
| Drop | Metadata-only in Iceberg and in Delta with mapping; the bytes stay until files are rewritten | Consumers that reference it. In Iceberg, re-adding the same name creates a **new** field ID, so the old data does not reappear. |
| Widen type | Iceberg spec promotions: int→long, float→double, decimal(P,S)→decimal(P',S) with P'>P. Delta: only with the type-widening feature, otherwise a rewrite. | Readers with a compiled schema (typed Avro or Protobuf consumers, strict DataFrame schemas). ClickHouse `MODIFY COLUMN` type changes rewrite parts as a mutation. |
| Narrow the type, change the type family, or change the decimal scale | Never in place | Everyone. Use expand/contract. |
| Required → optional | Safe for storage | Consumers that assume non-null (downstream NOT NULL constraints, primary keys) |
| Optional → required | Only after proving there are zero nulls, and only if the format allows it | Writers that still send nulls |
| Reorder columns | Iceberg and Delta resolve by ID or name | Positional consumers |

## Expand/contract: the default for any breaking change

1. **Expand:** add the new column (nullable) or a new table version next to the old one.
2. **Dual-write:** writers populate both the old and new columns.
3. **Backfill** the history into the new column one partition at a time, idempotently, using the format's atomic partition replace: Iceberg overwrite or `overwritePartitions()`, Delta `replaceWhere`, ClickHouse `REPLACE PARTITION ... FROM staging`.
4. **Switch readers.** Use query logs or lineage to find who still reads the old column.
5. **Contract:** drop the old column after the grace period, once reads have fallen to zero.

Rollback: until step 5, repoint readers and nothing is lost. After step 5, recover from time travel only within the snapshot or VACUUM retention.

In ClickHouse, avoid `ALTER TABLE ... UPDATE` backfills on large tables; they are asynchronous mutations that rewrite whole parts. Instead, add the column with a `DEFAULT` expression, which old parts compute at read time, then run `MATERIALIZE COLUMN` off-peak, or backfill via `REPLACE PARTITION` from a recomputed staging table.

## Ingestion: schema drift contracts

Decide per layer and make the choice explicit:

| Layer | Mode | Effect |
|-------|------|--------|
| Bronze / raw | evolve | New columns are added automatically; nothing is lost |
| Silver / gold, or any table with external consumers | freeze | A load with new or changed columns fails, so the change becomes a reviewed migration |
| Untrusted sources | discard_value / discard_row | Unknown columns, or rows containing them, are dropped |

```python
@dlt.resource(schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"})
def orders(): ...
```

- dlt's default is evolve. When a source field flips type (int to string), dlt creates a variant column (`<field>__v_text`) rather than failing, so alert on new variant columns. See [template-dlt-pipeline.md](../ingestion/dlt/template-dlt-pipeline.md).
- Spark and Delta `mergeSchema` on write is the "evolve" mode; enable it only on bronze.

## Transformation handoff

For dbt or SQLMesh incremental-model changes and historical restatements, use `data-analytics-engineering` (`references/transformation-patterns.md`). Record the model owner's backfill and consumer checks in this table migration before switching readers.

## Change record

Keep one versioned, reviewed migration file per change, applied in order. The table format's own history (Iceberg `metadata.schemas`, Delta `DESCRIBE HISTORY`) is the audit trail, so no separate schema-registry table is needed.

## Verify

- [ ] Before: list the consumers of every affected column from query logs or lineage.
- [ ] After: read a partition written **before** the change with every reader engine.
- [ ] The new column's null rate on old data matches expectations (all null until backfilled; then the expected rate).
- [ ] The backfill left row counts per partition unchanged.
- [ ] Dropped or renamed columns have zero reads in the query log before the contract step.
