---
description: Formal theory map for control-theory foundations. Use to distinguish stability guarantees from operational heuristics.
last_verified: 2026-05-02
status: stable
---

# Control Theory Formal Theory Map

## Purpose

Use this map when a feedback-control recommendation needs a formal stability argument, state-space framing, or a boundary between control theory and distributed-systems patterns.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| State-space systems | x_dot = Ax + Bu, y = Cx + Du | Observability, controllability, Kalman, MPC | Requires a state definition and model structure |
| Classical feedback | Transfer functions, poles/zeros, loop gain, phase margin | PID, feedforward, dead-time compensation | Linearized behavior near an operating point |
| Stability theory | Lyapunov functions, BIBO, ISS, passivity | Convergence, bounded queues, stable loops | A max-step cap is not a stability proof |
| Optimal control | Cost functions, dynamic programming, LQR/LQG | MPC, constrained planning, resource allocation | Objective must encode the actual cost and constraints |
| Robust control | Uncertainty sets, gain/phase margins, H-infinity | Delay tolerance, model error, regime changes | Robust margins trade performance for safety |
| Nonlinear/adaptive control | Saturation, switching, parameter drift | Anti-windup, gain scheduling, nonlinear plants | Switching can create transients without bumpless transfer |
| Stochastic estimation | Linear Gaussian state estimation | Kalman filtering and sensor fusion | Kalman optimality is assumption-bound |
| Networked control | Queues, admission control, backpressure signals | Circuit breakers, rate limiting, overload protection | Fail-fast without throttling can move overload elsewhere |
| Behavioral systems / Willems | Hankel matrices of past trajectories, persistency of excitation, Fundamental Lemma | DeePC (model-free MPC), data-driven control without parametric identification | Willems' Lemma is exact for noiseless LTI; noisy/nonlinear plants require regularization and stability proofs are weaker |

## Applied Primitive Coverage

| Primitive | Formal Backbone | Must Check Before Use |
|---|---|---|
| PID | Closed-loop error dynamics | Actuator bounds, sampling interval, delay |
| Feedback/feedforward | Disturbance rejection and model inversion | Disturbance observability and model accuracy |
| Observability/controllability | Rank tests for state-space systems | State definition, sensor placement, actuator authority |
| Lyapunov stability | Positive definite potential with negative derivative/difference | Candidate function and domain of attraction |
| MPC | Receding-horizon constrained optimization | Model validation, horizon, solver latency |
| Kalman filter | Linear Gaussian minimum-variance estimation | Q/R covariance, model linearity, sensor bias |
| Dead-time compensation | Delay model and phase margin | Delay estimate and delay variability |
| Anti-windup | Saturated actuator with integral state | Clamp logic and integral back-calculation |
| Gain scheduling | Local controllers across operating regimes | Scheduling variable and smooth transfer |
| Circuit breaker/backpressure | Bounded failure propagation and queue control | Downstream recovery behavior and ingress enforcement |
| Token bucket | Arrival curve and service budget | Fill rate, burst capacity, shared quota semantics |
| DeePC / Behavioral systems | Willems' Fundamental Lemma, Hankel matrix of past trajectories, persistency-of-excitation condition | Verify: offline excitation data is persistently exciting; Hankel matrix is full rank; regularization weights tuned for noise level |

## Production Rule

Every production loop needs a named plant, sensor, actuator, setpoint, disturbance, failure mode, saturation behavior, and verification method. Without those, control terminology is decoration, not design.
