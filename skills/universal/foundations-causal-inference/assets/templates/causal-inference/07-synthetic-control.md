# Primitive 7: Synthetic Control

## Definition

**Synthetic control** constructs a weighted combination of untreated units (the **donor pool**) that best matches the treated unit's pre-treatment characteristics. The synthetic control serves as the counterfactual for what the treated unit would have experienced absent treatment.

**Weights**: w = (w_1, ..., w_J) with w_j ≥ 0, Σw_j = 1, chosen to minimize:

‖X_1 − X_0 W‖_V

where X_1 is the pre-treatment predictor vector for the treated unit, X_0 is the predictor matrix for donor units, and V is a matrix weighting predictors by importance.

**Treatment effect in period t**:
α̂_{1t} = Y_{1t} − Ŷ_{1t}(0) = Y_{1t} − Σ_j w_j Y_{jt}

The treatment effect is the gap between the treated unit's actual outcome and the synthetic control's outcome.

**Inference**: permutation tests (placebo-in-space). Apply the same algorithm to every donor unit; compute their placebo gaps. The treated unit's effect is significant if it is an outlier in the distribution of placebo effects (pre-treatment RMSPE ratio).

## When to Use

- One or a small number of treated units (countries, regions, firms, stores).
- Long pre-treatment time series available (typically ≥ 10–20 pre-periods).
- A pool of untreated donor units exists.
- The treated unit's outcome is not clearly matched by any single donor unit (otherwise DiD is sufficient).

Common applications: policy evaluations (trade liberalization, tax reforms), major interventions in a single market, platform feature rollouts in a single country.

## Inputs / Outputs

**Inputs**: balanced panel data for the treated unit and donor pool; pre-treatment outcome values and predictor variables; the intervention date T_0.

**Outputs**: optimal donor weights; pre-treatment fit (RMSPE); post-treatment synthetic control trajectory (counterfactual); treatment effect estimates per post-treatment period; permutation p-values from placebo tests.

## Worst Failure Modes

1. **Poor pre-treatment fit**: if the synthetic control cannot reproduce the treated unit's pre-treatment trajectory, the counterfactual is unreliable. Report pre-treatment RMSPE. If it is high relative to donor units' RMSPE, the method may not apply.
2. **Interference among donor units**: if the treatment spills over to donor units (e.g., a country's trade policy change affects trading partners in the donor pool), the donor units are contaminated. Exclude directly affected donors.
3. **Interpolation extrapolation outside the donor pool's convex hull**: synthetic control cannot extrapolate beyond the range of donor outcomes. Verify that the treated unit's pre-treatment values fall within the donor pool's range.
4. **Overfitting the pre-treatment period**: with many predictor variables and few donors, weights can fit noise. Use only outcome lags and a small set of pre-treatment predictors.
5. **Short pre-treatment window**: with fewer than ~10 pre-treatment periods, the permutation distribution has low resolution and p-values are coarse.

## Worked Example

**Setting** (Abadie, Diamond & Hainmueller 2010): California passed Proposition 99, a large-scale tobacco control program, in 1988. Did it reduce per-capita cigarette sales (Y, packs)? Treated unit: California. Donor pool: 38 states. States with their own large tobacco programs or big cigarette-tax increases in the period were excluded.

**Predictors**: the 1980–1988 averages of retail cigarette price, log per-capita personal income, percentage of the population aged 15–24, and per-capita beer consumption. They are augmented with lagged cigarette sales for 1975, 1980 and 1988. Outcome data run from 1970 to 2000.

**Donor weights (paper, Table 2)**:

| State | Weight |
|---|---|
| Colorado | 0.164 |
| Connecticut | 0.069 |
| Montana | 0.199 |
| Nevada | 0.234 |
| Utah | 0.334 |
| All other donors | 0 |
| **Sum** | **1.000** |

Check Σw = 1 and w ≥ 0 on any reported weight vector. A vector that sums to 1.009, or has a negative entry, is a transcription error or not a synthetic control.

**Pre-treatment fit**: the paper reports a pre-Proposition-99 mean squared prediction error (MSPE) of about 3 for California. The median across the 38 donor states' own synthetic controls is about 6.

**Post-treatment gap (1989–2000)**: the paper estimates that cigarette consumption fell by "an average of almost 20 packs per capita, a decline of approximately 25%".

**Permutation test**: the same algorithm is applied to each donor state. Ranked by the ratio of post- to pre-period MSPE, California is the most extreme of the 39 units. The permutation p-value is 1/39 ≈ 0.026. This is the smallest p-value 38 donors can produce, so a larger donor pool is needed for finer resolution.

**Interpretation**: the gap is California's post-1988 effect relative to a convex combination of five states. It is credible only if no donor had a comparable intervention or spillover and if pre-period fit holds for the predictors that matter.

## Sources

1. Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies. *JASA*, 105(490), 493–505.
2. Abadie, A. (2021). Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects. *Journal of Economic Literature*, 59(2), 391–425.
3. Arkhangelsky, D., et al. (2021). Synthetic Difference-in-Differences. *American Economic Review*, 111(12), 4088–4118.
