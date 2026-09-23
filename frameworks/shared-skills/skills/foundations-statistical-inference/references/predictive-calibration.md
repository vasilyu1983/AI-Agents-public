# Predictive calibration and conformal thresholds

## Forecast assessment

Separate discrimination, calibration, and predictive sharpness. Compare probabilistic forecasts with outcomes using proper scores such as log loss or Brier score and inspect reliability by meaningful groups and time windows. Bin-dependent calibration summaries can hide errors; include uncertainty and sample counts. A calibrated constant forecast can be uninformative, and high classification accuracy does not imply calibrated probabilities.

Use prediction intervals for future outcomes, not confidence intervals for the mean. Assess coverage alongside width/set size and subgroup diagnostics on held-out observations. Do not select the best calibration procedure on the same observations used for final validation.

## Split conformal contract

Fit the model and define the nonconformity score without using the calibration outcomes. With n calibration scores, set k=ceil((n+1)(1−alpha)) and choose the k-th sorted score; if k>n use an unbounded threshold. Include candidate outcomes with score at most that threshold.

With exchangeable calibration/future scores, this supplies marginal coverage at least 1−alpha. Ties can make it conservative; do not claim an upper coverage bound without the additional no-ties/randomization conditions. Marginal coverage does not establish conditional coverage for every input or group. Time dependence, adaptive reuse, distribution shift, or scoring/model changes can invalidate the standard argument. Any modified conformal method requires its own theorem and assumptions.

Worked example: scores 1 through 9 and alpha=0.2 give k=8 and threshold 8. Scores [2,4] and alpha=0.1 give k=3, an unbounded threshold. Capping k at n would silently weaken the finite-sample guarantee.

Counterexample: nominal 90% marginal coverage can coexist with poor coverage in a minority group. Inspect group/time coverage with uncertainty; do not claim group validity from the marginal theorem.

Primary source: [Angelopoulos and Bates tutorial, section 1 and coverage discussion](https://arxiv.org/html/2107.07511v6).

## Helper interface

Command from the bundle:

```bash
python3 scripts/split_conformal_quantile.py < input.json
```

Standard input is one strict JSON object with exactly `scores` and `alpha`. `scores` is a nonempty array of finite JSON numbers, including negative values if appropriate to the chosen scoring rule; `alpha` is a finite JSON number strictly between 0 and 1. Booleans, strings, duplicate/unknown keys, nonfinite extensions, trailing objects, and command-line arguments are rejected. Scores must already be computed; the helper does not fit a model or choose a score.

Output on success (exit 0): `n` and one-based `rank` as integers, `unbounded` as boolean, `threshold` as an exact decimal string or null, and `comparison` as `score <= threshold`. For an unbounded result, include all finite scores. Strings preserve decimal precision and keep stdout strict JSON without Infinity. Interpret the threshold numerically with a decimal-capable parser, not as a lexical comparison.

Input `{ "scores": [1,2,3,4,5,6,7,8,9], "alpha": 0.2 }` returns rank 8, threshold `"8"`, and unbounded false. The helper parses decimal literals exactly and uses rational arithmetic for rank calculation to avoid binary-floating boundary errors.

On invalid input: exit 2, empty stdout, and one JSON object containing `error` on stderr. It uses the Python standard library only, accepts no file-path arguments, writes no files, and cannot check exchangeability, training leakage, scoring suitability, or empirical coverage. OS/process failures are outside this input-validation contract.
