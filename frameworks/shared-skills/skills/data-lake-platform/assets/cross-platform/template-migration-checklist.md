# Migration Checklist Template

## Overview

Step-by-step checklist for migrating data platforms to modern lakehouse architecture.

---

## Pre-Migration Assessment

### Source System Inventory

- [ ] **Document all source systems**
  - Databases (PostgreSQL, MySQL, SQL Server, Oracle)
  - APIs (REST, GraphQL, webhooks)
  - File systems (SFTP, S3, local)
  - SaaS applications (Salesforce, HubSpot, Stripe)

- [ ] **Catalog existing data**
  - Table names, schemas, row counts
  - Data volumes (GB/TB per table)
  - Update frequencies (real-time, hourly, daily, batch)
  - Data quality issues (nulls, duplicates, inconsistencies)

- [ ] **Map dependencies**
  - Downstream consumers (dashboards, reports, APIs)
  - ETL pipelines (Airflow DAGs, cron jobs, stored procedures)
  - Business-critical queries and SLAs

### Current State Assessment

```text
┌─────────────────────────────────────────────────────────────┐
│ CURRENT STATE ASSESSMENT                                    │
├─────────────────────────────────────────────────────────────┤
│ Source Systems: ______ (count)                             │
│ Total Data Volume: ______ TB                               │
│ Daily Ingestion: ______ GB                                 │
│ Active Users: ______                                       │
│ Critical Dashboards: ______                                │
│ SLA Requirements: ______                                   │
│ Current Monthly Cost: $______                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Design

### Target Architecture Selection

- [ ] **Choose lakehouse pattern**
  - [ ] Medallion (Bronze/Silver/Gold) - recommended for most cases
  - [ ] Data Mesh (domain-oriented) - for large organizations
  - [ ] Lambda/Kappa (streaming) - for real-time requirements

- [ ] **Select core technologies**

| Layer | Technology | Alternative |
|-------|------------|-------------|
| Ingestion | dlt | Airbyte |
| Storage | Iceberg | Delta Lake |
| Transformation | SQLMesh | dbt |
| Query Engine | ClickHouse | DuckDB, Doris |
| Orchestration | Dagster | Airflow |
| Catalog | OpenMetadata | DataHub |

- [ ] **Define data zones**

```text
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   BRONZE    │──→│   SILVER    │──→│    GOLD     │
│ (Raw/Lake)  │   │ (Validated) │   │  (Marts)    │
└─────────────┘   └─────────────┘   └─────────────┘
     │                  │                  │
  Append-only      Deduplicated      Business-ready
  Schema-on-read   Schema-enforced   Aggregated
  Full history     Current state     Domain models
```

### Infrastructure Planning

- [ ] **Storage requirements**
  - Current data size: ______ TB
  - 3-year projection: ______ TB
  - Hot storage: ______ TB (SSD/NVMe)
  - Warm storage: ______ TB (HDD/S3 Standard)
  - Cold storage: ______ TB (S3 Glacier)

- [ ] **Compute requirements**
  - Peak concurrent queries: ______
  - Average query complexity: ______
  - Batch processing windows: ______

- [ ] **Network requirements**
  - Data transfer between regions: ______ GB/day
  - Egress costs consideration

---

## Migration Phases

### Phase 1: Foundation (Weeks 1-2)

- [ ] **Set up infrastructure**
  - [ ] Provision object storage (S3/MinIO/GCS)
  - [ ] Deploy query engine (ClickHouse cluster)
  - [ ] Configure Iceberg REST catalog
  - [ ] Set up orchestration (Dagster/Airflow)

- [ ] **Configure security**
  - [ ] IAM roles and policies
  - [ ] Network security groups
  - [ ] Encryption at rest and in transit
  - [ ] Secrets management (Vault, AWS Secrets Manager)

- [ ] **Establish CI/CD**
  - [ ] Git repository structure
  - [ ] SQLMesh/dbt project scaffolding
  - [ ] Testing framework (Great Expectations/Soda)
  - [ ] Deployment pipelines

### Phase 2: Bronze Layer (Weeks 3-4)

- [ ] **Implement ingestion pipelines**

```python
# Example: dlt pipeline for each source
@dlt.source
def source_system():
    @dlt.resource(
        write_disposition="append",
        table_format="iceberg"
    )
    def table_name():
        yield from fetch_data()
    return table_name

pipeline = dlt.pipeline(
    pipeline_name="bronze_ingestion",
    destination="filesystem",
    dataset_name="bronze"
)
```

- [ ] **Source system checklist**
  - [ ] Source 1: ______ (status: pending/in-progress/complete)
  - [ ] Source 2: ______
  - [ ] Source 3: ______
  - [ ] Source N: ______

- [ ] **Validate bronze data**
  - [ ] Row counts match source
  - [ ] Schema captured correctly
  - [ ] Incremental logic working
  - [ ] Historical data backfilled

### Phase 3: Silver Layer (Weeks 5-6)

- [ ] **Build staging models**

```sql
-- SQLMesh model example
MODEL (
  name silver.stg_customers,
  kind INCREMENTAL_BY_UNIQUE_KEY (unique_key [customer_id]),
  audits (not_null(columns=[customer_id, email]), unique(columns=[customer_id]))
);

SELECT
    id AS customer_id,
    lower(trim(email)) AS email,
    name,
    created_at,
    updated_at
FROM bronze.raw_customers
WHERE id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) = 1;
```

- [ ] **Silver layer checklist**
  - [ ] Deduplication logic verified
  - [ ] Data type conversions correct
  - [ ] Null handling defined
  - [ ] Data quality checks passing
  - [ ] Schema documentation complete

### Phase 4: Gold Layer (Weeks 7-8)

- [ ] **Build business models**
  - [ ] Fact tables (events, transactions, activities)
  - [ ] Dimension tables (users, products, locations)
  - [ ] Aggregation tables (daily/weekly/monthly metrics)

- [ ] **Migrate existing reports**
  - [ ] Identify all dashboard queries
  - [ ] Map to new gold tables
  - [ ] Validate results match legacy system
  - [ ] Document query migration

### Phase 5: Cutover (Weeks 9-10)

- [ ] **Parallel run period**
  - [ ] Run old and new systems simultaneously
  - [ ] Compare query results daily
  - [ ] Measure performance differences
  - [ ] Document discrepancies

- [ ] **User acceptance testing**
  - [ ] Train users on new system
  - [ ] Collect feedback
  - [ ] Address issues
  - [ ] Sign-off from stakeholders

- [ ] **Production cutover**
  - [ ] Schedule cutover window
  - [ ] Notify all stakeholders
  - [ ] Execute cutover runbook
  - [ ] Monitor for issues
  - [ ] Rollback plan ready

---

## Validation Checklist

### Data Accuracy

```sql
-- Compare row counts
SELECT 'old_system' AS source, count(*) FROM old_db.customers
UNION ALL
SELECT 'new_system' AS source, count(*) FROM gold.dim_customers;

-- Compare aggregates
SELECT 'old_system', sum(amount), avg(amount) FROM old_db.orders
UNION ALL
SELECT 'new_system', sum(amount), avg(amount) FROM gold.fct_orders;

-- Sample comparison (random 1000 records)
SELECT * FROM old_db.customers
WHERE id IN (SELECT id FROM old_db.customers ORDER BY rand() LIMIT 1000)
EXCEPT
SELECT * FROM gold.dim_customers
WHERE customer_id IN (...);
```

### Performance Benchmarks

- [ ] **Query performance comparison**

| Query | Old System | New System | Improvement |
|-------|------------|------------|-------------|
| Daily sales report | ______ sec | ______ sec | ______% |
| User cohort analysis | ______ sec | ______ sec | ______% |
| Product metrics | ______ sec | ______ sec | ______% |

### Data Quality Metrics

- [ ] **Quality gate thresholds**
  - Completeness: >99.9% for required fields
  - Uniqueness: 0 duplicates on primary keys
  - Validity: >99% pass format checks
  - Freshness: Within SLA (e.g., <24 hours)

---

## Post-Migration

### Documentation

- [ ] **Technical documentation**
  - [ ] Architecture diagrams
  - [ ] Data flow diagrams
  - [ ] Schema documentation
  - [ ] Runbooks for common operations

- [ ] **User documentation**
  - [ ] Data dictionary
  - [ ] Query examples
  - [ ] Dashboard guide
  - [ ] FAQ

### Monitoring Setup

- [ ] **Alerts configured**
  - [ ] Pipeline failures
  - [ ] Data freshness SLA breaches
  - [ ] Quality check failures
  - [ ] Resource usage thresholds

- [ ] **Dashboards created**
  - [ ] Pipeline health dashboard
  - [ ] Data quality dashboard
  - [ ] Cost tracking dashboard
  - [ ] Performance metrics dashboard

### Decommissioning

- [ ] **Legacy system retirement**
  - [ ] Confirm all consumers migrated
  - [ ] Export final data snapshot
  - [ ] Archive for compliance (if required)
  - [ ] Terminate resources
  - [ ] Update documentation

---

## Risk Mitigation

### Common Risks

| Risk | Mitigation |
|------|------------|
| Data loss | Multiple backups, point-in-time recovery |
| Performance regression | Benchmark before cutover, optimize queries |
| Schema drift | Schema registry, automated testing |
| Downtime | Blue-green deployment, rollback plan |
| Cost overrun | Budget monitoring, cost alerts |

### Rollback Plan

```text
ROLLBACK PROCEDURE
─────────────────
1. STOP new system ingestion pipelines
2. VERIFY old system still receiving data
3. REDIRECT dashboards to old system
4. NOTIFY users of rollback
5. INVESTIGATE root cause
6. PLAN remediation
7. SCHEDULE retry
```

---

## Success Criteria

### Business Metrics

- [ ] Query performance: ≥______% improvement
- [ ] Data freshness: ≤______ hours
- [ ] Cost reduction: ≥______% savings
- [ ] User satisfaction: ≥______% positive feedback

### Technical Metrics

- [ ] Pipeline success rate: ≥99.5%
- [ ] Data quality score: ≥99%
- [ ] System availability: ≥99.9%
- [ ] P99 query latency: ≤______ seconds
