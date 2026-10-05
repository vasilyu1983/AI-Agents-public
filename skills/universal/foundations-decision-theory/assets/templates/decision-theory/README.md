# Decision Theory Primitives — Playbook Index

11 canonical decision-theory primitives. Each file is a standalone playbook covering: Definition / When to use / Inputs / Outputs / Failure modes / Worked example / Sources. Cross-cutting guidance lives in [`../../../SKILL.md`](../../../SKILL.md).

---

The primitive index lives in [`../../../SKILL.md#quick-reference`](../../../SKILL.md#quick-reference); this file keeps only the stacks and the selection guide.

---

## Composition Stacks

### Should we run this experiment?

Situation: A team proposes a study, A/B test, or pilot before making a decision.

Stack: **#4 (EVPI/EVSI gate)** → compare total EU including study costs/delay (EVSI > cost only for additive utility-compatible costs) → **#1 (EU)** + **#6 (risk aversion check)** on the posterior decision → **#3 (minimax regret)** as robustness check if prior is weak.

### Feature roadmap ranking under multiple objectives

Situation: Ranking features or bets on cost, reach, strategic value, and risk.

Stack: **#5 (MCDA weights + sensitivity)** → **#7 (real options)** for irreversible commitments → **#6 (CE check)** for high-variance options → surface rank-reversals from sensitivity analysis.

### Sequential resource allocation

Situation: Budget or capacity allocated across options whose performance is unknown and learned over time.

Stack: **#4 (EVPI as a ceiling on learning value)** → declare the objective (regret vs best-arm identification) → **#10 (Thompson sampling or UCB)** or a fixed-allocation test when an unbiased effect is needed → stop on expected loss below a threshold of caring ([thresholds-stopping-and-ope.md](../../../references/thresholds-stopping-and-ope.md)) → **#6 (risk aversion)** on a declared scalar utility.

### Behavioral pricing and framing

Situation: Pricing or offer design where human choice behavior matters.

Stack: **#8 (prospect theory)** for loss-framing and reference-point design → **#9 (Allais/Ellsberg check)** if the offer involves mixed probabilities or unknown distributions → **#1 (EU)** as normative baseline to compare against behavioral prediction.

---

## Selection Guide

| Decision structure | Primary primitive | Secondary |
|-------------------|-------------------|-----------|
| Known probabilities, commensurable outcomes | #1 (EU) | #6 (risk aversion) |
| Evidence arriving, posterior update | #2 (Bayesian) | #1 |
| Probabilities unknown / adversarial | #3 (minimax regret) | #9 (Ellsberg) |
| Pre-decision study | #4 (VoI) | #1, #2 |
| Multiple incommensurable criteria | #5 (MCDA) | #7 (real options) |
| Risk-averse stakeholder | #6 (risk aversion) | #1 |
| Irreversible commitment | #7 (real options) | #4 |
| Predicting human choice | #8 (prospect theory) | #9 |
| EU violations suspected | #9 (Ellsberg/Allais) | #3, #8 |
| Sequential exploration | #10 (MAB) | #4 |
| Probability → act / abstain threshold; pick-the-winner stopping; policy evaluation from logs | [thresholds-stopping-and-ope](../../../references/thresholds-stopping-and-ope.md) | #2, #4 |
| Distribution-level ranking | #11 (stochastic dominance) | #1 |
