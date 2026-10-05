# Primitive 5: Regression Discontinuity Design

## Definition

**Regression Discontinuity Design (RDD)** exploits a sharp threshold rule for treatment assignment. Units just above a cutoff c receive treatment; units just below do not. Under the assumption that potential outcomes are continuous through the cutoff, the jump in observed outcomes at c identifies the causal effect.

**Sharp RDD estimand**:
τ_RDD = lim_{x↓c} E[Y | X = x] − lim_{x↑c} E[Y | X = x]

where X is the **running variable** (also called forcing variable or score), and c is the threshold.

**Fuzzy RDD**: when treatment probability jumps at c but is not deterministic (some units above c are untreated; some below are treated), the threshold indicator T = 1(X ≥ c) serves as an instrument for actual treatment D. Fuzzy RDD is an IV at the threshold.

τ_Fuzzy = [lim_{x↓c} E[Y|X=x] − lim_{x↑c} E[Y|X=x]] / [lim_{x↓c} P(D=1|X=x) − lim_{x↑c} P(D=1|X=x)]

**Geographic and time-based variants**: spatial RDD uses geographic boundaries as thresholds; time-based RDD uses policy adoption dates.

## When to Use

- Treatment is determined or strongly predicted by a continuous score crossing a fixed threshold.
- You have enough data near the threshold for local estimation.
- The continuity assumption (no manipulation of the running variable) is plausible.

Common applications: test score cutoffs for admission, age cutoffs for program eligibility, vote share cutoffs for electoral outcomes, income thresholds for benefit programs.

## Inputs / Outputs

**Inputs**: running variable X (continuous, with known cutoff c); treatment indicator D; outcome Y; optional covariates for efficiency.

**Outputs**: local ATE at the cutoff; MSE-optimal bandwidth; robust bias-corrected confidence interval; density test at c; covariate-balance and placebo-cutoff tests.

## Worst Failure Modes

1. **Sorting (manipulation) of the running variable**: if units can control their score to land just above the threshold (e.g., inflate test scores), the continuity assumption fails. Test for a discontinuity in the density of X at c with the local-polynomial density test (Cattaneo, Jansson & Ma 2020; `rddensity`), which supersedes the binned McCrary (2008) test. A null density test does not rule out manipulation that preserves density (e.g., two-sided sorting).
2. **Bandwidth and inference mismatch**: observations far from the cutoff add bias from non-linearity. The MSE-optimal bandwidth is right for the point estimate, but a conventional CI at that bandwidth under-covers because it ignores the leading bias. Report the robust bias-corrected CI (Calonico, Cattaneo & Titiunik 2014; `rdrobust`).
3. **Estimating effects at non-threshold values**: RDD is strictly local. The effect at c tells you nothing about effects for units far from c. Extrapolating to the full population is unjustified.
4. **Other discontinuities at c**: if other policies or events also change at the same threshold, you cannot separate their effects. Pre-register that no other treatment changes at c.
5. **Small sample near the cutoff**: local estimates require sufficient density near c. Low sample sizes near the threshold inflate variance and the estimator may not converge.

## Worked Example

**Setting**: A government scholarship is awarded to students scoring ≥ 70 on a standardized test. Does receiving the scholarship (D) improve graduation rates (Y)? Score (X) is the running variable; cutoff c = 70.

**Data summary (near cutoff)**:

- Students with score 68–69: 200 observations, graduation rate = 0.62
- Students with score 70–71: 210 observations, graduation rate = 0.74

**Naive estimate**: τ_RDD ≈ 0.74 − 0.62 = 0.12 (12 pp)

**Local linear regression** (MSE-optimal bandwidth = 8 points, triangular kernel):

- Fit: Y = α + β(X − 70) + τD + γD(X − 70) + ε
- Point estimate τ̂ = 0.11 (conventional s.e. = 0.04). Do **not** report the conventional 0.11 ± 1.96·0.04 = [0.03, 0.19] interval: at the MSE-optimal bandwidth it under-covers.
- Report the robust bias-corrected interval from `rdrobust`. It is centred on the bias-corrected estimate and is typically wider than the conventional one. Its values come from the software run; this illustration does not invent them.

**Density test**: `rddensity` shows no discontinuity in the running-variable density at 70 (illustrative p = 0.43), so there is no evidence of manipulation. That is not proof of its absence.

**Placebo test**: apply same estimator at c = 60 and c = 80 → estimates of 0.01 and −0.02, neither significant → no spurious jumps elsewhere.

**Interpretation**: among students at the scholarship threshold, the point estimate is ~11 percentage points. Report its uncertainty from the robust bias-corrected interval. The effect is local to the cutoff. All numbers are illustrative.

## Sources

1. Imbens, G. W., & Lemieux, T. (2008). Regression Discontinuity Designs: A Guide to Practice. *Journal of Econometrics*, 142(2), 615–635.
2. Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust Nonparametric Confidence Intervals for Regression-Discontinuity Designs. *Econometrica*, 82(6), 2295–2326.
3. McCrary, J. (2008). Manipulation of the Running Variable in the Regression Discontinuity Design. *Journal of Econometrics*, 142(2), 698–714.
4. Cattaneo, M. D., Jansson, M., & Ma, X. (2020). Simple Local Polynomial Density Estimators. *JASA*, 115(531), 1449–1455.
