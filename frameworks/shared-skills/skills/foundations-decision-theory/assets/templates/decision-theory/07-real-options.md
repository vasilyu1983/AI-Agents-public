# Primitive 07 — Real Options (Defer, Expand, Abandon)

## Definition

A real option is the right — but not the obligation — to take an action at a future date at a predetermined cost. Real options analysis (ROA), developed by Dixit and Pindyck, applies financial option pricing to capital investment, product, and operational decisions.

Key option types:

| Option | Right | Exercise condition |
|--------|-------|--------------------|
| Option to defer | Invest later rather than now | Wait for uncertainty to resolve; NPV may improve |
| Option to expand | Scale up after initial success | Observed demand exceeds threshold |
| Option to abandon | Exit and recover salvage value | Continued operation is dominated by stopping |
| Option to switch | Switch inputs, outputs, or technology | Better alternative becomes available |
| Compound option | Option on an option | Stage-gate investments; each stage buys the next |

**Intuition**: Under uncertainty, commitment has a negative externality — it destroys the option value of waiting. The net value of investing now is:

```
NPV_invest_now = NPV_project − Option_value_of_waiting
```

If Option_value > 0, deferral is rational even when NPV_project > 0.

## When to Use

- Capital expenditure decisions where uncertainty will resolve over time.
- Product pivots: the option to pivot preserves value under uncertainty.
- Stage-gate funding: each funding round is an option purchase on the next.
- Any irreversible commitment where the cost of reversal exceeds a threshold.

## Inputs

| Input | Description |
|-------|-------------|
| Current NPV (without option) | Base-case discounted cash flow |
| Volatility σ | Standard deviation of the underlying value |
| Investment cost K | Cost to exercise the option (commit to the action) |
| Time horizon T | Length of time the option is available |
| Risk-free rate r | Discount rate for the riskless component |

## Outputs

| Output | Description |
|--------|-------------|
| Option value | Value of flexibility (Black-Scholes or binomial approximation) |
| Option-adjusted NPV | NPV_invest_now = NPV_project − Option_value_of_deferral |
| Exercise rule | Threshold value at which committing dominates deferring |

## Failure Modes

- **Sunk cost fallacy**: Treating past expenditure as a reason to continue ignores the option to abandon. The relevant comparison is: future value of continuing vs. salvage value of abandoning.
- **Ignoring irreversibility**: DCF analysis that adds up NPV without accounting for commitment cost overvalues early investment under uncertainty.
- **Option value overestimated for non-tradeable assets**: Black-Scholes assumes a liquid underlying market. For non-traded assets (private company, internal project), σ must be estimated from comparable markets or scenario analysis — not from option pricing theory directly.
- **Compound option ignored in stage-gates**: Approving all stages at once destroys the value of the intermediate options to abandon or redirect.

## Worked Example

A startup considers building a dedicated data centre (£2M) or waiting 12 months while demand signals accumulate.

- Current NPV_project = £2.4M → naïve DCF says invest now (NPV = +£400K).
- Volatility of underlying project value: σ = 40% per year.
- Investment cost K = £2M, risk-free rate r = 5%.

Using Black-Scholes approximation for a call option with S = £2.4M, K = £2M, T = 1, σ = 0.4, r = 0.05:

Option value ≈ £0.72M (illustrative; compute with B-S formula).

Option-adjusted NPV of investing now ≈ £400K − £720K = **−£320K**.

Despite a positive naive NPV, deferring is optimal. Wait 12 months; exercise only if the project value exceeds the exercise threshold.

## Multi-Stage Pathways (DAPP Extension)

For decisions with more than two contingent stages — where entire sequences of options depend on observable threshold-crossings — consider **Dynamic Adaptive Policy Pathways (DAPP)** (Haasnoot et al., 2013, *Global Environmental Change* 23(2), 485–498). DAPP maps full pathway sequences rather than a single defer/expand/abandon option: each pathway is a chain of policy choices triggered when an observable indicator crosses a pre-defined tipping point. This extends the single-option logic of real options to long-horizon planning (infrastructure, climate adaptation, multi-phase product rollout) where the right sequence of actions cannot be determined upfront.

**Kill criteria:** Drop if the decision has a short horizon (≤ 2 stages) or a simple state space where standard compound real options suffice.

## Sources

- Dixit, A. K. and Pindyck, R. S. (1994). Investment under Uncertainty. Princeton University Press.
- Myers, S. C. (1977). "Determinants of Corporate Borrowing." Journal of Financial Economics 5(2).
- Trigeorgis, L. (1996). Real Options: Managerial Flexibility and Strategy in Resource Allocation. MIT Press.
- Haasnoot, M. et al. (2013). "Dynamic adaptive policy pathways: A method for crafting robust decisions for a deeply uncertain world." Global Environmental Change 23(2), 485–498. https://doi.org/10.1016/j.gloenvcha.2012.12.006
