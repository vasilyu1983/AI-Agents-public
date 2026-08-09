# Primitive: Prospect Theory

## Definition

Prospect theory (Kahneman & Tversky, 1979) describes how people actually evaluate outcomes under uncertainty — which differs systematically from expected utility theory. Two core mechanisms:

1. **Value function**: Outcomes are evaluated relative to a reference point, not in absolute terms. The function is concave for gains (diminishing sensitivity) and convex for losses (also diminishing sensitivity), but steeper for losses than gains — producing loss aversion. The function is S-shaped.

2. **Probability weighting**: People overweight small probabilities and underweight medium-to-large probabilities. This explains why people buy lottery tickets (low probability of large gain overweighted) and insurance (low probability of large loss overweighted).

The value function implies:
- A $50 gain from a $100 starting point feels better than a $50 gain from a $500 starting point (diminishing sensitivity).
- A $50 loss from a $100 starting point feels worse than a $50 loss from a $500 starting point.
- Framing the same outcome as avoiding a loss vs achieving a gain changes its attractiveness.

## When to Use

- Writing pricing copy where the same value can be framed as gain or loss prevention.
- Designing upgrade or upsell messaging.
- Constructing offers with uncertain outcomes (trials, guarantees, money-back policies).
- Evaluating whether framing choices in your interface are gain-dominant or loss-dominant.

## Misuse Boundary

**Ethical use**: Use framing to accurately represent the genuine value or risk a user faces. If using a plan prevents a real cost (data loss, compliance failure, missed revenue), framing it as loss prevention is accurate.

**Manipulation**: Fabricating a reference point that inflates perceived loss ("You're losing $500/month in efficiency" when no evidence exists) or overweighting tiny probabilities ("You could win $10,000!") to drive impulsive decisions.

**Required condition**: The reference point must be real and relevant to this user's situation. Framing must not be more dramatic than the underlying reality warrants.

## Inputs

- The outcome to communicate (feature benefit, price saving, risk reduction).
- The user's existing reference point (current cost, current solution, current behavior).
- The context: is this a gain situation, a loss-prevention situation, or uncertain outcome?

## Outputs

- A framed message that matches the behavioral reality (gain vs loss framing, not arbitrary).
- A probability statement, if applicable, using accurate language.
- A reference point, set explicitly rather than left to the user's imagination.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Framing has no effect | User has a strong external reference point that overrides yours | Surface and address the existing anchor explicitly before presenting your frame |
| Loss framing creates anxiety without action | Loss is real but feels uncontrollable | Pair loss frame with a clear, low-friction action that prevents the loss |
| Probability language backfires | "5% chance of failure" interpreted as "5% chance of success" | Specify both the probability and the outcome direction explicitly |
| Gain framing underperforms loss framing | Outcome is genuinely a loss-prevention scenario | Switch to loss framing — it matches the value function's steeper loss curve |

## Worked Example

**Scenario**: Pricing page for a backup product.

Without prospect theory: "Get 100 GB of secure backup storage for $5/month."

With prospect theory:
- Identify the user's reference point: they risk losing work if their local drive fails.
- Loss framing (likely stronger): "Don't lose a week of work to a $0.17/day incident."
- Gain framing alternative: "Get peace of mind — your work is always recoverable."
- Combine: headline uses loss framing (high impact); body copy uses gain framing (reduces anxiety).

**Ethical check**: The reference point (drive failure risk) is real. The $0.17/day framing is the cost divided by 30 — accurate. The loss (a week's work) is a plausible outcome, not fabricated.

## Sources

- Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. _Econometrica_, 47(2), 263–292. — foundational.
- Tversky, A. & Kahneman, D. (1981). The framing of decisions and the psychology of choice. _Science_, 211(4481), 453–458. — framing effects.
- Kahneman, D. (2011). _Thinking, Fast and Slow_, ch. 26–28. — accessible treatment of prospect theory.
- Imai, T., Nunnari, S., Wu, J. & Vieider, F. M. (2025). Meta-Analysis of Prospect Theory Parameters. CESifo Working Paper No. 12334. First joint meta-analysis of all cumulative PT parameters simultaneously (166 papers, 812 estimates). Confirms diminishing sensitivity towards outcomes and probabilities; finds that experimental and measurement design indicators are the strongest predictors of parameter variation — reinforcing the caution against applying canonical parameter values outside their original elicitation context.
