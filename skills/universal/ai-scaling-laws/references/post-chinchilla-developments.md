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
- [Counter-Thesis: Chollet on Abstraction (Attributed, Not Consensus)](#counter-thesis-chollet-on-abstraction-attributed-not-consensus)
- [Sources](#sources)

---

## Overview

The Kaplan (2020) and Chinchilla (2022) results are necessary foundations but **not** the current state of the field. Since 2022 the compute-optimal picture was corrected, extended to the data-constrained and inference-aware regimes, and generalized to low precision and sparse (MoE) models. This reference summarizes each development and its operational consequence.

## 1. The Chinchilla Fit Was Corrected (2024)

**Besiroglu, Erdil, Barnett, You — "Chinchilla Scaling: A replication attempt" (arXiv 2404.10102).**

- Hoffmann et al.'s published Approach-3 parametric fit (`A≈406.4, B≈410.7, α≈0.34, β≈0.28, E≈1.69`) is inconsistent with their own Approaches 1–2, fails to fit the extracted data, and reports implausibly narrow confidence intervals (would require ~600k experiments; they ran <500).
- Root causes: optimizer halted before convergence (bad loss scale) + rounding of reported constants biasing predictions.
- Corrected re-fit: **α ≈ 0.35, β ≈ 0.37** (α ≈ β, i.e. closer to symmetric), consistent with Approaches 1–2. The published fit implies roughly 70+ tokens/param at Chinchilla-scale budgets; the refit brings the implied optimum back to ≈20.

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

## 4. Over-Training in Practice — Llama 3 and After

- **Llama 3 (2024):** Meta reports **over 15T pretraining tokens** for its 8B and 70B models. Both are trained far past the 20:1 heuristic, especially the smaller model. Read the [model card](https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md) before using either as a comparison.
- **Sparse (MoE) models:** apply the tokens/**activated**-param ratio (§6), not tokens/total-param; dividing by total params understates how over-trained a sparse model is.
- **Lookup step for a newer example:** read the model card or technical report for total training tokens and activated parameters, compute tokens per activated param yourself, and mark any figure the lab did not publish as an estimate. Use the result to calibrate how far past 20:1 comparable deployed models go.

**Operational consequence:** a token/(activated-)param ratio above 20:1 may be an intentional deployment decision. Calculate it from the chosen model card rather than treating a historical example as a default.

## 5. Precision-Aware Scaling (2024)

**Kumar, Ankner et al. — "Scaling Laws for Precision" (arXiv 2411.04330).**

- Low-precision training reduces a model's **effective parameter count**; the loss curve depends on the precision the weights are trained/served in.
- Post-training quantization degradation **grows with the number of training tokens** — i.e. an over-trained model can be *more* fragile to PTQ, so additional pretraining data can become actively harmful for a heavily-quantized deployment.
- Unifies training-precision and inference-precision effects in one functional form; training larger models in lower precision can be compute-optimal.

**Operational consequence:** keep the physical parameter count in a FLOP estimate such as `C ≈ 6ND`. The paper substitutes effective parameters into its *loss fit* and uses a separate precision-aware cost model; neither is a reason to reduce physical `N` in `6ND`. For low-precision training or quantized serving, measure hardware throughput and plan PTQ headroom alongside the token budget.

## 6. MoE / Sparsity Scaling Laws (2024–2025)

- **Ludziejewski et al. — "Scaling Laws for Fine-Grained Mixture of Experts" (arXiv 2402.07871):** introduces *granularity* (expert size relative to the FFN) as a scaling hyperparameter. Setting expert size equal to the dense FFN (granularity G=1) is **suboptimal at nearly every compute budget**.
- **Abnar et al. (2025) — "Parameters vs FLOPs: Scaling Laws for Optimal Sparsity for Mixture-of-Experts Language Models" (arXiv 2501.12370):** varies sparsity (the fraction of *inactive* parameters) and finds that "under different constraints (e.g., parameter size and total training compute), there is an optimal level of sparsity that improves both training efficiency and model performance." That is an *interior optimum* that moves with the budget — not a monotone "sparser is better" or "advantage widens with scale" result. Search sparsity per budget; do not max it out.

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
- Follow-up — "Test-Time Scaling Makes Overtraining Compute-Optimal" (arXiv 2604.01411) — introduces "Train-to-Test (T²)" scaling laws that jointly optimize model size, training tokens, *and* number of inference samples under one end-to-end train+inference budget; confirms empirically that planning for test-time sampling shifts the optimal *pretraining* token budget further into over-training than §3/§4 alone would suggest. (Do not quote fixed train-vs-test-time ratios; re-read the primary papers before using a number.)

**Operational consequence:** the `C ≈ 6ND` train-compute budget is no longer the whole cost model. For a reasoning deployment, jointly budget train **and** test-time FLOPs, and decide the model-size-vs-thinking-budget split from your actual query volume and difficulty mix — not from training-loss optimality alone.

## 9. Distillation Scaling Laws (2025)

**Busbridge, Shidani, Weers, Ramapuram, Littwin, Webb (Apple) — "Distillation Scaling Laws" (arXiv 2502.08606, ICLR 2025).**

- Gives a law predicting a **distilled student's** loss from the compute budget and how it is split between teacher and student — the distillation analogue of Chinchilla.
- **When a capable teacher already exists, or you will distill many students,** distillation beats from-scratch supervised training up to a compute level that scales predictably with student size. **If only one student is needed and the teacher must also be trained,** plain supervised training is generally the better use of the same compute.
- Yields compute-optimal recipes for both scenarios (teacher-exists vs teacher-also-trained).

**Operational consequence:** "should I distill or just train the small model?" is now answerable from a law, not vibes. Distillation is the rational default when amortizing one teacher across several students or when a strong teacher is already on hand; it is *not* free when the teacher's training compute must be counted against a single student.

## 10. RL Post-Training Compute Scaling (2025–2026) — Frontier, Not Yet Settled

Everything above (§1–9) is a scaling law for **pretraining or inference** compute. A distinct and much less mature line of work asks how loss/reward scales with **RL post-training compute** for reasoning models (the compute spent on rollouts + verifier scoring + policy updates, as in RLVR/GRPO-style training behind DeepSeek-R1, o1/o3, and similar reasoning models).

- **"The Art of Scaling Reinforcement Learning Compute for LLMs"** (arXiv 2510.13786) — a large RL-compute scaling study that fits sigmoidal compute–performance curves. Its reading: "not all recipes yield similar asymptotic performance", but details "such as loss aggregation, normalization, curriculum, and off-policy algorithm primarily modulate compute efficiency without materially shifting the asymptote." So the recipe family can set the ceiling, while most knobs change how fast you approach it.
- **"Scaling Behaviors of LLM Reinforcement Learning Post-Training"** (arXiv 2509.25300) — reports a power law between RL compute/data and performance that is "robust across both base and instruction-tuned models", with a "latent saturation trend" in learning efficiency as models grow.
- **CoScale-RL** (arXiv 2601.14695) — proposes co-scaling data and RL compute jointly for post-training.

**Operational consequence:** treat RL/reasoning post-training compute as a **fourth axis distinct from pretraining tokens, model size, and test-time compute (§8)**. The two main studies use different functional forms (sigmoid vs power law with saturation), so do not assume a Chinchilla-style closed-form law. Fit curves on your own recipe at 3+ compute levels before extrapolating, and re-read the primary papers before quoting a coefficient.

## Practitioner Summary — What Changed Since 2022

| Question | 2022 (Chinchilla) answer | Post-2022 answer |
|----------|--------------------------|------------------|
| Exact loss-fit constants | A≈406, α≈0.34, β≈0.28 | Refit: α≈0.35, β≈0.37, restoring ≈20:1 (Besiroglu 2024) |
| Tokens/param target | ~20 | ~20 to *minimize training loss*; fit a serving-aware target for the actual demand |
| Out of unique data? | Stop at corpus size | Repeat up to ~4 epochs ≈ free (Muennighoff 2023) |
| Optimize for? | Training loss at fixed train-compute | Train + inference compute jointly (Sardana 2024) |
| Precision in the loss fit? | Implicitly FP16/BF16 | Effective capacity depends on precision; physical FLOP counting still uses physical parameters (Kumar 2024) |
| Dense only? | Yes | MoE: use activated params + granularity/sparsity laws |
| Kaplan vs Chinchilla | Kaplan "incorrect" | Methodological difference, both reproducible |
| Inference compute in the law? | Not modeled | Test-time compute is a third axis, substitutable with pretraining (Snell 2024) |
| Distill or train small? | No principled answer | Distillation scaling law decides by teacher-exists / #students (Busbridge 2025) |
| RL post-training compute? | Not modeled | Fourth axis; functional form still contested (arXiv 2510.13786, 2509.25300) |

## Counter-Thesis: Chollet on Abstraction (Attributed, Not Consensus)

Everything in §1–10 argues *within* the scaling paradigm: how to spend compute best. François Chollet argues the paradigm itself is the limit. This section is the strongest published counterweight to scaling-economics reasoning, and it is recorded as an **attributed position, not a settled finding** — always present it as "Chollet argues…", never as consensus. Source: Chollet & Watson, *Deep Learning with Python*, 3rd ed. (Manning, 2026), ch. 19.

**The benchmarks-as-memorization-tests critique (pp. 571, 573).** Chollet argues that scaling-law proponents point to benchmark gains as evidence, but that the benchmarks used to measure "performance" are *effectively memorization tests* — "the kind we like to give university students." On his account LLMs score well by having memorized the answers, so cramming more questions and answers into a larger model raises the score without touching the underlying capability. He argues that scaling has produced no progress on inability to adapt to novelty, oversensitivity to phrasing, or failure to infer generalizable programs, because those failures are inherent to curve fitting rather than to model size. Note the load-bearing implication for this skill: if the claim holds, a benchmark improvement predicted by a scaling law is not automatically a capability improvement.

**The two poles of abstraction (pp. 585–588, Table 19.1).** Chollet's positive account splits abstraction into two kinds, arising from two ways of comparing things — similarity comparison versus exact structural match:

| Value-centric abstraction | Program-centric abstraction |
|---|---|
| Relates things by distance | Relates things by exact structural match |
| Continuous, grounded in geometry | Discrete, grounded in topology |
| Produces abstractions by "averaging" instances into "prototypes" | Produces abstractions by isolating isomorphic substructures across instances (subgraph isomorphism) |
| Underlies perception and intuition | Underlies reasoning and planning |
| Immediate, fuzzy, approximative | Slow, exact, rigorous |
| Requires a lot of experience to produce reliable results | Experience efficient: can operate on as few as two instances |

His central claim: deep learning "is very good at encoding value-centric abstraction, but it has basically no ability to generate program-centric abstraction" — so on his view the field is "missing half of what we need." He does soften this into a spectrum rather than a strict dichotomy: discrete programs can be embedded in continuous manifolds, and continuous distance functions can be emulated by discrete programs. His proposed missing piece is program synthesis (Table 19.2: gradient descent over a differentiable parametric function versus discrete search over a graph of operators, the latter data-efficient enough to work from a couple of examples) — presented as a complement to deep learning, not a replacement.

**The generalization spectrum (pp. 573–576).** Chollet grades systems by how far they generalize, not by scale:

- **Local generalization** — where he places deep nets: handles inputs deviating slightly from training data, generalizing only to *known unknowns*, i.e. factors of variation anticipated during development and densely featured in training data. He attributes this to generalizing via interpolation on a manifold.
- **Broad generalization** — his term for handling *unknown unknowns* within a single broad domain, including situations the creators could not have anticipated. His examples: a self-driving car safe in any situation, or a domestic robot passing the "Woz test" (entering a random kitchen and making coffee). He describes current progress here as coming from combining deep learning with handcrafted abstract world models.
- **Extreme generalization** — his term for human cognition: adapting to novel, never-before-experienced situations "using little data or even no new data at all."

He argues the deep learning paradigm has stayed confined to *cognitive automation*, and that calling the field "artificial intelligence" is "a category error" — proposing "artificial cognition" as the umbrella, with cognitive automation and artificial intelligence as nearly independent subfields. He is explicit that this is not a dismissal: he calls cognitive automation "incredibly useful" and "a game changer for essentially every industry."

**How to use this against the rest of the file.** §1–10 tell you how to allocate a compute budget; they are silent on whether the resulting capability generalizes off-distribution. Chollet's argument is the reason to state that limit out loud when a scaling projection is used to forecast *capability* rather than *loss*. Treat it as a contested position with a named proponent: it is a book-length argument from a primary source, not a measured result, and the scaling-economics literature in §1–10 does not concede it.

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
- Khatri et al. (2025). The Art of Scaling Reinforcement Learning Compute for LLMs. arXiv:2510.13786. https://arxiv.org/abs/2510.13786
- Anonymous/authors (2025). Scaling Behaviors of LLM Reinforcement Learning Post-Training. arXiv:2509.25300.
- Authors (2026). CoScale-RL. arXiv:2601.14695.
- (2026). Test-Time Scaling Makes Overtraining Compute-Optimal. arXiv:2604.01411.
