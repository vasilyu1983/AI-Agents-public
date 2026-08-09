# Advanced LLM-as-Judge: Juries, Calibration, and Agentic Reward

`llm-judge-bias.md` covers keeping a single judge honest. This file is the next
layer: when one prompted judge isn't enough — ensembles and juries, fine-tuned
judges, scoring methods that beat raw 1-10 ratings, measuring whether your judge
is actually calibrated, and the hardest case, grading multi-step agent
trajectories where there is no single "right answer" to compare against.

## Table of Contents

- [When to escalate past one judge](#when-to-escalate-past-one-judge)
- [Juries and ensembles](#juries-and-ensembles)
- [Prompted vs fine-tuned judges](#prompted-vs-fine-tuned-judges)
- [Scoring methods that beat 1-10](#scoring-methods-that-beat-1-10)
- [Reference-guided vs reference-free](#reference-guided-vs-reference-free)
- [Measuring judge calibration](#measuring-judge-calibration)
- [Agentic reward: grading trajectories](#agentic-reward-grading-trajectories)
- [Checklist](#checklist)

## When to escalate past one judge

A single prompted judge is fine when stakes are low and it agrees well with humans.
Escalate when: the gate is high-stakes, a single model's bias is structural (self-
preference on its own family), agreement with humans is mediocre, or the task is
open-ended enough that one model's opinion is too noisy. The escalations below
trade cost for reliability — spend it where the decision matters.

## Juries and ensembles

A **jury** is multiple *different* judge models voting; it beats a single large
judge on agreement-with-humans while often costing less (several small judges <
one frontier judge).

- **Use different model families**, not the same model thrice — correlated judges
  don't reduce bias, they amplify it. Diversity is the whole point.
- **Aggregate explicitly**: majority vote for binary, mean/median for scores,
  flag-on-any-fail for safety. State the rule.
- **Disagreement is signal, not noise**: cases where the jury splits are exactly
  the ambiguous/hard cases — route them to human review rather than averaging the
  split away. (This is the *correct* use of disagreement — contrast with pairwise
  order-swap disagreement, which means the judge is *unreliable* and the verdict
  should be dropped; see `llm-judge-bias.md`.)
- A jury never substitutes for human calibration — it still drifts as a group;
  anchor it to a human-labeled set.

## Prompted vs fine-tuned judges

| | Prompted judge | Fine-tuned judge |
|---|----------------|-----------------|
| Setup | Prompt only, instant | Needs labeled training data |
| Cost/latency | Higher per call (big model) | Lower (small specialized model) |
| Drift | Moves with base-model updates | Stable until retrained |
| Best for | Early/iterating, low volume | High volume, stable rubric, cost-sensitive |

- Open fine-tuned judges (e.g. Prometheus-family, JudgeLM-style) exist for rubric
  grading; verify the current model, license, and benchmark agreement before
  adopting — judge-model claims age fast (Fact-Checking note in SKILL.md).
- A fine-tuned judge is only as good as its training labels — same human-anchoring
  discipline applies; re-validate agreement after any base/data change.

## Scoring methods that beat 1-10

Raw "rate 1 to 10" is the weakest judge protocol — models cluster at 7-8 (scale
compression) and the numbers aren't comparable across runs. Better:

- **Chain-of-thought before the verdict**: require the judge to reason about the
  rubric criteria *first*, then emit the score. Improves agreement and gives an
  auditable rationale.
- **G-Eval-style probability weighting**: instead of taking the single argmax score
  token, compute the expectation over the judge's output-token probabilities for
  each score — yields a smooth, higher-resolution score that discriminates better
  than a clustered integer. (Needs logprob access.)
- **Decompose the rubric**: score several specific binary/low-cardinality criteria
  ("cites evidence: y/n", "no unsupported claims: y/n") and combine, instead of one
  holistic 1-10. Decomposed criteria are more reliable and more diagnosable.
- **Pairwise/preference over absolute** when you only need "is A better than B" —
  relative judgments are more reliable than absolute scores (with order-swap
  controls from `llm-judge-bias.md`).

## Reference-guided vs reference-free

- **Reference-guided** (judge sees an ideal answer / rubric): much more reliable;
  the judge grades *against a target* instead of its own taste. Prefer it whenever
  you have a reference (ties to `dataset-construction.md` ideal answers).
- **Reference-free** (judge rates quality with no target): necessary for fully
  open-ended generation, but carries the most bias — apply every control and a
  jury, and calibrate hard. Treat reference-free scores as the least trustworthy.

## Measuring judge calibration

A judge you haven't validated is a vibe with JSON output. Quantify it:

- **Agreement with humans**: Cohen's kappa (one judge vs one human), Fleiss' kappa
  or Krippendorff's alpha (multi-rater). Report the coefficient, not just raw
  agreement % — raw % is inflated by class imbalance. (Thresholds and procedure in
  `threshold-derivation.md`.)
- **Calibration of confidence**: if the judge emits a confidence/probability,
  measure **ECE** (expected calibration error) — does "80% confident" mean right
  80% of the time? An overconfident judge poisons any probability-weighted scoring.
- **Re-validate on a schedule and after every base-model change.** Judge agreement
  silently decays; a number from three model versions ago is not evidence.
- **Check for judge-model contamination.** If the judge was pretrained or
  RLHF'd on data that includes your benchmark's questions, reference answers, or
  even the specific eval framework's public repo, its high agreement with the
  "correct" answer may reflect memorization of the benchmark rather than
  genuine discrimination of quality. This inflates kappa/agreement on public
  benchmarks and does not transfer to your private eval set. Mitigate by
  preferring a private, unpublished calibration set for judge validation, and by
  being skeptical of judge agreement numbers measured only on well-known public
  benchmarks the judge model could have seen in training.

### Psychometric calibration (emerging)

Fit **item-response-theory (IRT)** models to the judge's responses across a set of
eval items to estimate per-item difficulty and discrimination parameters, and to
estimate a latent "judge ability" score. Items the judge gets wrong despite low
predicted difficulty flag systematic blind spots; high discrimination items are the
most informative for judge comparison.

- Treat each eval case as an IRT "item" and each judge as a "respondent."
- Estimate a 2-PL or 3-PL IRT model (difficulty + discrimination; optionally
  guessing) from a matrix of judge verdicts across cases.
- Use estimated difficulty scores to detect when a new judge systematically fails
  on items a human rater finds easy.
- **Status:** `validate` only — IRT-based judge calibration is not yet standard
  practice; treat as an experimental diagnostic layer on top of kappa/ECE, not a
  replacement.

## Agentic reward: grading trajectories

Grading a multi-step agent (tool calls, retrieval, sub-goals) is the hardest eval
because there's often no single correct sequence:

- **Outcome reward**: did the final state satisfy the goal? Robust and cheap to
  define, but gives zero partial credit and no diagnosis of *where* it failed.
- **Process/trajectory reward**: grade the steps — was each tool call appropriate,
  were sub-goals achieved, was the path efficient? Enables partial credit and
  pinpoints the failing step, but is harder to specify and easier to game.
- **Use both**: outcome as the gate, trajectory for partial credit and
  attribution. An agent that reaches the right answer by a reckless path
  (unnecessary destructive actions, 10x the tool calls) should not score the same
  as a clean solve.
- **Partial credit needs a rubric**, not a single judge call: define sub-goal
  checkpoints and score completion against them, so "got 4 of 5 steps" is
  measurable.
- **Verifiable sub-steps go to code, not the judge** (Rule 5): tool-call validity,
  schema, did-the-file-compile, did-the-test-pass are deterministic — only the
  genuinely judgment-laden steps (was this reasoning sound?) go to an LLM judge.
- **Reward hacking watch**: trajectory rewards are gameable (an agent learns to
  *look* like it's working). Hold out the outcome gate and periodically human-audit
  high-trajectory-score / low-outcome cases.

## Checklist

- [ ] Single judge only where stakes/agreement justify it; escalate otherwise
- [ ] Juries use *different* model families; aggregation rule stated
- [ ] Jury splits routed to humans, not averaged away
- [ ] Fine-tuned judge choice re-validated for current model/license/agreement
- [ ] CoT-before-verdict and decomposed rubric criteria over raw 1-10
- [ ] Probability-weighted scoring used where logprobs are available
- [ ] Reference-guided preferred; reference-free flagged as least trustworthy
- [ ] Judge agreement reported as kappa/alpha, not raw %; ECE checked if confidence used
- [ ] Judge re-validated after every base-model change
- [ ] Judge-model contamination considered; agreement re-checked on a private, non-public set
- [ ] Agent grading uses outcome gate + trajectory partial credit; verifiable steps in code
- [ ] Reward-hacking audited (high-process/low-outcome cases reviewed)
