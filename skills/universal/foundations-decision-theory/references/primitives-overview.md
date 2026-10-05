---
description: Anti-patterns by decision structure for decision-theory primitives. The primitive index and checklist live in SKILL.md.
status: stable
---

# Decision Theory Anti-Patterns by Decision Structure

The primitive index, misuse boundaries and sources live in [`../SKILL.md`](../SKILL.md) and [`../data/sources.json`](../data/sources.json). This file keeps only the structure-specific anti-patterns.

## Single Risky Choice

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Pick highest EV regardless of variance | Risk aversion ignored | Certainty equivalent (#6) — CE = EV only for risk-neutral agents |
| Compare options by most likely outcome | Mode ≠ mean ≠ CE | Use the full distribution; check stochastic dominance (#11) |
| Skip the option to wait | Irreversibility not priced | Real options (#7) — deferral has value when uncertainty will resolve |

## Experiment or Study Design

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Approve any study that "might help" | Value not checked | EVPI < utility-compatible additive cost ⇒ skip; otherwise approve only on EVSI of the specific design vs cost, with delay in terminal outcomes (#4) |
| Run full study when a pilot suffices | EVSI by sample size not computed | Optimise net value over sample sizes including n = 0 (#4) |
| Run a study whose results cannot change the action | The same action is optimal after every positive-probability signal | EVSI = 0 for that study; skip it at positive cost. EVPI may still be positive (#4; [Heath & Baio, §2](https://arxiv.org/pdf/1709.02319)) |

## Multi-Objective Ranking

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Report MCDA ranking without weight disclosure | Weights embed preferences that look like facts | Disclose weight provenance and sensitivity (#5) |
| Accept rank stability without tests | Weight perturbation and alternative-set changes can reverse rankings | Perturb weights and run RRT1–RRT3 (#5) |

## Sequential Decisions

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Bandit used where an unbiased effect size is needed | Adaptive allocation biases per-arm estimates | Fixed-allocation randomised test; bandit only when in-experiment reward dominates ([thresholds-stopping-and-ope §3](thresholds-stopping-and-ope.md#3-best-arm-identification-vs-regret)) |
| Fixed allocation when in-experiment reward dominates | Foregone reward during learning | UCB or Thompson sampling; a sublinear cumulative-regret bound does not mean a bounded total loss (#10) |
| Exploit immediately after a few observations | Posterior still wide | Keep exploring; stop on expected loss below a threshold of caring, not on P(best) alone |

## Thresholds and Abstention

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| 0.5 cut-off on a risk score | Ignores unequal error costs | p* = c_FP/(c_FP+c_FN) on calibrated, prevalence-adjusted probabilities ([§1](thresholds-stopping-and-ope.md#1-cost-sensitive-thresholds)) |
| Escalate everything uncertain to a human | Deferral has a cost and needs a reviewer who can resolve the case | Chow's three-way rule with explicit review cost ([§2](thresholds-stopping-and-ope.md#2-abstention-reject-option)) |
