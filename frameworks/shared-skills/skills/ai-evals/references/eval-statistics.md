# Eval Statistics: Trusting "X Beats Y"

Most eval conclusions are comparative — "the new prompt is better," "model B wins."
Without statistics, those claims are noise dressed as signal. This file is the
math that turns a score difference into a defensible decision.

## Table of Contents

- [The core question](#the-core-question)
- [Confidence intervals via bootstrap](#confidence-intervals-via-bootstrap)
- [Paired beats unpaired](#paired-beats-unpaired)
- [Tests by outcome type](#tests-by-outcome-type)
- [Sizing the eval set: power and MDE](#sizing-the-eval-set-power-and-mde)
- [Multiple comparisons](#multiple-comparisons)
- [Variance reduction](#variance-reduction)
- [Reporting](#reporting)
- [Checklist](#checklist)

## The core question

You ran the eval set on system A and system B. A scored 87%, B scored 85%. Is A
actually better, or is 2 points inside the noise? The answer depends on the
sample size, the per-case variance, and whether the systems were run on the
**same** cases. A point estimate alone ("87% vs 85%") is never a decision — it
needs an interval and a test.

## Confidence intervals via bootstrap

The bootstrap is the workhorse for LLM evals because pass rates are not normally
distributed at small n and metrics are often non-standard (nDCG, win rate,
rubric scores). It needs no distributional assumption.

```text
Given per-case scores s_1..s_n:
repeat B = 10,000 times:
    resample n cases WITH replacement
    record the metric (mean, win rate, nDCG...) of the resample
the 2.5th and 97.5th percentiles of those B values = 95% CI
```

- Report the CI, not just the mean. A 2-point gap with overlapping 95% CIs is
  not a result.
- For comparing A and B, bootstrap the **difference** (paired — see below), and
  check whether the CI of the difference excludes 0.
- 10k resamples is plenty; 1k is a fast smoke check.

## Paired beats unpaired

If A and B were run on the **same cases**, you have paired data — use it. Paired
analysis removes between-case difficulty variance and is dramatically more
powerful: it can detect a real difference with a fraction of the samples an
unpaired test needs.

- **Paired**: bootstrap or test the per-case difference `d_i = score_A(i) − score_B(i)`.
- **Unpaired** (different cases per system — avoid when you can): two-sample
  test on the two score sets, much weaker.

Rule: run every candidate on the same frozen eval set so you can always pair.

## Tests by outcome type

| Outcome | Paired test | Notes |
|---------|-------------|-------|
| **Binary pass/fail, same cases** | **McNemar's test** | The correct test for "did A pass cases B failed, and vice versa." Uses only the discordant pairs (b, c); ignores cases both got right/wrong. Far more powerful than comparing two proportions. |
| Continuous score (rubric, similarity), same cases | Paired bootstrap of the mean difference, or Wilcoxon signed-rank | Non-parametric; no normality assumption |
| Win rate (pairwise judge) | Bootstrap CI of win rate; sign test | Account for ties and position-swap agreement (see llm-judge-bias.md) |
| Ranking / ordering (retrieval) | Bootstrap CI of nDCG/MRR difference | Per-query bootstrap |

McNemar quick form: with `b` = A-right-B-wrong and `c` = A-wrong-B-right,
significance comes from whether `b` and `c` differ more than chance — a tiny
overall accuracy gap can be highly significant if the discordant pairs are
lopsided, and a large-looking gap can be noise if they're balanced.

## Sizing the eval set: power and MDE

Decide the set size from the smallest difference you need to detect (the
**minimum detectable effect**), not from a round number.

- For a binary metric near accuracy `p`, the 95% CI half-width on `n` cases is
  roughly `1.96 * sqrt(p(1−p)/n)`. At `p≈0.85`: n=100 → ±~7pp; n=400 → ±~3.5pp;
  n=1000 → ±~2.2pp. **To gate on a 2-point regression you need ~1000+ cases**,
  not 100.
- Set MDE, alpha (0.05), and power (0.80) **before** running. qa-agent-testing
  has a `required_sample_size()` power calculator — use it.
- Paired tests need fewer cases than these unpaired figures, often much fewer —
  another reason to pair.
- Slice-level gates need power **per slice**: 1000 total cases split across 10
  slices is 100/slice — underpowered per slice even if the aggregate is fine.

> Correction to earlier guidance: a "100-300 case calibration set" is fine for
> *calibrating a judge* against human labels, but is **underpowered for gating
> small regressions**. Size the gating set from MDE, not from the calibration
> set size.

## Multiple comparisons

Every extra slice/metric you test is another chance at a false positive. Testing
20 slices at α=0.05 gives ~64% chance of at least one spurious "regression."

- Apply **Benjamini-Hochberg (FDR)** across the family of slice/metric tests —
  it's the right default for eval dashboards (controls false-discovery rate
  while keeping power). Bonferroni is too conservative for many slices.
- State the family explicitly ("we tested 14 slices") so corrections are honest.
- Pre-register the primary metric; treat the rest as secondary/exploratory.

## Variance reduction

To detect smaller effects without growing n:

- **Common random numbers**: use the same seeds/sampling for A and B so shared
  randomness cancels in the paired difference.
- **CUPED-style covariate adjustment**: regress out a pre-experiment covariate
  (e.g., case difficulty score) to shrink variance — borrowed from online A/B,
  applies to offline paired evals too.
- **Stratified estimation**: estimate per-slice then combine, rather than one
  pooled mean, when slice difficulty varies widely.

## Reporting

Every comparative result should state: metric, point estimate **with 95% CI**,
the test used, n (and discordant-pair counts for McNemar), whether paired, and
any multiple-comparison correction. "A 87% vs B 85%" alone is not reportable.

## Checklist

- [ ] Candidates run on the same frozen cases (so analysis can be paired)
- [ ] Point estimates reported with bootstrap 95% CIs
- [ ] Binary same-case comparisons use McNemar, not two-proportion
- [ ] Gating set sized from MDE/power, not a round number
- [ ] Per-slice power checked, not just aggregate
- [ ] FDR correction applied across slice/metric families; family stated
- [ ] Primary metric pre-registered; CIs of differences exclude 0 before claiming a win
