# Reward Modeling and Preference Data

The load-bearing inputs to preference-based post-training: the **reward model** (when you use
one) and the **preference data** that trains it or feeds DPO directly. In reward-model RLHF,
final model quality is capped by reward-model quality — this is where most of the leverage and
most of the failure modes live.

## Table of Contents

- [Reward Model Types](#reward-model-types)
- [Outcome vs Process Rewards (ORM vs PRM)](#outcome-vs-process-rewards-orm-vs-prm)
- [Preference Data](#preference-data)
- [Synthetic and AI Feedback (RLAIF / Constitutional AI)](#synthetic-and-ai-feedback-rlaif--constitutional-ai)
- [When You Skip the Reward Model](#when-you-skip-the-reward-model)
- [Verifier Engineering: What "Deterministic Checker" Actually Requires](#verifier-engineering-what-deterministic-checker-actually-requires)
- [Model Merging as a Composition and Attribute-Removal Tool](#model-merging-as-a-composition-and-attribute-removal-tool)
- [Routing to Depth](#routing-to-depth)

## Reward Model Types

| Type | What it is | Use when |
|---|---|---|
| **Bradley-Terry RM** | An LM with a scalar value head trained on preference pairs to predict P(response A preferred to B). The standard reward model. | Classic reward-model RLHF (PPO); the default scalar reward |
| **Generative RM / LLM-as-judge** | A model emits a critique or numeric score rather than a scalar head | Flexible criteria, rubric grading; inherits the judge's biases |
| **Classifier / safety RM** | A discriminative head for a specific axis (toxicity, refusal) | Targeted safety or single-attribute gating |

The **Bradley-Terry** model is the theoretical backbone: it converts pairwise preferences into
a latent scalar reward by assuming preference probability is a logistic function of the reward
difference. DPO's key insight is that this same objective can be optimized *directly on the
policy* without ever materializing the reward model — which is why DPO is "RLHF without the RL."

## Outcome vs Process Rewards (ORM vs PRM)

- **ORM (Outcome Reward Model)** — scores only the final answer. Cheap to label (you only need
  the outcome), but gives no credit assignment across a long reasoning chain.
- **PRM (Process Reward Model)** — scores *each reasoning step*. Better signal for multi-step
  reasoning and harder to reward-hack with a lucky final answer, but needs step-level labels
  (expensive; often synthesized via Monte-Carlo rollouts or model labeling).

Pick ORM unless multi-step reasoning quality is the explicit target and you can afford
step-level labels — then PRM. But **which kind of PRM** is now the live question.

### Discriminative vs generative PRMs

The 2023 framing (*Let's Verify Step by Step*) is **discriminative**: a scalar score per step
from a classifier head. That form is now understood to carry specific failure modes — difficulty
in step segmentation, limited generalization, vulnerability to reward hacking, and training
inefficiencies. Zheng et al., *A Survey of Process Reward Models* (arXiv 2510.08049) is the survey to read for this; that failure-model list reached this
skill via expert review rather than from the survey's abstract, so **read the body before
attributing it**, and quote no magnitudes.

The field's response was **generative** PRMs and verifiers (GenPRM, ThinkPRM, R-PRM, RM-R1,
GRAM are names in circulation — *unverified here; verify each before citing*): the verifier
spends test-time compute *reasoning about* the step and then judges, rather than emitting a
scalar. Costlier per call, and reported to generalize better. Treat "generative is the
better choice where PRMs are used at all" as a direction of travel, not a measured claim.

The practical consequence: the "Generative RM / LLM-as-judge" row in the table above is not only
a rubric-grading convenience — it is the main alternative answer to the process-supervision problem. If
you are targeting multi-step reasoning, do not default to building a discriminative PRM because
that is what the 2023 paper describes. And note the cheapest move first: where the *outcome* is
mechanically checkable, RLVR sidesteps the PRM question entirely.

## Preference Data

Reward-model and DPO quality both trace back to preference-pair quality:

- **Balance and coverage** — pairs should span the prompt distribution you care about; gaps
  become blind spots the policy will exploit.
- **Spurious correlations are the enemy** — if "preferred" responses are systematically longer
  or more formatted, the reward model learns *length/format*, not quality, and the policy then
  inflates length (the classic RLHF length-bias). Control for it (length-penalize, balance).
- **Inter-annotator agreement** — low agreement means the signal is noisy; measure it, and
  consider rubric-anchored labeling.
- **Safety and refusal edge cases** — include them in the preference set deliberately; a set
  drawn only from ordinary traffic teaches nothing about where to refuse.
- **Match the data shape to the method** — pairwise (chosen, rejected) for DPO-family; unpaired
  good/bad labels for KTO; prompts only plus a checker for GRPO/RLVR, since the policy generates
  its own responses.
- **On-policy vs off-policy** — preferences collected from the *current* policy's outputs
  generalize better than stale off-policy pairs for online methods.

## Synthetic and AI Feedback (RLAIF / Constitutional AI)

When human labeling is the bottleneck, generate the preference/critique signal from a model:

- **RLAIF (RL from AI Feedback)** — an LLM ranks/labels responses in place of humans, producing
  preference data at scale. Quality depends on the labeler model and the rubric.
- **Constitutional AI (CAI)** — the model critiques and revises its own responses against a
  written **constitution** (a set of principles), producing both improved SFT data and AI
  preference labels. Scales harmlessness training without a human in every loop.

Synthetic preference data is now standard in open post-training recipes (e.g. Tülu 3), usually
*mixed* with human data rather than replacing it. Watch for model-bias amplification — the
labeler's blind spots become the policy's.

## When You Skip the Reward Model

**RLVR removes the learned reward model**: a deterministic checker (unit tests, a math
verifier, a compiler) supplies the reward. Its cost depends on the checker and rollout workload.
It is **not** automatically the true objective: incomplete tests can reward degenerate solutions,
and wrong labels feed straight into the gradient. A controlled RLVR study found that models
exploited what a rule-induction verifier failed to enforce
([Helff et al.](https://arxiv.org/abs/2604.15149)). Test the checker on plausible shortcuts
and keep an independent task-success measure. Use RLVR when the task has a reliable
verifiable answer; use a reward model — or a **rubric grader** (see
[methods-and-pipeline.md](methods-and-pipeline.md#rubrics-as-rewards-the-fourth-reward-source))
— when correctness is not mechanically checkable.

## Verifier Engineering: What "Deterministic Checker" Actually Requires

"Use a deterministic checker" hides real engineering. A naive `predicted == ground_truth`
verifier fails constantly on correct answers, and every false negative is a wrong reward — the
policy is punished for being right. Since RLVR has no reward model to absorb noise, verifier
defects pass straight into the gradient.

The pipeline below follows Raschka, *Build a Reasoning Model (From Scratch)* (Manning, 2026),
ch. 3 §3.4–3.7, which builds a MATH-500 verifier in four stages: **extract → normalize →
symbolically compare → grade part-wise**.

### 1. Extraction, with a fallback chain

Take the **last** `\boxed{...}` in the output — last, because reasoning traces often mention
intermediate boxed values. Scan for the final `\boxed`, skip whitespace, and **track brace
depth** so nested braces (`\boxed{\dfrac{14}{3}}`) are captured whole; naive matching to the
first `}` truncates the answer.

Then define fallbacks for when no box is present. The book's three modes:

- `number_then_full` (default) — take the last numeric candidate; otherwise the whole text.
- `number_only` — take the last numeric candidate; otherwise the empty string.
- `none` — boxed content only; otherwise the empty string.

The numeric fallback is a regex covering fractions, decimals, and scientific notation. Pick the
mode deliberately: `number_then_full` maximizes recall but can reward a stray number from the
reasoning trace, while `none` is strict and will mark unformatted-but-correct answers wrong.

### Do not use an LLM to extract the answer

Tempting, and wrong for this job. The book's argument, stated directly: using an LLM to extract
the boxed answer "would introduce unnecessary complexity and potential errors. Extraction is a
simple, mechanical task" — locate the last boxed expression, else fall back to a number or the
raw text. A small regex utility "is cheap to execute and handles the extraction deterministically
and reproducibly, without depending on the variability of another model's output."

Three properties are load-bearing for RLVR specifically:

- **Deterministic** — the same rollout scores the same every time, so gradients are not noise.
- **Reproducible** — a run can be replayed, and a reward regression is attributable.
- **No second-model dependency** — an extractor LLM makes reward drift when *it* changes, and
  reintroduces exactly the learned-proxy-to-hack that RLVR exists to eliminate.

Cost matters too: extraction runs on every rollout of every group of every step.

### 2. Normalization (canonicalization)

Rewrite both sides into one canonical form before comparison. What the book's `normalize_text`
handles, and each item exists because it is a real false-negative source:

- **LaTeX variants** — `\dfrac` and `\tfrac` → `\frac`; strip `\left`/`\right`, spacing macros
  (`\,` `\!` `\;` `\:`), and inline/display math wrappers `\(` `\)` `\[` `\]`; `\cdot` → `*`.
- **Structural unwrapping** — unwrap a whole-string `\text{...}`; strip leading multiple-choice
  labels (`c. 3` → `3`); strip chat special tokens (`<|assistant|>`).
- **Unicode superscripts** — map `⁰`–`⁹`, `⁺`, `⁻`, `⁽`, `⁾` to plaintext, attaching them to the
  preceding base as `**`.
- **Degree markers** — remove `^\circ` in its brace and non-brace spellings, and the `°`
  character.
- **Thousands separators** — drop commas inside digit groups, so `1,000` and `1000` agree.
- **Notation conversion** — `\sqrt{a}` → `sqrt(a)`, `\frac{a}{b}` → `(a)/(b)`, `^` → `**`, mixed
  numbers to explicit addition; then strip braces and lowercase.

Normalization is necessary but never sufficient — it makes `\dfrac{14}{3}` and `14/3` comparable,
but cannot see that `28/6` equals `14/3`. That is the next stage's job.

### 3. Symbolic equivalence, not string equality

Compare with a symbolic math engine. The book uses **SymPy**, parsing both sides and testing
whether `simplify(gtruth - pred) == 0`, with an exact string match tried first as the cheap path.

This is what closes the gap string comparison cannot:

- `0.5` vs `1/2` → equal.
- `28/6` vs `14/3` → equal (equivalent but unreduced fractions).
- `13/4.` vs `(13)/(4)` → equal (trailing punctuation and formatting ignored).
- `14/3` vs `15/3` → correctly not equal.

Guard the parser, because rollouts include garbage. The book's parser returns `None` on empty
input or input longer than 2000 characters "to avoid crashing on long garbage responses," and
catches `SympifyError`, `TypeError`, `PolynomialError`, and `TokenError`. Enable
`implicit_multiplication_application` so `2y` parses as `2*y`. **A verifier that throws is worse
than one that returns False** — an exception mid-rollout can kill the training step.

### 4. Grade multi-part answers element-wise

Symbolic comparison on the whole string still fails on tuples: comparing `(14/3, 2/3)` with
`(14/3, 4/6)` returns False despite being mathematically equal, "because it currently handles
only simple expressions, not tuples."

The fix is to split before comparing. Detect a bracketed, comma-containing string (`(a, b)` or
`[a, b]`), split on the commas, strip whitespace, then require **equal part counts** and compare
pairwise, returning True only if every pair matches. Default to False and only upgrade on a
passing check — the grader should fail closed.

### Beyond math: other checkers and strictness

- **Code:** execute the unit tests in a sandbox with time and resource limits; never run
  model-written code on the training host.
- **Structured output:** validate against the schema (and value constraints), not a string match.
- **Strictness is a calibration problem.** A checker that is too lenient pays for degenerate
  answers (reward hacking); one that is too strict marks correct answers wrong and starves the
  gradient. Measure both error rates on a labeled holdout of known-correct and known-wrong
  outputs before the run.

### Verifier checklist

- [ ] Extracts the **last** boxed answer with brace-depth parsing, not first-`}` matching
- [ ] Has an explicit, deliberately chosen fallback when no box is present
- [ ] Extraction is regex/code, **not an LLM call**
- [ ] Normalizes LaTeX variants, unicode superscripts, degree markers, thousands separators
- [ ] Compares symbolically (`simplify(a - b) == 0`), not with `==`
- [ ] Parser is length-capped and wrapped in exception handling; never raises into the loop
- [ ] Splits tuple/list answers and compares element-wise with a part-count check
- [ ] Defaults to False; a failed check is never silently a pass
- [ ] Has its own regression test set of known-equal and known-unequal pairs

That last item is the one most often skipped. The verifier is code that determines every reward
in the run — test it like the load-bearing component it is, with cases covering each
normalization rule above.

## Model Merging as a Composition and Attribute-Removal Tool

Merging combines the *parameters* of several models rather than training a new one. It is
adjacent to post-training rather than part of it: a way to compose already-fine-tuned
checkpoints, and — more interestingly — a way to *remove* behavior.

Taxonomy per Pai, *Designing Large Language Model Applications* (O'Reilly, 2025), ch. 7:

- **Averaging** — average the parameters of the models. The simplest method; the book reports
  simple averaging "has been shown to be quite effective."
- **Weighted averaging** — weight certain models, or certain layers within models, more heavily.
- **Interpolation** — weight each model by a factor `w1…wn` summing to 1, taking
  `w1·p1 + w2·p2 + … + wn·pn` over the parameters.
- **Adapter merging** — merge only a small portion of parameters, e.g. just the adapter modules.
  **AdapterSoup** (Chronopoulou et al.) averages the adapters of the closest domains to handle
  novel domains seen at inference time. **AdaMix** (Wang et al.) learns multiple expert adapter
  modules per layer in an MoE-style framing and merges all adaptation layers at inference.

### The load-bearing insight: fusion keeps what is shared

Zaman et al., as reported by Pai: **when models are fused, the shared capabilities are preserved
while the unshared capabilities are usually lost.** That turns merging from a pure capability-
combination trick into a deliberate instrument for stripping undesirable attributes — if a
behavior lives in only one of the merged models, fusion tends to forget it.

Directional claims attributed to those authors, with no magnitudes (the underlying papers were
not read for this entry — verify before quoting):

- Simple model averaging **reduced** gender and racial bias exhibited by LLMs.
- Merging **reduced** the model's propensity to leak sensitive information, because fusion
  forgets information that is not shared.
- The forgetting effect **strengthens with the number of models fused** ("the more the models
  are fused, the better the forgetting capability").

Treat these as reported directions, not as a quantified safety control. Nothing here establishes
how much bias is removed, whether capability is lost alongside it, or that forgetting is
reliable enough to serve as a privacy guarantee. The same mechanism that drops an unwanted
behavior drops a wanted specialist capability present in only one checkpoint — that is one
property, not two.

### ColD Fusion: merging for organizational reuse

**Collaborative Descent (ColD) Fusion** (Don-Yehiya et al.) targets the case where a base model
is fine-tuned independently by many teams: collect the fine-tuned checkpoints, merge their
weights, and publish the result as the new base version. The related idea is **intertraining** —
the hypothesis that a model already fine-tuned on another task is a better starting point than
the base model. Pai flags this as "a fairly new concept, so proceed with caution."

### Scope note: this is a pointer, not an implementation guide

Merging is adjacent to a post-training *decision* skill, not part of it, and this section is
deliberately left as orientation. The taxonomy above (averaging / weighted / interpolation /
adapter-level) is a sound way to reason about *what* a merge does. The named methods and
tooling — the **TIES / DARE / SLERP** family and the **mergekit** toolchain are the commonly
cited practical path — are **not** covered by the 2025 source above and have not been verified
here. Do not implement from this section: go to current documentation and benchmarks first.

## Routing to Depth

- Algorithm that consumes the reward (PPO/GRPO/DPO) -> [methods-and-pipeline.md](methods-and-pipeline.md)
- Reward hacking, KL control, evaluation -> [over-optimization-and-eval.md](over-optimization-and-eval.md)
- Judge calibration and grader design -> [ai-evals](../../ai-evals/SKILL.md)
- Synthetic-data curation at pretraining scale -> [ai-data-curation-pretraining](../../ai-data-curation-pretraining/SKILL.md)
