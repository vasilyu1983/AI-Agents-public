# Mechanism: PID Control

**Sources**: Åström & Murray, *Feedback Systems* Ch. 10-11 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* (8th ed., 2019). Ziegler & Nichols, "Optimum Settings for Automatic Controllers" (1942).

## Definition

A **Proportional-Integral-Derivative (PID) controller** computes a corrective output `u(t)` from the current error `e(t) = setpoint − measurement`:

```
u(t) = Kp·e(t)  +  Ki·∫e(τ)dτ  +  Kd·de/dt

where:
  Kp = proportional gain (react to present error)
  Ki = integral gain    (eliminate steady-state error)
  Kd = derivative gain  (damp oscillation, react to rate of change)
```

The three terms are independent levers. Real implementations are discrete:

```
u[k] = Kp·e[k] + Ki·T·Σe[j] + (Kd/T)·(e[k] − e[k-1])
T = sample period
```

## When to Use

- **Any closed-loop system** where you measure output, have a setpoint, and can apply a corrective input.
- Autoscaling: CPU/memory utilization vs. target.
- Budget pacing: daily spend rate vs. target rate.
- Retry/backoff: request success rate vs. target SLA.
- Agent loop throttling: token consumption rate vs. budget.
- Temperature or rate control in any physical process.

## Inputs

| Input | Symbol | Description |
|-------|--------|-------------|
| Setpoint | `r(t)` | Desired output value |
| Measurement | `y(t)` | Observed output (sensed) |
| Error | `e(t) = r − y` | Deviation to correct |
| Gains | `Kp, Ki, Kd` | Tuned parameters |

## Outputs

| Output | Description |
|--------|-------------|
| Control signal | `u(t)` — actuator command (e.g., add replicas, adjust bid, release tokens) |
| Steady-state error | Should converge to 0 with Ki > 0 |

## Tuning: Ziegler-Nichols Method

1. Set `Ki = Kd = 0`. Increase `Kp` until output oscillates at constant amplitude → record **ultimate gain** `Ku` and **ultimate period** `Tu`.
2. Apply the ZN table:

| Controller | Kp | Ki | Kd |
|------------|----|----|-----|
| P only | 0.5 Ku | — | — |
| PI | 0.45 Ku | 0.54 Ku/Tu | — |
| PID | 0.6 Ku | 1.2 Ku/Tu | 0.075 Ku·Tu |

3. ZN is a starting point. Fine-tune: if overshoot is too large, reduce Kp; if response is too slow, increase Ki.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Sustained oscillation | Kp too high (undamped) | Reduce Kp; add derivative term |
| Slow convergence | Kp too low | Increase Kp; increase Ki |
| Integrator windup | I-term accumulates during saturation | Add anti-windup ([08-anti-windup.md](08-anti-windup.md)) |
| Derivative kick | Noisy measurement magnifies Kd | Filter measurement; apply Kd to output not error |
| Steady-state offset | Ki = 0 | Add integral term |
| Wrong response to dead time | Transport lag misread as gain | Add Smith Predictor ([07-dead-time-compensation.md](07-dead-time-compensation.md)) |

## Worked Example: Autoscaler

**Problem**: Target 60% CPU utilization across a pod pool. Actual = 82%.

```
e = 60 − 82 = −22%  (need to scale up)
Kp = 0.05, Ki = 0.01, Kd = 0.005 (pre-tuned)

u = 0.05·(−22) + 0.01·Σe·T + 0.005·Δe/T
  ≈ −1.1 + (small I term) + (small D term)
  → add ~1 pod (rounded from −1.1 signal)
```

Next cycle: CPU = 68%, error = −8%, integral shrinks, derivative damps further response.

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 10-11. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 4.
- Ziegler & Nichols (1942), ASME Trans. 64:759-768.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 2.
