# SLO Design Guide

## Table of Contents

- [Choosing SLIs](#choosing-slis)
- [Defining SLOs](#defining-slos)
- [Error Budgets](#error-budgets)
- [Burn Rate Alerts](#burn-rate-alerts)
- [Canonical Multi-Window Burn-Rate Table](#canonical-multi-window-burn-rate-table)
- [Predictive (Lookahead) Burn Alerts](#predictive-lookahead-burn-alerts)
- [Multi-Window SLOs](#multi-window-slos)
- [Common SLO Pitfalls](#common-slo-pitfalls)
- [Example: E-Commerce API SLOs](#example-e-commerce-api-slos)
- [Advanced: Request-Based vs Time-Based SLOs](#advanced-request-based-vs-time-based-slos)
- [Further Reading](#further-reading)

Operational guide for defining SLIs, SLOs, and error budgets, based on Google SRE practice. The burn-rate table in this file is the canonical copy for the whole skill library; other files link here.

## Choosing SLIs

### Golden Signals (Recommended)

**1. Latency** - How long does it take to serve a request?

```promql
# Latency SLI as a ratio: share of requests served within 500ms.
# The le="0.5" bucket must exist in the histogram.
sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
/
sum(rate(http_request_duration_seconds_count[5m]))
```

A quantile compared to a threshold (`histogram_quantile(0.99, ...) > 0.5`) is useful on a dashboard, but it is not a ratio SLI: it has no good/total events, so no error budget or burn rate can be computed from it.

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

  - name: checkout-latency
    description: Share of checkouts completing within 3s
    measurement: |
      sum(rate(checkout_duration_seconds_bucket{le="3"}[30d]))
      / sum(rate(checkout_duration_seconds_count[30d]))
    target: 95%

  - name: payment-success-rate
    description: Percentage of payment attempts that succeed
    measurement: |
      sum(payment_success_total) / sum(payment_attempts_total)
    target: 99%
```

### Durability — the SLI availability does not cover

For any service that owns a datastore, **durability is a distinct SLI from availability**, and a green availability dashboard is not evidence of it. Availability is "the ability to return an expected response to the requesting client"; durability "indicates the successful persistence of a write operation to storage so that it can be retrieved at another time" (Campbell & Majors, *Database Reliability Engineering*, 2017, p. 16). A system can be fully available — accepting writes, returning 200s, meeting its latency target — while silently losing data: replication lagging past the failover point, an unfenced write path, a queue acknowledging before the write commits.

Express it as a bounded loss window rather than a percentage. The source's own form: *in the event of a system failure, no more than the past two seconds of data can be lost.* That maps directly onto an RPO and is falsifiable, which "99.99% durable" is not.

Evidencing it requires different instrumentation than an uptime probe, because uptime cannot observe loss:

- **Backup success as a signal, restore verification as the proof.** A backup job exiting zero says a file was written, not that it contains recoverable data. The SLI should be driven by periodic restores into a scratch environment with a row-count or checksum assertion — an unverified backup is an untested claim.
- **Measure the actual loss window, not the configured one.** Replication lag, unacknowledged-write depth, and time since last verified restore are the observable quantities. Alert on them the way you alert on burn rate.
- **Record the last successful restore verification** as a first-class metric with an age. A durability SLI whose freshest evidence is months old has already failed.

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
    allowed_failed_requests: 0.1%
    burn_rate_alerts:
      - threshold: 14.4x # 1h AND 5m; 2% budget in 1 hour -> page
      - threshold: 6x # 6h AND 30m; 5% budget in 6 hours -> page
      - threshold: 1x # 3d AND 6h; 10% budget in 3 days -> ticket
```

---

## Error Budgets

### What is an Error Budget?

**Error budget = Allowed failure rate over SLO window**

```
Request SLO: 99.9% of eligible requests succeed over 30 days
Allowed failed requests: 0.1% of eligible requests
Separate time-based SLO: 99.9% of measured time is available over 30 days
Allowed downtime for that time-based SLO: 0.1% of 30 days = 43.2 minutes
```

### Error Budget Calculation

The following example uses a complete-window time-based availability SLI. For request-based SLIs, multiply the allowed failure fraction by the eligible request count; minutes cannot be inferred from the request ratio ([SRE SLI definitions](https://sre.google/workbook/implementing-slos/)).

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

Time to exhaustion = SLO window / burn rate. For a 30-day window: 14.4x empties the budget in 50h, 6x in 5 days, 1x in 30 days.

---

## Canonical Multi-Window Burn-Rate Table

Source: Google SRE Workbook, ch.5 "Alerting on SLOs", Table 5-8 (https://sre.google/workbook/alerting-on-slos/). Values assume a 30-day SLO window. **This is the single canonical copy.** Other files in this library link here instead of repeating the table.

| Severity | Burn rate | Long window | Short window | Budget consumed | Action |
|---|---|---|---|---|---|
| Fast | 14.4× | 1h | 5m | 2% | page |
| Medium | 6× | 6h | 30m | 5% | page |
| Slow | 1× | 3d | 6h | 10% | ticket |

How to apply it:

- **Alert when both windows exceed the same burn rate.** The long window proves the burn is significant. The short window (1/12 of the long one) proves it is still happening, so the alert resets soon after the fix. Do not pair different burn rates (for example `1h > 14.4 AND 6h > 6`); the slower window then delays the page by hours.
- **Threshold = burn rate × (1 − SLO).** For 99.9%: error ratios of 0.0144, 0.006 and 0.001.
- **Budget consumed = burn rate × long window / SLO window**, e.g. 14.4 × 1h / 720h = 2%.
- **Other tiers are extensions, not Workbook content.** Some teams add a 1d/2h tier at 3× (10% of budget in 1 day). If you add one, label it local policy.
- **Low-traffic services:** at a few requests per hour, one failure can exceed 14.4×. The Workbook's options (ch.5, "Low-Traffic Services and Error Budget Alerting"): generate artificial traffic, combine small services for monitoring, change the product so one failure matters less, or lower the SLO / lengthen the window. A `sum(rate(requests[1h])) > <minimum>` guard suppresses those alerts rather than measuring the service.

Working PromQL with a passing `promtool` unit test: [`assets/monitoring/slo/prometheus-alert-rules.yaml`](../assets/monitoring/slo/prometheus-alert-rules.yaml). Aggregate with `sum by (service)` on both sides of every ratio; see [alerting-strategies.md](alerting-strategies.md#prometheus-implementation) for why. For many services, generate the rules (Sloth, Pyrra, OpenSLO specs) rather than writing them by hand.

---

## Predictive (Lookahead) Burn Alerts

A **second family** of burn alerting, alongside the fixed-threshold multi-window table above. The multi-window table answers "how fast are we burning right now, over these fixed windows?". Predictive alerts answer a different question: **"if current conditions hold, when does the budget hit zero — and is that soon enough to page someone?"** Both are legitimate; they are not substitutes for one another.

Source: Charity Majors, Liz Fong-Jones, George Miranda, *Observability Engineering* (Early Release ch. 12; final ed. ch. 13).

Scope note from the source: these preemptive calculations "work best to prevent violations for SLOs with targets up to 99.95%". Above 99.95% they work less preventatively but can still report on and warn about degradation — there simply is not enough tolerable downtime left to act inside.

### Prerequisite: frame time as a sliding window

Fixed calendar windows (1st to the 30th) fail for burn forecasting, and the reason is mechanical rather than philosophical:

> The correct first choice to make when calculating burn trajectories is to frame time as a sliding window, rather than a static fixed window. Otherwise, there isn't enough data after a window reset to make meaningful decisions.

A fixed window resets to full budget instantly, so for the first stretch of every new period the forecast has nearly no history to extrapolate from. A sliding window (any trailing 30-day period) burns and restores a little at each interval, which also matches customer memory better — a refund for an outage on the 31st does not make a customer tolerant of another outage on the 2nd. See [Multi-Window SLOs](#multi-window-slos) below, which already recommends rolling windows for the same underlying reason.

### Why a non-zero budget threshold is not enough

The simplest alert above zero is a fixed remaining-budget threshold — page when remaining error budget dips below, say, 30%. The source's verdict:

> A challenge with this model is that it effectively just moves the goalpost by setting a different empty threshold. This type of "early warning" system can be somewhat effective, but it is crude.

In practice the team treats the threshold crossing as if the whole budget were spent, sits in a feature freeze waiting for the budget to climb back above an arbitrary line, and forfeits delivery time it did not need to forfeit. The threshold buys headroom by giving up the thing the budget existed to permit.

### The lookahead window and the baseline window

A predictive burn alert needs two windows:

- **Lookahead window** — how far into the future the forecast extends.
- **Baseline (lookback) window** — how much recent data feeds the prediction.

The lookahead window is chosen by urgency, not by convention. A regression putting a 99.9% target on track for 99.88% a month from now is not an emergency and can wait for the next business day. A failure rate on track to reach 98% within one hour should page — left uncorrected it "could hemorrhage your error budget for the entire month, quarter, or year within a matter of hours." Set the lookahead to the horizon at which the answer changes your response, and route severity accordingly.

The baseline window is then constrained by the lookahead. **The sizing rule, verbatim:**

> In practice, we've found that a given baseline window can linearly predict forward by a factor of four at most without needing to add compensation for seasonality (e.g. peak/off-peak hours of day, weekday vs weekend, or end/beginning of month).

So one hour of observed performance, extrapolated four times over, gives an accurate-enough prediction of whether the budget empties in four hours. The general form: **baseline should be about the same order of magnitude as the lookahead, and no smaller than lookahead ÷ 4.**

Both directions of violating this rule are hazardous:

- **Baseline too short for the lookahead** — using the past thirty minutes to extrapolate the next few days "runs the risk of becoming flappy". Short windows carry minute-scale cyclical noise (an un-jittered cron job, a batch tick) that smooths out over a day but dominates a small sample. Forecast far enough from it and the alert oscillates on noise.
- **Baseline too long for the lookahead** — waiting for a full day of history before predicting the next several minutes is impractical: "Your error budget for the entire year could be blown by the time you make a prediction."

Beyond the 4× factor you are no longer doing linear extrapolation honestly; you need explicit seasonality compensation for time-of-day, weekday/weekend, and month-boundary effects.

### Short-term vs context-aware calculation

Two ways to compute the trajectory, differing in what history they consider:

| | **Short-term (ahistorical)** | **Context-aware** |
| --- | --- | --- |
| Input | Baseline data from the most recent period only | Total successful and failed events for the SLO's **entire trailing window** |
| Assumption | Extrapolates as if there had been no errors prior to the baseline window | Current remaining budget is part of the calculation |
| Cost | Cheaper | "Computationally more expensive than short-term burn alerts" |
| Behaviour | Same urgency regardless of budget already spent | Same degradation can be more urgent when little budget remains |

The choice hinges on two factors. The first is the **cost/sensitivity tradeoff** above. The second is a **philosophical stance**: should the amount of budget remaining influence how responsive you are to degradation? If a significant error with 10% of budget left should be treated as more urgent than the same error with 90% left, choose context-aware and pay the compute. If degradation severity should be judged on its own terms, short-term is sufficient and cheaper.

### Worked example (the book's)

Reproduced from the source, and labelled as its example rather than a general recommendation:

- SLO target: **99% of units succeed** over a moving 30-day window.
- Typical month: **43,800 units** (the book's figure: 525,600 minutes per year / 12, at one unit per minute; a 30-day window would be 43,200).
- Budget: only 1% may fail → **438 units** may fail per month.
- Past 24 hours: **1,440 units observed, 50 failed**.
- Past 6 hours: **360 units observed, 5 failed**.

A very simple short-term burn alert reasons from the most recent baseline: 5 units burned in the past 6 hours implies roughly 20 in the next 24, against a 438-unit budget — not alarming on its own. Note that the 24-hour figure (50 failures) tells a materially different story than the 6-hour figure (5 failures) extrapolated, which is exactly why the baseline window choice is a design decision and not a default. "Units" here is deliberately data-type-agnostic: the source uses it for the granular building block of the calculation, either a time-series datapoint marked good/bad or an individual event corresponding to a user transaction, at one datapoint per minute in these examples.

### Choosing between the two families

- Keep the **fixed-threshold multi-window burn-rate alerts** above as the paging backbone. They are cheap, well-understood, and their false-positive behaviour is well documented.
- Add **predictive alerts** when you need lead time to act rather than notification that burn is already fast — particularly for targets at or below 99.95%, where there is enough tolerable downtime for early warning to be actionable.
- Do not run both at the same severity on the same SLO. Two families paging for the same condition is the alert-fatigue failure mode described in [alerting-strategies.md](alerting-strategies.md).

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

PromQL has no calendar-month range selector, and `[30d]` is not a month. `@ start()` pins evaluation to the start of the *query range*, not of the month, and it must follow a selector: `sum(...) @ start()` is a parse error ("@ modifier must be preceded by an instant vector selector or range vector selector or a subquery", promtool 3.9.0).

Practical options:

- **Dashboard:** set the time picker to "This month so far" and run an instant query with Grafana's `$__range`:
  `sum(increase(http_requests_total{status!~"5.."}[$__range])) / sum(increase(http_requests_total[$__range]))`
- **Report job:** at month end, run an instant query whose range equals that month's length, with `@` on the selector: `sum(increase(http_requests_total{status!~"5.."}[31d] @ <month_end_unix_ts>))`.
- **SLO tooling** (Sloth, Pyrra, or a vendor SLO product) if you need calendar budgets routinely.

**Pros:**
- Aligns with SLA reporting
- Clean slate each month

**Cons:**
- Incident late in month has limited impact
- Encourages gaming (incident early in month is "better")

### Recommendation

Use **rolling windows** for SLOs, **calendar windows** for SLA reporting.

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

  - name: order-api-latency
    objective: 99% of order API requests complete in <= 500ms over 30 days
    sli:
      # Ratio SLI: requests under the threshold / all requests
      measurement: |
        sum(rate(http_request_duration_seconds_bucket{service="order-api",le="0.5"}[30d]))
        /
        sum(rate(http_request_duration_seconds_count{service="order-api"}[30d]))
    target: 0.99
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

Apply the [canonical table](#canonical-multi-window-burn-rate-table) to each SLO. For the 99.9% availability SLO, the fast tier fires when the error ratio exceeds 1.44% over both 1h and 5m; the medium tier when it exceeds 0.6% over both 6h and 30m.

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
- [SRE Workbook - Chapter 5: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
