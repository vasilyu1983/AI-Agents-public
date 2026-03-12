# Operational Playbook

## Monitoring

### Key Metrics

| Metric | Tool | Alert Threshold |
|--------|------|-----------------|
| **Data freshness** | dlt state, Iceberg snapshots | > SLA |
| **Pipeline failures** | Dagster/Airflow | Any failure |
| **Query latency** | ClickHouse system.query_log | p99 > 10s |
| **Storage growth** | system.parts | > 80% capacity |
| **Consumer lag** | Kafka metrics | > 10 min |

### ClickHouse Monitoring

```sql
-- Active queries
SELECT query_id, user, query, elapsed
FROM system.processes
ORDER BY elapsed DESC;

-- Failed queries (last 24h)
SELECT
    exception_code,
    count() AS failures,
    any(exception) AS example
FROM system.query_log
WHERE event_date >= today() - 1
  AND exception_code != 0
GROUP BY exception_code
ORDER BY failures DESC;

-- Slow queries
SELECT
    query,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) AS read_size
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### Grafana Dashboard

```yaml
# prometheus/clickhouse-alerts.yaml
groups:
  - name: clickhouse
    rules:
      - alert: ClickHouseQuerySlow
        expr: clickhouse_query_duration_ms_p99 > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ClickHouse p99 latency > 10s"

      - alert: ClickHouseDiskUsage
        expr: clickhouse_disk_used_bytes / clickhouse_disk_total_bytes > 0.8
        for: 10m
        labels:
          severity: critical
```

---

## Incident Response

### Pipeline Failure

```text
1. CHECK: Pipeline status in Dagster/Airflow UI
2. IDENTIFY: Error message and failed task
3. INVESTIGATE:
   - Source system availability
   - Credentials/permissions
   - Schema changes
   - Resource limits (memory, disk)
4. FIX: Address root cause
5. RETRY: Re-run failed pipeline
6. VERIFY: Check data quality downstream
7. DOCUMENT: Update runbook if new issue
```

### Data Quality Issue

```text
1. DETECT: Alert from Great Expectations/Soda
2. ASSESS: Scope of impact (which tables, time range)
3. QUARANTINE: Mark affected data (add flag column)
4. INVESTIGATE: Source system, transformation logic
5. FIX: Correct data or rollback
6. VALIDATE: Re-run quality checks
7. NOTIFY: Inform downstream consumers
```

### ClickHouse Performance Degradation

```sql
-- Step 1: Check for resource contention
SELECT * FROM system.metrics WHERE metric LIKE '%Memory%';
SELECT * FROM system.metrics WHERE metric LIKE '%Query%';

-- Step 2: Identify expensive queries
SELECT query_id, query, elapsed
FROM system.processes
ORDER BY elapsed DESC LIMIT 5;

-- Step 3: Kill if needed
KILL QUERY WHERE query_id = 'xxx';

-- Step 4: Check merge status
SELECT database, table, count() AS parts
FROM system.parts
WHERE active
GROUP BY database, table
HAVING count() > 100;

-- Step 5: Force merge if needed
OPTIMIZE TABLE events FINAL;
```

---

## Migration Procedures

### Adding New Data Source

```text
1. DOCUMENT: Schema, volumes, SLAs
2. DEVELOP: dlt source in dev environment
3. TEST: Run with sample data
4. VALIDATE: Schema inference, data quality
5. DEPLOY: Add to production pipeline
6. MONITOR: First few runs closely
7. CATALOG: Add to DataHub/OpenMetadata
```

### Schema Change

```text
1. PLAN: Backwards compatibility check
2. NOTIFY: Downstream consumers
3. UPDATE:
   - Iceberg: ALTER TABLE ADD/RENAME COLUMN
   - SQLMesh: Update model, run plan
4. MIGRATE: Backfill historical data if needed
5. VERIFY: Query both old and new schema
6. DOCUMENT: Update data catalog
```

### Table Format Migration (e.g., Parquet → Iceberg)

```sql
-- Step 1: Create Iceberg table
CREATE TABLE iceberg.events USING iceberg AS
SELECT * FROM parquet.events WHERE 1=0;

-- Step 2: Migrate data in batches
INSERT INTO iceberg.events
SELECT * FROM parquet.events
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31';

-- Step 3: Validate counts
SELECT count(*) FROM parquet.events;
SELECT count(*) FROM iceberg.events;

-- Step 4: Update pipelines to use Iceberg
-- Step 5: Keep Parquet as backup
-- Step 6: Drop Parquet after validation period
```

---

## Backup & Recovery

### ClickHouse Backup

```bash
# Using clickhouse-backup
clickhouse-backup create daily_backup
clickhouse-backup upload daily_backup

# Restore
clickhouse-backup download daily_backup
clickhouse-backup restore daily_backup
```

### Iceberg Time Travel (Recovery)

```sql
-- List snapshots
SELECT * FROM catalog.db.events.snapshots;

-- Rollback to snapshot
CALL catalog.system.rollback_to_snapshot('db.events', 123456789);

-- Read historical data
SELECT * FROM events VERSION AS OF 123456789;
```

---

## Runbook Template

```markdown
# Runbook: [Issue Type]

## Symptoms
- [Observable symptoms]

## Impact
- [Affected systems/users]

## Root Cause
- [Known causes]

## Resolution Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Verification
- [How to verify resolution]

## Prevention
- [Steps to prevent recurrence]

## Contacts
- On-call: [Team/person]
- Escalation: [Manager/senior]
```
