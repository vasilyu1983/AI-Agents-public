# Mechanism: Model Predictive Control (MPC)

**Sources**: Åström & Murray, *Feedback Systems* Ch. 8 (2020). Camacho & Bordons, *Model Predictive Control* 2nd ed. (2007). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 9 (2019).

## Definition

**Model Predictive Control (MPC)** solves a constrained optimization problem at each time step, using a model of the system to predict future behavior over a finite **prediction horizon** `N`, then applies only the first element of the optimal input sequence.

```
At time k, solve:
  minimize   Σ_{i=1}^{N} [‖x(k+i) − r‖²_Q + ‖u(k+i−1)‖²_R]
  subject to:
    x(k+i) = A·x(k+i−1) + B·u(k+i−1)   (model prediction)
    u_min ≤ u(k+i−1) ≤ u_max             (actuator limits)
    x_min ≤ x(k+i) ≤ x_max               (state constraints)

Apply u*(k) — the first element of the optimal sequence.
At k+1: shift horizon, re-measure, re-solve. (Receding horizon)
```

The "receding horizon" principle: the horizon slides forward with each step, so MPC continuously corrects for model–reality mismatch.

## When to Use

- System has **known constraints** (min/max actuator limits, safety envelopes).
- System has **multi-variable couplings** (changing one variable affects others).
- System has **predictable disturbances** worth planning around.
- Planning a **sequence of actions** with future consequences (resource scheduling, budget pacing, agent step planning).
- PID is insufficient because it cannot handle explicit constraints natively.

Practical examples:
- **Cloud resource scheduling**: predict workload trajectory; allocate capacity respecting budget and instance limits.
- **Budget pacing over a campaign**: optimize daily bids over a 7-day horizon with spend caps.
- **Agent step planning**: given a token budget and task model, plan a sequence of tool calls that finishes within budget.
- **Autoscaling with warm-up lag**: model the startup time of new replicas; plan scale-up before demand peaks.

## Inputs

| Input | Description |
|-------|-------------|
| System model | `(A, B)` state-space matrices (or learned model) |
| Prediction horizon `N` | Number of future steps to optimize over |
| Cost matrices `Q, R` | State tracking vs. input effort tradeoff |
| Constraints | `u_min/max`, `x_min/max` |
| Current state `x(k)` | Measured or estimated (Kalman filter if noisy) |

## Outputs

| Output | Description |
|--------|-------------|
| Optimal input `u*(k)` | Control action to apply at this step |
| Predicted trajectory | `x(k+1), ..., x(k+N)` — not applied, but useful for monitoring |
| Constraint satisfaction | Explicit guarantee that actuator and state limits are respected |

## When the Plant Model is Unknown

Standard MPC assumes the `(A, B)` model is given. When it is not, three paths exist:

| Approach | When to Use | Key Constraint |
|----------|-------------|----------------|
| **DeePC** (model-free) | No model; smooth inputs preferred; offline excitation feasible | Willems' Lemma requires persistently exciting data collection; stability proofs limited to noiseless LTI case |
| **Koopman MPC** (lifted-linear) | Nonlinear plant; stability certificate required; tight tracking | Proportional approximation error bound must hold on target system (Schimperna et al. 2025, arXiv:2511.21248) |
| **Physics-informed sysid** (partial knowledge) | Domain structure known (conservation laws, dissipativity); full data collection not feasible | Enforce stability/dissipativity constraints during ML training — models trained without these can destabilize control loops (Sivaranjani et al. 2025, arXiv:2512.06315) |

**Critical rule**: ML models trained for prediction accuracy alone can be accurate on average but destabilizing under feedback. Always enforce control-relevant properties (dissipativity, stability, energy conservation) during the sysid/training step — not just at deployment.

See [`12-deepc-behavioral.md`](12-deepc-behavioral.md) for the DeePC playbook and decision tree between these three approaches.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Poor performance when model is stale | Plant changed; model not updated | Retrain model online; add Kalman filter for state estimation |
| Optimization infeasible | Constraints too tight | Use soft constraints (penalty instead of hard limit) |
| Computation too slow | N too large or model too complex | Reduce horizon; use linear MPC; precompute offline for simple cases |
| Myopic planning | Horizon too short | Extend N to cover the relevant dynamics (at least 3–5 time constants) |
| Ignores disturbances | Open-loop prediction only | Add disturbance model; combine with feedforward ([02-feedback-vs-feedforward.md](02-feedback-vs-feedforward.md)) |

## Worked Example: Agent Token Budget Planning

**Problem**: An agent has a 10,000-token budget and a 5-step task. Each step has estimated cost `c_i` and produces estimated value `v_i`. Constraints: no step can exceed 3,000 tokens; total ≤ 10,000.

```
MPC formulation:
  Predict costs: [c_1, c_2, c_3, c_4, c_5] = [1200, 2000, 800, 3000, 1500]
  Remaining budget state: x(k) = budget_remaining
  Control: u(k) = tokens allocated to step k

  Minimize: −Σ v_i·u_i / c_i   (maximize value per token)
  Subject to:
    u_i ≤ 3000          (per-step cap)
    Σ u_i ≤ 10000       (total budget)
    u_i ≥ c_i · 0.5    (minimum viable per step)

At step 1: solve → apply u_1*. At step 2: update budget, re-solve.
```

If step 1 costs more than predicted, the re-solve at step 2 automatically adjusts remaining allocations.

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 8. [https://fbsbook.org](https://fbsbook.org)
- Camacho & Bordons, *Model Predictive Control*, 2nd ed. (2007), Springer.
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 9.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 9.
