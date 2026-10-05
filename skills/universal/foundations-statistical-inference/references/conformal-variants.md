# Conformal variants: choosing beyond split conformal

Start from the split-conformal contract in [predictive calibration](predictive-calibration.md). The bundle's `scripts/split_conformal_quantile.py` computes that exact finite-sample threshold. Every variant below changes either the score or the guarantee. Each variant needs its own theorem, so state which one you rely on.

## Variant chooser

| Variant | Guarantee | Assumption | Use when |
|---|---|---|---|
| Split conformal [AngelopoulosBates2022] | Marginal coverage ≥ 1 − α | Exchangeable calibration and test points | Default for sets or intervals on i.i.d. data |
| CQR, conformalized quantile regression [Romano2019] | Marginal coverage ≥ 1 − α, with widths that adapt to heteroscedasticity | Exchangeability; quantile regressors fit on a separate split | Regression where noise varies with x, and constant-width intervals waste width |
| Mondrian / group-conditional | Coverage ≥ 1 − α *within each pre-defined group* | Exchangeability within each group; enough calibration points per group | Per-language, per-segment or per-customer-tier coverage promises |
| Weighted conformal under covariate shift [Tibshirani2019] | Coverage under the shifted test distribution with the correct weights | Only P(X) shifts, P(Y given X) is unchanged, and the likelihood ratio w(x) = dP_test/dP_train is known; estimated weights need separate coverage-error analysis | A known deployment mix differs from the calibration mix |
| Adaptive conformal inference, ACI [GibbsCandes2021] | Long-run average miscoverage → α: \|mean(err_t) − α\| ≤ (max(α₁, 1 − α₁) + γ)/(Tγ) | None on the distribution; online feedback of err_t is required | Drifting streams where the label arrives after the prediction |
| Conformal risk control, CRC [Angelopoulos2022CRC] | E[loss] ≤ α for a bounded, monotone loss | Exchangeability; loss non-increasing in λ and bounded by B | A monotone loss such as false-negative rate or set-level recall loss |

## Conformal risk control recipe

- **Choose λ̂:** the smallest λ such that (n/(n + 1))·R̂_n(λ) + B/(n + 1) ≤ α, where R̂_n is the mean calibration loss.
- **Worked:**

  | Calibration size | Settings | Largest allowed empirical risk |
  |---|---|---|
  | n = 1000 | B = 1, α = 0.05 | (0.05 × 1001 − 1)/1000 = 0.04905 |
  | n = 100 | B = 1, α = 0.05 | 0.0405 |

  Small calibration sets pay a visible margin.
- **Abstention threshold example:** "keep the error rate among answered queries ≤ 5%" targets P(wrong | answered).
  - The indicator of a wrong answered query instead controls P(wrong and answered), with all queries in the denominator. CRC on this loss does not establish the conditional promise.
  - Conditional error need not be monotone in the confidence threshold. Use a learn-then-test procedure with valid tests over a pre-declared threshold family for this target; see [AngelopoulosBates2022] §5.5.

## Failure modes

- **Marginal is not conditional.** A 90% marginal guarantee can hide 60% coverage for a minority group. Promise per-group coverage only with Mondrian calibration, and report the per-group calibration counts.
- **ACI is not per-time-step coverage.** It controls long-run frequency. A burst of misses after a shift is expected, and γ trades adaptivity for stability.
- **Weighted conformal with poorly estimated weights** loses its guarantee. Extreme weights also make intervals explode, so inspect the effective sample size of the weights.
- **Reusing calibration data** to choose among variants or scores, then reporting the coverage from that same data, breaks exchangeability. Hold out a separate validation split.
- **Label noise.** Coverage is of the *recorded* label. With noisy gold labels, the guarantee covers the noise too.

## Tooling

- `MAPIE` (scikit-learn compatible; check its current PyPI release and docs).
  - Its package description lists split conformal regression and classification, CQR, and risk control, including conformal risk control and learn-then-test.
- Verify that the specific variant and guarantee you need is implemented in the installed version before relying on it. Mondrian and weighted conformal availability was not checked.

Sources: see [sources.json](../data/sources.json) IDs AngelopoulosBates2022, Romano2019, Tibshirani2019, GibbsCandes2021, Angelopoulos2022CRC.
