# Data Pipeline Code Review Checklist

Specialized checklist for reviewing data processing pipelines, ETL/ELT workflows, and feature engineering pipelines.

---

## Pipeline Architecture

### Design Principles
- [ ] Pipeline purpose and scope clearly defined
- [ ] Data flow diagram documented
- [ ] Input/output contracts specified
- [ ] Pipeline stages logically separated
- [ ] Idempotency ensured (can re-run safely)
- [ ] Incremental processing strategy defined

### Orchestration
- [ ] Orchestration tool appropriate (Airflow, Prefect, Dagster, etc.)
- [ ] DAG structure clear and logical
- [ ] Dependencies explicitly defined
- [ ] Task granularity appropriate
- [ ] Parallel execution opportunities identified
- [ ] Critical path optimized

### Scalability
- [ ] Data volume growth considered
- [ ] Processing strategy scales (batch vs streaming)
- [ ] Resource requirements documented
- [ ] Bottlenecks identified and addressed
- [ ] Partitioning strategy defined

---

## Data Ingestion

### Source Integration
- [ ] Data sources documented (APIs, databases, files)
- [ ] Authentication/authorization handled securely
- [ ] Rate limiting respected
- [ ] Connection pooling configured
- [ ] Retry logic with exponential backoff
- [ ] Timeout settings appropriate

### Data Extraction
- [ ] Incremental loading strategy defined
- [ ] Full refresh vs incremental logic clear
- [ ] Watermarks/checkpoints tracked
- [ ] Change data capture (CDC) if applicable
- [ ] Deleted records handled
- [ ] Schema evolution handled

### Error Handling
- [ ] Transient failures retried appropriately
- [ ] Permanent failures logged and alerted
- [ ] Partial failures don't block entire pipeline
- [ ] Dead letter queue for failed records
- [ ] Circuit breaker pattern for flaky sources

---

## Data Validation

### Schema Validation
- [ ] Input schema validated on ingestion
- [ ] Column types enforced
- [ ] Required fields checked
- [ ] Schema drift detected
- [ ] Schema versions tracked
- [ ] Breaking changes prevented

### Data Quality Checks
- [ ] Null/missing value checks
- [ ] Range/bound checks on numeric fields
- [ ] Format validation on strings/dates
- [ ] Referential integrity checks
- [ ] Duplicate detection
- [ ] Anomaly detection for data distribution

### Business Logic Validation
- [ ] Domain-specific rules validated
- [ ] Cross-field consistency checked
- [ ] Business constraints enforced
- [ ] Data completeness verified
- [ ] Thresholds for acceptable data quality defined

---

## Data Transformation

### Transformation Logic
- Baseline `CC-*` to apply (cite IDs if violated): `CC-DOC-01`, `CC-FUN-01`, `CC-FUN-04`, `CC-TYP-04`, `CC-NAM-03`
- [ ] Timezone handling explicit
- [ ] Date/time arithmetic correct

### Feature Engineering
- [ ] Feature transformations reproducible
- [ ] No train/serve skew in features
- [ ] Feature statistics computed from training data only
- [ ] Feature store integration (if applicable)
- [ ] Feature versioning tracked
- [ ] No data leakage in feature creation

### Performance Optimization
- [ ] Efficient SQL queries (proper joins, filters, indexes)
- [ ] Data shuffles minimized
- [ ] Unnecessary computations eliminated
- [ ] Caching used for expensive operations
- [ ] Broadcast joins for small tables (Spark)
- [ ] Partitioning strategy optimized

---

## Data Storage

### Storage Strategy
- [ ] Storage format appropriate (Parquet, Delta, Iceberg, etc.)
- [ ] Partitioning scheme efficient
- [ ] Compression enabled
- [ ] Data lifecycle policy defined
- [ ] Cold storage strategy for old data
- [ ] Retention periods documented

### Data Organization
- [ ] Staging/intermediate/marts layers clear
- [ ] Naming is consistent and intention-revealing (cite `CC-NAM-01`, `CC-NAM-02`, `CC-NAM-03`)
- [ ] Directory structure logical
- [ ] Metadata tracked (lineage, timestamps, versions)
- [ ] Access controls configured

### Data Versioning
- [ ] Data versions tracked
- [ ] Snapshots available for reproducibility
- [ ] Rollback strategy defined
- [ ] Version compatibility documented

---

## Monitoring & Observability

### Pipeline Monitoring
- [ ] Pipeline execution metrics tracked
- [ ] Processing duration monitored
- [ ] Record counts logged
- [ ] Success/failure rates tracked
- [ ] Resource utilization monitored (CPU, memory, I/O)

### Data Monitoring
- [ ] Data volume trends tracked
- [ ] Data quality metrics computed
- [ ] Schema changes detected
- [ ] Distribution shifts detected (data drift)
- [ ] Missing data alerts configured

### Alerting
- [ ] Critical failures trigger alerts
- [ ] Data quality violations trigger alerts
- [ ] SLA breaches trigger alerts
- [ ] Alert fatigue avoided (appropriate thresholds)
- [ ] Runbook linked to alerts

---

## Testing

### Unit Tests
- [ ] Transformation functions unit tested
- [ ] Edge cases covered
- [ ] Null handling tested
- [ ] Data type conversions tested
- [ ] Business logic validated

### Integration Tests
- [ ] End-to-end pipeline tested on sample data
- [ ] Source connections tested
- [ ] Destination writes tested
- [ ] Error handling paths tested
- [ ] Rollback tested

### Data Tests
- [ ] Expected schema tests
- [ ] Row count tests
- [ ] Uniqueness tests
- [ ] Non-null tests
- [ ] Referential integrity tests
- [ ] Regression tests for known issues

---

## Error Handling & Recovery

### Failure Modes
- [ ] Transient vs permanent failures distinguished
- [ ] Retry logic with exponential backoff
- [ ] Max retry limits defined
- [ ] Circuit breaker for repeated failures
- [ ] Graceful degradation where possible

### Recovery Mechanisms
- [ ] Checkpoint/resume capability
- [ ] Idempotent operations (safe to re-run)
- [ ] Rollback procedures documented
- [ ] Manual intervention triggers clear
- [ ] Data reconciliation after failures

### Logging
- [ ] Structured logging used
- [ ] Log levels appropriate (DEBUG, INFO, WARN, ERROR)
- [ ] Sensitive data not logged
- [ ] Correlation IDs for tracing
- [ ] Logs retained per policy

---

## Security & Privacy

### Data Security
- [ ] Data encrypted in transit (TLS)
- [ ] Data encrypted at rest (where required)
- [ ] Access controls enforced (IAM, RBAC)
- [ ] Secrets managed securely (vault, env vars)
- [ ] No credentials in code or logs
- [ ] Audit logs enabled

### Privacy Compliance
- [ ] PII identified and classified
- [ ] Data anonymization/pseudonymization applied
- [ ] Data retention policies followed
- [ ] Right to deletion supported
- [ ] Compliance requirements documented (GDPR, CCPA, etc.)
- [ ] Data lineage tracked for audits

### Data Governance
- [ ] Data ownership documented
- [ ] Data classification applied
- [ ] Access requests logged
- [ ] Data sharing agreements followed
- [ ] Compliance audits supported

---

## Clean Code (Core)

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Standards: cite `CC-*` IDs; do not restate rules.
- Common `CC-*` IDs for data pipelines: `CC-NAM-01`, `CC-NAM-03`, `CC-FUN-01`, `CC-FUN-05`, `CC-TYP-01`, `CC-TYP-04`, `CC-ERR-01`, `CC-ERR-04`, `CC-SEC-03`, `CC-SEC-05`, `CC-DOC-01`, `CC-DOC-04`, `CC-TST-01`

### Configuration Management

- [ ] Configuration is externalized (not hardcoded) and environment differences are explicit.
- [ ] Configuration is validated on startup; defaults are safe for production.

### Documentation

- [ ] Pipeline purpose and contracts documented (inputs, outputs, failure modes).
- [ ] Setup and troubleshooting steps are clear; runbook exists for on-call.

---

## Performance & Efficiency

### Resource Utilization
- [ ] Memory usage optimized (lazy loading, chunking)
- [ ] CPU utilization efficient
- [ ] Network I/O minimized
- [ ] Disk I/O minimized
- [ ] Parallelization used where beneficial

### Cost Optimization
- [ ] Compute resources right-sized
- [ ] Storage costs optimized (compression, lifecycle)
- [ ] Spot/preemptible instances used where appropriate
- [ ] Cost monitoring enabled
- [ ] Cost budget alerts configured

### Latency Optimization
- [ ] Pipeline duration meets SLA
- [ ] Critical path optimized
- [ ] Unnecessary dependencies eliminated
- [ ] Caching used for repeated computations
- [ ] Data locality optimized (avoid shuffles)

---

## Production Readiness

### Deployment
- [ ] CI/CD pipeline configured
- [ ] Automated testing in CI
- [ ] Deployment strategy defined (blue/green, canary)
- [ ] Rollback procedure documented
- [ ] Environment parity (dev/staging/prod)

### Maintenance
- [ ] Monitoring dashboards created
- [ ] Alert rules configured
- [ ] Runbook complete
- [ ] On-call rotation defined
- [ ] Incident response process documented

### Documentation
- [ ] Architecture diagram available
- [ ] Data dictionary maintained
- [ ] SLA/SLO documented
- [ ] Owners and contacts listed
- [ ] Handover documentation complete

---

## SQLMesh Specific (if applicable)

### Model Configuration
- [ ] Model types appropriate (FULL, INCREMENTAL_BY_TIME_RANGE, etc.)
- [ ] Incremental strategy correct
- [ ] Partitioning aligned with incremental key
- [ ] Dependencies (ref()) correct
- [ ] Model descriptions provided

### Testing & Validation
- [ ] Unit tests for model logic
- [ ] Audits for data quality
- [ ] CI/CD integration configured
- [ ] Test data fixtures provided

### Best Practices
- [ ] Staging/intermediate/marts layers clear
- [ ] Incremental models for large tables
- [ ] Backfill strategy defined
- [ ] Environment promotion workflow

---

## Final Checklist

Before approving data pipeline code:
- [ ] Pipeline runs successfully end-to-end
- [ ] Data quality checks passing
- [ ] Tests passing
- [ ] Monitoring and alerting configured
- [ ] Documentation complete
- [ ] Security and privacy reviewed
- [ ] Production deployment plan reviewed
