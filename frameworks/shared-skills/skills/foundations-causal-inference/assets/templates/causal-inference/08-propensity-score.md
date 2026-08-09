# Primitive 8: Propensity Score Methods

## Definition

The **propensity score** is e(x) = P(T = 1 | X = x) — the conditional probability of treatment given observed covariates X.

**Key theorem** (Rosenbaum & Rubin 1983): under **strong ignorability** (Y(0), Y(1) ⊥ T | X), the propensity score is a sufficient balancing score: (Y(0), Y(1)) ⊥ T | e(X). It is sufficient to balance on e(X) rather than the full X.

**Methods**:

**Propensity Score Matching (PSM)**: for each treated unit, find one or more control units with similar e(x). Estimate ATT from matched pairs.

**Inverse Probability Weighting (IPW)**: weight treated units by 1/e(x) and control units by 1/(1−e(x)). The weighted sample mimics a randomized experiment. IPW estimator for ATE:
τ̂_IPW = (1/n) Σ_i [T_i Y_i / e(X_i) − (1−T_i) Y_i / (1−e(X_i))]

**Augmented IPW / Doubly Robust (DR/AIPW)**: combines an outcome model μ̂(x, t) with the propensity model. Consistent if *either* the outcome model or the propensity model is correctly specified (not both need to be correct):
τ̂_DR = τ̂_IPW + correction term from outcome model residuals

**Overlap (positivity) assumption**: 0 < e(x) < 1 for all x in the support. Violation means some units have zero probability of one treatment status — their counterfactuals are not identified.

## When to Use

- Observational data with measured confounders.
- No valid instrument, discontinuity, or pre-post structure available.
- Strong ignorability assumption is defensible (all important confounders are measured).
- Estimand is ATE (IPW) or ATT (matching, ATT-IPW).

Do not use propensity methods when there are important unmeasured confounders — the method will produce precise but biased estimates.

## Inputs / Outputs

**Inputs**: treatment indicator T; outcome Y; covariates X; choice of estimand (ATE or ATT); propensity model (logistic regression, GBM, BART, or cross-fitted ML).

**Outputs**: estimated ATE or ATT; overlap diagnostics (propensity score histograms; effective sample size); covariate balance table (standardized mean differences before and after weighting); confidence intervals (bootstrap or influence function).

## Worst Failure Modes

1. **Overlap failure**: when treated and control units have non-overlapping covariate distributions, extreme propensity scores produce IPW weights near infinity. Trim weights at a maximum (e.g., 10) or clip propensity scores at 0.05/0.95.
2. **Strong ignorability violated (unmeasured confounders)**: propensity methods only control for *measured* confounders. If important confounders are unmeasured, the estimate is biased regardless of how well propensity is modeled.
3. **Post-treatment covariate inclusion**: including variables measured after treatment assignment inflates or deflates the propensity score. Only use pre-treatment variables.
4. **Matching on the wrong features**: propensity score alone may not fully balance covariates in finite samples. Check covariate balance explicitly (standardized mean differences < 0.1 after matching).
5. **Using PSM as a substitute for IV or RDD when unmeasured confounders exist**: propensity methods do not solve the problem of unobserved confounding. Use sensitivity analysis (#12) to quantify exposure.

## Worked Example

**Setting**: Does a job training program (T) increase 1-year earnings (Y)? Observed confounders: age, education, prior earnings, employment history.

**Step 1: Estimate propensity score** via logistic regression on age, education, prior earnings, employment status.

**Step 2: Check overlap**:
- Propensity score range for treated: [0.12, 0.87]
- Propensity score range for control: [0.04, 0.91]
- Overlap is adequate; no trimming needed

**Step 3: IPW ATE estimate**:
- Weighted mean outcome (treated): 24,500
- Weighted mean outcome (control): 21,800
- τ̂_IPW = 2,700 (s.e. = 820 via bootstrap)

**Step 4: DR correction** (adds outcome regression residual correction):
- τ̂_DR = 2,850 (s.e. = 750) — more efficient than IPW

**Step 5: Balance check**:
- Before weighting: standardized mean difference for prior earnings = 0.38 (imbalanced)
- After IPW weighting: standardized mean difference = 0.04 (balanced)

**Interpretation**: job training increased 1-year earnings by approximately $2,850, controlling for observed confounders. Sensitivity analysis (E-value = 2.1) indicates the conclusion requires a moderately strong unmeasured confounder to be overturned.

## Sources

1. Rosenbaum, P. R., & Rubin, D. B. (1983). The Central Role of the Propensity Score in Observational Studies for Causal Effects. *Biometrika*, 70(1), 41–55.
2. Imbens, G. W., & Rubin, D. B. (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*. Cambridge University Press. Chapters 12–14.
3. Chernozhukov, V., et al. (2018). Double/Debiased Machine Learning for Treatment and Structural Parameters. *The Econometrics Journal*, 21(1), C1–C68.
