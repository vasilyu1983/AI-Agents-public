# Fine-Tuning Eval Loop: From Baseline to Promotion

Fine-tuning is not a magic quality lever. It is a controlled intervention that
changes model behavior. The only defensible reason to do it is that a frozen,
held-out eval shows a specific behavioral gap that cheaper changes cannot close,
and a post-training eval shows the tuned model fixes that gap without unacceptable
regressions.

## Table of Contents

- [Decision ladder](#decision-ladder)
- [Technique selection](#technique-selection)
- [Dataset design for tuning](#dataset-design-for-tuning)
- [Split hygiene](#split-hygiene)
- [Training telemetry vs behavioral evidence](#training-telemetry-vs-behavioral-evidence)
- [Promotion gate](#promotion-gate)
- [Regression and safety replay](#regression-and-safety-replay)
- [Operational checklist](#operational-checklist)

## Decision ladder

Use the cheapest intervention that can plausibly fix the attributed failure:

1. **Prompt / instructions**: if the model can do the task when asked clearly,
   fix the prompt and contracts first.
2. **Retrieval / context**: if the answer depends on changing facts, proprietary
   evidence, citations, or freshness, use RAG/context, not fine-tuning.
3. **Tools / schemas**: if the failure is calculation, lookup, workflow state, or
   structured side effects, fix the tool contract and deterministic checks.
4. **Supervised fine-tuning (SFT)**: if the desired behavior is stable and
   demonstrable in examples: style, format, domain phrasing, tool-call patterns,
   extraction shape, classification policy, or routine expert procedure.
5. **Preference tuning / RFT / RL-style optimization**: if there are many valid
   outputs and quality is a rubric-scored tradeoff: reasoning depth, explanation
   quality, ranking, synthesis, or expert judgment.
6. **PEFT / LoRA / QLoRA**: if adapting an open model under limited compute,
   memory, or deployment constraints. Treat it as a training method choice, not
   proof that the product should be fine-tuned.

If the eval cannot say which failure class dominates, do not train yet. Improve
failure attribution first.

## Technique selection

| Need | Prefer | Why | Avoid when |
|------|--------|-----|------------|
| Stable target outputs | SFT | Teaches input -> desired output patterns directly | The correct output depends on changing knowledge |
| Better tool-call syntax / JSON | SFT + deterministic schema eval | Examples teach shape; code grades validity | Tool semantics are unclear or tools are missing |
| Expert reasoning scored by rubric | RFT / preference optimization | Rewards higher-scoring candidates when many answers are valid | The grader is weak or uncalibrated |
| Align pairwise preferences | DPO / preference tuning | Learns from chosen vs rejected outputs | Preference data is noisy or lacks disagreement handling |
| Cheap open-model adaptation | LoRA / QLoRA via PEFT stack | Reduces trainable params and memory | You need full-model adaptation or new world knowledge |
| Domain facts | RAG / context | Keeps evidence current and citeable | The goal is stable behavior, not knowledge access |

Default expert stance: **SFT for imitation, preference/RFT for judgment, RAG for
knowledge, tools for deterministic work, PEFT for efficient open-model training**.

> **AWS stack**: route fine-tuning to **SageMaker Training Jobs** (full-framework
> SFT/RL) or **Bedrock Custom Model Import** (bring a fine-tuned open model into
> the Bedrock serving layer) rather than the HuggingFace/OpenAI paths above.
> The eval loop and technique-selection criteria remain the same; only the
> training surface and deployment path differ.

## Dataset design for tuning

The training set should be a deliberately shaped intervention, not a dump of
everything available.

- Start from **attributed eval failures**: each new training example should map to
  a failing requirement, slice, or behavior you want to move.
- Include **positive and negative coverage** where relevant. For refusal/safety
  work, pair harmful prompts with benign-adjacent should-comply prompts to avoid
  over-refusal.
- Preserve the **real input distribution**, then over-sample high-impact rare
  slices with explicit weights/metadata.
- Deduplicate semantically, not only by exact string. Near-duplicates inflate
  training and leak across splits.
- Remove PII/secrets and document provenance. Production logs are useful only
  after privacy and licensing review.
- For SFT, examples must show the **final behavior you actually want**, including
  formatting, citations, tool calls, abstention, and tone.
- For preference/RFT, labels must encode the **rubric tradeoff**, not author
  taste. Capture why the winner is better.
- Keep a small **canary set** of known failure modes that should never improve by
  accidental leakage; investigate if scores jump implausibly.

Training data quality beats volume. If 50 excellent examples do not move a
simple SFT target, adding 5,000 weak examples usually teaches noise.

## Split hygiene

Use separate sets with separate jobs:

- **Train**: examples used to update weights or adapters.
- **Dev**: examples used to inspect failures and iterate data/prompt/grader.
- **Judge calibration**: human-labeled cases used to calibrate thresholds or
  judge agreement.
- **Gate / holdout**: frozen cases used for release decisions.
- **Safety/regression replay**: durable cases that protect critical behavior.

Rules:

- No exact, near-duplicate, or paraphrase leakage from train/dev into gate.
- Do not use the release gate to pick epochs, thresholds, prompts, or
  hyperparameters.
- If a gate case is edited, bump the dataset version and explain why.
- If the tuned model trains on data produced by another model, keep a
  human-anchored subset to detect style imitation and error inheritance.
- When using LLM-generated training data, run contamination and diversity checks;
  synthetic examples are a supplement, not the evidence base.

## Training telemetry vs behavioral evidence

Training and validation loss are diagnostics. They are not product quality.

- Falling train loss + flat held-out behavior means the model learned the wrong
  surface pattern or the eval target is not represented in the training data.
- Falling train loss + worse safety/format/tool behavior means overfitting or
  negative transfer.
- Better aggregate score + worse critical slice is not a win unless the product
  owner explicitly accepts that tradeoff.
- Earlier checkpoints can beat later checkpoints. Promote the checkpoint with the
  best held-out behavioral tradeoff, not the final epoch by habit.
- For stochastic models, compare multiple samples or pass@k where appropriate;
  one lucky tuned output is not a promotion signal.

Log every run with base model, tuned model/checkpoint, dataset versions, prompt
version, decoding params, training method, and grader versions.

## Promotion gate

A fine-tuned model earns release only if it beats the strongest reasonable
baseline on a paired, frozen evaluation:

1. Run **base + current prompt/RAG/tools** and **candidate tune + same surrounding
   system** on the same gate cases.
2. Report the primary metric with confidence intervals and a paired test where
   applicable (`eval-statistics.md`).
3. Require slice-level checks for high-impact categories, not just aggregate lift.
4. Re-run deterministic contracts: schema validity, tool-call validity,
   citation requirements, refusal rules, latency/cost ceilings.
5. Compare against a **prompt-only improvement baseline**. If prompt changes get
   the same lift, do not pay the fine-tune complexity tax.
6. Require human review for disagreement-heavy or high-stakes cases.
7. Record a rollback plan: previous model, dataset version, and trigger metrics.

The release note should state: what failure the tune targeted, what data changed,
what baseline it beat, which slices moved, which slices regressed, and what is
being watched online.

## Regression and safety replay

Post-training models can regress in surprising places. Always replay:

- The previous release gate.
- Known incident/regression cases.
- Safety/red-team cases, including over-refusal and should-comply sets.
- Tool-use and structured-output contracts.
- Long-context, multilingual, and domain-edge slices if the product uses them.
- Production shadow/canary traffic once offline gates pass.

If an offline gain fails online correlation, do not keep training blindly. Audit
distribution mismatch, tracing, data recency, and whether the grader rewarded a
proxy that users do not value.

## Operational checklist

- [ ] Failure attribution shows training is the right intervention
- [ ] Prompt/RAG/tool baselines attempted or explicitly ruled out
- [ ] Technique chosen: SFT, preference/RFT, PEFT, or no fine-tune
- [ ] Train/dev/calibration/gate/replay splits separated
- [ ] Near-duplicate and synthetic-data leakage checked
- [ ] Training examples mapped to target failures/slices
- [ ] Grader calibrated before RFT/preference use
- [ ] Candidate compared against base on paired frozen cases
- [ ] CIs/tests reported; primary metric pre-declared
- [ ] Critical slices, safety, tool/schema, cost, and latency replayed
- [ ] Release note includes tradeoffs and rollback trigger
