# Feature Freshness, Streaming & Schema Evolution

Operational patterns for managing real-time features, streaming pipelines, and schema changes in production ML systems.

---

## Overview

Modern ML systems increasingly require real-time features and streaming data pipelines. This guide covers best practices for maintaining freshness SLAs, ensuring batch-stream parity, and safely evolving schemas.

---

## 1. Freshness Contracts & SLAs

### 1.1 Defining Freshness Requirements

**Questions to answer:**
- What is the maximum acceptable lag between source update and feature availability?
- Are there different SLAs for different features?
- What happens when freshness SLA is violated?

**Common SLA tiers:**
- **Real-time**: < 1 minute lag (streaming features)
- **Near real-time**: 1-15 minutes lag (micro-batch)
- **Hourly**: < 1 hour lag (batch with frequent updates)
- **Daily**: < 24 hours lag (overnight batch jobs)

### 1.2 Freshness Monitoring

**Metrics to track:**
- **Lag**: `current_time - source_timestamp`
- **Staleness**: Time since last successful update
- **Update frequency**: Updates per hour/day

**Alerting thresholds:**
- **Critical**: Lag > 2x SLA threshold
- **Warning**: Lag > 1.5x SLA threshold
- **Info**: Lag approaching SLA threshold

**Checklist: Freshness Monitoring**

- [ ] Freshness SLAs defined per feature or feature group
- [ ] Lag metrics collected and dashboarded
- [ ] Alerts configured with appropriate thresholds
- [ ] Fallback strategy documented for stale data
- [ ] Historical lag trends analyzed (p50, p95, p99)

---

## 2. Batch + Stream Parity

### 2.1 The Parity Challenge

**Problem:**
- Batch pipelines use different code/frameworks than streaming
- Results can diverge due to:
  - Rounding differences
  - Aggregation window boundaries
  - Late-arriving data handling
  - Order-dependent operations

**Solution:**
- Use **shared feature transformation logic**
- Implement **idempotent upserts**
- Handle **late-arriving data** consistently
- Test parity with **synthetic replay**

### 2.2 Shared Feature Logic Patterns

**Option 1: Feature store abstraction**
```python
# Same code for batch and stream
@feature_definition
def user_7day_spend(events):
    return events.filter(
        lambda e: e.timestamp > now() - timedelta(days=7)
    ).sum("amount")
```

**Option 2: Shared libraries**
```python
# features/user_metrics.py (shared by Spark batch + Flink stream)
def compute_rolling_spend(events_df, window_days=7):
    # Deterministic logic works in both contexts
    return events_df.groupBy("user_id").agg(...)
```

**Checklist: Batch-Stream Parity**

- [ ] Feature logic shared between batch and streaming pipelines
- [ ] Idempotent upserts implemented (duplicate events handled)
- [ ] Late-arriving data strategy defined and consistent
- [ ] Parity tests: batch vs stream results match within tolerance
- [ ] Differences documented (if unavoidable due to windowing)

---

## 3. Schema Evolution Strategies

### 3.1 Compatible Changes

**Backward compatible (safe):**
- Adding new optional fields
- Widening numeric types (int32 -> int64)
- Relaxing constraints (nullable = true)

**Forward compatible (safe):**
- Removing optional fields (old code ignores)
- Adding default values for new fields

**Incompatible (breaking):**
- Renaming fields
- Changing types (string -> int)
- Removing required fields
- Changing semantics

### 3.2 Migration Process

**Step 1: Version schemas**
```json
{
  "schema_version": "v2.1",
  "fields": [...],
  "compatible_with": ["v2.0"]
}
```

**Step 2: Dual write/read**
- Write to both old and new schema
- Read from new schema with fallback to old
- Validate consistency

**Step 3: Backfill**
- Run backfill jobs to populate new schema
- Use idempotent writes
- Validate against original data

**Step 4: Cutover**
- Monitor error rates
- Gradual rollout (1% -> 10% -> 50% -> 100%)
- Keep rollback artifacts

**Checklist: Schema Evolution**

- [ ] Schema versioned with compatibility metadata
- [ ] Dual-write phase completed successfully
- [ ] Backfill job run and validated
- [ ] Rollback plan documented and tested
- [ ] Deprecated schemas marked with sunset date

---

## 4. Data Quality Gates

### 4.1 Quality Checks

**PII/Format checks:**
- Regex validation (email, phone, SSN patterns)
- PII detection and redaction
- Encoding validation (UTF-8)

**Range checks:**
- Min/max bounds per feature
- Enum membership checks
- Cross-field constraints (end_date > start_date)

**Distribution checks:**
- KL divergence vs training distribution
- Kolmogorov-Smirnov test
- Population Stability Index (PSI)

### 4.2 Gate Enforcement

**At ingestion:**
- Block writes on critical violations
- Log warnings on minor violations
- Quarantine invalid records

**At training:**
- Fail pipeline on distribution drift > threshold
- Require manual approval for major changes

**At serving:**
- Reject invalid requests
- Apply fallback values
- Log and alert

**Checklist: Quality Gates Active**

- [ ] PII detection rules configured
- [ ] Range checks defined per feature
- [ ] Distribution drift thresholds set
- [ ] Gates active in CI/CD pipeline
- [ ] Gates active in production serving
- [ ] Quarantine process for invalid data

---

## 5. Late-Arriving Data Handling

### 5.1 Patterns

**Pattern 1: Allowed lateness window**
- Accept events up to N hours late
- Drop events beyond window
- Trade-off: completeness vs complexity

**Pattern 2: Watermarks**
- Track event time watermark
- Trigger computations when watermark advances
- Handle stragglers with side outputs

**Pattern 3: Reprocessing**
- Periodically recompute features with full data
- Upsert corrected values
- Idempotent operations required

### 5.2 Implementation

**Flink watermark example:**
```java
env.fromSource(source)
   .assignTimestampsAndWatermarks(
       WatermarkStrategy
           .<Event>forBoundedOutOfOrderness(Duration.ofMinutes(5))
           .withTimestampAssigner((event, ts) -> event.timestamp)
   )
```

**Checklist: Late Data Handling**

- [ ] Allowed lateness window defined
- [ ] Watermark strategy configured
- [ ] Reprocessing cadence determined
- [ ] Idempotency verified for reprocessing
- [ ] Metrics track late arrival rates

---

## 6. Streaming Architecture Patterns

### 6.1 Lambda Architecture

**Components:**
- **Batch layer**: Complete, accurate, slow
- **Speed layer**: Approximate, fast, handles recent data
- **Serving layer**: Merges batch + speed results

**When to use:**
- Need both accuracy (batch) and low latency (streaming)
- Can tolerate eventual consistency

### 6.2 Kappa Architecture

**Components:**
- **Single streaming pipeline** for all data
- Reprocessing = replay from log (Kafka)

**When to use:**
- Can express all logic in streaming framework
- Want to avoid maintaining two pipelines

**Checklist: Architecture Selection**

- [ ] Latency requirements documented
- [ ] Accuracy vs speed trade-offs evaluated
- [ ] Replay/reprocessing needs assessed
- [ ] Framework capabilities validated (Flink, Spark Streaming, Kafka Streams)
- [ ] Operational complexity considered

---

## 7. Testing Strategies

### 7.1 Unit Tests

**Test feature transformations:**
```python
def test_rolling_spend_deterministic():
    events = create_test_events()
    result_batch = compute_rolling_spend_batch(events)
    result_stream = compute_rolling_spend_stream(events)
    assert result_batch == result_stream
```

### 7.2 Integration Tests

**Test end-to-end pipeline:**
- Inject synthetic events
- Wait for processing
- Verify output matches expected

### 7.3 Chaos Testing

**Simulate failures:**
- Late-arriving data
- Out-of-order events
- Duplicate events
- Network partitions
- Service restarts

**Checklist: Testing Complete**

- [ ] Unit tests for feature transformations (batch-stream parity)
- [ ] Integration tests for full pipeline
- [ ] Chaos tests for failure scenarios
- [ ] Performance tests (throughput, latency)
- [ ] Regression tests for schema changes

---

## 8. Operational Runbooks

### 8.1 Common Issues

**Issue: Features are stale**
- Check: Streaming job running?
- Check: Source producing events?
- Check: Network connectivity?
- Mitigation: Restart job, trigger backfill

**Issue: Batch-stream parity violation**
- Check: Transformation code versions match?
- Check: Late-arriving data handled?
- Mitigation: Align code, replay stream

**Issue: Schema mismatch errors**
- Check: Producers using latest schema?
- Check: Consumers handle old schema?
- Mitigation: Dual-write mode, schema registry

**Checklist: Runbooks Ready**

- [ ] Incident response procedures documented
- [ ] Common failure modes catalogued
- [ ] Escalation paths defined
- [ ] Rollback procedures tested
- [ ] On-call training completed

---

## Related Resources

- [Data Contracts & Lineage](data-contracts-lineage.md) - Schema versioning and lineage tracking
- [Reproducibility Checklist](reproducibility-checklist.md) - Experiment versioning
- [Production Feedback Loops](production-feedback-loops.md) - Online learning patterns
