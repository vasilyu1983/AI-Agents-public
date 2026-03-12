# Data Quality & Governance Checklist

Production-ready checklist for data lake quality, governance, and reliability.

---

## Data Quality Contracts

### Contract Definition Checklist

- [ ] Schema defined (columns, types, nullable, descriptions)
- [ ] Freshness SLA defined (max staleness in hours/minutes)
- [ ] Volume bounds defined (min/max row counts per load)
- [ ] Uniqueness constraints documented (primary keys, business keys)
- [ ] Referential integrity rules documented
- [ ] Allowed value ranges specified (for numeric/date columns)
- [ ] Contract version tracked in metadata

### Quality Rules by Tier

| Tier | Completeness | Accuracy | Freshness | Volume |
|------|--------------|----------|-----------|--------|
| **Bronze** | >95% non-null required fields | Raw data unchanged | ≤ source latency + 1h | Within 2x historical avg |
| **Silver** | >99% non-null required fields | Validated against rules | ≤ Bronze + 30min | Dedupe variance <5% |
| **Gold** | 100% non-null required fields | Business rules applied | ≤ Silver + 15min | Aggregation accuracy 100% |

### Validation Implementation

```python
# Great Expectations example
expectations = [
    # Completeness
    ExpectColumnValuesToNotBeNull("user_id"),
    ExpectColumnValuesToNotBeNull("event_timestamp"),

    # Accuracy
    ExpectColumnValuesToBeBetween("price", min_value=0, max_value=1000000),
    ExpectColumnValuesToMatchRegex("email", r'^[\w\.-]+@[\w\.-]+\.\w+$'),

    # Uniqueness
    ExpectCompoundColumnsToBeUnique(["user_id", "event_timestamp"]),

    # Freshness (check max timestamp)
    ExpectColumnMaxToBeBetween(
        "event_timestamp",
        min_value=datetime.now() - timedelta(hours=1)
    ),

    # Volume
    ExpectTableRowCountToBeBetween(min_value=1000, max_value=10000000),
]
```

---

## Governance & Access Control

### IAM & Permissions Checklist

- [ ] Role-based access control (RBAC) implemented
- [ ] Data classification applied (PII, sensitive, public)
- [ ] Row-level security configured for multi-tenant data
- [ ] Column-level masking for sensitive fields
- [ ] Service accounts have least-privilege access
- [ ] Access audit logging enabled
- [ ] Access reviews scheduled quarterly

### Permission Matrix Template

| Role | Bronze | Silver | Gold | PII Columns |
|------|--------|--------|------|-------------|
| Data Engineer | Read/Write | Read/Write | Read/Write | Masked |
| Data Analyst | Read | Read | Read | Masked |
| BI User | None | None | Read | Blocked |
| ML Engineer | Read | Read | Read | Tokenized |
| Admin | Full | Full | Full | Full |

### Data Classification

| Classification | Examples | Access | Retention | Encryption |
|----------------|----------|--------|-----------|------------|
| **Public** | Product catalog, prices | All authenticated | Per policy | At rest |
| **Internal** | Sales metrics, KPIs | Internal roles | 7 years | At rest |
| **Sensitive** | Customer emails, addresses | Restricted | Per GDPR/CCPA | At rest + in transit |
| **PII** | SSN, passport, financial | Highly restricted | Minimal | At rest + in transit + masked |

---

## Security Checklist

### Encryption

- [ ] Encryption at rest enabled (S3 SSE, GCS CMEK, Azure Blob)
- [ ] Encryption in transit (TLS 1.3 for all connections)
- [ ] Key rotation policy defined (90 days recommended)
- [ ] Key management service configured (AWS KMS, GCP KMS, HashiCorp Vault)

### Network Security

- [ ] VPC/private network for data infrastructure
- [ ] No public endpoints for data stores
- [ ] Firewall rules restrict ingress/egress
- [ ] Private Link / VPC endpoints for cloud services
- [ ] Bastion host for administrative access

### Audit & Compliance

- [ ] All data access logged
- [ ] Query audit logs retained (1+ year)
- [ ] Schema change audit trail
- [ ] Data lineage tracked (DataHub, OpenMetadata)
- [ ] Compliance reports automated (SOC2, GDPR, HIPAA as applicable)

---

## Reliability Patterns

### Backfill & Reprocessing Checklist

- [ ] Idempotent pipelines (re-run safe)
- [ ] Partition-based backfill supported
- [ ] Historical data retention policy defined
- [ ] Backfill runbook documented
- [ ] Backfill testing in staging environment
- [ ] Alerting for long-running backfills

### Backfill Procedure Template

```text
## Backfill Procedure: [Table Name]

### Pre-backfill
1. [ ] Identify affected partitions/date range
2. [ ] Estimate resource requirements (time, compute)
3. [ ] Notify downstream consumers
4. [ ] Take snapshot of current state (if destructive)

### Execution
1. [ ] Disable downstream dependencies (or pause)
2. [ ] Run backfill: `sqlmesh run --start-date 2024-01-01 --end-date 2024-03-01`
3. [ ] Monitor progress and resource usage
4. [ ] Validate row counts match expectations

### Post-backfill
1. [ ] Run data quality checks
2. [ ] Compare metrics before/after (spot check)
3. [ ] Re-enable downstream dependencies
4. [ ] Update documentation with backfill date
5. [ ] Notify stakeholders of completion
```

### Idempotency Patterns

| Pattern | Use When | Implementation |
|---------|----------|----------------|
| **REPLACE partition** | Full partition reload | `INSERT OVERWRITE PARTITION (date='2024-01-01')` |
| **MERGE/UPSERT** | Incremental with updates | `MERGE INTO target USING source ON key` |
| **Deduplication** | Event replay tolerance | `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC)` |
| **Tombstone markers** | Soft deletes | `is_deleted` flag + filter in views |

---

## Cost Control Checklist

### Storage Optimization

- [ ] Partitioning strategy defined (by date, region, etc.)
- [ ] Compaction scheduled (Iceberg: daily, target 512MB files)
- [ ] Snapshot expiration policy (keep 7 days)
- [ ] Z-ordering/clustering on common filter columns
- [ ] Compression enabled (Zstd recommended)
- [ ] Cold storage tiering for old data

### Compute Optimization

- [ ] Query result caching enabled
- [ ] Materialized views for expensive aggregations
- [ ] Resource quotas per user/team
- [ ] Auto-scaling configured with limits
- [ ] Idle cluster shutdown policy
- [ ] Cost attribution tags on all resources

### Cost Monitoring

- [ ] Daily cost reports configured
- [ ] Budget alerts at 50%, 80%, 100%
- [ ] Cost anomaly detection enabled
- [ ] Monthly cost review meeting scheduled
- [ ] Chargeback/showback model defined

---

## Do / Avoid

### GOOD: Do

- Define data contracts before building pipelines
- Implement quality gates at each tier (Bronze → Silver → Gold)
- Use idempotent operations for all transformations
- Enable audit logging from day one
- Automate data quality checks in CI/CD
- Document SLAs for every critical table
- Plan for backfills in pipeline design

### BAD: Avoid

- Skipping data quality validation to "move fast"
- Storing PII without classification and access controls
- Creating pipelines that can't be re-run safely
- Using shared service accounts without audit trails
- Ignoring cost controls until the bill arrives
- Manual schema changes without version control
- Single point of failure in critical pipelines

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Schema on read only** | Quality issues discovered too late | Add schema validation at Bronze layer |
| **No freshness SLA** | Stale data used in decisions | Define and monitor freshness contracts |
| **Single partition strategy** | Query costs explode | Partition by most common filter column |
| **Unversioned schemas** | Breaking changes surprise consumers | Use schema registry + contracts |
| **No data owner** | Accountability vacuum | Assign owner to every dataset |
| **Manual data fixes** | Untraceable changes | All fixes through versioned pipelines |

---

## Optional: AI/Automation

> **Note**: These are enhancements, not requirements. Implement only after core governance is solid.

### Automated Quality Monitoring

- Anomaly detection on data volumes and distributions
- Auto-alerting on schema drift
- ML-based freshness prediction

### AI-Assisted Governance

- Auto-classification of PII columns using NLP
- Metadata enrichment from column statistics
- Natural language data catalog search

### Bounded Claims

- AI quality detection should **supplement**, not replace, explicit rules
- Human review required for PII classification decisions
- Auto-generated metadata must be validated before production use

---

## Related Templates

- [template-medallion-architecture.md](template-medallion-architecture.md) — Bronze/Silver/Gold patterns
- [template-data-quality.md](template-data-quality.md) — Great Expectations integration
- [template-cost-optimization.md](template-cost-optimization.md) — Storage and compute cost control

---

**Last Updated**: December 2025
