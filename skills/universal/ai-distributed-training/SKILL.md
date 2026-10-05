---
name: ai-distributed-training
description: "Guides multi-GPU pre-training: DDP, FSDP2, ZeRO, tensor/pipeline/expert parallelism, fp8/Muon. Use when scaling a run, training MoE, or reproducing GPT-2 on rented GPUs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-25
---

# Distributed Training - Systems Performance Skill

**Operational focus**: picking and implementing the right parallelism strategy, not the theory. Covers data parallelism through FSDP/ZeRO/tensor+pipeline parallelism, memory-efficient attention, mixed precision at scale, activation checkpointing, rented-GPU cost discipline, and reproducing GPT-2 124M as the canonical sanity check.

Profile before you scale. Debug on the smallest GPU that fits. Stop the instance when done.

## When to Use This Skill

Activate when the user asks about:

- Choosing between DDP, FSDP2, DeepSpeed ZeRO stages 1/2/3, or Megatron-LM
- Training Mixture-of-Experts (MoE) models: expert parallelism, all-to-all, load balancing
- OOM errors on multi-GPU training runs
- Memory-efficient attention (FlashAttention-2/3, xformers)
- Mixed precision (bf16, fp8, nvfp4) trade-offs at pre-training scale
- Optimizer choice at scale (AdamW vs Muon/MuonClip)
- Choosing a hardware generation (A100, H100, Blackwell NVL72-class racks, newer racks as they reach your provider)
- Gradient checkpointing vs activation checkpointing cost
- Pre-training frameworks: litgpt, torchtitan, nanotron, levanter
- Reproducing GPT-2 (modded-nanoGPT or nanochat as the active reference; llm.c as the educational one)
- Rented GPU cost management (RunPod, Lambda, Vast.ai, Modal)
- Spot / interruptible instance checkpoint strategies
- Profiling a training run before deciding to scale

## Scope Boundaries (Use These Skills for Depth)

- **Data mix, filtering, dedup, decontamination** -> [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md). Hold the data mix fixed when comparing parallelism configurations.
- **Single-GPU pre-training build, data pipelines, tokenization** -> [ai-pretraining](../ai-pretraining/SKILL.md)
- **Checkpoint evals, benchmark harnesses, regression gates** -> [ai-evals](../ai-evals/SKILL.md)
- **Token budget, compute-optimal scaling, Chinchilla** -> [ai-scaling-laws](../ai-scaling-laws/SKILL.md)
- **Serving optimization, batching, quantization, inference** -> [ai-llm-inference](../ai-llm-inference/SKILL.md)
- **General cloud/infra cost optimization** -> [ops-cost-optimization](../ops-cost-optimization/SKILL.md)
- **Production MLOps, model registry, monitoring, deployment** -> [ai-mlops](../ai-mlops/SKILL.md)

## Default Workflow

1. **Confirm scale and budget**: how many GPUs, which provider, on-demand or spot, target hours.
2. **Profile at small scale**: run `nsys` or `torch.profiler` on 1-2 GPUs before adding more.
3. **Pick parallelism strategy**: data parallel (DDP) -> FSDP/ZeRO -> tensor+pipeline only as needed.
4. **Enable memory optimizations**: FlashAttention, gradient checkpointing, bf16, activation offload.
5. **Wire checkpointing**: use Distributed Checkpoint (DCP) for sharded state. Save to a shared filesystem or use a storage-specific writer; wait for completion, copy to durable storage when needed, and test restore before long runs.
6. **Scale and re-profile**: judge a scale-up by **time to target loss**, not tokens per second. A bigger global batch can raise throughput while needing more tokens to reach the same loss. Hold the global batch fixed across GPU counts (see [Changing GPU Count](#changing-gpu-count-hold-the-global-batch)), then fix exposed communication.
7. **Evaluate at checkpoints, not just at the end**: run a small fixed eval suite on every saved checkpoint alongside the loss curve. Loss falling while a downstream benchmark flatlines is the signal that catches a bad data mix or a broken tokenizer *while the GPUs are still running*, and gating only on systems metrics (MFU, throughput) will not surface it. See [ai-evals](../ai-evals/SKILL.md) for harness and gate design.
8. **Stop instance**: confirm instance termination; verify storage persistence; check billing.

## Quick Reference

| Decision | Default Move | Promote When | Avoid |
|----------|-------------|--------------|-------|
| Parallelism for ≤8 GPUs | DDP or FSDP2 (ZeRO-2 equiv) | Model does not fit in one GPU | Jumping to tensor parallel before model is too large |
| Parallelism for >8 GPUs | FSDP2 (ZeRO-3 equiv) or DeepSpeed ZeRO-3 | Multiple nodes needed | Mixing FSDP + DeepSpeed naively |
| FSDP version | FSDP2 (`fully_shard`, DTensor) | All new PyTorch projects | FSDP1 (`FullyShardedDataParallel`) for new code; check PyTorch release notes for its deprecation status |
| MoE routing at scale | Expert parallelism + all-to-all | Sparse MoE, experts exceed one GPU | TP on experts before EP (all-to-all is cheaper on NVLink) |
| Attention kernel | FlashAttention-2/3 | A100+ / H100 (FA3 = Hopper) | xformers as default (verify support for your GPU) |
| Mixed precision | bf16 | A100 / H100 (native bf16) | fp16 on A100+ (bf16 is safer; less loss spike risk) |
| Low-precision training | fp8 (H100 TransformerEngine/torchao) | Proven recipe + per-tile scaling | nvfp4/fp8 without loss-vs-bf16 validation |
| Optimizer | AdamW | Default, well-understood | — |
| Optimizer (frontier) | Muon / MuonClip | Matmul params, and a measured gain on your own setup (reported gains shrink with scale) | Muon on embeddings/scalars (keep those on AdamW) |
| Gradient checkpointing | Selective activation recomputation (SAC) | Activation memory prevents the chosen micro-batch or sequence length from fitting | Wrapping a whole block that contains FlashAttention (double-recompute); quoting sqrt(n) savings for per-block policy |
| Optimizer state sharding | ZeRO-1 | Memory pressure from optimizer | ZeRO-3 when params fit on one GPU; sharding a LoRA/PEFT run by reflex (only trainable params carry optimizer state, see [fsdp-vs-zero.md](references/fsdp-vs-zero.md#memory-model-comparison)) |
| Compile | `torch.compile` on the model | Want MFU; using torchtitan/FSDP2 | Leaving eager mode on long production runs |
| Framework for ≤7B pre-training | litgpt or torchtitan | Need Megatron-grade scale | Rolling your own training loop before reading existing frameworks |
| Dev / debug GPU | Smallest A10G or L4 that fits | Need bf16 native | Frontier-generation GPUs for debugging (cost bloat) |
| Production training GPU | H100-class; Blackwell NVL72-class racks for frontier scale (check your provider's current catalog) | Need fp8/nvfp4 + NVLink-domain scale | Renting a frontier rack to debug a 124M model |
| Checkpoint storage | DCP on shared storage, then verified durable copy; or a supported object-store writer | Spot instances (derive cadence from measured save time and interruption risk) | A local-only or still-pending save at shutdown |

## Parallelism Deep Dive

### Data Parallelism (DDP)

Each worker holds a full model replica. Forward + backward runs independently per GPU. `AllReduce` synchronizes gradients. **What sets the ceiling is gradient size ÷ interconnect bandwidth, not a GPU count** — the all-reduce must finish inside the backward pass it overlaps. In practice that is order-64 GPUs on a well-connected cluster and far less on a small model over Ethernet; measure exposed all-reduce time in the profiler rather than trusting any number, including this one. Memory cost: full model + optimizer state on every GPU.

```python
# PyTorch DDP minimal setup
model = DistributedDataParallel(model, device_ids=[local_rank])
```

### FSDP2 (Fully Sharded Data Parallel)

PyTorch-native. Shards parameters, gradients, and optimizer state across all workers. **Use FSDP2 (`fully_shard`) for all new work**; the original `FullyShardedDataParallel` (FSDP1, FlatParameter-based) is the older API. Check the PyTorch release notes for FSDP1's deprecation status rather than assuming it either way, and use DCP (below) for sharded checkpoints instead of FSDP1's `state_dict_type` path. FSDP2 shards each parameter individually as a DTensor (`Shard(dim=0)`), giving simpler/inspectable sharded state dicts, cleaner composition with TP/PP/CP via DeviceMesh, and tight `torch.compile` integration.

ZeRO-stage equivalents map onto `reshard_after_forward`:

- `reshard_after_forward=False` → keep params gathered after forward (ZeRO-2-like: shard grads + optimizer state, trade memory for fewer all-gathers)
- `reshard_after_forward=True` (default) → re-shard params after forward (ZeRO-3-like: shard params + grads + optimizer state)

```python
# FSDP2 (fully_shard). Shard each transformer block, then the root.
from torch.distributed.fsdp import fully_shard, MixedPrecisionPolicy

mp = MixedPrecisionPolicy(param_dtype=torch.bfloat16, reduce_dtype=torch.float32)
for block in model.layers:
    fully_shard(block, mp_policy=mp)
fully_shard(model, mp_policy=mp)
```

FSDP1 (`FullyShardedDataParallel` + `ShardingStrategy.FULL_SHARD/SHARD_GRAD_OP/NO_SHARD`) still appears in older tutorials; migrate new work to FSDP2. Test any checkpoint-format migration by loading a real saved checkpoint under the target implementation.

### DeepSpeed ZeRO Stages

The reduction is a **function of N (the shard count), not a constant** — so state the baseline before quoting a multiplier. Per-parameter baseline for the mixed-precision AdamW recipe this skill recommends:

```
bf16 params        2 B
bf16 gradients     2 B
fp32 master copy   4 B
fp32 Adam m        4 B
fp32 Adam v        4 B
                  ----
                  16 B/param   (the 4+12 split the ZeRO paper uses:
                                4 B "compute" state, 12 B optimizer state)
```

| Stage | What is Sharded | Memory per param | Reduction vs 16 B | Overhead |
|-------|-----------------|------------------|-------------------|---------|
| ZeRO-1 | Optimizer state | `4 + 12/N` | `16/(4+12/N)` → 4× as N→∞ | Low |
| ZeRO-2 | Optimizer state + gradients | `2 + 14/N` | `16/(2+14/N)` → 8× as N→∞ | Low |
| ZeRO-3 | Optimizer state + gradients + params | `16/N` | `N` — linear, no ceiling | Communication cost |

So 4× and 8× are the **N→∞ asymptotes**, not values you get on a small cluster, while ZeRO-3's reduction *is* N. At N=8 the three stages give **2.9× / 4.3× / 8×**; at N=64, **3.8× / 7.2× / 64×**. Quoting "ZeRO-3 gives 64×" without saying N=64 is how a reader on 8 GPUs ends up 8× short.

Worked example: a 7B model at 16 B/param is ~112 GB of model+optimizer state before a single activation — it does not fit on one 80 GB H100. At N=8 with ZeRO-3 that is 112/8 = **14 GB per GPU**, leaving ~65 GB for activations.

ZeRO-Infinity extends stage 3 to NVMe offload. Use only when GPU memory is genuinely exhausted — disk bandwidth becomes the bottleneck.

### Tensor Parallelism (Megatron-LM style)

Splits weight matrices across GPUs within a node (column/row parallel linear). Requires high-bandwidth NVLink. Megatron-LM implements Transformer-specific tensor parallel (TP) with sequence parallel (SP) for activation memory reduction. Best for models that cannot fit even with full sharding, or where communication budget allows.

### Pipeline Parallelism

Splits model layers across nodes (or GPU groups). Two schedule properties get conflated. With p stages and m micro-batches, the GPipe and 1F1B bubble is (p−1)/m of the ideal step time (Narayanan et al. 2021); **1F1B does not shrink it**, it caps in-flight activations at about p micro-batches instead of m. **Interleaved 1F1B** (v model chunks per stage) is what divides the bubble by v, at the cost of more point-to-point messages. Adds complexity: micro-batch sizing, bubble tuning. Typically combined with TP and DP in 3-D parallelism (Megatron-LM, nanotron).

`torch.distributed.pipelining` is the PyTorch-native PP API (`ScheduleGPipe`, `Schedule1F1B`, `ScheduleInterleaved1F1B`); it composes with FSDP2 and TP through DeviceMesh, so it is the PP layer that fits the rest of the stack this skill recommends without adopting Megatron or nanotron wholesale.

**DualPipe** (DeepSeek-V3, arXiv 2412.19437) is a bidirectional pipeline schedule that overlaps forward/backward compute with communication and reduces the bubble. How close to zero it gets is the paper's claim for its own configuration, not a property to assume; measure the bubble in your profile. It is the reference design for large MoE training where cross-node all-to-all would otherwise dominate.

### Expert Parallelism (MoE)

Mixture-of-Experts models activate only a few experts per token, so total params (e.g. 1T) vastly exceed activated params (e.g. 32B). **Expert parallelism (EP)** places different experts on different GPUs; the router dispatches each token to its experts via **all-to-all** communication (dispatch), then a second all-to-all gathers results (combine). EP composes with DP/TP/PP/CP as an extra mesh dimension.

Key concerns specific to MoE training:

- **Load balancing**: an auxiliary load-balancing loss (or DeepSeek-V3's auxiliary-loss-free bias-update scheme) keeps tokens spread across experts; without it, a few experts saturate and the rest idle.
- **All-to-all is the bottleneck**, not all-reduce. It scales with cross-node bandwidth — keep EP inside the NVLink domain where possible, and overlap it with compute (DualPipe). DeepSeek-V3 trained a 671B MoE with **no tensor parallelism**, relying on EP + DualPipe + fp8 instead.
- **Dropless routing is the modern default**; capacity factors are the legacy alternative. A capacity factor caps tokens per expert and drops or reroutes the overflow — simple, but it discards tokens to keep the GEMM shapes static. Since MegaBlocks, **dropless MoE** expresses the expert FFN as a block-sparse / grouped GEMM over variable-size expert batches, so no token is dropped and no capacity factor is tuned; Megatron-Core and torchtitan ship it. Reach for a capacity factor only when you deliberately want a throughput cap or a fixed memory envelope.
- **Frameworks**: Megatron-Core, DeepSpeed-MoE, and nanotron implement EP; `torch.distributed` provides the all-to-all primitives.

## MFU and HFU

This skill owns the utilization definitions; [ai-pretraining](../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card) and [ai-scaling-laws](../ai-scaling-laws/references/compute-budget-estimation.md) link here.

- **MFU** (model FLOPs utilization, PaLM, Chowdhery et al. 2022) = achieved model FLOP/s ÷ peak FLOP/s. Model FLOPs per token = `6·N_matmul + 12·L·d·T`: the second term is attention's QKᵀ and AV over a context of T. Recomputation does **not** count.
- **HFU** (hardware FLOPs utilization) counts what the GPU actually executed, recomputation included. Full activation recomputation adds one forward pass (about 8N instead of 6N per token, +33%), so HFU ≥ MFU. Report MFU when comparing recipes; report HFU only when you are debugging kernels.
- **State the definition with the number**: which N (total or non-embedding), and whether the attention term is in. For GPT-2 124M at T=1024, a 40% MFU computed with 6·N_nonemb is 67% in the PaLM form. Compare MFU across runs only under one definition.
- **Peak** is the dense (not sparse) datasheet figure for the precision you run, for the GPU in hand. Look it up; do not reuse a number from another generation.
- Low MFU calls for a profile of exposed communication, dataloader stalls, kernel efficiency, and launch overhead before selecting a fix.

## Changing GPU Count: Hold the Global Batch

- **Keep tokens per optimizer step fixed** when you add or remove GPUs: change the micro-batch or gradient-accumulation steps, not the global batch. Then the loss curve stays comparable and no hyperparameter moves.
- **If the global batch must change**, Adam-family optimizers follow the **square-root** rule, not the linear one (Malladi et al. 2022, arXiv 2205.10287): batch ×2 → LR ×1.41, ×4 → ×2, ×8 → ×2.83. The linear rule (LR ×k) is the SGD heuristic.
- **Stay below the critical batch size.** Past it, a bigger batch buys no reduction in steps to the target loss, so the extra GPUs raise tokens per second and do nothing for time to target loss. Estimate it from a small sweep; do not assume it.

## Overlapping Communication with Compute

If profiling shows exposed collectives, overlap communication with compute before adding GPUs.

- **FSDP2 prefetch.** The parameter all-gather for layer *n+1* should be in flight while layer *n* computes, and the gradient reduce-scatter for layer *n* should overlap layer *n-1*'s backward. Tune backward prefetch depth rather than accepting the default on an unusual model shape.
- **Async collectives.** `async_op=True` returns a handle you wait on later; the work between issue and wait is your overlap window. Gradient bucketing (DDP) is the same idea — group small gradients so a collective is worth launching.
- **Async tensor parallelism** fuses TP collectives into the matmul epilogue so the communication for one tile happens while the next tile computes. This is how torchtitan hides TP collectives; on recent PyTorch it is built on symmetric-memory primitives. Naming and API surface here are moving fast — check torchtitan's current config rather than quoting a flag from here.
- **DualPipe** (above, under Pipeline Parallelism) is the MoE-scale version of the same principle: schedule so the all-to-all is never exposed.

Measure overlap directly. A `torch.profiler` trace shows whether the NCCL stream sits idle during compute (good) or the compute stream sits idle during a collective (exposed communication). A ratio derived from step time cannot distinguish the two.

## Will It Fit? A Memory Sanity Check

Before choosing a parallelism strategy, check whether activations alone rule out the naive configuration. The Megatron activation formula for a transformer layer stack is `s·b·h·L·(10 + 24/t + 5·a·s/(h·t))` bytes (s = sequence length, b = micro-batch, h = hidden, L = layers, a = heads, t = TP degree).

For s=8192, b=1, h=4096, L=32, a=32, t=1 the full formula gives about **380 GB**, and 90% of that is the `5·a·s/(h·t)` term: the stored attention scores and softmax. FlashAttention (this skill's default) never materializes them, so the same configuration needs about **36.5 GB** (1.14 GB per layer). Compute both terms with `ai-scaling-laws/scripts/training_math.py activations` (it prints both, plus the quadratic share). The first says why naive attention at 8k context cannot work; the second, plus weights, gradients and optimizer state (16 B/param, below), decides between selective recomputation and TP/CP. The dropped term is quadratic in sequence length, so without FlashAttention long context breaks you on activations, not weights.

## Memory-Efficient Attention

**FlashAttention** (Dao et al., 2022/2024): reorders attention computation to avoid materializing the full N×N attention matrix. Result: O(N) memory vs O(N²), significant speedup on A100/H100.

```python
# PyTorch ≥2.3: select the Flash backend via the current API
from torch.nn.attention import sdpa_kernel, SDPBackend
with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
    out = F.scaled_dot_product_attention(q, k, v)
# (torch.backends.cuda.sdp_kernel(...) is the deprecated pre-2.3 form)
```

FlashAttention-3 (2024) targets H100 with further hardware-specific optimizations. xformers provides `memory_efficient_attention` as an alternative with broader GPU support.

## Mixed Precision at Scale

`bf16` (bfloat16) is the safe default for A100+ and H100. It keeps fp32's 8 exponent bits (same range, so no fp16-style overflow) but has only 7 explicit mantissa bits (machine epsilon 2^-7), so keep master weights and reductions in fp32. `torch.amp.autocast('cuda', dtype=torch.bfloat16)` or pass `torch_dtype=torch.bfloat16`. Gradient scaler (`torch.amp.GradScaler('cuda')`) is needed for fp16 but not for bf16. (The `torch.cuda.amp.autocast` / `torch.cuda.amp.GradScaler` spellings are deprecated — use the `torch.amp` forms.)

**fp8** has been used for production pre-training on Hopper (H100). DeepSeek-V3 (arXiv 2412.19437) trained at fp8 with fine-grained scaling — per-token 1×128 / per-block 128×128 tiles plus high-precision CUDA-core accumulation. Its **separate 16B and 230B baseline-model ablations**, not a full V3-versus-bf16 run, reported relative loss error below 0.25%. Use **TransformerEngine** or **torchao float8** for the linear layers; keep a bf16/fp32 master copy of weights and the optimizer state. Validate loss-vs-bf16 on your workload before committing a long run.

*What "use fp8" actually means to set* — an endorsement is not a recipe, and these are the parts people get wrong:

- **Which tensors stay higher precision**: embeddings, the LM head, all norms, and (in MoE) the router. fp8 applies to the FLOP-dense linear layers, not the whole model.
- **Scaling granularity**: per-tensor is the simplest and the most fragile; per-tile (DeepSeek-V3's 1×128 activations / 128×128 weights) is what made a long fp8 run hold. Delayed scaling reuses a scale from prior steps (cheaper, needs an amax history); current scaling computes it in-step (safer, costlier).
- **Accumulation stays high-precision** — fp8 inputs, fp32 accumulate. This is not optional.
- **First and last layers are commonly excluded** from fp8 even when everything else converts.
- Read the recipe off your framework's own docs (TransformerEngine `fp8_autocast` recipes, torchao `float8` configs) rather than a blog post; the defaults differ between them and both move.

**nvfp4 / fp4** arrives with Blackwell. The B200/GB200 add hardware FP4 (including NVIDIA's NVFP4, 16-element micro-scaled blocks with e4m3 scales, vs MXFP4's 32-element UE8M0 blocks). NVIDIA reported a **12B model trained on 10T tokens with NVFP4 closely tracking an fp8 baseline** (arXiv 2509.25149). In a **separate 8B, 1T-token comparison**, MXFP4 needed 36% more tokens to match NVFP4 loss; that result does not establish the same gap at 12B or for other recipes. Validate against bf16/fp8 on your own workload before a long run.

### Hardware Tiers (check availability before planning)

- **A10G / L4 class** — cheap debug and architecture validation. Native bf16 on L4.
- **A100 80GB** — bf16 workhorse; common and cost-effective on spot.
- **H100 (Hopper)** — bf16 + fp8 (TransformerEngine), FlashAttention-3, NVLink/NVSwitch domains.
- **Blackwell B200 / GB200 NVL72** — hardware fp4/nvfp4 and a 72-GPU NVLink domain that lets EP/TP span a rack at NVLink bandwidth.
- **Newer generations** — capacity and pricing change month to month. Before planning around any tier, check the provider's current catalog and quoted price, and take peak throughput from the vendor datasheet (dense, not sparse). Reserve rack-scale tiers for frontier-scale runs, not 124M debugging.

### torch.compile

`torch.compile(model)` (TorchInductor) fuses kernels and is essential for competitive MFU on modern hardware. It composes with FSDP2 and is on by default in torchtitan. Compile once outside the training loop; expect a warm-up cost on the first steps. Pair with bf16/fp8 — most of the published MFU numbers assume compile is on.

**Where compile actually costs you MFU.** Compile is a common source of "the run got slower and nobody knows why":

- **Silent recompilation on dynamic shapes.** Variable sequence length, a ragged last batch, or a changing micro-batch triggers a fresh compile per shape and can dominate step time. Pad to fixed shapes, or accept `dynamic=True` deliberately. Diagnose with `TORCH_LOGS=recompiles` — if you have never run this on a compiled training loop, do it once before trusting the MFU number.
- **Compile the block, not the world.** torchtitan compiles per transformer block rather than the whole model; regional compilation keeps compile times sane and lets the same compiled artifact be reused across identical layers. Whole-model compile on a deep model can cost minutes of warm-up per launch.
- **`fullgraph=True` surfaces graph breaks as errors** instead of letting them silently fragment the graph. Use it while tuning, then decide which breaks you are willing to live with.
- **`mode="max-autotune"`** buys extra kernel search time up front for better steady-state kernels — worth it on a long run, wasteful on a debug loop.

## Activation / Gradient Checkpointing

`torch.utils.checkpoint.checkpoint(function, *args)` recomputes activations during the backward pass instead of storing them. Two *different* policies get conflated — name the one you are using:

- **Per-transformer-block checkpointing** (what "wrap every block" means). You store one boundary activation per block instead of every intermediate tensor inside it. The saving is roughly the number of intra-block tensors you stop storing — on the order of **10–20×**, and it is a **constant factor independent of depth**, not a function of L. Cost: one extra forward per block. Since backward ≈ 2× forward, one extra forward over a 1F+2B budget is 1/3, so **~33% is the theoretical ceiling** for full recomputation; ~30–40% is the practical band.
- **sqrt(n)-segment checkpointing** (Chen et al. 2016, *Training Deep Nets with Sublinear Memory Cost*). Checkpoint `sqrt(n)` *segments* out of `n` layers — the memory-optimal segmentation, and the origin of the `O(sqrt(n))` result. This is a different policy from per-block wrapping; do not quote its scaling for per-block checkpointing.

**Prefer selective activation recomputation (the better default).** Instead of recomputing whole blocks, recompute only the tensors that are cheap to recompute and expensive to store — the attention softmax/dropout path — and keep the FLOP-dense matmuls stored. Megatron's *Reducing Activation Recomputation in Large Transformer Models* (arXiv 2205.05198) reports that sequence parallelism plus selective activation recomputation "reduces activation memory by 5x, while reducing execution time overhead from activation recomputation by over 90%", and that training a 530B GPT-3-style model on 2240 A100s reaches "a Model Flops Utilization of 54.2%, which is 29% faster than the 42.1% we achieve using recomputation" (quoted from the abstract).

Express it with `torch.utils.checkpoint.create_selective_checkpoint_contexts` (SAC) or torchtitan's SAC config; `checkpoint_wrapper` is the older FSDP-side entry point and only expresses whole-module recompute.

### FlashAttention already recomputes — do not checkpoint over it

FlashAttention *is* selective checkpointing internally: it stores O plus the softmax statistics (m, ℓ) and recomputes S and P blockwise in its own backward. If you additionally wrap the whole transformer block in `torch.utils.checkpoint`, the block-level recompute re-runs the FlashAttention **forward** kernel, and then FlashAttention's backward recomputes the softmax blockwise a second time. Attention is computed twice in backward while you believe you configured recomputation once. On long context, where attention dominates, this quietly costs MFU and reads as "communication-bound".

Fix: place the checkpoint boundary at the **output of the FlashAttention kernel** rather than at the transformer-layer boundary, so the stored tensor serves both the downstream recompute and FlashAttention's own backward. A selective policy that marks `scaled_dot_product_attention` as *not* recomputable expresses this directly — which is another reason selective recomputation is the better default: it never checkpoints over attention in the first place.

## RL Rollout Infrastructure (Scaling an RL Post-Training Run)

[ai-post-training](../ai-post-training/SKILL.md) routes here for the *systems* side of RL fine-tuning. That skill owns the algorithms (GRPO, DPO, reward design); this section owns only the GPU topology question, which has one structural decision:

- **Colocated** — the trainer and the rollout engine share the same GPUs, alternating between generation and update phases. Simplest to operate and memory-hungry: both the training state and the inference engine's KV cache want the same HBM. Weight sync between phases is cheap because the weights are already there.
- **Disaggregated** — separate GPU pools for rollout generation and for the trainer, with updated weights pushed to the rollout workers each round. Lets each side scale on its own bottleneck (decode-heavy generation is memory-bandwidth-bound, because every token re-reads the weights and KV cache; training is compute-bound large GEMMs) and is what makes *async* RL possible: rollouts for step *n+1* generate while step *n* trains, at the cost of running slightly off-policy. Weight transfer latency becomes a real term in the step budget.

**vLLM** is the common rollout engine (continuous batching is what makes generating thousands of samples per step affordable). **verl** is the usual backbone tying a rollout engine to an FSDP/Megatron trainer and handling the weight-sync path. This is a fast-moving area — verify the current integration story against the projects' own docs rather than treating any specific topology as settled. For serving-side generation tuning itself, see [ai-llm-inference](../ai-llm-inference/SKILL.md).

## Optimizers at Scale

**AdamW** remains the default and the best-understood choice. Its memory cost (two fp32 moments ≈ 2× params) is what ZeRO/FSDP optimizer-state sharding targets.

**Muon / MuonClip** is the notable optimizer shift since 2024: Newton–Schulz orthogonalization of 2-D matmul weight updates, used in production up to trillion-parameter MoE (MuonClip for Kimi K2, arXiv 2507.20534). Its speedup over AdamW shrinks with scale (about 2× reported at Moonlight scale, about 1.1× at 1.2B in the controlled benchmark of Wen et al., arXiv 2509.02046), so measure it on your own model. The algorithm, the speedup evidence, µP interaction and which models use it belong to [ai-pretraining](../ai-pretraining/references/modern-architecture-deltas.md#muon-and-the-speedrun-frontier); this section covers only the systems side.

Practical notes:

- Apply Muon only to 2-D matmul parameters; keep embeddings, the LM head, biases, and norm/scalar params on AdamW (a hybrid optimizer).
- Muon's per-step orthogonalization adds compute but less optimizer memory than Adam's two moments — a useful trade under memory pressure.
- For distributed use, see the DeepSpeed Muon integration; sharding Muon's update across DP ranks needs care.

## Pre-Training Frameworks

| Framework | Best For | Notes |
|-----------|----------|-------|
| litgpt | Research, ≤70B, HF-compatible | Clean PyTorch; easy to read |
| torchtitan | PyTorch-native large-scale | Meta's reference; FSDP2 + CP |
| nanotron | Efficient 3-D parallel | Hugging Face; minimal 3-D parallel pre-training library. (BLOOM was trained with Megatron-DeepSpeed, not nanotron.) Check recent commit activity |
| levanter | TPU / JAX | Stanford CRFM, now under the Marin community — repo is `marin-community/levanter` (`stanford-crfm/levanter` 301-redirects). Check recent commit activity |
| Megatron-LM | >70B, tensor+pipeline+data | NVIDIA; most complex, most scalable |
| modded-nanoGPT | Learning / GPT-2 reproduction | Keller Jordan; speed records; Muon optimizer |
| llm.c | Minimal C/CUDA GPT-2 | Karpathy; educational reference. Check recent commit activity; expect toolchain drift against a current CUDA/PyTorch stack |
| nanochat | End-to-end small-model train+chat | Karpathy; uses Muon; modern reference loop |
| Megatron-Core / NeMo | Modular TP+PP+DP+EP building blocks | NVIDIA; library form of Megatron-LM for MoE + fp8 |

## Reproducing GPT-2 124M (Reference Run)

The parameter count, FLOPs per token, run hours at a given MFU and the warmup live in one place: the [GPT-2 124M Reference Card](../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card) in ai-pretraining. This section covers only the systems choices.

Target: a FineWeb **validation loss** threshold (modded-nanoGPT's speedrun README states its current target) and, as a separate measurement, a HellaSwag **accuracy**. They are different numbers; do not report one as the other.

Use `modded-nanoGPT` or `nanochat` as the run you execute. `llm.c` is the clearest minimal C/CUDA read; check its recent commit activity before running it against a current CUDA/PyTorch stack.

1. Download a FineWeb-Edu 10B-token sample.
2. Fill GPU memory with the micro-batch; use gradient accumulation to reach the logical batch.
3. Enable FlashAttention and bf16. **Leave gradient checkpointing off**: 124M fits without it, and full recomputation costs up to ~33% of throughput (see [Activation / Gradient Checkpointing](#activation--gradient-checkpointing)).
4. Run ~10B tokens; monitor loss and [MFU](#mfu-and-hfu).
5. Cost: take the hours for your GPU count and MFU from the reference card, then multiply by GPUs and the provider's current $/GPU-hr.

## Checkpointing at Scale (DCP)

For sharded training (FSDP2, TP, PP), a single-rank full `state_dict` can force an all-gather onto one rank. Use **`torch.distributed.checkpoint` (DCP)** and follow the [PyTorch DCP recipe](https://docs.pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html):

- Each rank saves its own shard in parallel; DCP handles resharding on load (save on 8 GPUs, resume on 16).
- **`dcp.async_save`** stages a copy in CPU memory and writes in the background. Budget that memory, keep at most one save in flight, and call the returned future's `result()` before relying on the checkpoint. See the [PyTorch async recipe](https://docs.pytorch.org/tutorials/recipes/distributed_async_checkpoint_recipe.html).
- Save model, optimizer, scheduler, progress, and supported dataloader/RNG state together. Test a resumed step; identical bits are not guaranteed across changed topology or nondeterministic kernels.

```python
import torch.distributed.checkpoint as dcp
from torch.distributed.checkpoint.state_dict import get_state_dict

model_state, optim_state = get_state_dict(model, optimizer)
pending = dcp.async_save(
    {"model": model_state, "optim": optim_state},
    checkpoint_id=checkpoint_dir,  # unique directory on a shared filesystem
)
# Continue training; before publishing, reusing, or terminating:
pending.result()
```

PyTorch's default `FileSystemWriter` does not make an `s3://` checkpoint ID an object-store writer. After `pending.result()`, copy the **entire** checkpoint directory, including metadata, to durable storage and verify the copy and restore. For direct S3 writes, configure a compatible writer such as the [AWS S3 connector's `S3StorageWriter`](https://github.com/awslabs/s3-connector-for-pytorch#distributed-checkpoints) and check its current API. Never mark a pending save or upload as a restorable checkpoint.

**Choosing the interval.** The mechanics above say *how* to save; they do not say how often. Derive the cadence from the cluster's failure rate rather than picking a round number: per-device MTBF divides by device count, so a large cluster fails far more often than any one accelerator does, and the interval that balances checkpoint cost against expected lost work follows from that. Async save is what makes a short interval affordable. On spot instances the preemption rate, not hardware MTBF, is the number to work from. See [Failure Budget and Checkpoint Interval](references/failure-budget-and-checkpointing.md) for the fault taxonomy, the arithmetic, and the hedges on the published figures.

**Beyond checkpoint/restart: fault tolerance.** Checkpoint cadence bounds how much work a failure costs; it does not stop the failure from killing the job. `pytorch/torchft` (Meta/PyTorch) does per-step fault tolerance instead — fault-tolerant DDP/HSDP plus LocalSGD/DiLoCo, with a "lighthouse" coordinator that lets replica-group membership change *at step granularity* so a lost node does not require a full-job restart. That is the natural successor to checkpoint-interval arithmetic on a large cluster where node loss is routine rather than exceptional. It is young and moving; verify the current API and maturity against the repo before building a run around it.

## Reproducibility and Determinism at Scale

Debugging a loss spike assumes you can reproduce it. At scale you usually cannot, and it is worth knowing why before you burn GPU-hours on a bisect:

- **Reduction order is not fixed.** NCCL collectives, atomics in fused kernels, and split-K matmuls sum in whatever order the schedule produces, so bitwise-identical reruns are not the default even at fixed seed. Changing the GPU count changes the reduction tree and therefore the numerics.
- **Seed every rank deliberately** — model init, dataloader shuffling, and dropout each need a policy about whether ranks share a seed or offset from it. Save RNG and data position with the checkpoint, then test the resumed step; this improves repeatability without guaranteeing identical bits.
- **`torch.use_deterministic_algorithms(True)`** plus a fixed cuBLAS workspace buys determinism at a real throughput cost. Turn it on to isolate a suspected numerical bug on a small repro, not for a production run.
- When a spike is not reproducible, prefer evidence that survives non-determinism: gradient-norm and activation-norm histories, per-layer max logits, and the data shard in flight — not "run it again and watch."

## Cost Estimation

```
hours ≈ 6·N·D / (num_GPUs × peak FLOP/s per GPU × MFU × 3600)
cost  ≈ hours × num_GPUs × $/GPU-hr
```

N is parameters, D is training tokens, peak is the dense bf16 (or fp8) datasheet figure. Worked rows at **40% MFU**, using historical dense-bf16 datasheet peaks (A100 312 TFLOP/s, H100 989 TFLOP/s; look up the figure for the GPU you actually rent):

| Run | GPUs | 6·N·D | Hours at 40% MFU | GPU-hours |
|-----|------|-------|------------------|-----------|
| GPT-2 124M, 10B tokens | any | see the [reference card](../ai-pretraining/references/pretraining-loop.md#gpt-2-124m-reference-card) | card | card |
| 1B dense, 100B tokens | 8×A100 | 6.0e20 | ~167 h | ~1,340 |
| 7B dense, 100B tokens | 8×A100 | 4.2e21 | ~1,170 h | ~9,350 |
| 7B dense, 1T tokens | 64×H100 | 4.2e22 | ~461 h | ~29,500 |
| Frontier MoE / large dense (fp8/fp4) | rack-scale NVL72 | — | — | reserve and quote pricing |

`ai-scaling-laws/scripts/training_math.py hours` reproduces these rows and `mfu` inverts them. Sanity-check any quoted run time by solving the formula for MFU: check unusually high results against the precision and FLOP definition; above 100% against the correct dense peak is impossible.

**Price lookup step.** GPU-hour prices change month to month and vary by region, commitment and spot versus on-demand. Before budgeting, read the current rate and billing unit from the provider's pricing page (RunPod, Lambda, Vast.ai, Modal or your cloud) and multiply by the GPU-hours above. Add a contingency based on measured setup, checkpoint, and retry time for this workload.

## Rented GPU Cost Discipline

- **Debug on the smallest GPU that fits**: compare current GPU-hour rates before reserving production hardware for debugging.
- **Spot / interruptible instances**: compare the provider's current rates and preemption terms; choose a checkpoint cadence from expected lost work and measured save cost.
- **Durable checkpoint**: finish the DCP save, copy the complete directory to object storage if needed, and verify restore before relying on it.
- **Billing unit**: check the provider's current billing terms and terminate as soon as training ends; do not leave instances idle.
- **Validate checkpoint restore** before starting a long run on spot.
- **Estimate before running**: use the formula above and a contingency derived from a short run.

## Parallelism Promotion Gate

Treat the smallest configuration that fits as the control. Add sharding, tensor, pipeline, or expert parallelism only after a profile identifies the binding memory or communication limit. For each promotion, record model state, global batch and sequence mix, peak memory, step-time breakdown, tokens per second, utilization, and checkpoint size on the same workload. Accept it only after a forced interruption restores to the same optimizer step and the throughput gain survives steady state; setup success or a short warmup run is insufficient.

## Known Traps

- **Debugging on an 8xH100 box**: expensive and unnecessary; always debug on the smallest GPU first.
- **OOM blamed on GPUs when the real cause is the dataloader or precision bug**: profile first with `torch.profiler`; check `torch.cuda.memory_summary()`. For the attribution method (separating loader time from H2D copy time from GPU idle), see [Storage I/O and Dataloader Tuning](references/storage-and-dataloader-io.md).
- **Forgetting to stop the instance**: set a billing alert and calendar reminder; auto-shutdown scripts on training completion.
- **Not checkpointing on spot instances**: a preemption without a recent checkpoint loses hours of training.
- **Picking a checkpoint interval by feel**: the cadence should follow from the cluster-level failure interval (per-device MTBF divided by device count) weighed against checkpoint cost — not from a round step number. See [Failure Budget and Checkpoint Interval](references/failure-budget-and-checkpointing.md).
- **Unverified checkpoints**: a checkpoint written without a checksum can restore corrupted state silently. Hash on write, verify on restore, and keep more than one so a failed verification has a fallback.
- **Using fp16 instead of bf16 on A100+**: fp16 is more prone to loss spikes at pre-training scale; bf16 is safer and equally fast on A100/H100.
- **Mixing FSDP + DeepSpeed**: incompatible; pick one sharding framework per run.
- **Skipping profiling and tuning MFU**: low MFU alone does not identify a cause. Check collectives, dataloader stalls, and kernels in the profiler trace before scaling.
- **Checkpointing over FlashAttention**: wrapping a whole transformer block in `torch.utils.checkpoint` when the block uses FlashAttention recomputes attention twice in backward (once for the block recompute, once inside FA's own backward). Costs MFU silently on long context. Put the checkpoint boundary at the FA kernel output, or use selective recomputation.
- **Using FSDP1 in a new project**: start on FSDP2 (`fully_shard`); check PyTorch's release notes for FSDP1's deprecation status instead of assuming it, and avoid its `state_dict_type` / `FullStateDictConfig` checkpoint path (use DCP).
- **Saving a full `state_dict` from sharded training**: all-gathers the whole model onto one rank and stalls every other GPU. Use DCP (`dcp.async_save`) instead.
- **Loss spikes at scale, then NaN**: not always the optimizer. Common causes are fp16 instead of bf16, missing/late LR warmup, no gradient clipping, or unstable attention logits — mitigate with bf16, grad-clip, QK-norm, and (for MoE) z-loss. Save a checkpoint immediately before resuming from a spike.
- **MoE without a load-balancing loss**: a few experts saturate while the rest idle, tanking effective throughput and quality. Use an aux load-balancing loss or DeepSeek-V3's bias-update scheme.
- **fp8/nvfp4 without a bf16 baseline**: low-precision training can silently degrade loss. Always validate against bf16 on your own workload before a long run.

- FlashAttention version support varies by GPU architecture. Check the official repo for your target hardware.
- DeepSpeed ZeRO-Infinity NVMe offload performance depends heavily on NVMe bandwidth; benchmark before relying on it.
- Framework releases (torchtitan, nanotron, litgpt) move fast; verify current API against the repo's main branch.

## Navigation: Core References

- **[FSDP vs ZeRO Comparison](references/fsdp-vs-zero.md)** - side-by-side tradeoffs, when to pick each, config examples
- **[Parallelism Strategies](references/parallelism-strategies.md)** - DDP, tensor, pipeline, 3-D parallel decision guide
- **[Rented GPU Cost Guide](references/rented-gpu-cost.md)** - provider comparison, spot strategies, cost estimation
- **[Storage I/O and Dataloader Tuning](references/storage-and-dataloader-io.md)** - sharding, NVMe/NFS tuning, GPUDirect Storage, dataloader-bound diagnosis
- **[Failure Budget and Checkpoint Interval](references/failure-budget-and-checkpointing.md)** - fault taxonomy, cluster-level MTBF arithmetic, deriving the checkpoint cadence, ECC/fault-tolerance overhead

## External Sources

See **[data/sources.json](data/sources.json)** for curated primary sources across:

- FlashAttention 1/2/3 papers and implementation
- DeepSpeed ZeRO documentation and ZeRO paper
- PyTorch FSDP2 tutorial and torchtitan paper
- Megatron-LM (tensor parallel), selective activation recomputation (2205.05198), and the sqrt(n)-segment checkpointing origin (Chen et al. 2016)
- DeepSeek-V3 (DualPipe / expert parallelism / fp8) and Ring Attention (context parallel)
- Muon / Kimi K2, DeepSeek-V4, and GLM-5 optimizer reports
- Karpathy's GPT-2 reproduction projects (modded-nanoGPT, nanochat, llm.c) and levanter (marin-community)
- Rented GPU provider pricing and docs
- Reddi, *Machine Learning Systems* Ch. 16 (fault taxonomy, MTBF, ECC overhead)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
