# Migration Checklist Template

Use when moving a warehouse, Hive/Parquet estate, or legacy ETL onto a lakehouse. Target-stack choices: [SKILL.md](../../SKILL.md) decision tree and proof matrix. Table-format migration steps (in-place vs rewrite): [operational-playbook.md](../../references/operational-playbook.md#migrations).

## Assess (before choosing anything)

- [ ] Inventory sources (databases, APIs, files, SaaS) with volume, change rate, and **delete semantics** for each.
- [ ] Map every downstream consumer (dashboards, reports, APIs, exports) and the SLA it depends on — this list defines "done".
- [ ] Record the current cost, freshness, and the slowest business-critical queries: they are the comparison baseline.
- [ ] Run the interoperability proof matrix for the target format, catalog, and engines before provisioning.

## Sequence

Migrate by consumer slice (one business area end to end), not by layer across the whole estate. Each slice:

1. **Bronze**: ingest the slice's sources; row counts match source per table; incremental and delete handling proven; history backfilled.
2. **Silver**: dedup, typing, and null handling verified; quality checks pass.
3. **Gold**: rebuild the slice's reports on gold tables.
4. **Parallel run**: both systems fed and queried; compare daily (below) for an agreed period covering at least one month-end or other business-cycle peak.
5. **Cutover**: redirect consumers; keep the legacy system fed and read-only until the rollback window closes.

## Reconciliation — Prove Equality, Not Similarity

- Row counts per table **and per partition/day**; totals alone hide offsetting errors.
- Aggregates on money and key metrics compared with an explicit tolerance (exact for `DECIMAL`, stated epsilon for floats).
- **Symmetric** row diff on a sample of keys: `old EXCEPT new` **and** `new EXCEPT old`; one direction misses extra or duplicated rows.
- Normalize before diffing: time zones, NULL vs empty string, trailing spaces, decimal scale — otherwise every row "differs" and real errors hide in the noise.
- Business sign-off on the top reports, compared number by number.

## Cutover and Rollback

- [ ] Written rollback runbook: stop new-system ingestion, confirm the old system is still current, redirect dashboards, notify users, then investigate.
- [ ] Rollback is possible only while the legacy system is still fed — decide the window up front.
- [ ] Monitoring live on day one: pipeline failures, freshness, quality checks, cost.

## Decommission

- [ ] Every consumer confirmed migrated (from the consumer map, not from memory).
- [ ] Final snapshot exported and archived where retention rules require it.
- [ ] Legacy resources terminated; credentials revoked; docs updated.

## Risks

| Risk | Mitigation |
|------|------------|
| Silent data loss | Per-partition reconciliation, symmetric diffs, parallel run |
| Performance regression | Benchmark the baseline queries before cutover |
| Schema drift during migration | Contracts and automated schema checks on both sides |
| Cost overrun | Budget alerts; compaction and retention scheduled from day one |
| Big-bang cutover | Slice-by-slice migration with a rollback window per slice |
