# Data Lake Ingestion & Governance Checklist

Use this checklist when onboarding a new source, dataset, or data product into a lake/lakehouse.

---

## Core

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

---

## Do / Avoid

### Do

- Do define contracts and ownership before building pipelines
- Do plan for backfills and reprocessing from day one
- Do enforce least privilege and audit trails for sensitive datasets
- Do design partitions for the queries you will run (not for aesthetics)

### Avoid

- Avoid relying on “schema on read” without validation gates
- Avoid shared service accounts with no traceability
- Avoid unbounded retention and unbounded scans (cost runaway)
- Avoid pipelines that cannot be replayed safely

---

## Optional: AI/Automation

- Auto-detect anomalies (volume, distribution, freshness) as a supplement to rules
- Assist with metadata enrichment (tags, owners, column descriptions) with review
- Suggest partition keys from observed query patterns (human-approved)

### Bounded Claims

- Automation does not replace explicit contracts, tests, or access controls.
- PII classification suggestions require human validation.
