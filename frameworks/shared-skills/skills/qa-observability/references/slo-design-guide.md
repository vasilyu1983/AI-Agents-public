# SLO Design Guide

Operational guide for defining Service Level Objectives (SLOs), Service Level Indicators (SLIs), and error budgets. Based on Google SRE practices.

## Contents

- SLI/SLO/SLA Hierarchy
- Choosing SLIs
- Defining SLOs
- Error Budgets
- Burn Rate Alerts
- Multi-Window SLOs
- SLO Dashboard Template
- Common SLO Pitfalls
- SLO Implementation Checklist
- Example: E-Commerce API SLOs
- Advanced: Request-Based vs Time-Based SLOs
- Further Reading

## SLI/SLO/SLA Hierarchy

```
SLA (Service Level Agreement)
  - Business contract with customers
  - SLO (Service Level Objective)
    - Internal reliability target
    - SLI (Service Level Indicator)
      - Actual measurement
```

**Example:**
- **SLA**: 99.9% uptime or customer gets refund
- **SLO**: 99.95% uptime (buffer above SLA)
- **SLI**: Actual uptime measured (e.g., 99.97% last month)

---

## Choosing SLIs

### Golden Signals (Recommended)

**1. Latency** - How long does it take to serve a request?

```promql
# P99 latency
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)
```

**2. Availability** - What percentage of requests succeed?

```promql
# Success rate
sum(rate(http_requests_total{status!~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

**3. Error Rate** - What percentage of requests fail?

```promql
# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

**4. Throughput** - How many requests per second?

```promql
# Requests per second
sum(rate(http_requests_total[5m]))
```

### User Journey SLIs

**Use when:** Focusing on end-user experience

**Example: E-commerce checkout**

```yaml
slis:
  - name: checkout-completion-rate
    description: Percentage of checkout attempts that complete successfully
    measurement: |
      sum(checkout_completed_total) / sum(checkout_started_total)
    target: 95%

  - name: checkout-latency-p95
    description: 95th percentile checkout completion time
    measurement: |
      histogram_quantile(0.95, checkout_duration_seconds_bucket)
    target: 3s

  - name: payment-success-rate
    description: Percentage of payment attempts that succeed
    measurement: |
      sum(payment_success_total) / sum(payment_attempts_total)
    target: 99%
```

---

## Defining SLOs

### SLO Template

```yaml
slo:
  name: api-availability
  objective: Ensure API is available for 99.9% of requests over 30 days
  sli:
    type: availability
    measurement: |
      sum(rate(http_requests_total{status!~"5.."}[30d]))
      /
      sum(rate(http_requests_total[30d]))
  target: 0.999 # 99.9%
  window: 30d
  error_budget:
    allowed_downtime: 43.2 minutes per 30 days
    burn_rate_alerts:
      - threshold: 14.4x # 2% budget in 1 hour
        severity: critical
      - threshold: 6x # 5% budget in 6 hours
        severity: warning
```

### SLO Targets by Service Type

| Service Type | Availability SLO | Latency SLO (P99) |
|--------------|------------------|-------------------|
| User-facing API | 99.9% (3 nines) | 500ms |
| Internal API | 99.5% | 1s |
| Batch processing | 99% | N/A |
| Async jobs | 95% | N/A |
| Critical payment | 99.99% (4 nines) | 200ms |

---

## Error Budgets

### What is an Error Budget?

**Error budget = Allowed failure rate over SLO window**

```
SLO: 99.9% availability over 30 days
Allowed failure: 0.1% of requests
Allowed downtime: 0.1% of 30 days = 43.2 minutes/month
```

### Error Budget Calculation

```python
def calculate_error_budget(target_slo, actual_sli, window_days):
    """
    Calculate remaining error budget.

    Args:
        target_slo: Target SLO (e.g., 0.999 for 99.9%)
        actual_sli: Actual SLI (e.g., 0.9995 for 99.95%)
        window_days: SLO window in days (e.g., 30)

    Returns:
        remaining_budget_percent: Percentage of error budget remaining
        remaining_minutes: Minutes of downtime remaining
    """
    allowed_error_rate = 1 - target_slo
    actual_error_rate = 1 - actual_sli

    error_budget_consumed = actual_error_rate / allowed_error_rate
    remaining_budget_percent = (1 - error_budget_consumed) * 100

    total_minutes = window_days * 24 * 60
    allowed_downtime_minutes = total_minutes * allowed_error_rate
    actual_downtime_minutes = total_minutes * actual_error_rate
    remaining_minutes = allowed_downtime_minutes - actual_downtime_minutes

    return remaining_budget_percent, remaining_minutes

# Example
remaining_percent, remaining_minutes = calculate_error_budget(
    target_slo=0.999,      # 99.9%
    actual_sli=0.9995,     # 99.95% (better than target)
    window_days=30
)

print(f"Error budget remaining: {remaining_percent:.1f}%")
print(f"Downtime remaining: {remaining_minutes:.1f} minutes")
# Output:
# Error budget remaining: 50.0%
# Downtime remaining: 21.6 minutes
```

### Error Budget Policy

**Use error budgets to balance velocity and reliability:**

| Error Budget Remaining | Action |
|------------------------|--------|
| **>50%** | [OK] Full velocity: ship all features, run experiments |
| **25-50%** | [WARNING] Cautious: critical features only, reduce risk |
| **10-25%** | [BLOCK] Feature freeze: reliability work only |
| **<10%** | [RED] Incident mode: stop all releases, fix reliability |

**Example policy:**

```yaml
error_budget_policy:
  - threshold: 50%
    action: full_velocity
    description: Ship all features, run experiments, normal deployment cadence

  - threshold: 25%
    action: reduced_velocity
    description: |
      - Critical features only
      - Increase test coverage
      - Review upcoming changes for risk
      - Defer non-critical experiments

  - threshold: 10%
    action: feature_freeze
    description: |
      - Stop all feature releases
      - Focus on reliability improvements
      - Root cause analysis of recent incidents
      - Increase monitoring and alerting

  - threshold: 0%
    action: incident_mode
    description: |
      - Emergency incident response
      - Stop all releases (except fixes)
      - War room until budget recovered
      - Postmortem required
```

---

## Burn Rate Alerts

### What is Burn Rate?

**Burn rate = How fast you're consuming error budget**

```
1x burn rate = Consuming budget at normal rate (will hit 0% at end of window)
2x burn rate = Consuming budget 2x faster (will hit 0% in half the time)
14x burn rate = Consuming budget 14x faster (critical)
```

### Recommended Burn Rate Alerts

Based on Google SRE Workbook:

```yaml
burn_rate_alerts:
  # Fast burn (short window, high burn rate)
  - name: critical-burn-1h
    severity: critical
    window: 1h
    burn_rate: 14.4x
    budget_consumed: 2%
    description: |
      Consuming 2% of 30-day error budget in 1 hour.
      At this rate, will exhaust budget in 50 hours.

  - name: critical-burn-6h
    severity: critical
    window: 6h
    burn_rate: 6x
    budget_consumed: 5%
    description: |
      Consuming 5% of 30-day error budget in 6 hours.
      At this rate, will exhaust budget in 5 days.

  # Slow burn (longer window, lower burn rate)
  - name: warning-burn-1d
    severity: warning
    window: 1d
    burn_rate: 3x
    budget_consumed: 10%
    description: |
      Consuming 10% of 30-day error budget in 1 day.
      At this rate, will exhaust budget in 10 days.

  - name: warning-burn-3d
    severity: warning
    window: 3d
    burn_rate: 1x
    budget_consumed: 10%
    description: |
      Consuming 10% of 30-day error budget in 3 days.
      At this rate, will exhaust budget in 30 days.
```

### Prometheus Alert Rules

```yaml
# prometheus-alerts.yaml
groups:
  - name: slo-burn-rate
    rules:
      # Fast burn (1 hour window)
      - alert: ErrorBudgetBurnRateCritical1h
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[1h]))
              /
              sum(rate(http_requests_total[1h]))
            )
          ) > (14.4 * (1 - 0.999))
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical error budget burn rate (1h window)"
          description: "Consuming 2% of 30-day error budget in 1 hour"

      # Slow burn (6 hour window)
      - alert: ErrorBudgetBurnRateWarning6h
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{status!~"5.."}[6h]))
              /
              sum(rate(http_requests_total[6h]))
            )
          ) > (6 * (1 - 0.999))
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Warning error budget burn rate (6h window)"
          description: "Consuming 5% of 30-day error budget in 6 hours"
```

---

## Multi-Window SLOs

### Rolling Window (Recommended)

**Use when:** Continuous evaluation of SLO

```promql
# Availability SLI over rolling 30 days
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
```

**Pros:**
- Always up-to-date
- No artificial reset at month boundary

**Cons:**
- Past incidents affect SLO for 30 days

### Calendar Window

**Use when:** SLO resets monthly (for SLA reporting)

```promql
# Availability SLI for current calendar month
sum(increase(http_requests_total{status!~"5.."}[30d])) @ start()
/
sum(increase(http_requests_total[30d])) @ start()
```

**Pros:**
- Aligns with SLA reporting
- Clean slate each month

**Cons:**
- Incident late in month has limited impact
- Encourages gaming (incident early in month is "better")

### Recommendation

Use **rolling windows** for SLOs, **calendar windows** for SLA reporting.

---

## SLO Dashboard Template

### Grafana Dashboard Structure

**1. Current SLI Status**
```
+-------------------------------------+
| Availability SLI (30d)              |
| ####################.... 99.95%     |
| Target: 99.9% ([OK] 0.05% above)    |
+-------------------------------------+
```

**2. Error Budget Remaining**
```
+-------------------------------------+
| Error Budget Remaining              |
| ####################..... 50%       |
| 21.6 minutes of downtime remaining  |
+-------------------------------------+
```

**3. Error Budget Burn Rate**
```
+-------------------------------------+
| Burn Rate (1h window)               |
| #### 2x (Normal)                    |
| Alert threshold: 14.4x              |
+-------------------------------------+
```

**4. SLI History (30 days)**
```
Graph: SLI over time
- Green line: Target (99.9%)
- Blue line: Actual SLI
- Red shading: Below target
```

---

## Common SLO Pitfalls

### BAD: Pitfall 1: Too Many SLOs

**Problem:**
- Tracking 50 different SLOs
- Alert fatigue
- Unclear priorities

**Solution:**
- Start with 3-5 critical SLOs per service
- Focus on user-facing impact
- Consolidate related SLOs

### BAD: Pitfall 2: SLO Too Strict

**Problem:**
- 99.99% availability target
- Error budget exhausted quickly
- Constant feature freezes

**Solution:**
- Start with achievable targets (99% or 99.5%)
- Tighten over time as reliability improves
- Consider business impact of downtime

### BAD: Pitfall 3: SLO Not User-Centric

**Problem:**
- Measuring server uptime, not user experience
- Internal metrics (database CPU)
- No correlation with user impact

**Solution:**
- Measure request success rate, not server uptime
- Focus on user-facing APIs
- Include latency (users care about speed)

### BAD: Pitfall 4: No Error Budget Policy

**Problem:**
- Error budget reaches 0%
- Teams keep shipping features
- Reliability degrades further

**Solution:**
- Document error budget policy
- Enforce feature freeze at thresholds
- Make policy visible to all teams

---

## SLO Implementation Checklist

### 1. Define SLIs

- [ ] Identify 3-5 critical user journeys
- [ ] Choose appropriate metrics (availability, latency, error rate)
- [ ] Define measurement queries (PromQL, SQL)
- [ ] Validate data availability (historical data exists)

### 2. Set SLO Targets

- [ ] Analyze historical performance (baseline)
- [ ] Account for seasonality (holiday traffic)
- [ ] Set achievable targets (start conservative)
- [ ] Document rationale for targets
- [ ] Get stakeholder buy-in

### 3. Calculate Error Budgets

- [ ] Define SLO window (30 days recommended)
- [ ] Calculate allowed downtime
- [ ] Set burn rate thresholds
- [ ] Document error budget policy

### 4. Configure Alerting

- [ ] Implement burn rate alerts (fast and slow)
- [ ] Set up on-call rotation
- [ ] Document alert response procedures
- [ ] Test alerts with historical data

### 5. Create Dashboards

- [ ] Build SLO dashboard (Grafana)
- [ ] Display current SLI status
- [ ] Show error budget remaining
- [ ] Graph SLI history
- [ ] Make dashboard visible to all engineers

### 6. Review Regularly

- [ ] Weekly SLO review meeting
- [ ] Monthly error budget postmortem
- [ ] Quarterly SLO target review
- [ ] Annual SLO strategy update

---

## Example: E-Commerce API SLOs

### Service: Order API

```yaml
slos:
  - name: order-api-availability
    objective: 99.9% of order API requests succeed over 30 days
    sli:
      measurement: |
        sum(rate(http_requests_total{service="order-api",status!~"5.."}[30d]))
        /
        sum(rate(http_requests_total{service="order-api"}[30d]))
    target: 0.999
    window: 30d
    error_budget:
      allowed_requests_failed: 0.1%
      allowed_downtime: 43.2 minutes per 30 days

  - name: order-api-latency-p99
    objective: 99% of order API requests complete in < 500ms over 30 days
    sli:
      measurement: |
        histogram_quantile(0.99,
          rate(http_request_duration_seconds_bucket{service="order-api"}[30d])
        )
    target: 0.5 # 500ms
    window: 30d

  - name: checkout-success-rate
    objective: 95% of checkout flows complete successfully over 7 days
    sli:
      measurement: |
        sum(rate(checkout_completed_total[7d]))
        /
        sum(rate(checkout_started_total[7d]))
    target: 0.95
    window: 7d
    error_budget:
      allowed_failures: 5%
```

### Burn Rate Alerts

```yaml
burn_rate_alerts:
  - name: order-api-critical-burn-1h
    severity: critical
    condition: Availability SLI < 98.56% over 1 hour (14.4x burn rate)
    action: Page on-call immediately

  - name: order-api-warning-burn-6h
    severity: warning
    condition: Availability SLI < 99.4% over 6 hours (6x burn rate)
    action: Create incident, notify team
```

---

## Advanced: Request-Based vs Time-Based SLOs

### Request-Based SLO (Recommended for APIs)

**Measurement:**
```promql
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
```

**Pros:**
- Fair to users (weights by actual usage)
- High traffic periods have more weight

**Cons:**
- Can't measure if service is completely down (no requests)

### Time-Based SLO (Recommended for batch jobs)

**Measurement:**
```promql
avg_over_time(up{service="batch-processor"}[30d])
```

**Pros:**
- Measures uptime regardless of usage
- Simple to understand

**Cons:**
- Doesn't weight by user impact
- 1am downtime = 1pm downtime (equal weight)

---

## Further Reading

- [Google SRE Book - Chapter 4: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [SRE Workbook - Chapter 2: Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [The Art of SLOs](https://landing.google.com/sre/references/practicesandprocesses/art-of-slos/)
- [Atlassian: SLA vs SLO vs SLI](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
