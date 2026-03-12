# Data Quality & Backfill Runbook Template

Use this runbook when data is late, incorrect, missing, or when you need to reprocess a historical window safely.

---

## Core

## Runbook Metadata

- Incident/ticket ID:
- Date/time (timezone):
- Owner/on-call:
- Affected datasets/tables:
- Downstream consumers impacted:
- Severity:

## Trigger

- Freshness SLA breach
- Quality check failure (schema, nulls, duplicates, ranges)
- Upstream source correction
- Pipeline bug fix requiring reprocessing

## Safety Checks (Before Action)

- [ ] Confirm source of truth for the backfill window
- [ ] Confirm idempotency/replay behavior (upsert keys, dedupe keys)
- [ ] Confirm downstream behavior (will consumers auto-refresh?)
- [ ] Confirm compute budget and expected runtime
- [ ] Decide whether to pause downstream jobs during backfill

## Backfill Plan

### Window and Strategy

- Backfill window: start/end
- Strategy: overwrite partition / merge-upsert / append + reconcile
- Expected output partitions/tables:

### Execution Steps

1. Create a backfill branch/tag for pipeline config (auditability).
2. Run the backfill job for the defined window.
3. Capture job outputs (row counts, runtime, error logs).
4. Run validation suite (see below).
5. Re-enable downstream jobs and verify end-to-end freshness.

## Validation (Must Pass Before Closing)

### Contract Checks

- [ ] Schema matches contract (types, nullability)
- [ ] Primary/dedupe keys unique within window
- [ ] Freshness updated and within SLA

### Data Quality Checks

- [ ] Row-count sanity vs baseline (bounds)
- [ ] Null-rate and distribution checks (key columns)
- [ ] Business invariants hold (e.g., totals, monotonicity)

### Consumer Checks

- [ ] Dashboards refreshed and consistent
- [ ] Downstream tables rebuilt (if applicable)
- [ ] Sampling spot-check completed

## Rollback Plan

- Rollback trigger:
- Rollback mechanism (restore snapshot / revert partitions / rerun last-known-good):
- Verification after rollback:

## Communication

- Internal channel:
- Stakeholder update cadence:
- Customer-facing update needed: yes/no

## Post-Incident Follow-Up

- Root cause summary:
- Preventive actions (tests, monitors, contracts, process):
- Runbook updates required:

---

## Optional: AI/Automation

- Summarize validation results and highlight anomalies (human-verified)
- Suggest likely root causes from recent schema changes and upstream events (human-validated)
- Auto-generate stakeholder updates from structured runbook fields (human-approved)

### Bounded Claims

- Automation cannot determine correctness without explicit rules and human review.
- Never auto-apply destructive backfills without an approval workflow.
