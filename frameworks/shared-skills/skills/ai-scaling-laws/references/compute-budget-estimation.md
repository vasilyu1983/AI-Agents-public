## Table of Contents

- [Overview](#overview)
- [The C = 6ND Approximation](#the-c--6nd-approximation)
- [FLOPs to GPU-Hours Conversion](#flops-to-gpu-hours-conversion)
- [Common GPU Specs (Approximate)](#common-gpu-specs-approximate)
- [Worked Budget Table](#worked-budget-table)
- [Practical Sizing Steps](#practical-sizing-steps)
- [Caveats](#caveats)

---

## Overview

Before applying scaling laws, you need a reliable estimate of your compute budget in FLOPs. This reference covers: where C ≈ 6ND comes from, how to convert GPU-hours to FLOPs, and worked examples for common training scenarios.

## The C = 6ND Approximation

**Where it comes from:**

For a transformer with N non-embedding parameters, each forward pass over one token costs approximately 2N multiply-accumulate operations (MACs) ≈ 2N FLOPs (counting only the dominant matrix multiplications). A full training step (forward + backward) costs approximately 3× the forward cost, so:

```
FLOPs per token ≈ 6N
```

Over D training tokens:
```
C ≈ 6 N D
```

**What is excluded:** This formula counts only the dominant linear-layer operations. It excludes attention softmax, layer-norm, activations, and optimizer overhead. These omissions roughly cancel with rounding in the 6× factor — the approximation is empirically validated against actual FLOP counters in the literature.

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

## Common GPU Specs (Approximate)

Values below are BF16/FP16 peak; verify against current datasheets — these can change with driver updates and tensor core configurations.

| GPU | BF16 peak (TFLOP/s) | Notes |
|-----|---------------------|-------|
| A100 80GB SXM | ~312 | Standard pre-training GPU 2022–2024; still common in smaller clusters |
| A100 40GB PCIe | ~312 | Same compute, lower memory bandwidth |
| H100 SXM | ~989 | ~3× A100; the 2024–2025 workhorse, still widely deployed in 2026 |
| H100 NVL | ~835 | Dual-chip NVLink variant |
| H200 SXM | ~989 (BF16) | Same compute as H100, higher memory bandwidth |
| B200 (Blackwell) | ~2,250 | Dominant frontier-training chip as of 2026; ~2.3× H100 BF16 |
| GB200 NVL72 (per GPU) | ~2,500 (rack config) | Rack-scale NVLink domain; the reference chip for 2026 frontier runs |
| Rubin (GR200) | FP4 ~50 PFLOPS | Entered production June 2026; H2 2026 hyperscaler shipments — verify current availability before using as a budget baseline |
| V100 32GB | ~130 | Legacy; FP16 only |
| RTX 4090 | ~330 (FP16) | Consumer; memory-limited for large models |

**2026 note:** B200/GB200 (Blackwell) is the current production-dominant chip for frontier pre-training; H100/H200 remain common for mid-size runs and inference fleets. Rubin is shipping to hyperscalers in H2 2026 — treat its FLOP figures as provisional and verify against current NVIDIA datasheets before locking a budget on it.

**A100 practical rule of thumb:** 1 A100-hour ≈ 312e12 × 0.40 × 3600 ≈ **4.5e17 FLOPs** (at 40% MFU).

## Worked Budget Table

| Setup | MFU | Wall-clock hours | C (FLOPs) | Chinchilla-optimal at this C |
|-------|-----|-----------------|------------|------------------------------|
| 1× A100 | 40% | 24h | ~4.3e18 | N*≈190M, D*≈3.8B |
| 8× A100 | 40% | 8h | ~2.9e19 | N*≈490M, D*≈9.8B |
| 8× A100 | 40% | 168h (1 week) | ~6.1e20 | N*≈2.3B, D*≈46B |
| 64× A100 | 40% | 168h | ~4.8e21 | N*≈6.3B, D*≈126B |
| 512× A100 | 45% | 720h (1 month) | ~1.8e24 | N*≈122B, D*≈2.4T |

**Notes:** N* ≈ sqrt(C/120) and D* ≈ 20 × N* are approximations; use Hoffmann et al. Table A3 for precise values. All figures are order-of-magnitude estimates.

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

5. **If inference-constrained:** choose N significantly smaller than N* and train on D ≫ 20×N. The exact over-training ratio (e.g., 40–200× for Llama 3-style models) depends on your inference serving cost and acceptable training loss.

## Caveats

- The 6ND approximation ignores activation recomputation (gradient checkpointing), which adds roughly 30% to compute during backward. Some sources use C ≈ 6ND to implicitly include this; others use 6ND for the clean-memory case. Treat the constant as approximate.
- Sequence length enters implicitly through D (total tokens). If you change sequence length mid-training, recalculate D accordingly.
- MoE models have a different effective N (activated params) vs total params. Apply 6ND using activated parameters, not total parameters.
- For training with FP8 mixed precision (e.g., H100 FP8), peak FLOP rates are roughly 2× the BF16 numbers above, but actual MFU at FP8 is often lower due to precision-management overhead.
