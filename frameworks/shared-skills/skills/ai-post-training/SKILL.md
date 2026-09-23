---
name: ai-post-training
description: "Post-training and alignment: reward modeling, RLHF/PPO, DPO/DAAs, GRPO, RLVR, RLAIF, over-optimization. Use when adapting an SFT model with preference or verifiable-reward signals."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-08-31
---

# AI Post-Training

**Domain**: the rung *after* supervised fine-tuning — turning a pretrained or SFT'd base
model into an aligned, preference-tuned, or reasoning-capable model with a **reward signal**.
This skill owns the post-training *decision and pipeline*: when to post-train at all, which
reward signal you can produce, which algorithm family fits, and how to keep it from
over-optimizing. Per-algorithm operational depth lives in
[ai-llm/references/post-training.md](../ai-llm/references/post-training.md) (PPO, DPO, SimPO,
KTO, GRPO, GSPO, DAPO, RLVR, RULER, ORPO — catalogue + decision tree); this skill routes there.

It does **not** cover: pretraining ([ai-pretraining](../ai-pretraining/SKILL.md)),
the prompt→RAG→SFT promotion ladder ([ai-architecture-advisor](../ai-architecture-advisor/SKILL.md)),
or serving the result ([ai-llm-inference](../ai-llm-inference/SKILL.md)).

## Quick Reference

| You have / want | Method | Deep ref |
|---|---|---|
| Labeled demonstrations of the target behavior | **SFT** (baseline — exhaust it first; not RL) | [ai-llm](../ai-llm/SKILL.md) |
| Pairwise preferences, want the least machinery | **DPO** (or DAAs: KTO / ORPO / SimPO) | [methods](references/methods-and-pipeline.md) |
| A stronger teacher model, a small student | **On-policy distillation** — try before GRPO | [methods](references/methods-and-pipeline.md) |
| Preferences + reward model + online RL | **GRPO / RLOO** (critic-free, 2026 default); **PPO** is the reference algorithm, now `trl.experimental` | [methods](references/methods-and-pipeline.md) |
| Many samples scorable per prompt, drop the critic | **GRPO** (group-relative advantage) | [methods](references/methods-and-pipeline.md) |
| A real task with **no** mechanical checker | **Rubrics as rewards** (the fourth reward source) | [methods](references/methods-and-pipeline.md) |
| A multi-turn agent acting in an environment | **Agentic RL** (trajectory reward, rollout infra) | [methods](references/methods-and-pipeline.md) |
| A verifiable checker (math/code/tests) as the reward | **RLVR** (via GRPO or a GRPO-family variant — GSPO/DAPO/RLOO) — the dominant 2026 reasoning recipe | [methods](references/methods-and-pipeline.md) |
| Scale preference labels cheaply | **RLAIF / Constitutional AI** (model-as-judge) | [data](references/reward-and-data.md) |
| A quick lift with no RL loop | **Rejection sampling** (best-of-N → SFT) | [methods](references/methods-and-pipeline.md) |
| Train/choose the reward model itself | **Bradley-Terry RM**, ORM vs PRM, generative RM | [reward](references/reward-and-data.md) |
| Stop reward hacking / over-refusal | KL regularization, eval harness, over-optimization controls | [over-optimization](references/over-optimization-and-eval.md) |
| Interpret a **live** GRPO run's metrics | Advantage mean/std, entropy, reward exhaustion, degenerate groups | [diagnostics](references/grpo-run-diagnostics.md) |
| Build a robust RLVR checker (not just "use a verifier") | Extract → normalize → SymPy equivalence → element-wise grading | [reward](references/reward-and-data.md) |
| Compose fine-tuned checkpoints / strip an unwanted attribute | **Model merging** (averaging, weighted, interpolation, adapter merging) | [reward](references/reward-and-data.md) |

## When to Use This Skill

Activate when the user asks (in any language) some form of:

- "How do I run RLHF / align a model / train with human feedback?"
- "DPO vs PPO vs GRPO — which preference/RL method?"
- "How do I train a reasoning model / RLVR / GRPO like DeepSeek-R1?"
- "How do I build/choose a reward model? ORM or PRM?"
- "Should I use Constitutional AI / RLAIF instead of human labels?"
- "My fine-tune still has a preference/safety/refusal gap after SFT — now what?"
- "How do I collect preference data / what about synthetic preference data?"
- "My RL model is reward-hacking / over-refusing — how do I fix over-optimization?"

If the gap is missing *knowledge* (→ RAG), missing *format/behavior demonstrable with labels*
(→ SFT), or *reasoning closeable by more thinking on a hosted model* (→ raise the thinking
budget), you usually do **not** need this skill. Confirm with
[ai-architecture-advisor](../ai-architecture-advisor/SKILL.md) first if unsure.

## Scope Boundaries (Use These Skills for Depth)

- **Per-algorithm catalogue + decision tree (PPO/DPO/GRPO/RLVR/RULER/...)** ->
  [ai-llm/references/post-training.md](../ai-llm/references/post-training.md)
- **TRL / SFT / DPO / GRPO implementation in code** -> `huggingface-skills:` plugin (TRL)
- **Distributed RL training scale (FSDP, vLLM rollout, async RL)** ->
  [ai-distributed-training](../ai-distributed-training/SKILL.md)
- **Eval methodology, judge calibration, thresholds** -> [ai-evals](../ai-evals/SKILL.md)
- **The prompt→RAG→SFT→post-train promotion decision** ->
  [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md)
- **Reasoning-model build walkthrough** -> Raschka, *Build a Reasoning Model* (see sources)

## Workflow

1. **Confirm post-training is the right rung.** Is the gap *knowledge* (→ RAG), *format/behavior
   demonstrable with labels* (→ SFT), or *reasoning closeable on a hosted model* (→ raise the
   thinking budget)? If yes to any, stop — you don't need post-training. → verify: name the gap type.
2. **Exhaust SFT.** Establish the SFT baseline; only proceed if a measurable preference/safety/
   reasoning gap remains. → verify: SFT eval shows the residual gap.
3. **Identify the reward signal you can actually produce** — human pairs, AI feedback, a written
   rubric, or a verifiable checker. This, not a benchmark, picks the algorithm. → verify: signal is real and labelable.
4. **Pick the method** (see *Choosing the Method*): on-policy distillation if a stronger teacher
   exists; otherwise offline DPO/DAAs first, promote to GRPO/RLOO online on evidence, RLVR when
   the reward is verifiable. → verify: simplest method that fits the signal.
5. **Build/choose the reward model or checker** (see *Reward Modeling*). → verify: RM accuracy or checker coverage.
6. **Train with an eval harness from step 1, and KL scoped to the reward source** (KL when the
   reward is learned; β=0 with a verifiable checker). → verify: held-out true-objective metric, not reward curve.
7. **Hand off** per-algorithm depth to [ai-llm/references/post-training.md](../ai-llm/references/post-training.md)
   and scale to [ai-distributed-training](../ai-distributed-training/SKILL.md).

## The Post-Training Pipeline

Post-training is a sequence, not a single algorithm. Each stage is reached only when the
previous one is exhausted and a measurable gap remains.

```text
pretrained base
  |
  v
1. SFT (instruction tuning)        teach the format/behavior from demonstrations
  |   gap remains: preferences, safety, style the labels can't express
  v
2. preference optimization         DPO / DAAs (offline)  OR  reward model + GRPO/RLOO (online)
  |   gap remains: multi-step reasoning, verifiable correctness
  v
3. reasoning RL (RLVR)             verifiable rewards (math/code/tests), usually via GRPO
  |
  v
aligned / reasoning model          + continuous eval against over-optimization
```

Two orthogonal choices run through stages 2–3:

- **Online vs offline.** Offline (DPO/DAAs) trains on a fixed preference dataset — simple,
  stable, no sampling loop or reward model. Online (GRPO/RLOO, or historically PPO) samples from the current policy
  and scores it live — higher ceiling, more compute and moving parts. Start offline; go online
  when offline plateaus or you need a reward model's generalization.
- **Reward source.** Human preferences → reward model; AI preferences → RLAIF/Constitutional
  AI; a written multi-criteria rubric → rubrics-as-rewards; verifiable checker (compiler, unit
  tests, math solver) → RLVR. The reward source you can actually produce determines the
  algorithm more than any benchmark does — and it also determines whether KL is your trust
  region (learned reward) or clipping is (verifiable checker).
- **Reference-based vs reference-free.** Within the DAA family, DPO/KTO keep a frozen reference
  model (memory cost, implicit drift bound); ORPO/SimPO drop it (cheaper, no drift bound — pair
  with a capability regression suite).

## Choosing the Method

Pick by the **reward signal you can produce**, then by compute budget. Full per-algorithm
detail and a decision tree are in
[ai-llm/references/post-training.md](../ai-llm/references/post-training.md); the front-door
logic:

1. **Can you write demonstrations?** → SFT first. Do not reach for RL to teach something a
   few hundred labeled examples would teach.
2. **Do you have pairwise preferences and want simplicity?** → **DPO** (then KTO/ORPO/SimPO
   if its numerics misbehave or you only have binary good/bad signals).
3. **Does a stronger teacher model already exist, with a small student?** → **on-policy
   distillation** before any RL loop: the teacher scores the student's *own* rollouts
   token-by-token (on-policy, dense). Reported to outperform SFT and GRPO in that setting and to
   restore generalization SFT loses.
4. **Can you afford a reward model + online RL for a higher ceiling?** → a **critic-free
   group-baseline method (GRPO/RLOO)** is the 2026 default; it drops the value model and its
   optimizer state. **PPO** remains the reference algorithm (InstructGPT lineage) but ships under
   `trl.experimental` — a learned reward model does *not* imply PPO.
5. **Is the reward verifiable (math/code/tests)?** → **RLVR**, usually via GRPO or a GRPO-family
   variant (DAPO/GSPO/RLOO) — the dominant 2026 reasoning recipe, now a portfolio rather than one
   fixed algorithm; no human labels needed.
6. **Is the task real work with no mechanical checker?** → **rubrics as rewards**: a structured
   multi-criteria rubric grades the response. Legible and auditable, but a model-mediated proxy —
   so the KL and over-optimization controls apply as they do for a reward model.
7. **Are human labels the bottleneck?** → **RLAIF / Constitutional AI** to generate the
   preference/critique signal from a model + a written constitution.
8. **Want a quick gain without an RL loop?** → **Rejection sampling**: best-of-N generate →
   score → SFT on the winners.

## Reward Modeling (the load-bearing component)

In reward-model-based RLHF, model quality is capped by reward-model quality. Key choices:

- **Bradley-Terry RM** — the standard: an LM with a scalar value head trained on preference
  pairs to predict which response a human prefers. Quality depends on preference-data balance
  and avoiding spurious length/format correlations.
- **ORM vs PRM** — Outcome Reward Models score the final answer; **Process Reward Models**
  score each reasoning step. PRMs help on multi-step reasoning but need step-level labels and
  are costlier to build. PRMs themselves split into **discriminative** (a scalar per step — the
  2023 form, brittle on step segmentation and documented as hackable) and **generative** (the
  verifier reasons, then judges — the 2026 default where PRMs are used at all).
- **Generative reward modeling / LLM-as-a-judge** — use a model to emit a critique or score
  instead of a scalar head; flexible, but inherits the judge's biases (calibrate via
  [ai-evals](../ai-evals/SKILL.md)).
- For **RLVR you skip the reward model** — a deterministic checker is the reward. That is why
  RLVR is cheaper and *harder* to over-optimize than reward-model RL where the checker exists.
  The checker is a much tighter proxy, not the true objective: incomplete tests are still
  hackable.
- **Rubrics as rewards** — when the task is real work with no mechanical checker, a structured
  multi-criteria rubric can be the reward instead of forcing a fake verifier or falling back to
  opaque pairwise preferences. Still a model-mediated proxy; treat it like a reward model for
  over-optimization purposes.

Depth: [references/reward-and-data.md](references/reward-and-data.md).

## Over-Optimization Is the Default Failure Mode

Preference RL optimizes a *proxy* for what you want, so it Goodharts silently — the model
games the reward while the true objective degrades. Controls:

- **KL regularization — scoped by reward source.** With a **learned** reward (RM+PPO, rubric
  grader, DPO's implicit β) KL to the reference policy is the primary trust region and the main
  knob against reward hacking: tune it, don't omit it. Under a **verifiable checker (RLVR)**,
  `beta=0` is the 2026 standard — TRL's `GRPOConfig` ships `beta=0.0`, DAPO drops the KL term,
  GSPO sets it to zero — and the trust region is carried by PPO-style clipping instead. Reach
  for a nonzero β there only on evidence of drift or capability regression.
- **Eval harness, always** — "completed" is wrong if anything was skipped; measure the *true*
  objective (held-out human eval / verifiable tests), not just rising reward. Watch for
  **over-refusal** (the model refuses safe requests) and length/sycophancy inflation.
- **On-policy data + pretraining-gradient mixing** — mitigate forgetting and distribution
  collapse.

Depth: [references/over-optimization-and-eval.md](references/over-optimization-and-eval.md).

## Reward Exploit Gate

Before a run, define reward, KL or reference drift, refusal, verbosity, diversity, and task-success bounds. Use a representative development set for checkpoint selection and stopping; rising reward with flat or falling development-set success is a stop signal. Keep a separate locked, blinded true-objective holdout for one final promotion check, or predeclare a tightly limited lockbox-access policy with selection and multiplicity controls. Promote only after adversarial probes target the reward's known shortcuts and a base or SFT control is evaluated with the same decoding budget. Select the checkpoint on the development rule, not automatically the final or highest-reward checkpoint, then report the untouched holdout result.

## Known Traps

- reaching for PPO/GRPO when **DPO** would do — paying for a reward model + RL loop you don't need
- post-training at all when the gap is missing *knowledge* (RAG) or *format* (SFT), not preference/reasoning
- treating RLHF as one algorithm — it's a pipeline (SFT → preference → reasoning RL) with online/offline and reward-source choices inside it
- training a reward model on imbalanced/length-correlated preferences, then optimizing its spurious signal
- running preference RL **without an eval harness** — reward goes up, true quality goes down, silently (Goodhart)
- omitting the **KL penalty in reward-model RL** and watching the policy drift off its trusted SFT behavior (reward hacking, over-refusal) — but *carrying* a nonzero KL into RLVR by reflex, where β=0 is standard and KL mostly caps the reasoning gain
- carrying a **`beta` value across method families** — DPO's β (~0.1, an implicit-reward temperature) and a GRPO KL coefficient (0.0–0.001) are different objects two orders of magnitude apart
- reaching for **GRPO when a stronger teacher already exists** — on-policy distillation is the cheaper and often better move for a small student
- picking among DPO/KTO/ORPO/SimPO from a list of adjectives instead of the **reference-based vs reference-free** tradeoff (a frozen model in memory and an implicit drift bound, or neither)
- assuming a single-turn RLVR recipe transfers to a **multi-turn agent** — trajectory-level reward, cross-turn credit assignment, and rollout infrastructure are all new problems
- using RLVR where the reward is *not* actually verifiable (no deterministic checker) — then it's just reward-model RL with a brittle checker
- confusing ORM and PRM — process rewards need step-level labels you may not have
- running **vanilla GRPO on a large MoE** and fighting non-convergence — token-level ratios break under expert-routing volatility; use **GSPO** (sequence-level)
- ignoring **GRPO's length/std biases** that inflate response length and miscalibrate difficulty — use **Dr. GRPO** / **DAPO** fixes (see methods reference)
- assuming a reasoning gap needs RLVR when, on a hosted model, raising the **thinking budget** would close it without any training

## Common Anti-Patterns

- jumping to RL before SFT is exhausted
- choosing the algorithm from a benchmark instead of from the reward signal you can produce
- treating reward-model quality as an afterthought when it caps the whole result
- measuring success by reward curve instead of the true held-out objective
- this skill re-teaching the per-algorithm math instead of routing to the ai-llm catalogue

## Core Principles

1. **SFT first, RL last.** Exhaust demonstrations before any reward-based method.
2. **The reward signal picks the algorithm.** Four sources: human pairs → DPO/RM+GRPO; AI
   preferences → RLAIF; a rubric → rubrics-as-rewards; a verifiable checker → RLVR.
3. **Offline before online.** Start with DPO's simplicity; promote to GRPO/RLOO on evidence.
4. **Reward quality caps model quality.** Invest in the reward model, rubric, or checker accordingly.
5. **Assume over-optimization.** Always eval the true objective, or it Goodharts. Add KL to the
   reference when the reward is *learned*; under a verifiable checker the trust region is
   clipping and β=0 is standard.

## Navigation: Core References

- **[methods-and-pipeline.md](references/methods-and-pipeline.md)** — the SFT→preference→RL
  pipeline, online vs offline, reference-based vs reference-free, and how each method
  (DPO/PPO/GRPO/RLVR/rejection sampling/on-policy distillation) maps to a reward signal; also
  agentic/multi-turn RL, rubrics-as-rewards, and the per-method `beta` anchor table; routes to
  the ai-llm algorithm catalogue for per-algorithm depth
- **[reward-and-data.md](references/reward-and-data.md)** — reward modeling (Bradley-Terry,
  ORM/PRM, generative RM), preference-data collection, synthetic data, RLAIF/Constitutional AI
- **[over-optimization-and-eval.md](references/over-optimization-and-eval.md)** — reward
  hacking/Goodhart, KL regularization, over-refusal, and evaluating the true objective
- **[grpo-run-diagnostics.md](references/grpo-run-diagnostics.md)** — reading a live GRPO/RLVR
  run: advantage mean (sanity check) vs std (learning signal), degenerate zero-gradient groups,
  reward exhaustion at 1.00, entropy trajectories, and a triage table

## External Sources

See **[data/sources.json](data/sources.json)** for primary references: Lambert's *RLHF* book
(the anchor), InstructGPT, DPO, DeepSeek-R1 (GRPO/RLVR), Tülu 3, GKD and Thinking Machines'
on-policy distillation, *Rubrics as Rewards*, the multi-turn agentic RL practitioner's guide,
the PRM survey, Raschka's *Build a Reasoning Model* (verifier engineering + GRPO run telemetry),
and Pai's *Designing Large Language Model Applications* (model merging/fusion taxonomy).

## Fact-Checking

- Algorithm names, framework support, and which labs use which recipe are volatile; verify
  against current primary sources before recommending a specific one. TRL specifically turns
  over fast — its `loss_type` roster, trainer namespaces (first-class vs `trl.experimental`),
  and defaults all changed between 2026-07 and 2026-08.
- The framework landscape is wider than TRL: **verl** (the common backbone for large-scale and
  agentic RL, async rollout), **OpenRLHF** (multi-turn/VLM RL), and others (NeMo RL, AReaL,
  ROLL, slime). Choose beyond TRL when scale, asynchronous rollout, or multi-turn environments
  are the constraint; delegate depth to
  [ai-distributed-training](../ai-distributed-training/SKILL.md). Health and feature claims for
  any of these must be re-checked — they were not verified past 2026-08.
- Model-specific recipe claims (e.g. "DeepSeek-R1 used X") must be checked against the model's
  own technical report, not secondary summaries.
- If you cannot verify, present guidance as a dated assumption, not a fact.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
