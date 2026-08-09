---
description: Formal theory map for causal-inference foundations. Use to separate identification assumptions from estimation mechanics.
last_verified: 2026-05-02
status: stable
---

# Causal Inference Formal Theory Map

## Purpose

Use this map when a causal recommendation needs an explicit estimand, identification strategy, or assumption boundary. Causal inference fails most often when teams estimate a number before proving what that number identifies.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Structural causal models | DAGs, structural equations, exogenous noise, do-operator | Graph assumptions, backdoor/frontdoor, do-calculus | Graph is an assumption set, not learned truth by default |
| Potential outcomes | Y(1), Y(0), SUTVA, ignorability, compliance | ATE, ATT, LATE, RDD, DiD, matching | Counterfactuals are not jointly observed |
| Identification theory | Expressing causal effects via observed distributions | Do-calculus, adjustment, frontdoor, IV logic | If unidentified, better ML cannot fix it |
| Quasi-experimental design | Thresholds, timing shocks, donor pools, instruments | RDD, DiD, synthetic control, IV | Local assumptions determine external validity |
| Observational adjustment | Propensity score, IPW, matching, DR estimation | Covariate balance under measured confounding | Requires overlap and no unmeasured confounding |
| Heterogeneous effects | CATE, policy value, orthogonal scores | Uplift, subgroup targeting, policy learning | Extrapolation outside support is invalid |
| Mediation | Natural direct/indirect effects, path-specific effects | Mechanism attribution | Requires strong cross-world assumptions or alternatives |
| Sensitivity analysis | E-values, Rosenbaum bounds, tipping points | Robustness to hidden bias | Does not identify the effect; it quantifies fragility |

## Applied Primitive Coverage

| Primitive | Formal Backbone | Must Check Before Use |
|---|---|---|
| DAGs/SCMs | Markov condition, d-separation, structural equations | Confounders, colliders, mediators, time order |
| Do-calculus | Rules for interventions in modified graphs | Identifiability before estimation |
| Backdoor/frontdoor | Graphical adjustment criteria | Minimal valid adjustment set |
| Instrumental variables | Relevance, exclusion, independence, monotonicity | First stage, exclusion story, LATE population |
| Regression discontinuity | Continuity at threshold | Sorting/manipulation, bandwidth, local estimand |
| Difference-in-differences | Parallel trends and no anticipation | Pre-trends, staggered adoption, heterogeneous effects |
| Synthetic control | Weighted donor counterfactual | Pre-treatment fit and donor validity |
| Propensity methods | Balancing score theorem | Overlap, covariate balance, unmeasured confounding |
| CATE/uplift | Conditional potential outcomes | Cross-fitting, support, subgroup power |
| Simpson/confounding traps | Aggregation and conditioning logic | DAG before stratification |
| Mediation | Counterfactual pathway decomposition | Post-treatment confounding and mediator timing |
| Sensitivity analysis | Hidden-bias bounds | Plausible confounder strength and reporting scale |

## Production Rule

Every causal claim needs four artifacts before modeling: estimand, DAG or design diagram, identification assumptions, and sensitivity plan. Without all four, the result is an association report.
