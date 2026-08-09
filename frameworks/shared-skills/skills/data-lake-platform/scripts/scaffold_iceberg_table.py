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
  rest     — Any REST-catalog-compatible service (Polaris, Tabular, Nessie REST mode, Open Catalog)
  glue     — AWS Glue Data Catalog (SparkSQL / Athena / EMR)
  nessie   — Project Nessie (native REST, multi-table transactions)
  polaris  — Apache Polaris / Snowflake Open Catalog

PARTITION TRANSFORMS (--partition)
-----------------------------------
Provide a comma-separated list of column names. Each entry may optionally
include a transform prefix:

  ts_month          → MONTH(ts)          (auto-detected for TIMESTAMP/DATE columns when suffix matches)
  ts_day            → DAY(ts)
  ts_hour           → HOUR(ts)
  ts_year           → YEAR(ts)
  bucket_16_user_id → BUCKET(16, user_id)
  truncate_10_name  → TRUNCATE(10, name)
  event_type        → event_type          (identity partition — no transform)

KNOWN LIMITATIONS
-----------------
- Column types are passed through verbatim; no type validation is performed.
  Use Spark/Flink/Trino DDL type names appropriate for your engine.
- The output is a SQL template; actual catalog registration happens when you
  run it against your engine (Spark SQL, Trino, or Flink SQL).
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


def _parse_partition_transform(spec: str) -> str:
    """
    Convert a shorthand partition spec string into a SQL partition transform.

    Examples:
      "ts_month"           → "MONTH(ts)"
      "event_type"         → "event_type"
      "bucket_16_user_id"  → "BUCKET(16, user_id)"
      "truncate_10_name"   → "TRUNCATE(10, name)"
    """
    spec = spec.strip()

    # bucket_<N>_<col>
    m = re.match(r"^bucket_(\d+)_(.+)$", spec, re.IGNORECASE)
    if m:
        n, col = m.group(1), m.group(2)
        return f"BUCKET({n}, {col})"

    # truncate_<N>_<col>
    m = re.match(r"^truncate_(\d+)_(.+)$", spec, re.IGNORECASE)
    if m:
        n, col = m.group(1), m.group(2)
        return f"TRUNCATE({n}, {col})"

    # time-suffix shorthand: ts_month → MONTH(ts)
    for suffix, transform in _TIME_SUFFIX_MAP.items():
        if spec.lower().endswith(suffix):
            col = spec[: -len(suffix)]
            if col:
                return f"{transform}({col})"

    # Identity — no transform
    return spec


# ---------------------------------------------------------------------------
# Catalog-specific TBLPROPERTIES
# ---------------------------------------------------------------------------

_CATALOG_NOTES = {
    "rest": (
        "-- REST catalog: set 'warehouse' and 'uri' in your Spark/Trino session config.\n"
        "-- For Polaris/Tabular: also set 'credential' or 'token' in the catalog properties."
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
        # equality-delete + position-delete support (v2 feature, no-op on v1)
        ("write.distribution-mode", "hash"),
        # Parquet compression — zstd balances ratio vs CPU well for most workloads
        ("write.parquet.compression-codec", "zstd"),
        # Enable delete-row tracking for MOR (merge-on-read) compaction
        ("write.delete.mode", "merge-on-read"),
        ("write.update.mode", "merge-on-read"),
        ("write.merge.mode", "merge-on-read"),
    ]

    if catalog == "glue":
        # Glue requires explicit S3 location in properties for some engines
        props.append(("write.metadata.metrics.default", "full"))

    return props


# ---------------------------------------------------------------------------
# DDL generation
# ---------------------------------------------------------------------------

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
    parts = name.split(".")
    if len(parts) < 2:
        sys.exit(
            f"ERROR: --name must be in <namespace>.<table> format (e.g. analytics.events). Got: {name!r}"
        )
    table_ref = name  # keep fully-qualified

    # Format columns (passed in verbatim, indented for readability)
    col_lines = [c.strip() for c in columns.split(",") if c.strip()]
    col_block = ",\n    ".join(col_lines)

    # Partition transforms
    transforms = [_parse_partition_transform(p) for p in partition_specs]
    partition_block = ""
    if transforms:
        transform_lines = ",\n        ".join(transforms)
        partition_block = f"\nPARTITIONED BY (\n        {transform_lines}\n)"

    # TBLPROPERTIES
    props = _build_tblproperties(format_version, target_file_size_bytes, catalog)
    props_lines = ",\n    ".join(f"'{k}' = '{v}'" for k, v in props)

    catalog_note = _CATALOG_NOTES.get(catalog, "")

    ddl = textwrap.dedent(f"""\
        -- ============================================================
        -- Iceberg Table DDL — generated by scaffold_iceberg_table.py
        -- Catalog  : {catalog}
        -- Generated: {date.today().isoformat()}
        -- ============================================================
        --
        {catalog_note}
        --
        -- Run this in Spark SQL, Trino, or Flink SQL after configuring
        -- the catalog session properties for your environment.
        -- ============================================================

        CREATE TABLE IF NOT EXISTS {table_ref} (
            {col_block}
        )
        USING ICEBERG{partition_block}
        TBLPROPERTIES (
            {props_lines}
        );
    """)

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
--    Rule of thumb: aim for partitions that produce 128 MB–1 GB of data.
--
-- 2. SNAPSHOT RETENTION (expire_snapshots)
--    Iceberg retains all snapshots by default. Set up a scheduled job:
--
--    -- Spark:
--    CALL <catalog>.system.expire_snapshots(
--        table => '{name}',
--        older_than => TIMESTAMP '{date_7d}',
--        retain_last => 5
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
--    Run periodically (weekly is typical):
--
--    CALL <catalog>.system.remove_orphan_files(
--        table => '{name}',
--        older_than => TIMESTAMP '{date_3d}'
--    );
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
    from datetime import UTC, datetime, timedelta
    now = datetime.now(UTC).replace(tzinfo=None)
    date_7d = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    date_3d = (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    return _CHECKLIST.format(name=name, date_7d=date_7d, date_3d=date_3d)


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
        help="Iceberg format version. Default: 2 (broadly supported). Use 3 for new PG-style features.",
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
