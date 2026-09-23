# Eval Statistics: Trusting "X Beats Y"

Most eval conclusions are comparative — "the new prompt is better," "model B wins."
Without statistics, those claims are noise dressed as signal. This file is the
math that turns a score difference into a defensible decision.

## Table of Contents

- [The core question](#the-core-question)
- [Confidence intervals via bootstrap](#confidence-intervals-via-bootstrap)
- [Local paired analyzer](#local-paired-analyzer)
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
needs design-compatible uncertainty and a predeclared decision rule.

## Confidence intervals via bootstrap

The bootstrap is useful for LLM evals because metrics are often non-standard
(nDCG, win rate, rubric scores). Its validity still depends on the sampling
design and on resampling the unit that represents the target population.

```text
Given per-case scores s_1..s_n:
repeat B = 10,000 times:
    resample n cases WITH replacement
    record the metric (mean, win rate, nDCG...) of the resample
the 2.5th and 97.5th percentiles of those B values = 95% CI
```

- Report the interval for the paired difference rather than reasoning from
  overlap between two marginal intervals.
- For comparing A and B, bootstrap the **difference** (paired — see below), and
  check whether the CI of the difference excludes 0.
- Fix the seed and report the number of resamples. Increase the count until the
  reported percentile endpoints are stable enough for the decision; more
  resamples reduce Monte Carlo noise but do not repair a wrong resampling unit.

## Paired beats unpaired

If A and B were run on the **same cases**, you have paired data — use it. Paired
analysis removes between-case difficulty variance and can improve
precision when within-pair outcomes are positively associated; the gain depends
on the covariance and estimand, rather than a universal sample-size reduction.

- **Paired**: bootstrap or test the per-case difference `d_i = score_A(i) − score_B(i)`.
- **Unpaired** (different cases per system — avoid when you can): two-sample
  test on the two score sets, much weaker.

Rule: run every candidate on the same frozen eval set so you can always pair.

## Local paired analyzer

For already captured results, run:

```bash
python3 scripts/analyze_paired_results.py results.csv --estimand unit_mean --seed 20260908
```

The CSV requires unique `unit_id` values and finite `baseline` and `candidate`
scores. Optional columns are `cluster_id`, `stratum`, `critical_baseline`, and
`critical_candidate`. Repeated cluster IDs are expected: the helper samples
whole clusters and retains every baseline/candidate pair. `unit_mean` gives each
captured unit equal weight; `cluster_mean` first averages within a cluster and
then gives each cluster equal weight. Choose the estimand before inspecting the
result. The output reports the weighting and resampling rules, seeded percentile
intervals, every named stratum, and critical failures separately.

The interval describes resampling uncertainty for the declared captured-unit or
cluster population. It does not turn a fixed suite into evidence about a broader
task population, establish generic bootstrap validity, or measure a live model.
With fewer than two independent clusters, the helper suppresses the interval
instead of returning a misleading zero-width result. Cluster-bootstrap validity
depends on the population model and statistic; see Field and Welsh (2007),
*Bootstrapping clustered data*, https://doi.org/10.1111/j.1467-9868.2007.00593.x.

## Tests by outcome type

| Outcome | Paired test | Notes |
|---------|-------------|-------|
| **Binary pass/fail, same cases** | **McNemar's test** | Tests marginal binary equality using discordant pairs (b, c), assuming independent pairs. Repeated runs within clusters need a design-compatible clustered analysis; pairing does not remove clustering. |
| Continuous score (rubric, similarity), same cases | Paired bootstrap of the mean difference, or Wilcoxon signed-rank | Bootstrap requires design-compatible sampling and estimator regularity. Signed-rank tests a location claim under independent, symmetric paired differences; it is not a generic test of the mean difference. |
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
  n=1000 → ±~2.2pp. These are precision approximations for an independent proportion,
  not power calculations for a two-point paired regression. Determine gating
  size from the chosen test, alternative, discordance/variance, and dependence.
- Set the meaningful effect, error criterion, and desired power **before**
  running. If using a calculator, verify that its design and outcome assumptions
  match the eval; a two-independent-proportion formula does not size clustered
  paired comparisons.
- For paired binary data, sample-size needs depend on discordant probabilities;
  for continuous data they depend on within-pair difference variance.
- Slice-level gates need power **per slice**: 1000 total cases split across 10
  slices is 100/slice — underpowered per slice even if the aggregate is fine.

> Correction to earlier guidance: a "100-300 case calibration set" is fine for
> *calibrating a judge* against human labels, but is **underpowered for gating
> small regressions**. Size the gating set from MDE, not from the calibration
> set size.

## Multiple comparisons

Every extra slice/metric you test is another chance at a false positive. Testing
20 independent true-null tests at α=0.05 gives ~64% chance of at least one spurious "regression."

- Choose the error criterion for the decision: FDR controls the expected
  false-discovery proportion, while family-wise control bounds any false
  rejection. For blocking release gates, decide whether any false clearance or
  regression declaration matters. Bonferroni supports family-wise control with
  valid component p-values under arbitrary dependence. Benjamini-Hochberg FDR
  control requires independence or the applicable positive-dependence conditions;
  shared cases and overlapping slices do not automatically satisfy them.
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

Every inferential comparative result should state: estimand, metric, point
estimate and interval with declared coverage level, independent unit/cluster
count (and discordant-pair counts for McNemar), method and assumptions, pairing,
multiplicity, and stopping policy. Exact fixed-suite counts need their denominator
and scope rather than an invented sampling interval. "A 87% vs B 85%" alone does
not establish a population-level superiority claim.

## Checklist

- [ ] Candidates run on the same frozen cases (so analysis can be paired)
- [ ] Population claims use uncertainty matched to the estimand, sampling design,
      dependence, and declared coverage level; use bootstrap only when justified
- [ ] Exact deterministic fixed-suite outcomes report counts, denominators, and
      descriptive scope without an invented sampling interval
- [ ] Paired binary equality claims use McNemar only when pairs are independent;
      clustered repeats use a design-compatible analysis, and other estimands
      use the method appropriate to their target
- [ ] Gating set sized from MDE/power, not a round number
- [ ] Per-slice power checked, not just aggregate
- [ ] Multiplicity criterion, family, procedure, and dependence assumptions stated
- [ ] Primary metric and stopping rule declared; interval compared with the
      predeclared meaningful-effect or non-inferiority margin before a verdict

## Method sources and scope

For interpretation-changing uncertainty, load [statistical inference](../../foundations-statistical-inference/SKILL.md); skip population inference for exact deterministic suite outcomes. The [NIST signed-rank contract](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/signrank.htm) specifies symmetry and independence. The [author-institution abstract of the original dependence analysis](https://cris.tau.ac.il/en/publications/the-control-of-the-false-discovery-rate-in-multiple-testing-under/) distinguishes BH positive-dependence conditions from arbitrary dependence. The NIST contract and author-institution abstract were inspected on 2026-09-17 (the publisher full text was unavailable); they establish method conditions, not better live agent performance.
