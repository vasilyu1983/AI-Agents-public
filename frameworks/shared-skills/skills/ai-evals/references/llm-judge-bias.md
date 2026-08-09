# LLM-as-Judge Bias Taxonomy and Controls

## Table of Contents

- [Why this matters](#why-this-matters)
- [The bias taxonomy](#the-bias-taxonomy)
- [Controls by bias](#controls-by-bias)
- [Pairwise judging done right](#pairwise-judging-done-right)
- [Judge prompt design](#judge-prompt-design)
- [Verification checklist](#verification-checklist)

## Why this matters

An LLM-as-judge produces a number that *looks* objective. It is not. The judge is
a model with systematic, replicated biases. Untreated, these biases produce
scores that correlate with surface features (length, order, style) instead of
the quality you meant to measure — so the eval ships regressions while reporting
green. Controlling judge bias is the single highest-leverage step in any
LLM-judge eval program.

## The bias taxonomy

| Bias | What it is | Symptom |
|------|------------|---------|
| **Position bias** | In pairwise comparison, the judge favors whichever candidate is shown first (or, for some models, last). | Win rate flips when you swap A/B order. |
| **Length / verbosity bias** | The direction is model-dependent and has reversed for some 2025+ frontier judges, which show a conciseness preference. Do not assume a direction — measure on your own setup. | Score correlates with token count (either direction). |
| **Self-preference bias** | A judge rates outputs from its own model family / style higher. | Model-X-as-judge prefers Model-X answers. |
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
  holistically. Because direction is model-dependent (some 2025+ models prefer
  brevity), measure the correlation on your own setup rather than assuming it
  runs long.
- **Self-preference** -> Use a **different judge model** than the one (and ideally
  the family) under test. For the release-blocking gate, prefer a deterministic
  check or a human-labeled slice over any same-family judge.
- **Style bias** -> Strip or normalize formatting before judging when style is
  not part of the quality bar; require the judge to cite the specific evidence
  span that supports each credited claim.
- **Sycophancy** -> Never put the expected answer in the judge prompt unless the
  task is grading against a reference; when you do, randomize which side is
  labeled "reference."
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
3. Require both runs to agree; **order-swap disagreement = the judge is
   position-biased on this case, so its verdict is unreliable — score it a tie
   and drop it from the win/loss tally.** This is the opposite of *jury*
   disagreement (different judge models split), which is a *signal* that the case
   is genuinely ambiguous and should go to a human — see `advanced-judging.md`.
   One means "throw the verdict out," the other means "escalate the case." Don't
   conflate them.
4. Aggregate to a **win rate with a confidence interval**, not a raw tally (see
   `eval-statistics.md` for the bootstrap CI on win rate).
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

## Verification checklist

- [ ] Judge model differs from the model(s) under test
- [ ] Pairwise runs use both orderings and require agreement
- [ ] Rubric is pinned to verifiable behavior, not plausibility
- [ ] Judge returns structured JSON with reason + evidence
- [ ] Judge temperature is low and judge prompt/model are versioned
- [ ] Judge-human agreement is tracked over time (see threshold-derivation.md)
- [ ] Length-bias direction measured on your own setup (do not assume direction)
- [ ] Agreeableness bias tested with a known-incorrect set; TPR and TNR reported separately
