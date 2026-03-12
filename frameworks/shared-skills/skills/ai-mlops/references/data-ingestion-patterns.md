# Data Ingestion Patterns for ML Systems

Comprehensive patterns for data contracts, ingestion modes, lineage tracking, and schema evolution in production ML pipelines.

---

## Overview

Production ML systems require reliable data ingestion with clear contracts, reproducible lineage, and graceful schema evolution. This guide covers the operational patterns for building robust data pipelines.

**Key Topics:**
- Data contracts with SLAs and versioning
- Ingestion modes (CDC, batch, streaming)
- Lineage tracking and reproducibility
- Schema evolution and migration strategies
- Replay and backfill procedures

---

## Pattern 1: Data Contracts

### Definition

A data contract defines the **schema, quality guarantees, and SLAs** between data producers and consumers.

### Components

**Schema:**
- Column names, types, and constraints
- Nullability rules
- Value ranges and enums
- Primary keys and uniqueness guarantees

**SLAs:**
- Freshness (e.g., data available within 15 minutes)
- Completeness (e.g., no more than 0.1% missing values)
- Accuracy (e.g., referential integrity maintained)

**Versioning:**
- Semantic versioning for contract changes
- Backwards compatibility guarantees
- Migration paths documented

### Implementation Checklist

- [ ] Schema defined with types, constraints, and nullability
- [ ] SLAs documented (freshness, completeness, accuracy)
- [ ] Contract versioned and tracked in registry
- [ ] Breaking changes require version bump
- [ ] Validation tests run on every batch
- [ ] Contract violations block pipeline progression

### Example Contract (YAML)

```yaml
version: 2.1.0
table: user_events
owner: data-platform-team
sla:
  freshness: 15min
  completeness: 99.9%
schema:
  - name: user_id
    type: string
    nullable: false
    constraints:
      - pattern: '^[0-9a-f]{32}$'
  - name: event_type
    type: string
    nullable: false
    enum: [click, view, purchase, signup]
  - name: timestamp
    type: timestamp
    nullable: false
  - name: metadata
    type: json
    nullable: true
```

---

## Pattern 2: Ingestion Modes

### CDC (Change Data Capture)

**When to use:** Real-time replication from transactional databases

**Approaches:**
- Log-based CDC (read database transaction logs)
- Trigger-based CDC (database triggers on INSERT/UPDATE/DELETE)
- Timestamp-based polling (incremental queries)

**Best practices:**
- Prefer log-based CDC for low latency and minimal source impact
- Record source offsets/checkpoints for resumability
- Handle schema changes gracefully (see Pattern 4)
- Monitor lag between source and target

**Checklist:**
- [ ] CDC mechanism chosen and justified
- [ ] Source impact assessed (CPU, I/O, network)
- [ ] Offset/checkpoint persistence configured
- [ ] Lag monitoring and alerting in place
- [ ] Backfill procedure documented

### Batch Ingestion

**When to use:** Periodic bulk loads, historical data, scheduled reporting

**Best practices:**
- Idempotent ingestion (safe to rerun)
- Partitioned by date/hour for incremental processing
- Deduplication logic for overlapping batches
- Record watermarks (latest processed timestamp/ID)

**Checklist:**
- [ ] Batch schedule defined (hourly, daily, weekly)
- [ ] Idempotency guaranteed (upsert or partition overwrite)
- [ ] Watermarks tracked and persisted
- [ ] Failure retry logic implemented
- [ ] Backfill procedure tested

### Streaming Ingestion

**When to use:** Real-time event streams (clicks, logs, IoT)

**Approaches:**
- Message queue consumers (Kafka, Pulsar, Kinesis)
- Webhooks and event triggers
- Change streams from databases

**Best practices:**
- At-least-once or exactly-once delivery guarantees
- Offset management for resumability
- Windowing and aggregation strategies
- Late data handling and watermarking

**Checklist:**
- [ ] Delivery semantics chosen (at-least-once, exactly-once)
- [ ] Offset/checkpoint strategy implemented
- [ ] Late data policy defined (e.g., 24-hour grace period)
- [ ] Windowing strategy documented
- [ ] Backpressure and rate limiting configured

---

## Pattern 3: Lineage Tracking

### Purpose

Track data provenance from **source → feature store/warehouse → model input** for reproducibility and debugging.

### What to Track

**Source metadata:**
- Source system, table, or API endpoint
- Extraction timestamp and method (CDC, batch, stream)
- Source data version or snapshot ID

**Transformation lineage:**
- Pipeline run ID and version
- Transformation logic version (git commit, DAG version)
- Dependencies on other datasets

**Model input:**
- Feature definitions and versions
- Training/serving dataset IDs
- Model version consuming the features

### Implementation

**Tag every dataset with:**
- `source_id`: Identifier for upstream source
- `pipeline_run_id`: Unique ID for ingestion/transformation job
- `data_version`: Semantic version or snapshot timestamp
- `created_at`: Processing timestamp

**Example lineage record:**

```json
{
  "dataset_id": "user_features_v2_20250322",
  "source_id": "prod_db.user_events",
  "pipeline_run_id": "airflow_dag_run_12345",
  "pipeline_version": "git:abc123",
  "created_at": "2025-03-22T10:30:00Z",
  "dependencies": ["user_profiles_v1", "event_aggregates_v3"]
}
```

### Checklist

- [ ] Every dataset tagged with source, run ID, version
- [ ] Lineage graph queryable (e.g., via data catalog)
- [ ] Reproducible: Can rebuild dataset from lineage metadata
- [ ] Debugging: Can trace model input back to raw source
- [ ] Compliance: Audit trail for regulatory requirements

---

## Pattern 4: Schema Evolution

### Strategies

**Backwards-compatible changes:**
- Add new optional columns (safe)
- Widen column types (int → bigint, varchar(50) → varchar(100))
- Relax constraints (nullable: false → true)

**Breaking changes:**
- Remove columns
- Change column types incompatibly
- Add required columns
- Rename columns

### Migration Approaches

**Shadow schema pattern:**
1. Deploy new schema alongside old schema
2. Dual-write to both schemas
3. Validate new schema in shadow mode
4. Cut over consumers to new schema
5. Deprecate old schema after grace period

**Versioned datasets:**
- Create new versioned table/view (e.g., `user_events_v2`)
- Migrate consumers incrementally
- Maintain both versions during transition
- Sunset old version after all consumers migrated

**Alert on unexpected fields:**
- Monitor for columns not in contract
- Flag schema drift in dashboards
- Block ingestion if critical fields missing

### Checklist

- [ ] Schema change policy documented
- [ ] Backwards-compatible changes preferred
- [ ] Breaking changes require versioning or shadow deployment
- [ ] Migration path tested in staging
- [ ] Consumers notified before breaking changes
- [ ] Monitoring alerts on schema drift

---

## Pattern 5: Replay & Backfill

### Purpose

Reprocess historical data after bugs, schema changes, or new features.

### Replay Requirements

**Idempotency:**
- Same input → same output
- Safe to rerun without duplicates

**Guardrails:**
- Duplicate detection (dedup keys)
- Watermarking to track processed ranges
- Dry-run mode for validation

**Auditability:**
- Log replay job ID and date range
- Track which records were reprocessed
- Compare outputs before/after replay

### Backfill Strategies

**Full reprocessing:**
- Rerun pipeline on entire history
- Use when logic changed fundamentally

**Incremental backfill:**
- Reprocess only affected date partitions
- Use when bug affects specific time range

**Dual-write/dual-read for hot swaps:**
- Write to new and old tables simultaneously
- Read from new table, fallback to old if needed
- Validate consistency before cutover

### Checklist

- [ ] Idempotency guaranteed (upsert, partition overwrite)
- [ ] Deduplication logic in place
- [ ] Watermarks tracked for partial replay
- [ ] Dry-run capability implemented
- [ ] Backfill procedure documented and tested
- [ ] Rollback plan defined

---

## Pattern 6: Data Quality Validation

### Validation Layers

**Schema validation:**
- Type checking
- Nullability enforcement
- Constraint validation (ranges, enums, patterns)

**Statistical validation:**
- Row count within expected range
- Column distributions stable (e.g., PSI < 0.1)
- Referential integrity maintained

**Business logic validation:**
- Domain-specific rules (e.g., revenue >= 0)
- Cross-column consistency (e.g., start_date <= end_date)
- Completeness checks (critical fields populated)

### Quality Gates

**Block on critical failures:**
- Schema violations
- Missing required fields
- Referential integrity broken

**Warn on non-critical issues:**
- Row count deviation > 20%
- New columns detected
- Distribution drift detected

**Monitoring:**
- Quality metrics tracked over time
- Alerts on threshold breaches
- Dashboards for data health

### Checklist

- [ ] Schema validation runs on every batch
- [ ] Statistical checks compare to baseline
- [ ] Business rules enforced
- [ ] Quality gates configured (block vs warn)
- [ ] Quality metrics logged and monitored
- [ ] Runbook for quality failures documented

---

## Real-World Example: E-Commerce Events Pipeline

### Setup

**Source:** PostgreSQL database with user events (clicks, purchases)
**Target:** Snowflake data warehouse
**Ingestion:** CDC via Debezium + Kafka
**Frequency:** Real-time (sub-minute latency)

### Data Contract

```yaml
version: 3.2.0
table: ecommerce.user_events
owner: analytics-platform
sla:
  freshness: 60sec
  completeness: 99.9%
schema:
  - name: event_id
    type: string
    primary_key: true
  - name: user_id
    type: string
    nullable: false
  - name: event_type
    type: enum
    values: [page_view, add_to_cart, purchase, refund]
  - name: product_id
    type: string
    nullable: true
  - name: revenue
    type: decimal(10,2)
    nullable: true
    constraints:
      - min: 0
  - name: timestamp
    type: timestamp
    nullable: false
```

### Lineage Tracking

Every batch tagged with:
- `source_offset`: Kafka offset range
- `cdc_timestamp`: Database transaction timestamp
- `pipeline_run_id`: Airflow DAG run ID
- `data_version`: Date partition (YYYY-MM-DD)

### Schema Evolution

When adding `attribution_source` column:
1. Add as optional column in v3.3.0
2. Deploy dual-write logic (write with/without column)
3. Validate in shadow for 1 week
4. Migrate consumers to expect new column
5. Promote to required in v4.0.0

### Quality Gates

**Block on:**
- Missing `event_id` or `user_id`
- Invalid `event_type` enum
- Negative `revenue`

**Warn on:**
- Row count deviation > 30% vs previous day
- New columns not in contract
- Lag > 5 minutes

---

## Tools & Frameworks

**CDC:**
- Debezium (log-based CDC for PostgreSQL, MySQL, MongoDB)
- AWS DMS (managed CDC for cloud databases)
- Fivetran (managed CDC with pre-built connectors)

**Batch ingestion:**
- dlt (Python library for REST APIs, databases → warehouses)
- Airbyte (open-source ELT with 300+ connectors)
- Stitch (managed ELT)

**Lineage & cataloging:**
- OpenLineage (open standard for lineage tracking)
- DataHub (LinkedIn's data catalog with lineage)
- Amundsen (Lyft's data discovery with lineage)
- Apache Atlas (Hadoop ecosystem lineage)

**Quality validation:**
- Great Expectations (Python framework for data testing)
- dbt tests (SQL-based data quality checks)
- Soda (data quality monitoring)
- Datafold (data diff and quality checks)

---

## Related Resources

- [Deployment Patterns](deployment-patterns.md) - Serving strategies after ingestion
- [Drift Detection Guide](drift-detection-guide.md) - Monitoring data drift in production
- [Monitoring Best Practices](monitoring-best-practices.md) - Observability for pipelines
- [Model Registry Patterns](model-registry-patterns.md) - Versioning and lineage for models

---

## References

- **OpenLineage Spec:** https://openlineage.io/
- **dlt Documentation:** https://dlthub.com/docs
- **Great Expectations:** https://greatexpectations.io/
- **Debezium CDC:** https://debezium.io/
- **dbt Best Practices:** https://docs.getdbt.com/guides/best-practices
