# Post-Training Methods and the Pipeline

How the post-training stage maps a **reward signal** to an **algorithm**. This file owns the
*selection logic and pipeline*; per-algorithm operational depth (hyperparameters, loss forms,
implementation notes) lives in
[ai-llm/references/post-training.md](../../ai-llm/references/post-training.md) — link there
rather than duplicating it.

## Table of Contents

- [The Pipeline, Stage by Stage](#the-pipeline-stage-by-stage)
- [The Two Orthogonal Axes](#the-two-orthogonal-axes)
- [Reward Signal -> Algorithm Map](#reward-signal---algorithm-map)
- [Method Capsules](#method-capsules)
- [GRPO Variants and Known Biases](#grpo-variants-and-known-biases)
- [Rejection Sampling: the Cheap Rung](#rejection-sampling-the-cheap-rung)
- [RLOO: the Simpler REINFORCE Alternative](#rloo-the-simpler-reinforce-alternative)
- [Routing to Depth](#routing-to-depth)

## The Pipeline, Stage by Stage

Post-training is a *sequence*; each stage is reached only when the previous one is exhausted
and a measurable gap remains.

1. **SFT (supervised fine-tuning / instruction tuning).** Teach the format and base behavior
   from labeled demonstrations. Cross-entropy on (prompt, ideal-response) pairs. This is the
   floor — most "alignment" gaps that a few hundred good demonstrations can close should be
   closed here, not with RL. (Depth: [ai-llm](../../ai-llm/SKILL.md).)
2. **Preference optimization.** Close the gap SFT can't express in demonstrations — tone,
   helpfulness, harmlessness, "which of two answers is better." Either *offline* (DPO/DAAs on a
   fixed preference set) or *online* (reward model + PPO/GRPO).
3. **Reasoning RL (RLVR).** When the remaining gap is multi-step correctness on tasks with a
   *verifiable* answer (math, code, unit tests). Usually GRPO over a deterministic checker.
4. **Continuous evaluation** against over-optimization runs alongside stages 2–3, not after.

## The Two Orthogonal Axes

Inside stages 2–3, two independent choices determine the method:

| Axis | Option A | Option B |
|---|---|---|
| **Where the data comes from** | **Offline** — fixed preference dataset (DPO/DAAs). Simple, stable, no sampling loop, no reward model. | **Online** — sample from the current policy and score live (PPO/GRPO). Higher ceiling, more compute and moving parts. |
| **What produces the reward** | **Human** preferences → reward model · **AI** preferences → RLAIF/Constitutional AI | **Verifiable** checker (compiler/tests/math) → RLVR (no reward model) |

Default: **start offline (DPO); promote to online (PPO/GRPO) only when offline plateaus** or
you need a reward model's generalization to unseen prompts.

## Reward Signal -> Algorithm Map

| The reward signal you can actually produce | Algorithm | Why |
|---|---|---|
| Labeled demonstrations (no preference yet) | **SFT** | Not RL; teach behavior directly |
| Pairwise human preferences, want simplicity | **DPO** | Closed-form, no reward model or sampling loop |
| Binary good/bad or unpaired signal | **KTO** | Handles non-paired feedback |
| Want to merge SFT + preference in one stage | **ORPO** | Single-stage, reference-model-free |
| Reward model + online RL, highest ceiling | **PPO** | Clipped policy gradient + value model |
| Many samples scorable per prompt; drop the critic | **GRPO** | Group-relative advantage, ~40–60% memory cut |
| Verifiable checker available (math/code/tests) | **RLVR** (often via GRPO) | Reward = correctness; no reward model to hack |
| RL on a large **MoE** model; GRPO won't converge | **GSPO** | Sequence-level ratio is robust to expert-routing volatility |
| Want critic-free RL simpler than GRPO's std-normalized advantage | **RLOO** | Leave-one-out group mean as baseline; no learned value model, no GRPO std bias |
| Human labels are the bottleneck | **RLAIF / Constitutional AI** | Model + written constitution generate the signal |
| Want a quick lift, no RL loop | **Rejection sampling** | best-of-N → SFT on the winners |

## Method Capsules

One-paragraph orientation each; full detail in
[ai-llm/references/post-training.md](../../ai-llm/references/post-training.md).

- **PPO** — the original RLHF workhorse: a learned reward model scores samples; a clipped
  policy-gradient update with a value/critic model and a KL penalty to the SFT reference keeps
  the policy from drifting. Highest ceiling, most moving parts (four models in memory).
- **DPO** — reframes preference learning as a classification loss directly on the policy,
  eliminating the reward model and the RL loop. The default first reach for pairwise
  preferences. **DAAs** (Direct Alignment Algorithms) generalize it: **KTO** (unpaired),
  **ORPO** (single-stage, no reference model), **SimPO** (length-normalized, reference-free).
- **GRPO** — drops PPO's value model by estimating advantage from the *group* of samples drawn
  per prompt (their relative rewards). The memory lever behind DeepSeek-R1-style training;
  pairs naturally with verifiable rewards. Carries known biases — see *GRPO Variants and Known
  Biases* below.
- **GSPO** (Group Sequence Policy Optimization, Qwen 2025) — GRPO computes the importance ratio
  at the *token* level; GSPO computes it at the *sequence* level (sequence-likelihood ratio +
  sequence-level clipping). The payoff is stability: token-level ratios interact badly with
  **MoE expert-routing volatility** (≈10% of activated experts change per update), which can
  stall GRPO convergence and forces hacks like Routing Replay. GSPO is robust to that and
  trained Qwen3-235B-A22B. Reach for it when doing **RL on a large MoE** model.
- **RLVR** — RL with Verifiable Rewards: the reward is a deterministic checker (does the code
  pass tests? is the math answer correct?), so there is no reward model to over-optimize. The
  standard 2026 reasoning recipe; cheaper and less hackable where a checker exists.
- **RLAIF / Constitutional AI** — replace human preference labels with a model judging against
  a written constitution; scales the preference signal when human labeling is the bottleneck.

## GRPO Variants and Known Biases

GRPO is the dominant reasoning-RL method, but its vanilla objective carries documented biases.
Know them before scaling a run — each has a named workaround.

| Bias / failure mode | What it does | Workaround |
|---|---|---|
| **Length-normalization bias** | Per-response length normalization attenuates gradients on longer outputs → the policy inflates response length to game it | **Dr. GRPO** removes the per-response length normalization; **DAPO** normalizes by total token count instead |
| **Advantage-std bias** | Dividing the group advantage by its std over-weights easy/hard prompts (low variance) → miscalibrated gradients across difficulty | **Dr. GRPO** removes the std normalization in the advantage |
| **MoE routing volatility** | Token-level importance ratios are unstable when expert routing shifts per update → GRPO may not converge on MoE | **GSPO** (sequence-level ratio); see the capsule above |
| **Entropy collapse / exploration loss** | The policy narrows too fast and stops exploring | **DAPO**'s decoupled-clip (higher upper clip) + dynamic sampling (drop all-correct/all-wrong groups) |

**Dr. GRPO** = "Done Right" GRPO: strips the three bias sources (per-response length norm, advantage
std norm, and the KL term). **DAPO** (open large-scale RL recipe) keeps GRPO's group structure but
swaps in token-level loss, decoupled clipping, dynamic sampling, and drops the KL penalty. Pick the
fix by the symptom; don't stack all of them blindly. GRPO is now a **family, not one fixed
objective** — as of mid-2026 DAPO is TRL's default `GRPOTrainer` loss type, and further variants
(e.g. Balanced Aggregation, MAD-GRPO, λ-GRPO) address instability/verbosity that Dr. GRPO's own
normalization removal can introduce; treat any single fix as provisional and re-check TRL's
current default before quoting one as *the* answer (dated: 2026-07).

## Rejection Sampling: the Cheap Rung

Before any RL loop, **best-of-N rejection sampling** often captures much of the gain: generate
N candidates per prompt, score them (reward model, verifier, or LLM-judge), keep the best, and
SFT on those winners. No policy-gradient machinery, no KL tuning, easy to reason about. Use it
as the first rung above SFT and as a baseline any heavier RL method must beat.

## RLOO: the Simpler REINFORCE Alternative

**RLOO** (REINFORCE Leave-One-Out) is a lighter-weight critic-free alternative to GRPO/PPO: it
uses the mean reward of the *other* samples in a group as the baseline instead of a learned value
model or GRPO's group-std normalization. TRL ships an `RLOOTrainer` alongside `GRPOTrainer` as of
2026 — reach for it when GRPO's std-normalization biases are the concern and you want a simpler
critic-free baseline without adopting the full Dr. GRPO/DAPO fix set. TRL's GRPO/RLOO trainers
also gained **environment-owned rewards** in 2026 (e.g. Harbor/OpenEnv integration), letting a
sandboxed task suite compute the reward directly instead of a hand-rolled scoring function —
useful when the verifiable checker is itself a multi-step environment (agentic/tool-use tasks),
not a single-shot grader.

## Routing to Depth

- Per-algorithm hyperparameters, loss equations, decision tree, comparison table ->
  [ai-llm/references/post-training.md](../../ai-llm/references/post-training.md)
- Code-level TRL/verl implementation -> `huggingface-skills:` plugin (TRL); check TRL's current
  docs for the default `GRPOTrainer` loss type and trainer roster (GSPO is a `loss_type`, not a
  separate trainer) before quoting specifics — these move fast
- Scaling the RL run (FSDP, vLLM rollouts, async RL) ->
  [ai-distributed-training](../../ai-distributed-training/SKILL.md)
- Reward modeling and preference data -> [reward-and-data.md](reward-and-data.md)
- Keeping it from over-optimizing -> [over-optimization-and-eval.md](over-optimization-and-eval.md)
