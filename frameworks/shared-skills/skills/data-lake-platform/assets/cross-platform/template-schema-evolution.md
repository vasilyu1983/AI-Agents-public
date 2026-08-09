# Schema Evolution Template

## Overview

Patterns for handling schema changes in data lake tables without breaking downstream consumers.

## Schema Change Types

| Change Type | Risk Level | Strategy |
|-------------|------------|----------|
| Add column | Low | Backward compatible |
| Rename column | Medium | Add new → migrate → drop old |
| Change type (widen) | Low | Usually safe (int32 → int64) |
| Change type (narrow) | High | Requires data validation |
| Drop column | High | Deprecate → remove after grace period |
| Change nullability | Medium | Validate existing data first |

---

## Apache Iceberg Schema Evolution

### Add Column

```sql
-- Spark SQL
ALTER TABLE catalog.db.events ADD COLUMN user_agent STRING AFTER user_id;

-- With default value
ALTER TABLE catalog.db.events ADD COLUMN is_processed BOOLEAN DEFAULT false;

-- Nested column
ALTER TABLE catalog.db.events ADD COLUMN metadata.source STRING;
```

### Rename Column

```sql
-- Safe rename (preserves data)
ALTER TABLE catalog.db.events RENAME COLUMN user_agent TO browser_info;

-- Iceberg tracks column by ID, not name
-- Downstream queries using old name will fail
```

### Change Column Type

```sql
-- Widen type (safe)
ALTER TABLE catalog.db.events ALTER COLUMN user_id TYPE BIGINT;

-- Iceberg supports: int → long, float → double, decimal precision increase
```

### Drop Column

```sql
-- Iceberg "soft deletes" columns (data remains in files)
ALTER TABLE catalog.db.events DROP COLUMN deprecated_field;

-- Files not rewritten - just metadata update
-- Query with time travel still sees old column
```

### Required to Optional

```sql
ALTER TABLE catalog.db.events ALTER COLUMN email DROP NOT NULL;
```

### Schema Evolution Best Practices (Iceberg)

```python
# PyIceberg schema operations
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType

catalog = load_catalog("rest")
table = catalog.load_table("db.events")

# Get current schema
current_schema = table.schema()
print(f"Current schema version: {table.metadata.current_schema_id}")

# Add column with update
with table.update_schema() as update:
    update.add_column("new_field", StringType(), doc="New field description")
    update.add_column("nested.subfield", LongType())

# View schema history
for schema in table.metadata.schemas:
    print(f"Schema {schema.schema_id}: {len(schema.fields)} fields")
```

---

## Delta Lake Schema Evolution

### Schema Enforcement vs Evolution

```python
# Default: Schema enforcement (rejects mismatched schemas)
df.write.format("delta").mode("append").save("/delta/events")

# Enable schema evolution
df.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .save("/delta/events")

# Or set at table level
spark.sql("""
    ALTER TABLE delta.events
    SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name')
""")
```

### Column Mapping (Delta 2.0+)

```sql
-- Enable column mapping for renames/drops
ALTER TABLE events SET TBLPROPERTIES (
    'delta.columnMapping.mode' = 'name',
    'delta.minReaderVersion' = '2',
    'delta.minWriterVersion' = '5'
);

-- Now can rename columns
ALTER TABLE events RENAME COLUMN old_name TO new_name;

-- And drop columns
ALTER TABLE events DROP COLUMN deprecated_field;
```

### Schema Evolution Operations

```sql
-- Add column
ALTER TABLE events ADD COLUMN new_field STRING AFTER existing_field;

-- Change type (only widening allowed)
ALTER TABLE events ALTER COLUMN amount TYPE DECIMAL(20, 4);

-- Add constraint
ALTER TABLE events ADD CONSTRAINT positive_amount CHECK (amount >= 0);
```

---

## ClickHouse Schema Evolution

### Add Column

```sql
-- Add column with default
ALTER TABLE events ADD COLUMN browser_info String DEFAULT 'unknown';

-- Add column at position
ALTER TABLE events ADD COLUMN session_id UUID AFTER user_id;

-- For distributed tables
ALTER TABLE events ON CLUSTER my_cluster ADD COLUMN browser_info String;
```

### Modify Column

```sql
-- Change type
ALTER TABLE events MODIFY COLUMN user_id UInt64;  -- Was UInt32

-- Change default
ALTER TABLE events MODIFY COLUMN status String DEFAULT 'pending';

-- Add codec for compression
ALTER TABLE events MODIFY COLUMN event_data String CODEC(ZSTD(3));
```

### Rename Column (ClickHouse 23.4+)

```sql
ALTER TABLE events RENAME COLUMN old_name TO new_name;
```

### Drop Column

```sql
-- Immediate drop (data remains until merge)
ALTER TABLE events DROP COLUMN deprecated_field;

-- Clear data explicitly
ALTER TABLE events CLEAR COLUMN deprecated_field;

-- Distributed table
ALTER TABLE events ON CLUSTER my_cluster DROP COLUMN deprecated_field;
```

### Materialized Column

```sql
-- Add computed column
ALTER TABLE events ADD COLUMN day Date MATERIALIZED toDate(created_at);

-- Update existing data
ALTER TABLE events MATERIALIZE COLUMN day;
```

---

## SQLMesh Schema Management

### Model Schema Definition

```sql
-- models/staging/stg_events.sql
MODEL (
  name silver.stg_events,
  kind INCREMENTAL_BY_TIME_RANGE (time_column created_at),
  columns (
    event_id STRING NOT NULL,
    user_id INT64 NOT NULL,
    event_type STRING NOT NULL,
    -- New column: browser_info added 2024-06-01
    browser_info STRING,
    created_at TIMESTAMP NOT NULL
  )
);
```

### Plan and Apply Changes

```bash
# Preview schema changes
sqlmesh plan

# Output shows:
# Models:
#   silver.stg_events (schema change)
#     Added columns:
#       - browser_info STRING

# Apply changes
sqlmesh plan --auto-apply
```

### Backfill After Schema Change

```bash
# Backfill data for new column
sqlmesh plan --restate-model silver.stg_events --start 2024-01-01
```

---

## dlt Schema Evolution

### Auto Schema Evolution

```python
import dlt

# dlt auto-detects and evolves schema
pipeline = dlt.pipeline(
    pipeline_name="events",
    destination="clickhouse"
)

# First load: creates table with initial schema
pipeline.run(events_batch_1)

# Second load: auto-adds new columns if data has them
pipeline.run(events_batch_2_with_new_fields)

# Check schema
print(pipeline.default_schema.tables["events"])
```

### Schema Contract Mode

```python
# Strict mode: reject schema changes
@dlt.resource(
    name="events",
    schema_contract={"tables": "freeze", "columns": "freeze"}
)
def events():
    yield data

# Evolve mode: allow additive changes only
@dlt.resource(
    schema_contract={"tables": "evolve", "columns": "evolve"}
)
def events():
    yield data

# Discard mode: drop unknown columns silently
@dlt.resource(
    schema_contract={"columns": "discard_value"}
)
def events():
    yield data
```

### Manual Schema Definition

```python
@dlt.resource(
    columns={
        "event_id": {"data_type": "text", "nullable": False},
        "user_id": {"data_type": "bigint", "nullable": False},
        "amount": {"data_type": "decimal", "precision": 18, "scale": 2},
        "created_at": {"data_type": "timestamp", "nullable": False}
    }
)
def events():
    yield data
```

---

## Migration Patterns

### Pattern 1: Add Column with Backfill

```sql
-- Step 1: Add nullable column
ALTER TABLE events ADD COLUMN browser_info String;

-- Step 2: Backfill from another source
ALTER TABLE events UPDATE browser_info = extractBrowserFromUserAgent(user_agent)
WHERE browser_info IS NULL OR browser_info = '';

-- Step 3: Optionally add NOT NULL constraint after backfill
-- (ClickHouse doesn't support ALTER COLUMN NOT NULL)
```

### Pattern 2: Rename Column Safely

```sql
-- Step 1: Add new column
ALTER TABLE events ADD COLUMN browser_info String;

-- Step 2: Copy data
ALTER TABLE events UPDATE browser_info = user_agent WHERE 1=1;

-- Step 3: Update downstream consumers (allow grace period)

-- Step 4: Drop old column
ALTER TABLE events DROP COLUMN user_agent;
```

### Pattern 3: Type Change with New Column

```sql
-- Can't change String to Int directly
-- Step 1: Add new column with correct type
ALTER TABLE events ADD COLUMN user_id_new UInt64;

-- Step 2: Copy and convert
ALTER TABLE events UPDATE user_id_new = toUInt64(user_id) WHERE 1=1;

-- Step 3: Rename columns
ALTER TABLE events RENAME COLUMN user_id TO user_id_old;
ALTER TABLE events RENAME COLUMN user_id_new TO user_id;

-- Step 4: Drop old column after validation
ALTER TABLE events DROP COLUMN user_id_old;
```

---

## Version Tracking

### Schema Registry Table

```sql
CREATE TABLE meta.schema_versions (
    table_name String,
    version UInt32,
    schema_json String,
    created_at DateTime DEFAULT now(),
    created_by String,
    change_description String
)
ENGINE = MergeTree()
ORDER BY (table_name, version);

-- Record schema changes
INSERT INTO meta.schema_versions VALUES
('silver.stg_events', 2, '{"columns":[...]}', now(), 'data-team', 'Added browser_info column');
```

### Migration Scripts Directory

```text
migrations/
├── events/
│   ├── v001_initial_schema.sql
│   ├── v002_add_browser_info.sql
│   ├── v003_rename_user_agent.sql
│   └── v004_add_session_id.sql
└── orders/
    ├── v001_initial_schema.sql
    └── v002_add_discount_field.sql
```

---

## Best Practices

1. **Always add columns as nullable first** - then backfill and add constraints
2. **Never rename columns directly** - add new, migrate, drop old
3. **Document all schema changes** - in migration scripts and registry
4. **Test with production data copies** - before applying to production
5. **Communicate changes to consumers** - allow grace period for updates
6. **Use schema contracts** - enforce compatibility in CI/CD
7. **Track schema versions** - for debugging and rollback
