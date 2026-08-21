# Causal Inference Primitives — Overview


## Table of Contents

- [Purpose](#purpose)
- [The Causal Hierarchy](#the-causal-hierarchy)
- [Primitive 1: DAGs and Structural Causal Models](#primitive-1-dags-and-structural-causal-models)
- [Primitive 2: Do-Calculus](#primitive-2-do-calculus)
- [Primitive 3: Backdoor and Frontdoor Criteria](#primitive-3-backdoor-and-frontdoor-criteria)
- [Primitive 4: Instrumental Variables](#primitive-4-instrumental-variables)
- [Primitive 5: Regression Discontinuity Design](#primitive-5-regression-discontinuity-design)
- [Primitive 6: Difference-in-Differences](#primitive-6-difference-in-differences)
- [Primitive 7: Synthetic Control](#primitive-7-synthetic-control)
- [Primitive 8: Propensity Score Methods](#primitive-8-propensity-score-methods)
- [Primitive 9: CATE and Uplift Modeling](#primitive-9-cate-and-uplift-modeling)
- [Primitive 10: Simpson's Paradox and Confounding Traps](#primitive-10-simpsons-paradox-and-confounding-traps)
- [Primitive 11: Mediation Analysis](#primitive-11-mediation-analysis)
- [Primitive 12: Sensitivity Analysis](#primitive-12-sensitivity-analysis)
- [Identification Strategies — Decision Map](#identification-strategies--decision-map)
- [Estimand Taxonomy](#estimand-taxonomy)
- [Assumption Inventory](#assumption-inventory)
- [Tooling Landscape](#tooling-landscape)
- [Sources](#sources)

---

## Purpose

This document provides a dense, cross-primitive reference for agents and analysts working with causal inference. It complements `formal-theory-map.md` and `patterns-scenarios-traps.md` by providing:

- a conceptual map of how the primitives relate to each other
- a unified assumption inventory
- an estimand taxonomy
- a decision map for method selection
- conceptual connective tissue across the 12 primitives

Standalone primitive playbooks live under [`../assets/templates/causal-inference/`](../assets/templates/causal-inference/).

---

## The Causal Hierarchy

Causal reasoning operates at three levels (Pearl's Ladder of Causation):

1. **Association** (seeing): P(Y | X = x) — observational. Standard statistics operates here.
2. **Intervention** (doing): P(Y | do(X = x)) — what happens if we force X to x? Requires identification via do-calculus or design.
3. **Counterfactual** (imagining): P(Y_x | X = x', Y = y) — what would Y have been if X had been x, given that X was actually x'? Required for attribution and mediation.

All 12 primitives in this skill address how to move validly from Level 1 data to Level 2 or Level 3 conclusions. Conflating levels is the root cause of most causal inference errors.

---

## Primitive 1: DAGs and Structural Causal Models

A Directed Acyclic Graph (DAG) encodes the analyst's causal assumptions as a set of nodes (variables) and directed edges (direct causal effects). A Structural Causal Model (SCM) augments the DAG with structural equations: X_i = f_i(Pa_i, U_i), where Pa_i are the parents of X_i and U_i is an independent noise term.

**Key concepts:**
- **d-separation**: a graphical criterion for reading off conditional independences from a DAG. Two sets of nodes A and B are d-separated by Z if every path between A and B is blocked by Z.
- **Markov condition**: every variable is independent of its non-descendants given its parents.
- **Faithfulness**: every conditional independence in the data corresponds to a d-separation in the DAG (required for learning DAGs from data).

The DAG is the foundation for all other primitives. Drawing it forces explicit statement of assumptions and identifies which variables are confounders (common causes), mediators (on the causal path), and colliders (common effects).

---

## Primitive 2: Do-Calculus

The do-operator, do(X = x), represents a surgical intervention: set X to x and cut all incoming edges to X in the DAG. The distribution P(Y | do(X = x)) is the interventional distribution sought by causal questions.

**Three rules of do-calculus** (Pearl 2009):
- **Rule 1**: Insertion/deletion of observations: P(Y | do(X), Z, W) = P(Y | do(X), W) if (Y ⊥ Z | X, W) in G_X̄.
- **Rule 2**: Action/observation exchange: P(Y | do(X), do(Z), W) = P(Y | do(X), Z, W) if (Y ⊥ Z | X, W) in G_X̄Z̲.
- **Rule 3**: Deletion of actions: P(Y | do(X), do(Z), W) = P(Y | do(X), W) if (Y ⊥ Z | X, W) in G_X̄Z̄(W).

An effect is **identifiable** if P(Y | do(X)) can be expressed as a function of the observed distribution P using do-calculus. If not identifiable, no observational estimator is consistent.

---

## Primitive 3: Backdoor and Frontdoor Criteria

**Backdoor criterion**: A set Z satisfies the backdoor criterion relative to (X, Y) if:
1. No node in Z is a descendant of X.
2. Z blocks every backdoor path from X to Y (paths with an arrow into X).

If Z satisfies the backdoor criterion: P(Y | do(X)) = Σ_z P(Y | X, Z = z) P(Z = z).

**Frontdoor criterion**: A set M satisfies the frontdoor criterion if:
1. M intercepts all directed paths from X to Y.
2. There are no unblocked backdoor paths from X to M.
3. All backdoor paths from M to Y are blocked by X.

The frontdoor criterion identifies P(Y | do(X)) via the mediator M even when X and Y have unobserved common causes — provided the path X → M → Y is intact and identifiable.

**Minimal adjustment set**: among all valid adjustment sets, use the smallest one to minimize variance and avoid unnecessary conditioning.

---

## Primitive 4: Instrumental Variables

An instrument Z is a variable that:
1. **Relevance**: Z is correlated with the treatment X (first stage).
2. **Exclusion**: Z affects Y only through X (no direct path Z → Y).
3. **Independence**: Z is independent of unobserved confounders U.

Under these assumptions, the IV estimand is:

LATE (Local Average Treatment Effect) = Cov(Y, Z) / Cov(X, Z)

LATE identifies the ATE for **compliers** — units that take treatment when Z = 1 and do not when Z = 0. It does not identify effects for always-takers or never-takers.

**Weak instrument test**: first-stage F-statistic. Rule of thumb: F < 10 indicates weak instruments; use LIML or Anderson-Rubin confidence sets.

---

## Primitive 5: Regression Discontinuity Design

Units just above a threshold get treatment; units just below do not. Under continuity of potential outcomes around the cutoff:

τ_RDD = lim_{x↓c} E[Y | X = x] − lim_{x↑c} E[Y | X = x]

This is a **local** estimand: it identifies the treatment effect only for units at the threshold.

**Sharp RDD**: all units above the cutoff are treated; all below are not.
**Fuzzy RDD**: the probability of treatment jumps at the cutoff but is not deterministic. Fuzzy RDD is an IV where the threshold indicator is the instrument.

**Bandwidth selection**: use MSE-optimal bandwidth (Imbens-Kalyanaraman or Calonico-Cattaneo-Titiunik). Narrower bandwidth → less bias, more variance.

---

## Primitive 6: Difference-in-Differences

DiD compares the change over time in the treated group to the change over time in the control group:

τ_DiD = (Ȳ_T,post − Ȳ_T,pre) − (Ȳ_C,post − Ȳ_C,pre)

**Parallel trends assumption**: in the absence of treatment, the average outcomes for treated and control groups would have followed parallel paths over time. This is untestable for the post-period but can be checked pre-treatment.

**Extensions**:
- **Staggered DiD**: different units adopt treatment at different times. Canonical two-way fixed effects (TWFE) produces a weighted average of all two-group/two-period DiD comparisons (Goodman-Bacon 2021), and those weights can be negative under heterogeneous treatment effects. Use one of the four canonical heterogeneity-robust estimators:
  1. **Callaway & Sant'Anna (2021)**: doubly robust group-time ATTs aggregated across cohorts; accommodates covariates and parallel trends conditional on X.
  2. **Sun & Abraham (2021)**: interaction-weighted estimator; decomposes TWFE coefficients by cohort to eliminate contamination across groups.
  3. **Borusyak, Jaravel & Spiess (2024, *RES*)**: imputation estimator — fit Y(0) on never/not-yet-treated units, impute counterfactuals for treated cells; asymptotically efficient under unrestricted heterogeneity; provides valid pre-trend tests.
  4. **Gardner (2022)**: two-stage DiD — regress Y on unit + time FEs using untreated obs (stage 1), then regress residuals on treatment dummies (stage 2); intuitive and extends naturally to event studies.
  - **Parallel-trends robustness**: pre-trend tests have low power. Use **Rambachan & Roth (2023, *RES*) HonestDiD** to impose restrictions on how much post-treatment violations can exceed pre-treatment violations, producing honest confidence intervals without the binary "pass/fail" pre-test logic. R/Stata `HonestDiD` package.
  - **Known trap (BJS)**: imputation requires no always-treated units; check panel structure before applying.
- **Synthetic DiD (Arkhangelsky et al. 2021, *AER*)**: combines unit weights (synthetic control) with time weights (DiD) to jointly balance pre-treatment outcomes. Inherits SC robustness for few treated units while recovering DiD efficiency when units are many. R package `synthdid`. Prefer over pure SC when staggered treatment and moderate donor pool.
- **Continuous DiD**: treatment dose varies; use interaction-weighted estimator.
- **Estimator choice is setting-dependent.** Baker, Callaway, Cunningham, Goodman-Bacon & Sant'Anna (2026, *JEL*) organizes the design space by target estimand, covariates, weights, and timing structure rather than naming a single best estimator. Pick by what the design identifies, then report the aggregation scheme explicitly — different aggregations of the same group-time ATTs answer different questions.

---

## Primitive 7: Synthetic Control

For a single treated unit, synthetic control constructs a weighted combination of donor units (untreated) that best matches the treated unit's pre-treatment characteristics:

Ŷ_1t(0) = Σ_j w_j Y_jt, where w_j ≥ 0, Σ_j w_j = 1

Weights are chosen to minimize pre-treatment fit. The treatment effect in period t is Y_1t − Ŷ_1t(0).

**Inference**: permutation tests (placebo in space) — apply the same algorithm to every donor unit; the treated unit's effect should be an outlier in the distribution of placebo effects.

**Limitations**: requires a long pre-treatment window and a donor pool with similar pre-treatment outcomes. Not valid when the treated unit is systematically different from all donors.

**Synthetic DiD extension (Arkhangelsky et al. 2021)**: when there are moderately many treated units, SDiD reweights both units (like SC) and time periods (like DiD) to match pre-treatment trajectories. More efficient than pure DiD in many settings; more robust to pre-trends than pure DiD. Prefer SDiD when parallel trends is uncertain and a donor pool is available. R package: `synthdid`.

---

## Primitive 8: Propensity Score Methods

The propensity score is e(x) = P(T = 1 | X = x). Under the **strong ignorability** assumption (Y(0), Y(1) ⊥ T | X), the propensity score is a sufficient balancing score.

**Methods**:
- **Propensity Score Matching (PSM)**: match treated to control units with similar e(x); estimate ATT from matched pairs.
- **Inverse Probability Weighting (IPW)**: weight treated by 1/e(x), control by 1/(1 − e(x)); estimate ATE from weighted regression.
- **Doubly Robust (DR/AIPW)**: combine outcome model and propensity model; consistent if either is correctly specified.

**Overlap (positivity) assumption**: 0 < e(x) < 1 for all x in the support of X. Violation collapses IPW weights.

---

## Primitive 9: CATE and Uplift Modeling

The Conditional Average Treatment Effect: τ(x) = E[Y(1) − Y(0) | X = x].

**Meta-learners**:
- **S-learner**: fit one model on (X, T); τ̂(x) = μ̂(x, 1) − μ̂(x, 0). Simple; can fail to learn heterogeneity if T is regularized away.
- **T-learner**: fit separate models μ̂_1(x) and μ̂_0(x); τ̂(x) = μ̂_1(x) − μ̂_0(x). Variance depends on within-arm sample sizes.
- **X-learner**: uses cross-fitted residuals; better in imbalanced treatment arms (common in observational data).
- **DR-learner / R-learner**: based on Neyman-orthogonal scores; doubly robust to outcome model misspecification.

**Uplift modeling** (in industry/marketing context): τ(x) directly — who responds positively to treatment? Targets the "persuadables" and avoids treating "sure things" and "sleeping dogs."

---

## Primitive 10: Simpson's Paradox and Confounding Traps

Simpson's paradox occurs when a trend present in aggregate data reverses or disappears when data is partitioned by a confounding variable. The paradox arises because naive aggregation conflates association with causation.

**Collider bias**: conditioning on a common effect (collider) of two variables opens a spurious association path between its causes. This is the opposite of confounding. Example: conditioning on "hospitalized" makes severity and another cause appear negatively correlated.

**Mediator conditioning**: adjusting for a mediator on the causal path from X to Y blocks the causal effect and introduces bias.

The DAG is the only reliable guide to which variables to condition on. Rules of thumb (e.g., "always control for more variables") are wrong and dangerous.

---

## Primitive 11: Mediation Analysis

Mediation decomposes the total causal effect of X on Y via a mediator M:

- **Total Effect (TE)**: E[Y(x) − Y(x*)]
- **Natural Direct Effect (NDE)**: E[Y(x, M(x*)) − Y(x*, M(x*))] — effect of X on Y holding M at its natural value under X = x*
- **Natural Indirect Effect (NIE)**: E[Y(x*, M(x)) − Y(x*, M(x*))] — effect of X on Y mediated through M
- **TE = NDE + NIE**

**Required assumptions**: no unmeasured (i) exposure-outcome confounders, (ii) exposure-mediator confounders, (iii) mediator-outcome confounders, and (iv) no exposure-induced confounding of the M-Y relationship.

Assumption (iv) is the most commonly violated. When it fails, use interventional (stochastic) effects or principal stratification.

---

## Primitive 12: Sensitivity Analysis

No observational study fully eliminates unobserved confounding. Sensitivity analysis quantifies how strong confounding would need to be to explain away a finding.

**E-value** (VanderWeele & Ding 2017): the minimum strength of association (on the risk ratio scale) that an unmeasured confounder would need to have with both exposure and outcome to fully explain away the observed association. A large E-value means the finding is robust.

Formula for risk ratio RR:
E-value = RR + √(RR × (RR − 1))

**Rosenbaum bounds**: in matched observational studies, Γ is the maximum odds ratio of treatment assignment that could be due to hidden bias. Test whether conclusions hold for Γ > 1.

**Tipping-point analysis**: how large and prevalent would an unmeasured confounder need to be (in terms of its effects on treatment and outcome) to reduce the estimate to zero or flip the sign?

---

## Identification Strategies — Decision Map

```
Q0: Can one unit's treatment change another unit's outcome?
  YES → SUTVA fails. Fix the design first: cluster/geo randomization (graph or
        market interference), switchback (temporal carryover), or clustered
        switchback (both). Estimate the GLOBAL treatment effect and say so.
  NO  → Continue.

Q1: Is the treatment randomized?
  YES → Use the experimental design directly. Check SUTVA and compliance.
  NO  → Continue.

Q2: Is there a threshold rule for treatment assignment?
  YES → RDD (#5). Check bandwidth and continuity.
  NO  → Continue.

Q3: Is there a valid instrument (relevance + exclusion + independence)?
  YES → IV (#4). Check first-stage F.
  NO  → Continue.

Q4: Is there pre/post data with a comparable untreated group?
  YES → DiD (#6). Check parallel trends.
  NO  → Continue.

Q5: Single treated unit with a pool of untreated donors?
  YES → Synthetic control (#7).
  NO  → Continue.

Q6: All confounders measured?
  YES → Propensity / DR (#8). Check overlap.
  NO  → Sensitivity analysis (#12) required regardless of method; flag unidentified.
```

---

## Estimand Taxonomy

| Estimand | Symbol | Definition | Method |
|----------|--------|------------|--------|
| Average Treatment Effect | ATE | E[Y(1) − Y(0)] | RCT, IPW, DR |
| Average Treatment Effect on the Treated | ATT | E[Y(1) − Y(0) \| T = 1] | DiD, matching |
| Local Average Treatment Effect | LATE | ATE for compliers | IV |
| Local ATE at cutoff | LATE_c | ATE for units at threshold | RDD |
| Conditional ATE | CATE | E[Y(1) − Y(0) \| X = x] | Meta-learners |
| Natural Direct Effect | NDE | E[Y(x, M(x*)) − Y(x*, M(x*))] | Mediation |
| Natural Indirect Effect | NIE | TE − NDE | Mediation |

---

## Assumption Inventory

| Assumption | Methods That Require It | What Breaks When Violated |
|-----------|------------------------|--------------------------|
| Unconfoundedness (strong ignorability) | Propensity (#8), DR | ATE/ATT bias; direction may flip |
| Overlap (positivity) | IPW, DR | Variance explodes; effective sample collapses |
| SUTVA (no interference, single version) | All methods | Spillover contaminates the control group; the unit-level and global treatment effects diverge. Randomization does not repair it — fix the design (cluster, geo, or switchback) |
| Parallel trends | DiD (#6) | ATT estimate captures pre-existing trend, not treatment |
| Pre-treatment fit | Synthetic control (#7) | Donor pool is invalid counterfactual |
| Relevance (strong instrument) | IV (#4) | LIML consistent but OLS-like bias amplifies |
| Exclusion restriction | IV (#4) | IV estimate biased; direction unpredictable |
| Continuity of potential outcomes | RDD (#5) | Local estimate undefined; sorting at threshold |
| No unmeasured confounders | Mediation (#11) | NDE/NIE estimates are biased |

---

## Tooling Landscape

Theory selects the identification strategy; these are the maintained libraries that implement it (current as of mid-2026 — verify version and API against current docs before pinning in production code, per this skill's Fact-Checking policy).

| Primitive(s) | Python | R |
|---|---|---|
| DAG authoring, refutation tests, end-to-end pipeline (#1–#3, #8) | `dowhy` (PyWhy ecosystem; unified graphical + potential-outcomes API, built-in refutation API) | `dagitty` |
| Propensity / DR / CATE meta-learners (#8, #9) | `econml` (Microsoft; DML, meta-learners, policy learning), `causalml` (Uber; uplift-focused meta-learners) | `grf` (generalized random forests, causal forests) |
| Quasi-experimental designs — SC, ITS, DiD, RDD (#5, #6, #7) | `CausalPy` (PyMC-Labs; Bayesian and OLS backends, `effect_summary()` decision-ready output) | `synthdid` (Synthetic DiD), `rdrobust` (RDD bandwidth/inference) |
| Staggered DiD heterogeneity-robust estimators (#6) | `differences`, `csdid` (Python ports) | `did` (Callaway–Sant'Anna), `didimputation` (BJS), `did2s` (Gardner), `eventstudyinteract` (Sun–Abraham) |
| Parallel-trends robustness (#6) | — | `HonestDiD` (Rambachan & Roth) |
| Sensitivity analysis (#12) | `sensemakr` (Python port) | `sensemakr` (Cinelli & Hazlett OVB), `dml.sensemakr` (Chernozhukov et al. ML-OVB), `iv.sensemakr` (IV OVB), `EValue` |
| Interference-aware designs (cluster, geo, switchback) | No maintained general-purpose equivalent; in-house schedulers are the norm | `GeoLift` (Meta; geo market selection + synthetic-control inference, MIT) |

Interference tooling is the least mature area here: there is no maintained general-purpose library for cluster/switchback design and estimation comparable to `dowhy` or `did`. Expect to implement the randomization schedule and the estimator directly from the papers, and validate with simulation on your own data before trusting a launch decision.

**Selection rule**: prefer `dowhy` + `econml` when the pipeline needs an explicit DAG and a refutation step alongside estimation; prefer `CausalPy` when the design is a single quasi-experiment (SC/ITS/DiD/RDD) and Bayesian uncertainty quantification is wanted; prefer the R packages above for DiD and sensitivity work — the staggered-DiD and OVB-sensitivity Python ports lag the R originals in maintenance and feature completeness as of mid-2026, so cross-check R output when the estimate is decision-critical.

## Sources

1. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
2. Imbens, G. W., & Rubin, D. B. (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*. Cambridge University Press.
3. Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press.
4. Athey, S., & Imbens, G. W. (2017). The State of Applied Econometrics: Causality and Policy Evaluation. *Journal of Economic Perspectives*, 31(2), 3–32.
5. Hernán, M. A., & Robins, J. M. (2020). *What If*. Chapman & Hall/CRC.
6. Chernozhukov, V., et al. (2018). Double/Debiased Machine Learning for Treatment and Structural Parameters. *The Econometrics Journal*, 21(1), C1–C68.
7. VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, 167(4), 268–274.
8. Rosenbaum, P. R. (2002). *Observational Studies* (2nd ed.). Springer.
9. Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230.
10. Wager, S., & Athey, S. (2018). Estimation and Inference of Heterogeneous Treatment Effects Using Random Forests. *Journal of the American Statistical Association*, 113(523), 1228–1242.
11. Borusyak, K., Jaravel, X., & Spiess, J. (2024). Revisiting Event-Study Designs: Robust and Efficient Estimation. *Review of Economic Studies*, 91(6), 3253–3285. doi:10.1093/restud/rhae011
12. Rambachan, A., & Roth, J. (2023). A More Credible Approach to Parallel Trends. *Review of Economic Studies*, 90(5), 2555–2591. doi:10.1093/restud/rhad018
13. Roth, J., Sant'Anna, P. H. C., Bilinski, A., & Poe, J. (2023). What's Trending in Difference-in-Differences? A Synthesis of the Recent Econometrics Literature. *Journal of Econometrics*, 235(2), 2218–2244. doi:10.1016/j.jeconom.2022.11.001
14. Sun, L., & Abraham, S. (2021). Estimating Dynamic Treatment Effects in Event Studies with Heterogeneous Treatment Effects. *Journal of Econometrics*, 225(2), 175–199. doi:10.1016/j.jeconom.2020.09.006
15. Goodman-Bacon, A. (2021). Difference-in-Differences with Variation in Treatment Timing. *Journal of Econometrics*, 225(2), 254–277. doi:10.1016/j.jeconom.2021.03.014
16. Arkhangelsky, D., Athey, S., Hirshberg, D. A., Imbens, G. W., & Wager, S. (2021). Synthetic Difference-in-Differences. *American Economic Review*, 111(12), 4088–4118. doi:10.1257/aer.20190159
17. Sant'Anna, P. H. C., & Zhao, J. (2020). Doubly Robust Difference-in-Differences Estimators. *Journal of Econometrics*, 219(1), 101–122. doi:10.1016/j.jeconom.2020.06.003
18. Gardner, J. (2022). Two-Stage Differences in Differences. arXiv:2207.05943.
