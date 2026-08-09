# Queueing Theory Applied to Observability

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Cross-skill reference: applies primitives from [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md) to the observability domain.  
Primitives live in `../../foundations-queueing-theory/assets/templates/queueing-theory/`.  
Sibling applied references: [`information-theory-applied.md`](information-theory-applied.md) · [`control-theory-applied.md`](control-theory-applied.md)._

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — Saturation SLOs via Little's Law on Queue Depth](#p1--saturation-slos-via-littles-law-on-queue-depth)
  - [P2 — Kingman Tail-Latency Prediction for Alert Thresholds](#p2--kingman-tail-latency-prediction-for-alert-thresholds)
  - [P3 — USL-Based Regression Detection Across Releases](#p3--usl-based-regression-detection-across-releases)
  - [P4 — Bufferbloat Detection from p99/p50 Spread](#p4--bufferbloat-detection-from-p99p50-spread)
  - [P5 — Priority-Queue Analysis for Tiered SLOs](#p5--priority-queue-analysis-for-tiered-slos)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Alert Thresholds on Raw Latency Without ρ Context](#a1--alert-thresholds-on-raw-latency-without-ρ-context)
  - [A2 — SLOs That Ignore CV² of Service Time](#a2--slos-that-ignore-cv-of-service-time)
  - [A3 — Using ρ Alone as the Saturation Signal](#a3--using-ρ-alone-as-the-saturation-signal)
  - [A4 — Ignoring Jackson-Network Propagation When Alerting on a Single Service](#a4--ignoring-jackson-network-propagation-when-alerting-on-a-single-service)
- [Recipes](#recipes)
  - [R1 — Saturation SLO: Little's Law → Lq Alert → p99 Budget](#r1--saturation-slo-littles-law--lq-alert--p99-budget)
  - [R2 — Release Regression Check via USL Fit Before and After Deploy](#r2--release-regression-check-via-usl-fit-before-and-after-deploy)
  - [R3 — End-to-End Latency Budget via Jackson Network → Component p99 Allocation](#r3--end-to-end-latency-budget-via-jackson-network--component-p99-allocation)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Saturation SLOs via Little's Law on Queue Depth

**Primitive**: [Little's Law (#1)](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)

**Problem**: Latency-based SLO alerts are reactive — they fire only after p99 has already breached the budget. The underlying saturation signal that causes p99 to spike is queue depth: requests waiting to be dispatched. Queue depth exceeds its steady-state level before p99 crosses any threshold, making it the correct leading indicator.

**Approach**: Little's Law establishes the consistent relationship between queue depth (L), arrival rate (λ), and mean system time (W):

```
L = λ × W
```

Invert this to set a proactive alert on queue depth:

1. Determine your p99 SLO budget, e.g., `W_slo = 200 ms`.
2. Measure your mean arrival rate λ from production (e.g., `rate(http_requests_total[5m])`).
3. Compute the queue depth threshold at which mean latency will approach the SLO:
   ```
   L_alert = λ × W_slo
   ```
   For λ = 500 req/s and W_slo = 200 ms: L_alert = 500 × 0.2 = 100 in-flight requests.
4. Alert when observed in-flight concurrency `L_observed > L_alert`.

The queue depth alert fires before p99 breaches because queue depth is a cause and p99 is an effect. The headroom between L_alert and actual SLO breach gives responders time to investigate.

**Consistency check**: If measured `L_observed ≠ λ × W_mean` by more than 20%, the measurement windows are misaligned (different time bases, mixed populations). Investigate before trusting either metric. A divergence typically indicates hidden queues — thread pool, connection pool, or upstream buffer — not captured in the telemetry.

**Tooling anchor**: Prometheus gauge `http_requests_in_flight` or `http_server_active_requests` (OpenTelemetry semantic convention `http.server.active_requests`). Grafana panel overlaying L_observed vs. L_alert. K6 load test: set `vus` = L_alert as the concurrency ceiling.

**Outcome**: A queue-depth alert that fires 30–120 seconds ahead of a p99 SLO breach, giving an actionable window before user impact.

---

### P2 — Kingman Tail-Latency Prediction for Alert Thresholds

**Primitive**: [Kingman's Formula (#7)](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md)

**Problem**: Alert thresholds based on M/M/1 assumptions (pure Poisson arrivals, exponential service) systematically underestimate real tail latency. Cloud-native services have bursty HTTP arrivals (CV²_a > 1) and variable service times from database lookups, LLM calls, or downstream fan-out (CV²_s >> 1). Setting an alert threshold calibrated on M/M/1 will fire too late or not at all.

**Approach**: Use Kingman's G/G/1 heavy-traffic approximation to predict the mean queue wait at a given utilization ρ:

```
Wq ≈ (ρ / (1 − ρ)) × ((CV²_a + CV²_s) / 2) × E[S]
```

The variability factor `VF = (CV²_a + CV²_s) / 2` is the multiplier that separates real p99 from the M/M/1 prediction:

| VF | Queue wait vs. M/M/1 baseline |
|----|-------------------------------|
| 0.5 | 50% of M/M/1 |
| 1.0 | Equal to M/M/1 |
| 2.5 | 2.5× M/M/1 — common for bursty HTTP + DB calls |
| 5.0 | 5× M/M/1 — common for LLM or batch processing tiers |

**Calibrating alert thresholds**:

1. From production traces, compute CV²_a (variance/mean² of inter-arrival times) and CV²_s (variance/mean² of service times, i.e., span durations).
2. Compute VF.
3. Compute Wq(ρ) = Kingman formula for ρ from 0.5 to 0.9 in steps of 0.05.
4. Find ρ* such that `Wq(ρ*) + E[S] = p99_slo_budget × 0.80` — build in 20% margin.
5. Set the CPU or thread-pool utilization alert at ρ*, not at a fixed 80% ceiling.

For a service with CV²_a = 2.0 (bursty arrivals), CV²_s = 3.0 (variable DB latency), E[S] = 20 ms, and p99 SLO = 500 ms, Kingman predicts Wq breach at ρ ≈ 0.62, while M/M/1 would place it at ρ ≈ 0.95. The correctly calibrated alert fires more than 30 utilization points earlier.

**Tooling anchor**: Compute CV²_s from `histogram_stddev² / histogram_mean²` using Prometheus histogram buckets. Compute CV²_a from inter-request interval metrics or sampling trace arrival gaps. Grafana: add a Kingman-derived ρ* annotation to the utilization panel.

**Outcome**: Alert thresholds derived from actual traffic variability, not M/M/1 assumptions. False alarms decrease; missed early-degradation incidents decrease.

---

### P3 — USL-Based Regression Detection Across Releases

**Primitive**: [Universal Scalability Law (#9)](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md)

**Problem**: A release changes throughput at scale. Simple before/after throughput comparisons at a single load level can miss regressions because the USL parameters (contention σ and coherency κ) may worsen even if single-node performance is unchanged. A new release that increases cross-request locking or adds distributed coordination will look fine at low concurrency and degrade severely only at production-level concurrency.

**Approach**: Model throughput as a function of concurrency N using the USL:

```
X(N) = λ × N / (1 + σ(N − 1) + κN(N − 1))
```

Fit (σ, κ) from load-test data at multiple concurrency levels (N = 1, 2, 4, 8, 16, ...). Compare fitted parameters before and after a release:

| Parameter | Meaning | Regression Signal |
|-----------|---------|-------------------|
| σ (contention) | Serialized resource contention | σ_after > σ_before → new lock or shared resource added |
| κ (coherency) | Cross-node coordination cost | κ_after > κ_before → new distributed state or consensus path |
| N_max | Optimal concurrency ceiling | N_max_after < N_max_before → scaling regression |

**Retrograde flag**: if `X(N_prod)_after < X(N_prod)_before` for production concurrency `N_prod`, the release causes retrograde. Fail the release gate.

**CI integration**: run load tests at 5–6 concurrency levels in the staging environment. Fit USL via non-linear least squares. Compare σ and κ to the main-branch baseline. Flag if either degrades by more than 10% or if N_max drops below N_prod.

```python
from scipy.optimize import curve_fit
import numpy as np

def usl(N, lam, sigma, kappa):
    return lam * N / (1 + sigma * (N - 1) + kappa * N * (N - 1))

# N_vals: concurrency levels tested; X_vals: measured throughput
popt, _ = curve_fit(usl, N_vals, X_vals, p0=[X_vals[0], 0.01, 0.001],
                    bounds=([0, 0, 0], [np.inf, 1, 1]))
lam_fit, sigma_fit, kappa_fit = popt
N_max = np.sqrt((1 - sigma_fit) / kappa_fit) if kappa_fit > 0 else np.inf
```

**Tooling anchor**: K6 or Artillery load tests with stepped concurrency. Grafana: USL curve overlay on throughput panel. Prometheus `rate(http_requests_total[1m])` as X(N) measurement at each load step.

**Outcome**: A quantitative, release-gating regression check that catches contention and coherency regressions invisible to single-concurrency benchmarks.

---

### P4 — Bufferbloat Detection from p99/p50 Spread

**Primitive**: [Bufferbloat (#8)](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)

**Problem**: A service appears healthy by throughput and error rate metrics but delivers terrible user experience at high load because of a standing queue in an unbounded application buffer. The signature is a large and growing gap between p99 and p50 latency under load — p50 stays flat (requests processed quickly when dispatched) while p99 climbs (requests waiting long in the buffer before dispatch).

**Approach**: The p99/p50 latency ratio is a bufferbloat signal:

```
Spread ratio = p99_latency / p50_latency

Healthy:    Spread ratio ≤ 3–5×  (tail from service-time variance only)
Warning:    Spread ratio 5–15×   (buffer accumulation under load)
Bufferbloat: Spread ratio > 15×  (standing queue; buffer likely unbounded)
```

At high ρ, Kingman's formula and Little's Law together predict the expected spread ratio for a given CV² and queue depth. If the observed spread exceeds the Kingman prediction by 3× or more, an unbounded buffer or insufficient backpressure is the root cause — not service-time variability.

**Diagnosing the buffer location**: bufferbloat can occur at multiple layers. Identify which layer by checking queue depth metrics:

| Layer | Metric to check | Tool |
|-------|----------------|------|
| Application thread pool | `threadpool.queue.size` or `executor.queue.remaining_capacity` | JVM JMX, Node.js `libuv` |
| HTTP server backlog | `net.connections` or `socket_queue_length` | eBPF / `ss -s`, Beyla |
| Kafka consumer | `kafka.consumer.lag`, `records-lag-max` | Kafka JMX, Prometheus Kafka exporter |
| Database connection pool | `db.pool.pending_requests` | OTEL semantic convention `db.client.connections.wait_time` |

**Fix**: Set a finite queue depth proportional to the Bandwidth-Delay Product (BDP):

```
BDP = RTprop × bottleneck_rate
Optimal_queue_depth ≈ 2–3 × Lq(M/M/1) = 2–3 × (ρ² / (1 − ρ))
```

For ρ = 0.80, Lq = 3.2 requests. Set maximum queue depth at 10. Add backpressure (HTTP 429 or gRPC RESOURCE_EXHAUSTED) when full.

**Alert**: `histogram_quantile(0.99, ...) / histogram_quantile(0.50, ...) > 10` sustained over 5 minutes. Wire this alert as a secondary check alongside the primary p99 SLO alert.

**Tooling anchor**: Prometheus `http_request_duration_seconds` histogram. Grafana heatmap to visualize the latency distribution shift under load. OpenTelemetry Collector `spanmetrics` connector to derive p50/p99 from trace data.

---

### P5 — Priority-Queue Analysis for Tiered SLOs

**Primitive**: [Priority Queues (#5)](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md)

**Problem**: A service handles multiple request classes with different SLO requirements — for example, interactive API requests (p99 < 100 ms) and background batch jobs (p99 < 10 s) sharing the same worker pool. Without explicit priority assignment, batch jobs can occupy workers and delay interactive requests to SLO violation, even at moderate overall utilization.

**Approach**: Apply non-preemptive priority queue analysis to predict per-class wait time and verify the SLO for each tier.

For a two-class system (class 1 = high priority, class 2 = low priority) on M/G/1 base:

```
Wq_1 = W0 / (1 − ρ₁)
Wq_2 = W0 / ((1 − ρ₁)(1 − ρ₁ − ρ₂))

where:
  W0 = (λ₁ × E[S₁²] + λ₂ × E[S₂²]) / 2  (residual service time)
  ρ₁ = λ₁ × E[S₁]
  ρ₂ = λ₂ × E[S₂]
```

**SLO validation per tier**:

1. Collect per-class arrival rates and service time histograms from production traces (segmented by `request_type`, `priority`, or `user_tier` span attribute).
2. Compute ρ₁, ρ₂, W0, Wq_1, Wq_2.
3. Verify `Wq_1 + E[S₁] ≤ SLO_interactive` and `Wq_2 + E[S₂] ≤ SLO_batch`.
4. If the SLO for class 1 is violated, lower ρ_total or explicitly throttle class 2 to increase headroom for class 1.

**Starvation guard**: priority inversion occurs when ρ₁ ≈ 1. Class 2 wait time → ∞ as ρ₁ → 1. If class 1 can consume 100% of capacity, reserve a minimum fraction of workers for class 2 (e.g., dedicate 1 of c workers exclusively to class 2) to prevent starvation.

**Tiered SLO dashboard**: track `p99_latency` split by `request_priority` label. Alert when class 1 p99 exceeds its SLO tier. Use the priority-queue prediction as the expected-value overlay on the dashboard to confirm whether observed wait matches theory.

**Tooling anchor**: OpenTelemetry span attribute `request.priority` or `user.tier`. Prometheus label split: `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{priority="high"}[5m]))`. Kafka: separate topics per priority tier with consumer group partitioning ratios.

---

## Anti-Patterns

### A1 — Alert Thresholds on Raw Latency Without ρ Context

**Symptom**: An alert fires when `p99_latency > 300 ms`. On a Saturday morning at low traffic (λ is 20% of peak), the same service runs at ρ = 0.15. A cache miss or slow downstream call occasionally pushes p99 to 320 ms. Alert fires; on-call investigates; finds nothing wrong; goes back to sleep. Alert fatigue accumulates.

**Why it's wrong**: Raw latency thresholds conflate service-time variance (expected tail at any ρ) with queuing delay (grows only as ρ → 1). At low ρ, p99 reflects service-time distribution alone — CV² > 1 services will regularly hit high p99 without any queuing degradation. The correct alert condition requires both a high absolute latency *and* a high ρ to indicate true saturation.

**Fix**: Gate the p99 alert on ρ context:

```promql
# Fire only when p99 is high AND utilization is elevated
(
  histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.300
)
and
(
  rate(http_requests_total[5m]) / on(service) service_capacity_requests_per_second > 0.70
)
```

Where `service_capacity_requests_per_second` is the measured service rate μ (from load tests). Alternatively, use queue depth (P1) as the ρ-aware leading indicator and make p99 a lagging confirmation.

---

### A2 — SLOs That Ignore CV² of Service Time

**Symptom**: An SLO states "p99 < 200 ms at ρ ≤ 0.80." The SLO was derived from M/M/1 math at ρ = 0.80. In production, the service hits its SLO budget at ρ = 0.55 because service-time CV²_s = 4.0 (high variance from mixed fast cache hits and slow database calls). The team tightens the alert threshold but does not understand why the original SLO budget was wrong.

**Why it's wrong**: M/M/1 assumes CV²_s = 1. The P-K formula corrects this:

```
Wq(M/G/1) = (ρ × E[S] × (1 + CV²_s)) / (2(1 − ρ))
```

At CV²_s = 4 and ρ = 0.80: Wq = (0.80 × E[S] × 5) / (2 × 0.20) = 10 × E[S]. At CV²_s = 1: Wq = (0.80 × E[S] × 2) / (0.40) = 4 × E[S]. The actual wait is 2.5× higher than the SLO model assumed. Any SLO derived from M/M/1 math without measuring CV²_s is optimistically wrong.

**Fix**: Measure CV²_s from the service-time histogram (Prometheus histogram or APM span duration distribution). Apply P-K or Kingman to derive the ρ* at which the SLO will breach. Encode CV²_s in the SLO documentation alongside the target ρ. Re-derive SLOs whenever the workload mix changes significantly (e.g., after adding a new request type with different service-time characteristics).

---

### A3 — Using ρ Alone (Without Queue Depth) as the Saturation Signal

**Symptom**: The runbook says "page on-call when CPU utilization > 80%." At 80% utilization, the service has been building a queue for 15 minutes: Lq = ρ²/(1 − ρ) = 0.64/0.20 = 3.2 requests mean, but due to CV² = 3, actual queue depth is 10–15 requests. Users have been experiencing elevated p99 for 10 minutes already. The ρ alert fired on time, but by then the SLO budget was already burned.

**Why it's wrong**: ρ is a derived summary of rate and capacity. It does not capture whether queuing delay has already materialized. Little's Law shows that L = λ × W grows with W, not with ρ directly. A queue depth metric integrates the latency impact over time and is thus a more direct saturation signal. A service can reach ρ = 0.80 from below in 30 seconds (no queue accumulation) or drift there over 10 minutes (significant queue accumulation). ρ alone cannot distinguish these cases.

**Fix**: Alert on both ρ (as a leading utilization indicator) and Lq (as the queue-accumulation indicator). Lq is the queueing-theory-grounded SLO signal. ρ > ρ* triggers a warning; Lq > L_alert (derived from Little's Law against the p99 SLO) triggers the page. See P1 and Recipe R1 for the precise construction.

---

### A4 — Ignoring Jackson-Network Propagation When Alerting on a Single Service

**Symptom**: A downstream database service develops a slow-down. Its p99 latency triples. An alert fires on the database service. The upstream API service — which calls the database on 70% of requests — shows no active alert. On-call investigates only the database tier. Meanwhile, the upstream API service's p99 has been climbing for 5 minutes (waiting on the slow database) and is about to breach its own SLO. A second page fires; on-call scrambles.

**Why it's wrong**: In a Jackson network of services, the effective arrival rate at each downstream station is derived from the upstream routing matrix. A latency increase at station k propagates back to upstream stations as increased holding time. If station k's mean service time doubles, every upstream station that routes to k sees its W increase proportionally (by Little's Law: W_upstream increases because requests spend more time in the system).

**Fix**: Build end-to-end trace-based SLO coverage. For each critical service chain, alert on the end-to-end latency (from the entry service to the terminal service) in addition to per-service alerts. Use distributed trace data to construct the critical path: the slowest sequential chain of spans. Alert when the critical-path latency exceeds the end-to-end SLO budget, regardless of which component is slow. Jackson-network flow balance equations (Recipe R3) identify which stations to instrument with pre-emptive queue-depth alerts so that upstream services fire before downstream user impact.

---

## Recipes

### R1 — Saturation SLO: Little's Law → Lq Alert → p99 Budget

**Goal**: Define a queue-depth alert threshold for a service that fires before p99 breaches its SLO budget. Wire it as a Prometheus alert rule alongside the SLO burn-rate alert.

**Primitives used**: Little's Law (#1), Kingman (#7), Bufferbloat (#8).

**Inputs**:

- p99 SLO target: `W_p99_slo` (e.g., 200 ms)
- Mean arrival rate: `λ` (from `rate(http_requests_total[5m])`)
- Mean service time: `E[S]` (from APM span mean or `histogram_sum / histogram_count`)
- CV²_s and CV²_a: from service-time and inter-arrival-time histograms

**Steps**:

**Step 1 — Compute ρ* via Kingman**

Find the utilization ρ* at which Kingman predicts mean queue wait Wq will consume 50% of the p99 budget:

```python
def kingman_wq(rho, cv2_a, cv2_s, mean_service_s):
    if rho >= 1.0:
        return float('inf')
    VF = (cv2_a + cv2_s) / 2.0
    return (rho / (1.0 - rho)) * VF * mean_service_s

# Binary search for rho* where Wq = 0.5 × W_p99_slo
# (leaving 50% budget for service time and tail variance)
w_budget = W_p99_slo * 0.5
rho_lo, rho_hi = 0.01, 0.99
for _ in range(50):
    rho_mid = (rho_lo + rho_hi) / 2.0
    if kingman_wq(rho_mid, cv2_a, cv2_s, mean_service_s) < w_budget:
        rho_lo = rho_mid
    else:
        rho_hi = rho_mid
rho_star = rho_lo
```

**Step 2 — Derive L_alert via Little's Law**

```python
# Queue depth at rho* — this is the alert threshold
Wq_star = kingman_wq(rho_star, cv2_a, cv2_s, mean_service_s)
L_alert = lambda_mean * (Wq_star + mean_service_s)  # in-flight concurrency
```

**Step 3 — Write the Prometheus recording rules and alert**

```yaml
groups:
  - name: saturation_slo
    rules:
      # Record current in-flight concurrency (Little's L)
      - record: job:http_in_flight:current
        expr: http_requests_in_flight

      # Record the arrival rate (Little's λ)
      - record: job:http_arrival_rate:5m
        expr: rate(http_requests_total[5m])

      # Queue-depth saturation alert — fires before p99 SLO breach
      - alert: SaturationQueueDepthHigh
        expr: |
          http_requests_in_flight
          > 100     # L_alert from Step 2 — replace with computed value
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "In-flight concurrency exceeds Little's Law saturation threshold"
          detail: "L_alert=100, current={{ $value }}, rho_star=0.72"
          runbook: "https://runbooks.example.com/saturation-queue-depth"

      # Validate Little's Law consistency — detect hidden queues
      - alert: LittlesLawViolation
        expr: |
          abs(
            http_requests_in_flight
            - (
                rate(http_requests_total[5m])
                * histogram_sum(http_request_duration_seconds)
                  / histogram_count(http_request_duration_seconds)
              )
          )
          / http_requests_in_flight > 0.30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Little's Law inconsistency: hidden queue suspected"
          detail: "L_observed diverges from λ×W by >30%"
```

**Step 4 — Verify**

Run a load test stepping from ρ = 0.50 to ρ = 0.90 in increments. Confirm:
- `SaturationQueueDepthHigh` fires at ρ ≥ ρ_star and before p99 breaches SLO.
- `LittlesLawViolation` remains silent during normal operation and fires when a thread-pool or connection-pool queue is excluded from the concurrency counter.

**Tooling**: K6 constant-arrival-rate executor (`arrival-rate` scenario). Prometheus `http_requests_in_flight` (OpenTelemetry HTTP server semantic convention). Grafana panel: overlay `L_observed`, `L_alert` (horizontal line), and `p99_latency` on a dual-axis chart.

---

### R2 — Release Regression Check via USL Fit Before and After Deploy

**Goal**: Automatically detect contention (σ) or coherency (κ) regressions introduced by a release. Gate the release or trigger rollback if the USL parameters degrade materially.

**Primitives used**: USL (#9), Little's Law (#1), Kingman (#7).

**Inputs**:

- Load-test throughput at N = 1, 2, 4, 8, 16, 32 concurrent workers: `X(N)` for baseline (main branch) and candidate (release branch)
- Production concurrency `N_prod` (from `http_requests_in_flight` median at peak)

**Steps**:

**Step 1 — Run load tests at stepped concurrency**

Use K6 with `stages` to step concurrency from 1 to 32:

```javascript
// k6 USL load-test script
export const options = {
  scenarios: {
    usl_ramp: {
      executor: 'per-vu-iterations',
      vus: 1,    // start; override per run: k6 run --vus 1/2/4/8/16/32
      iterations: 200,
    },
  },
};
```

Collect `rate(http_requests_total[30s])` at each VU level as X(N).

**Step 2 — Fit USL parameters**

```python
import numpy as np
from scipy.optimize import curve_fit

def usl(N, lam, sigma, kappa):
    """USL throughput model."""
    return lam * N / (1.0 + sigma * (N - 1) + kappa * N * (N - 1))

def fit_usl(N_vals, X_vals):
    popt, pcov = curve_fit(
        usl, N_vals, X_vals,
        p0=[X_vals[0], 0.02, 0.001],
        bounds=([0, 0, 0], [np.inf, 1.0, 1.0]),
        maxfev=10000,
    )
    lam, sigma, kappa = popt
    N_max = np.sqrt((1 - sigma) / kappa) if kappa > 1e-9 else np.inf
    return dict(lam=lam, sigma=sigma, kappa=kappa, N_max=N_max)

baseline = fit_usl(N_baseline, X_baseline)
candidate = fit_usl(N_candidate, X_candidate)
```

**Step 3 — Evaluate regression flags**

```python
def evaluate_regression(baseline, candidate, N_prod, threshold=0.10):
    flags = []

    # Contention regression
    if candidate['sigma'] > baseline['sigma'] * (1 + threshold):
        flags.append(f"CONTENTION REGRESSION: sigma {baseline['sigma']:.4f} → {candidate['sigma']:.4f}")

    # Coherency regression
    if candidate['kappa'] > baseline['kappa'] * (1 + threshold):
        flags.append(f"COHERENCY REGRESSION: kappa {baseline['kappa']:.6f} → {candidate['kappa']:.6f}")

    # N_max regression
    if candidate['N_max'] < N_prod:
        flags.append(f"RETROGRADE AT PRODUCTION: N_max={candidate['N_max']:.1f} < N_prod={N_prod}")

    # Throughput regression at production concurrency
    X_base = usl(N_prod, baseline['lam'], baseline['sigma'], baseline['kappa'])
    X_cand = usl(N_prod, candidate['lam'], candidate['sigma'], candidate['kappa'])
    if X_cand < X_base * (1 - threshold):
        flags.append(f"THROUGHPUT REGRESSION at N={N_prod}: {X_base:.1f} → {X_cand:.1f} req/s")

    return flags

flags = evaluate_regression(baseline, candidate, N_prod=16)
if flags:
    print("RELEASE GATE: FAIL")
    for f in flags:
        print(f"  {f}")
    sys.exit(1)
```

**Step 4 — Add to CI pipeline**

Integrate the regression check as a post-load-test step in the staging CI environment. Emit USL parameters as Prometheus metrics (or CI artifact JSON) to track σ and κ trends across releases:

```yaml
# Grafana annotation added by CI on each deployment
POST /api/annotations
{
  "text": "Release v1.42 — σ=0.032 κ=0.0008 N_max=32",
  "tags": ["deploy", "usl"]
}
```

**Verify**: On a known-bad release (one that introduced a global lock), the regression check must flag a contention increase within the load-test run. On a clean release, the check must pass with σ and κ within 10% of baseline.

**Tooling**: K6 per-VU-iterations executor for controlled concurrency. Grafana: USL curve panel comparing baseline vs. candidate across N. Prometheus: emit `usl_sigma`, `usl_kappa`, `usl_n_max` as custom metrics per deploy.

---

### R3 — End-to-End Latency Budget via Jackson Network → Component p99 Allocation

**Goal**: Given an end-to-end p99 SLO for a microservice chain, allocate per-service latency budgets using Jackson network flow balance. Derive per-service alert thresholds that guarantee the end-to-end SLO when all services are within budget.

**Primitives used**: Jackson Networks (#6), Little's Law (#1), Kingman (#7).

**Inputs**:

- End-to-end p99 SLO: `W_e2e` (e.g., 500 ms)
- Service chain topology: services `S₁, S₂, ..., Sₖ` with routing matrix
- Per-service telemetry: `λᵢ`, `E[Sᵢ]`, `CV²_aᵢ`, `CV²_sᵢ`

**Example system**: checkout flow with four services:

| Service | External γᵢ (req/s) | μᵢ (req/s) | Servers cᵢ | Routes to |
|---------|---------------------|------------|------------|-----------|
| API gateway | 200 | 1000 | 4 | 100% → Auth |
| Auth | 0 | 500 | 2 | 100% → Order |
| Order | 0 | 300 | 3 | 80% → DB, 20% exit |
| DB | 0 | 400 | 4 | 100% exit |

**Steps**:

**Step 1 — Solve Jackson flow balance equations**

```python
# Traffic equations: λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ
# For the example above (no feedback loops):
gamma = {'api': 200, 'auth': 0, 'order': 0, 'db': 0}
routing = {
    'api':   {'auth': 1.0},
    'auth':  {'order': 1.0},
    'order': {'db': 0.8},
    'db':    {},
}
# Solve forward (no cycles here):
lam = {'api': 200}
lam['auth']  = lam['api']  * routing['api'].get('auth', 0)    # 200
lam['order'] = lam['auth'] * routing['auth'].get('order', 0)  # 200
lam['db']    = lam['order'] * routing['order'].get('db', 0)   # 160

# Utilizations
mu = {'api': 1000, 'auth': 500, 'order': 300, 'db': 400}
c  = {'api': 4,    'auth': 2,   'order': 3,   'db': 4}
rho = {svc: lam[svc] / (c[svc] * mu[svc]) for svc in lam}
# rho = {'api': 0.05, 'auth': 0.20, 'order': 0.22, 'db': 0.10}
```

**Step 2 — Estimate per-service mean latency via Kingman**

For each service, apply Kingman to get expected Wᵢ = Wqᵢ + E[Sᵢ]:

```python
cv2_a = {'api': 1.0, 'auth': 1.5, 'order': 1.2, 'db': 2.0}  # from trace data
cv2_s = {'api': 0.5, 'auth': 1.0, 'order': 2.5, 'db': 3.0}  # from span histograms
E_S   = {'api': 0.001, 'auth': 0.002, 'order': 0.0033, 'db': 0.0025}  # seconds

W = {}
for svc in lam:
    rho_i = rho[svc]
    VF_i  = (cv2_a[svc] + cv2_s[svc]) / 2.0
    Wq_i  = (rho_i / (1.0 - rho_i)) * VF_i * E_S[svc]
    W[svc] = Wq_i + E_S[svc]
```

**Step 3 — Compute critical-path end-to-end latency**

The end-to-end mean latency on the critical path (API → Auth → Order → DB) is the sum of per-station W weighted by routing probability:

```python
# Critical path: all 4 services in sequence (routing probability product = 0.8 for DB)
W_e2e_mean = W['api'] + W['auth'] + W['order'] + 0.8 * W['db']
```

Compare to the SLO budget. If `W_e2e_mean > W_e2e_slo × 0.50` (mean exceeds 50% of the p99 budget), there is insufficient headroom for the p99 tail.

**Step 4 — Allocate per-service p99 budgets**

Distribute the remaining budget (after mean latency) proportionally to each service's variability contribution:

```python
# Remaining budget for tail (50% of e2e SLO after mean latency is accounted for)
W_e2e_slo = 0.500  # 500 ms
tail_budget = W_e2e_slo - W_e2e_mean

# Weight each service by its CV²_s contribution
weights = {svc: cv2_s[svc] * E_S[svc] for svc in lam}
total_weight = sum(weights.values())

# Per-service p99 SLO budget (mean W + allocated tail)
p99_budget = {}
for svc in lam:
    tail_share = tail_budget * (weights[svc] / total_weight)
    p99_budget[svc] = W[svc] + tail_share
```

**Step 5 — Wire per-service p99 alerts**

```yaml
# Generated alert rules from p99 budget allocation
groups:
  - name: e2e_latency_budget
    rules:
      - alert: AuthServiceLatencyBudgetExceeded
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket{service="auth"}[5m])
          ) > 0.025    # p99_budget['auth'] in seconds
        for: 3m
        labels:
          severity: warning
          slo_tier: e2e_checkout
        annotations:
          summary: "Auth service p99 exceeds its allocated budget in the checkout SLO"
          e2e_slo_ms: "500"
          service_budget_ms: "25"
          runbook: "https://runbooks.example.com/checkout-latency-budget"

      - alert: OrderServiceLatencyBudgetExceeded
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket{service="order"}[5m])
          ) > 0.060
        for: 3m
        labels:
          severity: warning
          slo_tier: e2e_checkout
```

**Step 6 — Track bottleneck migration**

After each capacity change (scaling a service, changing a routing rule), re-run Steps 1–4. The bottleneck station (highest ρ) may shift. Re-derive budgets and update alert thresholds accordingly. The Jackson product-form result means each station can be analyzed independently after re-solving flow balance — no full-system simulation required.

**Verify**: Using distributed traces from Grafana Tempo or Jaeger, confirm that the sum of sampled per-service p99 spans is within the end-to-end budget on 99% of requests during a representative load test. Flag any service where the observed p99 exceeds its allocated budget — this service is the current latency budget violator.

**Tooling**: OpenTelemetry distributed traces for routing topology discovery. `otelcol` `spanmetrics` connector for per-service latency histograms. Grafana service graph panel for visualizing the Jackson flow with ρ per node. Jaeger / Tempo critical-path analysis for trace-level budget validation.

---

## Composition

These patterns and recipes compose with each other and with the sibling applied references:

| Starting point | Add | Result |
|---|---|---|
| R1 (Lq saturation alert) | P2 (Kingman ρ* calibration) | Queue-depth threshold is Kingman-calibrated to actual CV², not M/M/1 assumption |
| R2 (USL regression) | P2 (Kingman alert threshold) | After detecting σ regression, Kingman shows exactly how much the alert ρ* must shift |
| R3 (Jackson budget) | P5 (priority queues) | Per-service budgets split further by priority tier: high-priority requests get tighter budget within the station |
| P4 (bufferbloat detection) | R1 (Little's Law alert) | p99/p50 spread fires first; Lq alert confirms queue accumulation; both resolve when buffer is bounded |
| P3 (USL regression) | R3 (Jackson budget) | USL fit per station identifies where σ/κ increase is draining the throughput needed to stay within latency budget |

**With control theory (cross-skill)**: apply the Kalman health estimator from [`control-theory-applied.md`](control-theory-applied.md) R3 using the queueing-derived signals (Lq, ρ, p99/p50 spread) as the three fused inputs. The queueing theory patterns calibrate what the signals *mean*; control theory governs how the health score responds to them.

**With information theory (cross-skill)**: apply KL drift detection from [`information-theory-applied.md`](information-theory-applied.md) R3 to the service-time distribution. When KL divergence fires on a latency histogram, use Kingman to quantify how much the changed CV²_s shifts the p99 alert threshold — avoiding a false regression if the distribution shifted but ρ* also improved.

---

## Sources

Primitive playbooks (canonical references for all formulas above):

- [`01-littles-law.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) — L = λW, steady-state conditions, failure modes
- [`05-priority-queues.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) — Non-preemptive and preemptive priority, Wq per class
- [`06-jackson-networks.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) — Product-form solution, traffic equations, bottleneck identification
- [`07-kingman-formula.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) — G/G/1 heavy-traffic approximation, variability factor
- [`08-bufferbloat.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) — BDP rule, AQM, p99/p50 spread diagnosis
- [`09-usl-universal-scalability.md`](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) — USL model, N_max, σ and κ fitting

Primary sources (verify before citing in production runbooks):

- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer. — USL derivation and application.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. — Priority queues (Ch. 18–19), Jackson networks (Ch. 30), Little's Law (Ch. 9).
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.

Sibling references in this skill:

- [`references/slo-design-guide.md`](slo-design-guide.md) — SLO construction and error budget policy
- [`references/alerting-strategies.md`](alerting-strategies.md) — multi-window burn-rate alert design
- [`references/methods-red-use-golden.md`](methods-red-use-golden.md) — RED/USE/Golden Signals framework
- [`references/performance-profiling-guide.md`](performance-profiling-guide.md) — service-time measurement and profiling
- [`references/anti-patterns-best-practices.md`](anti-patterns-best-practices.md) — observability anti-pattern catalog
- [`references/information-theory-applied.md`](information-theory-applied.md) — KL drift detection, sampling budget
- [`references/control-theory-applied.md`](control-theory-applied.md) — health estimator, burn-rate damping
