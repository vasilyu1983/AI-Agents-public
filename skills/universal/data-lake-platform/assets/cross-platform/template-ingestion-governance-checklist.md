# Data Lake Ingestion & Governance Checklist

Use this checklist when onboarding a new source, dataset, or data product into a lake/lakehouse.

## 1) Dataset Intake

- Dataset name:
- Business owner:
- Technical owner/on-call:
- Source system(s):
- Consumers (dashboards, ML features, downstream services):
- Data classification: public / internal / confidential / restricted (PII/PHI/PCI)
- Freshness target (SLA/SLO):
- Retention requirements (legal/regulatory + business):

## 2) Ingestion Design (Batch / Streaming / CDC)

- [ ] Ingestion mode chosen: batch / streaming / CDC
- [ ] Contract defined:
  - [ ] Schema (types, nullability, semantics)
  - [ ] Primary key / natural key / dedupe key
  - [ ] Event time vs processing time (if applicable)
  - [ ] Allowed late data window (if applicable)
  - [ ] Delete semantics: hard deletes, soft-delete flag, or tombstones — and how each reaches the lake
- [ ] Idempotency strategy:
  - [ ] Upsert/merge keys defined
  - [ ] Re-runs are safe (no double counts)
  - [ ] Exactly-once is not assumed; use at-least-once + dedupe
- [ ] Schema evolution policy:
  - [ ] Additive changes allowed by default
  - [ ] Breaking changes require versioning and consumer notice
  - [ ] Backward/forward compatibility rules documented
- [ ] Failure handling:
  - [ ] Dead-letter/quarantine path defined
  - [ ] Retries with backoff/jitter
  - [ ] Partial loads are detectable and alertable

## 3) Storage and Table Format

- [ ] Table format chosen (open, multi-engine where possible)
- [ ] Partitioning/clustering strategy documented (aligned to common filters)
- [ ] Compaction/maintenance plan (small files, manifests, vacuum) scheduled
- [ ] Naming conventions and dataset layout standardized

## 4) Governance and Access Control

- [ ] Catalog entry created (owner, description, tags, lineage links)
- [ ] Data classification tags applied (PII columns identified)
- [ ] RBAC policy defined (who can read/write/admin)
- [ ] Row/column-level security policy defined (where required)
- [ ] Audit logging enabled for access and schema changes
- [ ] Encryption in transit and at rest verified

## 5) Quality Gates and Reliability

- [ ] Data quality checks defined (schema, not-null, uniqueness, ranges, freshness)
- [ ] SLAs/SLOs defined and monitored (freshness, completeness, latency)
- [ ] Backfill strategy documented (time window, compute budget, verification)
- [ ] Reprocessing strategy documented (how to rebuild from source of truth)
- [ ] Runbook exists for top failure modes (late data, schema change, upstream outage)

## 6) Cost Controls

- [ ] Retention and lifecycle policy enforced (tiering, deletion, archival)
- [ ] Compute guardrails (quotas, scheduling, environment budgets)
- [ ] Query cost controls (partition pruning, pre-aggregations, caching)
- [ ] Regular maintenance jobs scheduled (compaction, stats, clustering)

Strategy details: [ingestion-patterns.md](../../references/ingestion-patterns.md). Automated PII or metadata suggestions need human validation before policy applies.
