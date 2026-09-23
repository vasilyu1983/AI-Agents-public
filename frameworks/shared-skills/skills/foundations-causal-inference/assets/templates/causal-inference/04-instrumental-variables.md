# Primitive 4: Instrumental Variables

## Definition

An **instrument** Z is a variable satisfying the following conditions for the usual binary-instrument, binary-treatment LATE:
1. **Relevance**: Z is correlated with the treatment X. Formally: Cov(Z, X) ≠ 0.
2. **Exclusion restriction**: Z affects the outcome Y *only* through X. No direct path Z → Y or through an unobserved confounder.
3. **Independence**: Z is independent of relevant potential outcomes and treatment responses, possibly conditional on baseline covariates.
4. **Monotonicity/no defiers**: X(1) >= X(0), with consistency and a nonzero first stage. Continuous instruments/treatments require their own interpretation and assumptions.

Under these conditions, the IV estimand is:

τ_IV = Cov(Y, Z) / Cov(X, Z)

In the two-stage least squares (2SLS) implementation:
- **First stage**: regress X on Z (and any controls). Predict X̂.
- **Second stage**: regress Y on X̂ (and controls). The coefficient on X̂ is the IV estimate.

**What IV identifies**: the **Local Average Treatment Effect (LATE)** — the ATE for **compliers** only (units that change treatment status in response to Z). It does not identify effects for always-takers or never-takers.

## When to Use

- Treatment assignment is non-random with unobserved confounders.
- A valid instrument exists (from randomization, natural variation, policy rules, or geographic discontinuities).
- LATE for compliers is the estimand of interest (or compliers are a relevant subpopulation).

Common instruments: randomized encouragement to take up a program, distance to a facility, lottery assignment, quarter of birth, policy change affecting only some groups.

## Inputs / Outputs

**Inputs**: treatment variable X, outcome Y, instrument Z, optional control variables W; sample size adequate for first-stage power.

**Outputs**: IV estimate of LATE; first-stage F-statistic; second-stage standard errors (must account for first-stage estimation); 95% confidence interval.

## Worst Failure Modes

1. **Weak instruments (low first-stage F)**: when Cov(Z, X) is near zero, the denominator is near zero and tiny errors dominate. F<10 is a historical heuristic for some conventional designs, not a universal strength or validity certificate. Use design-appropriate weak-instrument diagnostics and robust inference (e.g., justified Anderson-Rubin sets); heteroskedasticity, clustering, instrument count and estimator matter. LIML can reduce some finite-sample bias but is not a universal cure.
2. **Violated exclusion restriction**: if Z has any direct effect on Y (or through another channel), the exclusion restriction fails and the IV estimate is inconsistent. This assumption is untestable from data alone — it requires domain knowledge.
3. **Instrument not exogenous**: if Z is correlated with U, independence fails. Example: distance to a hospital as an instrument for hospital care is violated if sicker people systematically move closer to hospitals.
4. **Extrapolating LATE to ATE**: LATE identifies effects only for compliers. Compliers may be systematically different from always-takers or never-takers.
5. **Many weak instruments**: adding many instruments improves first-stage fit but can overfit. Use regularized IV methods (JIVE, Lasso-IV) when instruments are numerous.

## Worked Example

**Illustrative binary encouragement design:** X=1 means attending college, X=0 means not attending; Z=1 is randomized encouragement and Z=0 is no encouragement. Y is log earnings. Randomization supports independence, but exclusion (encouragement affects earnings only through attendance), no defiers, consistency/no relevant interference and a nonzero first stage must still be justified. An encouragement that directly provides job contacts would violate exclusion.

**First stage:** Attendance probability is .60 under encouragement and .40 without: difference .20. **Reduced form:** Mean log earnings differ by .02. The Wald estimate is .02/.20=.10 log points, an attendance-versus-no-attendance LATE for encouragement compliers, not an effect per year of college. The usual approximate proportional interpretation is 10%; exp(.10)−1≈10.52% is the log-scale conversion, not automatically the mean level-earnings ATE.

Report the first-stage estimate/uncertainty and design-appropriate weak-IV robust interval. An illustrative F=22.4 alone proves neither exclusion nor adequate strength for every design. OLS-IV differences alone do not prove ability bias or its direction. No effect is extrapolated to always-takers, never-takers, years of education, or all students.

## Sources

1. Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. Chapter 4.
2. Imbens, G. W., & Angrist, J. D. (1994). Identification and Estimation of Local Average Treatment Effects. *Econometrica*, 62(2), 467–475.
3. Bound, J., Jaeger, D. A., & Baker, R. M. (1995). Problems with Instrumental Variables Estimation When the Correlation Between the Instruments and the Endogenous Explanatory Variable is Weak. *JASA*, 90(430), 443–450.
