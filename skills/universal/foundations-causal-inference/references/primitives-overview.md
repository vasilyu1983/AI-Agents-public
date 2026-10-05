# Causal Inference Primitives — Overview


## Table of Contents

- [Purpose](#purpose)
- [The Causal Hierarchy](#the-causal-hierarchy)
- [Operational Notes by Primitive](#operational-notes-by-primitive)
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

Association P(Y|X), intervention P(Y|do(X)) and counterfactual P(Y_x|X=x',Y=y) are different targets (Pearl's Ladder). Every primitive here moves from level-1 data to a level-2 or level-3 claim; conflating levels is the root cause of most errors.

---

## Operational Notes by Primitive

Definitions and worked examples live in the per-primitive templates. This section keeps only the non-obvious rules.

| # | Primitive | Operational note |
|---|---|---|
| 1 | DAG / SCM | The graph is an assumption set; faithfulness is needed only to *learn* a DAG from data, not to use one. |
| 2 | Do-calculus | If P(Y\|do(X)) is not identifiable, no observational estimator is consistent; better ML does not help. |
| 3 | Backdoor / frontdoor | Minimal means no removable member, not minimum variance. Extra valid outcome-predictive covariates can improve precision; treatment-only predictors can hurt it. Never add colliders or inappropriate descendants. |
| 4 | IV | Binary encouragement/treatment LATE needs relevance, exclusion, independence and monotonicity (no defiers). **Strength:** with one instrument, do not gate on F > 10 — a true 5% t-test needs F > 104.7, and at F = 10 the valid critical value is 3.43 (Lee, McCrary, Moreira & Porter, *AER* 2022); use Anderson–Rubin intervals or the tF adjustment. With several instruments, report the effective F (Montiel Olea & Pflueger 2013) and use weak-IV-robust (AR-type) inference; the 104.7/tF results are single-instrument and do not extend (review: Andrews, Stock & Sun 2019; check the over-identified procedure for your setting against that review). LIML is not a universal cure. |
| 5 | RDD | Choose an MSE-optimal bandwidth for the point estimate, but report the **robust bias-corrected** interval (Calonico, Cattaneo & Titiunik 2014; `rdrobust`) — the conventional CI at the MSE-optimal bandwidth under-covers. Test manipulation with the local-polynomial density test (Cattaneo, Jansson & Ma 2020; `rddensity`). Fuzzy RDD is IV at the cutoff and inherits the weak-IV rules. |
| 6 | DiD | Staggered adoption: The Goodman-Bacon (2021) decomposition assigns non-negative weights to 2×2 comparisons. Already-treated comparisons can subtract changing effects, yielding negative weights on underlying treatment effects when effects vary over time. Use Callaway–Sant'Anna (DR group-time ATTs), Sun–Abraham (interaction-weighted, binary staggered), BJS imputation (needs no always-treated units) or Gardner two-stage. Pre-trend tests have low power; use HonestDiD (Rambachan & Roth 2023). **Continuous dose:** under the usual parallel trends, ATT-type parameters at each dose are identified, but comparisons *across* doses carry selection bias; causal dose-response comparisons need a stronger parallel-trends assumption (Callaway, Goodman-Bacon & Sant'Anna, NBER w32117, 2024). When every unit's dose changes between periods ("no stayers"), see de Chaisemartin, D'Haultfœuille & Vazquez-Bare (2024, *AEA P&P* 114). Estimator choice is setting-dependent (Baker et al. 2026, *JEL*); report the aggregation scheme. |
| 7 | Synthetic control / SDiD | Weights are non-negative and sum to 1, so the counterfactual cannot leave the donors' convex hull. Inspect the weight vector, not only RMSPE. Inference is placebo-in-space (rank of post/pre MSPE ratio). SDiD (Arkhangelsky et al. 2021) adds time weights; its canonical implementation assumes block timing. |
| 8 | Propensity / IPW / DR | Balance on observed covariates says nothing about unobserved ones. Positivity failure is structural when a subgroup can never be treated; trimming changes the estimand. |
| 9 | CATE / uplift | X-learner for imbalanced arms; DR-learner has the either-nuisance-correct property; R-learner orthogonality alone does not. Evaluate targeting policy value on held-out data. |
| 10 | Simpson / confounding traps | Stratify by the DAG, not by "more controls". Conditioning on a common effect opens a spurious path. |
| 11 | Mediation | TE = pure NDE + total NIE; with exposure-mediator interaction the pure NIE needs the complementary total NDE. Exposure-induced mediator-outcome confounding is the usual failure; switch to interventional effects or report the total effect. |
| 12 | Sensitivity | E-value = RR + √(RR(RR−1)) applies to risk ratios (or justified conversions) only; continuous outcomes use partial-R²/OVB (`sensemakr`); matched designs use Rosenbaum Γ; DiD uses HonestDiD. |

---

## Identification Strategies — Decision Map

```
Q0: Can one unit's treatment change another unit's outcome?
  YES → Define exposure mapping, target contrast and assignment support.
        Use design-compatible estimation if identified; otherwise consider
        cluster/geo randomization, switchback or clustered switchback.
        Do not assume the identified contrast equals the global launch effect.
  NO  → Continue.

Q1: Is the treatment randomized?
  YES → Use the experimental design directly. Check SUTVA and compliance.
  NO  → Continue.

Q2: Is there a threshold rule for treatment assignment?
  YES → RDD (#5). Density test, robust bias-corrected CI.
  NO  → Continue.

Q3: Is there a valid instrument (relevance + exclusion + independence)?
  YES → IV (#4). Weak-IV-robust inference (AR/tF for one instrument;
        effective F + AR-type for several), not an F > 10 gate.
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
        Consider negative controls, bounds, or the designs in
        beyond-canonical-designs.md (ITS, OPE, surrogate index).
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
| No-interference / treatment-version consistency | Conventional unit-level formulas; explicit interference models relax no-interference | Define exposure mapping, assignment support and direct/indirect/total/global contrast; a direct effect need not equal global rollout. Use a design-compatible estimator or redesign if the target lacks support |
| Parallel trends | DiD (#6) | ATT estimate captures pre-existing trend, not treatment |
| Pre-treatment fit | Synthetic control (#7) | Donor pool is invalid counterfactual |
| Relevance (strong instrument) | IV (#4) | 2SLS is biased toward OLS and conventional t-tests over-reject; use AR or tF inference |
| Exclusion restriction | IV (#4) | IV estimate biased; direction unpredictable |
| Continuity of potential outcomes | RDD (#5) | Local estimate undefined; sorting at threshold |
| No unmeasured confounders | Mediation (#11) | NDE/NIE estimates are biased |

---

## Tooling Landscape

Select the identification strategy first, then check the current official documentation for the estimator, supported design, inference API, release and maintenance status before choosing or pinning a package:

- DAG and refutation workflows: [DoWhy](https://www.pywhy.org/dowhy/).
- CATE, DML and policy estimation: [EconML](https://www.pywhy.org/EconML/) and [GRF](https://grf-labs.github.io/grf/).
- Quasi-experimental workflows: [CausalPy](https://causalpy.readthedocs.io/); verify support for the particular design and uncertainty calculation rather than assuming a shared summary API.
- Group-time DiD: [R did](https://bcallaway11.github.io/did/); verify comparison groups, aggregation and inference options.
- Other R estimators and sensitivity packages: look up the package manual and release history in [CRAN](https://cran.r-project.org/), including `rdrobust`, `synthdid`, `HonestDiD`, `sensemakr` and `EValue` as relevant.
- Interference designs: verify that a candidate implementation matches the paper’s exposure mapping, randomization schedule, carryover assumptions and estimator. Test it by simulation for the intended design; package availability alone does not establish identification.

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
19. Lee, D. S., McCrary, J., Moreira, M. J., & Porter, J. (2022). Valid t-ratio Inference for IV. *American Economic Review*, 112(10), 3260–3290. doi:10.1257/aer.20211063
20. Montiel Olea, J. L., & Pflueger, C. (2013). A Robust Test for Weak Instruments. *Journal of Business & Economic Statistics*, 31(3), 358–369. doi:10.1080/00401706.2013.806694
21. Andrews, I., Stock, J. H., & Sun, L. (2019). Weak Instruments in Instrumental Variables Regression: Theory and Practice. *Annual Review of Economics*, 11, 727–753. doi:10.1146/annurev-economics-080218-025643
22. Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust Nonparametric Confidence Intervals for Regression-Discontinuity Designs. *Econometrica*, 82(6), 2295–2326. doi:10.3982/ECTA11757
23. Cattaneo, M. D., Jansson, M., & Ma, X. (2020). Simple Local Polynomial Density Estimators. *JASA*, 115(531), 1449–1455. doi:10.1080/01621459.2019.1635480
24. Callaway, B., Goodman-Bacon, A., & Sant'Anna, P. H. C. (2024). Difference-in-Differences with a Continuous Treatment. NBER Working Paper 32117.
25. de Chaisemartin, C., D'Haultfœuille, X., & Vazquez-Bare, G. (2024). Difference-in-Difference Estimators with Continuous Treatments and No Stayers. *AEA Papers and Proceedings*, 114, 610–613. doi:10.1257/pandp.20241049
