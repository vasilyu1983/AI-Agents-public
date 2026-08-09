---
description: Domain-agnostic overview of 11 decision-theory primitives. Canonical definitions, primary use cases, and cross-cutting failure modes.
last_verified: 2026-05-02
status: stable
---

# Decision Theory Primitives Overview

## Table of Contents

- [Why Formal Decision Theory Matters](#why-formal-decision-theory-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Decision Structure](#anti-patterns-by-decision-structure)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Formal Decision Theory Matters

Decisions under uncertainty fail in predictable ways. Without formal structure:

| Failure Mode | Decision Theory Diagnosis | What Goes Wrong |
|-------------|--------------------------|-----------------|
| Option chosen by highest average outcome | Raw expected value ignores risk; CE < EV for risk-averse agents | Risk-averse stakeholder accepts a bet they would pay to avoid |
| Experiment approved without value check | EVPI not computed; study cost may exceed the decision value of its information | Wasted time and budget on a study that cannot change the optimal action |
| Multiple objectives collapsed to one number silently | MCDA weights are hidden preferences; rank-reversals go undisclosed | Ranking looks objective; different reasonable weights reverse it |
| Irreversible commitment made under high uncertainty | Option value of deferral ignored | Unnecessary value destroyed by premature lock-in |
| Human choices predicted with EU | Prospect theory effects — loss aversion, probability weighting, reference dependence — are systematic deviations | Model fails to predict behavior; nudges misfire |

Each primitive below addresses a specific structural failure.

---

## Primitive Index

11 primitives, each in its own playbook under [`../assets/templates/decision-theory/`](../assets/templates/decision-theory/).

| # | Primitive | Failure Mode | Primary Use Cases |
|---|-----------|-------------|------------------|
| 1 | [Expected Utility](../assets/templates/decision-theory/01-expected-utility.md) | Choosing by EV without risk adjustment | Option ranking, go/no-go gates, pricing bets |
| 2 | [Bayesian Decision](../assets/templates/decision-theory/02-bayesian-decision.md) | Acting on stale priors; ignoring evidence | Medical diagnosis, fraud detection, posterior action |
| 3 | [Minimax Regret](../assets/templates/decision-theory/03-minimax-regret.md) | Paralysis or overconfidence under unknown probabilities | Adversarial pricing, unknown-market entry, robustness |
| 4 | [Value of Information](../assets/templates/decision-theory/04-value-of-information.md) | Running experiments that cannot improve the decision | Study sizing, pilot design, A/B test gating |
| 5 | [Multi-Criteria Decision Analysis](../assets/templates/decision-theory/05-multi-criteria.md) | Ignoring incommensurable objectives | Roadmap ranking, vendor selection, investment screening |
| 6 | [Risk Aversion](../assets/templates/decision-theory/06-risk-aversion.md) | Treating EV as the decision criterion for risk-averse agents | CE pricing, insurance, downside-sensitive allocation |
| 7 | [Real Options](../assets/templates/decision-theory/07-real-options.md) | Committing irreversibly under resolvable uncertainty | Capex timing, product pivots, staged funding |
| 8 | [Prospect Theory](../assets/templates/decision-theory/08-prospect-theory.md) | Predicting human choice with EU | Pricing framing, loss-aversion design, behavioral nudges |
| 9 | [Ellsberg and Allais Paradoxes](../assets/templates/decision-theory/09-ellsberg-allais.md) | Applying EU where ambiguity or certainty effects dominate | Unknown-prior situations, mixed-bet design |
| 10 | [Multi-Armed Bandit](../assets/templates/decision-theory/10-multi-armed-bandit.md) | Fixed allocation ignoring the exploration value | Ad targeting, experiment routing, sequential search |
| 11 | [Stochastic Dominance](../assets/templates/decision-theory/11-stochastic-dominance.md) | Comparing options only at their means | Portfolio comparison, treatment comparison, robust ranking |

---

## Anti-Patterns by Decision Structure

### Single Risky Choice

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Pick highest EV regardless of variance | Risk aversion ignored | Certainty equivalent (#6) — CE = EV only for risk-neutral agents |
| Compare options by most likely outcome | Mode ≠ mean ≠ CE | Use full distribution; check stochastic dominance (#11) |
| Skip the option to wait | Irreversibility not priced | Real options (#7) — value of deferral is positive under resolvable uncertainty |

### Experiment or Study Design

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Approve any study that "might help" | EVPI not checked | EVPI bounds the maximum value; if cost > EVPI, skip (#4) |
| Run full study when a pilot suffices | EVSI for partial sample not computed | EVSI curves show optimal sample size (#4) |
| Run experiment while already knowing the action | Decision is robust to outcomes | Prior expected utility already dominates; no study needed (#4) |

### Multi-Objective Ranking

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Report MCDA ranking without weight disclosure | Weights embed preferences that look like facts | Disclose weight provenance and sensitivity (#5) |
| Accept rank stability without sensitivity check | Small weight perturbations can reverse rankings | Perturb weights ±20% and report rank-reversals (#5) |

### Sequential Decisions

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Fixed per-arm allocation from the start | Foregone learning value | UCB or Thompson sampling adapts; regret is bounded (#10) |
| Exploit immediately after a few observations | Sample variance is high; best arm not identified | Thompson sampling maintains exploration pressure; UCB adjusts confidence bounds (#10) |

---

## Decision Checklist

- [ ] **Probabilistic outcomes**: Are outcomes governed by known or estimable probabilities? → EU (#1)
- [ ] **Evidence arriving sequentially**: Does new data update the action? → Bayesian decision (#2)
- [ ] **Probabilities unknown or contested**: Is the probability distribution itself uncertain? → minimax regret (#3) or Ellsberg handling (#9)
- [ ] **Pre-decision study proposed**: Is information being purchased before acting? → VoI / EVPI (#4) first
- [ ] **Multiple incommensurable criteria**: Are objectives not reducible to a common scale? → MCDA (#5)
- [ ] **Decision maker risk-averse**: Does variance matter beyond the mean? → risk aversion (#6), CE
- [ ] **Irreversible commitment at stake**: Does the action foreclose future options? → real options (#7)
- [ ] **Human behavior to predict or design**: Are actual human choices (not idealized) the target? → prospect theory (#8)
- [ ] **Known EU violations**: Is the choice set one where Allais or Ellsberg effects are likely? → (#9)
- [ ] **Exploration vs. exploitation tradeoff**: Is the reward distribution unknown and learned through pulls? → MAB (#10)
- [ ] **Distribution-level comparison needed**: Is a utility-free dominance check needed? → stochastic dominance (#11)

---

## Sources

Primary sources are the authoritative tier. Textbook treatments are cited for definitions and axioms; practitioner summaries are not cited as primary evidence.

- von Neumann and Morgenstern (1944/1947). Theory of Games and Economic Behavior. Princeton University Press.
- Savage, L. J. (1954). The Foundations of Statistics. Wiley.
- Raiffa, H. and Schlaifer, R. (1961). Applied Statistical Decision Theory. Harvard University Press.
- Howard, R. A. (1966). "Information Value Theory." IEEE Transactions on Systems Science and Cybernetics 2(1).
- Pratt, J. W. (1964). "Risk Aversion in the Small and in the Large." Econometrica 32(1–2).
- Saaty, T. L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
- Kahneman, D. and Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." Econometrica 47(2).
- Ellsberg, D. (1961). "Risk, Ambiguity, and the Savage Axioms." Quarterly Journal of Economics 75(4).
- Allais, M. (1953). "Le comportement de l'homme rationnel devant le risque." Econometrica 21(4).
- Dixit, A. K. and Pindyck, R. S. (1994). Investment under Uncertainty. Princeton University Press.
- Robbins, H. (1952). "Some Aspects of the Sequential Design of Experiments." Bulletin of the AMS 58.
- Auer, P., Cesa-Bianchi, N., and Fischer, P. (2002). "Finite-time Analysis of the Multiarmed Bandit Problem." Machine Learning 47.
- Thompson, W. R. (1933). "On the Likelihood that One Unknown Probability Exceeds Another." Biometrika 25(3–4).
- Russo, D. et al. (2018). "A Tutorial on Thompson Sampling." Foundations and Trends in Machine Learning 11(1).
- Hadar, J. and Russell, W. R. (1969). "Rules for Ordering Uncertain Prospects." American Economic Review 59(1).
- Levy, H. (1992). "Stochastic Dominance and Expected Utility: Survey and Analysis." Management Science 38(4).
- Lattimore, T. and Szepesvári, C. (2020). Bandit Algorithms. Cambridge University Press.
