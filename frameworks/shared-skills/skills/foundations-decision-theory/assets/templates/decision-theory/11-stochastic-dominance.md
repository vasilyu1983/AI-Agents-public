# Primitive 11 — Stochastic Dominance (FSD, SSD)

## Definition

Stochastic dominance provides distribution-level comparisons between uncertain options without requiring a fully specified utility function. It ranks lotteries for broad classes of utility functions.

**First-Order Stochastic Dominance (FSD)**: Lottery A FSD-dominates lottery B if, for every outcome x:
```
F_A(x) ≤ F_B(x) for all x, with strict inequality for some x
```
where F(x) is the cumulative distribution function (CDF). Equivalently, A FSD B iff E_A[u(x)] ≥ E_B[u(x)] for every non-decreasing utility function u. A rational agent — regardless of risk attitude — will prefer A over B.

**Second-Order Stochastic Dominance (SSD)**: A SSD-dominates B if:
```
∫_{-∞}^{z} F_A(x) dx ≤ ∫_{-∞}^{z} F_B(x) dx for all z
```
Equivalently, A SSD B iff E_A[u(x)] ≥ E_B[u(x)] for every non-decreasing and concave utility function u. SSD applies to risk-averse agents; A SSD B implies A has lower or equal variance for any given mean. If A and B have the same mean, A SSD B means A is a mean-preserving contraction of B.

## When to Use

- Comparing portfolios, treatments, or plans when the utility function is not known precisely but the agent is known to be risk-averse.
- Confirming that one option dominates before applying a more specific decision rule.
- Ruling out clearly inferior options (FSD-dominated) without any utility specification.
- Post-experiment analysis: checking whether the winner FSD-dominates the control.

## Inputs

| Input | Description |
|-------|-------------|
| CDFs F_A(x), F_B(x) | Full distributions for each option |
| Agent type | Non-decreasing u (FSD) or concave and non-decreasing u (SSD) |

## Outputs

| Output | Description |
|--------|-------------|
| FSD result | A FSD-dominates B, B FSD-dominates A, or neither |
| SSD result | A SSD-dominates B, B SSD-dominates A, or neither |
| Dominant option | Option to prefer if dominance holds |
| Non-dominated pairs | Pairs requiring further utility specification |

## Failure Modes

- **Comparing only at the mean**: Two distributions with the same mean can have very different variance profiles; the mean does not determine dominance.
- **FSD confused with SSD**: FSD is a stronger condition. FSD implies SSD, but not vice versa. A risk-seeking agent may not prefer the SSD-dominant option.
- **Dominance used as proof of optimality**: Stochastic dominance identifies robust preferences, not optima. An option could SSD-dominate all others yet still not be the EU-maximizing choice for a specific utility function.
- **Empirical distributions used with small samples**: Estimating CDFs from small samples introduces significant sampling error. Check dominance with bootstrapped confidence intervals.

## Worked Example

Two marketing channels (A and B) for a product launch. Daily revenue distributions (simplified to five scenarios):

| Scenario (p=0.20 each) | Channel A | Channel B |
|------------------------|-----------|-----------|
| S1 | £100 | £80 |
| S2 | £200 | £150 |
| S3 | £300 | £320 |
| S4 | £400 | £430 |
| S5 | £500 | £600 |

Mean A = £300, Mean B = £316.

CDF check for FSD (F_A(x) ≤ F_B(x) for all x):
- At x=100: F_A = 0.20, F_B = 0.20 (equal)
- At x=150: F_A = 0.20, F_B = 0.40 (F_A < F_B → A better here)
- At x=300: F_A = 0.60, F_B = 0.40 (F_A > F_B → B better here)

Neither dominates under FSD (CDFs cross). SSD check requires comparing integrated CDFs.

∫F_A − ∫F_B changes sign → neither dominates under SSD either. Conclusion: neither channel stochastically dominates the other; a specific utility function is needed to rank them.

## Sources

- Hadar, J. and Russell, W. R. (1969). "Rules for Ordering Uncertain Prospects." American Economic Review 59(1).
- Hanoch, G. and Levy, H. (1969). "The Efficiency Analysis of Choices Involving Risk." Review of Economic Studies 36(3).
- Levy, H. (1992). "Stochastic Dominance and Expected Utility: Survey and Analysis." Management Science 38(4).
- Rothschild, M. and Stiglitz, J. E. (1970). "Increasing Risk: I. A Definition." Journal of Economic Theory 2(3).
