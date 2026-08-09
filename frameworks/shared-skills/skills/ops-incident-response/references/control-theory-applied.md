# Control Theory Applied to Incident Response

> **Gate before invoking:** Check [`foundations-control-theory` § When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Feedback-control primitives mapped to production operations: autoscaling, cascading-failure isolation, admission control, slow-signal compensation, and traffic-regime switching. Each section names the anchoring primitive and cross-links its full reference.

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — Autoscaling as PID with Anti-Windup](#p1--autoscaling-as-pid-with-anti-windup)
  - [P2 — Circuit Breakers and Bulkheads for Cascading-Failure Isolation](#p2--circuit-breakers-and-bulkheads-for-cascading-failure-isolation)
  - [P3 — Token-Bucket Admission Control During Incident Mitigation](#p3--token-bucket-admission-control-during-incident-mitigation)
  - [P4 — Dead-Time Compensation for Slow-Feedback Signals](#p4--dead-time-compensation-for-slow-feedback-signals)
  - [P5 — Gain Scheduling for Traffic Regimes](#p5--gain-scheduling-for-traffic-regimes)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Manual Scaling That Creates Oscillation](#a1--manual-scaling-that-creates-oscillation)
  - [A2 — Retry Storms (No Damping in the Retry Loop)](#a2--retry-storms-no-damping-in-the-retry-loop)
  - [A3 — Disabling Rate Limits During Recovery](#a3--disabling-rate-limits-during-recovery)
  - [A4 — P-Only Autoscaler Tuning](#a4--p-only-autoscaler-tuning)
  - [A5 — Blackholing as Default Under Partial Failure](#a5--blackholing-as-default-under-partial-failure)
- [Recipes](#recipes)
  - [R1 — Stable Autoscaler Retune](#r1--stable-autoscaler-retune)
  - [R2 — Cascading-Failure Containment](#r2--cascading-failure-containment)
  - [R3 — Recovery Throttling](#r3--recovery-throttling)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Autoscaling as PID with Anti-Windup

**Primitive anchors**: [PID Control](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md), [Anti-Windup](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md)

**The feedback loop.** Kubernetes HPA and AWS Auto Scaling are closed-loop PID controllers: the measurement is utilization (CPU, request rate, queue depth), the setpoint is target utilization, and the actuator is replica count or instance count. The controller computes a delta and applies it on each reconciliation cycle.

```
e[k] = setpoint_utilization − measured_utilization

u[k] = Kp·e[k]
     + Ki·T·Σe[j]      ← integral eliminates steady-state offset
     + (Kd/T)·(e[k] − e[k−1])  ← derivative damps oscillation

replica_delta = round(u[k])
new_replicas  = clamp(current + replica_delta, min_replicas, max_replicas)
```

**Why anti-windup is mandatory here.** When the cluster is at `max_replicas` (actuator saturated), measured utilization may still be above setpoint. The integral term continues accumulating a large positive error. When load finally drops and the scaler begins removing replicas, the wound-up integral fires a large positive command — adding pods just as load is leaving — causing the characteristic overshoot-removal-overshoot oscillation seen in many production autoscaler incidents.

**Fix: freeze integral at actuator limits.**

```python
# Pseudocode — HPA controller loop
def pid_step(e, integral, prev_e, at_max, at_min):
    # Anti-windup: do not accumulate while clamped
    if not (at_max and e > 0) and not (at_min and e < 0):
        integral += e * T
    p_term = Kp * e
    i_term = Ki * integral
    d_term = Kd * (e - prev_e) / T
    return p_term + i_term + d_term, integral
```

**Kubernetes HPA mapping.**
- Measurement: `averageUtilization` from metrics server (sampled every 15 s by default).
- Actuator limits: `minReplicas` and `maxReplicas` in the HPA spec are the anti-windup bounds.
- HPA uses a simplified proportional formula by default; for true PID behavior use KEDA with a custom scaler or VPA + custom controller.
- `--horizontal-pod-autoscaler-downscale-stabilization` (default 5 min) is a crude anti-windup substitute — it delays downscale but does not zero the integral. Explicit integral freeze is more precise.

**Incident signal.** Seeing "replica count oscillates above and below target with a regular period" in a postmortem is the characteristic fingerprint of a PID with missing or misconfigured anti-windup.

---

### P2 — Circuit Breakers and Bulkheads for Cascading-Failure Isolation

**Primitive anchor**: [Circuit Breaker and Backpressure](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md)

**Cascading failure as positive feedback.** When a downstream service degrades, upstream callers accumulate threads or goroutines waiting on slow responses. This reduces upstream throughput, which increases latency, which causes the upstream's own callers to queue — a classic positive-feedback loop with no inherent damping. Circuit breakers and bulkheads are the damping mechanism.

**Circuit breaker state machine (recap).**

```
CLOSED  ──(failures > threshold in window)──► OPEN
OPEN    ──(timeout elapsed)──────────────────► HALF-OPEN
HALF-OPEN ──(probe succeeds)─────────────────► CLOSED
HALF-OPEN ──(probe fails)────────────────────► OPEN (reset timer)
```

When OPEN, calls fail fast (< 1 ms) instead of waiting for the full downstream timeout. This prevents thread exhaustion.

**Bulkheads isolate failure blast radius.** Named after the watertight compartments in ship hulls: dedicate a separate thread pool or connection pool to each downstream dependency. A slow dependency exhausts only its bulkhead, not the shared pool.

```
Without bulkheads:
  slow_db calls → consume all 200 shared threads
  → payment_api calls can't execute
  → checkout fails entirely

With bulkheads:
  slow_db pool: 50 threads (exhausted, returns 503 for DB calls)
  payment_api pool: 50 threads (unaffected)
  → checkout degrades gracefully (no DB features), not full failure
```

**Tuning for incident response.** During an active incident the team adjusts circuit-breaker thresholds in real time:

| Signal | Action |
|--------|--------|
| Dependency latency spikes but failure rate < threshold | Lower failure-rate threshold or shorten window; trip the breaker earlier |
| Breaker trips on transient blip | Widen window or require minimum request count; add latency percentile trigger instead of raw failure rate |
| Recovery is slow after breaker re-closes | Increase half-open probe count; add progressive re-enable (10%, 25%, 50%, 100%) |

**On-call check.** Before manually disabling a circuit breaker under incident pressure, verify: is the downstream healthy (check its own SLO dashboard) or still degraded? Re-closing a breaker into a still-degraded service re-triggers the cascade. Use the half-open probe as the signal, not wall-clock time.

---

### P3 — Token-Bucket Admission Control During Incident Mitigation

**Primitive anchor**: [Rate Limiting / Token Bucket](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md)

**Why admission control is a mitigation tool.** During a database saturation incident the standard mitigation sequence is: (1) identify the bottleneck, (2) reduce load to the bottleneck below its saturation point, (3) restore load gradually as headroom returns. Step 2 is admission control. Without it, every mitigation action — rollback, restart, scaling — re-saturates the bottleneck before it can recover.

**Token bucket as an on-call instrument.** The fill rate `r` and burst capacity `b` are runtime-tunable. In an Nginx, Envoy, or AWS API Gateway rate limit configuration these are live knobs:

```
Normal operation:  r = 500 req/s, b = 1000
Incident (DB sat): r = 150 req/s, b = 300   ← shed 70% of load
Recovery step 1:   r = 250 req/s, b = 500
Recovery step 2:   r = 400 req/s, b = 800
Recovery step 3:   r = 500 req/s, b = 1000  ← full traffic restored
```

**Retry budget as a token bucket.** During recovery, client-side retries must also be rate-limited. Model the retry budget as a separate token bucket with a low fill rate:

```python
RETRY_BUCKET = TokenBucket(fill_rate=0.5, capacity=5)  # max 5 retries; 1 per 2 sec

def call_with_retry(fn, max_attempts=3):
    for attempt in range(max_attempts):
        if not RETRY_BUCKET.consume(1):
            raise RetryBudgetExhausted()
        try:
            return fn()
        except TransientError:
            delay = min(60, 1 * 2**attempt) + random.uniform(0, 1)
            time.sleep(delay)
    raise MaxAttemptsExceeded()
```

**Key invariant.** The token bucket fill rate on retries must be less than the downstream service's recovery throughput. If downstream can accept 100 req/s during recovery and N callers each retry at 2 req/s, break even at N = 50. Above 50 callers the retry load re-saturates the recovering service — the exact failure mode of a retry storm.

---

### P4 — Dead-Time Compensation for Slow-Feedback Signals

**Primitive anchor**: [Dead-Time Compensation](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)

**The problem.** Certain production signals have inherent transport lag between the causal event and the observable metric:

| Signal | Typical lag | Cause |
|--------|------------|-------|
| Queue depth (SQS, Kafka) | 30–120 s | Polling interval + aggregation |
| Pod ready after scale-up | 60–180 s | Container pull + JVM warmup |
| CDN cache miss rate after purge | 2–10 min | Global propagation |
| RDS replica lag | 10 s – minutes | Replication pipeline |
| Batch job completion | Minutes to hours | Job execution time |

If an on-call engineer or an autoscaler uses a signal with a 90-second lag in a feedback loop with a 30-second reconciliation period, the loop fires actions faster than it can observe their effects — classical dead-time instability.

**Smith Predictor for autoscalers.** The controller uses an internal model to predict what the output *would be* if there were no delay:

```
L = 90s  (pod startup dead time)

predicted_capacity(t) = f(replica_request(t − L), capacity_per_pod)

error_compensated(t) = target − (model_no_delay(u(t)) − model_with_delay(u(t))) − measured(t)

Scaler acts on error_compensated, not on the 90s-stale direct measurement.
```

**Practical heuristic (no Smith Predictor implemented).** When the team cannot modify the scaler:

1. Identify L (dead time) via step test: make a deliberate +1 replica change, measure how long until utilization metrics visibly respond.
2. If L > 0.5 × dominant time constant T: increase scaler cooldown period to at least 2L. This is a conservative detuning, not compensation, but it prevents repeated over-scaling.
3. Log "scaling action applied at t=X, effect expected at t=X+L" in the incident timeline. On-call engineers often misread a stale metric as "nothing worked" and over-apply further changes.

**Slow-queue example.** A consumer service is falling behind on a Kafka topic. Queue depth is reported via Datadog with a 60-second aggregation window. The on-call engineer sees the depth rising and adds more consumers. The metric continues to rise for the next 60 seconds (reflecting state *before* the new consumers started). Without awareness of the 60-second lag, the engineer adds more consumers again — over-provisioning by 2×. When the lag window clears, depth drops sharply, the scaler removes consumers, and the oscillation begins.

**On-call rule.** After any scaling action on a lagged signal, insert a mandatory observation window of at least `2 × lag_seconds` before taking another action. Make this explicit in the runbook.

---

### P5 — Gain Scheduling for Traffic Regimes

**Primitive anchor**: [Gain Scheduling](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md)

**Why a single controller fails across regimes.** A Kubernetes HPA tuned for 70% CPU at 200 req/s will oscillate at 1000 req/s (too slow to respond) and over-react at 20 req/s (noise amplification). Traffic regimes are operating points in the control-theory sense: the plant dynamics — time constants, gain, nonlinearity — differ across them.

**Three-regime scheduling example.**

| Regime | Scheduling variable | Kp | Ki | Kd | Cooldown |
|--------|--------------------|----|----|----|----------|
| Off-peak (< 30% target load) | p50 RPS < 200 | 0.03 | 0.004 | 0.008 | 300 s |
| Normal (30–80% target load) | p50 RPS 200–600 | 0.06 | 0.010 | 0.015 | 120 s |
| Peak (> 80% target load) | p50 RPS > 600 | 0.10 | 0.018 | 0.005 | 60 s |

During peak: higher Kp for fast scale-up, lower Kd to avoid derivative kick on noisy latency signals. During off-peak: lower Kp to avoid reacting to noise, longer cooldown to avoid thrashing on low-volume spikes.

**Recovery regime.** A fourth regime unique to incident response: the recovery ramp after a full mitigation. Gains should be conservative — lower Kp, longer cooldown — because the state of the system (cache fill fraction, connection pool warmup, JVM JIT state) is unknown. Once baseline metrics have been stable for 10 minutes, switch back to normal-regime gains.

```
Recovery regime:
  Scheduling variable: "time since incident resolved" < 10 min
  Kp = 0.02 (very conservative)
  Cooldown = 600 s
  Max scale-down rate: −10% replicas per cycle
```

**Bumpless transfer.** When switching regimes, carry the integral state forward:

```python
# When transitioning from normal → peak
new_gains = PEAK_GAINS
# Do NOT reset integral:
# integral = 0  ← wrong: causes step change in output
# Carry integral forward, adjust only Kp/Ki/Kd
controller.gains = new_gains  # integral state unchanged
```

Resetting integral on a regime switch causes a transient output step that looks like a scaler bug in the metrics. Most KEDA and custom controller implementations require explicit handling; the default HPA has no integral state to worry about, but KEDA custom scalers do.

---

## Anti-Patterns

### A1 — Manual Scaling That Creates Oscillation

**Control theory diagnosis**: Open-loop impulse with no feedback and no damping.

Manual scaling during an incident — "add 10 pods now" — is an open-loop impulse. There is no measurement of current error, no integral to eliminate steady-state offset, and no derivative to damp the response. The human operator becomes the feedback loop, but the human loop has:
- Variable reaction time (minutes, not seconds)
- No anti-windup (the engineer keeps adding until it "looks fixed")
- Cognitive load that degrades under incident pressure

**What happens**: pods are added, utilization drops, engineer sees "fixed", removes some pods, utilization rises again, engineer adds more — a 10-to-20-minute oscillation driven by manual action intervals.

**Fix**: trust the automated scaler's feedback loop; use manual intervention only to change setpoints or bounds, not to command raw replica counts. If the scaler is insufficient, fix its parameters — do not bypass it.

---

### A2 — Retry Storms (No Damping in the Retry Loop)

**Control theory diagnosis**: Positive feedback loop with no rate limiting or damping.

When a service returns errors, clients retry. If all clients retry immediately with no backoff:

```
failure → N clients retry simultaneously → N × original load
→ higher failure rate → all clients retry again → (N × original load)²
→ service dies entirely
```

This is unstable positive feedback. The "gain" of the retry loop is > 1 (each retry creates at least as much load as the original request, often more due to connection overhead).

**Exponential backoff with jitter is the damping term.**

```python
def backoff(attempt, base=1.0, cap=60.0, jitter=True):
    delay = min(cap, base * (2 ** attempt))
    if jitter:
        delay += random.uniform(0, delay * 0.25)
    return delay
```

Jitter desynchronizes retry timing across clients — converting the synchronized burst into a smooth ramp. Without jitter, backoff alone still creates synchronized retry waves at each backoff interval boundary.

**Incident implication.** When diagnosing a "waves of errors" pattern on a recovering service, the first question is: do clients have jittered exponential backoff? If not, the recovery will be self-defeating regardless of how much capacity is added.

---

### A3 — Disabling Rate Limits During Recovery

**Control theory diagnosis**: Removing admission control while the plant is still saturated introduces an uncontrolled positive-feedback surge.

The reasoning is intuitive but wrong: "traffic is being shed, users are frustrated, let's let more in so they can succeed." The problem is that the bottleneck resource (database connections, memory, CPU) has not recovered yet. Removing rate limits floods the bottleneck with the previously queued traffic plus new arrivals simultaneously.

**What happens**: rate limits disabled → 5× normal load hits recovering DB → DB saturates again → circuit breakers trip → full outage re-established → MTTR doubles.

**Correct approach**: keep rate limits active throughout recovery. Increase the allowed rate in increments (see Recipe R3). The rate limit is the integral term of the recovery feedback loop — removing it removes the only mechanism preventing overshoot.

---

### A4 — P-Only Autoscaler Tuning

**Control theory diagnosis**: Proportional-only control has inherent steady-state offset and no oscillation damping under nonlinear load.

A P-only controller cannot eliminate steady-state error: if Kp is set to make the scaler responsive, it will overshoot; if set to prevent overshoot, it will maintain a permanent offset from the setpoint. This is the proportional offset law — not a tuning artifact but a mathematical property.

**Practical signature**: HPA holds steady at 75% CPU when target is 60%, regardless of how replicas are adjusted. The permanent offset is `steady_state_error = disturbance / Kp`. Increasing Kp to close the gap increases overshoot risk.

**Fix**: add the integral term (Ki > 0) to eliminate steady-state error, and add derivative (Kd) to damp the resulting oscillatory tendency. Apply anti-windup (Pattern P1) or the I term will cause the exact overshoot the operator was trying to avoid.

---

### A5 — Blackholing as Default Under Partial Failure

**Control theory diagnosis**: Disabling observability collapses the feedback loop. The controller (the on-call team) operates blind.

"Blackholing" a degraded endpoint — routing all traffic away from it without monitoring it — eliminates the feedback signal needed to detect recovery. This is equivalent to removing the sensor from the feedback loop. The controller loses observability of the system state.

**Specific failure mode**: blackholed service recovers at t+15 min, but the on-call team has no signal of this. Traffic stays blackholed for hours. MTTR increases. Users continue to receive degraded service from the reduced-capacity remaining endpoints.

**Correct approach**: maintain a low-volume probe (synthetic transactions or a small traffic percentage) to the isolated component even when it is out of rotation. This is the circuit breaker half-open probe — see Primitive 10. The probe is the feedback signal for recovery detection.

**Observability rule**: never disable metrics collection on a degraded component. Increased log verbosity and metric collection on the degraded path is diagnostic signal; removing it is the anti-pattern.

---

## Recipes

### R1 — Stable Autoscaler Retune

**Objective**: Replace an oscillating HPA configuration with a tuned PID+anti-windup+dead-time-compensated scaler that does not oscillate under load test.

**Primitive stack**: PID (#1) + Anti-Windup (#8) + Dead-Time Compensation (#7) + Gain Scheduling (#9)

**Step 1: Measure the step response.**

```bash
# In a staging environment at steady state:
# 1. Record current replica count and CPU utilization baseline.
# 2. Apply a step load increase: generate 2× normal traffic for 10 minutes.
# 3. Observe CPU until it reaches a new steady state.
# 4. Record:
#    - L: time from load step to first measurable CPU change (dead time)
#    - T: time from first change to 63% of final change (time constant)
#    - K: (final_cpu - initial_cpu) / (final_replicas - initial_replicas) (plant gain)
```

**Step 2: Derive initial gains (Ziegler-Nichols style).**

```
# For a PI controller (recommended over PID for noisy CPU signals):
Ku = 1/K (approximate ultimate gain)
Tu ≈ 2πT (approximate)

Kp_init = 0.45 × Ku
Ki_init = 0.54 × Ku / Tu

# Apply L correction: if L/T > 0.5, reduce Kp_init by 30%
```

**Step 3: Implement anti-windup.**

```python
class PIDAutoscaler:
    def __init__(self, kp, ki, kd, min_r, max_r):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.min_r, self.max_r = min_r, max_r
        self.integral = 0.0
        self.prev_error = 0.0

    def step(self, setpoint, measurement, dt):
        e = setpoint - measurement
        at_max = (self.integral * self.ki >= self.max_r - self.min_r)
        at_min = (self.integral * self.ki <= 0)
        # Anti-windup: freeze integral when clamped in error direction
        if not (at_max and e > 0) and not (at_min and e < 0):
            self.integral += e * dt
        u = self.kp * e + self.ki * self.integral + self.kd * (e - self.prev_error) / dt
        self.prev_error = e
        return int(round(max(self.min_r, min(self.max_r, u))))
```

**Step 4: Add dead-time compensator for slow metrics.**

If queue depth or custom metrics have lag > 30 s:

```python
# Simple Smith Predictor approximation:
# Maintain a ring buffer of past control outputs
# Predicted output = current_model_output - model_output_L_seconds_ago

from collections import deque

class SmithPredictor:
    def __init__(self, L_seconds, sample_period):
        self.buffer = deque(maxlen=int(L_seconds / sample_period))
        self.model_gain = 1.0  # replicas → utilization_delta

    def predicted_error(self, setpoint, measured, u_now):
        u_delayed = self.buffer[0] if len(self.buffer) == self.buffer.maxlen else u_now
        self.buffer.append(u_now)
        model_correction = (u_now - u_delayed) * self.model_gain
        return setpoint - measured - model_correction
```

**Step 5: Add gain schedule.**

```python
def get_gains(current_rps):
    if current_rps < 200:
        return (0.03, 0.004, 0.008)   # off-peak
    elif current_rps < 600:
        return (0.06, 0.010, 0.015)   # normal
    else:
        return (0.10, 0.018, 0.005)   # peak
```

**Step 6: Load test to validate.**

```
Load test protocol:
  1. Ramp load from 0 to 2× target over 5 min.
  2. Hold at 2× for 10 min. Confirm replica count stabilizes ± 2 replicas.
  3. Step-drop load to 0.5× target. Confirm scaler does not overshoot min_replicas.
  4. Ramp back to 1× target. Confirm stabilization without oscillation.
  5. Pass criterion: replica count standard deviation < 10% of mean during steady-state holds.
```

**Verify**: step-response metrics, CPU target tracked to within ±5% at steady state, no oscillation with period < 10 min.

---

### R2 — Cascading-Failure Containment

**Objective**: Stop a cascading failure from spreading across dependency boundaries and establish a controlled recovery path.

**Primitive stack**: Circuit Breaker (#10) + Bulkheads (#10) + Token Bucket (#11) + Gain Scheduling (#9)

**Step 1: Identify the failure origin and its blast radius.**

```
During triage:
  - Check which circuit breakers are OPEN (or should be).
  - Map dependency graph: which upstream services call the failing dependency?
  - Estimate thread/connection exhaustion: is the upstream thread pool saturated?
```

**Step 2: Trip circuit breakers on failing dependencies.**

If breakers are not automated or threshold has not been reached:

```bash
# Envoy admin API — manually force circuit breaker OPEN on a cluster
curl -X POST localhost:9901/clusters/payment_service/circuit_breakers/default/open
```

Or, if using Hystrix / Resilience4j / similar:

```java
// Force OPEN programmatically during incident
circuitBreaker.transitionToOpenState();
```

Verify: upstream service latency drops immediately. If it does not, the upstream is waiting on something else — re-examine the dependency map.

**Step 3: Apply bulkhead isolation.**

If bulkheads are not pre-configured, set thread pool limits in your service mesh or application config for the failing dependency. Accept that the failing-dependency thread pool will exhaust — that is the point. All other pools continue.

**Step 4: Rate-limit retry load via token bucket.**

```python
# Set retry token bucket to 10% of normal throughput to the recovering dependency
RECOVERY_RETRY_BUCKET = TokenBucket(
    fill_rate=normal_rps * 0.10,
    capacity=normal_rps * 0.10 * 5  # 5-second burst
)
```

**Step 5: Progressive recovery via gain schedule.**

Once the failing service signals recovery (health check passing, latency < P99 SLO), re-enable traffic in stages:

```
Stage 0 (OPEN):      0% traffic to dependency, 100% fallback
Stage 1 (HALF-OPEN): 10% traffic; monitor error rate for 5 min
Stage 2:             25% traffic; monitor for 5 min
Stage 3:             50% traffic; monitor for 5 min
Stage 4:             100% traffic; close circuit breaker fully
```

Revert to Stage 0 at any stage if error rate exceeds the original trip threshold. This staged re-enable is the gain schedule applied to recovery — the "gain" (traffic fraction) increases only when the stability criterion is met.

**Step 6: Verify isolation is complete.**

- Upstream service SLO is recovering (latency and error rate dropping).
- Downstream failing service is no longer receiving exponentially growing retry load.
- Bulkhead thread pools for non-affected dependencies show no saturation.

---

### R3 — Recovery Throttling

**Objective**: Restore traffic to a recovered service without re-saturating it, using a feedback-controlled ramp that halts and rolls back if recovery metrics breach a Lyapunov-style termination criterion.

**Primitive stack**: PID (#1) + Token Bucket (#11) + Lyapunov Stability (#4) + Gain Scheduling (#9)

**The recovery feedback loop.** The "setpoint" is the target SLO (e.g., p99 latency < 200 ms). The "measurement" is the current p99 latency. The "actuator" is the allowed traffic fraction (0–100%). The integral term ramps traffic up over time while the p99 stays below the SLO threshold.

**Step 1: Define the Lyapunov termination criterion.**

```python
# Lyapunov potential: distance from SLO
# V(t) = max(0, p99_latency(t) - slo_target) / slo_target

# Recovery is "stable" if V decreases or stays at 0 at each step.
# Rollback condition: V increases for 3 consecutive steps.

def lyapunov_check(p99_history, slo_target):
    V = [max(0, p - slo_target) / slo_target for p in p99_history[-4:]]
    if len(V) < 3:
        return "insufficient_data"
    if V[-1] > V[-2] > V[-3]:
        return "rollback"  # V increasing: system diverging
    if V[-1] == 0:
        return "stable"
    return "continue"
```

**Step 2: Implement the traffic ramp as a PID loop.**

```python
class RecoveryRamp:
    """
    Setpoint: slo_target (latency ms)
    Measurement: current p99 latency
    Actuator: traffic_fraction (0.0 to 1.0)
    """
    def __init__(self, slo_target):
        self.slo_target = slo_target
        self.traffic_fraction = 0.10  # start at 10%
        self.integral = 0.0
        self.prev_error = 0.0
        # Conservative recovery-regime gains (Gain Scheduling #9)
        self.kp, self.ki, self.kd = 0.002, 0.0005, 0.001

    def step(self, p99_latency, dt):
        # Error: negative means headroom (latency below SLO → can increase traffic)
        e = self.slo_target - p99_latency
        # Anti-windup: do not accumulate if at traffic ceiling
        if not (self.traffic_fraction >= 1.0 and e < 0):
            self.integral += e * dt
        delta = self.kp * e + self.ki * self.integral + self.kd * (e - self.prev_error) / dt
        self.prev_error = e
        # Rate limit: max +5% per cycle, max -100% per cycle (instant rollback)
        delta = max(-1.0, min(0.05, delta))
        self.traffic_fraction = max(0.0, min(1.0, self.traffic_fraction + delta))
        return self.traffic_fraction
```

**Step 3: Gate ramp progression on the Lyapunov check.**

```python
def recovery_loop(service, slo_target, check_interval_s=60):
    ramp = RecoveryRamp(slo_target)
    p99_history = []

    while ramp.traffic_fraction < 1.0:
        # Set traffic
        service.set_traffic_fraction(ramp.traffic_fraction)
        time.sleep(check_interval_s)

        # Measure
        p99 = service.get_p99_latency()
        p99_history.append(p99)

        # Lyapunov check
        verdict = lyapunov_check(p99_history, slo_target)
        if verdict == "rollback":
            service.set_traffic_fraction(0.0)
            page_on_call("Recovery ramp failed: p99 diverging. Traffic reset to 0.")
            return "failed"

        # PID step
        new_fraction = ramp.step(p99, check_interval_s)
        log(f"Recovery: traffic={new_fraction:.0%}, p99={p99}ms, verdict={verdict}")

    return "success"
```

**Step 4: Switch to normal-regime gains once stable.**

After 10 minutes at 100% traffic with p99 < SLO, transition from recovery-regime gains to normal-regime gains (Gain Scheduling Pattern P5). Log the transition; include it in the postmortem timeline.

**Expected timeline for a typical database recovery.**

```
t=0:   Incident resolved; DB healthy; 0% traffic.
t=1:   Ramp starts at 10% traffic; p99 = 80 ms (well within SLO 200 ms).
t=5:   Ramp reaches ~35% via integral term; p99 = 120 ms (stable).
t=10:  Ramp reaches ~60%; p99 = 155 ms (approaching SLO; ramp slows).
t=15:  Ramp reaches ~80%; p99 = 180 ms (near SLO; Ki holds).
t=20:  Ramp reaches 100%; p99 stabilizes at 170 ms. Lyapunov: stable.
t=30:  Switch to normal-regime gains. Declare incident fully resolved.
```

---

## Composition

These patterns and recipes compose. The full stack for a resilient production autoscaler under incident conditions:

```
Normal operation:
  Gain Scheduling (P5) selects regime gains
  → PID with Anti-Windup (P1) drives replica count
  → Dead-Time Compensator (P4) corrects slow-metric lag
  → Circuit Breakers (P2) isolate dependency failures
  → Token Bucket (P3) limits request admission

Incident declared:
  + Circuit Breakers OPEN on degraded dependency
  + Token Bucket fill rate reduced to shed load
  + Recovery-regime gains applied (conservative Kp, long cooldown)
  + Lyapunov termination criterion gates any ramp-up

Incident recovering (Recipe R3):
  + Recovery ramp PID drives traffic fraction toward 1.0
  + Lyapunov check halts and rolls back if p99 diverges
  + Gain switch on 10-min stability confirmation
  + Circuit Breaker returns to CLOSED
  + Token Bucket fill rate restored
  + Normal-regime gains resume
```

The key insight from control theory is that each mechanism addresses a distinct failure mode. They do not overlap:

| Mechanism | Failure Mode Addressed |
|-----------|----------------------|
| PID + Anti-Windup | Oscillation and steady-state error in scaling |
| Dead-Time Compensation | Stale metrics causing over-correction |
| Gain Scheduling | Wrong dynamics across traffic regimes |
| Circuit Breaker | Cascading failure from downstream degradation |
| Token Bucket | Retry storms and admission overload |
| Lyapunov Check | Recovery ramp diverging before it's safe to continue |

Running multiple mechanisms does not cause interference provided each is scoped to its own signal and actuator. The token bucket governs admission; the PID governs replica count; the circuit breaker governs dependency health. They share information (e.g., circuit breaker state pauses replica ramp) but each owns a separate control output.

---

## Sources

- Åström, K.J. & Murray, R.M. (2020). *Feedback Systems: An Introduction for Scientists and Engineers*, 2nd ed. Princeton University Press. [https://fbsbook.org](https://fbsbook.org)
- Franklin, G., Powell, J.D. & Emami-Naeini, A. (2019). *Feedback Control of Dynamic Systems*, 8th ed. Pearson.
- Hellerstein, J.L., Diao, Y., Parekh, S. & Tilbury, D.M. (2004). *Feedback Control of Computing Systems*. Wiley-IEEE Press.
- Nygard, M. (2018). *Release It! Design and Deploy Production-Ready Software*, 2nd ed. Pragmatic Bookshelf. (Circuit breaker pattern, Ch. 5.)
- Smith, O.J.M. (1957). "Closer control of loops with dead time." *Chemical Engineering Progress* 53(5):217–219. (Smith Predictor.)
- Turner, J.S. (1986). "New directions in communications." *IEEE Communications Magazine* 24(10):2–9. (Token bucket.)
- Ziegler, J.G. & Nichols, N.B. (1942). "Optimum settings for automatic controllers." *ASME Transactions* 64:759–768.
- Rugh, W.J. & Shamma, J.S. (2000). "Research on gain scheduling." *Automatica* 36(10):1401–1425.
- Fowler, M. "CircuitBreaker." [https://martinfowler.com/bliki/CircuitBreaker.html](https://martinfowler.com/bliki/CircuitBreaker.html)

### Primitive Cross-References (foundations-control-theory)

| # | File |
|---|------|
| 1 | [01-pid-control.md](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md) |
| 4 | [04-lyapunov-stability.md](../../foundations-control-theory/assets/templates/control-theory/04-lyapunov-stability.md) |
| 7 | [07-dead-time-compensation.md](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md) |
| 8 | [08-anti-windup.md](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md) |
| 9 | [09-gain-scheduling.md](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md) |
| 10 | [10-circuit-breaker-backpressure.md](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md) |
| 11 | [11-rate-limiting-token-bucket.md](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md) |
