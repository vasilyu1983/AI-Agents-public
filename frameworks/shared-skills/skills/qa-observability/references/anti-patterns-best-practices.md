# Anti-Patterns & Best Practices

Common observability mistakes and how to avoid them, based on production experience from thousands of teams.

## Contents

- Critical Anti-Patterns to Avoid
- Best Practices Summary
- Decision Matrix: When to Use What
- ROI Validation

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
- 90% of logs are noise, 10% are signal
- Expensive log storage costs ($1000s/month for 100GB/day)
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
- 10k RPS = 864M traces/day = $10k-50k/month storage
- High write load on trace backend (Jaeger, Tempo)
- Most traces are identical (successful requests)

**Best Practice:**
```javascript
// Adaptive sampling: 100% errors, 10% success
const provider = new TracerProvider({
  sampler: new ParentBasedSampler({
    root: new TraceIdRatioBasedSampler(0.1), // 10% of root spans
  }),
});

// Or custom sampler
class AdaptiveSampler {
  shouldSample(context, traceId, spanName, spanKind, attributes, links) {
    // Always sample errors
    if (attributes['http.status_code'] >= 500) {
      return { decision: SamplingDecision.RECORD_AND_SAMPLED };
    }

    // Always sample slow requests
    if (attributes['http.duration_ms'] > 1000) {
      return { decision: SamplingDecision.RECORD_AND_SAMPLED };
    }

    // Sample 1% of normal requests
    return Math.random() < 0.01
      ? { decision: SamplingDecision.RECORD_AND_SAMPLED }
      : { decision: SamplingDecision.NOT_RECORD };
  }
}
```

**Sampling Strategy by Traffic Volume:**

| RPS | Recommended Sampling | Traces/Day | Est. Cost/Month |
|-----|---------------------|------------|-----------------|
| 100 | 100% | 8.6M | $50-100 |
| 1k | 10% | 8.6M | $50-100 |
| 10k | 1% | 8.6M | $50-100 |
| 100k | 0.1% | 8.6M | $50-100 |

**Target:** ~10M traces/day for cost-effective observability.

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

**Best Practice (SLO-Based Alerting):**
```yaml
# Alert on SLO burn rate
alerts:
  # Fast burn: 2% budget consumed in 1 hour = P0 incident
  - alert: ErrorBudgetFastBurn
    expr: |
      (1 - slo:availability:ratio_rate1h) > (14.4 * (1 - 0.999))
    labels:
      severity: critical
    annotations:
      summary: "Fast burn rate - 2% error budget consumed in 1 hour"

  # Slow burn: 5% budget consumed in 6 hours = P1 warning
  - alert: ErrorBudgetSlowBurn
    expr: |
      (1 - slo:availability:ratio_rate6h) > (2.4 * (1 - 0.999))
    labels:
      severity: warning
    annotations:
      summary: "Slow burn rate - 5% error budget consumed in 6 hours"
```

**Alerting Philosophy:**
- **Alert on user impact**, not infrastructure metrics
- **Use multi-window burn rate** (fast: 1h, slow: 6h)
- **Target 5-10 alerts/day** (not 100s)
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
SLO: 99.9% availability over 30 days
Error Budget: 43.2 minutes downtime/month

| Error Budget Remaining | Action |
|------------------------|--------|
| > 50% | Full velocity (all features, experiments, rewrites) |
| 25-50% | Cautious (critical features only, no experiments) |
| 10-25% | Feature freeze (reliability work only) |
| < 10% | Incident mode (stop all releases, rollback) |
```

**Example:**

```
Month 1:
- Shipped 10 features
- Had 2 outages (30 minutes total)
- Error budget remaining: 30% (13 minutes left)
- Action: Feature freeze, focus on reliability

Month 2:
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

### 7. No Cost Tracking (Observability Costs 20% of Infrastructure)

**Anti-Pattern:**
```
"We need observability, enable everything!"
  -> $50k/month infrastructure
  -> $10k/month observability (20% overhead)
  -> Team doesn't realize cost
```

**Why It's Bad:**
- Observability can cost 10-20% of infrastructure
- Log storage grows unbounded (1TB/day = $1000s/month)
- Trace storage grows exponentially (10M traces/day = $5k/month)

**Cost Breakdown (Typical 100 RPS Service):**

| Component | Volume | Cost/Month |
|-----------|--------|------------|
| Log storage (7-day retention) | 100GB/day | $500 |
| Metrics storage (Prometheus) | 1M series | $200 |
| Trace storage (1% sampling) | 10M traces/day | $1000 |
| APM (Datadog, New Relic) | 10 hosts | $1500 |
| **Total** | | **$3200/month** |

**Best Practice:**

```javascript
// Log sampling (only sample 10% of successful requests)
logger.info({ order_id: '123', sample_rate: 0.1 }, 'Order processed');

// Trace sampling (1% of successful requests, 100% of errors)
const provider = new TracerProvider({
  sampler: new AdaptiveSampler(), // Custom sampler
});

// Metric cardinality limits (avoid user_id in metrics)
// Bad: metrics.counter('orders', { user_id: '123' }); // 1M unique users = 1M series
// Good: metrics.counter('orders', { status: 'success' }); // 2 series (success, failure)
```

**Cost Optimization Strategies:**
1. **Log retention**: 7 days hot, 30 days cold, 90 days archive
2. **Trace sampling**: 1% for 10k RPS, 0.1% for 100k RPS
3. **Metric cardinality**: <1000 unique label combinations per metric
4. **APM**: Use open source (Jaeger, Grafana) instead of commercial ($200/month vs $1500/month)

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
- [OK] Sample traces intelligently (100% errors, 1-10% success)
- [OK] Alert on SLO burn rate, not infrastructure metrics
- [OK] Track tail latency (P99, P999), not just averages
- [OK] Use error budgets to balance velocity vs reliability
- [OK] Add context to dashboards (baselines, annotations, SLOs)
- [OK] Track observability costs, optimize aggressively
- [OK] Continuous profiling for intermittent issues

**Don'ts:**
- [FAIL] Log everything (bloats logs, high cardinality)
- [FAIL] Collect 100% of traces (expensive, unnecessary)
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

## ROI Validation

**Observability Investment vs Returns:**

```
Investment (100 RPS service):
- Tools: $3k/month (logs, metrics, traces, APM)
- Engineering: 2 engineers * $150k/year = $25k/month
- Total: ~$30k/month

Returns:
- MTTR: 2 hours -> 10 minutes (12x faster incident resolution)
- MTTD: 1 hour -> 5 minutes (12x faster detection)
- Incident cost: $10k/hour * 2 hours = $20k -> $10k/hour * 10 min = $1.7k
- Savings: $18k/incident
- If 3 incidents/month -> $54k/month savings
- ROI: $54k savings - $30k investment = $24k/month profit
```

**When NOT to Invest in Advanced Observability:**
- Early-stage startup (<10 RPS, <5 engineers)
- Prototype/MVP (focus on product-market fit first)
- Internal tools (low SLO requirements)

**When to Invest:**
- Production systems (>100 RPS, >10 engineers)
- Mission-critical services (financial, healthcare)
- High incident costs ($10k-100k/hour downtime)

---

> **Golden Rule:** Observability should cost 10-20% of infrastructure, not 50%. Optimize aggressively (sampling, retention, cardinality) while maintaining debugging capabilities.
