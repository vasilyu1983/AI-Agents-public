# Mechanism: Lyapunov Stability

**Sources**: Åström & Murray, *Feedback Systems* Ch. 4 (2020). Ogata, *Modern Control Engineering* 5th ed., Ch. 9 (2010). Lyapunov, A.M. (1892), "The General Problem of the Stability of Motion" (translated 1992, Taylor & Francis).

## Definition

**Lyapunov stability** is a method for proving whether a dynamical system converges to (or stays near) an equilibrium point — without solving the differential equations explicitly.

**Core idea**: Construct a scalar **Lyapunov function** `V(x)` that behaves like a generalized energy function:
1. `V(x) > 0` for all `x ≠ 0` (positive definite)
2. `V(0) = 0` (zero at equilibrium)
3. `dV/dt ≤ 0` along all trajectories (non-increasing — system is losing "energy")

If such a `V` exists, the equilibrium is **stable**. If `dV/dt < 0` (strictly decreasing), it is **asymptotically stable** — the system converges to equilibrium.

```
Stability conditions:
  V(x) > 0,    V(0) = 0,    dV/dt ≤ 0  → Stable (Lyapunov stable)
  V(x) > 0,    V(0) = 0,    dV/dt < 0  → Asymptotically stable
  V(x) > 0,    V(0) = 0,    dV/dt < 0, V(x)→∞ as ‖x‖→∞ → Globally asymptotically stable
```

For linear systems `ẋ = Ax`, the quadratic form `V(x) = xᵀPx` is a standard Lyapunov function. The system is asymptotically stable iff all eigenvalues of `A` have negative real parts (equivalently, `AᵀP + PA = −Q` has a positive definite solution `P` for any positive definite `Q`).

## When to Use

- **Proving convergence** of a control loop before deployment (no need to run to find out).
- **Agent loop termination**: verify that a reasoning loop's "potential function" (cost, uncertainty, or objective distance) decreases on each step.
- **Retry/backoff design**: show that the retry count or request queue drains.
- **Nonlinear system design**: linear stability (eigenvalues) is insufficient; Lyapunov handles nonlinear dynamics.
- **Safety verification**: certify that a system stays in a safe region under all disturbances.

## Inputs

| Input | Description |
|-------|-------------|
| System dynamics | `ẋ = f(x)` or `ẋ = Ax + Bu` |
| Candidate Lyapunov function | `V(x)` — must be constructed; no universal recipe |
| Equilibrium point | `x*` (often 0 after coordinate shift) |

## Outputs

| Output | Description |
|--------|-------------|
| Stability certificate | Proof that the system is stable or asymptotically stable |
| Region of attraction | Set of initial conditions from which convergence is guaranteed |
| Instability certificate | If no valid V exists (or dV/dt can be positive), the system may be unstable |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Cannot find valid V | Nonlinear system with complex dynamics | Try sum-of-squares (SOS) methods; use simulation to estimate stability region |
| V found but dV/dt ≤ 0 not strictly | Lyapunov stable but not asymptotic | Check LaSalle's invariance principle for asymptotic conclusion |
| Stable in theory, unstable in practice | Discretization of continuous system | Re-derive Lyapunov conditions in discrete time |
| Region of attraction too small | Conservative V choice | Refine V; use Zubov's method for largest domain |
| Linear Lyapunov used on nonlinear system | Quadratic V valid only locally | Confirm V conditions hold globally, or restrict claims to local neighborhood |
| Deterministic CBF applied to noisy measurements | Classical CBFs guarantee forward-invariance only for noise-free dynamics; sensor noise violates the invariance condition | Use stochastic/probabilistic CBF (P(safety violation) ≤ δ via martingale or sub-Gaussian bounds) or add an explicit safety margin to the CBF constraint. See Echigo et al. 2026, arXiv:2604.08831. |

## Worked Example: Agent Loop Termination

**Problem**: An agent loop iteratively refines an answer. Does it terminate?

Define the potential function `V(k) = remaining_uncertainty(k)` (e.g., entropy of the answer distribution at step k).

Check the Lyapunov conditions:
1. `V(k) ≥ 0` — uncertainty is non-negative. ✓
2. `V(k) = 0` iff the answer is fully determined. ✓
3. `ΔV = V(k+1) − V(k) < 0` — each refinement step must reduce uncertainty.

If condition 3 holds (each step strictly reduces uncertainty by at least `ε`), the loop terminates in at most `V(0)/ε` steps. If condition 3 cannot be guaranteed (e.g., the agent can get stuck in a contradiction), add a fallback: hard step limit or circuit breaker ([10-circuit-breaker-backpressure.md](10-circuit-breaker-backpressure.md)).

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 4. [https://fbsbook.org](https://fbsbook.org)
- Ogata, *Modern Control Engineering*, 5th ed., Ch. 9 (2010).
- Lyapunov (1892/1992), "The General Problem of the Stability of Motion," Taylor & Francis.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 2.
