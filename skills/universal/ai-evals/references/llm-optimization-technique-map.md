# LLM Optimization Technique Map: Getting Maximum Performance

This file turns research methods into an eval-gated decision ladder. The goal is
not to try every technique. The goal is to choose the cheapest intervention that
fixes the measured failure, prove the lift against a strong baseline, and avoid
training or inference complexity that only improves a benchmark proxy.

## Table of Contents

- [Method families](#method-families)
- [Decision ladder](#decision-ladder)
- [Technique gates](#technique-gates)
- [Measured case: a confidence scorer can be net-negative](#measured-case-a-confidence-scorer-can-be-net-negative)
- [Research-scout idea cards](#research-scout-idea-cards)
- [Composition patterns](#composition-patterns)
- [Kill criteria](#kill-criteria)

## Method families

| Family | Use when | Primary gate |
|--------|----------|--------------|
| Prompt/contract engineering | The base model can solve with clearer instructions, examples, or schema | Same model, same cases, prompt-only delta with cost/latency unchanged |
| Context/RAG/tools | Correctness depends on facts, actions, calculation, state, or citations | Retrieval/tool trace attribution + deterministic checks |
| Test-time compute | The model sometimes knows the answer but greedy decoding underperforms | pass@k / best-of-N lift net of latency and judge/verifier reliability |
| Data construction | Missing behavior can be demonstrated or synthesized safely | Training/dev/gate split hygiene + per-slice data provenance |
| SFT / instruction tuning | You need stable style, format, policy, tool-call, extraction, or routine expert behavior | Paired held-out behavior lift vs prompt/RAG/tool baseline |
| Preference optimization | You have chosen/rejected, binary, or rubric-scored feedback | Human-anchored preference labels + judge/reward calibration |
| RL with verifiable rewards | Correctness is programmatically checkable: math, code, schema, extraction | Verifier precision/recall + reward-hacking replay |
| PEFT / LoRA / QLoRA | You need open-model adaptation under compute/deploy constraints | Same gates as SFT/preference, plus adapter merge/deploy validation |
| Distillation | You need smaller/cheaper models or production latency/cost reduction | Student beats baseline under cost target without losing critical slices |
| Judge/reward model training | Eval volume is high or rubric is stable enough to specialize a judge | Agreement with humans, calibration, drift checks, and bias controls |

## Decision ladder

Run this in order; only climb when the lower rung fails on a real eval:

1. **Clarify the target behavior.** If the requirement cannot be turned into
   cases, rubrics, slices, and release gates, no optimization method is justified.
2. **Baseline the strongest cheap system.** Current prompt + current model +
   retrieval/tools + deterministic validators. Record traces.
3. **Fix prompt/contracts/context/tools.** Most failures are spec, context, or
   tool failures, not weight failures.
3a. **Automatic prompt optimization.** When manual prompt iteration has plateaued
    on a held-out metric, use DSPy MIPROv2-style or platform-native auto-optimizers
    (e.g. Braintrust Loop) to search the prompt space. Gate: held-out metric lift vs
    the best manual prompt baseline on the same dev set; require a *separate* held-out
    gate set because the optimizer overfits the dev split it sees.
4. **Add test-time compute selectively.** Use self-consistency, best-of-N,
   rerank/verify/refine, or search only on cases where uncertainty/complexity
   predicts lift. Gate cost and latency.
5. **Improve data.** Curate high-quality examples, synthetic variants, refusals,
   hard negatives, tool traces, and domain slices. Deduplicate before training.
6. **Tune weights.** Choose SFT, preference optimization, RLVR/RFT, or PEFT based
   on the feedback signal, not hype.
7. **Distill or specialize.** Compress only after the high-quality teacher/system
   is proven; otherwise distillation preserves mistakes.
8. **Promote with online correlation.** Offline lift is a filter; production
   guardrails and drift/replay decide durability.

## Technique gates

| Technique | Stealable method | What to measure | Main traps |
|-----------|------------------|-----------------|------------|
| Few-shot / schema / constrained output | Put the target behavior in the prompt and validate structure in code | Valid schema %, tool-call validity, exact/refusal checks | Prompt overfit, hidden examples leaked into gate |
| Automatic prompt optimization (DSPy MIPROv2 / Braintrust Loop) | When manual prompt iteration plateaus: run optimizer over the dev set, then gate on a separate held-out set | Held-out metric lift vs best manual prompt baseline; separate gate set required | Data-leakage — the optimizer overfits the dev split it sees, making that split stale for gating |
| Chain-of-thought style prompting | Encourage decomposed reasoning for hard reasoning tasks | Accuracy lift on reasoning slice; no extra unsupported claims | Reasoning text can be persuasive but wrong |
| Self-consistency / majority vote | Sample multiple reasoning paths and aggregate final answers | pass@k, marginal lift per extra sample, tie rate | Cost blowup, gains only on benchmark-like tasks |
| Tree/search over thoughts | Explore candidate intermediate states with a heuristic judge/verifier | Solve rate vs node budget, verifier error, latency | Judge becomes the bottleneck; search over bad thoughts |
| Reflexion / self-refine | Use feedback to critique and retry without changing weights | Retry lift, error-fix rate, regression on easy cases | Self-feedback can reinforce wrong assumptions; a confidence-based selector can score *below* no selector at all — see [measured case](#measured-case-a-confidence-scorer-can-be-net-negative) |
| Best-of-N + reranker | Generate candidates, select by reward/judge/verifier | Winner quality vs random candidate, judge agreement; **also measure against no reranker (keep-first / keep-last)** | Reward hacking, verbosity/style bias; likelihood-based rerankers select fluent-but-wrong answers |
| Self-Instruct / Evol-Instruct | Bootstrap diverse instructions, then filter and train | Diversity, dedupe, hard-slice coverage, human spot-checks | Synthetic style collapse, self-training error inheritance |
| LIMA-style curation | Prefer few excellent examples over many noisy ones | Lift per example, author diversity, slice balance | Too narrow or author-style-specific examples |
| RAFT / retrieval-aware tuning | Train the model to answer from retrieved docs, including distractors | Grounded answer rate, citation support, distractor robustness | Encoding stale facts into weights |
| SFT | Teach stable output behavior from demonstrations | Held-out behavior lift, format/tool/refusal slices | Training loss mistaken for quality |
| DPO / SimPO / ORPO | Learn from chosen/rejected pairs without PPO-style RM/rollout complexity | Preference win rate with order/length controls, slice CIs | Label noise, length bias, weak rejected samples |
| KTO / binary feedback | Learn from desirable/undesirable scalar feedback | Calibration of binary labels, production-log slice lift | Feedback imbalance, accidental refusal training |
| RFT / RLVR / GRPO | Optimize against verifiable rewards or programmable graders | Verifier precision, reward/pass correlation, reward-hacking replay | Over-optimizing verifier quirks |
| LoRA / QLoRA | Adapt open models cheaply via adapters/quantized adapters | Same behavioral gates as the objective; adapter merge parity | Capacity too low, target modules wrong, quantization regressions |
| Distilling step-by-step | Train smaller student with labels plus teacher rationales | Student quality/cost Pareto, rationale usefulness, safety replay | Distilling teacher errors or private/unsafe traces |
| Fine-tuned judges/reward models | Replace expensive prompted judges with calibrated specialists | Kappa/alpha vs humans, ECE, slice drift, bias probes | Judge overfits rubric wording; self-preference |

## Measured case: a confidence scorer can be net-negative

The gate rows above name "reward hacking" and "self-feedback reinforces wrong
assumptions" abstractly. This is one published run where the scorer measurably
made things *worse* than having no scorer — useful because it is the ablation
most teams skip.

**Conditions, which the numbers do not survive without:** Sebastian Raschka,
*Build a Reasoning Model (From Scratch)* (Manning, 2026), ch. 5 §5.8, table 5.1
(p. 176). Qwen3 0.6B base model, all 500 samples of the MATH-500 test set, one
GPU configuration (DGX Spark). One model, one task, one run — no confidence
intervals, no seed replication. Treat every row below as **directional evidence
that this failure mode is real**, not as an effect size that transfers.

Base-model rows, quoting the table verbatim:

| Method | Scoring | Iterations | Accuracy | Time |
| ------ | ------- | ---------- | -------- | ---- |
| Baseline (no refinement) | – | – | 15.2% | 10.1 min |
| Self-refinement | None | 1 | 25.0% | 84.8 min |
| Self-refinement | None | 2 | 22.0% | 165.4 min |
| Self-refinement | Heuristic | 1 | 21.6% | 84.7 min |
| Self-refinement | Heuristic | 2 | 20.8% | 151.4 min |
| Self-refinement | Avg. logprob | 1 | 21.4% | 85.3 min |
| Self-refinement | Avg. logprob | 2 | 22.0% | 165.3 min |

What to take from it:

- **The best base-model accuracy came with no scorer at all** (25.0%), above both
  the heuristic scorer (21.6%) and the average-logprob scorer (21.4%). Raschka
  describes the overall gain over baseline as "very moderate" and concludes that
  "both the heuristic score and the average logprob score can sometimes lead to
  incorrect answers being accepted over the initial correct answer."
- **The stated mechanism**: average logprob "is more closely related to how
  natural or expected an answer looks under the model than to whether the answer
  is actually correct… it can favor answers that are fluent, familiar, or
  syntactically clean, even when they are semantically wrong. In other words, the
  logprob criterion can unintentionally select confident mistakes."
- **A second refinement iteration did not reliably help.** It lowered accuracy in
  the None (25.0% → 22.0%) and Heuristic (21.6% → 20.8%) rows and raised it
  slightly in the Avg. logprob row (21.4% → 22.0%), while roughly doubling
  runtime in each.
- **Cost is not incidental**: the cheapest refinement row took 84.8 min against
  10.1 min for the unrefined baseline — roughly 8x on this setup — for the ~10pp
  gain.
- **The direction reverses on the reasoning model.** On the same task, rows 8–11
  show the reasoning-model baseline at 48.2% and heuristic-scored refinement at
  57.8%, with avg-logprob scoring at 48.4% — so "scorer hurts" is not a general
  law even within this one table. What generalizes is that *the scorer's value is
  an empirical question per model and task*, not an assumption.
- Raschka also reports that self-refinement was **less effective than
  self-consistency** for this model on this math task.

**The eval consequence.** Whenever you add a reranker, verifier, or refinement
scorer, the mandatory arm is *the same pipeline with the scorer removed*
(keep-first or keep-last). Comparing "scorer vs no pipeline" hides the case where
the pipeline helps and the scorer inside it hurts. Likelihood-shaped scorers —
average logprob, perplexity, self-reported confidence — are the ones to distrust
first: they rank fluency, and fluency and correctness come apart exactly on the
hard slice you built the eval for. Prefer a scorer with an outside signal
(tests, a verifier, an execution result) over one derived from the generating
model's own probabilities.

## Research-scout idea cards

These are method cards, not a literature review. arXiv entries are preprints
unless otherwise noted; promote only after local gates pass.

### Idea: Automatic prompt optimization

**Source(s):** DSPy MIPROv2 (`arXiv:2310.03714`); platform-native auto-optimization
(Braintrust Loop and similar — verify current feature availability).
**Method shape(s):** `prompting-pattern`, `evaluation-method`.

Use a structured optimizer (instruction + few-shot selection search) to find a
prompt that maximizes a held-out metric automatically. Use when manual prompt
iteration has plateaued and you have enough labeled examples to support a dev/gate
split.

**Eval transfer:** measure held-out metric lift vs the best manual prompt baseline
on the same dev set; then gate on a *separate* held-out gate set — the optimizer
overfits the dev split it sees, making that split stale for final gating.
**Trap tags:** `data-leakage-suspicion` (dev-split overfitting), `benchmark-overfit`.
**Status:** `validate` — confirm local lift on a separate gate set before promoting
optimizer-tuned prompts to production.

### Idea: Sample-and-aggregate reasoning

**Source(s):** Self-consistency (`arXiv:2203.11171`), Tree of Thoughts
(`arXiv:2305.10601`), test-time compute survey (`arXiv:2501.02497`).
**Method shape(s):** `prompting-pattern`, `inference-time-method`.

Generate multiple reasoning paths or search over intermediate "thoughts", then
aggregate or select the answer. Use when the task has a checkable or stable final
answer and the base model is inconsistent rather than ignorant.

**Eval transfer:** measure pass@k, marginal lift per extra sample, latency/cost,
and whether gains survive fresh cases.
**Trap tags:** `compute-asymmetry`, `benchmark-overfit`, `negative-trade-off-hidden`.
**Status:** `promote` for cheap self-consistency on high-value hard slices;
`validate` for deeper search unless the verifier is strong.

### Idea: Critique-retry loops

**Source(s):** Reflexion (`arXiv:2303.11366`), Self-Refine (`arXiv:2303.17651`).
**Method shape(s):** `prompting-pattern`, `inference-time-method`,
`system-design-pattern`.

Have the model or an external verifier produce feedback on a failed attempt, then
retry with that feedback as context. Best for coding, tool-use, extraction, and
agent tasks where failures are inspectable.

**Eval transfer:** compare first-attempt vs retry success, easy-case regression,
and whether the feedback is grounded in traces/tests.
**Trap tags:** `negative-trade-off-hidden`, `benchmark-overfit`.
**Status:** `promote` when feedback comes from tests/tools/humans; `validate`
when feedback is only self-critique.

### Idea: High-signal instruction data over volume

**Source(s):** Self-Instruct (`arXiv:2212.10560`), LIMA (`arXiv:2305.11206`),
WizardCoder/Evol-Instruct (`arXiv:2306.08568`).
**Method shape(s):** `data-construction-recipe`, `training-recipe`.

Use synthetic instruction generation and evolution to expand coverage, but
promote only examples that survive filtering, dedupe, human review, and slice
coverage checks. Treat a small curated set as a strong baseline before scaling.

**Eval transfer:** lift per example, diversity, near-duplicate leakage, hard-slice
coverage, and human spot-check acceptance.
**Trap tags:** `data-leakage-suspicion`, `hype-bubble`, `narrow-applicability`.
**Status:** `promote` for curated demonstrations; `validate` for synthetic-only
training data.

### Idea: Retrieval-aware fine-tuning

**Source(s):** RAFT (`arXiv:2403.10131`).
**Method shape(s):** `training-recipe`, `data-construction-recipe`,
`system-design-pattern`.

Train the model to answer from retrieved documents and ignore distractors. This
belongs between RAG and SFT: use it when retrieval is stable enough to teach
behavior, but facts still live in the corpus.

**Eval transfer:** grounded answer rate, citation support, distractor robustness,
and regression on unanswerable queries.
**Trap tags:** `narrow-applicability`, `data-leakage-suspicion`.
**Status:** `validate` until your local corpus/distractor distribution is tested.

### Idea: Direct preference optimization family

**Source(s):** DPO (`arXiv:2305.18290`), KTO (`arXiv:2402.01306`), ORPO
(`arXiv:2403.07691`), SimPO (`arXiv:2405.14734`).
**Method shape(s):** `training-recipe`.

Choose the loss from the feedback signal: DPO/SimPO/ORPO for chosen-vs-rejected
pairs; KTO for desirable/undesirable scalar feedback; keep PPO-style RLHF as the
complex last resort for subjective rewards that need a learned reward model.

**Eval transfer:** preference win rate with order and length controls, human
agreement, label quality, slice CIs, and rejected-sample strength.
**Trap tags:** `cherry-picked-baselines`, `benchmark-overfit`, `data-leakage-suspicion`.
**Status:** `promote` only with clean preference labels and a held-out pairwise gate.

### Idea: Verifiable-reward reasoning optimization

**Source(s):** DeepSeekMath/GRPO (`arXiv:2402.03300`), DeepSeek-R1
(`arXiv:2501.12948`), DAPO-family work (emerging; verify current paper/support).
**Method shape(s):** `training-recipe`, `evaluation-method`.

Use programmable rewards or graders where correctness can be checked: math,
code, schemas, extraction, formal constraints, or tool outcomes. The verifier is
the product: if it is wrong or gameable, the training will optimize the wrong
thing.

**Eval transfer:** verifier precision/recall, reward/pass correlation, held-out
hard cases, reward-hacking probes, and entropy/collapse telemetry.
**Trap tags:** `benchmark-overfit`, `compute-asymmetry`, `benchmark-gaming`.
**Status:** `promote` for truly verifiable tasks; `validate` for open-ended
reasoning judged by an LLM.

### Idea: Rationale and behavior distillation

**Source(s):** Distilling Step-by-Step (`arXiv:2305.02301`), Constitutional AI
(`arXiv:2212.08073`), Self-Rewarding Language Models (`arXiv:2401.10020`).
**Method shape(s):** `training-recipe`, `data-construction-recipe`,
`evaluation-method`.

Distill a stronger teacher/system into a cheaper student using labels, rationales,
critiques, or preference/reward signals. Use this after the teacher behavior is
proven, not before.

**Eval transfer:** student-vs-teacher quality/cost Pareto, critical-slice
retention, rationale usefulness, and safety replay.
**Trap tags:** `proprietary-component`, `data-leakage-suspicion`, `negative-trade-off-hidden`.
**Status:** `validate` unless the teacher data is licensed, safe, and locally
verified.

## Composition patterns

- **Quality-first assistant:** prompt/schema baseline -> curated SFT -> DPO/SimPO
  on real preferences -> online guardrails.
- **Reasoning model:** hard-case eval -> self-consistency/best-of-N baseline ->
  verifier -> GRPO/RFT if verifier precision is high -> distill if cost matters.
- **RAG expert:** retrieval eval -> grounding/citation gate -> RAFT-style
  behavior tuning only for stable corpus interactions -> drift replay.
- **Tool agent:** deterministic tool-contract eval -> trace grader -> critique
  retry -> SFT on correct traces -> RFT only with reliable tool outcome rewards.
- **Cheap production model:** prove frontier/large-model behavior -> distill
  step-by-step into smaller model -> regression/safety replay -> canary rollout.

## Kill criteria

Stop an optimization path when any of these happen:

- It does not beat the best prompt/context/tool baseline on paired held-out cases.
- It improves the aggregate but regresses a critical slice, safety set, or tool
  contract.
- Its gains disappear after order/length controls, fresh cases, or contamination
  checks.
- The lift costs more in latency, tokens, labeling, or training than the product
  value of the improvement.
- The method needs proprietary teacher/judge data that cannot be licensed,
  audited, or replaced.
- The verifier/judge can be gamed by examples that a human would reject.
