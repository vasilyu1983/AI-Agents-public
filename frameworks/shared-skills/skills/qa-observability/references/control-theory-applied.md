# Control Theory Applied to Observability

> **Gate before invoking:** Check [`foundations-control-theory` § When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Alerting and health scoring are feedback control problems. Signals are noisy, pipelines introduce delay, incidents saturate dashboards, and a single bad threshold causes either alert storms or silent failures. Control theory supplies the tools to reason about each failure mode precisely and to select a correct remedy rather than a heuristic one.

This reference applies the 11 primitives from [`foundations-control-theory`](../../foundations-control-theory/SKILL.md) to the specific constraints of metric pipelines, SLO burn-rate alerts, and service-health state estimation.

---

## Contents

- [Patterns](#patterns)
  - [P1 — Alert Hysteresis (Schmitt-Trigger Feedback Control)](#p1--alert-hysteresis-schmitt-trigger-feedback-control)
  - [P2 — Derivative-Based Detection (Rate-of-Change SLOs)](#p2--derivative-based-detection-rate-of-change-slos)
  - [P3 — Kalman-Style Fused Service-Health State Estimation](#p3--kalman-style-fused-service-health-state-estimation)
  - [P4 — Dead-Time-Aware Alert Thresholds](#p4--dead-time-aware-alert-thresholds)
  - [P5 — Anti-Windup for Long-Burning Incidents](#p5--anti-windup-for-long-burning-incidents)
- [Anti-Patterns](#anti-patterns)
  - [AP1 — Threshold-Only Alerts on Noisy Signals (Chatter)](#ap1--threshold-only-alerts-on-noisy-signals-chatter)
  - [AP2 — No Cooldown Window — Flap City](#ap2--no-cooldown-window--flap-city)
  - [AP3 — Raw Derivative as Trend (No Filtering)](#ap3--raw-derivative-as-trend-no-filtering)
  - [AP4 — Ignoring Measurement Dead-Time When Timing Alert Acks](#ap4--ignoring-measurement-dead-time-when-timing-alert-acks)
  - [AP5 — Competing Alerts With No Priority Scheduling](#ap5--competing-alerts-with-no-priority-scheduling)
- [Recipes](#recipes)
  - [R1 — Anti-Flap Alert Tuning](#r1--anti-flap-alert-tuning)
  - [R2 — Burn-Rate Alert With Derivative Damping](#r2--burn-rate-alert-with-derivative-damping)
  - [R3 — Health-Score State Estimator](#r3--health-score-state-estimator)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Alert Hysteresis (Schmitt-Trigger Feedback Control)

**Primitive**: [PID Control — derivative term](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md) and implicit bang-bang hysteresis in threshold comparators. The Schmitt trigger is a comparator with two distinct thresholds — one to arm the alert and a lower one to resolve it — rather than a single crossing point.

**Problem it solves**: A single threshold at exactly the SLO boundary causes rapid ON/OFF toggling whenever the signal oscillates around that value. One minute the error rate is 0.101%, the next it is 0.099% — the alert fires and resolves in every scrape interval. This is the observability equivalent of an underdamped P-only controller hunting around the setpoint.

**Mechanism**:

```
ALERT fires when:    signal > threshold_high   (e.g., error_rate > 0.15%)
ALERT resolves when: signal < threshold_low    (e.g., error_rate < 0.08%)

Hysteresis band = threshold_high − threshold_low

The signal must cross the band fully in either direction before the state flips.
```

The width of the band is a direct translation of the PID derivative-damping concept: you are introducing enough separation between the fire and resolve thresholds to absorb the noise amplitude of the signal.

**Setting the band**:

1. Collect 30 days of the raw signal at scrape resolution (no rate windows).
2. Measure the peak-to-peak noise amplitude under normal conditions.
3. Set `threshold_high = slo_boundary + (1.5 × noise_amplitude)`.
4. Set `threshold_low = slo_boundary − (0.5 × noise_amplitude)`.

The asymmetric placement keeps the alert sensitive to real violations while giving it a generous path to resolution. A tighter threshold_low means the alert holds longer during recovery — acceptable for SLO signals where "almost resolved" is not the same as "safe."

**Observability implementation**:

In Prometheus, implement hysteresis with a `for` clause for arming and a separate `for` clause (or resolved delay in Alertmanager) for resolution:

```yaml
- alert: ErrorRateHigh
  expr: rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.0015
  for: 3m          # must stay above threshold_high for 3 min before firing
  labels:
    severity: warning
  annotations:
    summary: "Sustained error rate above SLO boundary"

# Pair with Alertmanager resolve_timeout to prevent instant resolution:
# resolve_timeout: 5m   # signal must drop below threshold_low for 5 min before resolving
```

---

### P2 — Derivative-Based Detection (Rate-of-Change SLOs)

**Primitive**: [PID Control — derivative term (Kd)](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md)

**Problem it solves**: Absolute-value SLO alerts detect sustained violations but fire too late during fast ramps. If error rate climbs from 0.01% to 1% in 90 seconds, an alert gated on the 0.5% threshold fires only after the damage is largely done. The derivative of the signal — the rate of change — carries early warning information that the absolute value discards.

**Mechanism**:

The PID derivative term `Kd · de/dt` reacts to the speed of error growth, not just its size. Translated to alerting: define a rate-of-change SLO alongside the level SLO.

```
Level SLO:       error_rate > 0.5%          → fire (lagging indicator)
Derivative SLO:  Δerror_rate/Δt > 0.1%/min → fire (leading indicator)
```

Both fire independently. The derivative alert is a canary; the level alert is the confirmed incident. A two-signal system produces fewer missed incidents during rapid degradation.

**Low-pass filter requirement**: Raw derivatives amplify noise catastrophically. Before computing the slope, smooth the input with a low-pass filter. In Prometheus, `rate()` over a 5m window is already a smoothed estimate of the per-second rate; the second derivative (rate-of-change of the rate) requires an explicit smoothing step:

```yaml
# Detect acceleration in error rate — signal must be sustained across 10 min
- alert: ErrorRateAccelerating
  expr: |
    deriv(
      rate(http_errors_total[10m])[30m:]
    ) > 0.00001   # > 0.001%/min acceleration
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Error rate rising rapidly — investigate before SLO breach"
```

The `deriv()` function in Prometheus computes a least-squares linear regression slope over the provided range — this is the low-pass filtering step, not an instantaneous difference (see AP3).

---

### P3 — Kalman-Style Fused Service-Health State Estimation

**Primitive**: [Kalman Filter](../../foundations-control-theory/assets/templates/control-theory/06-kalman-filter.md)

**Problem it solves**: No single metric is a reliable proxy for service health. Error rate can spike briefly from a single downstream retry batch. p95 latency can be elevated by a large file export. Saturation (CPU, thread pool) can be temporarily high during a batch job without user impact. Alerting on any one signal produces both false positives and missed incidents. What is needed is a fused estimate of true service health that weighs each signal by its reliability.

**Mechanism**:

Model the service as a scalar hidden state `h(k)` representing "true health" on a 0–1 scale, with 1 = fully healthy. Three noisy measurements feed into the estimator:

```
y1(k) = error_rate_normalized     (R1 = high noise — burst-sensitive)
y2(k) = p95_latency_normalized    (R2 = medium noise)
y3(k) = saturation_normalized     (R3 = medium noise)
```

A simplified scalar Kalman filter with vector observations:

```
Predict:
  h⁻(k) = h(k−1)                        (health is a random walk)
  P⁻(k) = P(k−1) + Q                    (Q = process noise; health can change)

Update (for each measurement yi):
  Ki  = P⁻ / (P⁻ + Ri)                  (Kalman gain per signal)
  h(k) = h⁻ + K_fused · innovation       (weighted correction)
  P(k) = (1 − K_fused) · P⁻
```

In practice, implement as an exponentially-weighted moving average (EWMA) per signal, then combine:

```python
def update_health_score(
    prev_score: float,
    error_rate: float,        # 0..1, where 0 = no errors
    p95_latency_ms: float,    # raw ms
    saturation_pct: float,    # 0..100
    # Noise weights (higher R = less trust in this signal)
    R_error: float = 0.10,
    R_latency: float = 0.05,
    R_saturation: float = 0.05,
    Q: float = 0.02,          # how fast health can change
) -> float:
    # Normalize signals to 0..1 degradation scores
    d_error    = min(error_rate / 0.05, 1.0)          # 5% errors = fully degraded
    d_latency  = min(p95_latency_ms / 2000.0, 1.0)    # 2s p95 = fully degraded
    d_sat      = min(saturation_pct / 90.0, 1.0)      # 90% saturation = fully degraded

    # Kalman gains
    P_prior = min(prev_score * (1 - prev_score) + Q, 1.0)
    K_error    = P_prior / (P_prior + R_error)
    K_latency  = P_prior / (P_prior + R_latency)
    K_sat      = P_prior / (P_prior + R_saturation)

    # Degradation estimate (fused)
    degradation = (
        K_error    * d_error    +
        K_latency  * d_latency  +
        K_sat      * d_sat
    ) / (K_error + K_latency + K_sat)

    return 1.0 - degradation
```

**Result**: A single `health_score` time series that changes slowly unless multiple signals confirm degradation. Alert on the fused score, not on individual signals. This score becomes the single source of truth for incident pages.

---

### P4 — Dead-Time-Aware Alert Thresholds

**Primitive**: [Dead-Time Compensation (Smith Predictor)](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)

**Problem it solves**: In control theory, acting on a stale measurement as if it were current causes the controller to overshoot or oscillate. In observability, the equivalent error is setting alert thresholds and `for` durations without accounting for the pipeline delay between the real event and the alert notification.

A typical telemetry pipeline has compounding dead time:

```
Event occurs
  → SDK buffer flush: +5–30s
  → Collector batching: +10–30s
  → Prometheus scrape interval: +15–60s
  → Alertmanager group_wait: +30s
  → Alertmanager evaluation: +1m
  → PagerDuty delivery: +5–15s

Total pipeline dead time L: 2–4 minutes typical, up to 10 minutes under load
```

**Consequences of ignoring dead time**:

- A 1-minute `for` duration inside a 3-minute pipeline means the alert effectively fires only after 4 minutes of real violation time — the SLO may already be materially breached.
- Setting SLO burn-rate alert thresholds at exactly the SLO boundary assumes instantaneous measurement. The real threshold needs to account for the budget already consumed during the dead-time window.

**Dead-time-adjusted burn-rate budget loss**:

```
Budget consumed during dead time = burn_rate × L / (30 days × 24h × 60min)

For L = 3 min, burn rate = 14.4x, SLO = 99.9% (30-day budget = 43.2 min):
  Budget lost in pipeline: 14.4 × 3 / 43200 = 0.1% of monthly budget

At critical burn rates, 0.1% per mis-alert is significant.
```

**Implementation**: Measure pipeline dead time empirically once per environment using a synthetic error injection test. Record the timestamp of injection versus the timestamp of the first fired alert. Subtract this measured `L` from the `for` duration in all burn-rate alerts so that the stated evaluation window reflects real violation time, not pipeline-padded time.

```yaml
# Without dead-time correction — misleading
- alert: SLOBurnCritical
  expr: burn_rate > 14.4
  for: 5m      # appears to require 5 real minutes of violation

# With dead-time correction (measured L = 2.5 min)
- alert: SLOBurnCritical
  expr: burn_rate > 14.4
  for: 2m30s   # 5m target − 2m30s dead time = 5 real minutes of violation
  annotations:
    dead_time_L: "2m30s"
    pipeline_measured: "2026-01-15"
```

---

### P5 — Anti-Windup on Long-Burning Incidents

**Primitive**: [Anti-Windup](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md)

**Problem it solves**: In a PID controller, the integral term accumulates indefinitely while the actuator is saturated — producing a massive overshoot when saturation ends. In observability, the equivalent phenomenon is an incident that fires dozens of related alerts while the service is degraded. When the service recovers, the alert system floods operators with a cascade of resolves and re-fires as each alert crosses its threshold at a different moment. The "saturation" here is the operator's attention budget.

**Mechanism**:

The integrator in an alert pipeline is the accumulation of unique alert states (firing) during a sustained incident. Anti-windup in observability has two forms:

**1. Alert suppression during parent incidents (inhibition)**:

Do not allow child alerts to accumulate while a parent incident is active. Use Alertmanager inhibit rules to suppress lower-priority alerts when a higher-level health alert is firing.

```yaml
# alertmanager.yaml
inhibit_rules:
  # Suppress individual signal alerts while the fused health score is critical
  - source_match:
      alertname: ServiceHealthCritical
    target_match_re:
      alertname: "(ErrorRateHigh|LatencyHigh|SaturationHigh)"
    equal: ["service", "namespace"]
```

**2. Cool-down window after recovery (resolve delay)**:

Just as back-calculation in anti-windup prevents the integral from over-correcting when saturation ends, a resolve delay in the alert pipeline prevents a burst of resolve→re-fire transitions when the service is on the boundary of recovery.

```yaml
# Alertmanager global config
resolve_timeout: 10m   # signal must stay below threshold for 10 min before resolve notification
```

**3. Incident-active flag to gate new notifications**:

Maintain an incident-active boolean (from a ticketing system or on-call tool). While incident is active, route new alert firings to the existing incident thread rather than creating new pages. This is the direct analog of clamping the actuator — the "control output" (new page creation) is bounded while the system is already at its limit.

---

## Anti-Patterns

### AP1 — Threshold-Only Alerts on Noisy Signals (Chatter)

Alerting on a raw metric with a single threshold and no `for` clause or hysteresis band. The signal fluctuates across the boundary on every scrape cycle, producing page noise that trains engineers to ignore the alert.

**Control theory diagnosis**: P-only bang-bang controller at the setpoint — no derivative damping, no hysteresis. The system oscillates indefinitely because there is no mechanism to resist crossing.

**Fix**: Apply P1 (alert hysteresis). Measure the noise floor first; set the high threshold above noise + SLO boundary, the low threshold inside it.

---

### AP2 — No Cooldown Window — Flap City

An alert fires, the service recovers momentarily, the alert resolves, then fires again within the same minute — possibly dozens of times over an hour. Each cycle produces a new page, a new incident ticket, or a new Slack notification.

**Control theory diagnosis**: Missing the equivalent of the derivative kick suppressor or the Schmitt-trigger hysteresis. The controller has no memory of its recent state and treats each measurement independently.

**Fix**: Add a `resolve_timeout` in Alertmanager (minimum 5–10 minutes for P2 alerts) and a `for` clause of at least 2× the scrape interval before firing. See P1 and Recipe R1.

---

### AP3 — Raw Derivative as the Trend (No Filtering)

Computing `instant_change = current_value − previous_value` and alerting when this exceeds a threshold. A single anomalous scrape produces a false alert; a real trend that builds gradually is missed because individual step changes are small.

**Control theory diagnosis**: This is the equivalent of applying the PID derivative term directly to an unfiltered measurement. Åström & Murray explicitly warn against this: `de/dt` magnifies any noise present in `e(t)`. The standard fix is to filter the measurement before differentiation, or to use least-squares slope estimation over a window (which is what Prometheus `deriv()` does).

**Fix**: Use `deriv(signal[30m])` in Prometheus — this fits a regression line to 30 minutes of data and returns the slope. Never use `signal[1m] - signal[5m]` style subtraction as a trend detector. See P2 and Recipe R2.

---

### AP4 — Ignoring Measurement Dead-Time When Timing Alert Acks

Setting an SLO-breach response SLA (e.g., "acknowledge within 5 minutes of alert fire") without subtracting the pipeline dead time from the clock. If the pipeline adds 3 minutes of delay between the breach and the page, and the response SLA is 5 minutes, the actual time budget for the engineer is 2 minutes — but the SLA dashboard shows 5.

**Control theory diagnosis**: Treating the measurement timestamp as the event timestamp. This is the same error as ignoring dead time `L` in a Smith Predictor loop: the controller (engineer) responds to a stale state, and the timing assumptions in the control policy are wrong by `L`.

**Fix**: Instrument the full pipeline lag. Emit a timestamp when the SLO is first breached in the raw data. Compare to the timestamp of the Alertmanager notification. The difference is `L`. Subtract `L` from all response-time SLA calculations. See P4.

---

### AP5 — Competing Alerts With No Priority Scheduling

Multiple alerts from the same service fire simultaneously during an incident and route independently to the on-call engineer. The engineer receives six pages across different channels (PagerDuty, Slack, email) for the same root cause. Attention is split; the most important signal (the one that points to root cause) is buried.

**Control theory diagnosis**: No priority function applied to the controller outputs. In MPC terms ([05-mpc.md](../../foundations-control-theory/assets/templates/control-theory/05-mpc.md)), you have multiple actuators competing for the same resource (operator attention) with no cost matrix weighting their outputs. Without a cost function, the system applies all control signals simultaneously regardless of their relative importance.

**Fix**: Implement Alertmanager inhibition rules (see P5). Define a strict alert hierarchy: the fused health score alert is P1; individual signal alerts are P3 when the health score is already firing. Use routing trees to ensure only the highest-priority alert creates a new page; lower-priority alerts append to the open incident.

---

## Recipes

### R1 — Anti-Flap Alert Tuning

**Goal**: Tune a single alert to fire at most once per genuine incident, resolve only when the service is stably recovered, and produce zero flaps under normal noise.

**Inputs**: 30 days of the target signal at scrape resolution, an SLO target, an acceptable false-positive rate.

**Steps**:

**Step 1 — Estimate noise floor**

```python
import numpy as np

signal = np.array([...])   # 30 days of raw signal at 15s scrape resolution

# Rolling std over 5-minute windows (20 samples at 15s cadence)
window = 20
rolling_std = np.array([signal[i:i+window].std() for i in range(len(signal) - window)])
noise_floor = np.percentile(rolling_std, 95)   # p95 noise amplitude
```

**Step 2 — Set Schmitt-trigger thresholds**

```python
slo_boundary = 0.001    # 0.1% error rate SLO threshold
threshold_high = slo_boundary + (1.5 * noise_floor)
threshold_low  = slo_boundary - (0.5 * noise_floor)

print(f"Fire threshold:    {threshold_high:.4f}")
print(f"Resolve threshold: {threshold_low:.4f}")
```

**Step 3 — Set cooldown `for` duration**

The `for` clause should be at least 3× the noise autocorrelation window. If consecutive scrapes are correlated for up to 2 minutes under normal load, use `for: 6m`. This ensures that only a sustained signal — not a noise burst — clears the hysteresis band for long enough to arm the alert.

**Step 4 — Write the Prometheus alert**

```yaml
- alert: ErrorRateSustainedHigh
  expr: |
    rate(http_errors_total[5m])
    / rate(http_requests_total[5m])
    > 0.0018          # threshold_high from Step 2
  for: 6m             # cooldown from Step 3
  labels:
    severity: warning
  annotations:
    summary: "Error rate above SLO boundary for 6 consecutive minutes"
    threshold_high: "0.0018"
    threshold_low:  "0.0007"
    resolve_timeout: "10m"   # set matching resolve_timeout in Alertmanager
```

**Step 5 — Validate against history**

Replay 30 days of metrics through the rule using `promtool test rules`. Count fires. Target: ≤1 fire per genuine incident in the history. If the rule fires during known quiet periods, widen `threshold_high` or extend `for`.

**Verify**: Zero flaps on any rolling 1-hour window in normal operation. All known incidents in history fire within `pipeline_dead_time + for` duration of the breach start.

---

### R2 — Burn-Rate Alert With Derivative Damping

**Goal**: Alert on accelerating SLO degradation before the level threshold is breached, while suppressing false positives from noisy rate spikes.

**Inputs**: Multi-window burn-rate signal, historical noise profile for the burn-rate metric.

**Architecture**:

```
raw_error_rate[5m] → EWMA smoother → burn_rate_signal
                                            ↓
                             rate window 1h → level alert
                             deriv window 30m → derivative alert
```

**Step 1 — Define the smoothed burn-rate signal**

```yaml
# recording rule: pre-compute smoothed error rate
- record: job:http_error_rate:smooth5m
  expr: |
    rate(http_errors_total[5m])
    / rate(http_requests_total[5m])

# burn rate = current error rate / (1 - SLO target)
# SLO target = 0.999 → error_budget_per_second = 0.001
- record: job:slo_burn_rate:1h
  expr: |
    (
      1 - rate(http_requests_total{status!~"5.."}[1h])
      / rate(http_requests_total[1h])
    ) / 0.001
```

**Step 2 — Compute the low-pass filtered derivative**

```yaml
# Slope of burn rate over 30m — Prometheus deriv() uses least-squares regression
# This is the filtered derivative; not a raw delta
- record: job:slo_burn_rate:deriv30m
  expr: deriv(job:slo_burn_rate:1h[30m])
```

**Step 3 — Wire the two-signal alert**

```yaml
rules:
  # Level alert: sustained high burn rate (lagging)
  - alert: SLOBurnRateCritical
    expr: |
      job:slo_burn_rate:1h > 14.4
      and
      job:slo_burn_rate:1h offset 5m > 14.4   # multi-window confirmation
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "SLO budget burning at 14.4x — exhaustion in ~50h"

  # Derivative alert: burn rate accelerating (leading)
  - alert: SLOBurnRateAccelerating
    expr: |
      job:slo_burn_rate:deriv30m > 0.5         # burn rate growing by >0.5x/min
      and
      job:slo_burn_rate:1h > 3.0               # only trigger when already burning
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "SLO burn rate accelerating — investigate before critical threshold"
      runbook: "https://runbooks.example.com/slo-burn-accelerating"
```

**Step 4 — Tune the derivative threshold**

Run `deriv()` over 90 days of historical burn-rate data. Identify the 99th percentile of `deriv30m` during known quiet periods (no incidents). Set the alert threshold at 2× this value to ensure the alert fires only on anomalous slopes, not on ordinary day-to-day variation.

**Verify**: Derivative alert fires ≥5 minutes before level alert during all historical incidents with burn rate ramps. Derivative alert does not fire during routine traffic patterns (deploy completions, end-of-business traffic drops).

---

### R3 — Health-Score State Estimator

**Goal**: Produce a single `service_health_score` (0.0–1.0) by fusing error rate, p95 latency, and saturation through a Kalman-inspired estimator. Use this score as the single source-of-truth for incident page decisions, replacing the three competing individual-signal alerts.

**Inputs**: Three normalized degradation signals, noise covariance parameters calibrated per service.

**Step 1 — Normalize signals to 0..1 degradation scale**

```python
def normalize_signals(
    error_rate: float,       # e.g. 0.005 = 0.5%
    p95_latency_ms: float,   # e.g. 350ms
    saturation_pct: float,   # e.g. 72.0
    # Calibration: what value = fully degraded?
    error_rate_max: float = 0.05,      # 5% error rate → degradation = 1.0
    latency_max_ms: float = 2000.0,    # 2s p95 → degradation = 1.0
    saturation_max_pct: float = 90.0,  # 90% → degradation = 1.0
) -> tuple[float, float, float]:
    d_error = min(error_rate / error_rate_max, 1.0)
    d_lat   = min(p95_latency_ms / latency_max_ms, 1.0)
    d_sat   = min(saturation_pct / saturation_max_pct, 1.0)
    return d_error, d_lat, d_sat
```

**Step 2 — Kalman update loop**

```python
class ServiceHealthEstimator:
    # State x: true degradation (0 = healthy, 1 = fully degraded)
    def __init__(self, Q=0.005, R_error=0.12, R_latency=0.06, R_saturation=0.06):
        self.x = 0.0   # starts healthy
        self.P = 0.5   # high initial uncertainty
        self.Q = Q
        self.R = [R_error, R_latency, R_saturation]

    def update(self, d_error: float, d_latency: float, d_saturation: float) -> float:
        # Predict
        P_prior = self.P + self.Q
        x_prior = self.x
        # Sequential scalar Kalman updates per measurement
        for y, R in zip([d_error, d_latency, d_saturation], self.R):
            K = P_prior / (P_prior + R)
            x_prior = x_prior + K * (y - x_prior)
            P_prior = (1 - K) * P_prior
        self.x = max(0.0, min(1.0, x_prior))
        self.P = P_prior
        return 1.0 - self.x   # health = 1 − degradation
```

**Step 3 — Emit as a Prometheus gauge (Python exporter, evaluated every 30s)**

```python
health_gauge = Gauge("service_health_score",
                     "Kalman-fused service health (0=degraded, 1=healthy)", ["service"])
estimator = ServiceHealthEstimator()

def update_health(service: str):
    d_e, d_l, d_s = normalize_signals(
        fetch_metric("http_error_rate_5m", service),
        fetch_metric("http_latency_p95_ms", service),
        fetch_metric("cpu_saturation_pct", service),
    )
    health_gauge.labels(service=service).set(estimator.update(d_e, d_l, d_s))
```

**Step 4 — Alert exclusively on the fused score**

```yaml
# Primary incident page — replaces all individual-signal P1 alerts
- alert: ServiceHealthCritical
  expr: service_health_score < 0.3
  for: 3m
  labels:
    severity: critical
  annotations:
    summary: "Service health critically degraded (score < 0.3)"
    runbook: "https://runbooks.example.com/service-health-critical"

# Warning tier
- alert: ServiceHealthDegraded
  expr: service_health_score < 0.6
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Service health degraded (score < 0.6) — investigate"
```

**Step 5 — Calibrate Q and R per service using historical incidents**

Replay historical incidents through the estimator. Tune:
- `Q` upward if the estimator reacts too slowly to known incidents.
- `R_error` upward if single-signal error spikes cause false health dips.
- `R_latency` downward if latency is the most reliable predictor for this service.

**Verify**: Health score drops below 0.3 within 5 minutes of confirmed incident start in ≥90% of historical incidents. Health score remains above 0.6 during all known non-incident periods. Score recovers to > 0.9 within 10 minutes of confirmed incident resolution.

---

## Composition

The three recipes compose into a complete alerting control system:

| Layer | Recipe | Primitive | Role |
|-------|--------|-----------|------|
| Signal conditioning | R3 (health estimator) | Kalman Filter (#6) | Fuse noisy signals into stable state |
| Leading detection | R2 (derivative alert) | PID Kd (#1) | Early warning before threshold breach |
| Sustained detection | R1 (anti-flap hysteresis) | Schmitt trigger / PID damping (#1) | Confirmed level violation, no flap |
| Attention budget | P5 (anti-windup) | Anti-Windup (#8) | Cap alert volume during incidents |
| Lag correction | P4 (dead-time) | Dead-Time Compensation (#7) | Align alert timing to real violation time |

**Loading order**:

1. Start R3 first — the health score is the foundation. Individual-signal alerts should be inhibited while the health score is the active incident signal.
2. Add R1 per critical signal that matters before the health score catches up (e.g., payment error rate where even a 1-minute window matters).
3. Add R2 on burn-rate signals where ramp speed (not level) is the primary risk indicator.
4. Apply P4 corrections to all `for` durations after measuring pipeline dead time in each environment.
5. Wire P5 inhibition rules to prevent the R1 and R2 alerts from competing with the R3 health score alert during active incidents.

---

## Sources

- Åström & Murray, *Feedback Systems* (2020), Chapters 8, 10, 11 — Kalman filter, PID with derivative filtering, dead-time compensation. [https://fbsbook.org](https://fbsbook.org)
- Ziegler & Nichols (1942), "Optimum Settings for Automatic Controllers," ASME Trans. 64:759-768 — PID tuning foundations; the source of derivative-damping rationale.
- Kalman, R.E. (1960), "A New Approach to Linear Filtering and Prediction Problems," ASME J. Basic Engineering 82:35-45 — state estimation under noise.
- Smith, O.J.M. (1957), "Closer control of loops with dead time," Chemical Engineering Progress 53(5):217-219 — dead-time compensation.
- Bohn & Atherton (1995), "An analysis package comparing PID anti-windup strategies," IEEE Control Systems 15(2):34-40 — anti-windup in bounded actuator systems.
- Google SRE Workbook (2018), Chapter 5: "Alerting on SLOs" — multi-window burn-rate alert design; the burn-rate table used in R2 originates here.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Chapters 2, 4, 8 — applying control theory primitives to computing-system metrics.
- Welch & Bishop, "An Introduction to the Kalman Filter," UNC-Chapel Hill TR 95-041 — practical Kalman filter implementation guide.
