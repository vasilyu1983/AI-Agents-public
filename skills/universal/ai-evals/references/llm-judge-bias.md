# LLM-as-Judge Bias Taxonomy and Controls

## Table of Contents

- [Why this matters](#why-this-matters)
- [The bias taxonomy](#the-bias-taxonomy)
- [Controls by bias](#controls-by-bias)
- [Pairwise judging done right](#pairwise-judging-done-right)
- [Judge prompt design](#judge-prompt-design)
- [Judge drift](#judge-drift)
- [Verification checklist](#verification-checklist)

## Why this matters

An LLM-as-judge produces a number that *looks* objective. It is not. The judge is
a model with systematic, replicated biases. Untreated, these biases produce
scores that correlate with surface features (length, order, style) instead of
the quality you meant to measure — so the eval ships regressions while reporting
green. Calibrate bias controls against human labels before using judge scores as gates.

## The bias taxonomy

| Bias | What it is | Symptom |
|------|------------|---------|
| **Position bias** | In pairwise comparison, the judge favors whichever candidate is shown first (or, for some models, last). | Win rate flips when you swap A/B order. |
| **Length / verbosity bias** | Judges have historically favored longer answers (Dubois et al., 2024, arXiv 2404.04475), but the direction is judge-dependent: some judges prefer concise answers. Do not assume a direction — measure on your own setup. | Score correlates with token count (either direction). |
| **Self-preference bias** | Some evaluators favor their own outputs beyond human-rated quality; magnitude depends on the evaluator and task. | Model-X-as-judge prefers Model-X answers. |
| **Style / formatting bias** | Confident tone, markdown, bullet lists, and citations inflate scores regardless of correctness. | Well-formatted wrong answers beat plain right ones. |
| **Sycophancy / leading-prompt bias** | The judge agrees with whatever the prompt implies the "expected" answer is. | Scores shift when you hint the desired verdict. |
| **Scale compression** | On 1-10 rubrics the judge clusters at 7-8 and rarely uses extremes. | Low variance; can't separate candidates. |
| **Agreeableness bias** | Judge TPR (true-positive rate on correct answers) far exceeds TNR (true-negative rate on incorrect answers), inflating pass rates on low-quality output. The judge rarely says "no." | Pass rate looks high but a known-incorrect set also scores well. |

## Controls by bias

- **Position bias** -> Always run pairwise comparisons in **both orderings** and
  require agreement. Count a disagreement as a tie, not a win. Never gate on a
  single-order comparison.
- **Length bias** -> Pin the rubric to **verifiable behavior** (correct claims,
  tests pass, blast radius) and add an explicit instruction to ignore length;
  better, normalize or cap length before judging, or score per-claim rather than
  holistically. Because direction is judge-dependent (some judges prefer
  brevity), measure the correlation on your own setup rather than assuming it
  runs long.
- **Self-preference** -> Use a **different judge model** than the one (and ideally
  the family) under test. For the release-blocking gate, prefer a deterministic
  check or a human-labeled slice over any same-family judge.
- **Style bias** -> Strip or normalize formatting before judging when style is
  not part of the quality bar; require the judge to cite the specific evidence
  span that supports each credited claim.
- **Sycophancy** -> Never put the expected answer in the judge prompt unless the
  task is grading against a reference. Label the trusted reference consistently
  so the judge can distinguish the answer key from a candidate; randomize
  candidate order in pairwise comparisons.
- **Scale compression** -> Prefer **binary or few-level rubrics** (pass/fail,
  or grounded/partial/hallucinated) over 1-10 scales; if you need a scale,
  anchor each level with a concrete description.
- **Agreeableness bias** -> Construct a **known-incorrect set** and measure TNR
  explicitly; a judge that never says "no" will appear well-calibrated on a
  correct-answer set alone. Report TPR and TNR separately.

## Pairwise judging done right

Pairwise (A-vs-B) is more reliable than absolute scoring for *choosing* between
two candidates, but only with these guards:

1. Show both candidates for the same input.
2. Run order AB and order BA.
3. Require a consistent winner in both orderings; otherwise record an
   `order_inconsistent` tie under the conservative rule from
   [MT-Bench §3.4](https://arxiv.org/html/2306.05685v4). One swapped disagreement
   does not isolate position bias from sampling noise or ambiguous candidates.
   Preserve every case in the report and expose ties and inconsistency rates.
   Define whether the win-rate denominator includes ties before scoring; a
   non-tie win rate describes only that selected subset. Escalate unresolved
   blocking cases or weak judge agreement to humans (`advanced-judging.md`).
4. For population claims, aggregate the declared win-rate estimand with
   design-compatible uncertainty (`eval-statistics.md`); fixed-suite tallies
   describe only that suite.
5. Gate on win rate **and** absolute cost/latency, so a "winner" that doubled
   cost is surfaced as a trade, not a silent victory.

## Judge prompt design

- Force **structured output**: `{"verdict": ..., "reason": ..., "evidence": ...}`.
  A free-text verdict is unparseable and uncalibratable.
- Require a **reason and an evidence pointer** for every verdict — this both
  improves accuracy and lets you audit drift.
- Keep judge **temperature low** (near 0) for reproducibility; the judge is a
  measuring instrument, not a creative writer.
- Version the judge prompt and judge model alongside the eval; a changed judge
  is a changed instrument and invalidates historical comparisons.

## Judge drift

Judge scores drift for three separable reasons, and each has its own fix:

1. **Provider update behind a stable model name** → re-run the frozen
   human-labeled set; re-pin or re-validate the judge.
2. **Grader-prompt edit** (made for one case, shifting unrelated scores) → diff
   scores on the frozen set before and after the edit; version the prompt.
3. **Shift in the system's failure mix** (old calibration cases stop covering
   current failures) → add fresh labeled cases; the judge may be fine.

Log the judge model id and grader-prompt version with every score. Re-run the
frozen set on a fixed cadence and after any provider update you did not start,
and alert when agreement falls below its baseline band
([threshold-derivation.md](threshold-derivation.md#measure-judge-human-agreement)).
Attribute the cause before recalibrating: a judge drifting in the same direction
as the system hides a regression; drifting the opposite way invents one.

## Verification checklist

- [ ] Judge model differs from the model(s) under test
- [ ] Pairwise runs use both orderings and require agreement
- [ ] Rubric is pinned to verifiable behavior, not plausibility
- [ ] Judge returns structured JSON with reason + evidence
- [ ] Judge temperature is low and judge prompt/model are versioned
- [ ] Judge-human agreement is tracked over time (see threshold-derivation.md)
- [ ] Length-bias direction measured on your own setup (do not assume direction)
- [ ] Agreeableness bias tested with a known-incorrect set; TPR and TNR reported separately
- [ ] Judge model id and grader-prompt version logged with every score; drift cause attributed before recalibration

Primary evidence: [MT-Bench](https://arxiv.org/html/2306.05685v4) reports
position and verbosity effects and a conservative swap-to-tie rule;
[Panickssery et al.](https://arxiv.org/abs/2404.13076) studies self-preference
under controlled self-recognition experiments. Neither establishes a universal
bias magnitude or makes a different-family judge sufficient for calibration.
