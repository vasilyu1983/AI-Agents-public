# Primitive 08 — Prospect Theory

## Definition

Prospect theory (Kahneman and Tversky, 1979) is a descriptive model of decision under risk that accounts for systematic deviations from EU theory. It replaces the EU framework with two modifications:

**Value function v(x)** over gains and losses relative to a reference point:
- Defined over changes from the reference point, not final wealth.
- Concave in the gain domain: v''(x) < 0 for x > 0 (diminishing sensitivity to gains).
- Convex in the loss domain: v''(x) > 0 for x < 0 (diminishing sensitivity to losses, risk-seeking below the reference point).
- Steeper for losses than gains: |v(−x)| > |v(x)| (loss aversion).

The most common parameterization: v(x) = x^α for x ≥ 0, v(x) = −λ(−x)^α for x < 0, with Tversky and Kahneman's (1992) original CPT estimate α ≈ 0.88, λ ≈ 2.25. **Correction (2026-07-11)**: treat λ ≈ 2.25 as one data point, not the population parameter. Brown, Imai, Vieider, and Camerer's large-scale meta-analysis (*Journal of Economic Literature* 62(2), 2024, pooling 607 estimates from 150 studies) puts the mean loss-aversion coefficient at λ ≈ 1.955 (95% CI [1.820, 2.102]) — meaningfully lower than the original 2.25, after correcting for publication bias and methodological heterogeneity across the literature. A separate 2024 meta-analysis in risky contexts (Walasek, Mullett, and Stewart, *Journal of Economic Psychology* 103) and a subsequent re-meta-analysis have also questioned how robust loss aversion is as a stable individual trait versus an artifact of elicitation method. **Practical implication**: elicit λ for the specific population when precision matters (see Elicitation Failure Modes in SKILL.md); do not hard-code 2.25, and do not treat any single point estimate — including 1.955 — as beyond dispute.

**Probability weighting function w(p)**:
- Overweights small probabilities: w(p) > p for small p.
- Underweights large probabilities: w(p) < p for p close to 1.
- w(0) = 0, w(1) = 1.

The prospect theory value:
```
V(L) = Σᵢ w(pᵢ) · v(xᵢ − r)
```
where r is the reference point.

## When to Use

- Predicting actual human choices, not prescribing optimal ones.
- Designing pricing, framing, or incentive structures that account for loss aversion.
- Evaluating why rational-model recommendations are rejected in practice.
- Calibrating behavioral nudges or default settings.

## Inputs

| Input | Description |
|-------|-------------|
| Outcomes {xᵢ} | Gains and losses relative to reference point r |
| Reference point r | Status quo, aspiration level, or expectation anchor |
| Probabilities {pᵢ} | Objective or stated probabilities |
| Parameters α, λ | Value function curvature and loss aversion coefficient |

## Outputs

| Output | Description |
|--------|-------------|
| Prospect value V(L) | Weighted utility under prospect theory |
| Predicted choice | Option with highest V among the choice set |
| Loss aversion gap | Difference between EU prediction and PT prediction |

## Failure Modes

- **Using PT as a prescriptive model**: PT describes how people choose; it does not recommend the best choice. For normative decisions, use EU (#1) or Bayesian decision (#2).
- **Reference point misidentified**: The value function is defined relative to r. A wrong reference point produces wrong predictions. Anchors shift reference points; track them explicitly.
- **Loss aversion parameter treated as universal**: λ is not a fixed constant — meta-analytic estimates range roughly 1.8–2.3 depending on domain, elicitation method, and publication-bias correction (see Correction above). Individual and population variation is substantial; elicit λ for the specific population if precision matters, and report it as a range, not a point value.
- **Probability weighting ignored at the tails**: PT overweights small probabilities — this drives insurance purchases and lottery buying. Ignoring probability weighting leads to wrong framing predictions.

## Worked Example

A product team evaluates two pricing framings for a £50/month subscription:

- Framing A: "£50/month — save £10 vs. the standard £60 plan" (gain frame: +£10 saving).
- Framing B: "£60/month — unless you upgrade, you lose £10 off compared to early adopters" (loss frame: −£10 relative to a £50 reference).

EU predicts indifference: both framings describe the same £50 price. Prospect theory predicts Framing B induces more conversions because the loss frame (−£10) has higher |v| than the equivalent gain frame (+£10) by factor λ ≈ 2.25.

Prediction: conversion rate under Framing B will exceed Framing A by approximately 10–20% in typical B2C contexts (empirically tested in Kahneman and Tversky's original work and replicated widely).

## Resource-Rational Reframe (2024–2025)

Prospect theory deviations from EU — loss aversion, probability weighting, reference-point dependence — are now reinterpreted by **resource-rational analysis** as optimal cognitive adaptations to computational cost constraints, not unexplained irrationality. Lieder and Griffiths (2020, *Behavioral and Brain Sciences*) show that many PT anomalies arise when agents allocate limited cognitive resources optimally. The **ARRM** framework (Lu et al., *Cognitive Psychology* 156, 2025; PubMed 39813936) extends this to a modular computational account that explains specific anomalies (overweighting of losses, probability distortion) as cost-optimal resource allocation.

**Practical implication for nudge design:** Correcting PT biases may fight the grain of cognitively rational behaviour. Interventions should reduce cognitive load rather than assume pure irrationality. This also updates Primitive #9 (Ellsberg/Allais): ambiguity aversion may similarly reflect resource-rational avoidance of costly probability estimation.

**Kill criteria:** Drop the resource-rational framing if the application is purely prescriptive (designing rational decision aids for ideal agents with no cognitive-cost model) — the framing is most useful for descriptive analysis and nudge design.

## Sources

- Kahneman, D. and Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." Econometrica 47(2).
- Tversky, A. and Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty." Journal of Risk and Uncertainty 5(4).
- Camerer, C. F. (1995). "Individual Decision Making." In J. Kagel and A. Roth (eds.), Handbook of Experimental Economics. Princeton University Press.
- Brown, A. L., Imai, T., Vieider, F. M., and Camerer, C. F. (2024). "Meta-Analysis of Empirical Estimates of Loss Aversion." Journal of Economic Literature 62(2), 485–516. https://doi.org/10.1257/jel.20221698
- Lieder, F. and Griffiths, T. L. (2020). "Resource-rational analysis: Understanding human cognition as the optimal use of limited computational resources." Behavioral and Brain Sciences. https://cocosci.princeton.edu/papers/lieder_resource.pdf
- Lu, Y.-L. et al. (2025). "Exploring the bounded rationality in human decision anomalies through an assemblable computational framework." Cognitive Psychology 156, 101713. PubMed 39813936. https://www.sciencedirect.com/science/article/pii/S0010028525000015
