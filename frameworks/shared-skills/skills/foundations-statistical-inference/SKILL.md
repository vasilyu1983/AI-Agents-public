---
name: foundations-statistical-inference
description: Assesses statistical evidence. Use when choosing sampling uncertainty, power, multiplicity, sequential inference, calibration, or predictive coverage methods.
version: "1.0"
last_validated: 2026-09-17
---

# Statistical Inference Foundations

Turn observations into appropriately bounded claims. A numerical estimate is incomplete without its population, estimand, sampling mechanism, independent unit, uncertainty, and assumptions.

**Triggers:** sampling uncertainty, confidence or credible intervals, effect-size precision, statistical power, multiple comparisons, optional stopping, Bayesian inference, predictive calibration, or conformal prediction.

Use measurement theory for whether the instrument measures the intended construct, causal inference for identification of intervention effects, and decision theory for choosing actions given uncertainty. This skill owns inference contracts; applied evaluation workflows remain with `ai-evals`. Do not create causal claims from statistical significance.

## Quick Reference

| Need | Load |
|---|---|
| Population, estimator, confidence or credible interval | Sampling and estimation |
| Precision, selection, repeated looks | Design and sequential inference |
| Forecast uncertainty or conformal threshold | Predictive calibration |

## Workflow

1. Define the target population, estimand, units, time window, data provenance, selection/missingness mechanism, and independent sampling or randomization unit. Count users or clusters when runs are dependent; repeated outputs are not automatically independent evidence.
2. Read [sampling and estimation](references/sampling-and-estimation.md) for descriptive, frequentist, or Bayesian inference. Select a method that matches dependence, outcome support, and available sample size. State modeling choices before interpreting results.
3. Read [design and sequential inference](references/design-and-sequential.md) when power, multiple hypotheses, stopping, or repeated comparisons matter. Declare the hypothesis family, minimum meaningful effect, and stopping rule. Separate exploration from confirmatory claims.
4. Read [predictive calibration](references/predictive-calibration.md) for predictive intervals, probabilistic forecasts, or conformal sets. Check training/calibration separation and exchangeability before claiming marginal coverage.
5. Produce an [inference report](assets/templates/inference-report.md), adapting its detail to the request. Report effect magnitude, uncertainty, assumptions, diagnostics, and what the analysis cannot establish. A null result can be imprecise; equivalence needs an explicit margin and appropriate test or interval.

## Interpretation constraints

- A p-value is not the probability a hypothesis is true; significance does not measure effect magnitude or practical importance [ASA2016].
- A frequentist confidence interval has repeated-sampling coverage under its assumptions. A Bayesian credible interval is posterior probability conditional on the model and prior; neither automatically covers future observations.
- More samples reduce sampling error under the model; they do not repair selection bias, invalid measurement, leakage, or dependence.
- Ordinary fixed-horizon intervals are not generally valid after data-dependent repeated stopping. Anytime-valid methods require their own null, filtration, and process assumptions [Ramdas2023].
- Conformal coverage is marginal over calibration and future observations under exchangeability. It does not ensure every group or individual has nominal coverage [AngelopoulosBates2022].
- Do not translate a standardized effect size into a conversion multiplier without the outcome model and baseline needed for that conversion.

## Helper

Use [split_conformal_quantile.py](scripts/split_conformal_quantile.py) only to compute the finite-sample score threshold. It uses exact rational arithmetic from JSON decimal literals and an inclusive score cutoff. It cannot inspect exchangeability or certify empirical coverage. Full input/output and examples are in [predictive calibration](references/predictive-calibration.md).

Run its independently specified tests with `python3 scripts/test_split_conformal_quantile.py` from this bundle. The test suite is [test_split_conformal_quantile.py](scripts/test_split_conformal_quantile.py).

## Completion criteria

The report names population, estimand, independent unit, method, assumptions, uncertainty, multiplicity/stopping policy, missing evidence, and supported interpretation. Any numerical helper result is reproducible from supplied inputs. Disclose exploratory or model-conditional conclusions and avoid treating structural validation as demonstrated agent performance.

## Fact-Checking

Verify the assumptions and precise theorem used against the primary source before asserting a guarantee. Treat worked values as illustrative examples; they are not empirical effect estimates. Record method versions or implementation choices when they affect reproducibility.

## Navigation

- [Sampling and estimation](references/sampling-and-estimation.md): inferential targets and interval interpretation.
- [Design and sequential inference](references/design-and-sequential.md): precision, multiplicity, and stopping.
- [Predictive calibration](references/predictive-calibration.md): coverage assumptions and full helper interface.
- [Inference report](assets/templates/inference-report.md): output template.

Source IDs above resolve to dated primary records in [sources.json](data/sources.json). Scope cutoff: 17 September 2026; no claim of exhaustive coverage of all research through that date.

Related: [causal inference](../foundations-causal-inference/SKILL.md), [decision theory](../foundations-decision-theory/SKILL.md), [AI evaluations](../ai-evals/SKILL.md).
