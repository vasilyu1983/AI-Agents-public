# Primitive 4: Instrumental Variables

## Definition

An **instrument** Z is a variable satisfying three conditions:
1. **Relevance**: Z is correlated with the treatment X. Formally: Cov(Z, X) ≠ 0.
2. **Exclusion restriction**: Z affects the outcome Y *only* through X. No direct path Z → Y or through an unobserved confounder.
3. **Independence**: Z is independent of unobserved confounders U that affect both X and Y.

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

1. **Weak instruments (low first-stage F)**: when Cov(Z, X) is near zero, the denominator is near zero and tiny errors dominate. Rule of thumb: F < 10 is a weak instrument. Under weak instruments, IV is biased toward OLS and confidence intervals are distorted. Use LIML or Anderson-Rubin confidence sets.
2. **Violated exclusion restriction**: if Z has any direct effect on Y (or through another channel), the exclusion restriction fails and the IV estimate is inconsistent. This assumption is untestable from data alone — it requires domain knowledge.
3. **Instrument not exogenous**: if Z is correlated with U, independence fails. Example: distance to a hospital as an instrument for hospital care is violated if sicker people systematically move closer to hospitals.
4. **Extrapolating LATE to ATE**: LATE identifies effects only for compliers. Compliers may be systematically different from always-takers or never-takers.
5. **Many weak instruments**: adding many instruments improves first-stage fit but can overfit. Use regularized IV methods (JIVE, Lasso-IV) when instruments are numerous.

## Worked Example

**Setting**: Does college education (X) increase earnings (Y)? Unobserved confounders: innate ability and family connections. Instrument: proximity to a college (Z) — affects probability of attending college but has no direct effect on earnings.

**First stage**: Regress X (college attendance) on Z (distance) and controls (family income, local labor market).
- Coefficient on Z: β_1 = −0.12 (closer distance → higher attendance)
- First-stage F = 22.4 → strong instrument

**Second stage**: Regress Y (log earnings) on predicted X̂.
- τ_IV = 0.10 (10% earnings premium per year of college for compliers)

**Comparison**: OLS without IV gives 0.18 — upward bias because high-ability people both attend college and earn more (unobserved ability is a confounder).

**Interpretation**: among people induced to attend college by living near one (compliers), each year of college increases earnings by ~10%.

## Sources

1. Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. Chapter 4.
2. Imbens, G. W., & Angrist, J. D. (1994). Identification and Estimation of Local Average Treatment Effects. *Econometrica*, 62(2), 467–475.
3. Bound, J., Jaeger, D. A., & Baker, R. M. (1995). Problems with Instrumental Variables Estimation When the Correlation Between the Instruments and the Endogenous Explanatory Variable is Weak. *JASA*, 90(430), 443–450.
