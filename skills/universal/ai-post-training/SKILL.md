---
name: ai-post-training
description: "Chooses DPO, GRPO/RLVR, reward models, and over-optimization controls. Use when adapting a pretrained or SFT model with preference or verifiable reward signals."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.4"
last_validated: 2026-08-31
---

# AI Post-Training

**Domain**: adaptation after pretraining, often after supervised fine-tuning — turning a base or SFT
model into an aligned, preference-tuned, or reasoning-capable model with a **reward signal**.
This skill owns the post-training *decision and pipeline*: when to post-train at all, which
reward signal you can produce, which algorithm family fits, and how to keep it from
over-optimizing. The per-algorithm catalogue and decision map (PPO, DPO, SimPO, KTO, ORPO,
GRPO, GSPO, DAPO, RLOO, RLVR, RULER) live in
[references/methods-and-pipeline.md](references/methods-and-pipeline.md).

It does **not** cover: pretraining ([ai-pretraining](../ai-pretraining/SKILL.md)),
the prompt→RAG→SFT promotion ladder ([ai-architecture-advisor](../ai-architecture-advisor/SKILL.md)),
or serving the result ([ai-llm-inference](../ai-llm-inference/SKILL.md)).

## Quick Reference

| You have / want | Method | Deep ref |
|---|---|---|
| Labeled demonstrations of the target behavior | **SFT** (compare as a baseline; not RL) | [ai-llm](../ai-llm/SKILL.md) |
| Pairwise preferences, want the least machinery | **DPO**; compare ORPO/SimPO for their different objectives | [methods](references/methods-and-pipeline.md) |
| Unpaired good/bad feedback | **KTO** | [methods](references/methods-and-pipeline.md) |
| A stronger teacher model, a small student | **On-policy distillation** — try before GRPO | [methods](references/methods-and-pipeline.md) |
| Preferences + reward model + online RL | **GRPO / RLOO** (critic-free, the common choice); **PPO** is the reference algorithm, but check that your trainer still ships it (release notes) | [methods](references/methods-and-pipeline.md) |
| Many samples scorable per prompt, drop the critic | **GRPO** (group-relative advantage) | [methods](references/methods-and-pipeline.md) |
| A real task with **no** mechanical checker | **Rubrics as rewards** (the fourth reward source) | [methods](references/methods-and-pipeline.md) |
| A multi-turn agent acting in an environment | **Agentic RL** (trajectory reward, rollout infra) | [methods](references/methods-and-pipeline.md) |
| A verifiable checker (math/code/tests) as the reward | **RLVR** (via GRPO or a GRPO-family variant — GSPO/DAPO/RLOO) — a widely used reasoning recipe | [methods](references/methods-and-pipeline.md) |
| Scale preference labels cheaply | **RLAIF / Constitutional AI** (model-as-judge) | [data](references/reward-and-data.md) |
| A quick lift with no RL loop | **Rejection sampling** (best-of-N → SFT) | [methods](references/methods-and-pipeline.md) |
| Train/choose the reward model itself | **Bradley-Terry RM**, ORM vs PRM, generative RM | [reward](references/reward-and-data.md) |
| Stop reward hacking / over-refusal | KL regularization, eval harness, over-optimization controls | [over-optimization](references/over-optimization-and-eval.md) |
| Interpret a **live** GRPO run's metrics | Advantage mean/std, entropy, reward exhaustion, degenerate groups | [diagnostics](references/grpo-run-diagnostics.md) |
| Build a robust RLVR checker (not just "use a verifier") | Extract → normalize → SymPy equivalence → element-wise grading | [reward](references/reward-and-data.md) |
| Compose fine-tuned checkpoints / strip an unwanted attribute | **Model merging** (averaging, weighted, interpolation, adapter merging) | [reward](references/reward-and-data.md) |

## Scope Boundaries (Use These Skills for Depth)

- **Per-algorithm catalogue + decision map (PPO/DPO/GRPO/RLVR/RULER/...)** ->
  [references/methods-and-pipeline.md](references/methods-and-pipeline.md)
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
2. **Compare an SFT baseline where demonstrations are available.** For reasoning RLVR, a
   pretrained base is also a possible starting point: DeepSeek-R1-Zero used RL without prior SFT,
   but its report describes readability and language-mixing problems. Choose the starting policy
   against the deployment requirements. → verify: baseline and residual gap are measured.
3. **Identify the reward signal you can actually produce** — human pairs, AI feedback, a written
   rubric, or a verifiable checker. This, not a benchmark, picks the algorithm. → verify: signal is real and labelable.
4. **Pick the method** (see *Choosing the Method*): try on-policy distillation if a stronger teacher
   exists; DPO/DAAs fit preference pairs, while RLVR fits a reliable verifier. Promote from an
   offline preference method to online RL on evidence. → verify: method fits the available signal.
5. **Validate the training signal** (see *Reward Modeling*): preference-pair quality for DPO,
   reward-model calibration for learned rewards, or checker coverage for RLVR.
6. **Train with an eval harness from step 1, and KL scoped to the reward source** (KL when the
   reward is learned; with a verifiable checker, set β deliberately: many recipes use 0, the
   original GRPO used 0.04). → verify: held-out task success, not just the reward curve; for
   RLVR, compare pass@1 and large-k pass rates with the starting policy.
7. **Package and hand off.** Version the policy, reward model or checker, and training config
   together; keep the previous checkpoint deployable for rollback. Scale the run with
   [ai-distributed-training](../ai-distributed-training/SKILL.md).

## Pipeline Choices

SFT, preference optimization, and RLVR are choices driven by the remaining gap and available
signal, not mandatory consecutive stages. DeepSeek-R1-Zero is a documented base→RLVR path;
DeepSeek-R1 used cold-start SFT before RL to improve usability
([technical report](https://arxiv.org/abs/2501.12948)). Evaluate the starting policy and
true objective before and after each stage.

Three independent choices govern preference optimization and RLVR:

- **Online vs offline.** Offline (DPO/DAAs) trains on a fixed preference dataset — no sampling
  loop or explicit reward model. Online (GRPO/RLOO, or historically PPO) samples from the current
  policy and scores it live — more compute and moving parts. With preference pairs, start offline;
  go online when the offline method plateaus or the task needs live rollouts.
- **Reward source.** Human preferences → DPO or a reward model; AI preferences → RLAIF/Constitutional
  AI; a written multi-criteria rubric → rubrics-as-rewards; verifiable checker (compiler, unit
  tests, math solver) → RLVR. The reward source you can actually produce determines the
  algorithm more than any benchmark does — and it also determines whether KL is your trust
  region (learned reward) or clipping is (verifiable checker).
- **Reference-based vs reference-free.** Within the DAA family, DPO/KTO use frozen reference
  log probabilities (which can be precomputed for a fixed dataset); ORPO/SimPO drop the reference
  term. Compare compute and capability drift rather than assuming one memory footprint.

## Choosing the Method

Pick by the **reward signal you can produce**, then by compute budget. Full per-algorithm
detail and the decision map are in
[references/methods-and-pipeline.md](references/methods-and-pipeline.md); the front-door
logic:

1. **Can you write demonstrations?** → compare SFT before adding a reward loop for behavior
   that demonstrations can teach. RLVR can instead begin from a base model if its usability
   tradeoffs are acceptable and the checker is reliable.
2. **Do you have pairwise preferences and want simplicity?** → **DPO**. Compare ORPO/SimPO
   for their different objectives; use KTO when feedback is unpaired good/bad labels.
3. **Does a stronger teacher model already exist, with a small student?** → **on-policy
   distillation** before any RL loop: the teacher scores the student's *own* rollouts
   token-by-token (on-policy, dense). Reported to outperform SFT and GRPO in that setting and to
   restore generalization SFT loses.
4. **Can you afford a reward model + online RL for a higher ceiling?** → a **critic-free
   group-baseline method (GRPO/RLOO)** is the common choice; it drops the value model and its
   optimizer state. **PPO** remains the reference algorithm (InstructGPT lineage), but trainer
   support moves (TRL first demoted it to `trl.experimental`, then removed it), so check your
   trainer's release notes before planning on it. A learned reward model does *not* imply PPO.
5. **Is the reward verifiable (math/code/tests)?** → **RLVR**, usually via GRPO or a GRPO-family
   variant (DAPO/GSPO/RLOO) — a widely used reasoning recipe, a portfolio rather than one
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
  and avoiding spurious length/format correlations. **Validate it under optimization, not only
  by pairwise accuracy**: one method, following Gao et al. 2022 (arXiv 2210.10760; method only,
  figures not re-checked here), is best-of-N curves of proxy reward vs a gold score (held-out
  humans or a stronger judge) as N grows. Where gold flattens or falls while proxy keeps rising,
  over-optimization has begun; an RM with high pairwise accuracy can still turn early.
- **ORM vs PRM** — Outcome Reward Models score the final answer; **Process Reward Models**
  score each reasoning step. PRMs help on multi-step reasoning but need step-level labels and
  are costlier to build. PRMs themselves split into **discriminative** (a scalar per step — the
  2023 form, brittle on step segmentation and documented as hackable) and **generative** (the
  verifier reasons, then judges; reported to generalize better, at a higher cost per call).
- **Generative reward modeling / LLM-as-a-judge** — use a model to emit a critique or score
  instead of a scalar head; flexible, but inherits the judge's biases (calibrate via
  [ai-evals](../ai-evals/SKILL.md)).
- For **RLVR you skip the reward model** — a deterministic checker is the reward. This removes
  the learned reward model but not reward exploitation: incomplete tests can
  reward degenerate solutions. Probe checker shortcuts against a separate true-objective eval.
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
  many recipes run `beta=0` and carry the trust region with PPO-style clipping instead: DAPO
  drops the KL term, and trainer defaults may ship `beta=0.0` (check your version's config).
  The original GRPO (DeepSeekMath) used β=0.04, so nonzero is not wrong. GSPO's paper omits
  the KL term "for brevity"; that is not evidence that β must be 0. Set β deliberately, and
  raise it on evidence of drift or capability regression.
- **Eval harness, always** — "completed" is wrong if anything was skipped; measure the *true*
  objective (held-out human eval / verifiable tests), not just rising reward. Watch for
  **over-refusal** (the model refuses safe requests) and length/sycophancy inflation.
- **On-policy data + pretraining-gradient mixing** — mitigate forgetting and distribution
  collapse.
- **Report pass@k at large k, not only pass@1.** Yue et al. 2025 (arXiv 2504.13837) found RLVR
  models beat their base at k=1, but "the base models achieve a higher pass@k score when k is
  large". An RL gain at pass@1 that comes with a loss at, say, pass@256 is the policy narrowing
  onto answers the base could already sample, not new capability. Report both on the same
  prompts and sampling settings.

Depth: [references/over-optimization-and-eval.md](references/over-optimization-and-eval.md).

## Reward Exploit Gate

Before a run, define reward, KL or reference drift, refusal, verbosity, diversity, and task-success bounds. Use a representative development set for checkpoint selection and stopping; rising reward with flat or falling development-set success is a stop signal. Keep a separate locked, blinded true-objective holdout for one final promotion check, or predeclare a tightly limited lockbox-access policy with selection and multiplicity controls. Promote only after adversarial probes target the reward's known shortcuts and a base or SFT control is evaluated with the same decoding budget. Select the checkpoint on the development rule, not automatically the final or highest-reward checkpoint, then report the untouched holdout result.

## Known Traps

- reaching for PPO/GRPO when **DPO** would do — paying for a reward model + RL loop you don't need
- assuming DPO and other direct alignment algorithms cannot reward-hack — they over-optimize their *implicit* reward too, most visibly by lengthening outputs; compare output-length distributions before and after
- post-training at all when the gap is missing *knowledge* (RAG) or *format* (SFT), not preference/reasoning
- treating RLHF as one algorithm — it's a pipeline (SFT → preference → reasoning RL) with online/offline and reward-source choices inside it
- training a reward model on imbalanced/length-correlated preferences, then optimizing its spurious signal
- running preference RL **without an eval harness** — reward goes up, true quality goes down, silently (Goodhart)
- omitting the **KL penalty in reward-model RL** and watching the policy drift off its trusted SFT behavior (reward hacking, over-refusal) — but *carrying* a nonzero KL into RLVR by reflex, where many recipes run β=0 and a large KL can cap the reasoning gain
- carrying a **`beta` value across method families** — DPO's β (~0.1, an implicit-reward temperature) and a GRPO KL coefficient (DeepSeekMath's GRPO used 0.04; many RLVR recipes use 0) are different objects, so a similar-looking number means nothing across them
- reaching for **GRPO when a stronger teacher already exists** — on-policy distillation is the cheaper and often better move for a small student
- picking among DPO/KTO/ORPO/SimPO from a list of adjectives instead of the **reference-based vs reference-free** tradeoff (a frozen model in memory and an implicit drift bound, or neither)
- assuming a single-turn RLVR recipe transfers to a **multi-turn agent** — trajectory-level reward, cross-turn credit assignment, and rollout infrastructure are all new problems
- using RLVR where the reward is *not* actually verifiable (no deterministic checker) — then it's just reward-model RL with a brittle checker
- confusing ORM and PRM — process rewards need step-level labels you may not have
- running **vanilla GRPO on a large MoE** and fighting non-convergence — token-level ratios break under expert-routing volatility; use **GSPO** (sequence-level)
- ignoring **GRPO's length/std biases** that inflate response length and miscalibrate difficulty — use **Dr. GRPO** / **DAPO** fixes (see methods reference)
- assuming a reasoning gap needs RLVR when, on a hosted model, raising the **thinking budget** would close it without any training

- Algorithm names, framework support, and which labs use which recipe are volatile; verify
  against current primary sources before recommending a specific one. TRL specifically turns
  over fast — its `loss_type` roster, trainer namespaces (first-class vs `trl.experimental`),
  and defaults change between minor releases, so read the release notes for the version you install.
- The framework landscape is wider than TRL: **verl** (the common backbone for large-scale and
  agentic RL, async rollout), **OpenRLHF** (multi-turn/VLM RL), and others (NeMo RL, AReaL,
  ROLL, slime). Choose beyond TRL when scale, asynchronous rollout, or multi-turn environments
  are the constraint; delegate depth to
  [ai-distributed-training](../ai-distributed-training/SKILL.md). Health and feature claims for
  any of these must be re-checked against each project's recent releases.
- Model-specific recipe claims (e.g. "DeepSeek-R1 used X") must be checked against the model's
  own technical report, not secondary summaries.

## Navigation: Core References

- **[methods-and-pipeline.md](references/methods-and-pipeline.md)** — the SFT→preference→RL
  pipeline, online vs offline, reference-based vs reference-free, and how each method
  (DPO/PPO/GRPO/RLVR/rejection sampling/on-policy distillation) maps to a reward signal; also
  agentic/multi-turn RL, rubrics-as-rewards, RULER, the per-method `beta` anchor table, and
  the per-algorithm catalogue
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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
