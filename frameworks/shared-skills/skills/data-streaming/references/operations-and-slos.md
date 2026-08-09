# Streaming Operations And SLOs

Use this reference when the user asks how to run streaming pipelines safely in production.

## Minimum SLO Set

Define at least:

- End-to-end freshness or latency target
- Consumer lag tolerance
- Produce and consume error budget
- Recovery-time target for broker, connector, and processor incidents
- Replay or backfill completion target for critical pipelines

## Minimum Dashboard Set

Track:

- Produce throughput and error rate
- Consumer lag by topic, group, and partition
- Broker or service health
- Checkpoint duration and failure count
- Savepoint success rate for planned Flink changes
- Connector task failures and restart churn
- Retention pressure, storage growth, and under-replicated partitions

## Incident Patterns

### Growing Consumer Lag

Check:

- Traffic spike vs consumer regression
- Partition imbalance
- Downstream sink throttling
- Rebalance churn
- Poison messages or deserialization failures

### Checkpoint Or Savepoint Failures

Check:

- State size growth
- Externalized checkpoint configuration
- Sink backpressure
- Object storage or metadata-store instability

### CDC Drift

Check:

- Source privileges and connector health
- WAL/binlog retention
- Schema changes not reflected downstream
- Delete handling regressions

## Consumer Commit And Failure Routing

- Never commit message offsets (or acknowledge messages) after a processing failure. Committing in `finally` regardless of outcome defeats manual commit mode and causes acknowledged message loss. With manual commit (`enable.auto.commit=false`), commit the source offset only after one durable outcome: successful processing, durable publish to a retry topic, or durable publish to a DLQ topic.
- Classify exceptions into retryable and non-retryable before entering the retry loop, not inside it. Non-retryable exceptions (validation, schema mismatch, deterministic business rejection, poison messages) must be routed to dead-letter or terminal failure handling immediately — never fed into the generic retry loop.
- Treat cancellation as control flow, not failure handling. `OperationCanceledException` from host shutdown must exit the processing loop cleanly — never route to retry/DLQ, never commit the message offset, and never log as a processing failure.
- Isolate failure-routing failures to the narrowest scope possible. If publishing to a retry or DLQ topic fails, pause or park only the affected partition — do not silently kill the entire consumer task or leave a dead background task behind. A retry/DLQ publish failure should produce visible host-level faulting (metrics, health degradation) so operators can detect it.

## Operational Rules

- Rehearse replay and restore before the first real incident
- Version topic contracts and processing jobs deliberately
- Prefer reversible rollout paths for processor upgrades
- Do not expand retention or partition count blindly; tie it to replay and cost requirements
- Record which changes require savepoints, dual-run periods, or consumer restarts

## Deployment Guidance

For processing jobs:

- Use progressive rollout where supported
- Keep rollback artifacts and savepoints accessible
- Validate sink idempotency before resuming after failure

For brokers or managed services:

- Verify service-specific quotas and scaling behavior from official docs
- Capture hard limits and operational caveats in the recommendation, not just the happy path
