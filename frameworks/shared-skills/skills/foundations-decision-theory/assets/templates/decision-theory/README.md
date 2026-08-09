# Decision Theory Primitives — Playbook Index

11 canonical decision-theory primitives. Each file is a standalone playbook covering: Definition / When to use / Inputs / Outputs / Failure modes / Worked example / Sources. Cross-cutting guidance lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-expected-utility.md](01-expected-utility.md) | Choosing options by raw expected value, ignoring risk |
| 2 | [02-bayesian-decision.md](02-bayesian-decision.md) | Acting on stale priors without updating on available evidence |
| 3 | [03-minimax-regret.md](03-minimax-regret.md) | Paralysis or overconfidence under deep uncertainty with unknown probabilities |
| 4 | [04-value-of-information.md](04-value-of-information.md) | Running experiments whose cost exceeds their decision value |
| 5 | [05-multi-criteria.md](05-multi-criteria.md) | Collapsing incommensurable objectives without disclosing weights |
| 6 | [06-risk-aversion.md](06-risk-aversion.md) | Ignoring the difference between expected value and certainty equivalent |
| 7 | [07-real-options.md](07-real-options.md) | Treating irreversible decisions as if they were freely reversible |
| 8 | [08-prospect-theory.md](08-prospect-theory.md) | Prescriptive models failing to predict actual human choice |
| 9 | [09-ellsberg-allais.md](09-ellsberg-allais.md) | Applying EU where ambiguity aversion or certainty effects dominate |
| 10 | [10-multi-armed-bandit.md](10-multi-armed-bandit.md) | Fixed allocation that ignores the value of exploration |
| 11 | [11-stochastic-dominance.md](11-stochastic-dominance.md) | Comparing uncertain options only at their mean outcomes |

---

## Composition Stacks

### Should we run this experiment?

Situation: A team proposes a study, A/B test, or pilot before making a decision.

Stack: **#4 (EVPI/EVSI gate)** → if EVSI > cost, run study → **#1 (EU)** + **#6 (risk aversion check)** on the posterior decision → **#3 (minimax regret)** as robustness check if prior is weak.

### Feature roadmap ranking under multiple objectives

Situation: Ranking features or bets on cost, reach, strategic value, and risk.

Stack: **#5 (MCDA weights + sensitivity)** → **#7 (real options)** for irreversible commitments → **#6 (CE check)** for high-variance options → surface rank-reversals from sensitivity analysis.

### Sequential resource allocation

Situation: Budget or capacity allocated across options whose performance is unknown and learned over time.

Stack: **#4 (EVPI bound)** → **#10 (Thompson sampling or UCB)** → **#11 (stochastic dominance)** for early reallocation when dominance becomes clear → **#6 (risk aversion)** to adjust exploitation timing.

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
| Distribution-level ranking | #11 (stochastic dominance) | #1 |
