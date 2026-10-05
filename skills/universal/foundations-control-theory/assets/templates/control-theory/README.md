# Control Theory Primitives — Composition Guide

12 domain-agnostic control theory primitives. Each file is a standalone reference (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) and [`../../../SKILL.md`](../../../SKILL.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-pid-control.md](01-pid-control.md) | Uncontrolled oscillation, steady-state error |
| 2 | [02-feedback-vs-feedforward.md](02-feedback-vs-feedforward.md) | Reactive-only control ignores predictable disturbances |
| 3 | [03-observability-controllability.md](03-observability-controllability.md) | Controlling or monitoring states that cannot be reached or seen |
| 4 | [04-lyapunov-stability.md](04-lyapunov-stability.md) | No proof of convergence; loop may diverge |
| 5 | [05-mpc.md](05-mpc.md) | Constraint violations; myopic one-step control |
| 6 | [06-kalman-filter.md](06-kalman-filter.md) | State estimation under noisy measurements |
| 7 | [07-dead-time-compensation.md](07-dead-time-compensation.md) | Oscillation and overshoot caused by transport lag |
| 8 | [08-anti-windup.md](08-anti-windup.md) | Integrator saturation and post-saturation overshoot |
| 9 | [09-gain-scheduling.md](09-gain-scheduling.md) | Single fixed-gain controller fails across operating regimes |
| 10 | [10-circuit-breaker-backpressure.md](10-circuit-breaker-backpressure.md) | Cascading failure; unbounded queue growth |
| 11 | [11-rate-limiting-token-bucket.md](11-rate-limiting-token-bucket.md) | Overload from bursty traffic; retry storms |
| 12 | [12-deepc-behavioral.md](12-deepc-behavioral.md) | MPC-level control when no plant model is available (unknown dynamics) |

---

## Composition Recipes

### Autoscaler That Does Not Oscillate

**Problem**: Kubernetes HPA oscillates — adds pods, overshoots, removes pods, undershoots.

**Stack**:
1. [PID](01-pid-control.md) — core control loop (CPU utilization → replica count)
2. [Anti-windup](08-anti-windup.md) — freeze integral when replica count is at min/max
3. [Dead-time compensation](07-dead-time-compensation.md) — account for pod startup lag
4. [Gain scheduling](09-gain-scheduling.md) — different gains at low/mid/high load

**Sequence**: Measure CPU → PID with anti-windup → Smith Predictor applies dead-time offset → scheduled gains adjust for current load regime.

---

### Stable Agent Loop with Budget Control

**Problem**: An agentic reasoning loop runs tool calls without bounded cost or convergence guarantee.

**Stack**:
1. [Token bucket](11-rate-limiting-token-bucket.md) — admission control on tool calls per step
2. [Circuit breaker](10-circuit-breaker-backpressure.md) — isolate failing tools; fail fast
3. [Lyapunov termination](04-lyapunov-stability.md) — define a potential function (uncertainty/cost remaining) that must decrease each step; hard limit as fallback
4. [MPC planning](05-mpc.md) — plan token allocation across remaining steps before executing

**Sequence**: MPC allocates token budget per step → token bucket enforces per-call rate → circuit breaker isolates broken tools → Lyapunov check verifies step reduces uncertainty.

---

### Budget Pacing Without Windup or Oscillation

**Problem**: Ad campaign daily spend oscillates — underspends overnight, overspends at peak, jams at bid cap, recovers with a lag.

**Stack**:
1. [PID](01-pid-control.md) — spend rate error → bid multiplier adjustment
2. [Anti-windup](08-anti-windup.md) — bid multiplier clamped at platform min/max; freeze integral at limits
3. [Feedforward](02-feedback-vs-feedforward.md) — time-of-day schedule pre-adjusts bid before measurement confirms the error
4. [Kalman filter](06-kalman-filter.md) — smooth noisy CPM/spend signals before feeding to PID

**Sequence**: Kalman-filtered spend rate → error to PID → anti-windup on bid clamps → feedforward adds schedule signal → combined bid multiplier applied.

---

### Predictive (Feedforward-Dominant) Autoscaler

**Problem**: Reactive HPA/KEDA lags behind predictable load patterns — startup lag means pods arrive after the spike.

**When**: Load is forecastable (periodic, trending) AND pod startup lag dominates the latency budget.

**Stack**:
1. [Kalman filter](06-kalman-filter.md) — smooth noisy request-rate time series
2. [Feedforward](02-feedback-vs-feedforward.md) — forecast load; scale before demand arrives; preempt startup-lag penalty
3. [Dead-time compensation](07-dead-time-compensation.md) — encode startup time L in the forecast horizon (scale N steps ahead)
4. [Anti-windup](08-anti-windup.md) — freeze integral at min/max replica bounds

**Empirical reference**: Tymoshenko et al. (2026, arXiv:2604.19705): 26ms median vs. 154ms KEDA vs. 522ms HPA on Node.js/Kubernetes steady ramp.

---

### Multi-Agent Constraint Arbitration

**Problem**: Several agents each defend a different objective and resolve conflicts by negotiating — nondeterministic, unauditable, sensitive to prompt and temperature.

**Stack**:
1. Scoped loops ([Lyapunov](04-lyapunov-stability.md)) — one agent per controlled variable; no agent writes another's actuator
2. MIN/MAX selectors — arbitrate competing controlled variables over one actuator
3. Split-range logic — order multiple actuators serving one controlled variable by cost
4. [Circuit breaker](10-circuit-breaker-backpressure.md) + [token bucket](11-rate-limiting-token-bucket.md) — unchanged, per tool

**Sequence**: Each agent reports its loop's error → orchestrator applies fixed priority order → selector picks the governing loop → split-range engages actuators in cost order. Arbitration never calls the model.

**Reference**: Nogueira & Skogestad (2026, arXiv:2606.30877). Architecture is the transferable claim; the 4-day dairy-barn ventilation evaluation is illustrative.

---

### Distributed System Resilience Stack

**Problem**: Microservice calls to downstream APIs fail intermittently; queues grow under load; recovery is slow.

**Stack**:
1. [Circuit breaker](10-circuit-breaker-backpressure.md) — isolate failed downstream services
2. [Backpressure](10-circuit-breaker-backpressure.md) — slow producer when queue depth grows
3. [Rate limiter / token bucket](11-rate-limiting-token-bucket.md) — cap retry rates; prevent retry storm when circuit re-closes
4. [Dead-time compensation](07-dead-time-compensation.md) — account for recovery lag before reducing circuit-open timeout

**Sequence**: Failure rate exceeds threshold → circuit opens → backpressure signals to producer → token bucket gates retries on probe success → circuit closes when recovery confirmed.

---

## Related

- Primitives overview: [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md)
- Skill entry point: [`../../../SKILL.md`](../../../SKILL.md)
- Sources: [`../../../data/sources.json`](../../../data/sources.json)
