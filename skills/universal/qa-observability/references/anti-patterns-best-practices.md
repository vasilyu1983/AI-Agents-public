# Anti-Patterns & Best Practices

## Table of Contents

- [Contents](#contents)
- [Critical Anti-Patterns to Avoid](#critical-anti-patterns-to-avoid)
- [Best Practices Summary](#best-practices-summary)
- [Decision Matrix: When to Use What](#decision-matrix-when-to-use-what)

Common observability mistakes and how to avoid them, based on production experience from thousands of teams.

## Contents

- Critical Anti-Patterns to Avoid
- Best Practices Summary
- Decision Matrix: When to Use What

## Critical Anti-Patterns to Avoid

### 1. Logging Everything (Log Bloat)

**Anti-Pattern:**
```javascript
// Logging every function call
function processOrder(order) {
  logger.info('processOrder called', { order });
  logger.info('Validating order');
  const isValid = validateOrder(order);
  logger.info('Validation result', { isValid });
  logger.info('Saving to database');
  const saved = db.save(order);
  logger.info('Saved to database', { saved });
  logger.info('Sending email');
  sendEmail(order);
  logger.info('Email sent');
  logger.info('processOrder completed');
}
```

**Why It's Bad:**
- High-cardinality data bloats logs (every order ID, user ID)
- Most log lines are noise, and the signal is buried in them
- Storage cost scales with ingested volume (check your vendor's per-GB pricing)
- Slow log search (searching through terabytes)

**Best Practice:**
```javascript
// Log only important events and errors
function processOrder(order) {
  const span = tracer.startSpan('process-order');
  span.setAttribute('order.id', order.id);
  span.setAttribute('user.id', order.userId);

  try {
    validateOrder(order);
    db.save(order);
    sendEmail(order);

    logger.info('Order processed successfully', { order_id: order.id });
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    logger.error('Order processing failed', { order_id: order.id, error });
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw error;
  } finally {
    span.end();
  }
}
```

**Rule of Thumb:**
- **Logs**: Important business events (order created, payment failed)
- **Traces**: Execution flow and timing (function entry/exit, database calls)
- **Metrics**: Aggregated data (request count, latency percentiles)

---

### 2. No Sampling (100% Trace Collection)

**Anti-Pattern:**
```javascript
// Collecting 100% of traces in production
const provider = new TracerProvider({
  sampler: new AlwaysOnSampler(), // Samples every single trace
});
```

**Why It's Bad:**
- 10k RPS = 864M traces/day; storage cost scales with that volume
- High write load on trace backend (Jaeger, Tempo)
- Most traces are identical (successful requests)

**Best Practice:**
```javascript
// Example head sampler: keeps 10% of root traces regardless of outcome
const provider = new TracerProvider({
  sampler: new ParentBasedSampler({
    root: new TraceIdRatioBasedSampler(0.1),
  }),
});
```

Head sampling decides before the completed response status and duration are known. To retain errors or slow traces by outcome, send their spans to a tail sampler; traces dropped upstream cannot be recovered there. Monitor collector buffering and drops, and query a known error trace to verify retention ([OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/)).

**Illustrative volume arithmetic, not recommended rates:**

| RPS | Example sampling ratio | Traces/Day |
|-----|---------------------|------------|
| 100 | 100% | 8.6M |
| 1k | 10% | 8.6M |
| 10k | 1% | 8.6M |
| 100k | 0.1% | 8.6M |

**Target:** hold stored trace volume roughly constant as traffic grows; pick the level from your backend's pricing and query needs.

---

### 3. Alert Fatigue (Too Many Noisy Alerts)

**Anti-Pattern:**
```yaml
# Alerting on every metric spike
alerts:
  - alert: HighCPU
    expr: cpu_usage > 50%
    for: 1m

  - alert: HighMemory
    expr: memory_usage > 50%
    for: 1m

  - alert: HighLatency
    expr: http_latency_p99 > 100ms
    for: 1m

  - alert: AnyError
    expr: error_count > 0
    for: 1m
```

**Why It's Bad:**
- 100s of alerts/day -> engineers ignore alerts
- False positives (CPU spike during deployment)
- No context (is this actually impacting users?)

**Best Practice (SLO-Based Alerting):** page on multi-window burn rate from the [canonical table](slo-design-guide.md#canonical-multi-window-burn-rate-table) (14.4× over 1h and 5m, 6× over 6h and 30m; 1× over 3d and 6h as a ticket). Working rules with a `promtool` test: [`prometheus-alert-rules.yaml`](../assets/monitoring/slo/prometheus-alert-rules.yaml).

**Alerting Philosophy:**
- **Alert on user impact**, not infrastructure metrics
- **Pair each long window with a short window at the same burn rate**
- **Track pages per on-call shift** and treat a rising count as an alert-design defect
- **Every alert should be actionable** (runbook required)

---

### 4. Ignoring Tail Latency (Only Monitoring Averages)

**Anti-Pattern:**
```promql
# Only tracking average latency
avg(http_request_duration_seconds)
```

**Why It's Bad:**
- Average latency can be 100ms while P99 is 10s
- 1% of users experience terrible performance
- Tail latency often reveals systemic issues

**Example:**

```
100 requests:
- 99 requests: 50ms (average: 50ms)
- 1 request: 10,000ms (P99: 10,000ms)

Average latency: 149ms [OK] "Looks good"
P99 latency: 10,000ms [FAIL] "1% of users wait 10 seconds"
```

**Best Practice:**
```promql
# Track percentiles (P50, P95, P99, P999)
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))  # P50
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))  # P95
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # P99
histogram_quantile(0.999, rate(http_request_duration_seconds_bucket[5m])) # P999
```

**SLO Definition:**
```yaml
slos:
  - name: api-latency-p99
    sli: http_request_duration_p99
    target: 500ms  # 99% of requests < 500ms
    window: 30d
```

**Why P99 Matters:**
- 10k RPS -> 100 slow requests/second
- 100 slow requests/sec -> 360k unhappy users/hour
- Tail latency reveals database hotspots, cache misses, GC pauses

---

### 5. No Error Budgets (Move Too Slow or Too Fast)

**Anti-Pattern:**
```
Team A: "We can't ship this feature, it might break production"
  -> 100% reliability target, 0 features shipped

Team B: "Ship fast, break things"
  -> 95% reliability, constant outages
```

**Why It's Bad:**
- Without error budgets, teams either move too slow (fear) or too fast (chaos)
- No quantifiable trade-off between velocity and reliability
- Political debates instead of data-driven decisions

**Best Practice (Error Budget Policy):**

```markdown
Time-based SLO: available for 99.9% of measured time over 30 days
Error Budget: 43.2 minutes downtime over that 30-day window

| Error Budget Remaining | Action |
|------------------------|--------|
| > 50% | Full velocity (all features, experiments, rewrites) |
| 25-50% | Cautious (critical features only, no experiments) |
| 10-25% | Feature freeze (reliability work only) |
| < 10% | Incident mode (stop all releases, rollback) |
```

**Example:**

```
30-day window 1:
- Shipped 10 features
- Had 2 outages (30 minutes total)
- Error budget remaining: 30% (13 minutes left)
- Action: Feature freeze, focus on reliability

30-day window 2:
- Shipped 0 features (freeze mode)
- Added retries, circuit breakers, better monitoring
- Had 0 outages
- Error budget remaining: 100% (43.2 minutes available)
- Action: Resume full velocity
```

**Benefits:**
- [OK] Quantifiable reliability vs velocity trade-off
- [OK] Data-driven decisions (not political)
- [OK] Incentivizes reliability work (replenish error budget)
- [OK] Prevents over-engineering (don't target 100% uptime)

---

### 6. Metrics Without Context (Dashboard Mysteries)

**Anti-Pattern:**
```
Grafana Dashboard:
- CPU: 80% (is this normal? abnormal?)
- Latency: 200ms (is this good? bad?)
- Error Rate: 0.5% (should I be worried?)
```

**Why It's Bad:**
- No baseline (is 80% CPU normal during peak hours?)
- No annotations (was there a deployment? traffic spike?)
- No SLO context (is 0.5% error rate within budget?)

**Best Practice:**
```
Grafana Dashboard (with context):
- CPU: 80% (normal during peak hours: 70-85%)
  [Annotation: Deployment at 10:30 AM]
- Latency P99: 450ms (SLO target: <500ms, 90% of budget used)
  [Annotation: Traffic spike from marketing campaign]
- Error Rate: 0.5% (SLO target: <0.1%, OVER BUDGET [FAIL])
  [Alert: Error budget exhausted, feature freeze active]
```

**Add Context with:**
- **Baselines**: Show expected range (min/max/avg)
- **Annotations**: Mark deployments, incidents, campaigns
- **SLO indicators**: Show how close to SLO target
- **Related metrics**: Correlated graphs (latency + error rate + traffic)

---

### 7. No Cost Tracking

**Anti-Pattern:** enabling every signal at full fidelity with no owner for the bill. Cost grows with log volume, retained trace volume, and active metric series, and nobody sees it until the invoice arrives.

**Best Practice:** measure your own cost drivers per signal and per service (bytes ingested per day, spans retained per day, active series), set a budget for each, and review them like any other capacity metric. Vendor prices vary widely and change, so take figures from your own bill, not from generic tables.

**Controls that actually cap cost:**
1. **Log retention and routing**: tiered hot/cold/archive retention; drop or sample debug and success-path logs at the Collector (`filter`, `transform` processors).
2. **Trace sampling**: choose head sampling for volume control or tail sampling for outcome selection. Combining them only selects among traces that reach the tail sampler. Preserve sampling metadata, but use unsampled request metrics for SLIs; a sample-rate attribute alone cannot reconstruct missing outcomes (see [sampling-strategies.md](sampling-strategies.md)).
3. **Metric cardinality**: no unbounded IDs as labels; Prometheus `sample_limit` / `label_limit` per scrape job; OTel metric views to drop attributes.

```javascript
// Bad: 1M unique users = 1M series
metrics.counter('orders', { user_id: '123' });
// Good: bounded label values
metrics.counter('orders', { status: 'success' });
```

---

### 8. Point-in-Time Profiling (Missing Intermittent Issues)

**Anti-Pattern:**
```bash
# Manual profiling when users report slowness
node --prof app.js
# Run for 5 minutes, analyze profile
node --prof-process isolate-*.log
```

**Why It's Bad:**
- Intermittent issues only happen at 3 AM on Tuesdays
- Performance issues correlate with specific user actions
- Manual profiling misses root cause

**Best Practice (Continuous Profiling):**

```javascript
// Automatic heap snapshots every hour
const v8 = require('v8');
const fs = require('fs');

setInterval(() => {
  const filename = `heap-${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(filename);

  // Upload to S3, analyze for memory leaks
  uploadToS3(filename);
  analyzeForLeaks(filename);
}, 60 * 60 * 1000); // Every hour

// Or use continuous profiling tools
// - Pyroscope (open source)
// - Google Cloud Profiler
// - Datadog Continuous Profiler
```

**Benefits:**
- [OK] Catch intermittent issues (memory leaks, GC pauses)
- [OK] Historical profiling data (compare before/after deployment)
- [OK] Correlate performance with traffic patterns
- [OK] Proactive optimization (before users complain)

---

## Best Practices Summary

**Do's:**
- [OK] Log important business events, use traces for execution flow
- [OK] Select trace retention by evidence needs; outcome retention requires spans to reach the tail sampler
- [OK] Alert on SLO burn rate, not infrastructure metrics
- [OK] Track tail latency (P99, P999), not just averages
- [OK] Use error budgets to balance velocity vs reliability
- [OK] Add context to dashboards (baselines, annotations, SLOs)
- [OK] Track observability costs, optimize aggressively
- [OK] Continuous profiling for intermittent issues

**Don'ts:**
- [FAIL] Log everything (bloats logs, high cardinality)
- [FAIL] Collect every trace without checking volume, cost, and evidence needs
- [FAIL] Alert on every metric spike (alert fatigue)
- [FAIL] Only monitor averages (tail latency matters)
- [FAIL] Target 100% reliability (no error budget = no velocity)
- [FAIL] Dashboards without context (mysteries)
- [FAIL] Ignore observability costs (20% overhead)
- [FAIL] Point-in-time profiling (misses intermittent issues)

---

## Decision Matrix: When to Use What

| Scenario | Use This | Not This |
|----------|----------|----------|
| Track order created | Log (INFO) | Trace every step |
| Debug slow request | Distributed trace | Logs in 10 services |
| Alert on user impact | SLO burn rate | CPU >80% |
| Measure performance | P99 latency | Average latency |
| Balance velocity/reliability | Error budgets | "Move fast" or "Never break" |
| Understand dashboard spike | Annotations + SLO context | Raw metrics |
| Reduce observability costs | Sampling + retention policies | Collect everything |
| Find memory leaks | Continuous profiling | Manual profiling |

---
