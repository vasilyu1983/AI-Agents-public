# Primitive 01 — Expected Utility Theory

## Definition

Expected utility (EU) is the probability-weighted sum of utilities over outcomes. Given a lottery L = {(p₁, x₁), …, (pₙ, xₙ)}, the expected utility is:

```
EU(L) = Σᵢ pᵢ · u(xᵢ)
```

The von Neumann–Morgenstern (vNM) theorem states that if a decision maker's preferences over lotteries satisfy four axioms — completeness, transitivity, continuity, and independence — there exists a utility function u such that L₁ is preferred to L₂ if and only if EU(L₁) > EU(L₂).

## When to Use

- Choosing among options with well-defined outcome probabilities.
- Ranking investments, bets, or plans where outcomes are commensurable.
- Checking whether a risk-neutral EV calculation is appropriate (it is only if u is linear).

## Inputs

| Input | Description |
|-------|-------------|
| Outcome set {xᵢ} | Mutually exclusive, exhaustive outcomes |
| Probabilities {pᵢ} | Subjective or objective; must sum to 1 |
| Utility function u(·) | Encodes preferences; linear for risk-neutral, concave for risk-averse |

## Outputs

| Output | Description |
|--------|-------------|
| EU score per option | Scalar; higher is preferred |
| Ranking | Ordered list of options by EU |

## Failure Modes

- **Probability mis-specification**: EU is only as valid as the probability estimates. Garbage probabilities produce misleading rankings.
- **Wrong utility function**: Using a linear u (risk-neutral) for a risk-averse agent overvalues high-variance options.
- **Independence axiom violations**: When the independence axiom fails (see Allais, primitive #9), EU rankings may not predict actual choice.
- **Non-commensurable outcomes**: If outcomes cannot be put on a common scale (money, lives, reputation), a utility function that combines them requires explicit elicitation and discloses those trade-offs.

## Worked Example

A startup must choose between two product bets:

- Option A: 70% chance of +£500K revenue, 30% chance of £0.
- Option B: 40% chance of +£900K revenue, 60% chance of £0.

Risk-neutral EV: A = £350K, B = £360K → B is marginally preferred.

With a concave utility u(x) = √x (risk-averse):

- EU(A) = 0.7·√500 + 0.3·√0 = 0.7·22.36 ≈ 15.65
- EU(B) = 0.4·√900 + 0.6·√0 = 0.4·30 = 12.00

Under risk aversion, A is preferred. The raw EV comparison reversed.

## Sources

- von Neumann, J. and Morgenstern, O. (1944/1947). Theory of Games and Economic Behavior. Princeton University Press.
- Savage, L. J. (1954). The Foundations of Statistics. Wiley. (Subjective EU extension.)
- Anscombe, F. J. and Aumann, R. J. (1963). "A Definition of Subjective Probability." Annals of Mathematical Statistics 34(1).
