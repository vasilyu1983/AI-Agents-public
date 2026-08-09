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

**Outputs**: local ATE at the cutoff; optimal bandwidth; continuity test (density test at c); placebo tests at non-cutoffs; confidence interval.

## Worst Failure Modes

1. **Sorting (manipulation) of the running variable**: if units can control their score to land just above the threshold (e.g., inflate test scores), the continuity assumption fails. Test with the McCrary (2008) density test — look for a discontinuity in the density of X at c.
2. **Bandwidth too wide**: including observations far from the cutoff introduces bias from non-linear relationships between X and Y. Use the Imbens-Kalyanaraman or Calonico-Cattaneo-Titiunik MSE-optimal bandwidth.
3. **Estimating effects at non-threshold values**: RDD is strictly local. The effect at c tells you nothing about effects for units far from c. Extrapolating to the full population is unjustified.
4. **Other discontinuities at c**: if other policies or events also change at the same threshold, you cannot separate their effects. Pre-register that no other treatment changes at c.
5. **Small sample near the cutoff**: local estimates require sufficient density near c. Low sample sizes near the threshold inflate variance and the estimator may not converge.

## Worked Example

**Setting**: A government scholarship is awarded to students scoring ≥ 70 on a standardized test. Does receiving the scholarship (D) improve graduation rates (Y)? Score (X) is the running variable; cutoff c = 70.

**Data summary (near cutoff)**:

- Students with score 68–69: 200 observations, graduation rate = 0.62
- Students with score 70–71: 210 observations, graduation rate = 0.74

**Naive estimate**: τ_RDD ≈ 0.74 − 0.62 = 0.12 (12 pp)

**Local linear regression** (MSE-optimal bandwidth = 8 points):

- Fit: Y = α + β(X − 70) + τD + γD(X − 70) + ε
- τ̂ = 0.11 (s.e. = 0.04), 95% CI: [0.03, 0.19]

**Density test**: McCrary test shows no discontinuity in the running variable density at 70 (p = 0.43) → no evidence of manipulation.

**Placebo test**: apply same estimator at c = 60 and c = 80 → estimates of 0.01 and −0.02, neither significant → no spurious jumps elsewhere.

**Interpretation**: among students just at the scholarship threshold, receiving the scholarship increases graduation probability by ~11 percentage points.

## Sources

1. Imbens, G. W., & Lemieux, T. (2008). Regression Discontinuity Designs: A Guide to Practice. *Journal of Econometrics*, 142(2), 615–635.
2. Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust Nonparametric Confidence Intervals for Regression-Discontinuity Designs. *Econometrica*, 82(6), 2295–2326.
3. McCrary, J. (2008). Manipulation of the Running Variable in the Regression Discontinuity Design. *Journal of Econometrics*, 142(2), 698–714.
