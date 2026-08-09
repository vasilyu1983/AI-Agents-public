---
description: Applied patterns, scenarios, anti-patterns, and known traps for control-theory foundations.
last_verified: 2026-05-02
status: stable
---

# Control Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Stable setpoint loop | Metric must reach and hold a target | PID -> anti-windup -> delay check |
| Predictive resource planning | Future constraints matter | Kalman/state estimate -> MPC -> constraint monitor |
| Overload containment | A downstream system can fail or slow | Circuit breaker -> backpressure -> token bucket |
| Delayed actuator response | Action effect arrives late | Step test -> dead-time compensation -> lower bandwidth |
| Multi-regime control | Dynamics change by load, season, or mode | Gain scheduling -> bumpless transfer -> per-regime tests |
| Agent loop governance | Tool loop must converge under budget | Lyapunov progress metric -> token bucket -> circuit breaker |

## Scenarios

| Scenario | First Question | Correct Primitive |
|---|---|---|
| Autoscaler oscillates | Is the loop underdamped or delayed? | PID plus dead-time compensation |
| Spend controller hits bid cap then overshoots | Did the integral accumulate while saturated? | Anti-windup |
| Queue keeps growing after overload signal | Is producer honoring backpressure? | Backpressure and admission control |
| Monitoring looks healthy but users fail | Is the failing state observable? | Observability analysis |
| Agent retries the same failing tool | Is failure isolated and rate-limited? | Circuit breaker and token bucket |
| Planner violates future budget | Does controller optimize across horizon? | MPC |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Safer Move |
|---|---|---|
| "Just increase Kp" | Higher gain can reduce margin and amplify oscillation | Check delay, damping, and phase margin |
| PID without saturation handling | Integral windup creates overshoot after clamp release | Add anti-windup by default |
| Circuit breaker without rate limits | Recovery can trigger synchronized retries | Add token bucket and jitter |
| Max iterations as convergence proof | It bounds cost, not stability | Define a Lyapunov-like progress metric |
| Kalman filter as generic smoother | It assumes a state model and noise covariance | Validate Q/R and sensor bias |
| MPC without solver budget | Optimization latency becomes part of the plant | Bound solve time and add fallback control |

## Known Traps

- Dead time changes phase; it is not equivalent to lower gain.
- A good local linear controller can fail badly outside the operating point.
- Gain scheduling needs smooth transfer of controller state.
- Backpressure is only real if enforced at ingress.
- Half-open circuit breaker probes must be small and staggered.
- Token bucket semantics differ across APIs: request rate, token rate, concurrency, and daily quota are separate controls.

## Exit Checklist

- [ ] Plant, sensor, actuator, setpoint, and disturbance are named.
- [ ] Saturation behavior and anti-windup path are defined.
- [ ] Delay is measured or bounded.
- [ ] Stability/progress argument is explicit.
- [ ] Fallback behavior is defined when the model or solver fails.
- [ ] Load, failure, and recovery scenarios are tested separately.
