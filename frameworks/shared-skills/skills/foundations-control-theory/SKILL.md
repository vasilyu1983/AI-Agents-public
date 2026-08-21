---
name: foundations-control-theory
description: Control-theory primitives for PID, MPC, Kalman, stability, anti-windup, dead-time, breakers, and limits. Use when tuning autoscaling, retries, or agent loops.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Control Theory Foundations

12 applied control-theory primitives for feedback control and dynamical systems, backed by a formal theory map. Each primitive owns a specific failure mode in any system that must reach and hold a target state despite disturbances, delays, noise, or nonlinearities. Primitives are domain-agnostic: the same PID loop that controls CPU utilization controls budget pacing and retry rates; the same circuit breaker that isolates a failing database isolates a failing LLM tool.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Anti-Patterns](#anti-patterns)
- [Misuse Boundaries](#misuse-boundaries)
- [Expert Judgment](#expert-judgment)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Navigation](#navigation)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| Primitive | Problem It Solves | Key Parameters |
|-----------|------------------|----------------|
| [PID Control](#1-pid-control) | Drive output to setpoint despite steady-state error and disturbances | Kp, Ki, Kd; tuned via Ziegler-Nichols |
| [Feedback vs. Feedforward](#2-feedback-vs-feedforward) | Reactive-only loops ignore predictable disturbances | Plant model accuracy; disturbance measurability |
| [Observability & Controllability](#3-observability--controllability) | States you cannot see or reach make the loop fail silently | Controllability matrix rank; observability matrix rank |
| [Lyapunov Stability](#4-lyapunov-stability) | No proof that a loop converges; may oscillate or diverge | Lyapunov function V(x); dV/dt < 0 condition |
| [MPC](#5-model-predictive-control-mpc) | One-step control ignores future constraints and couplings | Horizon N; cost matrices Q, R; constraint bounds |
| [Kalman Filter](#6-kalman-filter) | Noisy measurements degrade controller and monitoring accuracy | Process noise Q; measurement noise R; model (A, B, C) |
| [Dead-Time Compensation](#7-dead-time-compensation-smith-predictor) | Transport lag causes oscillation or instability | Dead time L; plant model (delay-free) |
| [Anti-Windup](#8-anti-windup) | Integrator saturates during limit-clamping → overshoot on release | Actuator min/max; tracking constant T_t |
| [Gain Scheduling](#9-gain-scheduling) | Single fixed-gain controller fails across operating regimes | Scheduling variable σ; per-regime gain tables |
| [Circuit Breaker & Backpressure](#10-circuit-breaker--backpressure) | Cascading failure; unbounded queue growth | Failure threshold; timeout; half-open probe logic |
| [Rate Limiting / Token Bucket](#11-rate-limiting--token-bucket) | Bursts and retry storms overload downstream; 429s cascade | Fill rate r; burst capacity b; per-request cost s |
| [DeePC / Behavioral Systems](#12-deepc--behavioral-systems) | MPC without a plant model — unknown dynamics make model-based prediction impossible | Hankel matrix T (data length); regularization λ_g, λ_y; persistency-of-excitation order |

---

## When to Apply

**Apply control-theory when:**
- A measurable variable must track a setpoint over time (autoscaler latency target, rate limiter throughput, retry pacing)
- Feedback loop with measurable lag — current state shapes the next action
- Oscillation or overshoot is observed (system swings around target instead of settling)
- Anti-windup needed — integral term must be clamped during saturation
- Plant has dead-time or transport delay (e.g., pod startup ~45 s)

**Skip and use simpler alternatives when:**
- One-shot decision, no feedback, no setpoint — use foundations-decision-theory
- Static threshold rule that doesn't need to adapt — a constant or hysteresis band is simpler
- Capacity sizing question, not feedback question — use foundations-queueing-theory
- Plant model is unknown and you can't measure error reliably — fix observability first
- Dead-time > 30% of desired settling time — PID alone is insufficient; consider Smith Predictor or MPC
- System is unstable open-loop and you don't know why — diagnose root cause before adding feedback

---

## Primitive Index

Each primitive is summarized here, expanded in [`references/primitives-overview.md`](references/primitives-overview.md), and covered by standalone playbooks under [`assets/templates/control-theory/`](assets/templates/control-theory/). Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs stability assumptions, state-space reasoning, or robustness boundaries.

| # | Mechanism | Failure Mode Addressed |
|---|-----------|----------------------|
| 1 | PID Control | Uncontrolled oscillation or steady-state error in a closed loop |
| 2 | Feedback vs. Feedforward | Reactive-only control cannot anticipate predictable disturbances |
| 3 | Observability & Controllability | Controlling or monitoring states that cannot be reached or seen |
| 4 | Lyapunov Stability | No convergence proof; loop may diverge without warning |
| 5 | MPC | Constraint violations; myopic one-step control |
| 6 | Kalman Filter | State estimation errors from noisy sensors degrade controller performance |
| 7 | Dead-Time Compensation | Transport lag causes oscillation or instability in feedback loops |
| 8 | Anti-Windup | Integrator saturation during actuator clamping -> post-release overshoot |
| 9 | Gain Scheduling | Fixed gains inadequate outside the design operating point |
| 10 | Circuit Breaker & Backpressure | Cascading failure from downstream service failures; unbounded queues |
| 11 | Rate Limiting / Token Bucket | Burst overload and retry storms after failure recovery |
| 12 | DeePC / Behavioral Systems | MPC-level optimization when no plant model is available; unknown or hard-to-identify dynamics |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| State-space systems | Need A/B/C/D models, poles, modes, controllability, observability | #3, #4, #5, #6 |
| Classical feedback | Need loop shaping, root locus, Bode/Nyquist, margins, PID tuning | #1, #2, #7, #8 |
| Stability theory | Need Lyapunov, input-to-state stability, passivity, bounded-input bounded-output | #4, #10, #11 |
| Optimal control | Need LQR/LQG, dynamic programming, constrained optimization, MPC | #5, #6 |
| Robust control | Need uncertainty margins, H-infinity, mu-synthesis, delay robustness | #4, #7, #9 |
| Adaptive/nonlinear control | Need parameter drift, operating regimes, saturation, nonlinear dynamics | #8, #9 |
| Stochastic estimation | Need Kalman assumptions, noise covariance, filtering vs smoothing | #6 |
| Networked/distributed control | Need queueing, backpressure, admission control, cascading-failure boundaries | #10, #11 |
| Safe RL with certificates | Need hard safety constraints in a learned/RL-controlled system at deployment | #4 |
| Online convex optimization / adaptive control | Need regret bounds for algorithms that update controller parameters online | #5 (adaptive MPC) |
| Behavioral systems / Willems' Fundamental Lemma | Need MPC without a parametric model; replace explicit prediction with data-driven Hankel matrix; unknown or nonlinear plant | #12 (DeePC) |
| Advanced regulatory control (ARC) | Need to decompose a multi-loop or multi-agent system into scoped elements with deterministic conflict resolution (selectors, split-range) rather than negotiation | #4, #5, #9 |

---

## Anti-Patterns

| Anti-Pattern | Control Theory Diagnosis | Fix |
|-------------|------------------------|-----|
| P-only autoscaler oscillates around target | Underdamped proportional-only control; no derivative damping | Add derivative term (Kd); tune with Ziegler-Nichols (#1) |
| Integrator windup at actuator limit | Integral accumulates during saturation; releases as large overshoot | Anti-windup on every PID with bounded actuator (#8) — this is always required |
| Reactive controller ignores predictable patterns (load spikes, business hours) | Feedback-only; no model of known disturbances | Add feedforward schedule component (#2) |
| Observability gap: slow-changing state invisible to aggregate metric | Unobservable state mode in measurement design | Observability rank test (#3); add direct sensor or redesign C matrix |
| MPC tuned on stale system model | Model–reality mismatch degrades constraint handling and prediction | Retrain model online; add Kalman filter for state estimation (#6) |
| Dead time treated as additional plant gain | Transport lag misidentified → wrong tuning; oscillation | Smith Predictor (#7); estimate L via step test; never increase Kp to compensate |
| Retry storm after circuit re-closes | All blocked callers retry simultaneously; re-triggers failure | Token bucket with jitter (#11); stagger retries; half-open probe first (#10) |
| Agent loop with no convergence proof | No potential function that decreases per step | Define Lyapunov potential (e.g., remaining uncertainty); add hard step limit as fallback (#4) |
| Gain scheduled without bumpless transfer | Abrupt gain switch causes transient at boundary | Interpolate gains smoothly (#9); transfer integral state during switch |
| Backpressure signal not honored by producer | Queue grows despite signal | Enforce at ingress; drop or block if producer ignores signal (#10) |
| Agent loop passes safety tests in simulation but fails on hardware | CBF applied only at inference, not baked into training; policy never internalized the constraint | CBF-RL: embed CBF as training-time safety filter so policy internalizes constraint before deployment (#4) |
| Multi-agent system resolves constraint conflicts by LLM negotiation | Conflict resolution delegated to a stochastic component; no deterministic priority order | Structural priority: MIN/MAX selectors for competing controlled variables, split-range for competing actuators; orchestrator resolves deterministically regardless of model output (#4, #5) |

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Tuning PID by folklore constants | Ziegler-Nichols is an aggressive starting point, not a guarantee | Test margins and re-tune on the actual plant |
| Ignoring actuator saturation | Integral windup creates overshoot and instability | Add anti-windup to bounded actuators |
| Treating delay as lower gain | Dead time changes phase and can destabilize loops | Estimate delay and use compensation or lower bandwidth |
| Claiming Kalman optimality outside assumptions | Kalman is optimal for linear Gaussian systems | Use EKF/UKF/particle filters with caveats |
| Applying MPC without model validation | Bad model makes constrained optimization confidently wrong | Validate model error and add robust margins. When plant model is unknown: use DeePC (#12) for a model-free alternative, Koopman MPC if a stability certificate is required (Schimperna et al. 2025), or physics-informed sysid if partial domain knowledge exists (Sivaranjani et al. 2025, arXiv:2512.06315). |
| Applying deterministic CBF with noisy measurements | Classical CBFs guarantee forward-invariance only for noise-free dynamics; sensor noise violates the invariance condition | Use stochastic/probabilistic CBF (Echigo et al. 2026, arXiv:2604.08831) or add an explicit safety margin to the CBF constraint. |
| Using circuit breakers without backpressure | Fail-fast alone can shift overload elsewhere | Pair breakers with queues, rate limits, and admission control |
| Calling an agent loop stable because it has max steps | Max steps bound cost, not convergence | Define a potential function or monotone progress metric |

---

## Expert Judgment

What separates a control-theory-literate engineer from someone reading the tables above: recognizing failure before the dashboard shows it, and knowing when the discipline does not apply.

### Recognizing an unstable loop before it visibly oscillates

Visible oscillation is the *late* symptom. By the time replica count or bid multiplier is swinging, margin was gone cycles earlier. Earlier signals, roughly in order of how early they appear:

- **Growing control-signal variance at constant error variance.** If `u` (replicas added/removed, bid delta) is getting noisier while the error it's responding to is not, gain margin is shrinking — the loop is amplifying noise it used to damp. This shows up in `stddev(Δu)` well before it shows up in the tracked metric.
- **Settling time creeping up release over release.** Each correction takes a bit longer to return to setpoint than the previous one. A single slow cycle is noise; a multi-week upward trend is phase margin eroding, usually from an added dependency, a slower downstream, or a metrics pipeline that got an extra aggregation stage.
- **Widening lag between command and effect.** Cross-correlate the actuator command timestamp against the measured-effect timestamp on a rolling window. Dead time is supposed to be a constant you compensate for once; if the cross-correlation lag is trending up, something upstream (queueing, batching, an added retry layer) is adding delay the control loop was never tuned against.
- **Two independently-stable loops sharing an actuator or measurement surface.** An autoscaler and a load balancer's outlier-ejection logic both write to "how many pods serve traffic." Each can pass isolated load-testing and still destabilize the composite system, because neither loop's model includes the other's action. Before declaring a loop stable, ask what else reads or writes the same actuator and measurement.
- **The absence of a plant model is itself a signal.** If nobody on the team can say "here is the transfer function, or here is the step response we measured," any stability claim is a guess. Silence on this question is the earliest warning of all — it means the loop was tuned by trial and error under one traffic pattern and has no basis for extrapolation to another.

### Measurement-delay traps

Dead time is not just physical (network RTT, pod boot, replication lag). The measurement pipeline adds its own, and it is the one teams forget to model:

- A rolling average over a `W`-second window adds roughly `W/2` seconds of effective dead time on top of the true delay — a 60 s Prometheus rate() window plus a 30 s scrape interval can add 45–60 s of lag the PID was never told about.
- Dashboards built for humans (5-minute buckets, smoothed lines) are the wrong signal to feed a controller — they look clean specifically because they've been low-pass filtered, which is delay in another form.
- Symptom of this trap: a loop tuned against historical/backtested data (already aggregated, already lagged) oscillates in production against the live, less-delayed-but-noisier raw signal, or vice versa — tuned against raw data and unstable once someone "cleans it up" with a wider aggregation window.
- Fix: state the total loop dead time as one number — scrape interval + aggregation window + decision latency + actuation latency + propagation time — and compensate (or gain-reduce) against that total, not the physical component alone.

### Why most software "controllers" fail

It is rarely bad arithmetic. Nearly every production PID-like autoscaler, pacer, or admission controller that misbehaves is missing one or more of three universal preconditions, and most are missing all three at once:

1. **Delay** (dead time) is not modeled — see above.
2. **Noise** is fed to the controller raw — an unfiltered P99 or a jittery per-second rate drives Kd (derivative) into "derivative kick," amplifying sensor noise into actuator chatter.
3. **Actuator saturation** has no anti-windup — the moment the loop hits a hard limit (max replicas, bid cap, rate-limit ceiling), the integral term keeps accumulating against a wall, then overshoots on release.

The fix for each is well-known (Kalman/low-pass filtering, Smith Predictor, anti-windup) and documented in this skill — the expert judgment is diagnosing *which* of the three is actually dominant before reaching for a fix, since applying the wrong one (e.g., adding derivative gain to a problem that is really unmodeled dead time) makes the loop worse.

### When open-loop beats closed-loop

Closed-loop control is not free — it costs a measurement, a delay, and a risk of instability. Prefer open-loop (feedforward-only, or a scheduled/static policy) when:

- The dominant disturbance is fully predictable (diurnal traffic, a scheduled batch job) **and** dead time is a large fraction of the desired response time — feedback correction physically cannot arrive before the disturbance has already passed. See the Predictive Autoscaler recipe below; empirically this beat reactive HPA/KEDA by roughly 6–20x median latency in one measured case (Tymoshenko, Maraschi & Collina 2026, arXiv:2604.19705 — Node.js/Kubernetes-specific, not verified to generalize).
- The measurement itself is slow, expensive, or destabilizing — e.g., a business metric only available T+1 day, or a metric whose own collection changes the system being measured. Closed-loop control against a badly-delayed proxy signal can be strictly worse than a static policy tuned offline from historical data.
- The actuator is high-consequence and effectively irreversible on the timescale of one control cycle (a schema migration, a pricing change, a one-way data deletion). "Act, observe, correct" is not a viable strategy when the correction cannot undo the action — get it right open-loop, using simulation and backtesting, not live feedback.
- As a rule of thumb: if `dead_time / desired_settling_time > ~0.5`, or if the disturbance is highly predictable and the loop's only job is to react to something already known in advance, feedback control is fighting a battle it starts already behind. Feedforward-first, feedback-as-trim is the correct architecture, not "add more gain."

---

## Decision Checklist

- [ ] **Setpoint tracking**: System must reach and hold a target value under disturbances? → PID (#1)
- [ ] **Predictable disturbances**: Known patterns (time of day, schedule, traffic shape) available? → Feedforward (#2)
- [ ] **State visibility**: Can all relevant states be inferred from available sensors? → Observability rank test (#3)
- [ ] **Actuator reachability**: Can all target states be reached by available actuators? → Controllability rank test (#3)
- [ ] **Convergence proof required**: Must prove loop terminates or converges by design? → Lyapunov function (#4)
- [ ] **Constraints exist**: Actuator limits, safety bounds, or resource caps that must never be violated? → MPC (#5) or anti-windup (#8) in PID
- [ ] **Noisy measurements**: Sensor output too noisy for direct use in controller? → Kalman filter (#6)
- [ ] **Transport lag**: Action-to-effect delay > 30% of dominant time constant? → Dead-time compensation (#7)
- [ ] **Bounded actuator**: Control output has hard min/max? → Anti-windup (#8) — include by default
- [ ] **Regime variation**: System dynamics differ significantly across load or operating conditions? → Gain scheduling (#9)
- [ ] **External service dependency**: Calling a downstream service that can fail? → Circuit breaker (#10)
- [ ] **Producer-consumer queue**: Queue can grow unboundedly under sustained load? → Backpressure (#10)
- [ ] **Bursty arrivals or retry risk**: Traffic or retries can spike beyond downstream capacity? → Token bucket (#11)
- [ ] **Unknown plant + MPC desired**: Need MPC-level constraint handling but have no plant model and system identification is impractical? → DeePC (#12) — collect persistently-exciting offline data first
- [ ] **Predictable load pattern + dominant startup lag**: Load is forecastable and startup delay dominates latency? → Feedforward-dominant (predictive autoscaling) before PID
- [ ] **Competing objectives across agents or loops**: Several controllers contend for one actuator, or one objective is served by several actuators? → ARC decomposition with MIN/MAX selectors and split-range, not negotiation (#4, #5)

---

## Composition Recipes

Use these stacks as starting designs. Validate the plant model, sensor quality, actuator bounds, and disturbance profile before production deployment.

### Autoscaler That Does Not Oscillate

**Failure**: HPA oscillates — adds pods, overshoots, removes pods, undershoots.

- PID (#1): CPU utilization error → replica delta
- Anti-windup (#8): freeze integral when at min/max replica count
- Dead-time compensation (#7): Smith Predictor for pod startup lag
- Gain scheduling (#9): separate gains for low/mid/high load regimes

**Data-driven variant (no plant model):** DeePC (#12) or Koopman-MPC (kEDMD) can replace model-based MPC (#5) when system dynamics are unknown but input-output data is available. Both require persistently exciting excitation during offline data collection (Willems' Fundamental Lemma). DeePC preferred for smooth inputs; Koopman preferred for tight tracking or when a stability certificate is required (see [12-deepc-behavioral.md](assets/templates/control-theory/12-deepc-behavioral.md)).

**Worked example — p95 latency autoscaler:** Setpoint = 200 ms. Measured p95 = 320 ms → error = +120 ms. Gains: Kp = 0.05, Ki = 0.01, Kd = 0.0. At t = 0 the integral ∫error ≈ 0, so ΔReplicas = 0.05 × 120 + 0.01 × 0 = +6 replicas. After 30 s with sustained error (∫error ≈ 600 ms·s): ΔReplicas = 0.05 × 80 + 0.01 × 600 = 4 + 6 = +10 replicas. Anti-windup: clamp the integral and freeze accumulation when |ΔReplicas| ≥ 10/step to prevent the integrator from winding up during the pod-startup dead-time window (~45 s). Load doubles (e.g., 2× traffic spike at t = 120 s): error jumps to +160 ms; proportional term fires immediately (+8 replicas) while the integral catches up over the next 2–3 cycles — this is the correct separation of fast proportional response from slow steady-state correction. Bad-tuning symptom: if you observe oscillation with period ≈ 60 s at Ki = 0.01, halve Ki (oscillation period ≈ 2π / √Ki for a simple integrating plant).

### Stable Agent Loop with Budget Control

**Failure**: Agentic loop runs tool calls without bounded cost or convergence guarantee.

- Token bucket (#11): admission control on tool calls per step
- Circuit breaker (#10): isolate failing tools; fail fast instead of waiting
- Lyapunov termination (#4): potential function (uncertainty/cost remaining) must decrease per step
- MPC planning (#5): plan token allocation across remaining steps before executing the current one

### LLM Inference Autoscaler Without Oscillation

**Failure**: Kubernetes HPA oscillates or lags — scales on CPU/memory while the actual bottleneck is KV-cache saturation and queue depth.

- Backpressure (#10): use KV-cache utilization as the backpressure signal (not CPU); scale when cache approaches saturation threshold
- Token bucket (#11): admission control at ingress; shed load before queue depth triggers failure cascade
- MPC (#5): receding-horizon planning across replica variants (prefill vs. decode disaggregated scaling) — preferentially add cheap variants, remove expensive ones
- Dead-time compensation (#7): account for pod startup latency (~30–60 s for GPU pods) when projecting replica count forward

**Reference implementation**: WVA (Malvankar et al. 2026, arXiv:2603.09730). Empirical: 37% throughput gain, 10× failure reduction vs. HPA.
**Key insight**: Control signal must be engine-internal saturation state (KV-cache, queue depth), not OS-level metrics. OS-level metrics introduce unobservable lag that makes the feedback loop underdamped.

### Predictive (Feedforward-Dominant) Autoscaler

**Failure**: Reactive HPA/KEDA lags behind demand — startup latency means pods arrive after the load spike, causing transient latency degradation.

**When to prefer over PID-dominant autoscaling**: Load pattern is predictable (periodic, trending) AND startup lag is the dominant latency contributor. If the load is unpredictable or bursty, fall back to the PID-dominant recipe above.

- Kalman filter (#6): smooth noisy request-rate time series; produce a filtered load estimate
- Feedforward (#2): forecast load trajectory; scale proactively before demand arrives (eliminates startup-lag penalty)
- Dead-time compensation (#7): encode pod startup time L in the forecast horizon (scale N steps ahead where N ≥ L / sample_period)
- Anti-windup (#8): freeze integral when at min/max replica bounds

**Contrast with PID-dominant recipe**: PID-dominant is feedback-corrective (best for unpredictable disturbances); feedforward-dominant is anticipatory (best when load pattern is predictable and startup lag dominates the error budget).

**Empirical reference**: Tymoshenko, Maraschi & Collina (2026, arXiv:2604.19705) achieve 26 ms median latency vs. 154 ms for KEDA and 522 ms for HPA under a steady ramp load on Node.js/Kubernetes. Caveat: Node.js-specific; generalizability to other runtimes unverified.

### Multi-Agent System with Deterministic Constraint Arbitration

**Failure**: Several agents each defend a different objective (cost, latency, safety, quota) and conflicts are resolved by letting the models negotiate — so the resolution is nondeterministic, unauditable, and changes with prompt or temperature.

The advanced-regulatory-control (ARC) decomposition replaces negotiation with structure. Each feedback loop becomes one scoped agent carrying its own control-theoretic context (controlled variable, setpoint, chain priority, selector kind); an orchestrator encodes the priority order and resolves every conflict deterministically, outside the model.

- Scoped loops (#4): one agent per controlled variable; no agent may write another's actuator
- MIN/MAX selectors: arbitrate when several controlled variables compete for one actuator — the most-constrained loop wins by construction
- Split-range logic: arbitrate when one controlled variable is served by several actuators of differing cost, engaging them in a fixed order
- Circuit breaker (#10) and token bucket (#11): unchanged, still applied per tool

**Key insight**: the safety property comes from the arbitration topology, not from the model. Constraint conflicts resolve identically regardless of what any agent outputs, which is what makes the trajectory auditable.

**Reference**: Nogueira & Skogestad (2026, arXiv:2606.30877). Evaluated on a dairy-barn ventilation loop over 4 days with Qwen 2.5 7B Instruct; contribution is the architecture and auditable trajectories, not a benchmark win. Skogestad is the originator of the ARC framing this borrows.

### Budget Pacing Without Windup or Oscillation

**Failure**: Ad spend oscillates — underspends overnight, overspends at peak, jams at bid cap.

- PID (#1): spend rate error → bid multiplier
- Anti-windup (#8): bid multiplier clamped at platform min/max; freeze integral at limits
- Feedforward (#2): time-of-day schedule pre-adjusts bid before measurement confirms error
- Kalman filter (#6): smooth noisy CPM/spend signals before feeding to PID

---

## Workflow

1. Identify the feedback failure mode in your system (oscillation, windup, dead time, unobservable state, no convergence proof, cascading failure, overload).
2. Use the [Decision Checklist](#decision-checklist) to map failure mode → primitive.
3. Open [`references/primitives-overview.md`](references/primitives-overview.md) for definitions, failure modes, and source anchors.
4. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) and [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) to stack primitives.
5. Check the [Anti-Patterns](#anti-patterns) table before finalizing the design — most common mistakes are listed there.
6. Verify numeric thresholds (gains, dead-time estimates, bucket sizes) against the primary sources in [`data/sources.json`](data/sources.json) and the reference files before deploying at scale.

---

## ASCII Flow

```text
Feedback system failure
  -> Classify symptom: oscillation, windup, delay, overload, cascade, unobserved state
  -> Map symptom to control primitive
  -> Model loop, signal, actuator, delay, and constraint
  -> Choose controller or protection pattern
     +-- unstable or unobservable -> add measurement or redesign loop
     +-- stable enough -> tune and simulate
  -> Deploy with monitored thresholds and rollback criteria
```

---

## Navigation

- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Primitives overview and domain anti-patterns: [`references/primitives-overview.md`](references/primitives-overview.md)
- Per-primitive playbooks: [`assets/templates/control-theory/README.md`](assets/templates/control-theory/README.md)
- Sources: [`data/sources.json`](data/sources.json)

## Related Skills

_Consumer skills that apply these primitives to specific domains will link here. This section is reserved for future applied-recipe references._

---

## Fact-Checking

Sources and verification notes for the 12 primitives:

- **PID / Ziegler-Nichols**: Tuning table values are from the original 1942 Ziegler & Nichols paper. They are starting points, not universal optima. Re-tune on your specific plant before production deployment. Åström & Murray, *Feedback Systems*, is the canonical modern reference.
- **Lyapunov stability**: The Lyapunov function must be constructed for each system — no universal recipe exists. The conditions (positive definite V, negative definite dV/dt) are sufficient for asymptotic stability but not always necessary.
- **Kalman filter optimality**: Minimum-variance only for linear systems with Gaussian noise. For nonlinear systems, EKF and UKF are approximations; claim optimality carefully.
- **Smith Predictor**: Effective when dead time is approximately constant and known. Robustness degrades with time-varying or uncertain delays. The "30% rule" for when to apply it is a heuristic, not a hard theorem.
- **MPC computation**: Real-time feasibility depends on horizon length and model complexity. Claims about computation time are hardware- and implementation-specific.
- **Circuit breaker thresholds**: The specific values in worked examples (40% failure rate, 60-second window) are illustrative starting points from Nygard (2018). Tune to your service's actual failure distribution.
- **Token bucket**: Turner (1986) introduced the algorithm in the networking context. Application to LLM API rate limiting is by analogy; verify platform-specific rate limit semantics (per-minute vs. per-second, token counting vs. request counting).
- **CBF / Safe RL boundary**: CBFs provide forward-invariance guarantees for continuous-time systems; discrete-time implementations require care (discrete-time CBF conditions differ from continuous-time). Yang et al. (ICRA 2026) prove continuous-time safety filters can be deployed via closed-form expressions on discrete-time rollouts — verify this holds for your specific discretization step.
- **CBF as a token-level decoding filter**: Miyaoka & Inoue, *Control Barrier Function for Aligning Large Language Models* (arXiv:2511.03121), published in IEEE Transactions on Control Systems Technology (2026) — one of the few peer-reviewed control-theory-on-LLM results rather than a preprint. The CBF acts as an add-on filter on the predicted token during decoding, so alignment is enforced without fine-tuning the base model. Note the boundary: this controls the *decoding* loop of one model, not an agent's tool-use loop; it needs an evaluation model to define the barrier, and its guarantee is only as good as that evaluator.
- **ARC-based multi-agent decomposition**: Nogueira & Skogestad (2026, arXiv:2606.30877) map each loop of an advanced-regulatory-control chain to one scoped LLM operator agent, resolving conflicts via MIN/MAX selectors and split-range logic in an orchestrator rather than via model negotiation. Demonstrated on a dairy-barn ventilation scenario over 4 days with Qwen 2.5 7B Instruct — a case study establishing auditability, not a benchmark result. arXiv preprint (eess.SY); treat the architecture as the transferable claim and the evaluation as illustrative.
- **Context assembly as a controlled variable**: Paul (2026, arXiv:2607.25408) frames harness policy for a frozen LLM — prompt template, few-shot count, retrieved-context volume, number of verification passes — as the controlled variable, with an outer context policy learned online. The stability claim is non-decreasing expected reward under bounded policy change, which is a weaker condition than Lyapunov asymptotic stability; the paper reports no quantitative results and defers empirics to a companion paper. Useful as framing, not as evidence.
- **ISS applied to LLM agent loops**: Prinos et al. (arXiv:2605.03034, 2026) apply Input-to-State Stability formally to an LLM-based agentic system, with a Lyapunov function machine-checked in Lean 4. Key finding: architectural constraints (finite action catalogs at tool interfaces) guarantee stability independently of model capability or temperature. A tool-mediated Claude Sonnet 4 controller reduced attacker payoff by 59% vs. a deterministic greedy baseline; a Claude Haiku 4.5 controller converged to a suboptimal value but stayed catalog-bounded, showing stability held independent of model capability. This confirms the guidance in #4 — stability must be baked into loop architecture, not delegated to the model. Paper-only; domain is autonomous cyber defense, generalizability to other agent loops unverified. **Correction (2026-07-11)**: earlier drafts of this skill misattributed this paper to "Iyer et al." — the actual first author is Prinos; the arXiv ID and findings are unchanged.
- **Online MPC / adaptive control regret**: The IQC framework (Lessard et al. 2016 for static analysis; Jakob & Iannelli, CDC 2025, for OCO regret) unifies classical control robustness and online optimization regret analysis. When an adaptive MPC scheme updates its model online, the IQC SDP approach provides automated regret certificates without bounding the feasible set.
- **DeePC / Willems' Fundamental Lemma**: Willems' Lemma is exact for noiseless LTI systems; noisy or nonlinear plants require regularization (λ_g, λ_y) and the guarantees degrade. The canonical DeePC paper is Coulson, Lygeros & Dörfler (ECC 2019, arXiv:1811.05890) — not 1811.10455 which is an unrelated ML paper. Stability of the regularized/nonlinear variants is an active research area; do not claim deterministic safety certificates for noisy nonlinear deployments without verification.
- **Predictive autoscaling latency numbers (26 ms / 154 ms / 522 ms)**: Confirmed verbatim from Tymoshenko et al. (2026, arXiv:2604.19705) under a steady ramp load on Node.js/Kubernetes. Node.js-specific; generalizability to JVM, Python, or GPU workloads unverified.
- **Stochastic CBF (Echigo et al. 2026, arXiv:2604.08831)**: Provides probabilistic safety guarantees via sub-Gaussian concentration bounds. Framework is paper-only; no production code confirmed. Santoyo et al. 2021 (CDC) is the widely-cited predecessor for stochastic CBF — specific arXiv ID unconfirmed; treat as DEFERRED.
- **Sivaranjani et al. sysid survey (arXiv:2512.06315)**: arXiv preprint only; no confirmed peer-review venue. Use with evidence grade B.
- Verify all numeric thresholds against primary sources before treating as domain-portable benchmarks. Primary sources for each primitive are listed in [`references/primitives-overview.md`](references/primitives-overview.md) and [`data/sources.json`](data/sources.json).

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
