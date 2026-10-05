# Indexing Strategy

Use this file when choosing index types and index rules for a schema's known access patterns. For tuning indexes against an existing query plan, use [data-sql-optimization](../../data-sql-optimization/SKILL.md).

## Access Pattern to Index Type

| Access Pattern | Index Type | Example |
|---------------|------------|---------|
| Exact lookup | B-tree (default) | `WHERE email = ?` |
| Range queries | B-tree | `WHERE created_at > ?` |
| Full-text search | GIN + tsvector (PG) / FULLTEXT (MySQL) | `WHERE search @@ to_tsquery(?)` |
| JSON field queries | GIN (PG) | `WHERE metadata @> '{"key": "val"}'` |
| Geospatial | GiST or SP-GiST | `WHERE ST_DWithin(location, ?, 1000)` |
| Composite lookups | Multi-column B-tree | `WHERE tenant_id = ? AND status = ?` |
| Uniqueness enforcement | Unique index | `CREATE UNIQUE INDEX ON users(email)` |
| Partial indexing | Filtered index | `WHERE deleted_at IS NULL` |
| Large append-only / naturally ordered columns | BRIN (PG) | `WHERE created_at BETWEEN ? AND ?` on a table physically clustered by insert order (time-series, event logs) |

## Indexing Rules

- [ ] Index columns that appear in WHERE, JOIN ON, and ORDER BY
- [ ] In composite indexes, put equality-filter columns first, then sort, then range (Equality → Sort → Range), and favor prefix reuse across the queries that will hit the index — do not order by cardinality; PostgreSQL 18's B-tree skip scan also changes the leading-column calculus (see [data-sql-optimization/references/index-patterns.md](../../data-sql-optimization/references/index-patterns.md); MongoDB ESR in [references/nosql-modeling.md](nosql-modeling.md))
- [ ] Use partial indexes to exclude soft-deleted rows
- [ ] Monitor unused indexes and drop them (they slow writes)
- [ ] Prefer covering indexes for hot queries (include all SELECT columns)
- [ ] Reach for BRIN only when the column correlates with physical row order (e.g. an append-only `created_at`); BRIN is a lossy, block-range summary — a few bytes per range vs. a full B-tree entry per row — and degrades badly the moment the table is updated out of insertion order (e.g. `UPDATE`-heavy tables, or reordering from `VACUUM FULL`/`CLUSTER`)
- [ ] On PostgreSQL, keep `fillfactor` below 100 on frequently-`UPDATE`d tables (e.g. 90) so updates that don't touch indexed columns can use HOT (Heap-Only Tuple) updates — they skip index maintenance entirely and are the single biggest lever against index bloat on write-heavy tables
- [ ] Don't reach for GIN/GiST on a hunch — profile the actual query first; a well-designed B-tree composite index outperforms both for exact-match and range lookups, and GIN write overhead is real on high-churn `jsonb`/array columns
