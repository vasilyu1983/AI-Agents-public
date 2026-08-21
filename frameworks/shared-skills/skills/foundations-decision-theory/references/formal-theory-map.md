---
description: Formal theory map for decision-theory foundations. Use to separate normative decision quality from descriptive human choice.
last_verified: 2026-08-14
status: stable
---

# Decision Theory Formal Theory Map

## Purpose

Use this map when a decision recommendation needs an explicit decision rule, utility model, probability contract, or uncertainty boundary.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Expected utility | Lotteries, preferences, utility functions | Normative ranking under risk | Requires axioms and known probabilities |
| Bayesian decision theory | Prior, likelihood, posterior, loss function | Actions after evidence | Sensitive to priors and loss specification |
| Robust choice | Regret matrix, maximin, minimax regret | Deep uncertainty and ambiguity | Can be conservative |
| Value of information | EVPI, EVSI, sample information | Experiment and research funding | Information is valuable only if it can change action |
| Multi-criteria decision analysis | Criteria, weights, scores, dominance | Tradeoffs across objectives | Weights are subjective |
| Risk aversion | Concave utility, Arrow-Pratt measures | Certainty equivalent and downside aversion | Utility is stakeholder-specific |
| Real options | Irreversibility, volatility, option value | Defer/expand/abandon choices | Requires a credible uncertainty-resolution path |
| Sequential learning | Arms, policies, regret, posterior sampling | Bandits and adaptive allocation | Guardrails may dominate regret optimum |

## Production Rule

Before using a decision score, state the decision maker, action set, state space, probability source, utility or loss function, and sensitivity range. Without those, the score is a spreadsheet preference, not decision theory.

"Probability source" now has to name whether the number came from a human, a model, or a market, because the three carry different failure modes. A model-generated prior is a forecaster with a measurable track record, not a ground truth: as of early 2026 the best LLMs still trail human superforecasters on ForecastBench, skew overconfident on events they rate as likely, and produce verbalized confidence that diverges from both their own token likelihoods and realized accuracy. Record the provenance so the sensitivity range can be set against it.
