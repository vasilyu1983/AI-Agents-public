# Mechanism: Data-Enabled Predictive Control (DeePC) / Behavioral Systems

**Sources**: Coulson, Lygeros & Dörfler, "Data-Enabled Predictive Control: In the Shallows of the DeePC," ECC 2019, arXiv:1811.05890. Willems, Rapisarda, Markovsky & De Moor, "A note on persistency of excitation," *Systems & Control Letters* 54(4):325–329, 2005. DOI: https://doi.org/10.1016/j.sysconle.2004.09.003.

## Definition

**Data-Enabled Predictive Control (DeePC)** replaces the explicit plant model in standard MPC with a Hankel matrix of past input-output trajectories, using Willems' Fundamental Lemma (2005) as the theoretical backbone.

**Willems' Fundamental Lemma**: For a controllable linear time-invariant (LTI) system, any trajectory of the system can be expressed as a linear combination of a single persistently-exciting experiment's columns. This means one sufficiently rich dataset encodes all reachable trajectories — no parametric identification step needed.

```
DeePC replaces the model-prediction step in MPC:

Standard MPC step:
  x(k+i) = A·x(k+i−1) + B·u(k+i−1)   ← explicit model required

DeePC step:
  [u_future; y_future] = H · g           ← Hankel matrix H of past data; g is the combination vector
  subject to: [u_past; y_past] = H_past · g  (consistency with observed trajectory)

At time k:
  Minimize   ‖y_future − r‖²_Q + ‖u_future‖²_R + λ_g · ‖g‖²₂ + λ_y · ‖σ_y‖²
  Subject to: trajectory consistency, actuator bounds, state constraints
  Apply first element of u_future. Slide window forward.
```

The λ_g regularization on g handles noisy data (pure LTI Lemma assumes noise-free). The λ_y slack variable σ_y on past output consistency handles measurement noise.

## When to Use

- **Plant model is unknown or too expensive to identify** — system identification from first principles is impractical.
- **Fast nonlinear dynamics** — standard Koopman/kEDMD linearization error is large; regularized DeePC may generalize better than a lifted-linear model.
- **Smooth input trajectory required** — DeePC produces substantially smoother input trajectories than Koopman MPC for the same tracking task (Daráš et al. 2026, arXiv:2604.00524).
- **Short data-collection window is feasible** — a single persistently-exciting offline experiment suffices; no ongoing system ID required.
- **MPC is preferred but no model exists** — DeePC is the drop-in model-free variant of MPC.

**Prefer Koopman MPC over DeePC when:**
- Tight tracking accuracy is the primary objective (Koopman MPC tracks more tightly).
- Stability certificate is required (Koopman stability via proportional error bound is proven; DeePC stability proofs exist for the linear noiseless case).
- Online update of the surrogate model is needed.

## Inputs

| Input | Description |
|-------|-------------|
| Offline trajectory data | Input-output experiment: `(u_d, y_d)` with length ≥ `(m+p+1)(T_ini+N) − 1` where m=inputs, p=outputs, T_ini=init window, N=horizon |
| Persistency-of-excitation condition | Input signal must be persistently exciting of order `T_ini + N`; use PRBS or band-limited noise |
| Regularization weights | λ_g (Hankel combination penalty), λ_y (output slack penalty); tune for noise level |
| Cost matrices Q, R | State tracking vs. input effort — same as standard MPC |
| Constraints | Actuator bounds u_min/max, state bounds x_min/max |

## Outputs

| Output | Description |
|--------|-------------|
| Optimal input `u*(k)` | Control action to apply — first element of u_future |
| Predicted output trajectory | y_future over horizon N — not applied; useful for monitoring |
| Constraint satisfaction | Same hard-constraint guarantees as MPC (for noiseless LTI case) |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Poor performance on noisy data | Willems' Lemma assumes exact LTI; noise violates this | Increase λ_g and λ_y regularization; collect longer dataset |
| Persistency-of-excitation not satisfied | Offline experiment too narrow in frequency content | Use PRBS or chirp; verify rank of Hankel matrix before deployment |
| Hankel matrix too large for real-time solve | Long horizon or large dataset | Use SVD to reduce Hankel rank (Scalable Nonlinear DeePC, de Jong et al. 2025, arXiv:2512.14535) |
| Nonlinear system: performance degrades | Willems' Lemma is exact only for LTI; nonlinear systems need extensions | Use kernel-based or regularized nonlinear DeePC (arXiv:2512.14535); or switch to Koopman MPC |
| No stability certificate | DeePC stability for nonlinear/noisy case is active research area | Use Koopman MPC if a formal stability certificate is required |

## Composition Recipe: Autoscaler with Unknown Plant Dynamics

**Problem**: Need MPC-level autoscaling but cannot build or validate an explicit plant model (startup time, saturation, interference from other workloads makes identification impractical).

**Stack**:
1. DeePC (this primitive) — replaces model-based MPC (#5); uses Hankel matrix of historical CPU/latency/replica data
2. Anti-windup (#8) — freeze integral in the receding-horizon objective when at min/max replica count
3. Dead-time compensation (#7) — encode pod startup lag in the T_ini window length
4. Kalman filter (#6) — pre-filter noisy KV-cache / queue-depth measurements before passing to DeePC as y_past

**Data-collection step**: Run a PRBS (pseudo-random binary sequence) on replica count for 30–60 minutes during off-peak to collect persistently exciting data. Record: replicas, CPU, p95 latency, queue depth. Verify Hankel rank.

**DeePC vs. Model-Based MPC decision**:
- Unknown plant → DeePC
- Known plant, tight tracking → Model-based MPC (#5)
- Known plant, nonlinear → Koopman MPC (#5 + Schimperna et al. 2025)
- Smooth inputs, unknown plant → DeePC
- Tight tracking, unknown plant, stability proof needed → collect more data + Koopman

## Sources

- Coulson, Lygeros & Dörfler (2019). "Data-Enabled Predictive Control: In the Shallows of the DeePC." ECC 2019. arXiv:1811.05890.
- Willems, Rapisarda, Markovsky & De Moor (2005). "A note on persistency of excitation." *Systems & Control Letters* 54(4):325–329. DOI: 10.1016/j.sysconle.2004.09.003.
- de Jong, Lazar, Weiland & Dörfler (2025). "Scalable Nonlinear DeePC: Bridging Direct and Indirect Methods and Basis Reduction." arXiv:2512.14535.
- Daráš et al. (2026). DeePC vs. Koopman MPC comparison. arXiv:2604.00524.
- Schimperna et al. (2025). Stability of data-driven Koopman MPC with terminal conditions. arXiv:2511.21248.
