# CDC Rollout Checklist

Use this checklist before launching or migrating a CDC pipeline.

## Source Readiness

- [ ] WAL or binlog retention is sufficient for expected lag and recovery
- [ ] Source privileges are documented and tested
- [ ] Primary key or sink dedupe key exists
- [ ] Snapshot mode is chosen intentionally

## Pipeline Readiness

- [ ] Topic naming and retention are approved
- [ ] Schema registry and compatibility policy are configured
- [ ] Delete and tombstone behavior is documented
- [ ] Backfill and replay path is tested
- [ ] Sink upsert or delete semantics are verified

## Operations Readiness

- [ ] Lag, connector health, and sink failure alerts exist
- [ ] Failover and connector restart procedure is documented
- [ ] Dual-run or validation plan exists for cutover
- [ ] Rollback plan exists if downstream correctness fails

## Post-Launch Validation

- [ ] Row counts or reconciliation checks pass
- [ ] Delete behavior matches expectations
- [ ] Schema evolution test passes
- [ ] Incident owner is assigned for the first production window
