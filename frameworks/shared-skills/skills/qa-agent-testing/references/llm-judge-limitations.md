# LLM-as-Judge Limitations

Use model judges carefully. They are useful, but they are not the ground truth for agent behavior.

## Contents

- [When Judges Help](#when-judges-help)
- [Known Failure Modes](#known-failure-modes)
- [Mitigations](#mitigations)
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

### Position bias

In pairwise or multi-way comparisons, judges systematically favor whichever response appears in a particular slot (commonly the first, though the direction can vary by judge model and prompt), independent of quality. This is a distinct, well-documented bias from verbosity or self-preference below — test for it directly by swapping response order and checking whether the verdict flips.

### Verbosity bias

Judges tend to score longer, more elaborated responses higher even when the extra length adds no information — a documented tendency sometimes called "length bias." If your rubric does not explicitly penalize unnecessary length, a verbose-but-shallow response can out-score a concise-but-correct one. Mitigate by adding an explicit conciseness criterion to the grader prompt and by spot-checking whether score correlates with response length in your own data.

### Self-preference bias (model-family bias)

Some judges score outputs from their own model family (or closely related models) more favorably than outputs from other families, even when a blind human rater would not distinguish them. This matters most when using a frontier model both to generate candidate outputs and to judge which candidate is better — treat any such setup as a documented risk to control for (cross-family judge panels, blind human spot-checks), not something to assume away.

### Domain gap

Judges are weaker in specialized or high-stakes domains where SMEs matter.

### Prompt sensitivity

Small grader-prompt changes can materially change scores.

### Frontier problem

If the judge is not clearly stronger than the system being judged, score quality becomes less trustworthy.

## Mitigations

- Randomize answer order for pairwise comparisons.
- Use structured grader prompts tied to explicit criteria, including an explicit conciseness or length-neutrality instruction to counter verbosity bias.
- Keep a human-labeled calibration set.
- Log judge model, grader prompt, and grader version.
- Use multiple judge families for ranking tasks if the cost is justified, especially when the system under test and the judge share a model family.
- Escalate borderline or high-stakes cases to human review.

## Escalation Rules

Do not rely on model judges alone for:

- High-stakes compliance or legal decisions
- Safety-critical refusal validation
- Expert-domain correctness
- Single-case approval to ship

Treat model judges as one grader type inside a larger evaluation system.

## When Human Review Beats Automated Judging

A judge model is not a substitute for a human reviewer in every situation — it is a substitute in the situations where its known failure modes do not touch the decision. Use this as a working test, not a checklist to satisfy mechanically:

- **Stakes and reversibility.** If a wrong call ships something that is expensive or slow to undo (a compliance answer, a safety refusal boundary, a financial or medical claim), route it to a human. Judges are a throughput tool for volume, not a risk-transfer tool for consequence.
- **Novelty relative to the calibration set.** A judge calibrated against a human-labeled set is only as trustworthy as that set's coverage. When a batch contains a task shape, domain, or failure mode not represented in calibration, treat judge output on that batch as a hypothesis, not a verdict — spot-check it with a human before trusting the aggregate.
- **Disagreement density.** If re-running the same judge with a paraphrased prompt or swapped order changes a meaningful fraction of verdicts (track this — it is cheap to measure), the judge is not stable enough to be the sole gate for that rubric dimension yet, regardless of its average accuracy.
- **Volume economics, inverted.** Judges exist because human review of every case does not scale. But when the batch is small (a release gate of 10-25 regression cases, not thousands of production samples), the cost argument for skipping human review mostly disappears — a person can read 20 transcripts in the time it takes to build and validate a judge prompt.

Rule of thumb: use judges to triage volume down to a manageable set of borderline or flagged cases, then have a human make the actual high-stakes call on that smaller set. Do not skip straight from "judge said PASS" to "ship" for anything you would regret getting wrong.

## Judge-Model Drift

Judge behavior is not fixed over time, and this is a distinct risk from the biases above — it is about your calibration silently going stale, not about a structural bias in a single judge call.

- **What drifts:** the underlying judge model's provider-side updates (even "same model" endpoints can change behind a stable name), your grader prompt (edited for one fix, quietly changing scores on unrelated cases), and the task distribution itself (your agent's failure modes shift as it evolves, and old calibration examples stop representing current risk).
- **Why it is dangerous:** drift is invisible until you compare against a fixed reference. A suite that reports a stable pass rate over months can be silently drifting if the judge is drifting in the same direction as the system under test, or masking a real regression if the judge is drifting in the opposite direction.
- **Detection:** re-run your human-labeled calibration set on a fixed cadence (monthly is a reasonable default for active projects; tighten it after any provider-side model update you did not initiate) and alert if judge-vs-human agreement drops below your established baseline (see agreement thresholds in `eval-dataset-design.md`). Log the judge model identifier and grader-prompt version with every run so a drift investigation has something to diff against.
- **Response:** when drift is detected, do not just re-calibrate and move on — determine whether the drift came from the judge, the grader prompt, or a real shift in the agent's behavior, since the fix differs in each case.

## References

- Survey: `https://arxiv.org/abs/2411.15594`
- Limits of scalable assessment: `https://arxiv.org/abs/2410.13341`
- OpenAI graders guide: `https://platform.openai.com/docs/guides/graders`
- LangSmith trajectory evaluators: `https://docs.langchain.com/langsmith/trajectory-evals`
