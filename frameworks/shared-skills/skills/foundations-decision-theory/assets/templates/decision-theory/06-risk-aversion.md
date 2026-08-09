# Primitive 06 — Risk Aversion, CARA/CRRA, and Certainty Equivalent

## Definition

A decision maker is risk-averse if, for any lottery L, the certainty equivalent CE(L) < E[L] — they prefer a certain amount smaller than the lottery's expected value to the lottery itself. Risk aversion follows from a concave utility function u.

**Certainty Equivalent (CE)**:
```
CE(L) = u⁻¹( E[u(L)] ) = u⁻¹( Σᵢ pᵢ · u(xᵢ) )
```

**Arrow-Pratt measures of risk aversion**:
- Absolute risk aversion: ARA(x) = −u''(x) / u'(x)
- Relative risk aversion: RRA(x) = −x · u''(x) / u'(x)

**CARA (Constant Absolute Risk Aversion)**: u(x) = −e^{−αx}, ARA = α for all x. Suitable for decisions expressed in absolute monetary terms.

**CRRA (Constant Relative Risk Aversion)**: u(x) = x^{1−γ} / (1−γ) for γ ≠ 1 (or ln(x) for γ = 1), RRA = γ. Suitable for proportional or wealth-normalized decisions.

## When to Use

- Any decision where the decision maker's tolerance for variance matters.
- Pricing insurance, reinsurance, or options where CE diverges from EV.
- Checking whether a risk-neutral EV analysis is appropriate (it is only if u is linear).
- Comparing options with the same expected value but different variances.

## Inputs

| Input | Description |
|-------|-------------|
| Lottery / outcome distribution | Probability-outcome pairs |
| Risk aversion type | CARA (α) or CRRA (γ) parameter |
| Utility function u(·) | Derived from the type and parameter |

## Outputs

| Output | Description |
|--------|-------------|
| EU score | Expected utility of the lottery |
| Certainty equivalent CE | The sure amount the agent values equally to the lottery |
| Risk premium | E[L] − CE; the premium paid for certainty |

## Failure Modes

- **Using EV for a risk-averse agent**: CE < EV; the optimal action under EV may not be optimal under EU.
- **Wrong risk aversion parameter**: α or γ should be elicited empirically, not assumed. An underestimated γ produces a ranking biased toward variance.
- **CARA used for proportional bets**: CARA assumes absolute, not proportional, risk tolerance. For percentage returns or wealth-normalized decisions, use CRRA.
- **CE conflated with fair price**: CE is the agent's indifference price; the market price may differ.

## Worked Example

A risk-averse investor (CRRA, γ = 2) evaluates two bets:

- Bet A: 50% × £10,000 + 50% × £0 → EV = £5,000
- Bet B: 100% × £4,000 (certain) → EV = £4,000

CRRA utility u(x) = x^{1−2} / (1−2) = −1/x.

EU(A) = 0.5 × (−1/10000) + 0.5 × (−1/0⁺) → CE of A ≈ £0 (dominated by the zero outcome under CRRA with γ = 2 as x→0). For a clean illustration, use u(x) = √x (equivalent to CRRA γ = 0.5):

- EU(A) = 0.5 × √10000 + 0.5 × √0 = 0.5 × 100 = 50 → CE = 50² = £2,500
- EU(B) = √4000 ≈ 63.2 → CE = £4,000

Under √x utility (γ = 0.5), Bet B is preferred despite lower EV: £4,000 certain > CE of £2,500 for Bet A.

Risk premium for Bet A = £5,000 − £2,500 = £2,500.

## Non-Ergodicity, Kelly Criterion, and Ruin Risk (Expert Judgment)

CE and Arrow-Pratt risk aversion describe a *single* decision averaged over an ensemble of possible states. They do not, by themselves, capture what happens when the same bet is *repeated* and outcomes *compound* (returns, survival probability, compounding debt). Peters (2019, *Nature Physics*) shows that the ensemble average (what EU computes) and the time average (the growth rate one actor actually experiences across repeated multiplicative bets) diverge whenever there is a nonzero chance of an absorbing floor. A bet can have strictly positive EV and still shrink the decision maker's wealth to zero over time — no re-shaping of u(x) fixes this, because the problem is the compounding structure, not the curvature of utility.

**Kelly criterion** (Kelly, 1956): for a repeated bet with known edge, the growth-optimal fraction of bankroll to wager is f* = p − q/b (binary case; p = win probability, q = 1−p, b = net odds). Wagering above f* reduces long-run compound growth even though each individual bet has positive EV — over-betting relative to Kelly is a common and costly error in sizing repeated bets (trading positions, marketing spend per channel, R&D allocation). Full-Kelly is higher-variance than most decision makers can tolerate emotionally or organizationally; fractional Kelly (commonly half-Kelly) is the standard practitioner correction for parameter uncertainty in the edge estimate.

**Practical rule**: before applying CE or CARA/CRRA to a decision that repeats or compounds, ask whether there is an absorbing floor (bankruptcy, delisting, irrecoverable reputational damage, project death). If yes, treat ruin avoidance as a hard constraint gating the decision, not as another term traded off against expected utility — a high-CE option with non-negligible ruin probability is not rescued by a favorable CE calculation.

**Kill criteria**: skip this section for one-shot, non-compounding decisions (the standard CE/Arrow-Pratt treatment above is sufficient); apply it whenever the decision is a repeated bet, a leveraged position, or has a plausible ruin state.

## Sources

- Pratt, J. W. (1964). "Risk Aversion in the Small and in the Large." Econometrica 32(1–2).
- Arrow, K. J. (1971). Essays in the Theory of Risk Bearing. Markham.
- Mas-Colell, A., Whinston, M. D., and Green, J. R. (1995). Microeconomic Theory. Oxford University Press. Chapter 6.
- Peters, O. (2019). "The ergodicity problem in economics." Nature Physics 15, 1216–1221.
- Kelly, J. L. (1956). "A New Interpretation of Information Rate." Bell System Technical Journal 35(4).
