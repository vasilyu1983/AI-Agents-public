# Parquet Optimization Template

Use when tuning Parquet writes (file and row-group size, compression, encoding, sort order) or diagnosing why predicate pushdown does not prune.

Under a table format (Iceberg, Delta, Hudi), set these through table properties and compact with the format's own tools. Hand-written Parquet files dropped into a table's directory are invisible or orphaned.

## Defaults

| Setting | Default | Reason |
|---------|---------|--------|
| File size | 128 MB–1 GB | Fewer files mean less listing, planning, and per-object request cost. Beyond about 1 GB, a single slow file stalls a task. |
| Row group | about 128 MB **of data** | The row group is the unit of parallel reading and of min/max pruning. Larger groups mean fewer footer entries but more writer memory. Smaller groups prune more finely but compress worse and bloat metadata. |
| Page size | about 1 MB | The pruning granularity when readers use the page index. |
| Compression | zstd at a low level | A better ratio than snappy at a usually similar decode speed for scan-heavy analytics. Use snappy or lz4 only when write or decode CPU is the proven bottleneck. Use higher zstd levels for cold, write-once data. gzip has no advantage over zstd. Compare codecs on one representative partition; ratios depend on data and sort order. |
| Statistics | On, plus the page index where the writer supports it | Pruning depends on them. |

## Units trap: row-group size

Row-group size units differ by writer:

- **PyArrow `row_group_size`:** rows.
- **DuckDB `ROW_GROUP_SIZE`:** rows.
- **Spark and parquet-mr `parquet.block.size`:** bytes.

Passing `128 * 1024 * 1024` to PyArrow asks for 134 million rows per group, which usually means one row group per file and no intra-file pruning or parallelism. Convert the byte target to rows using the measured average row size:

```python
import pyarrow.parquet as pq

md = pq.ParquetFile(sample_path).metadata
avg_row_bytes = sum(md.row_group(i).total_byte_size for i in range(md.num_row_groups)) / md.num_rows
rows_per_group = int(128 * 1024 * 1024 / avg_row_bytes)

pq.write_table(
    table, out_path,
    compression="zstd",
    row_group_size=rows_per_group,                # ROWS, not bytes
    use_dictionary=["event_type", "country"],     # low-cardinality columns only
    write_statistics=True,
)
```

## Sort order (the biggest pruning lever)

- Sort within each file by the leading filter column. Min/max statistics then span narrow, mostly non-overlapping ranges per row group, so readers skip most row groups.
- Secondary sort columns prune well only within runs of the first column. For several independent filter columns, use the table format's Z-order or clustering instead.
- A random order (UUID, hash) makes every row group's min/max span the whole domain, so nothing is skipped.
- Sorting also improves compression, because repeated values form runs that dictionary and RLE encode well.

## Encoding

- Writers dictionary-encode columns by default and fall back to plain encoding when a column chunk's dictionary exceeds the page limit. For high-cardinality columns (UUIDs, free text) this is wasted work, so restrict `use_dictionary` to the low-cardinality columns.
- In PyArrow, a non-dictionary `column_encoding` (for example `DELTA_BINARY_PACKED` for sorted integers and timestamps) applies only to columns that are not dictionary-encoded. With `use_dictionary=True`, PyArrow raises an error. Pass `use_dictionary` as a list (or `False`) that excludes those columns.

## Schema design

- **JSON in a string column defeats pruning and projection.** There are no useful statistics and the whole blob is read. Promote frequently filtered keys to typed columns.
- Use a `struct` for known fixed fields, because each leaf becomes its own column with statistics. Use a `map` only for sparse keys, and expect weak pruning on it.
- **Timestamps:** agree on one physical type and unit across writers (int64 micros vs legacy int96 vs nanos). Mismatched units or time-zone flags show up as shifted times or read errors in some engines.
- Use decimal, not float, for money.

## Raw Parquet datasets (no table format)

- Compact into a **new prefix**, then switch readers atomically, for example by swapping a view or pointer. Readers listing a directory mid-rewrite see old and new files together, which means duplicate rows.
- Hive-style directory partitioning rules are in [template-partitioning-strategy.md](../../cross-platform/template-partitioning-strategy.md).

## Pushdown checklist

- Filter a column against a literal of a compatible type. Wrapping the column in a function or cast (`CAST(ts AS DATE) = ...`, `lower(col) = ...`) disables statistics pruning in many engines.
- Project only the needed columns. `SELECT *` reads every column chunk.

## Verify

```python
import pyarrow.parquet as pq

md = pq.ParquetFile(path).metadata
j = next(k for k in range(md.num_columns) if md.row_group(0).column(k).path_in_schema == "user_id")
for i in range(md.num_row_groups):
    c = md.row_group(i).column(j)
    s = c.statistics
    print(i, md.row_group(i).num_rows, c.total_compressed_size, s.min if s else None, s.max if s else None)
```

- [ ] Files larger than the row-group target contain more than one row group, each near the target size.
- [ ] Min/max ranges of the leading filter column barely overlap across row groups. Heavy overlap means the data is unsorted and pruning will not work.
- [ ] Per-column `total_uncompressed_size / total_compressed_size` is plausible. A ratio near 1x marks a high-entropy column, which should not be dictionary-encoded.
- [ ] The engine's `EXPLAIN` or profile for a typical filter shows row groups or files skipped.
