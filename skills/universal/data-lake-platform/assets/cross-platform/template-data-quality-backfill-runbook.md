# Data Quality & Backfill Runbook Template

Use this runbook when data is late, incorrect, missing, or when you need to reprocess a historical window safely.

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
- [ ] Decide whether to pause downstream jobs during backfill (default: pause, so consumers never read a half-rewritten window)
- [ ] Record the current snapshot/version id of every table the backfill writes (this is the rollback point)
- [ ] Confirm snapshot retention will not expire that rollback point before the backfill is validated

## Backfill Plan

### Window and Strategy

- Backfill window: start/end
- Strategy: overwrite partition / merge-upsert / append + reconcile
- Expected output partitions/tables:

### Execution Steps

1. Create a backfill branch/tag for pipeline config (auditability).
2. Run the backfill job for the defined window, bounded by partition and with a concurrency limit so daily runs keep their slots. Prefer writing to a table-format branch or staging table and publishing after validation.
   Overwrite exactly the partitions the job recomputes; a wider overwrite filter deletes data the job did not rebuild.
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
- Rollback mechanism (restore the recorded snapshot id / revert partitions / rerun last-known-good). Restoring a snapshot also discards any other writes committed after it; pause other writers first:
- Verification after rollback:

## Communication

- Internal channel:
- Stakeholder update cadence:
- Customer-facing update needed: yes/no

## Post-Incident Follow-Up

- Root cause summary:
- Preventive actions (tests, monitors, contracts, process):
- Runbook updates required:

Never auto-apply a destructive backfill without an approval step; automated summaries of validation results need human review.
