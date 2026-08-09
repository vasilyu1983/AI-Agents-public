# Primitive 02 — Bayesian Decision Theory

## Definition

Bayesian decision theory combines prior beliefs with observed evidence to minimize expected loss under the posterior distribution. Given a prior p(θ), a likelihood p(x|θ), and a loss function L(a, θ) for action a and state of nature θ:

```
Posterior: p(θ|x) ∝ p(x|θ) · p(θ)
Bayes risk: r(a|x) = ∫ L(a, θ) · p(θ|x) dθ
Optimal action: a* = argmin_a r(a|x)
```

The Bayes decision rule minimizes the posterior expected loss (equivalently, maximizes posterior expected utility).

## When to Use

- A decision must be taken after observing evidence (test results, market data, user signals).
- The prior is meaningful — based on historical data, expert elicitation, or theory.
- The loss function is asymmetric (false negatives vs. false positives have different costs).

## Inputs

| Input | Description |
|-------|-------------|
| Prior p(θ) | Belief distribution over unknown state before observing data |
| Likelihood p(x|θ) | Probability of observed data given state |
| Loss function L(a, θ) | Cost of taking action a when the true state is θ |
| Observed data x | The evidence that triggers the update |

## Outputs

| Output | Description |
|--------|-------------|
| Posterior p(θ|x) | Updated belief after observing x |
| Bayes risk per action | Posterior expected loss for each action |
| Optimal action a* | Action minimizing Bayes risk |

## Failure Modes

- **Prior dominates with sparse data**: A strong prior and few observations means the posterior barely moves from the prior. Flag this when n is small.
- **Misspecified likelihood**: If the likelihood model is wrong, the posterior is wrong regardless of data volume.
- **Asymmetric loss ignored**: Using a symmetric loss (e.g., squared error) when the actual loss is asymmetric (e.g., missing a fraud event is 10x more costly than a false alert) produces a suboptimal action.
- **Point estimate used instead of posterior**: Acting on the posterior mode (MAP) rather than minimizing expected loss under the full posterior discards uncertainty information.

## Worked Example

A fraud detection system must decide whether to block a transaction.

- Prior fraud rate: p(fraud) = 0.02.
- Likelihood: a fraud-detection model outputs a score s. p(s ≥ 0.8 | fraud) = 0.90, p(s ≥ 0.8 | legitimate) = 0.05.
- Observed: score s = 0.85 (s ≥ 0.8).

Posterior via Bayes' theorem:

```
p(fraud | s ≥ 0.8) = 0.90 × 0.02 / (0.90 × 0.02 + 0.05 × 0.98)
                   = 0.018 / (0.018 + 0.049) ≈ 0.27
```

Loss function: L(block | legitimate) = £5 (false block), L(pass | fraud) = £200 (missed fraud).

Bayes risk of blocking: 0.27 × 0 + 0.73 × £5 = £3.65.
Bayes risk of passing: 0.27 × £200 + 0.73 × 0 = £54.

Block: the Bayesian optimal action despite only a 27% posterior fraud probability.

## Sources

- Raiffa, H. and Schlaifer, R. (1961). Applied Statistical Decision Theory. Harvard University Press.
- Berger, J. O. (1985). Statistical Decision Theory and Bayesian Analysis. Springer.
- DeGroot, M. H. (1970). Optimal Statistical Decisions. McGraw-Hill.
