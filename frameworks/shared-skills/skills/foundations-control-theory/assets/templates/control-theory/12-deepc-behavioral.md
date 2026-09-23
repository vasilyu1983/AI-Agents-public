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
- **MPC is preferred but no model exists** — consider DeePC after validating data richness, lag and operating-domain assumptions; it is not a guaranteed drop-in for arbitrary plants.

**Compare Koopman MPC and DeePC locally:** reported tracking/input-smoothness differences are task-specific. A certificate requires the selected formulation's terminal conditions, recursive feasibility, model-error bounds and operating-domain assumptions; the method name alone supplies none. Noisy/nonlinear DeePC regularization does not restore the exact LTI theorem.

## Inputs

| Input | Description |
|-------|-------------|
| Offline trajectory data | Input-output experiment: `(u_d, y_d)` with length T ≥ `(m+1)(T_ini+N+n) − 1` as a necessary richness bound, with n=state order (or justified conservative upper bound), m=inputs, T_ini=initial window, N=horizon; length alone is insufficient |
| Persistency-of-excitation condition | Input signal must be persistently exciting of order `T_ini + N + n`: verify input Hankel full row rank at this order; a named PRBS/noise signal alone proves no rank condition. Require T_ini at least the system lag for unique output prediction |
| Regularization weights | λ_g (Hankel combination penalty), λ_y (output slack penalty); tune for noise level |
| Cost matrices Q, R | State tracking vs. input effort — same as standard MPC |
| Constraints | Actuator bounds u_min/max, state bounds x_min/max |

## Outputs

| Output | Description |
|--------|-------------|
| Optimal input `u*(k)` | Control action to apply — first element of u_future |
| Predicted output trajectory | y_future over horizon N — not applied; useful for monitoring |
| Constraint satisfaction | Predicted input/output feasibility under the exact controllable noiseless LTI theorem and data/lag conditions; recursive feasibility, stability and real-plant safety require their own assumptions. Unmeasured state bounds need a justified state representation |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Poor performance on noisy data | Willems' Lemma assumes exact LTI; noise violates this | Increase λ_g and λ_y regularization; collect longer dataset |
| Persistency-of-excitation not satisfied | Offline experiment too narrow in frequency content | Use PRBS or chirp; verify rank of Hankel matrix before deployment |
| Hankel matrix too large for real-time solve | Long horizon or large dataset | Use SVD to reduce Hankel rank (Scalable Nonlinear DeePC, de Jong et al. 2025, arXiv:2512.14535) |
| Nonlinear system: performance degrades | Willems' Lemma is exact only for LTI; nonlinear systems need extensions | Use kernel-based or regularized nonlinear DeePC (arXiv:2512.14535); or switch to Koopman MPC |
| No stability certificate | DeePC stability for nonlinear/noisy case is active research area | Specify and verify terminal/robustness and recursive-feasibility assumptions for the selected formulation; otherwise report no certificate |

## Composition Recipe: Autoscaler with Unknown Plant Dynamics

**Problem**: Need MPC-level autoscaling but cannot build or validate an explicit plant model (startup time, saturation, interference from other workloads makes identification impractical).

**Stack**:
1. DeePC (this primitive) — replaces model-based MPC (#5); uses Hankel matrix of historical CPU/latency/replica data
2. Constraint handling — enforce replica/rate limits in the optimizer; anti-windup applies only if an explicit integral augmentation or separate PI/PID loop is defined, and must allow unwinding
3. Dead-time handling (#7) — include startup dynamics in collected trajectories, initial-history lag and horizon; selecting T_ini alone does not compensate transport delay
4. Kalman filter (#6) — pre-filter noisy KV-cache / queue-depth measurements before passing to DeePC as y_past

**Data-collection step**: Plan a bounded, authorized excitation experiment with safe fallback; choose sample rate, length and input amplitude from lag/order and rank requirements, not a universal duration. Record replicas, CPU, latency and queue depth, then verify rank, held-out prediction and constraint margins. For n=10,m=1,T_ini+N=10, excitation order is20 and necessary length is39, not order10/length29. Source: [Coulson et al. §V-A/Theorem V.1](https://arxiv.org/html/1811.05890v2), checked2026-09-17.

**DeePC vs. Model-Based MPC decision**:
- Unknown plant → DeePC
- Known plant, tight tracking → Model-based MPC (#5)
- Known plant, nonlinear → Koopman MPC (#5 + Schimperna et al. 2025)
- Smooth inputs, unknown plant → DeePC
- Unknown plant, certificate needed → establish model-error/terminal/robustness assumptions and verify the chosen controller; more data alone supplies no certificate

## Sources

- Coulson, Lygeros & Dörfler (2019). "Data-Enabled Predictive Control: In the Shallows of the DeePC." ECC 2019. arXiv:1811.05890.
- Willems, Rapisarda, Markovsky & De Moor (2005). "A note on persistency of excitation." *Systems & Control Letters* 54(4):325–329. DOI: 10.1016/j.sysconle.2004.09.003.
- de Jong, Lazar, Weiland & Dörfler (2025). "Scalable Nonlinear DeePC: Bridging Direct and Indirect Methods and Basis Reduction." arXiv:2512.14535.
- Daráš et al. (2026). DeePC vs. Koopman MPC comparison. arXiv:2604.00524.
- Schimperna et al. (2025). Stability of data-driven Koopman MPC with terminal conditions. arXiv:2511.21248.
