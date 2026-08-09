# Primitive 03 — Minimax Regret

## Definition

Minimax regret (Savage, 1954) is a decision rule for decisions under ignorance — when probabilities over states of nature are unknown. Regret for action a under state θ is the opportunity loss relative to the best action in that state:

```
Regret(a, θ) = max_{a'} u(a', θ) − u(a, θ)
```

The minimax regret rule selects the action that minimizes the maximum regret across all states:

```
a* = argmin_a [ max_θ Regret(a, θ) ]
```

Unlike maximin (which maximizes the worst-case payoff), minimax regret benchmarks against what could have been done — making it sensitive to the opportunity cost of being wrong, not merely the absolute outcome.

## When to Use

- Probabilities are unknown or contested and EU cannot be applied.
- Adversarial environments where a worst-case nature is plausible.
- Robustness is required: the decision should not look catastrophically wrong in hindsight under any realized state.
- As a cross-check on EU when the prior is weak.

## Inputs

| Input | Description |
|-------|-------------|
| Action set {aᵢ} | Available choices |
| State set {θⱼ} | Exhaustive states of nature (probabilities unknown) |
| Payoff matrix u(aᵢ, θⱼ) | Utility or payoff of each action under each state |

## Outputs

| Output | Description |
|--------|-------------|
| Regret matrix | Opportunity loss for each action-state pair |
| Max regret per action | Worst-case regret for each action |
| Minimax-regret action | Action minimizing max regret |

## Failure Modes

- **Adding irrelevant alternatives changes the choice**: Minimax regret is not independent of irrelevant alternatives. Adding a new (never-chosen) action can alter the recommendation. Check whether the addition is truly irrelevant.
- **State enumeration is incomplete**: If the state space misses a scenario, the regret calculation is wrong. Enumerate scenarios conservatively.
- **Used where probabilities are actually estimable**: When a meaningful prior exists, EU or Bayesian decision dominates. Minimax regret is for genuine ignorance, not laziness about probability elicitation.
- **Maximin confused with minimax regret**: Maximin (maximize the minimum payoff) ignores opportunity costs and can be excessively conservative. Minimax regret is distinct.

## Worked Example

A product team must choose an infrastructure architecture before demand is known:

| Architecture | Low demand (θ₁) | High demand (θ₂) |
|--------------|-----------------|------------------|
| Serverless (a₁) | £200K savings | -£400K (bottleneck) |
| Dedicated (a₂) | -£100K (over-provisioned) | £600K benefit |
| Hybrid (a₃) | £80K savings | £200K benefit |

Best in θ₁: a₁ = 200K. Best in θ₂: a₂ = 600K.

Regret matrix:

| Architecture | Regret(θ₁) | Regret(θ₂) | Max Regret |
|--------------|------------|------------|------------|
| Serverless (a₁) | 0 | 1000K | **1000K** |
| Dedicated (a₂) | 300K | 0 | **300K** |
| Hybrid (a₃) | 120K | 400K | **400K** |

Minimax regret selects dedicated (a₂) with a max regret of £300K.

## Wasserstein DRO / Minimax-Regret Bridge (2025)

When the probability distribution over states is itself uncertain (unknown within an ambiguity set), minimax regret and distributionally robust optimization (DRO) converge: Wasserstein DRRO (Fiechtner & Blanchet, 2025) shows this reduces to ERM up to first-order under smooth losses; Gen-WDRO (NeurIPS 2025) uses generative models to adaptively size ambiguity sets; DRPO (Jia et al., NeurIPS 2025) handles the case where *decisions influence the distribution*. Use when you have data on past states (enabling Wasserstein-ball ambiguity) but cannot commit to a single prior.

**Kill criteria:** Drop if the state distribution is well-characterized (use EU or Bayesian); drop if no historical data samples exist to anchor the Wasserstein ball.

## Sources

- Savage, L. J. (1954). The Foundations of Statistics. Wiley. Chapter 9.
- Milnor, J. (1954). "Games Against Nature." In R. Thrall et al. (eds.), Decision Processes. Wiley.
- Stoye, J. (2011). "Axioms for Minimax Regret Choice Correspondences." Journal of Economic Theory 146(6).
- Fiechtner, M. and Blanchet, J. (2025). "Wasserstein Distributionally Robust Regret Optimization." arXiv:2504.10796.
- NeurIPS 2025. "Robust Decisions via Generative Wasserstein Distributionally Robust Optimization." (Gen-WDRO).
- Jia, Wang, Dong, Hanasusanto (2025). "Distributionally Robust Performative Optimization." arXiv:2407.01344. NeurIPS 2025.
