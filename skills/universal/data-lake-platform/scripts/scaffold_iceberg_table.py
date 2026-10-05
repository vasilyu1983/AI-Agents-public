#!/usr/bin/env python3
"""
scaffold_iceberg_table.py — Stdlib-only Iceberg CREATE TABLE DDL generator.

Emits a copy-pasteable CREATE TABLE ... USING ICEBERG statement with partition
spec and TBLPROPERTIES pre-configured for production defaults, plus a checklist
of post-creation tasks.

USAGE
-----
  python scaffold_iceberg_table.py \\
      --catalog rest \\
      --name analytics.events \\
      --columns "event_id BIGINT, user_id BIGINT, event_type STRING, ts TIMESTAMP, payload STRING" \\
      --partition ts_month,event_type \\
      --format-version 2 \\
      --target-file-size-mb 256

SUPPORTED CATALOGS
------------------
  rest     — Any REST-catalog-compatible service (Polaris, Nessie REST mode, Open Catalog)
  glue     — AWS Glue Data Catalog (SparkSQL / Athena / EMR)
  nessie   — Project Nessie (native REST, multi-table transactions)
  polaris  — Apache Polaris / Snowflake Open Catalog

PARTITION TRANSFORMS (--partition)
-----------------------------------
Provide a comma-separated list of column names. Each entry may optionally
include a transform prefix:

  ts_month          → MONTH(ts)          (only when ts is a declared DATE/TIMESTAMP column)
  ts_day            → DAY(ts)
  ts_hour           → HOUR(ts)
  ts_year           → YEAR(ts)
  bucket_16_user_id → BUCKET(16, user_id)
  truncate_10_name  → TRUNCATE(10, name)
  event_type        → event_type          (identity partition — no transform)

Every partition entry must resolve to a column declared in --columns. An exact
column-name match wins over the shorthand, so a column literally named
"payment_day" stays an identity partition. Unknown columns, time transforms on
non-temporal columns, and zero bucket/truncate widths exit non-zero.

KNOWN LIMITATIONS
-----------------
- Column types are passed through verbatim (only "name TYPE" shape is checked).
  Use Spark/Flink/Trino DDL type names appropriate for your engine.
- The output is Spark SQL DDL (USING ICEBERG, PARTITIONED BY transforms,
  TBLPROPERTIES). Run it in Spark SQL. Trino needs
  WITH (format_version = 2, partitioning = ARRAY['month(ts)']) instead, and
  Flink SQL DDL does not accept transform partitioning.
- Nessie branch targeting (CREATE TABLE ON BRANCH ...) is not included; add
  manually if using multi-table Nessie transactions.
"""

import argparse
import re
import sys
import textwrap
from datetime import date


# ---------------------------------------------------------------------------
# Partition transform logic
# ---------------------------------------------------------------------------

# Suffixes that imply a time transform — matched against the column name
_TIME_SUFFIX_MAP = {
    "_year": "YEAR",
    "_month": "MONTH",
    "_day": "DAY",
    "_hour": "HOUR",
}


_TEMPORAL_TYPES = ("DATE", "TIMESTAMP", "TIMESTAMP_NTZ", "TIMESTAMP_LTZ", "TIMESTAMPTZ")


def _fail(msg: str) -> None:
    sys.exit(f"ERROR: {msg}")


def _parse_partition_transform(spec: str, col_types: dict[str, str]) -> str:
    """
    Convert a shorthand partition spec string into a SQL partition transform,
    resolved against the declared columns (name -> upper-cased type).

    Examples (columns: ts TIMESTAMP, event_type STRING, user_id BIGINT):
      "ts_month"           → "MONTH(ts)"
      "event_type"         → "event_type"
      "bucket_16_user_id"  → "BUCKET(16, user_id)"
    """
    spec = spec.strip()
    lower = {c.lower(): c for c in col_types}

    # Exact column name → identity partition (wins over any shorthand).
    if spec.lower() in lower:
        return lower[spec.lower()]

    # bucket_<N>_<col> / truncate_<N>_<col>
    m = re.match(r"^(bucket|truncate)_(\d+)_(.+)$", spec, re.IGNORECASE)
    if m:
        kind, n, col = m.group(1).upper(), int(m.group(2)), m.group(3)
        if n <= 0:
            _fail(f"partition {spec!r}: {kind.lower()} width must be > 0.")
        if col.lower() not in lower:
            _fail(f"partition {spec!r}: column {col!r} is not declared in --columns.")
        return f"{kind}({n}, {lower[col.lower()]})"

    # time-suffix shorthand: ts_month → MONTH(ts); base column must be temporal
    for suffix, transform in _TIME_SUFFIX_MAP.items():
        if spec.lower().endswith(suffix) and len(spec) > len(suffix):
            col = spec[: -len(suffix)]
            if col.lower() not in lower:
                break
            real = lower[col.lower()]
            ctype = col_types[real]
            if not ctype.startswith(_TEMPORAL_TYPES):
                _fail(
                    f"partition {spec!r}: {transform}() needs a DATE/TIMESTAMP column, "
                    f"but {real!r} is {ctype}. Use an identity or bucket partition instead."
                )
            if transform == "HOUR" and ctype.startswith("DATE"):
                _fail(f"partition {spec!r}: HOUR() is not valid on DATE column {real!r}; use DAY().")
            return f"{transform}({real})"

    _fail(
        f"partition {spec!r} does not match any column in --columns "
        f"({', '.join(col_types)}). Use a declared column name or a shorthand such as <col>_month."
    )


# ---------------------------------------------------------------------------
# Catalog-specific TBLPROPERTIES
# ---------------------------------------------------------------------------

_CATALOG_NOTES = {
    "rest": (
        "-- REST catalog: set 'warehouse' and 'uri' in your Spark/Trino session config.\n"
        "-- For Polaris or another authenticated REST catalog: also set 'credential' or 'token'\n"
        "-- in the catalog properties."
    ),
    "glue": (
        "-- AWS Glue catalog: set spark.sql.catalog.<name>=org.apache.iceberg.spark.SparkCatalog\n"
        "-- and spark.sql.catalog.<name>.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog\n"
        "-- in your SparkSession config. Ensure the IAM role has glue:CreateTable permission."
    ),
    "nessie": (
        "-- Nessie catalog: set catalog-impl=org.apache.iceberg.nessie.NessieCatalog\n"
        "-- and io-impl=org.apache.iceberg.aws.s3.S3FileIO (or GCS equivalent).\n"
        "-- To target a specific branch: append VERSION AS OF 'branch:<branch>' in Spark SQL."
    ),
    "polaris": (
        "-- Apache Polaris / Snowflake Open Catalog: use the REST catalog implementation.\n"
        "-- Set 'credential' (client_id:client_secret) and 'scope' in catalog properties.\n"
        "-- Polaris enforces catalog-level RBAC; grant USAGE on the catalog before creating tables."
    ),
}


def _build_tblproperties(format_version: int, target_file_size_bytes: int, catalog: str) -> list[tuple[str, str]]:
    """Return a list of (key, value) pairs for TBLPROPERTIES."""
    props = [
        ("format-version", str(format_version)),
        ("write.target-file-size-bytes", str(target_file_size_bytes)),
        # cluster rows by partition before writing, so each task writes few, large files
        ("write.distribution-mode", "hash"),
        # Parquet compression — zstd balances ratio vs CPU well for most workloads
        ("write.parquet.compression-codec", "zstd"),
        # Merge-on-read: cheap updates/deletes via delete files; reads pay until compaction runs.
        # For read-heavy tables with rare updates, switch these three to copy-on-write.
        ("write.delete.mode", "merge-on-read"),
        ("write.update.mode", "merge-on-read"),
        ("write.merge.mode", "merge-on-read"),
    ]

    if catalog == "glue":
        # Keep full (untruncated) column bounds in manifests for file pruning; costs larger manifests
        props.append(("write.metadata.metrics.default", "full"))

    return props


# ---------------------------------------------------------------------------
# DDL generation
# ---------------------------------------------------------------------------

def _split_top_level(columns: str) -> list[str]:
    """Split column definitions on commas outside (), <> so DECIMAL(10,2) and MAP<K,V> survive."""
    parts, depth, buf = [], 0, []
    for ch in columns:
        if ch in "(<":
            depth += 1
        elif ch in ")>":
            depth -= 1
            if depth < 0:
                _fail("unbalanced brackets in --columns.")
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    if depth != 0:
        sys.exit(f"ERROR: unbalanced brackets in --columns: {columns!r}")
    return [p.strip() for p in parts if p.strip()]


def generate_ddl(
    catalog: str,
    name: str,
    columns: str,
    partition_specs: list[str],
    format_version: int,
    target_file_size_bytes: int,
) -> str:
    """Assemble the full CREATE TABLE DDL string."""
    # Parse namespace and table name
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+", name):
        sys.exit(
            "ERROR: --name must use unquoted SQL identifiers in <namespace>.<table> form "
            f"(e.g. analytics.events). Got: {name!r}"
        )
    table_ref = name  # keep fully-qualified

    # Format columns (passed in verbatim, indented for readability)
    col_lines = _split_top_level(columns)
    if not col_lines:
        _fail('--columns is empty. Pass definitions like "id BIGINT, ts TIMESTAMP".')
    if any(token in columns for token in (";", "--", "/*", "*/", "\n", "\r")):
        _fail("--columns contains a SQL statement boundary or comment marker.")
    col_types: dict[str, str] = {}
    for line in col_lines:
        bits = line.split(None, 1)
        if len(bits) < 2 or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", bits[0]):
            _fail(f"column definition {line!r} must be '<name> <TYPE>', e.g. 'ts TIMESTAMP'.")
        if bits[0].lower() in {c.lower() for c in col_types}:
            _fail(f"column {bits[0]!r} is declared twice in --columns.")
        col_types[bits[0]] = bits[1].strip().upper()
    col_block = ",\n    ".join(col_lines)

    # Partition transforms
    transforms = [_parse_partition_transform(p, col_types) for p in partition_specs]
    partition_block = ""
    if transforms:
        transform_lines = ",\n    ".join(transforms)
        partition_block = f"\nPARTITIONED BY (\n    {transform_lines}\n)"

    # TBLPROPERTIES
    props = _build_tblproperties(format_version, target_file_size_bytes, catalog)
    props_lines = ",\n    ".join(f"'{k}' = '{v}'" for k, v in props)

    catalog_note = _CATALOG_NOTES.get(catalog, "")

    # Dedent the static template first, then substitute multi-line values,
    # so interpolated lines do not break the common indentation.
    template = textwrap.dedent("""\
        -- ============================================================
        -- Iceberg Table DDL — generated by scaffold_iceberg_table.py
        -- Catalog  : {catalog}
        -- Generated: {generated}
        -- ============================================================
        --
        {catalog_note}
        --
        -- Spark SQL DDL: run this in Spark SQL after configuring the catalog
        -- session properties. Trino uses CREATE TABLE ... WITH (format_version = N,
        -- partitioning = ARRAY['month(ts)']); Flink SQL DDL does not accept
        -- transform partitioning.
        -- ============================================================

        CREATE TABLE IF NOT EXISTS {table_ref} (
            {col_block}
        )
        USING ICEBERG{partition_block}
        TBLPROPERTIES (
            {props_lines}
        );
    """)
    ddl = template.format(
        catalog=catalog,
        generated=date.today().isoformat(),
        catalog_note=catalog_note,
        table_ref=table_ref,
        col_block=col_block,
        partition_block=partition_block,
        props_lines=props_lines,
    )

    return ddl


# ---------------------------------------------------------------------------
# Post-creation checklist
# ---------------------------------------------------------------------------

_CHECKLIST = """\
-- ============================================================
-- POST-CREATION CHECKLIST
-- ============================================================
--
-- 1. PARTITION CARDINALITY
--    Review each partition column for cardinality. Identity partitions
--    on high-cardinality columns (e.g. user_id with millions of values)
--    create millions of small files and metadata explosion.
--    Prefer BUCKET(N, col) for high-cardinality columns.
--    Size partitions from observed ingest volume and query patterns.
--
-- 2. SNAPSHOT RETENTION (expire_snapshots)
--    Iceberg retains all snapshots by default. Set up a scheduled job. The cutoff is
--    "now minus your time-travel window", computed by the scheduler at run time;
--    never paste a literal date into a recurring job.
--
--    -- Spark:
--    CALL <catalog>.system.expire_snapshots(
--        table => '{name}',
--        older_than => TIMESTAMP '<now minus time-travel window>',
--        retain_last => <retained-snapshot-count-from-policy>
--    );
--
--    -- Trino (via connector procedure):
--    ALTER TABLE {name} EXECUTE expire_snapshots(retention_threshold => '7d');
--
-- 3. COMPACTION (rewrite_data_files)
--    Small files accumulate from streaming ingest and frequent upserts.
--    Schedule regular compaction:
--
--    -- Spark:
--    CALL <catalog>.system.rewrite_data_files(
--        table => '{name}',
--        strategy => 'sort',
--        sort_order => 'zorder(col1, col2)'
--    );
--
--    -- Trino:
--    ALTER TABLE {name} EXECUTE optimize(file_size_threshold => '128MB');
--
-- 4. ORPHAN FILE CLEANUP (remove_orphan_files)
--    Failed writes and aborted jobs leave unreferenced files in object storage.
--    Run periodically (weekly is typical). The cutoff must be older than your
--    longest-running write, or in-flight files of a live job get deleted:
--
--    CALL <catalog>.system.remove_orphan_files(
--        table => '{name}',
--        older_than => TIMESTAMP '<now minus margin longer than longest write>',
--        dry_run => true
--    );
--    Review dry-run results before a separate cleanup call.
--
-- 5. METADATA COMPACTION (rewrite_manifests)
--    Many small manifests slow down planning. Compact after bulk loads:
--
--    CALL <catalog>.system.rewrite_manifests('{name}');
--
-- 6. STATISTICS (for Trino / Spark cost-based optimiser)
--    ANALYZE TABLE {name} COMPUTE STATISTICS FOR ALL COLUMNS;
--
-- ============================================================
"""


def generate_checklist(name: str) -> str:
    return _CHECKLIST.format(name=name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--catalog",
        choices=["rest", "glue", "nessie", "polaris"],
        required=True,
        help="Target catalog type.",
    )
    parser.add_argument(
        "--name",
        required=True,
        metavar="NS.TABLE",
        help="Fully-qualified table name, e.g. analytics.events",
    )
    parser.add_argument(
        "--columns",
        required=True,
        metavar="COL_DEF,...",
        help='Comma-separated column definitions, e.g. "id BIGINT, ts TIMESTAMP, val STRING"',
    )
    parser.add_argument(
        "--partition",
        default="",
        metavar="COL,...",
        help=(
            "Comma-separated partition specs. Supports shorthand transforms: "
            "ts_month, ts_day, bucket_16_user_id, truncate_10_name. "
            "Bare column names → identity partition."
        ),
    )
    parser.add_argument(
        "--format-version",
        type=int,
        choices=[2, 3],
        default=2,
        help=(
            "Iceberg format version. Default: 2 (broadest engine support). Use 3 only after every "
            "reader and writer engine is confirmed to support it (see SKILL.md, Version and support lookup)."
        ),
    )
    parser.add_argument(
        "--target-file-size-mb",
        type=int,
        default=128,
        metavar="MB",
        help="Target Parquet file size in MB (default: 128). Converted to bytes in TBLPROPERTIES.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write DDL to a file instead of stdout.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    partition_specs = [p.strip() for p in args.partition.split(",") if p.strip()] if args.partition else []
    if args.target_file_size_mb <= 0:
        parser.error("--target-file-size-mb must be a positive number of MB (default 128).")
    target_bytes = args.target_file_size_mb * 1024 * 1024

    ddl = generate_ddl(
        catalog=args.catalog,
        name=args.name,
        columns=args.columns,
        partition_specs=partition_specs,
        format_version=args.format_version,
        target_file_size_bytes=target_bytes,
    )
    checklist = generate_checklist(args.name)
    output = ddl + "\n" + checklist

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"DDL written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
