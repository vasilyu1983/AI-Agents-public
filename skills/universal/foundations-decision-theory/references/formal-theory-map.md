---
description: Formal theory map for decision-theory foundations. Use to separate normative decision quality from descriptive human choice.
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
| Sequential learning | Arms, policies, regret, posterior sampling | Bandits and adaptive allocation | Guardrails may dominate regret optimum; adaptive allocation biases estimates |
| Pure exploration and stopping | Best-arm identification, expected loss | Pick-the-winner tests | Needs a declared threshold of caring |
| Cost-sensitive classification and reject option | Loss matrix, Bayes threshold, abstention cost | Approve / block / defer rules | Requires calibrated, prevalence-matched probabilities |
| Off-policy evaluation | Logged propensities, importance weights, DR | Judging a new policy from logs | Fails without overlap |

## Production Rule

Before using a decision score, state the decision maker, action set, state space, probability source, utility or loss function, and sensitivity range. Without those, the score is a spreadsheet preference, not decision theory.

"Probability source" now has to name whether the number came from a human, a model, or a market, because the three carry different failure modes. A model-generated prior is a forecaster with a measurable track record, not a ground truth. FRI's 2026-07-16 ForecastBench update finds several models statistically indistinguishable from superforecasters on the tournament leaderboard (overlapping intervals: parity, not outperformance), but benchmark parity is not calibration on your question class, and verbalized confidence is not a probability. Score locally. Record the provenance so the sensitivity range can be set against it.
