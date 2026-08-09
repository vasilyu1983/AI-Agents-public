# Mechanism: Observability and Controllability

**Sources**: Åström & Murray, *Feedback Systems* Ch. 7 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 7 (2019). Ogata, *Modern Control Engineering* 5th ed., Ch. 9 (2010).

## Definition

Two fundamental structural properties of a dynamical system in state-space form `ẋ = Ax + Bu, y = Cx`:

**Controllability**: Every state `x` can be driven to any desired state by some finite input sequence `u`. The system can be "steered" from the outside.

**Observability**: Every internal state `x` can be inferred from a finite sequence of outputs `y` and inputs `u`. The system can be "seen" from the outside.

### State-Space Rank Tests

```
System: ẋ = Ax + Bu
        y  = Cx

Controllability matrix:
  C_c = [B | AB | A²B | ... | A^(n-1)B]
  Rank(C_c) = n  →  fully controllable

Observability matrix:
  C_o = [C; CA; CA²; ...; CA^(n-1)]ᵀ
  Rank(C_o) = n  →  fully observable

where n = number of state variables (system order)
```

A state is **uncontrollable** if no input can reach it. It is **unobservable** if no sensor can reveal it. Both conditions are design failures, not measurement failures.

## When to Use

- Before deploying a feedback controller: confirm the states you want to control are reachable and the states you want to monitor are visible.
- Distributed system design: check whether aggregate metrics (CPU, latency) encode enough information to infer individual service states.
- Sensor placement: determine the minimum sensor set that makes the system fully observable.
- Actuator placement: determine the minimum actuator set that makes the system fully controllable.
- Agent loop diagnosis: identify which loop variables cannot be driven to target (uncontrollable) or cannot be tracked (unobservable).

## Inputs

| Input | Description |
|-------|-------------|
| State matrix `A` | System dynamics (n×n) |
| Input matrix `B` | How actuators affect state (n×m) |
| Output matrix `C` | Which states are measured (p×n) |

## Outputs

| Output | Description |
|--------|-------------|
| Controllability rank | n = fully controllable; < n = some states unreachable |
| Observability rank | n = fully observable; < n = some states invisible |
| Uncontrollable subspace | States that inputs cannot reach |
| Unobservable subspace | States that outputs cannot reveal |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Controller cannot eliminate error | Target state is uncontrollable | Add actuator; redesign plant topology |
| Observer cannot track state | State is unobservable from available sensors | Add sensor; change output matrix C |
| Eigenvalue placement fails | System is not fully controllable | Use partial pole placement on controllable subspace |
| Kalman filter diverges | Unobservable mode grows unchecked | Verify observability before deploying Kalman filter |
| Slow state detected too late | Sensor rate too low for state dynamics | Increase sampling rate; add direct state measurement |

## Worked Example: Microservices Observability

**System**: Three-tier web app with frontend (F), API (A), database (D). State vector `x = [latency_F, latency_A, latency_D]`.

Sensors: Only frontend and API latency are measured (`y = [latency_F, latency_A]`).

```
C = [1 0 0]   (observes F)
    [0 1 0]   (observes A)

Build observability matrix C_o = [C; CA; CA²]
If rank(C_o) = 3 → database latency is observable from F and A dynamics.
If rank(C_o) < 3 → database state is invisible; add a DB latency sensor.
```

The observability test answers the question: "Can we infer DB health from what we already measure?" before deciding whether to add instrumentation.

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 7. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 7.
- Ogata, *Modern Control Engineering*, 5th ed., Ch. 9 (2010).
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 2.
