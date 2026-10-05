# GRPO Run Diagnostics

How to read a **live GRPO/RLVR training run**. Over-optimization
([over-optimization-and-eval.md](over-optimization-and-eval.md)) is about the proxy silently
diverging from the true objective over a whole run; this file is the narrower, in-flight
question: given the numbers scrolling past right now, is the run healthy, is it learning
nothing, or is it about to destabilize?

Source for the metric semantics: Raschka, *Build a Reasoning Model (From Scratch)* (Manning,
2026), ch. 7 §7.2.2–7.3.3 — a Qwen3-0.6B RLVR/GRPO run on MATH-500. Treat the thresholds as
that book's rules of thumb from that configuration, not as universal constants.

## Table of Contents

- [The Metric Set](#the-metric-set)
- [Advantage Mean: a Sanity Check, Not a Signal](#advantage-mean-a-sanity-check-not-a-signal)
- [Advantage Std: the Learning-Signal Gauge](#advantage-std-the-learning-signal-gauge)
- [Degenerate Groups: Zero Gradient from All-Correct and All-Wrong Alike](#degenerate-groups-zero-gradient-from-all-correct-and-all-wrong-alike)
- [Average Reward: 1.00 Means Stop](#average-reward-100-means-stop)
- [Entropy: Direction Is Ambiguous, Read It in Context](#entropy-direction-is-ambiguous-read-it-in-context)
- [Loss and Response Length](#loss-and-response-length)
- [Read the Metrics Jointly](#read-the-metrics-jointly)
- [Triage Table](#triage-table)
- [Routing to Depth](#routing-to-depth)

## The Metric Set

Track these together per step; none of them is interpretable alone.

| Metric | What it is | Primary use |
|---|---|---|
| `adv_avg` | Mean of the group-normalized advantages | Implementation sanity check only |
| `adv_std` | Std of the group-normalized advantages | Is there a usable learning signal? |
| `reward_avg` | Mean verifier reward over the sampled rollouts | Progress, and the exhaustion signal |
| `entropy_avg` | Mean per-token entropy of the generated answer tokens | Exploration vs determinism vs collapse |
| `loss` | Policy-gradient loss | Weak sanity check; should stay relatively stable |
| `avg_response_len` | Mean generated answer length | Length inflation / degenerate-brevity watch |
| `eval_acc` | Held-out benchmark accuracy (e.g. MATH-500) | The *actual* objective; the others are proxies |

Evaluation accuracy is the only entry that measures what you want. In Raschka's run it is
computed periodically rather than per step — the book notes that computing it on every
checkpoint "significantly slows down training" and recommends running it separately after
training instead.

## Advantage Mean: a Sanity Check, Not a Signal

GRPO computes advantages by subtracting the group mean and dividing by the group std, so
**the mean is zero by construction**. Raschka: "Because of how advantages are computed in
GRPO, their mean is always zero. In practice, this makes the mean mostly a sanity check that
the implementation behaves as expected."

The diagnostic value is therefore entirely negative:

- `adv_avg ≈ 0` tells you nothing about learning. Do not read it as progress.
- `adv_avg` **drifting away from zero is a bug** — "that would point to a bug or a
  normalization issue," not to a training dynamic. Go read the advantage computation; do not
  tune hyperparameters in response to it.

## Advantage Std: the Learning-Signal Gauge

This is the informative half of the advantage statistics. Raschka's reading, for that run:

- **Close to 1** — "a well-scaled gradient signal," usually associated with stable updates.
- **Very small** — "a vanishing learning signal, which often happens when rewards collapse."
- **Very large** — "overly spiky updates that can destabilize training."

The trajectory matters as much as the level. In the book's run the std starts relatively high
(rollouts vary widely in quality), then "gradually decreases and stabilizes," meaning rollouts
are converging in quality. The stated pass condition is a trend, not a threshold: **as long as
`adv_std` stays nonzero and reasonably stable, a usable learning signal remains and training is
still happening.**

## Degenerate Groups: Zero Gradient from All-Correct and All-Wrong Alike

The extreme case is worth calling out separately because it is easy to misread as progress.

When every rollout in a sampled group receives an identical reward, the normalized advantages
are all identical, `adv_std` is 0, **the policy-gradient update is zero, and no weight update
occurs** — "the model fails to learn from these cases."

The trap: this is symmetric. A group where all four rollouts are **wrong** teaches the model
nothing, and so does a group where all four are **right**. Raschka demonstrates it with
all-zero rewards and notes "the outputs are similar" when the all-zero rewards are replaced
with all-one rewards. A prompt too hard for the current policy and a prompt already mastered
are equally worthless for that step, and only the all-correct case looks good on the reward
curve.

This is the mechanism behind the dynamic-sampling fix listed in
[methods-and-pipeline.md](methods-and-pipeline.md) — DAPO drops all-correct and all-wrong
groups so the batch is not padded with prompts contributing zero gradient. If a large fraction
of groups is degenerate, the effective batch size is far smaller than the nominal one.

Dynamic sampling removes these groups *during* the run, after paying for their rollouts. The
cheaper complement is **before** the run: sample each training prompt k times from the starting
policy, record its pass rate, and drop prompts at 0/k (too hard for now) or k/k (already
mastered). Re-run the filter when the policy improves, because mastered prompts accumulate.

## Average Reward: 1.00 Means Stop

Rising `reward_avg` is the expected direction, but the ceiling is a stopping condition rather
than a win. Raschka: "an average reward of 1.00 means that all sampled responses are correct,
which is desirable, but it also means that the training signal has disappeared. At that point,
further training is unlikely to be useful, and stopping early can save us time and resources."

The two responses, per the book: **stop training, or switch to more challenging examples.** A
reward curve pinned at the ceiling is the same zero-gradient condition as the all-correct
degenerate group, just measured across the whole batch — harden the data or end the run.

Note the granularity: with `num_rollouts=4`, `reward_avg` moves in quarter steps, so
intermediate values (0.250, 0.500) reflect how many of the four rollouts were correct.

## Entropy: Direction Is Ambiguous, Read It in Context

Entropy measures how spread out the next-token distribution is: high = exploratory/random,
low = deterministic. Raschka's rough rule of thumb, stated for a toy 7-token vocabulary
example:

- Very low (≈ 0–0.5): one token dominates the distribution.
- Moderate (≈ 1–2): probability shared across a reasonably small set of tokens.
- High (approaching log of vocabulary size — log(7) = 1.9459 in that example): near-uniform.

Those numbers are anchored to that illustration's vocabulary, not to a production model's;
carry the *shape* of the rule, not the constants.

Two directional claims sit in the text, and they must be held together rather than collapsed
into one expectation:

- **The prior**: "we expect entropy to gradually decrease as the model becomes more confident.
  A sudden collapse to very low entropy can be a warning sign of unstable training." Very low
  entropy "can also be a sign of collapse, where the model repeatedly produces the same or very
  similar outputs" — the repetition-collapse failure mode.
- **What that run actually did**: entropy started relatively low and flat, then "after roughly
  step 200, entropy increases quite noticeably." The book reads this *not* as a failure but as
  "somewhat healthy exploration rather than collapse" — because reward was still rising,
  `adv_std` had not vanished, and MATH-500 accuracy stayed "in the 30%–40% range," which the
  book calls "not great, but it is not near zero."

The operational lesson is the caveat, not the prior: **an entropy trajectory alone does not
classify a run.** Rising entropy is not automatically instability, and falling entropy is not
automatically progress. Only the sudden collapse toward zero is a standalone warning, and even
that should be confirmed against reward and `adv_std`.

## Loss and Response Length

- **Loss** is a weak signal here. Unlike pretraining, "the loss value itself is less
  informative and mainly serves as a sanity check. Overall, the loss should remain relatively
  stable. Some fluctuations are expected," but large spikes appearing partway through a run are
  described as "somewhat concerning." Do not over-interpret magnitude: steps where
  `reward_avg` is 0.000 produce identical rewards, hence near-zero advantages and little to no
  gradient signal.
- **Response length** should "initially increase, ideally, along with an improvement in
  accuracy." A later decline is a flag worth investigating rather than a neutral fact. Sustained
  growth without accuracy gains is the GRPO length-inflation bias — see
  [methods-and-pipeline.md](methods-and-pipeline.md) for the Dr. GRPO / DAPO fixes.

## Read the Metrics Jointly

The book's closing point on the metric set is the one to carry: "each metric tells a slightly
different part of the story, and they are most useful when considered together and in context."

The run analyzed there is a concrete example of why. It shows fast gains early, then
diminishing returns after roughly 50 steps, loss spikes partway through, response length
rising then declining, and **evaluation accuracy that increases at first and then begins to
decline** — which the book reads as pointing "to problems and instabilities in the training
process." Crucially, the held-out accuracy turned over while the in-run metrics still looked
defensible. Instrument `eval_acc`, or you will not see this.

## Triage Table

| Observation | Reading | Action |
|---|---|---|
| `adv_avg` drifts off zero | Normalization/implementation bug | Fix the advantage computation; ignore other metrics until clean |
| `adv_std` → 0 | Vanishing signal; rewards collapsed or groups degenerate | Check reward distribution; harden or re-balance prompt difficulty |
| `adv_std` very large | Spiky, destabilizing updates | Clip, lower LR, or revisit reward scale |
| `adv_std` nonzero and stable | Usable learning signal present | Continue |
| Many all-identical-reward groups | Zero gradient from those prompts; effective batch shrinks | Dynamic sampling (drop all-correct/all-wrong); re-target difficulty |
| `reward_avg` → 1.00 | Training signal exhausted | Stop, or move to harder examples |
| Entropy suddenly collapses toward 0 | Possible repetition collapse / instability | Confirm against reward + `adv_std`; inspect samples for repetition |
| Entropy rising, reward rising, `adv_std` alive | Plausibly healthy exploration | Continue, keep watching held-out accuracy |
| `eval_acc` declining while reward rises | Instability or over-optimization | Stop or roll back to the best checkpoint; this outranks every in-run metric |

## Routing to Depth

- Goodhart symptoms, KL control, evaluating the true objective ->
  [over-optimization-and-eval.md](over-optimization-and-eval.md)
- GRPO's named biases and their fixes (Dr. GRPO, DAPO dynamic sampling, GSPO) ->
  [methods-and-pipeline.md](methods-and-pipeline.md)
- Building the verifier that produces `reward_avg` -> [reward-and-data.md](reward-and-data.md)
- Benchmark methodology and threshold setting -> [ai-evals](../../ai-evals/SKILL.md)
