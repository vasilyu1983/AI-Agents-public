# Data Quality and Governance Checklist

Use before declaring a lake table production-ready. Test implementation (GX, Soda, dbt/SQLMesh audits): `data-analytics-engineering`. Access, masking, and erasure: [security-access-patterns.md](../../references/security-access-patterns.md). Cost controls: [cost-optimization.md](../../references/cost-optimization.md).

## Contract (per table, before the first production write)

- [ ] Schema: columns, types, nullability, descriptions; version tracked
- [ ] Freshness SLA (max staleness) and who is paged
- [ ] Volume bounds per load, derived from history (not guessed)
- [ ] Uniqueness: primary/business key and grain
- [ ] Referential integrity to named upstream tables
- [ ] Allowed ranges/values for numeric, date, and enum columns
- [ ] Owner and data classification (public / internal / sensitive / PII)

## Quality Gates by Layer

Tighten the gate at each layer; set the actual thresholds per table in its contract, from observed history.

| Layer | Gate |
|-------|------|
| Bronze | Load arrived, schema readable, row count within bounds; do not reject on content |
| Silver | Required fields complete, key unique, types valid, rejects quarantined with reason |
| Gold | Required fields complete, grain unique, totals reconcile to silver |

Freshness checks compare the max event/commit timestamp against the SLA at query time; a check that only runs after a successful load never fires when the load stops.

## Governance

- [ ] Role matrix per layer: engineers write bronze/silver/gold; analysts read silver/gold; BI users read gold only; PII masked or tokenized for everyone without a PII role
- [ ] Row-level security for multi-tenant tables; column masks for sensitive fields
- [ ] Per-pipeline service principals with least privilege; no shared credentials
- [ ] Access audit logging on; periodic access reviews
- [ ] Lineage emitted (OpenLineage or platform-native) and visible in the catalog

## Reliability

- [ ] Every pipeline is idempotent for a logical interval (see idempotency patterns below)
- [ ] Partition-scoped backfill supported and rehearsed in staging: [template-data-quality-backfill-runbook.md](template-data-quality-backfill-runbook.md)
- [ ] Snapshot retention covers the recovery objective; compaction and orphan cleanup scheduled

| Idempotency pattern | Use when | Mechanism |
|---------------------|----------|-----------|
| Replace partition | Full reload of a bounded slice | `INSERT OVERWRITE` / dynamic partition overwrite for exactly the slice |
| Merge / upsert | Incremental with updates | `MERGE INTO target USING source ON key` with an ordering guard (`source.updated_at > target.updated_at`) |
| Dedup on read/write | At-least-once replay | `ROW_NUMBER()` over key ordered by source version |
| Tombstones | Soft deletes that must propagate | `is_deleted` flag, applied as a hard delete or filtered in every consumer |

Dynamic partition overwrite with a filter that is wider or narrower than the recomputed data silently deletes or duplicates partitions — scope the overwrite to exactly the partitions the job recomputed.

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| No freshness SLA | Define and monitor per table |
| Unversioned schemas | Contracts + schema registry; breaking changes go through consumers |
| No owner | Every table has an owner in the catalog |
| Manual data fixes | All fixes via versioned pipelines and backfills |
| AI-only PII classification | Use it to suggest; a human confirms before policy applies |
