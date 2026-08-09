# Primitive: Weibull Analysis

## Definition

The **Weibull distribution** is the most widely used lifetime distribution in reliability engineering because a single two-parameter family can model decreasing, constant, and increasing failure rates by varying the shape parameter β.

```
Weibull PDF:         f(t) = (β/η)(t/η)^(β-1) exp(-(t/η)^β)
Reliability:         R(t) = exp(-(t/η)^β)
Hazard function:     h(t) = (β/η)(t/η)^(β-1)
CDF (unreliability): F(t) = 1 - exp(-(t/η)^β)
```

| Parameter | Name | Interpretation |
|-----------|------|----------------|
| β (beta) | Shape parameter | Controls failure rate shape: β<1 DFR, β=1 CFR, β>1 IFR |
| η (eta) | Scale / characteristic life | Time at which 63.2% of units have failed, regardless of β |
| γ (gamma) | Location / threshold (optional 3-param) | Earliest possible failure time; often set to 0 |

**β = 1 recovers the exponential distribution.** MTBF = η for β = 1; otherwise MTBF = η × Γ(1 + 1/β).

## When to Use

- Fitting a distribution to observed failure time data, especially when failures are not exponentially distributed.
- Estimating MTBF, B10 life (time at which 10% have failed), or any Bx percentile.
- Classifying current operating phase (DFR / CFR / IFR) from field data — feeds into bathtub analysis (primitive 04).
- Planning maintenance intervals from predicted Bx percentiles.
- Comparing reliability of two designs from accelerated-life test data.

## Inputs

| Input | Description |
|-------|-------------|
| Failure times | Times-to-failure for individual units or events |
| Suspension times | Run-times of units that have not yet failed (right-censored) |
| Test environment | Accelerated stress level (temperature, voltage) if applicable |

## Outputs

- β and η estimates with confidence intervals.
- Reliability R(t) at any mission time t.
- Bx life: time at which x% of units fail.
- Goodness-of-fit statistic (Kolmogorov-Smirnov or correlation coefficient on Weibull probability plot).

## Estimation Methods

### Method of Maximum Likelihood Estimation (MLE)

Preferred when censored data are present. Solves:

```
Σᵢ [ln(tᵢ) - (1/β) - Σⱼ tⱼ^β ln(tⱼ) / Σⱼ tⱼ^β] = 0   [for β]
η = (Σᵢ tᵢ^β / n)^(1/β)
```

Use numerical solver; confidence intervals via Fisher information matrix.

### Probability Plot (Median Rank Regression)

1. Sort failure times in ascending order.
2. Assign median rank F(tᵢ) ≈ (i - 0.3) / (n + 0.4).
3. Plot ln(tᵢ) vs. ln(-ln(1 - F(tᵢ))) — should be linear for Weibull.
4. β = slope, η = exp(-intercept/slope).

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Fitting Weibull to fewer than 6–10 complete failures | β and η estimates have very wide confidence intervals; unreliable | Report confidence intervals explicitly; collect more data or use Bayesian priors |
| Ignoring suspended (right-censored) data | Survivorship bias underestimates hazard and overestimates MTBF | Include suspensions in MLE; do not drop unfailed units from analysis |
| Using the 2-parameter model when a threshold γ > 0 exists | Systematic curvature on probability plot; poor fit | Fit 3-parameter Weibull or investigate the physical reason for the threshold |
| Reporting MTBF without noting β | MTBF from a Weibull IFR system is a misleading average of a rising hazard | Report β alongside MTBF; for β > 1.5, report B10 life instead of MTBF |
| Assuming a single Weibull fits a mixed-failure-mode population | Bimodal probability plot; β is meaningless | Separate competing failure modes; fit separate distributions to each |

## Worked Example

A server hard drive fleet: 50 drives, 12 failures recorded, 38 right-censored at various operating times.

**MLE estimates** (from Weibull++ or scipy.stats.weibull_min):

```
β = 2.4    (IFR — wear-out mode confirmed)
η = 4,380 days  (~12 years characteristic life)

B10 life = η × (-ln(1 - 0.10))^(1/β)
         = 4,380 × (0.1054)^(1/2.4)
         ≈ 4,380 × 0.3915
         ≈ 1,715 days  (~4.7 years: 10% failed by here)

MTBF = η × Γ(1 + 1/β) = 4,380 × Γ(1.417) ≈ 4,380 × 0.886 ≈ 3,880 days
```

**Maintenance recommendation**: replace drives proactively by day 1,715 (~4.7 years) — the B10 life — to keep expected cumulative failures at or below 10% of the fleet. At day 1,200 (~3.3 years) cumulative failures are only ≈4.4%; pulling the replacement date that early trades cost for negligible risk reduction. Waiting to 4,380 days (η, the characteristic life) allows 63% cumulative failures — unacceptable for production storage. (Corrected 2026-07-11: the previous version of this example mis-derived the (0.1054)^(1/2.4) term as ≈0.291 instead of ≈0.3915, understating B10 life by roughly 25% and understating the day-1,200 cumulative failure fraction.)

## Sparse Data Note

When failure observations are expensive to obtain — e.g., evaluating LLM agent reliability from test runs, or running destructive hardware tests — adaptive sampling designs can reduce the required sample size **3–5×** while maintaining valid confidence intervals. Factorized Active Querying (FAQ; Wu, Nair & Candès 2026) frames evaluation as finite-population inference and uses Bayesian factor modelling plus active-learning question selection to achieve this gain. The methodology is a statistical parallel to the reliability-estimation problem: wherever uniform sampling of failures is expensive, adaptive designs that leverage historical data and selectively query high-variance items produce tighter CIs from fewer observations. (Code: https://github.com/skbwu/efficiently-evaluating-llms.) Note: validated on NLP benchmarks; transfer to hardware or field reliability contexts is adjacent but not directly replicated.

## Sources

- Weibull, W. (1951). A statistical distribution function of wide applicability. *Journal of Applied Mechanics*, 18(3), 293–297.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer. Appendix A.
- Wu, S., Nair, Y., & Candès, E. J. (2026). Efficient Evaluation of LLM Performance with Statistical Guarantees. arXiv:2601.20251.
