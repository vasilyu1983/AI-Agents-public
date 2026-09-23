# Primitive 12: Sensitivity Analysis

## Definition

Sensitivity analysis quantifies how robust an observational causal estimate is to violations of the identification assumptions — primarily unmeasured confounding. It answers: "How strong would an unmeasured confounder need to be to overturn this conclusion?"

Sensitivity analysis does not prove that confounding is absent. It communicates *how much* confounding the conclusion can tolerate.

**E-value** (VanderWeele & Ding 2017): the minimum **risk ratio** (RR) that an unmeasured confounder would need to have with both the exposure and the outcome to fully explain away the observed association.

For a risk ratio (RR) estimate between exposure and outcome:
E-value = RR + √(RR × (RR − 1))

For the confidence interval, use the bound closest to the null. For a protective
association entirely below 1 this is the upper bound; invert that bound before
applying the formula. If the interval includes 1, its E-value is 1.

A large E-value means a confounding RR of that magnitude with both exposure and outcome would be needed to nullify the finding. Small E-values indicate fragile conclusions.

**Rosenbaum bounds** (for matched observational studies): Γ is the maximum odds ratio of treatment assignment due to hidden bias. A sensitivity analysis asks: at what Γ does the statistical test lose significance? Large Γ tolerance indicates a robust finding.

**Tipping-point analysis**: express the conclusion as a function of a hypothetical unmeasured confounder's effect sizes. Identify the pair (RR_UD, RR_EU) — the confounder's effect on outcome and association with exposure — that would reduce the estimate to zero. Plot the tipping-point curve.

**Partial R² approach** (Cinelli & Hazlett 2020): quantifies sensitivity in terms of the proportion of residual variance in outcome and treatment explained by an unmeasured confounder.

## When to Use

- Any observational study reporting a causal estimate.
- Required at every presentation of an observational effect estimate.
- Particularly important when the effect is used to inform resource allocation or policy.
- Supplementary to all propensity (#8), DiD (#6), and IV (#4) analyses when identification assumptions are uncertain.

Do not use sensitivity analysis as a replacement for identifying assumptions — it quantifies robustness, not validity.

## Inputs / Outputs

**Inputs**: point estimate (risk ratio, odds ratio, mean difference, or regression coefficient) and its confidence interval; study design (matched, weighted, regression); exposure prevalence if known.

**Outputs**: E-value for the point estimate; E-value for the confidence interval limit; Rosenbaum Γ bound (for matched studies); tipping-point plot; verbal interpretation ("the finding is consistent with confounders of moderate/large/very large magnitude").

## Worst Failure Modes

1. **Reporting E-value without context**: an E-value of 2.0 may be large in one domain (where known confounders have RR ≈ 1.3) and small in another (where genetic confounders have RR > 5). Always compare E-value to known confounders in the domain.
2. **Sensitivity analysis replaces identification**: if the effect is not identified (e.g., the DAG shows the effect is non-identifiable), a sensitivity analysis on a meaningless estimate is still meaningless.
3. **Only analyzing the point estimate, not the CI**: the CI E-value is more conservative and more relevant for decision-making. Report both.
4. **Treating large E-value as proof of causation**: a large E-value means the finding is *robust*, not that it is *causal*. A specific strong confounder can still explain it if it exists.
5. **Misapplying the risk-ratio formula to mean differences**: the E-value formula applies to risk ratios. For mean differences, use the partial R² approach (Cinelli & Hazlett 2020) or convert via approximation.

## Worked Example

**Setting**: An observational study estimates that daily coffee drinking (X) reduces 10-year cardiovascular event risk (Y) by RR = 0.75 (95% CI: 0.62–0.91). Concern: unmeasured confounding by healthy lifestyle habits.

**E-value for point estimate** (RR = 0.75 → use reciprocal for protective effect = 1/0.75 = 1.33):
E-value = 1.33 + √(1.33 × 0.33) = 1.33 + 0.66 = 1.99

**E-value for CI bound closest to the null** (RR_upper = 0.91 → reciprocal ≈ 1.10):
E-value_CI ≈ 1.10 + √(1.10 × 0.10) ≈ 1.43

**Interpretation**: to fully explain away the point estimate, an unmeasured confounder would need to be associated with both coffee drinking and cardiovascular events with a risk ratio of about 2.0 each, conditional on measured covariates. Moving the confidence interval to include the null requires associations of about 1.43 each.

**Comparison to known confounders**:
- Exercise (a known healthy-lifestyle confounder): RR_with_coffee ≈ 1.4, RR_with_CV_risk ≈ 1.5
- Illustrative bias factor = 1.4 × 1.5 / (1.4 + 1.5 − 1) ≈ 1.105. Compare this bias factor with the inverted observed RR 1.333, not directly with the E-value 2.0, which is a symmetric association-strength threshold. The associations above are hypothetical, not verified exercise estimates

**Conclusion**: interpret both values against measured, domain-plausible confounders; the E-value alone does not establish causality or a universal action threshold.

Run the checked calculator for risk-ratio inputs:

```bash
python3 scripts/evalue.py --rr 0.75 --ci-low 0.62 --ci-high 0.91
```

## Sources

1. VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, 167(4), 268–274. https://doi.org/10.7326/M16-2607
2. Rosenbaum, P. R. (2002). *Observational Studies* (2nd ed.). Springer. Chapter 4.
3. Cinelli, C., & Hazlett, C. (2020). Making Sense of Sensitivity: Extending Omitted Variable Bias. *Journal of the Royal Statistical Society: Series B*, 82(1), 39–67.
