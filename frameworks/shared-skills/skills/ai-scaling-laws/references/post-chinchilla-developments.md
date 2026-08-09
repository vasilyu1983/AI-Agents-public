## Table of Contents

- [Overview](#overview)
- [1. The Chinchilla Fit Was Corrected (2024)](#1-the-chinchilla-fit-was-corrected-2024)
- [2. Data-Constrained Scaling — Repeating Data (2023)](#2-data-constrained-scaling--repeating-data-2023)
- [3. Inference-Aware Scaling — Beyond Chinchilla-Optimal (2024)](#3-inference-aware-scaling--beyond-chinchilla-optimal-2024)
- [4. Over-Training in Practice — Llama 3 and After](#4-over-training-in-practice--llama-3-and-after)
- [5. Precision-Aware Scaling (2024)](#5-precision-aware-scaling-2024)
- [6. MoE / Sparsity Scaling Laws (2024–2025)](#6-moe--sparsity-scaling-laws-20242025)
- [7. Reconciling Kaplan and Chinchilla (2024)](#7-reconciling-kaplan-and-chinchilla-2024)
- [8. Test-Time-Compute Scaling (2024–2026)](#8-test-time-compute-scaling-20242026)
- [9. Distillation Scaling Laws (2025)](#9-distillation-scaling-laws-2025)
- [10. RL Post-Training Compute Scaling (2025–2026)](#10-rl-post-training-compute-scaling-20252026--frontier-not-yet-settled)
- [Practitioner Summary — What Changed Since 2022](#practitioner-summary--what-changed-since-2022)
- [Sources](#sources)

---

## Overview

The Kaplan (2020) and Chinchilla (2022) results are necessary foundations but **not** the current state of the field. Between 2023 and 2026 the compute-optimal picture was corrected, extended to the data-constrained and inference-aware regimes, and generalized to low precision and sparse (MoE) models. A July-2026 practitioner is expected to know these. This reference summarizes each development and its operational consequence.

## 1. The Chinchilla Fit Was Corrected (2024)

**Besiroglu, Erdil, Barnett, You — "Chinchilla Scaling: A replication attempt" (arXiv 2404.10102).**

- Hoffmann et al.'s published Approach-3 parametric fit (`A≈406.4, B≈410.7, α≈0.336, β≈0.283, E≈1.69`) is inconsistent with their own Approaches 1–2, fails to fit the extracted data, and reports implausibly narrow confidence intervals (would require ~600k experiments; they ran <500).
- Root causes: optimizer halted before convergence (bad loss scale) + rounding of reported constants biasing predictions.
- Corrected re-fit: **α ≈ 0.35, β ≈ 0.37** (α ≈ β, i.e. closer to symmetric), consistent with Approaches 1–2.

**Operational consequence:** do not quote the published constants as authoritative. The headline "~20 tokens/param" survives as an order-of-magnitude heuristic, but the exact exponents and any loss projection should use the corrected fit.

## 2. Data-Constrained Scaling — Repeating Data (2023)

**Muennighoff et al. — "Scaling Data-Constrained Language Models" (NeurIPS 2023, arXiv 2305.16264).**

- Up to **~4 epochs of repeated data are nearly as good as the same volume of fresh unique data** (negligible loss difference at fixed compute).
- Beyond ~4 epochs, the marginal value of repeated tokens decays toward zero; beyond ~16 epochs repetition adds essentially nothing.
- Proposes a data-constrained generalization of Chinchilla with separate decay terms for repeated tokens and excess parameters.
- When data-bound, **train a smaller model for more epochs** rather than a Chinchilla-optimal-sized model on too-few unique tokens.

**Operational consequence:** "data-constrained" no longer means "stop at corpus size." Budget for ~4 effective epochs of high-quality data before treating data as the hard ceiling.

## 3. Inference-Aware Scaling — Beyond Chinchilla-Optimal (2024)

**Sardana, Portes, Doubov, Frankle — "Beyond Chinchilla-Optimal: Accounting for Inference in LM Scaling Laws" (ICML 2024, arXiv 2401.00448).**

- Chinchilla minimizes *training* loss for fixed *training* compute. It ignores the cost of serving the model.
- When you account for expected inference demand, the optimal model is **smaller and trained longer** than Chinchilla. At ~1B inference requests, train well below Chinchilla N*.
- Trained 47 models; quality keeps improving as tokens/param is pushed to extreme ranges (up to ~10,000 tokens/param), far past the 20:1 point.

**Operational consequence:** for any deployed model, compute the *total* (train + serve) FLOP budget, not just training. Over-training is the rational default for anything served at scale.

## 4. Over-Training in Practice — Llama 3/4 and After

- **Llama 3 (2024):** 8B and 70B both trained on **15T tokens** — ~1,875 tokens/param for the 8B (vs Chinchilla's ~20). Performance improved log-linearly well past the Chinchilla point. The 8B Chinchilla-optimal token budget would be ~200B tokens; Meta used ~75× that deliberately.
- **Llama 4 (2025) — current canonical datapoint, and now an MoE example, not dense:** Scout and Maverick are MoE models (17B *activated* params; 109B and ~400B *total* params respectively) trained on an estimated ~22–40T tokens. The unreleased Behemoth targets ~288B activated / ~2T total params. Because these are sparse, apply the tokens/activated-param ratio (§6), not tokens/total-param — conflating the two understates how over-trained these models actually are.
- Llama 3 remains the cleanest **dense-model** illustration of extreme over-training; Llama 4 is the more current illustration of over-training *combined with* MoE sparsity, and is the one to reach for when asked "what's a current example."

**Operational consequence:** modern token/(activated-)param ratios of 100–2000× are normal and intentional, not mistakes. "Under-trained vs over-trained" is a deployment decision, not a correctness verdict. When citing a "current" example, prefer Llama 4 (2025) over Llama 3 (2024) and verify against the latest model card — frontier-lab token/param ratios shift with nearly every release.

## 5. Precision-Aware Scaling (2024)

**Kumar, Ankner et al. — "Scaling Laws for Precision" (arXiv 2411.04330).**

- Low-precision training reduces a model's **effective parameter count**; the loss curve depends on the precision the weights are trained/served in.
- Post-training quantization degradation **grows with the number of training tokens** — i.e. an over-trained model can be *more* fragile to PTQ, so additional pretraining data can become actively harmful for a heavily-quantized deployment.
- Unifies training-precision and inference-precision effects in one functional form; training larger models in lower precision can be compute-optimal.

**Operational consequence:** in 2026, FP8 training and INT4/INT8 serving are common — the param count in `C ≈ 6ND` and in scaling fits should be the *effective* (precision-adjusted) count, and PTQ headroom must be planned alongside the token budget.

## 6. MoE / Sparsity Scaling Laws (2024–2025)

- **Ludziejewski et al. — "Scaling Laws for Fine-Grained Mixture of Experts" (arXiv 2402.07871):** introduces *granularity* (expert size relative to the FFN) as a scaling hyperparameter. Setting expert size equal to the dense FFN (granularity G=1) is **suboptimal at nearly every compute budget**.
- **Abnar et al. (2025):** scaling laws for optimal *sparsity*; MoE matches compute-optimal dense quality at substantially fewer FLOPs, and the advantage widens with scale and expert count.

**Operational consequence:** for sparse models, apply `C ≈ 6ND` using **activated** (not total) parameters, and treat granularity/sparsity as first-class knobs in the optimal-config search — not a one-line caveat on a dense law.

## 7. Reconciling Kaplan and Chinchilla (2024)

**Pearce & Song, "Reconciling Kaplan and Chinchilla Scaling Laws" (arXiv 2406.12907); Porian et al., "Resolving Discrepancies in Compute-Optimal Scaling" (arXiv 2406.19146).**

- The Kaplan (N* ∝ C^0.73) vs Chinchilla (N* ∝ C^0.50) split is **methodological**, driven by: (1) counting non-embedding vs total FLOPs at small scale, (2) non-scaled warmup duration, (3) scale-dependent optimizer tuning.
- Correct all three and Kaplan's setup reproduces Chinchilla's C^0.50.

**Operational consequence:** drop "Kaplan was wrong" framing. The lesson is that scaling-law coefficients are sensitive to experimental hygiene (FLOP accounting, warmup, per-scale tuning) — which is also why your own re-fits must control these.

## 8. Test-Time-Compute Scaling (2024–2026)

**Snell, Lee, Xu, Kumar — "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters" (arXiv 2408.03314, ICLR 2025).**

- A *third* compute axis joins train-params and train-tokens: compute spent **at inference** (repeated sampling + verification, search/MCTS over reasoning steps, revision). This is the scaling law underneath the o1/o3-style reasoning-model paradigm.
- Test-time and pretraining compute are **substitutable within a regime**: when the inference-to-pretraining token ratio is *low* (few queries), a small model under heavy test-time scaling can beat a model ~14× larger; when serving *high volume*, pretraining a bigger model wins because the per-query test-time premium is paid on every request.
- The gain from extra test-time compute is highly **nonlinear in per-sample quality** and **task-difficulty-dependent** — easy prompts saturate fast; hard prompts keep benefiting. Allocate test-time budget per-prompt, not uniformly.
- 2026 follow-up — "Test-Time Scaling Makes Overtraining Compute-Optimal" (arXiv 2604.01411, Wisconsin–Madison/Stanford) — introduces "Train-to-Test (T²)" scaling laws that jointly optimize model size, training tokens, *and* number of inference samples under one end-to-end train+inference budget; confirms empirically that planning for test-time sampling shifts the optimal *pretraining* token budget further into over-training than §3/§4 alone would suggest. (Verify the latest train-vs-test-time tradeoff results before quoting fixed ratios — this is the most active scaling frontier in 2026.)

**Operational consequence:** the `C ≈ 6ND` train-compute budget is no longer the whole cost model. For a reasoning deployment, jointly budget train **and** test-time FLOPs, and decide the model-size-vs-thinking-budget split from your actual query volume and difficulty mix — not from training-loss optimality alone.

## 9. Distillation Scaling Laws (2025)

**Busbridge, Shidani, Weers, Ramapuram, Littwin, Webb (Apple) — "Distillation Scaling Laws" (arXiv 2502.08606, ICLR 2025).**

- Gives a law predicting a **distilled student's** loss from the compute budget and how it is split between teacher and student — the distillation analogue of Chinchilla.
- **When a capable teacher already exists, or you will distill many students,** distillation beats from-scratch supervised training up to a compute level that scales predictably with student size. **If only one student is needed and the teacher must also be trained,** plain supervised training is generally the better use of the same compute.
- Yields compute-optimal recipes for both scenarios (teacher-exists vs teacher-also-trained).

**Operational consequence:** "should I distill or just train the small model?" is now answerable from a law, not vibes. Distillation is the rational default when amortizing one teacher across several students or when a strong teacher is already on hand; it is *not* free when the teacher's training compute must be counted against a single student.

## 10. RL Post-Training Compute Scaling (2025–2026) — Frontier, Not Yet Settled

Everything above (§1–9) is a scaling law for **pretraining or inference** compute. A distinct and much less mature line of work asks how loss/reward scales with **RL post-training compute** for reasoning models (the compute spent on rollouts + verifier scoring + policy updates, as in RLVR/GRPO-style training behind DeepSeek-R1, o1/o3, and similar reasoning models).

- **"The Art of Scaling Reinforcement Learning Compute for LLMs"** (Meta + UT Austin/Berkeley/UCL/Harvard, Oct 2025) — the first rigorous RL-compute scaling study (400K+ GPU-hours): RL post-training follows a predictable sigmoidal (not simple power-law) compute-performance curve, with asymptotic ceiling and midpoint sensitive to algorithm/loss-type choices — meaning the *recipe* (algorithm family, loss aggregation, curriculum) determines the ceiling, not just compute poured in.
- **"Scaling Behaviors of LLM Reinforcement Learning Post-Training"** (arXiv:2509.25300, 2025) — finds RL scaling saturates faster and differently than pretraining scaling; naively extrapolating pretraining-style power laws to RL compute overstates expected gains.
- **CoScale-RL** (arXiv:2601.14695, Jan 2026) — proposes co-scaling data and RL-compute jointly for post-training, rather than treating the SFT/RL split as fixed.

**Operational consequence:** treat RL/reasoning post-training compute as a **fourth axis distinct from pretraining tokens, model size, and test-time compute (§8)** — with its own (still-evolving, sigmoidal rather than clean power-law) scaling behavior. Do not assume a Chinchilla-style closed-form law here; the honest 2026 answer is "we have empirical curves and a rough sense of saturation, not a mature predictive law." Verify against the latest RL-scaling literature before quoting a specific coefficient — this area moves faster than pretraining scaling laws and is the least settled part of this skill.

## Practitioner Summary — What Changed Since 2022

| Question | 2022 (Chinchilla) answer | July 2026 answer |
|----------|--------------------------|------------------|
| Exact loss-fit constants | A≈406, α≈0.336, β≈0.283 | Corrected: α≈0.35, β≈0.37 (Besiroglu 2024) |
| Tokens/param target | ~20 | ~20 to *minimize training loss*; 100–2000+ if serving at scale |
| Out of unique data? | Stop at corpus size | Repeat up to ~4 epochs ≈ free (Muennighoff 2023) |
| Optimize for? | Training loss at fixed train-compute | Train + inference compute jointly (Sardana 2024) |
| Precision in the formula? | Implicitly FP16/BF16 | Effective param count is precision-dependent (Kumar 2024) |
| Dense only? | Yes | MoE: use activated params + granularity/sparsity laws |
| Kaplan vs Chinchilla | Kaplan "incorrect" | Methodological difference, both reproducible |
| Inference compute in the law? | Not modeled | Test-time compute is a third axis, substitutable with pretraining (Snell 2024) |
| Distill or train small? | No principled answer | Distillation scaling law decides by teacher-exists / #students (Busbridge 2025) |
| RL post-training compute? | Not modeled | Fourth axis; sigmoidal, recipe-dependent, still unsettled (Meta et al. 2025, arXiv:2509.25300) |

## Sources

- Besiroglu et al. (2024). Chinchilla Scaling: A replication attempt. arXiv:2404.10102. https://arxiv.org/abs/2404.10102
- Muennighoff et al. (2023). Scaling Data-Constrained Language Models. arXiv:2305.16264. https://arxiv.org/abs/2305.16264
- Sardana et al. (2024). Beyond Chinchilla-Optimal: Accounting for Inference. arXiv:2401.00448. https://arxiv.org/abs/2401.00448
- Kumar et al. (2024). Scaling Laws for Precision. arXiv:2411.04330. https://arxiv.org/abs/2411.04330
- Ludziejewski et al. (2024). Scaling Laws for Fine-Grained Mixture of Experts. arXiv:2402.07871. https://arxiv.org/abs/2402.07871
- Pearce & Song (2024). Reconciling Kaplan and Chinchilla Scaling Laws. arXiv:2406.12907. https://arxiv.org/abs/2406.12907
- Porian et al. (2024). Resolving Discrepancies in Compute-Optimal Scaling. arXiv:2406.19146. https://arxiv.org/abs/2406.19146
- Snell et al. (2024). Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters. arXiv:2408.03314. https://arxiv.org/abs/2408.03314
- Busbridge et al. (2025). Distillation Scaling Laws. arXiv:2502.08606. https://arxiv.org/abs/2502.08606
- Meta (2024). Llama 3 Model Card. https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md
- Meta AI et al. (2025). The Art of Scaling Reinforcement Learning Compute for LLMs. (Oct 2025; verify current arXiv ID before citing a number.)
- Anonymous/authors (2025). Scaling Behaviors of LLM Reinforcement Learning Post-Training. arXiv:2509.25300.
- Authors (2026). CoScale-RL. arXiv:2601.14695.
- Wisconsin–Madison/Stanford (2026). Test-Time Scaling Makes Overtraining Compute-Optimal. arXiv:2604.01411.
- Meta (2025). Llama 4 (Scout/Maverick/Behemoth) release materials. https://ai.meta.com/blog/llama-4-multimodal-intelligence/ (verify token/param figures against the current model card — pre-release numbers were estimates).
