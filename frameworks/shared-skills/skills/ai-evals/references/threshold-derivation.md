# Deriving Thresholds and Gates from Labeled Data

## Table of Contents

- [The problem with copied thresholds](#the-problem-with-copied-thresholds)
- [Build a calibration set](#build-a-calibration-set)
- [Measure judge-human agreement](#measure-judge-human-agreement)
- [Derive the threshold](#derive-the-threshold)
- [Gate design](#gate-design)
- [Checklist](#checklist)

## The problem with copied thresholds

">95% accuracy" or ">0.85 faithfulness" copied from a blog is a guess until it
is validated on *your* distribution. A threshold has meaning only relative to:

- the task difficulty mix in your eval set
- the cost of a false pass vs a false fail in your product
- how well your grader agrees with humans

Setting the threshold *after* seeing results so a candidate passes is
threshold-on-the-fly — the most common way evals lie.

## Build a calibration set

1. Sample real cases spanning the difficulty/slice mix you care about. **100-300
   cases is a reasonable size for *calibrating a judge* against human labels**
   (estimating agreement, locating the operating point). It is **not** a sizing
   rule for a *gating* set: detecting a small regression needs far more — size
   that from the minimum detectable effect, not a round number. A 100-case set
   has a ±~7pp confidence band near 85% accuracy, so it cannot gate a 2-point
   regression. See `eval-statistics.md` for the power/MDE math and the
   `required_sample_size()` calculator.
2. Have humans label them with the same rubric the judge uses.
3. Keep this set **frozen and held out** from any tuning of the system or prompts.
4. Re-label a fresh slice periodically; distributions drift.

This set does double duty: it calibrates the judge *and* anchors the threshold.
Size the *gating* set separately, from power — they are not the same set.

## Measure judge-human agreement

Before trusting a judge's number, measure how well it matches human labels on the
calibration set:

- **Binary verdicts** -> Cohen's kappa (one judge vs human) or percent agreement.
- **Multi-rater** -> Fleiss' kappa or Krippendorff's alpha.
- **Scores/rankings** -> Spearman/Kendall correlation with human ranking.

Rules of thumb (not laws): kappa < 0.4 means the judge is too noisy to gate on —
fix the rubric or use a deterministic check. kappa 0.6-0.8 is usable for
non-blocking signal. Re-measure when you change the judge model or prompt.

## Derive the threshold

1. Run the (bias-controlled) judge on the calibration set.
2. Plot the score distribution for human-pass vs human-fail cases.
3. Pick the operating point from the cost of each error type:
   - High cost of shipping a bug -> threshold high, accept more false fails.
   - High cost of blocking good releases -> threshold lower, accept more false passes.
4. Report the resulting precision/recall at that threshold, not just the cutoff.
5. For abstention/confidence gates, derive two thresholds (act vs abstain) the
   same way — see ai-rag `references/abstention-recipe.md` for the two-tier pattern.

## Gate design

- **Layer the gate**: cheap deterministic check first (always-on), LLM judge on
  the slice the deterministic check can't decide, human review on a sampled
  remainder. Cheapest grader that works at each layer.
- **Gate on a slice table, not one number.** A single aggregate hides per-slice
  regressions; require no slice to drop below its own floor.
- **Pair quality with cost/latency.** A candidate that improves quality while
  doubling cost is a trade to surface, not a silent pass.
- **Fail loud.** The gate output must report skipped, errored, and quarantined
  cases. "All passed" is false if anything was silently skipped.

## Checklist

- [ ] Frozen, human-labeled calibration set exists and is held out from tuning
- [ ] Judge-human agreement measured (kappa/alpha/correlation) and acceptable
- [ ] Threshold derived from the labeled distribution + error-cost tradeoff
- [ ] Threshold committed to version control, not set after seeing results
- [ ] Gate is layered (deterministic -> judge -> human) and slice-aware
- [ ] Gate output names skipped/quarantined cases
