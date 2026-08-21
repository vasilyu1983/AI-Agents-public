---
description: Domain-agnostic overview of 12 control-theory primitives. Mathematical definitions, failure modes, and decision checklist.
last_verified: 2026-08-14
status: stable
---

# Control Theory Primitives Overview

## Table of Contents

- [Why Control Theory Matters](#why-control-theory-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Control Theory Matters

Control theory provides the mathematical tools for designing systems that reliably reach and hold a target state — despite disturbances, delays, noise, and nonlinearities. Without it:

| Failure Mode | Control Theory Diagnosis | What Goes Wrong |
|-------------|------------------------|-----------------|
| Autoscaler oscillates at target CPU | P-only control with no damping | Underdamped second-order response; never settles |
| Budget pacing jams at max bid and overshoots | Integrator windup during actuator saturation | Large I-term unwinds after clamp releases → overshoot |
| Retry storm amplifies a partial failure | No isolation between caller and failed service | Cascading failure; callers overwhelm recovering service |
| Scaling response is sluggish despite high gains | Dead time (pod startup) treated as plant gain | Loop oscillates or destabilizes around the delay |
| Agent loop runs without termination guarantee | No Lyapunov potential function defined | Loop may cycle indefinitely; no convergence certificate |
| Controller tuned for normal load fails at peak | Single operating point for a nonlinear system | Inadequate response outside the tuned regime |

Each primitive below addresses a specific class of feedback failure.

---

## Primitive Index

12 primitives. This overview is the operational reference; use [`formal-theory-map.md`](formal-theory-map.md) for state-space and stability assumptions, [`patterns-scenarios-traps.md`](patterns-scenarios-traps.md) for production failure modes, and [`../assets/templates/control-theory/README.md`](../assets/templates/control-theory/README.md) for standalone primitive playbooks.

| # | Primitive | Failure Mode Addressed | Primary Domains |
|---|-----------|----------------------|-----------------|
| 1 | PID Control | Uncontrolled deviation from setpoint; steady-state error | Autoscaling, budget pacing, rate control |
| 2 | Feedback vs. Feedforward | Reactive-only control ignores predictable disturbances | Budget pacing, thermal control, agent planning |
| 3 | Observability & Controllability | Blind spots in state monitoring; unreachable target states | Distributed systems, sensor design, agent loops |
| 4 | Lyapunov Stability | No proof of convergence; diverging loop | Agent termination, nonlinear system design |
| 5 | MPC | Constraint violations; myopic single-step control | Resource scheduling, budget pacing, agent planning |
| 6 | Kalman Filter | Noisy state estimates degrade controller performance | Monitoring, anomaly detection, state estimation |
| 7 | Dead-Time Compensation | Transport lag causes oscillation or instability | Autoscaling, replication lag, CDN invalidation |
| 8 | Anti-Windup | Integrator saturation causes post-saturation overshoot | Any PID with actuator limits |
| 9 | Gain Scheduling | Fixed gains fail outside the design operating point | Load-varying systems, multi-regime controllers |
| 10 | Circuit Breaker & Backpressure | Cascading failure; unbounded queue growth | Microservices, agent tool calls, stream pipelines |
| 11 | Rate Limiting / Token Bucket | Overload from bursts; retry storms after failure | API rate limiting, LLM call budgets, admission control |
| 12 | DeePC / Behavioral Systems | MPC-level optimization when no plant model is available; unknown dynamics | Autoscaling, process control, any system where sysid is impractical |

---

## Anti-Patterns by Domain

### Autoscaling

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Replica count oscillates at target | P-only or underdamped PID | Add derivative term; tune with Ziegler-Nichols |
| Scaler adds max replicas, then removes all | Integrator windup at ceiling | Anti-windup (#8) |
| Scaler reacts 90 seconds after load spike | Pod startup dead time uncompensated | Smith Predictor (#7) |
| Single gain set fails under both light and heavy load | Operating point mismatch | Gain scheduling (#9) |

### Budget Pacing and Bidding

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Bid jams at platform cap, then crashes | No anti-windup on integral | Anti-windup (#8) |
| Spend slow to respond to intraday traffic changes | Reactive feedback only | Add feedforward schedule (#2) |
| Noisy CPM/CTR causes erratic bid swings | Raw measurement fed to controller | Kalman filter (#6) before PID input |
| Campaign ends with budget remaining | Controller has no lookahead | MPC with daily horizon (#5) |

### Distributed Systems and Microservices

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Partial failure becomes full outage | No cascading-failure isolation | Circuit breaker (#10) |
| Queue grows without bound under sustained load | No backpressure signal | Backpressure (#10) |
| 429 errors from retry storm after recovery | Uncapped retries at recovery time | Token bucket rate limiter (#11) with jitter |
| DB state invisible from aggregate API metrics | Unobservable state | Observability analysis (#3) + add direct sensor |

### Agent Loops

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Loop runs indefinitely without progress | No convergence guarantee | Lyapunov potential function (#4) + hard step limit |
| Tool calls burst to API limit | No admission control | Token bucket (#11) on tool calls |
| External tool failure stalls entire loop | No isolation | Circuit breaker (#10) around each tool |
| Token budget exhausted on early steps | No multi-step planning | MPC step planner (#5) |
| Agents with competing objectives argue instead of arbitrating | Conflict resolution delegated to the model; nondeterministic and unauditable | Structural priority outside the model: MIN/MAX selectors, split-range, fixed chain order (#4, #5) |
| Loop "stabilized" by lowering temperature | Temperature is not a control parameter; stability came from architecture, not sampling | Constrain the action space at the tool interface — finite action catalogs bound the loop independently of model settings (#4) |

---

## Decision Checklist

- [ ] **Setpoint tracking needed**: System must reach and hold a target value? → PID (#1)
- [ ] **Known predictable disturbances**: Can anticipate load pattern or schedule? → Feedforward (#2)
- [ ] **State visibility unclear**: Are all relevant states measurable? → Observability analysis (#3)
- [ ] **Convergence must be proven**: Loop must terminate or converge by design? → Lyapunov (#4)
- [ ] **Constraints exist**: Actuator limits, safety envelopes, or resource caps? → MPC (#5)
- [ ] **Noisy measurements**: Sensor output is too noisy for direct use? → Kalman filter (#6)
- [ ] **Delay between action and effect**: Transport lag > 30% of time constant? → Dead-time compensation (#7)
- [ ] **Actuator has hard limits**: Min/max bounds on the control output? → Anti-windup (#8) in every PID
- [ ] **Operating conditions vary widely**: System dynamics differ significantly across regimes? → Gain scheduling (#9)
- [ ] **Downstream failure risk**: Calling external services or dependencies? → Circuit breaker (#10)
- [ ] **Producer-consumer queue**: Queue can grow unboundedly under load? → Backpressure (#10)
- [ ] **Burst traffic or retry risk**: Bursty arrivals or retries can overload downstream? → Token bucket (#11)

---

## Sources

Primary references for the 12 primitives. Numeric claims should be verified against primary sources before treating as universal.

- Åström & Murray, *Feedback Systems* (2020). [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, 8th ed. (2019).
- Ogata, *Modern Control Engineering*, 5th ed. (2010).
- Hellerstein, Diao, Parekh & Tilbury, *Feedback Control of Computing Systems* (2004). Wiley.
- Nygard, *Release It! Design and Deploy Production-Ready Software*, 2nd ed. (2018).
- Camacho & Bordons, *Model Predictive Control*, 2nd ed. (2007).
- Kalman (1960), ASME J. Basic Engineering 82:35-45.
- Ziegler & Nichols (1942), ASME Trans. 64:759-768.
- Rugh & Shamma (2000), Automatica 36(10):1401-1425.
- Varghese (2004), *Network Algorithmics*. Morgan Kaufmann.
- Coulson, Lygeros & Dörfler (2019), ECC 2019, arXiv:1811.05890 — DeePC (#12).
- Willems, Rapisarda, Markovsky & De Moor (2005), Systems & Control Letters 54(4):325-329 — Fundamental Lemma, backbone of #12.

Full records, including 2024–2026 applied work, are in [`../data/sources.json`](../data/sources.json).
