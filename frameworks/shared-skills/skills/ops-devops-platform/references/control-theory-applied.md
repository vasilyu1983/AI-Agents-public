# Control Theory Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-control-theory` § When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-02._

Control theory is not abstract here. Every deployment pipeline, autoscaler, and CI queue is a dynamical system with a setpoint, a feedback path, and a failure mode. This reference maps the 11 primitives from [foundations-control-theory](../../foundations-control-theory/SKILL.md) onto the concrete problems that platform and DevOps engineers face daily.

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 Deployment-Frequency Control Loop](#p1-deployment-frequency-control-loop)
  - [P2 Feature-Flag Rollout as MPC](#p2-feature-flag-rollout-as-mpc)
  - [P3 Canary Analysis as Kalman-Style Estimator](#p3-canary-analysis-as-kalman-style-estimator)
  - [P4 Build and CI Queue Stabilization](#p4-build-and-ci-queue-stabilization)
  - [P5 Cost Autoscaler with PID on Spend](#p5-cost-autoscaler-with-pid-on-spend)
  - [P6 Rollback as Derivative-Controlled Response](#p6-rollback-as-derivative-controlled-response)
  - [P7 Gain-Scheduled Deploys by Operational Regime](#p7-gain-scheduled-deploys-by-operational-regime)
- [Anti-Patterns](#anti-patterns)
  - [A1 Linear Traffic Ramp with No Slow-Signal Observability](#a1-linear-traffic-ramp-with-no-slow-signal-observability)
  - [A2 Canary Verdict on a Single Noisy Metric](#a2-canary-verdict-on-a-single-noisy-metric)
  - [A3 CI Auto-Merge Without Backpressure on Test Capacity](#a3-ci-auto-merge-without-backpressure-on-test-capacity)
  - [A4 Aggressive Cost-Down Without Anti-Windup](#a4-aggressive-cost-down-without-anti-windup)
  - [A5 Rollback on One-Sample Spikes](#a5-rollback-on-one-sample-spikes)
- [Recipes](#recipes)
  - [R1 Canary with Kalman Fusion](#r1-canary-with-kalman-fusion)
  - [R2 Cost Autoscaler with Anti-Windup and Gain Scheduling](#r2-cost-autoscaler-with-anti-windup-and-gain-scheduling)
  - [R3 CI Capacity Stabilizer with Token Bucket](#r3-ci-capacity-stabilizer-with-token-bucket)
- [Composition Guide](#composition-guide)
- [Sources](#sources)

---

## Patterns

### P1 Deployment-Frequency Control Loop

**Primitive**: [PID Control](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md)

**Problem**: DORA elite target is four or more deploys per day. Teams that deploy once a week are in a low-frequency equilibrium that self-reinforces: large batches increase risk, risk triggers longer review cycles, long cycles reduce frequency further. Breaking out requires treating deployment frequency as a controlled variable with an explicit setpoint.

**Structure**:

```
setpoint r  = target deploys/week (e.g., 20)
measurement y = actual deploys/week (7-day rolling average)
error e     = r − y
control u   = adjust: merge-queue capacity, deploy-pipeline parallelism, batch size limit

u[k] = Kp·e[k] + Ki·T·Σe[j] + (Kd/T)·(e[k] − e[k−1])
```

The **proportional term** reacts to the current shortfall. The **integral term** identifies systemic drag — review bottlenecks, flaky tests, slow artifact builds — that produces persistent negative error. The **derivative term** catches regression: a sudden drop in frequency signals a new blocker to investigate before it compounds.

**Implementation in practice**:
- Instrument deploys with a DORA metrics dashboard (Datadog DORA plugin, LinearB, or a simple GitHub Actions counter writing to a metrics endpoint).
- Setpoint is a team agreement, not a metric threshold alarm. Define it in an SLO document alongside error budget.
- Actuators: merge queue concurrency (GitHub Merge Queue slots), pipeline parallelism (GitHub Actions runner count), maximum PR batch size for auto-merge.
- Dead time: the deployment pipeline itself is the transport lag. A 20-minute pipeline means frequency cannot exceed three deploys per hour regardless of controller output. Recognize this bound and do not over-tune Kp trying to compensate for it.

**Tuning note**: Start with proportional-only (Ki = Kd = 0). Only add integral if frequency consistently undershoots across weeks. Add derivative only if the team is in change-freeze periods that cause sudden frequency drops worth detecting as a rate signal.

---

### P2 Feature-Flag Rollout as MPC

**Primitive**: [Model Predictive Control](../../foundations-control-theory/assets/templates/control-theory/05-mpc.md)

**Problem**: A feature-flag rollout to 100% is not a single action — it is a sequence of traffic shifts (1%, 5%, 10%, 25%, 50%, 100%) where each step's outcome should inform the next step's timing and magnitude. A reactive approach waits for problems to occur before pausing. MPC plans the ramp schedule while respecting constraints and predicting risk ahead.

**Structure**:

```
State x(k)  = [rollout_percentage, error_rate_delta, p99_latency_delta]
Input u(k)  = rollout_step_size (e.g., 5pp, 10pp, 25pp — discrete)
Horizon N   = 4–6 steps (one step per observation window, typically 15–30 min)

Constraints:
  u(k) ≥ 0 (no rollback in forward-ramp mode — use separate rollback policy)
  x_error_rate_delta ≤ 0.5%   (error rate must not rise more than 0.5pp)
  x_p99_latency_delta ≤ 20ms  (latency must not increase more than 20ms)

Minimize:
  Σ_{i=1}^{N} [w1·(100 − rollout%) + w2·error_delta + w3·latency_delta]
```

At each observation window, re-solve with updated state. If the optimizer returns u = 0 (no progress is safe given the prediction), hold at current percentage. If constraints are violated, hand off to the rollback policy (see P6).

**Implementation in practice**: Flagger or Argo Rollouts provide the traffic-shifting actuator. The MPC optimizer is a Python script (or a lightweight LP solver) that reads metrics from Datadog or Prometheus and writes the next rollout step to the Argo Rollouts custom resource. The receding-horizon structure means you never commit to a full ramp at deploy time — the schedule emerges from observed state.

**Key constraint**: MPC is only as good as its system model. Seed the model with historical error-rate and latency behavior from similar deploys. For a new service with no history, use conservative constraints and a short horizon (N = 3) rather than relying on an unvalidated model.

---

### P3 Canary Analysis as Kalman-Style Estimator

**Primitive**: [Kalman Filter](../../foundations-control-theory/assets/templates/control-theory/06-kalman-filter.md)

**Problem**: Canary analysis must decide whether a new version is safe to promote. Raw metrics are noisy: a single P99 spike, a brief error-rate blip, or a saturated thread pool may be a measurement artifact, a traffic burst, or a real regression. Deciding on raw signals produces false positives (unnecessary rollbacks) and false negatives (regressions promoted to full traffic).

**Structure — fusing three signal streams**:

```
Signals (noisy measurements):
  y1 = error_rate_delta (canary vs. baseline)    R1 = 0.01² (low noise — discrete events)
  y2 = p99_latency_delta (ms)                    R2 = 15²   (high noise — latency is noisy)
  y3 = cpu_saturation_delta (%)                  R3 = 5²    (medium noise)

State:
  x = true_canary_health_score  (−1.0 bad, 0.0 neutral, +1.0 good)

Model (slowly-varying random walk):
  A = 1, Q = 0.001  (health changes slowly; trust the model between samples)

Observation matrix C maps each signal to a health contribution:
  C = [w_err, w_lat, w_sat]  (weights tuned from historical data)

Kalman gain K weights noisy signals:
  K(k) = P⁻·Cᵀ·[C·P⁻·Cᵀ + R]⁻¹

Fused health estimate x̂(k) feeds the rollout decision:
  x̂ > threshold_promote  → advance rollout
  x̂ < threshold_rollback → trigger rollback
  otherwise              → hold and continue sampling
```

**Implementation in practice**: Flagger supports custom metric providers. Implement the Kalman update loop as a webhook or sidecar that reads from Datadog and writes the fused health score to a Prometheus gauge that Flagger reads as its canary metric. Alternatively, use Kayenta (Spinnaker's automated canary analysis engine) and configure it with weighted metric groups that approximate this fusion.

**Tuning R values**: Set R high for inherently noisy metrics (latency percentiles, saturation percentages). Set R low for clean counters (HTTP 5xx counts per request). The Kalman gain will automatically weight the clean signal more heavily — this is the mechanism, not a hack.

**Innovation as anomaly detector**: The innovation `y(k) − C·x̂⁻(k)` should be near zero if the canary is behaving as expected. A sustained large innovation across all three signals is a stronger rollback signal than any single metric breach.

---

### P4 Build and CI Queue Stabilization

**Primitives**: [Circuit Breaker and Backpressure](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md), [Rate Limiting / Token Bucket](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md)

**Problem**: A PR merge spike — end of sprint, post-standup, release cut — saturates the runner pool. Queued builds time out, flaky retries amplify the queue, and the CI system enters a degraded state that persists for hours after the spike. This is a classic backpressure failure: the producer (PRs merging) is not rate-limited by consumer (runner) capacity.

**Structure**:

```
Consumer capacity signal:
  queue_depth = jobs waiting for a runner (Prometheus gauge from GitHub Actions or Buildkite)
  runner_utilization = running / total runners

Backpressure control:
  if queue_depth > high_watermark (e.g., 50 jobs):
    reduce merge-queue slot concurrency → slow PR admission
  if queue_depth < low_watermark (e.g., 10 jobs):
    restore concurrency

Token bucket on PR-triggered builds:
  fill_rate r = runner_pool_capacity × 0.8  (admit at 80% of capacity)
  burst b     = 2 × r                       (allow short spikes)
  On each PR merge event: consume 1 token
  If bucket empty: queue the merge, retry when tokens available
```

**Implementation in GitHub Actions**: Use a concurrency group with a cancel-in-progress strategy for non-main-branch builds (fast feedback for feature branches) but queue-not-cancel for main (every merge must be verified). A separate workflow limits merge-queue entry rate by setting `max_parallel` on the merge group trigger. Monitor queue depth via the GitHub Actions API and write it to a Datadog metric.

**Circuit breaker on the test pool**: If more than 40% of test runs fail in a 10-minute window (likely a shared infra failure, not code regressions), open the circuit: stop admitting new builds and alert on-call. This prevents false rollbacks caused by CI environment failures rather than code defects.

**Bypass for security patches**: Token bucket admission must have an override. Security CVE fixes, incident rollbacks, and hotfixes bypass the rate limiter via a label (`priority: security`) or a specific workflow dispatch path. Document this explicitly in the runbook to prevent abuse.

---

### P5 Cost Autoscaler with PID on Spend

**Primitives**: [PID Control](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md), [Anti-Windup](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md), [Gain Scheduling](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md)

**Problem**: Cloud cost control is a setpoint-tracking problem. Daily spend has a target (budget allocation). The actuator is the compute footprint: instance type, replica count, spot vs. on-demand ratio. A naive threshold alarm tells you when you are over budget but does not steer you back. A PID loop does.

**Structure**:

```
setpoint r = target daily spend ($)
measurement y = actual spend rate ($ per hour × 24, Datadog cost metric or AWS Cost Explorer)
error e = r − y  (positive = underspend, negative = overspend)

control u = workload scaling factor applied to:
  - spot instance percentage (increase when underspending, decrease when overspending)
  - non-critical replica count (scale up/down)
  - scheduled job concurrency

Actuator limits:
  u_min = baseline replicas (SLO floor — cannot scale below minimum viable capacity)
  u_max = budget ceiling replicas
  → Anti-windup required on both limits
```

**Anti-windup is mandatory**: When the workload is at minimum capacity (u_min), the controller cannot reduce spend further even if `e` is large and negative. Without anti-windup, the integral term accumulates a large "cut cost" signal that fires an aggressive scale-down when capacity is temporarily raised — oscillating between minimum and maximum repeatedly. Freeze the integral whenever u is clamped.

**Gain scheduling for spot reclaim events**: AWS spot reclaim events change the system dynamics instantly — capacity drops 20–30% in under two minutes. At this operating point, the normal PID gains are too slow. Switch to a high-Kp, low-Ki "incident regime" gain schedule triggered by spot reclaim notifications (EC2 instance interruption events via EventBridge). Return to normal gains after 15 minutes of stable capacity.

---

### P6 Rollback as Derivative-Controlled Response

**Primitive**: [PID Control (derivative term)](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md)

**Problem**: Rollback policies that fire on absolute thresholds (error rate > 1%) react too late — the threshold is already breached. Rollback policies that react to any single sample above a threshold fire too eagerly on noise. What matters is the **rate of change** of the error signal: a rapid increase in error rate indicates a real regression even if the absolute level is still below threshold.

**Structure**:

```
signal s(t) = error_rate (or latency P99) from the new version
derivative D = (s(t) − s(t − Δt)) / Δt   (rate of change per minute)

Rollback trigger:
  if s(t) > absolute_threshold OR D > rate_threshold:
    initiate rollback

Example thresholds (tune to your SLO):
  absolute_threshold = 2.0%  (error rate)
  rate_threshold     = 0.5%/min  (error rate rising faster than 0.5pp per minute)
```

**Derivative smoothing**: Raw derivative of a noisy metric is itself noisy. Apply a short EMA (exponential moving average, α ≈ 0.3) to the signal before differentiating. This is the "filtered derivative" approach from PID literature — apply Kd to the smoothed output, not to the raw error.

**Implementation in Argo Rollouts**: Define a custom metric that computes the 1-minute rate of change of the error counter (`rate(http_requests_total{status=~"5.."}[1m])` in PromQL). Add this as a secondary canary metric with a `max` threshold. Flagger has `threshold` and `interval` configuration — set a short interval (30s) and a low threshold to catch rate-of-change early.

**Rollback is not just reset**: After a derivative-triggered rollback, the derivative signal tells you something important — the regression was fast and steep, suggesting a latent defect that appeared under load. Log the rollback trigger signal alongside the deployment metadata. This data feeds the postmortem.

---

### P7 Gain-Scheduled Deploys by Operational Regime

**Primitive**: [Gain Scheduling](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md)

**Problem**: A deploy that is safe at 2 AM Tuesday is risky at 6 PM Friday before a holiday weekend. Deploy risk varies with operating regime. A fixed deploy policy — same canary duration, same rollback thresholds, same approval requirements — does not account for regime differences. Gain scheduling provides the framework to vary deploy aggressiveness with the current operating context.

**Scheduling variable**: `σ = operational_risk_score`, a composite of:
- Time of day (business hours vs. night)
- Day of week (weekday vs. weekend vs. holiday)
- Incident state (no incident / active incident / post-incident stabilization period)
- Service load (p50 request rate relative to peak)

**Regime table**:

| Regime | σ range | Canary duration | Rollback threshold | Approval gate |
|--------|---------|-----------------|-------------------|---------------|
| Low-risk (weekday off-peak) | 0–0.3 | 15 min | Normal (see P6) | Auto |
| Normal (weekday business hours) | 0.3–0.7 | 30 min | Tightened −20% | Auto with PagerDuty quiet |
| High-risk (Friday PM, pre-holiday) | 0.7–0.9 | 60 min | Tightened −40% | Manual approval |
| Incident regime (active P1/P2) | 0.9–1.0 | Block non-hotfix | N/A | Incident commander only |

**Bumpless transfer**: When σ crosses a boundary (e.g., a P1 incident is declared during a rolling deploy in progress), do not abruptly switch policy. Complete the current canary step at its existing thresholds, then apply the new regime for the next step. For the incident regime, pause the rollout after the current step completes rather than interrupting mid-step.

**Implementation**: Encode the regime table as a GitHub Actions workflow condition or an ArgoCD ApplicationSet with overlays. Use a Datadog monitor that writes `operational_risk_score` to a feature flag (LaunchDarkly or Unleash) that the deploy workflow reads. This makes the scheduling variable observable and auditable.

---

## Anti-Patterns

### A1 Linear Traffic Ramp with No Slow-Signal Observability

**Control theory diagnosis**: Unobservable state mode. The rollout controller only observes fast signals (error rate, 5xx count) but the system state includes slow signals (database connection pool exhaustion, memory leak rate, connection timeout accumulation) that only manifest after sustained load at elevated traffic percentages.

**Symptom**: A canary passes at 10% and 25% but causes a production incident at 50% or 100%. Post-incident review finds the slow signal was present and rising throughout the ramp — it just was not being monitored.

**Fix**: Before designing the canary analysis loop, run the observability rank test (Primitive 3): list all state variables that could explain a service degradation. For each, ask whether it is observable within the canary window duration. Add explicit slow-signal monitors — GC pause time trend, DB connection wait time, heap allocation rate — to the canary scorecard alongside the fast signals. Set the canary window duration long enough for slow signals to manifest (30 minutes minimum for services with stateful connections).

**Tooling**: Datadog APM continuous profiler and heap analysis. Prometheus `process_resident_memory_bytes` rate-of-change over the canary window. ArgoCD analysis run with a `successCondition` that checks a slow-signal metric in addition to the fast ones.

---

### A2 Canary Verdict on a Single Noisy Metric

**Control theory diagnosis**: Single-sensor state estimation without noise filtering. Using raw P99 latency as the sole canary signal is equivalent to estimating true service health from one noisy measurement with no model and no filtering. The measurement noise `R` for P99 latency is high (easily 20–50% coefficient of variation). A single sample above threshold proves nothing.

**Symptom**: Canary rollouts are rolled back frequently on noise, eroding team confidence in automated canary analysis. Teams disable automated rollback to stop false positives — eliminating the safety mechanism entirely.

**Fix**: Apply the Kalman-style fusion from P3. Require at least three independent signal streams. Weight signals by their noise level. Use a multi-sample innovation test rather than a single-point threshold: require the signal to exceed threshold in `k` of `n` consecutive samples (a sliding-window filter) or use the fused state estimate from the Kalman update. Spinnaker's Kayenta supports multi-metric weighted scoring; Flagger supports `threshold` with `interval` and `iterations` to enforce multi-sample confirmation.

---

### A3 CI Auto-Merge Without Backpressure on Test Capacity

**Control theory diagnosis**: Producer-consumer queue with no feedback signal. The merge queue (producer) is not rate-limited by the test runner pool (consumer). When PRs arrive faster than runners can process them, the queue grows unboundedly — eventually causing timeout-induced failures that trigger retries, amplifying the overload.

**Symptom**: During high-activity periods (post-sprint, release cut), CI queues balloon to 100+ jobs, build times grow from 8 to 45 minutes, flaky tests accumulate retries, and developers lose confidence in CI signal quality.

**Fix**: Apply the backpressure and token bucket pattern from P4. Set a merge queue concurrency limit proportional to runner pool size (target 75–80% utilization). Expose queue depth as a Prometheus metric. Alert when queue depth exceeds two times the runner pool size. Bypass for security patches and incident hotfixes as documented in P4.

**GitHub Actions specifics**: Use the merge queue feature with `max_parallel` set to `floor(runner_count × 0.75)`. For self-hosted runners, emit a `ci_queue_depth` metric in the post-job step and feed it to an autoscaler that provisions additional ephemeral runners (GitHub Actions Runner Controller on Kubernetes).

---

### A4 Aggressive Cost-Down Without Anti-Windup

**Control theory diagnosis**: Integrator windup at actuator minimum. A cost-reduction policy that continuously reduces spot instance percentage hits the minimum viable spot ratio (e.g., 40% — below which latency degrades). The integral term keeps accumulating "cut cost" signal while the actuator is clamped at the floor. When a traffic event forces an emergency scale-out, the wound-up integral fires an over-aggressive cost-cut immediately after the scale-out, oscillating between spot-heavy and on-demand-heavy configurations.

**Symptom**: Infrastructure cost graphs show a sawtooth pattern — periods of heavy cost cutting followed by expensive scale-outs when SLOs are breached, then immediate cost cutting again. Each cycle stresses the spot reclaim risk and the on-demand cost budget simultaneously.

**Fix**: Add anti-windup to every cost control PID. When spot percentage reaches its floor, freeze the integral. When it reaches its ceiling, freeze the integral in the other direction. The tracking time constant `T_t` should be set to the spot reclaim recovery time (typically 5–15 minutes for a managed node group to stabilize after a reclaim event). See the anti-windup primitive for back-calculation implementation details.

---

### A5 Rollback on One-Sample Spikes

**Control theory diagnosis**: Missing derivative damping combined with no noise filtering. Rollback triggered on a single-sample metric breach is equivalent to a proportional-only controller with no derivative damping — it reacts to noise as aggressively as to signal. A traffic spike that causes a momentary P99 elevation causes an unnecessary rollback, deploys the previous version, which itself causes a brief degradation, which may trigger another rollback of the rollback.

**Symptom**: Automated rollbacks fire on known-benign events (scheduled jobs, traffic bursts, upstream retries). Engineers add exceptions and suppression rules to the rollback policy, progressively hollowing out its coverage until it fires only for catastrophic failures — too late.

**Fix**: As described in P6, require the error signal to show sustained elevation across multiple samples (use a sliding window), or require the rate-of-change to exceed a threshold (derivative trigger), or both. Use the Kalman-filtered health score from P3 rather than raw metrics as the rollback input. Set the minimum sample count to at least three before any rollback is triggered.

---

## Recipes

### R1 Canary with Kalman Fusion

**Goal**: Promote or roll back a canary deployment based on a fused health estimate that is robust to noisy individual metrics.

**Primitives used**: Kalman Filter (#6), Circuit Breaker (#10), MPC (#5) for rollout pacing.

**Tooling**: Flagger or Argo Rollouts (traffic shifting), Prometheus or Datadog (metrics), Python sidecar (Kalman update loop).

```
Step 1 — Signal collection (per 30s scrape interval)
  y1 = rate(http_5xx[1m]) / rate(http_total[1m])   # error rate delta (canary − baseline)
  y2 = histogram_quantile(0.99, latency_bucket)     # P99 latency delta
  y3 = (cpu_usage_canary − cpu_usage_baseline)      # CPU saturation delta

  Normalize all signals to z-scores using baseline rolling stats
  (mean and stddev from last 1 hour of baseline metrics)

Step 2 — Kalman filter state update (Python, runs in analysis webhook)
  # State: scalar health score  x ∈ [−1.0, +1.0]
  # Model: slowly-varying random walk
  A, B, C = 1, 0, array([w_err, w_lat, w_cpu])  # C weights sum to 1
  Q = 0.001   # process noise: health changes slowly
  R = diag([0.01, 0.25, 0.10])  # measurement noise covariances

  x_prior = A * x_hat + B * 0
  P_prior = A * P * A + Q

  y_vec = array([y1_norm, y2_norm, y3_norm])
  innov = y_vec - C * x_prior
  S = C @ P_prior @ C.T + R
  K = P_prior @ C.T @ inv(S)

  x_hat = x_prior + K @ innov
  P = (I - outer(K, C)) @ P_prior

Step 3 — Decision
  if x_hat > +0.3:
    emit metric canary_health_score = x_hat
    # Flagger reads this metric; successCondition: "result > 0.3"
    # Advance rollout by next step size from MPC plan (P2)

  elif x_hat < -0.4 or abs(innov).max() > 3.0:
    # Large innovation across any signal: anomaly detected
    emit canary_health_score = -1.0
    # Flagger triggers rollback

  else:
    # Hold — do not advance, do not rollback
    emit canary_health_score = x_hat
```

**Calibrating noise covariances**: Start with `R` diagonal values set to the empirical variance of each metric measured over 24 hours of stable baseline. Increase R by 2× if your traffic is highly bursty. The filter self-tunes within 3–5 samples as P converges.

**Compose with P2 (MPC)**: The Kalman health estimate feeds the MPC state vector as the canary health dimension. If `x_hat` is trending toward −0.4 (health score declining but not yet below rollback threshold), MPC reduces the next planned rollout step size before the threshold is breached — proactive deceleration rather than reactive rollback.

**Strongest signal combination**: For web services, weight the signals `w_err = 0.6, w_lat = 0.3, w_cpu = 0.1`. Error rate is the cleanest signal (low R1) and has the highest diagnostic value. Latency is noisier (high R2) but catches regressions that do not surface as errors. CPU saturation is a leading indicator of future degradation.

---

### R2 Cost Autoscaler with Anti-Windup and Gain Scheduling

**Goal**: Keep daily cloud spend within a target band, scaling compute up and down via spot instance percentage, without oscillating at actuator limits or failing to react quickly during spot reclaim events.

**Primitives used**: PID (#1) with Anti-Windup (#8), Gain Scheduling (#9), Dead-Time Compensation (#7) for provisioning lag.

**Tooling**: AWS EC2 Auto Scaling Groups, Datadog cost metrics (or AWS Cost Explorer API), Lambda or ECS task running the controller loop.

```
Step 1 — Setpoints and measurement
  r   = daily_budget / 24           # target $/hour
  y   = aws_cost_per_hour           # from CUR or Datadog AWS Cost integration
  e   = r − y                       # positive: under budget, can scale up
                                    # negative: over budget, must scale down

Step 2 — Regime detection (scheduling variable)
  spot_reclaim_active = EC2 interruption event in last 10 minutes (EventBridge)

  σ_normal   = {Kp=0.05, Ki=0.01, Kd=0.002, T_t=600s}
  σ_reclaim  = {Kp=0.15, Ki=0.00, Kd=0.000, T_t=0s}
    # During reclaim: P-only, high gain, no integral, no derivative
    # Recover capacity fast; let normal regime re-engage after 15 min

  Smooth interpolation between regimes:
    α = min(1.0, minutes_since_reclaim / 15)
    Kp = (1−α)·σ_reclaim.Kp + α·σ_normal.Kp

Step 3 — PID with anti-windup
  u_raw = Kp·e + Ki·I + Kd·(e − e_prev)

  Actuator limits:
    u_min = spot_floor_percentage = 0.40   # below this, latency SLO at risk
    u_max = spot_ceiling_percentage = 0.85  # above this, reclaim risk exceeds budget savings

  u_sat = clamp(u_raw, u_min, u_max)

  # Anti-windup: back-calculation
  I = I + e·T + (u_sat − u_raw) / T_t   # T_t = 600s in normal regime

  Apply u_sat → set spot instance percentage in Auto Scaling Group

Step 4 — Dead-time compensation for provisioning lag
  L = 8 minutes  # time for new spot instances to pass health checks and serve traffic
  # Smith Predictor: controller acts on e_pred, not raw e
  e_pred = e − (model_no_delay(u) − model_with_delay(u))
    # model_no_delay: cost if u% spot were instantaneously active
    # model_with_delay: same, shifted by L=8min
```

**Tuning guidance**:
- Start with Kp = 0.05 (a 1% cost deviation produces a 0.05pp change in spot percentage). Observe response over 48 hours before tuning.
- Set T_t (tracking time constant for anti-windup back-calculation) to the expected saturation duration — roughly the time you expect the actuator to be clamped. For overnight periods when demand is low, this is 6–8 hours. Set T_t accordingly rather than leaving it at a short default.
- Do not enable the derivative term until the proportional and integral terms are stable. Derivative gain on cost metrics amplifies the noise in hourly cost sampling.

---

### R3 CI Capacity Stabilizer with Token Bucket

**Goal**: Prevent CI queue saturation by rate-limiting PR build admission relative to available runner capacity, with bypass for high-priority changes.

**Primitives used**: Token Bucket / Rate Limiting (#11), Circuit Breaker and Backpressure (#10).

**Tooling**: GitHub Actions, GitHub Actions Runner Controller (ARC) on Kubernetes, Prometheus + Grafana, a custom webhook or GitHub App that mediates merge queue entry.

```
Step 1 — Measure consumer capacity
  runner_total    = count of registered runners (GitHub Actions REST API)
  runner_active   = count of jobs in `in_progress` state
  runner_idle     = runner_total − runner_active
  queue_depth     = count of jobs in `queued` state

  # Capacity utilization signal
  util = runner_active / runner_total

Step 2 — Token bucket configuration
  r = runner_total × 0.75   # admit at 75% of capacity (tokens per minute)
  b = runner_total × 0.25   # burst: up to 25% over steady rate
  s = 1                     # each PR merge event costs 1 token

  On PR merge event received:
    if bucket_tokens >= s:
      bucket_tokens -= s
      allow merge → trigger CI workflow
    else:
      delay PR merge by 60s and retry
      emit metric ci_admission_delayed{reason="capacity"} += 1

Step 3 — Backpressure on merge queue concurrency
  high_watermark = runner_total × 1.5   # queue depth above which to slow admission
  low_watermark  = runner_total × 0.5

  if queue_depth > high_watermark:
    reduce GitHub Merge Queue max_parallel by 2 (minimum: 1)
    emit metric ci_merge_queue_throttled = 1

  elif queue_depth < low_watermark AND merge_queue_max_parallel < configured_max:
    increase max_parallel by 1 (recovery step)
    emit metric ci_merge_queue_throttled = 0

Step 4 — Circuit breaker on test infrastructure
  window          = 10 minutes
  failure_threshold = 40%  # if >40% of runs fail in 10-minute window
    # → likely infra failure, not code regressions
  action:
    open circuit: set merge_queue max_parallel = 0 (pause merges)
    alert on-call: "CI infra failure suspected"
    probe: allow 1 run per 5 minutes; if success rate > 80% over 3 probes → reclose

Step 5 — Priority bypass
  Labels that bypass token bucket and circuit breaker:
    `priority: security`
    `type: hotfix`
    `incident: active`
  Implementation: webhook checks PR labels before token bucket check
  Audit: log all bypasses to Datadog with PR URL and label
```

**Autoscaler integration**: ARC (Actions Runner Controller) scales the runner pool based on `queue_depth`. The token bucket and ARC work together: the token bucket prevents runaway queue growth while ARC provisions additional capacity. Set ARC's scale-up threshold at `queue_depth > low_watermark` to ensure new runners are provisioned before backpressure engages. Set scale-down delay to 15 minutes to prevent spot-like thrashing of runner instances.

**Operational baseline**: For a team of 20 engineers with 50–80 PRs per day, a pool of 20 runners with this configuration targets:
- Build wait time P95 < 5 minutes under normal load
- Build wait time P95 < 15 minutes during end-of-sprint surge
- Zero queue-induced timeouts (versus 10–20% timeout rate without stabilization)

---

## Composition Guide

These patterns are not independent. The most resilient deploy pipelines stack multiple primitives:

| Deployment phase | Active patterns | Primitives |
|-----------------|-----------------|------------|
| PR build admission | Token bucket (#11), Backpressure (#10) | P4, R3 |
| Feature flag forward ramp | MPC (#5) with Kalman state (#6) | P2, P3, R1 |
| Canary health assessment | Kalman fusion (#6), Derivative trigger (#1 D-term) | P3, P6, R1 |
| Rollback decision | Derivative trigger, Circuit breaker (#10) | P6, A5 fix |
| Post-deploy cost control | PID (#1), Anti-windup (#8), Gain scheduling (#9) | P5, R2 |
| Incident deploy freeze | Gain scheduling regime table (#9) | P7 |

**Composition rule**: Primitives at different timescales compose without coupling. The cost PID (hourly timescale) and the deployment-frequency PID (weekly timescale) share no state and can be tuned independently. The Kalman canary filter (30-second timescale) feeds the MPC rollout planner (15-minute timescale) — these share state and must be tuned together: the Kalman convergence window should be shorter than the MPC step interval.

**Starting point for a new platform**: Implement in this order:
1. R3 (CI stabilizer) — reduces the most common pain without requiring a model.
2. P6 (derivative rollback) — fixes false-positive rollbacks before adding canary automation.
3. R1 (Kalman canary) — adds automated promotion confidence after rollback policy is sound.
4. R2 (cost autoscaler) — add only after deployment reliability is solid; cost oscillation is a distraction when deploy reliability is the bigger problem.

---

## Sources

- Åström, K.J. & Murray, R.M. (2020). *Feedback Systems: An Introduction for Scientists and Engineers*, 2nd ed. Princeton. [https://fbsbook.org](https://fbsbook.org)
- Forsgren, N., Humble, J., & Kim, G. (2018). *Accelerate: The Science of Lean Software and DevOps*. IT Revolution. (DORA metrics and deployment frequency targets.)
- Hellerstein, J.L., Diao, Y., Parekh, S. & Tilbury, D.M. (2004). *Feedback Control of Computing Systems*. Wiley-IEEE.
- Nygard, M. (2018). *Release It! Design and Deploy Production-Ready Software*, 2nd ed. Pragmatic Bookshelf. (Circuit breaker patterns.)
- Kalman, R.E. (1960). "A New Approach to Linear Filtering and Prediction Problems." *ASME Journal of Basic Engineering* 82:35–45.
- Camacho, E.F. & Bordons, C. (2007). *Model Predictive Control*, 2nd ed. Springer.
- Rugh, W.J. & Shamma, J.S. (2000). "Research on gain scheduling." *Automatica* 36(10):1401–1425.
- Turner, J.S. (1986). "New directions in communications." *IEEE Communications Magazine* 24(10):2–9. (Token bucket algorithm.)
- Flagger documentation. [https://docs.flagger.app](https://docs.flagger.app)
- Argo Rollouts documentation. [https://argoproj.github.io/rollouts](https://argoproj.github.io/rollouts)
- Google SRE Book (2016). Ch. 17: "Testing for Reliability." [https://sre.google/sre-book](https://sre.google/sre-book)
- DORA State of DevOps Report 2023. [https://dora.dev](https://dora.dev)
