## Table of Contents

- [Overview](#overview)
- [The C = 6ND Approximation](#the-c--6nd-approximation)
- [FLOPs to GPU-Hours Conversion](#flops-to-gpu-hours-conversion)
- [Peak Throughput: Look It Up](#peak-throughput-look-it-up)
- [Worked Budget Table](#worked-budget-table)
- [Practical Sizing Steps](#practical-sizing-steps)
- [Caveats](#caveats)

---

## Overview

Before applying scaling laws, you need a reliable estimate of your compute budget in FLOPs. This reference covers: where C ≈ 6ND comes from, how to convert GPU-hours to FLOPs, and worked examples for common training scenarios.

## The C = 6ND Approximation

**Where it comes from:**

For a transformer with N parameters, each forward pass over one token costs approximately 2N multiply-accumulate operations (MACs) ≈ 2N FLOPs (counting only the dominant matrix multiplications). A full training step (forward + backward) costs approximately 3× the forward cost, so:

```
FLOPs per token ≈ 6N
```

Over D training tokens:
```
C ≈ 6 N D
```

**Which N:** Kaplan-style accounting uses non-embedding N; Chinchilla-style uses total N. At small scale the choice moves the answer by tens of percent (GPT-2 124M: the tied embedding is 31% of params), so name the convention.

**What is excluded:** the attention score and value matmuls, which cost 12·L·d·T FLOPs per token (L layers, width d, context T) on top of 6N. They do **not** cancel: at GPT-2 124M with T = 1024 the attention term adds ≈15% over 6N_total and ≈22% over 6N_nonemb, and the share grows with context length. PaLM's accounting (6N + 12·L·d·T) is the usual MFU convention; the MFU/HFU definitions live in [ai-distributed-training](../../ai-distributed-training/SKILL.md#mfu-and-hfu). Softmax, norms, and optimizer steps are small and are usually left out. Worked per-token numbers: [ai-pretraining's reference card](../../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card).

**When to use a more precise count:** For architecture comparisons (MoE vs dense, different attention variants), use a per-architecture FLOP counter (e.g., DeepSpeed's `flops_profiler`, or compute the exact ops from the model config). The 6ND heuristic is for budget planning and order-of-magnitude reasoning.

## FLOPs to GPU-Hours Conversion

```
C (FLOPs) = num_gpus × peak_flops_per_sec × MFU × training_duration_sec
```

Where:
- `peak_flops_per_sec`: hardware specification (see table below)
- `MFU` (Model FLOP Utilization): fraction of peak FLOPs actually used; accounts for communication overhead, memory bottlenecks, and compute gaps. Typical range: 30–50% for well-optimized training; 20–35% for smaller or less-optimized runs.
- `training_duration_sec` = wall-clock hours × 3600

**Rearranged to get training duration:**
```
hours = C / (num_gpus × peak_flops_per_sec × MFU × 3600)
```

## Peak Throughput: Look It Up

**Lookup step:** read the vendor datasheet for the exact SKU (SXM vs PCIe vs NVL differ) and take the **dense** figure for the dtype you will train in. Datasheets often headline the 2:4-sparse number, which is 2× the dense one; using it halves your realistic time estimate. Accelerator generations and their figures change, so do not keep a spec table in planning docs; record the figure and its source next to your budget.

Historical dense BF16 peaks, for the worked examples only: A100 ≈ 312 TFLOP/s; H100 SXM ≈ 989 TFLOP/s.

**A100 practical rule of thumb:** 1 A100-hour ≈ 312e12 × 0.40 × 3600 ≈ **4.5e17 FLOPs** (at 40% MFU).

## Worked Budget Table

| Setup | MFU | Wall-clock hours | C (FLOPs) | Chinchilla-optimal at this C |
|-------|-----|-----------------|------------|------------------------------|
| 1× A100 | 40% | 24h | ~1.1e19 | N*≈0.30B, D*≈6.0B |
| 8× A100 | 40% | 8h | ~2.9e19 | N*≈490M, D*≈9.8B |
| 8× A100 | 40% | 168h (1 week) | ~6.0e20 | N*≈2.2B, D*≈45B |
| 64× A100 | 40% | 168h | ~4.8e21 | N*≈6.3B, D*≈127B |
| 512× A100 | 45% | 720h (1 month) | ~1.9e23 | N*≈39B, D*≈790B |

**Notes:** N* ≈ sqrt(C/120) and D* ≈ 20 × N* are 20:1 algebra, not a paper table; refit on your own data for anything load-bearing. All figures are order-of-magnitude estimates. Reproduce a row with `scripts/training_math.py hours` (FLOPs ↔ wall-clock) and `scripts/training_math.py optimum --compute <C>`.

## Practical Sizing Steps

1. **Measure your actual tokens/second** on a short training run before committing to a full run. Published MFU numbers are for specific batch sizes, sequence lengths, and network configurations; your setup may differ.

2. **Compute C from your measured throughput:**
   ```
   C = tokens_per_second × training_duration_seconds × 6 × N
   ```
   Or equivalently: C ≈ 6 N D where D is the total tokens you will train on.

3. **Check if your planned D is consistent with Chinchilla optimum:**
   ```
   D_chinchilla = 20 × N
   ```
   If your planned D < D_chinchilla, you are under-training and should either reduce N or train longer.

4. **If data-constrained:** D is limited by corpus size. Solve for the maximum N that remains compute-feasible given D:
   ```
   N_max = D / 20   (Chinchilla-optimal at your token budget)
   ```
   Training a larger N than this with your available D will be suboptimal.

5. **If inference-constrained:** choose N smaller than N* and train on D ≫ 20×N. The over-training ratio depends on your inference demand and acceptable training loss; calculate a comparison from the selected model card rather than copying a historical ratio.

## Caveats

- Activation recomputation (gradient checkpointing) re-runs the forward pass: full recompute costs ≈8N per token instead of 6N (+33%). Count it in hardware FLOPs utilization (HFU), not in MFU or in the model's training compute C; your wall-clock estimate must include it.
- Sequence length enters implicitly through D (total tokens). If you change sequence length mid-training, recalculate D accordingly.
- MoE models have a different effective N (activated params) vs total params. Apply 6ND using activated parameters, not total parameters.
- For training with FP8 mixed precision (e.g., H100 FP8), peak FLOP rates are roughly 2× the BF16 numbers above, but actual MFU at FP8 is often lower due to precision-management overhead.
