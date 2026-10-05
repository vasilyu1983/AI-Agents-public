---
name: ai-scaling-laws
description: "Sizes models and token budgets using Kaplan/Chinchilla scaling laws. Use when reasoning about compute-optimal N and D, tokens-per-parameter ratios, or over-training tradeoffs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-09-25
---

# AI Scaling Laws — Compute-Optimal Sizing Skill

Use this skill to allocate training compute between model parameters and tokens, then adjust for data and inference constraints.

## Quick Reference

| Concept | Formula / Heuristic | Notes |
|---------|---------------------|-------|
| Compute budget | C ≈ 6 N D | D = training tokens. **Say which N you use**: Kaplan counts non-embedding params; Chinchilla counts total params (embeddings included). ≈6 = forward + backward matmuls only; the attention term is extra (see compute-budget reference) |
| Chinchilla-optimal ratio | D ≈ 20 × N | From Hoffmann et al. 2022; holds compute constant |
| Kaplan (2020) allocation | N ∝ C^0.73, D ∝ C^0.27 | No fixed D/N ratio: the compute-efficient path grows D ∝ N^0.37, so D/N falls as C grows. Difference from Chinchilla is *methodological* (FLOP counting, warmup, optimizer tuning), not simply "wrong" — see post-Chinchilla ref |
| Optimal N given C | N* ≈ (C / 120)^0.5 | **Derived**, not a paper table: it is C = 6ND with D = 20N |
| Optimal D given C | D* ≈ (C / 0.3)^0.5 | Same algebra (D* = 20 N*) |
| Over-training (Llama-style) | D ≫ 20 × N | Trades higher training loss for cheaper inference. Meta reports over 15T pretraining tokens for Llama 3 8B, far above 20:1. For MoE models apply the ratio to *activated*, not total, params |
| GPT-3 (175B) training tokens | ~300B tokens | ≈1.7 tok/param (Kaplan-era; undercooked by Chinchilla standard) |
| Chinchilla (70B) training tokens | ~1.4T tokens | 70B × 20; compute-matched to **Gopher** (280B, 300B tokens), about 1.9× GPT-3's compute |
| GPT-2 (124M) at 20:1 | ≈2.5B tokens | See worked example below; param counts live in ai-pretraining's reference card |
| Fit constants | Hoffmann eq.: α≈0.34, β≈0.28 | **Besiroglu et al. 2024 refit: α≈0.35, β≈0.37**; the published fit implies far more than 20 tok/param, the refit restores ≈20 |

**Key distinction:** Chinchilla-optimal minimizes validation loss *for a given compute budget*. It is not inference-optimal. Over-training a smaller model to more tokens gives a model that is cheaper per inference call, even though it spent more of the compute budget on data than the loss-optimal split would dictate.

## When to Use This Skill

- Answering: "How many tokens should I train on for a model of size X?"
- Answering: "Given a GPU budget of Y A100-hours, what model size and token count should I target?"
- Evaluating whether a published training run is compute-optimal, over-trained, or under-trained
- Sizing a GPT-2 reproduction or any from-scratch experiment

## Scope Boundaries

Depth on adjacent topics lives in these skills:

- **Pre-training implementation, data pipelines, optimizer config** → [ai-pretraining](../ai-pretraining/SKILL.md)
- **Distributed training, tensor/pipeline parallelism, MFU** → [ai-distributed-training](../ai-distributed-training/SKILL.md)
- **Token budget sourcing, deduplication, quality filters** → [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md)
- **Model architecture, post-training, deployment** → [ai-llm](../ai-llm/SKILL.md)

## Sizing Workflow

1. **Fix compute budget C** in FLOPs. Multiply GPU-hours by dense peak FLOPs/s and measured or explicitly assumed model FLOPs utilization (MFU); vary assumed MFU in the sensitivity table until a pilot measures it.
2. **Apply C ≈ 6 N D** to enumerate feasible (N, D) pairs along the iso-compute curve.
3. **Pick Chinchilla-optimal point**: D* ≈ 20 × N (equivalently N* ≈ D / 20). Treat 20 as a prior: when the budget justifies it, fit your own IsoFLOP curves (see *Fit Your Own Allocation*) and report D/N as a range.
4. **Check data availability**: if your corpus yields fewer than D* tokens at acceptable quality, you are data-constrained; shrink N or accept suboptimal allocation.
5. **Adjust for inference regime**: if you will serve the model at high QPS, favor a smaller N trained on more tokens (over-trained relative to Chinchilla). If training cost is the binding constraint, stay near Chinchilla-optimal.
6. **Set hyperparameters from a fitted law, not a rule of thumb.** Sweep LR and batch on 3+ small proxy budgets, fit η_opt(C) and B_opt(C) as power laws, and pick the centre of the near-optimal band at the target C. [DeepSeek LLM](https://arxiv.org/html/2401.02954) fit η_opt = 0.3118·C^−0.125 and B_opt = 0.2920·C^0.3271 for its own data and architecture; it defined near-optimal as generalization error within 0.25% of the minimum. Copy the method, never the constants. Under µP, transfer from the proxy instead ([ai-pretraining](../ai-pretraining/SKILL.md)). Schedule: cosine or WSD over D tokens.

## Worked Example: 64 GPU-Hours on 8× A100

Every figure below is reproduced by `scripts/training_math.py` (`hours`, `optimum`, `flops`); recompute with your own inputs rather than reusing them.

**Given:** 8 × A100 (312 TFLOP/s dense BF16 peak each), MFU 40%, 8 h wall-clock = **64 GPU-hours**.

**Step 1 — Compute budget:**
```
C = 8 GPUs × 312e12 FLOP/s × 0.40 × (8 × 3600 s) = 2.875e19 FLOP
```

**Step 2 — Budget-first (choose N and D):**
```
N* = sqrt(C / 120) = 0.49B params      D* = 20 × N* = 9.8B tokens
```

**Step 3 — Model-first (N fixed at GPT-2 124M):** use the *total* parameter count (tied embedding included, ≈124.4M; the breakdown is in [ai-pretraining's reference card](../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card)).
```
D_20:1   = 20 × 124.4M          = 2.49B tokens
C_needed = 6 × 124.4M × 2.49B   = 1.86e18 FLOP   → the budget is 15.5× that
tokens the budget buys = C / (6N) = 38.5B (≈ 309 tok/param)
```
With the attention term included (per-token FLOPs from the same card) the budget buys ≈33.6B tokens (≈270 tok/param).

**Decision:** at this budget a 124M model is 15× over-provisioned for loss-optimal training. Pick one:
- minimize loss at fixed compute → train the ≈0.49B model on ≈9.8B tokens;
- the 124M model is what you will serve → over-train it on as many good tokens as you have (up to ≈34B);
- you only need the 20:1 reproduction → it takes ≈31 min of the 8 h.

**Note:** MFU, batch size, and sequence length all move realized throughput. Measure tokens/second on a short run before locking the schedule.

## Fit Your Own Allocation

- **Refit on your corpus before trusting 20:1.** Data quality shifts the optimum: DeepSeek LLM reports that "the higher the data quality, the more the increased compute budget should be allocated to model scaling." A new corpus or tokenizer means a new fit.
- **IsoFLOP protocol:** at least 3 compute budgets, 4+ model sizes per budget, one FLOP formula throughout, total params (or state your N convention), and a tuned LR/batch per size. Report the fitted D/N as a range with its budget span; do not extrapolate far beyond the largest fitted budget.

## Estimate Decision Gate

Return ranges, not a single compute-optimal point. State the fitted regime, units, data-quality assumption, hardware efficiency, training objective, and which inputs are measured versus borrowed. Vary tokens per parameter, model size, utilization, and data availability in a sensitivity table, then name the decision that changes across the range. Use the estimate to choose pilots and budgets; do not present extrapolation outside the source regime as a measured outcome.

## Known Traps

1. **Using Kaplan (2020) allocation after Chinchilla corrected it.** Kaplan's compute-efficient path grows N much faster than D (N ∝ C^0.73, D ∝ C^0.27, i.e. D ∝ N^0.37). The often-quoted D ∝ N^0.74 is Kaplan's overfitting bound, not the compute-optimal path. Chinchilla showed roughly equal scaling. GPT-3 is a canonical example of a Kaplan-era undercooked model: 175B params but only ~300B tokens, whereas Chinchilla-optimal would require ~3.5T tokens.

2. **Conflating Chinchilla-optimal with inference-optimal.** The Chinchilla optimum minimizes training loss for a fixed compute budget. Llama, Mistral, and most open-weight models deliberately over-train smaller models because inference cost matters more than training cost for deployed models.

3. **Conflating total parameters with non-embedding parameters.** Kaplan fits use non-embedding N; Chinchilla counts total N and includes embedding FLOPs. At small scale the embedding table is a large share of total params (31% at GPT-2 124M), so the two conventions give different coefficients. State which N you use and keep it fixed across a fit.

4. **Ignoring that data is often the binding constraint.** High-quality deduplicated text in a specific domain is finite. When the corpus cannot provide D* tokens at acceptable quality, the model is data-constrained regardless of the compute budget. Data quality shifts the effective loss curve — better data means lower loss at the same N and D.

5. **Treating the 20:1 heuristic as a universal law.** The exact coefficient varies with model architecture, data quality, and what loss metric is being optimized. 20:1 is the central Chinchilla finding; refit it on your own data (see *Fit Your Own Allocation*).

6. **Quoting Chinchilla's published fit constants as ground truth.** Besiroglu et al. (2024) showed the Approach-3 fit (α≈0.34, β≈0.28) is biased by a pre-convergence optimizer and rounding. Its implied optimum is far above 20 tok/param (≈93 at Chinchilla's budget by our computation); the refit (α≈0.35, β≈0.37) restores ≈20. Use the refit for projections.

7. **Saying "Kaplan was wrong."** The Kaplan/Chinchilla split is methodological (FLOP counting, warmup, optimizer tuning); correcting those reproduces Chinchilla's C^0.50 from Kaplan's setup (Pearce & Song 2024; Porian et al. 2024).

8. **Ignoring inference cost when sizing a deployed model.** Chinchilla optimizes training loss for training compute only. For anything served at scale, minimize *total* train+serve compute — which means smaller-and-longer than Chinchilla (Sardana & Frankle 2024).

9. **Putting effective parameters into a FLOP count.** Low-precision training changes effective capacity in the *loss fit*, not the model's physical parameter count in `C ≈ 6ND`. Precision changes hardware throughput and may call for a separate cost model; PTQ damage can grow with training tokens (Kumar et al. 2024). Plan quantization headroom alongside the token budget.

## Post-Chinchilla Developments

Kaplan and Chinchilla are foundations, not the whole picture. Full detail in **[post-chinchilla-developments.md](references/post-chinchilla-developments.md)**.

1. **Chinchilla's published fit was corrected** (Besiroglu et al. 2024). The Approach-3 constants are biased (pre-convergence optimizer + rounding); the refit's exponents are α≈0.35, β≈0.37 and restore the ~20:1 heuristic, which survives as an order-of-magnitude rule; the exact constants do not.
2. **Repeating data is nearly free up to ~4 epochs** (Muennighoff et al. 2023). When data-bound, train a smaller model for more epochs rather than under-feeding a Chinchilla-sized model. Marginal value of repeats decays to ~0 past ~16 epochs.
3. **Inference-aware scaling** (Sardana & Frankle 2024). Account for serving cost: deployed models should be smaller and trained far longer than Chinchilla-optimal. Quality improves out to ~10,000 tok/param.
4. **Over-training is the deployed norm.** Meta reports over 15T pretraining tokens for Llama 3 8B, far beyond the 20:1 point.
5. **Precision-aware scaling** (Kumar et al. 2024). Low-precision training lowers *effective capacity* in a loss fit; PTQ damage grows with training tokens, so over-training can hurt a heavily-quantized deployment. Keep physical parameters in FLOP estimates.
6. **MoE/sparsity scaling** (Ludziejewski et al. 2024; Abnar et al. 2025). Apply 6ND with *activated* params; expert granularity and sparsity are first-class optimization knobs, not a footnote on a dense law.
7. **Test-time-compute scaling** (Snell et al. 2024). Inference compute (sampling + verification, search over reasoning) is a third axis, substitutable with pretraining: few-query/low-volume favors a small model + heavy test-time compute (can beat a ~14× larger model); high-volume favors pretraining bigger. The scaling law under the o1/o3 reasoning paradigm.
8. **Distillation scaling** (Busbridge et al. 2025). A law for distilled-student loss vs teacher/student compute split: distill when a teacher exists or you serve many students; train supervised when only one student is needed and the teacher must also be trained.
9. **RL post-training compute — a fourth axis, still unsettled.** Two readings exist: arXiv 2510.13786 fits sigmoidal compute–performance curves, where recipe details mostly change compute efficiency rather than the asymptote; arXiv 2509.25300 reports a power law across base and instruct models with a latent saturation trend in learning efficiency. Don't quote a fixed RL-compute coefficient as settled science — this is the least mature scaling regime.

## Navigation: Core References

- **[Chinchilla Math](references/chinchilla-math.md)** — L(N,D) loss form, 20:1 derivation intuition, derived optimum table, the 2024 fit correction
- **[Compute Budget Estimation](references/compute-budget-estimation.md)** — C = 6ND derivation, FLOPs-to-GPU-hours conversion, worked table
- **[Post-Chinchilla Developments](references/post-chinchilla-developments.md)** — corrections and extensions since 2022: data-constrained, inference-aware, precision, MoE, Kaplan/Chinchilla reconciliation, test-time-compute and distillation scaling

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/training_math.py` | Shared training arithmetic for the pretraining skills: parameter count, 6ND and PaLM FLOPs, MFU, wall-clock hours, 20:1 and parametric optima, MinHash LSH banding, activation memory. Each function's docstring states its formula and assumptions. Run `--help`; bad input exits 2. Tests: `scripts/test_training_math.py` |

## External Sources

See **[data/sources.json](data/sources.json)** for canonical papers and primary sources:
- Kaplan et al. "Scaling Laws for Neural Language Models" (arXiv 2001.08361)
- Hoffmann et al. "Training Compute-Optimal Large Language Models" / Chinchilla (arXiv 2203.15556)
- Besiroglu et al. "Chinchilla Scaling: A replication attempt" (arXiv 2404.10102) — corrects the Chinchilla fit
- Muennighoff et al. "Scaling Data-Constrained Language Models" (arXiv 2305.16264)
- Sardana & Frankle "Beyond Chinchilla-Optimal: Accounting for Inference" (arXiv 2401.00448)
- Kumar et al. "Scaling Laws for Precision" (arXiv 2411.04330)
- Brown et al. GPT-3 (arXiv 2005.14165)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
