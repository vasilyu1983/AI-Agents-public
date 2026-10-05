---
name: foundations-statistical-inference
description: "Tests whether data supports a claim: A/B significance, peeking, sample size, eval error bars, multiple comparisons. Use when deciding if results are significant."
version: "1.1"
last_validated: 2026-09-17
---

# Statistical Inference Foundations

Turn observations into appropriately bounded claims. A numerical estimate is incomplete without its population, estimand, sampling mechanism, independent unit, uncertainty, and assumptions.

**Triggers:** "is this A/B test uplift significant or noise", "can we stop the experiment early / we peeked daily", "how many users or eval items do we need", "error bars on eval or benchmark scores", "is model B really better than A", "CI for pass rate graded by an LLM judge", "we tested 20 metrics", sample-ratio mismatch, CUPED, ratio metrics, confidence or credible intervals, calibration, conformal prediction.

Use measurement theory for whether the instrument measures the intended construct, causal inference for identification of intervention effects, and decision theory for choosing actions given uncertainty. This skill owns inference contracts; applied evaluation workflows remain with `ai-evals`. Do not create causal claims from statistical significance.

## Quick Reference

| Need | Load |
|---|---|
| Population, estimator, confidence or credible interval | Sampling and estimation |
| Precision, selection, repeated looks | Design and sequential inference |
| Forecast uncertainty or conformal threshold | Predictive calibration |
| A/B test validity (SRM), CUPED, ratio metrics, peeking, sequential stopping | [A/B test craft](references/ab-test-craft.md) |
| Holm vs BH vs BY; FWER vs FDR | [Multiplicity procedures](references/multiplicity-procedures.md) |
| Eval scores: clustered SE, paired model comparison, eval size | [Eval error bars](references/eval-error-bars.md) |
| LLM-judge labels plus a small human gold set | [Judge-assisted inference (PPI/PPI++)](references/judge-assisted-inference.md) |
| CQR, per-group, covariate-shift, drift, or risk-control conformal | [Conformal variants](references/conformal-variants.md) |

## Workflow

1. Define the target population, estimand, units, time window, data provenance, selection/missingness mechanism, and independent sampling or randomization unit. Count users or clusters when runs are dependent; repeated outputs are not automatically independent evidence.
2. Read [sampling and estimation](references/sampling-and-estimation.md) for descriptive, frequentist, or Bayesian inference. Select a method that matches dependence, outcome support, and available sample size. State modeling choices before interpreting results.
   - Most labels come from an LLM judge or classifier: read [judge-assisted inference](references/judge-assisted-inference.md); a judge-only mean is not an estimate of the human-label quantity.
   - Eval or benchmark scores, or model A vs B on shared items: read [eval error bars](references/eval-error-bars.md); pair, and cluster related items.
3. Read [design and sequential inference](references/design-and-sequential.md) when power, multiple hypotheses, stopping, or repeated comparisons matter. Declare the hypothesis family, minimum meaningful effect, and stopping rule. Separate exploration from confirmatory claims.
   - Online experiment: run the SRM and unit checks in [A/B test craft](references/ab-test-craft.md) before reading any effect, and pick fixed-horizon, group-sequential, or always-valid stopping before launch.
   - More than one hypothesis: pick FWER or FDR and the procedure in [multiplicity procedures](references/multiplicity-procedures.md).
4. Read [predictive calibration](references/predictive-calibration.md) for predictive intervals, probabilistic forecasts, or conformal sets. Check training/calibration separation and exchangeability before claiming marginal coverage. For per-group coverage, drift, covariate shift, or an error-rate target (abstention), choose from [conformal variants](references/conformal-variants.md).
5. Produce an [inference report](assets/templates/inference-report.md), adapting its detail to the request. Report effect magnitude, uncertainty, assumptions, diagnostics, and what the analysis cannot establish. A null result can be imprecise; equivalence needs an explicit margin and appropriate test or interval.

## Interpretation constraints

- A p-value is not the probability a hypothesis is true; significance does not measure effect magnitude or practical importance [ASA2016].
- A frequentist confidence interval has repeated-sampling coverage under its assumptions. A Bayesian credible interval is posterior probability conditional on the model and prior; neither automatically covers future observations.
- More samples reduce sampling error under the model; they do not repair selection bias, invalid measurement, leakage, or dependence.
- Ordinary fixed-horizon intervals are not generally valid after data-dependent repeated stopping. Anytime-valid methods require their own null, filtration, and process assumptions [Ramdas2023].
- Conformal coverage is marginal over calibration and future observations under exchangeability. It does not ensure every group or individual has nominal coverage [AngelopoulosBates2022].
- Do not translate a standardized effect size into a conversion multiplier without the outcome model and baseline needed for that conversion.

## Helper

[split_conformal_quantile.py](scripts/split_conformal_quantile.py) computes only the exact finite-sample split-conformal threshold; it cannot check exchangeability or certify coverage. Interface in [predictive calibration](references/predictive-calibration.md#helper-interface); tests: `python3 scripts/test_split_conformal_quantile.py`.

## Completion criteria

The report names population, estimand, independent unit, method, assumptions, uncertainty, multiplicity/stopping policy, missing evidence, and supported interpretation. Any numerical helper result is reproducible from supplied inputs. Disclose exploratory or model-conditional conclusions and avoid treating structural validation as demonstrated agent performance.

## Verification Notes

Verify the precise theorem and assumptions against the primary source before asserting a guarantee. Worked values in the references are illustrative re-derivations, not empirical effect estimates; re-check package versions (ppi-python, MAPIE) before quoting them.

## Navigation

- [Sampling and estimation](references/sampling-and-estimation.md): inferential targets and interval interpretation.
- [Design and sequential inference](references/design-and-sequential.md): precision, multiplicity, and stopping.
- [Predictive calibration](references/predictive-calibration.md): coverage assumptions and full helper interface.
- [A/B test craft](references/ab-test-craft.md): SRM, CUPED, delta method, heavy tails, stopping designs, peeking remediation.
- [Multiplicity procedures](references/multiplicity-procedures.md): Holm, BH, BY, e-BH, gatekeeping.
- [Eval error bars](references/eval-error-bars.md): clustered and paired eval inference, eval sizing.
- [Judge-assisted inference](references/judge-assisted-inference.md): PPI/PPI++ for LLM-judge-labelled data.
- [Conformal variants](references/conformal-variants.md): CQR, Mondrian, weighted, adaptive, risk control.
- [Inference report](assets/templates/inference-report.md): output template.

Source IDs above resolve to dated primary records in [sources.json](data/sources.json). No claim of exhaustive coverage of the research literature.

Related: [causal inference](../foundations-causal-inference/SKILL.md), [decision theory](../foundations-decision-theory/SKILL.md), [AI evaluations](../ai-evals/SKILL.md).
