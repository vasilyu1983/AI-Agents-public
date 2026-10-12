# Nonlinear Dynamics Checks

Load when an agent loop gives different outcomes for near-identical input, when someone asks for an early-warning alert, or when someone claims "chaos" or a power law in ops data. Chaos and fractal vocabulary adds a decision here only through four checks: run-to-run divergence, early-warning statistics, tail fitting, and a reverse parameter sweep.

Primary texts: Strogatz, *Nonlinear Dynamics and Chaos*, 3rd ed. (2024) for the mathematics; Sayama, *Introduction to the Modeling and Analysis of Complex Systems* (2015, open textbook) for discrete-time, cellular-automaton and agent-based simulations. Gleick's *Chaos* (1987) is history, not a rule source.

## Two different "Lyapunov" terms

- Lyapunov function (primitive #4): a potential that decreases each step. It is a convergence proof for a loop.
- Lyapunov exponent: the average growth rate of a small perturbation, defined for a deterministic map or flow and estimated over a long orbit (Strogatz §10.5). It needs a long, stationary, low-noise series. Agent runs and ops metrics rarely meet that condition.
- Never swap the two. Do not report an exponent for an agent loop.

## Checks

| Check | Rule | Source |
|---|---|---|
| Run-to-run divergence | Separate two causes first: serving noise and input sensitivity. Temperature 0 is not deterministic: batch-size-dependent kernels change outputs. Fix serving (batch-invariant kernels) or record a seed before any dynamics claim. | He et al. 2025 (Thinking Machines blog, not peer reviewed) |
| Perturbation divergence | Use meaning-preserving prompt edits with a fixed seed. Report the mean pairwise distance of outcomes per round and its log-slope with an interval. Call it an "instability index", not an exponent. | Shimao et al. 2026, arXiv:2603.09127 (preprint) |
| Divergence vs quality | Divergent trajectories matter only if outcome quality differs. The authors state they have not linked divergence to decision quality. Link it to an accuracy or review metric before you act. | Shimao et al. 2026 |
| Early-warning signals | Rising lag-1 autocorrelation and variance of a detrended metric can precede a regime change, but false positives are the key problem. Results depend on window, filter and detrending. Variance can fall, and noise-induced transitions give no warning. | Lenton et al. 2012 |
| Heavy-tail claim | Fit by maximum likelihood, report xmin, a goodness-of-fit test and a likelihood-ratio comparison against log-normal and exponential. Do not read a slope off a log-log plot. No sourced minimum sample size: use the Clauset-Shalizi-Newman goodness-of-fit test, and say "inconclusive" when it fails. | Clauset, Shalizi, Newman 2009 |
| Regime boundary | Sweep one parameter (retry budget, gain, queue limit, temperature) on a fixed workload. A sudden change in steady state marks the boundary (a bifurcation). Stay a margin away from it. | Strogatz ch. 3 |
| Reverse sweep | After a jump, sweep the parameter back. If the system does not return by the same path, it is bistable with hysteresis: restoring the setting does not restore the state. Then a config rollback is not a rollback; plan a state reset (drain, restart, cache flush) as part of it. | Strogatz §3.6-3.7 |
| Emergence claim | Before you credit a collective pattern in a multi-agent run to prompt design or agent intelligence, build the simplest fixed-rule model (cellular automaton or agent-based) that reproduces it. If the pattern appears without the feature you credit, the claim fails. | Sayama ch. 11-12, 19 |

## Judgment rules

1. Measure before you name. "Not measured" is a valid result when you have too few runs.
2. Before you alert on an early-warning statistic, backtest it on past incidents and on quiet periods. Alert only if it beats a plain threshold on the metric itself. Use two statistics and two window lengths.
3. A heavy-tail fit changes planning only when it changes the tail percentile you provision for.
4. Prefer a damped design to a tuned boundary: add a cap, a step limit or a temperature floor instead of operating near a sensitivity threshold.
5. Treat a slow parameter drift (traffic growth, context length, model upgrade) as a sweep: the jump arrives without a change event, so an incident with "nothing changed" is a bifurcation suspect (Strogatz §3.7).

## Hand-offs

- Heavy tails and self-similar traffic: `foundations-queueing-theory`.
- Power-law fitting and scale-free caveats: `foundations-network-science`.
- Metastable retry feedback: `foundations-distributed-systems`.
- Chaos engineering (fault injection) is not the same subject. It tests failure handling and says nothing about sensitive dependence: `qa-resilience`.
- Oscillation from gain, delay or windup: this skill, primitives #1, #7, #8.

## Misuse boundaries

- Sampling randomness is not chaos. Chaos needs deterministic dynamics with bounded, aperiodic orbits and sensitive dependence on initial conditions (Strogatz §9.3).
- A straight line on a log-log plot is not a power law. Log-normals look the same.
- "Butterfly effect" is not a reason to skip root-cause analysis.

## Not yet decision-grade

- Edge of chaos in networks (Poole et al. 2016): an initialization topic, not an ops rule.
- Fractal dimension of dependency graphs vs bug counts (Marchesi and Tonelli): two open-source systems, not validated. Do not use it as a gate.
- Power-law incident sizes in software postmortems: unsourced, verify.
- Early-warning validation on software metrics: unsourced, verify.
