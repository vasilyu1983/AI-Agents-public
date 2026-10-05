# LLM-as-Judge Limitations

Use model judges carefully. They are useful, but they are not the ground truth for agent behavior.

## Contents

- [When Judges Help](#when-judges-help)
- [Known Failure Modes](#known-failure-modes)
- [Calibration Gate](#calibration-gate)
- [Escalation Rules](#escalation-rules)
- [When Human Review Beats Automated Judging](#when-human-review-beats-automated-judging)
- [Judge-Model Drift](#judge-model-drift)

## When Judges Help

Model judges are useful for:

- Ranking multiple outputs
- Style or communication checks
- Triage of large eval batches
- Trace grading where objective validation is incomplete

Prefer objective graders first:

- Schema validators
- Code-based assertions
- Tool and trace checks
- Policy oracles

## Known Failure Modes

Judge bias method (position, length/verbosity, self-preference, style,
agreeableness) and its controls are owned by
[ai-evals llm-judge-bias.md](../../ai-evals/references/llm-judge-bias.md). Do not
assume a length-bias direction; it is judge-dependent, so measure it on your own
data. Harness-specific caveats on top of that:

- **Domain gap** — judges are weaker in specialist or high-stakes domains; keep
  an SME-labeled slice.
- **Prompt sensitivity** — a small grader-prompt edit can move scores on
  unrelated cases; version the grader prompt with the suite.
- **Frontier problem** — if the judge is not clearly stronger than the agent
  under test on the graded dimension, treat its verdicts as weak signal.

## Calibration Gate

A judge may decide suite status only after all of the following hold on your own data. Defaults are starting points; tighten them with the stakes of the decision.

1. **Labeled slice.** A human-labeled slice drawn from the same task distribution, large enough that a disagreement rate is a number and not an anecdote (roughly 30 cases as a floor for a smoke pack; size a statistical claim in ai-evals). Include failures, not only passes; a judge validated on passes learns nothing about misses.
2. **Agreement reported, not assumed.** Report agreement with the human labels as a kappa or as separate false-pass and false-fail rates. A false pass on a policy dimension is disqualifying at any rate; the whole point of a gate is that it does not wave through violations.
3. **Stability under perturbation.** Re-judge the slice with candidate order swapped (for pairwise) or with a meaning-preserving paraphrase of the rubric. Any flip on a case the humans marked as clear-cut means the judge is reading form, not substance.
4. **Strength margin.** The judge is clearly stronger than the agent under test on the graded dimension. If not, its verdicts are a weak signal and the dimension needs an oracle or a human.
5. **Versioned.** Judge model id and grader-prompt version are logged per run; a change to either re-runs the slice before the next gated result.

Until the gate holds, judge output is triage: it orders transcripts for a human to read, it does not set `PASS`.

**Never judged, always oracle:** refusal correctness, approval-boundary crossings, forbidden side effects, secret leakage, and action claims with no matching tool call. These are joins against the trace and a policy list; a model judge adds nothing but a failure mode.

## Escalation Rules

Do not rely on model judges alone for:

- High-stakes compliance or legal decisions
- Safety-critical refusal validation
- Expert-domain correctness
- Single-case approval to ship

Treat model judges as one grader type inside a larger evaluation system.

## When Human Review Beats Automated Judging

The routing rule (stakes and reversibility, calibration coverage, verdict flips
under order-swap or paraphrase, small-gate economics) is owned by
[ai-evals advanced-judging.md § Human vs judge routing](../../ai-evals/references/advanced-judging.md#human-vs-judge-routing).
For agent suites: a smoke/regression pack of 15-25 cases is small enough that a
person reading the transcripts usually beats building a judge.

## Judge-Model Drift

Attribution (provider update, grader-prompt edit, shift in the agent's failure
mix) and the re-run cadence are owned by
[ai-evals llm-judge-bias.md § Judge drift](../../ai-evals/references/llm-judge-bias.md#judge-drift).
Log the judge model id and grader-prompt version in `assets/regression-log.md`
for every run so a drift investigation has something to diff against.

## References

- Survey: `https://arxiv.org/abs/2411.15594`
- Limits of scalable assessment: `https://arxiv.org/abs/2410.13341`
- OpenAI graders guide: `https://platform.openai.com/docs/guides/graders`
- LangSmith trajectory evaluators: `https://docs.langchain.com/langsmith/trajectory-evals`
