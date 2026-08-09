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
step-level labels — then PRM.

## Preference Data

Reward-model and DPO quality both trace back to preference-pair quality:

- **Balance and coverage** — pairs should span the prompt distribution you care about; gaps
  become blind spots the policy will exploit.
- **Spurious correlations are the enemy** — if "preferred" responses are systematically longer
  or more formatted, the reward model learns *length/format*, not quality, and the policy then
  inflates length (the classic RLHF length-bias). Control for it (length-penalize, balance).
- **Inter-annotator agreement** — low agreement means the signal is noisy; measure it, and
  consider rubric-anchored labeling.
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

**RLVR removes the reward model entirely**: a deterministic checker (unit tests, a math
verifier, a compiler) is the reward. This is why RLVR is cheaper to run and structurally harder
to over-optimize — there is no learned proxy to hack, only the true objective. Use it whenever
the task has a verifiable answer; fall back to a reward model only when correctness is not
mechanically checkable.

## Routing to Depth

- Algorithm that consumes the reward (PPO/GRPO/DPO) -> [methods-and-pipeline.md](methods-and-pipeline.md)
- Reward hacking, KL control, evaluation -> [over-optimization-and-eval.md](over-optimization-and-eval.md)
- Judge calibration and grader design -> [ai-evals](../../ai-evals/SKILL.md)
- Synthetic-data curation at pretraining scale -> [ai-data-curation-pretraining](../../ai-data-curation-pretraining/SKILL.md)
