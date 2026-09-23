---
name: ai-distributed-training
description: "Guides multi-GPU pre-training: DDP, FSDP2, ZeRO, tensor/pipeline/expert parallelism, fp8/Muon. Use when scaling a run, training MoE, or reproducing GPT-2 on rented GPUs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Distributed Training - Systems Performance Skill

**Operational focus**: picking and implementing the right parallelism strategy, not the theory. Covers data parallelism through FSDP/ZeRO/tensor+pipeline parallelism, memory-efficient attention, mixed precision at scale, activation checkpointing, rented-GPU cost discipline, and reproducing GPT-2 124M as the canonical sanity check.

Profile before you scale. Debug on the smallest GPU that fits. Stop the instance when done.

## ASCII Flow

```text
single GPU (debug/prototype)
  └─ DDP: replicate model, all-reduce gradients — scales until the gradient all-reduce stops hiding behind compute
      └─ FSDP2 / ZeRO: shard optimizer state, gradients, params across GPUs
          └─ tensor parallelism: split weight matrices across GPUs (intra-node)
              └─ pipeline parallelism: split layers across nodes (inter-node)
                  └─ context parallelism: shard the sequence dim (long context)
                      └─ expert parallelism: route MoE experts across GPUs (all-to-all)
                          └─ N-D parallelism: DP + TP + PP + CP + EP (frontier MoE)

profile-before-scale
  └─ nsys / torch.profiler → find bottleneck (compute? memory? dataloader?)
      └─ fix bottleneck at small scale, then scale
```

## When to Use This Skill

Activate when the user asks about:

- Choosing between DDP, FSDP2, DeepSpeed ZeRO stages 1/2/3, or Megatron-LM
- Training Mixture-of-Experts (MoE) models: expert parallelism, all-to-all, load balancing
- OOM errors on multi-GPU training runs
- Memory-efficient attention (FlashAttention-2/3, xformers)
- Mixed precision (bf16, fp8, nvfp4) trade-offs at pre-training scale
- Optimizer choice at scale (AdamW vs Muon/MuonClip)
- Targeting current-gen hardware (H100, Blackwell B200/GB200 NVL72, early Rubin NVL72 access)
- Gradient checkpointing vs activation checkpointing cost
- Pre-training frameworks: litgpt, torchtitan, nanotron, levanter
- Reproducing GPT-2 (modded-nanoGPT or nanochat as the active reference; llm.c as the educational one)
- Rented GPU cost management (RunPod, Lambda, Vast.ai, Modal)
- Spot / interruptible instance checkpoint strategies
- Profiling a training run before deciding to scale

## Scope Boundaries (Use These Skills for Depth)

- **Data mix, filtering, dedup, decontamination** -> [ai-data-curation-pretraining](../ai-data-curation-pretraining/SKILL.md). Before spending on N GPUs, the data mix matters more than the parallelism — a better corpus beats a better topology at the same budget, and it is far cheaper to change.
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
5. **Wire checkpointing**: use Distributed Checkpoint (DCP) for sharded state, save async to object storage every N steps; test restore before long runs.
6. **Scale and re-profile**: verify near-linear throughput scaling; fix communication bottlenecks.
7. **Evaluate at checkpoints, not just at the end**: run a small fixed eval suite on every saved checkpoint alongside the loss curve. Loss falling while a downstream benchmark flatlines is the signal that catches a bad data mix or a broken tokenizer *while the GPUs are still running*, and gating only on systems metrics (MFU, throughput) will not surface it. See [ai-evals](../ai-evals/SKILL.md) for harness and gate design.
8. **Stop instance**: confirm instance termination; verify storage persistence; check billing.

## Quick Reference

| Decision | Default Move | Promote When | Avoid |
|----------|-------------|--------------|-------|
| Parallelism for ≤8 GPUs | DDP or FSDP2 (ZeRO-2 equiv) | Model does not fit in one GPU | Jumping to tensor parallel before model is too large |
| Parallelism for >8 GPUs | FSDP2 (ZeRO-3 equiv) or DeepSpeed ZeRO-3 | Multiple nodes needed | Mixing FSDP + DeepSpeed naively |
| FSDP version | FSDP2 (`fully_shard`, DTensor) | All new PyTorch projects | FSDP1 (`FullyShardedDataParallel`) — deprecated since PyTorch 2.11 |
| MoE routing at scale | Expert parallelism + all-to-all | Sparse MoE, experts exceed one GPU | TP on experts before EP (all-to-all is cheaper on NVLink) |
| Attention kernel | FlashAttention-2/3 | A100+ / H100 (FA3 = Hopper) | xformers as default (verify support for your GPU) |
| Mixed precision | bf16 | A100 / H100 (native bf16) | fp16 on A100+ (bf16 is safer; less loss spike risk) |
| Low-precision training | fp8 (H100 TransformerEngine/torchao) | Proven recipe + per-tile scaling | nvfp4/fp8 without loss-vs-bf16 validation |
| Optimizer | AdamW | Default, well-understood | — |
| Optimizer (frontier) | Muon / MuonClip | Matmul params, want ~1.3–1.5× token efficiency | Muon on embeddings/scalars (keep those on AdamW) |
| Gradient checkpointing | Selective activation recomputation (SAC) | Any model >1B params; full per-block recompute only when SAC still does not fit | Wrapping a whole block that contains FlashAttention (double-recompute); quoting sqrt(n) savings for per-block policy |
| Optimizer state sharding | ZeRO-1 | Memory pressure from optimizer | ZeRO-3 when params fit on one GPU |
| Compile | `torch.compile` on the model | Want MFU; using torchtitan/FSDP2 | Leaving eager mode on long production runs |
| Framework for ≤7B pre-training | litgpt or torchtitan | Need Megatron-grade scale | Rolling your own training loop before reading existing frameworks |
| Dev / debug GPU | Smallest A10G or L4 that fits | Need bf16 native | H100/B200/Rubin for debugging (cost bloat) |
| Production training GPU | H100; B200/GB200 NVL72 for frontier; Rubin NVL72 where available | Need fp8/nvfp4 + NVLink-domain scale | Renting Blackwell/Rubin to debug a 124M model |
| Checkpoint storage | S3-compatible object store + DCP async | Spot instances (checkpoint every N steps) | Local disk only (lost on preemption) |

## Parallelism Deep Dive

### Data Parallelism (DDP)

Each worker holds a full model replica. Forward + backward runs independently per GPU. `AllReduce` synchronizes gradients. **What sets the ceiling is gradient size ÷ interconnect bandwidth, not a GPU count** — the all-reduce must finish inside the backward pass it overlaps. In practice that is order-64 GPUs on a well-connected cluster and far less on a small model over Ethernet; measure exposed all-reduce time in the profiler rather than trusting any number, including this one. Memory cost: full model + optimizer state on every GPU.

```python
# PyTorch DDP minimal setup
model = DistributedDataParallel(model, device_ids=[local_rank])
```

### FSDP2 (Fully Sharded Data Parallel)

PyTorch-native. Shards parameters, gradients, and optimizer state across all workers. **Use FSDP2 (`fully_shard`) for all new work** — the original `FullyShardedDataParallel` (FSDP1, FlatParameter-based) is deprecated as of PyTorch 2.11. FSDP2 shards each parameter individually as a DTensor (`Shard(dim=0)`), giving simpler/inspectable sharded state dicts, cleaner composition with TP/PP/CP via DeviceMesh, and tight `torch.compile` integration.

ZeRO-stage equivalents map onto `reshard_after_forward`:

- `reshard_after_forward=False` → keep params gathered after forward (ZeRO-2-like: shard grads + optimizer state, trade memory for fewer all-gathers)
- `reshard_after_forward=True` (default) → re-shard params after forward (ZeRO-3-like: shard params + grads + optimizer state)

```python
# FSDP2 (PyTorch >=2.11). Shard each transformer block, then the root.
from torch.distributed.fsdp import fully_shard, MixedPrecisionPolicy

mp = MixedPrecisionPolicy(param_dtype=torch.bfloat16, reduce_dtype=torch.float32)
for block in model.layers:
    fully_shard(block, mp_policy=mp)
fully_shard(model, mp_policy=mp)
```

FSDP1 (`FullyShardedDataParallel` + `ShardingStrategy.FULL_SHARD/SHARD_GRAD_OP/NO_SHARD`) still appears in older tutorials; migrate to FSDP2. Checkpoints are compatible across the two, but the construction API is not.

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

Splits model layers across nodes (or GPU groups). Interleaved schedules (1F1B) reduce pipeline bubble overhead. Adds complexity: microbatch sizing, bubble fraction tuning. Typically combined with TP and DP in 3-D parallelism (Megatron-LM, nanotron).

`torch.distributed.pipelining` is the PyTorch-native PP API (`ScheduleGPipe`, `Schedule1F1B`, `ScheduleInterleaved1F1B`); it composes with FSDP2 and TP through DeviceMesh, so it is the PP layer that fits the rest of the stack this skill recommends without adopting Megatron or nanotron wholesale.

**DualPipe** (DeepSeek-V3, 2024) is a bidirectional pipeline schedule that fully overlaps forward/backward compute with communication, driving the bubble toward zero — the reference design for large MoE training where cross-node all-to-all would otherwise dominate.

### Expert Parallelism (MoE)

Mixture-of-Experts models activate only a few experts per token, so total params (e.g. 1T) vastly exceed activated params (e.g. 32B). **Expert parallelism (EP)** places different experts on different GPUs; the router dispatches each token to its experts via **all-to-all** communication (dispatch), then a second all-to-all gathers results (combine). EP composes with DP/TP/PP/CP as an extra mesh dimension.

Key concerns specific to MoE training:

- **Load balancing**: an auxiliary load-balancing loss (or DeepSeek-V3's auxiliary-loss-free bias-update scheme) keeps tokens spread across experts; without it, a few experts saturate and the rest idle.
- **All-to-all is the bottleneck**, not all-reduce. It scales with cross-node bandwidth — keep EP inside the NVLink domain where possible, and overlap it with compute (DualPipe). DeepSeek-V3 trained a 671B MoE with **no tensor parallelism**, relying on EP + DualPipe + fp8 instead.
- **Dropless routing is the modern default**; capacity factors are the legacy alternative. A capacity factor caps tokens per expert and drops or reroutes the overflow — simple, but it discards tokens to keep the GEMM shapes static. Since MegaBlocks, **dropless MoE** expresses the expert FFN as a block-sparse / grouped GEMM over variable-size expert batches, so no token is dropped and no capacity factor is tuned; Megatron-Core and torchtitan ship it. Reach for a capacity factor only when you deliberately want a throughput cap or a fixed memory envelope.
- **Frameworks**: Megatron-Core, DeepSpeed-MoE, and nanotron implement EP; `torch.distributed` provides the all-to-all primitives.

## Overlapping Communication with Compute

"MFU below 30% means communication bound" tells you how to *detect* the problem. This is how to fix it: exposed collectives are the target, and the lever is overlap, not less communication.

- **FSDP2 prefetch.** The parameter all-gather for layer *n+1* should be in flight while layer *n* computes, and the gradient reduce-scatter for layer *n* should overlap layer *n-1*'s backward. Tune backward prefetch depth rather than accepting the default on an unusual model shape.
- **Async collectives.** `async_op=True` returns a handle you wait on later; the work between issue and wait is your overlap window. Gradient bucketing (DDP) is the same idea — group small gradients so a collective is worth launching.
- **Async tensor parallelism** fuses TP collectives into the matmul epilogue so the communication for one tile happens while the next tile computes. This is how torchtitan hides TP collectives; on recent PyTorch it is built on symmetric-memory primitives. Naming and API surface here are moving fast — check torchtitan's current config rather than quoting a flag from here.
- **DualPipe** (above, under Pipeline Parallelism) is the MoE-scale version of the same principle: schedule so the all-to-all is never exposed.

Measure overlap directly. A `torch.profiler` trace shows whether the NCCL stream sits idle during compute (good) or the compute stream sits idle during a collective (exposed communication). A ratio derived from step time cannot distinguish the two.

## Will It Fit? A Memory Sanity Check

Before choosing a parallelism strategy, check whether activations alone rule out the naive configuration. The Megatron activation formula for a transformer layer stack is `s·b·h·L·(10 + 24/t + 5·a·s/(h·t))` bytes (s = sequence length, b = micro-batch, h = hidden, L = layers, a = heads, t = TP degree).

For s=8192, b=1, h=4096, L=32, a=32, t=1 this comes to roughly **380 GB** — a *single* 8k-context sample does not fit on an 80GB H100 without recomputation or tensor parallelism. That is the arithmetic that decides between "add gradient checkpointing" and "add TP", and it is worth running before renting anything. Note the `5·a·s/(h·t)` term is quadratic in sequence length: at long context, attention activations, not weights, are what breaks you.

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

`bf16` (bfloat16) is the safe default for A100+ and H100. Same exponent range as fp32 (avoids the overflow spikes common in fp16), 16-bit mantissa precision. `torch.amp.autocast('cuda', dtype=torch.bfloat16)` or pass `torch_dtype=torch.bfloat16`. Gradient scaler (`torch.amp.GradScaler('cuda')`) is needed for fp16 but not for bf16. (The `torch.cuda.amp.autocast` / `torch.cuda.amp.GradScaler` spellings are deprecated — use the `torch.amp` forms.)

**fp8** is now production-proven on Hopper (H100), not just emerging. DeepSeek-V3 trained at fp8 with fine-grained scaling — per-token 1×128 / per-block 128×128 tiles plus high-precision CUDA-core accumulation — keeping the loss within ~0.25% of bf16. Use **TransformerEngine** or **torchao float8** for the linear layers; keep a bf16/fp32 master copy of weights and the optimizer state. Validate loss-vs-bf16 on your workload before committing a long run.

*What "use fp8" actually means to set* — an endorsement is not a recipe, and these are the parts people get wrong:

- **Which tensors stay higher precision**: embeddings, the LM head, all norms, and (in MoE) the router. fp8 applies to the FLOP-dense linear layers, not the whole model.
- **Scaling granularity**: per-tensor is the simplest and the most fragile; per-tile (DeepSeek-V3's 1×128 activations / 128×128 weights) is what made a long fp8 run hold. Delayed scaling reuses a scale from prior steps (cheaper, needs an amax history); current scaling computes it in-step (safer, costlier).
- **Accumulation stays high-precision** — fp8 inputs, fp32 accumulate. This is not optional.
- **First and last layers are commonly excluded** from fp8 even when everything else converts.
- Read the recipe off your framework's own docs (TransformerEngine `fp8_autocast` recipes, torchao `float8` configs) rather than a blog post; the defaults differ between them and both move.

**nvfp4 / fp4** arrives with Blackwell. The B200/GB200 add hardware FP4 (including NVIDIA's NVFP4, 16-element micro-scaled blocks with e4m3 scales, vs MXFP4's 32-element UE8M0 blocks). It has moved past pure research: NVIDIA pre-trained a **12B model on 10T tokens with NVFP4 matching the fp8 baseline** (arXiv 2509.25149), and MXFP4 needed ~36% more tokens to reach the same loss — so NVFP4 is the stronger FP4 format. Still validate against bf16/fp8 on your own workload before a long run; the recipe (which tensors stay higher-precision, scaling, outlier handling) is less battle-tested than fp8.

### Hardware Tiers (mid-2026)

- **A10G / L4** — cheap debug and architecture validation. Native bf16 on L4.
- **A100 80GB** — bf16 workhorse; still common and cost-effective on spot.
- **H100** — bf16 + fp8 (TransformerEngine), FlashAttention-3, NVLink/NVSwitch domains. Now the mainstream production tier, not the frontier.
- **Blackwell B200 / GB200 NVL72** — mainstream frontier: fp4/nvfp4 hardware, ~2–3× faster training than H100, and a 72-GPU NVLink domain (NVL72) that lets EP/TP span a whole rack at NVLink bandwidth. Widely available on major clouds by mid-2026.
- **Rubin / Vera Rubin NVL72** — newest generation: entered production ~June 2026, with cloud/neocloud availability (AWS, GCP, Azure, CoreWeave, Lambda, Nebius) rolling out through H2 2026. Treat as capacity-constrained and premium-priced for now; verify current availability and quoted pricing before planning around it. Reserve any Blackwell/Rubin tier for frontier-scale runs, not 124M debugging.

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

**Prefer selective activation recomputation (the 2026 default).** Instead of recomputing whole blocks, recompute only the tensors that are cheap to recompute and expensive to store — the attention softmax/dropout path — and keep the FLOP-dense matmuls stored. Megatron's *Reducing Activation Recomputation in Large Transformer Models* (arXiv 2205.05198) reports that sequence parallelism plus selective activation recomputation "reduces activation memory by 5x, while reducing execution time overhead from activation recomputation by over 90%", and that training a 530B GPT-3-style model on 2240 A100s reaches "a Model Flops Utilization of 54.2%, which is 29% faster than the 42.1% we achieve using recomputation" (quoted from the abstract, verified 2026-08-31).

Express it with `torch.utils.checkpoint.create_selective_checkpoint_contexts` (SAC) or torchtitan's SAC config; `checkpoint_wrapper` is the older FSDP-side entry point and only expresses whole-module recompute.

### FlashAttention already recomputes — do not checkpoint over it

FlashAttention *is* selective checkpointing internally: it stores O plus the softmax statistics (m, ℓ) and recomputes S and P blockwise in its own backward. If you additionally wrap the whole transformer block in `torch.utils.checkpoint`, the block-level recompute re-runs the FlashAttention **forward** kernel, and then FlashAttention's backward recomputes the softmax blockwise a second time. Attention is computed twice in backward while you believe you configured recomputation once. On long context, where attention dominates, this quietly costs MFU and reads as "communication-bound".

Fix: place the checkpoint boundary at the **output of the FlashAttention kernel** rather than at the transformer-layer boundary, so the stored tensor serves both the downstream recompute and FlashAttention's own backward. A selective policy that marks `scaled_dot_product_attention` as *not* recomputable expresses this directly — which is another reason selective recomputation is the better default: it never checkpoints over attention in the first place.

## RL Rollout Infrastructure (Scaling an RL Post-Training Run)

[ai-post-training](../ai-post-training/SKILL.md) routes here for the *systems* side of RL fine-tuning. That skill owns the algorithms (GRPO, DPO, reward design); this section owns only the GPU topology question, which has one structural decision:

- **Colocated** — the trainer and the rollout engine share the same GPUs, alternating between generation and update phases. Simplest to operate and memory-hungry: both the training state and the inference engine's KV cache want the same HBM. Weight sync between phases is cheap because the weights are already there.
- **Disaggregated** — separate GPU pools for rollout generation and for the trainer, with updated weights pushed to the rollout workers each round. Lets each side scale on its own bottleneck (generation is throughput-bound, training is memory-bound) and is what makes *async* RL possible: rollouts for step *n+1* generate while step *n* trains, at the cost of running slightly off-policy. Weight transfer latency becomes a real term in the step budget.

**vLLM** is the common rollout engine (continuous batching is what makes generating thousands of samples per step affordable). **verl** is the usual backbone tying a rollout engine to an FSDP/Megatron trainer and handling the weight-sync path. This is a fast-moving area — verify the current integration story against the projects' own docs rather than treating any specific topology as settled. For serving-side generation tuning itself, see [ai-llm-inference](../ai-llm-inference/SKILL.md).

## Optimizers at Scale

**AdamW** remains the default and the best-understood choice. Its memory cost (two fp32 moments ≈ 2× params) is what ZeRO/FSDP optimizer-state sharding targets.

**Muon / MuonClip** is the notable frontier shift since 2024. Muon (Keller Jordan, originating in modded-nanoGPT speedruns) applies Newton–Schulz orthogonalization to 2-D matmul weight matrices, treating each weight as a matrix rather than a flat vector. It delivers roughly 1.3–1.5× token efficiency over AdamW on pre-training and holds the modded-nanoGPT GPT-2 speed records. *"Muon is Scalable for LLM Training"* (arXiv 2502.16982) supplied the two fixes — weight decay and per-parameter update-scale adjustment — that make it work at scale without bespoke tuning. By 2026 it trains trillion-param MoE in production: **MuonClip** (a stability-clamped variant) pre-trained Moonshot's **Kimi K2** (1T-param MoE, 15.5T tokens; arXiv 2507.20534), and Muon now also underpins **DeepSeek-V4** (arXiv 2606.19348 names Muon explicitly for faster convergence and stability) and **GLM-4.5/GLM-5** (Zhipu/Z.ai; GLM-5's paper, arXiv 2602.15763, adds a "Muon Split" per-head orthogonalization plus a zero-redundancy distributed Muon implementation), plus Karpathy's nanochat. It is a serious AdamW replacement at frontier scale, not a speedrun curiosity. Re-verify against the primary report before quoting exact figures — these are recent releases and details can be revised.

Practical notes:

- Apply Muon only to 2-D matmul parameters; keep embeddings, the LM head, biases, and norm/scalar params on AdamW (a hybrid optimizer).
- Muon's per-step orthogonalization adds compute but less optimizer memory than Adam's two moments — a useful trade under memory pressure.
- For distributed use, see the DeepSpeed Muon integration; sharding Muon's update across DP ranks needs care.

## Pre-Training Frameworks

| Framework | Best For | Notes |
|-----------|----------|-------|
| litgpt | Research, ≤70B, HF-compatible | Clean PyTorch; easy to read |
| torchtitan | PyTorch-native large-scale | Meta's reference; FSDP2 + CP |
| nanotron | Efficient 3-D parallel | HuggingFace; powers BLOOM/IDEFICS training. Last push 2026-05-26 — active but slower-cadence than torchtitan/Megatron-LM |
| levanter | TPU / JAX | Stanford CRFM, now under the Marin community — repo is `marin-community/levanter` (`stanford-crfm/levanter` 301-redirects). Last push 2026-01-26, slower-moving than torchtitan/Megatron-LM |
| Megatron-LM | >70B, tensor+pipeline+data | NVIDIA; most complex, most scalable |
| modded-nanoGPT | Learning / GPT-2 reproduction | Keller Jordan; speed records; Muon optimizer |
| llm.c | Minimal C/CUDA GPT-2 | Karpathy; educational reference. Last release 2025-06-26 — stable but not actively developed; expect toolchain drift against a current CUDA/PyTorch stack |
| nanochat | End-to-end small-model train+chat | Karpathy; uses Muon; modern reference loop |
| Megatron-Core / NeMo | Modular TP+PP+DP+EP building blocks | NVIDIA; library form of Megatron-LM for MoE + fp8 |

## Reproducing GPT-2 124M (Reference Run)

Target: ~3.28 loss on FineWeb/Hellaswag after ~10B tokens.

Use `modded-nanoGPT` or `nanochat` — both are actively developed against a current toolchain. `llm.c` is still the clearest minimal C/CUDA read, but its last release is 2025-06-26; treat it as an educational reference rather than the run you execute today.

1. Download FineWeb-edu 10B token sample.
2. Set batch size to fill GPU memory (gradient accumulation for logical large batch).
3. Enable FlashAttention, bf16, gradient checkpointing.
4. Run for ~10B tokens; monitor loss curve and MFU (model FLOP utilization).
5. Cost estimate: ~$50-150 on 4×A100 80 GB on RunPod spot (8-12 hours).

Full GPT-2 124M with full convergence checks: **~$100-300** depending on GPU type and provider.

## Checkpointing at Scale (DCP)

For sharded training (FSDP2, TP, PP), a single-rank `state_dict` is the wrong pattern — it forces an all-gather of the full model onto one rank and serializes saving. Use **`torch.distributed.checkpoint` (DCP)**:

- Each rank saves its own shard in parallel; DCP handles resharding on load (save on 8 GPUs, resume on 16).
- **`dcp.async_save`** offloads the write so training continues while the checkpoint flushes to storage — critical on spot instances where every minute of stall is wasted cost.
- Save model + optimizer + dataloader/RNG state together so a resume is bit-for-bit resumable, not just architecturally loadable.

```python
import torch.distributed.checkpoint as dcp
state = {"model": model, "optim": optimizer}        # FSDP2 DTensors handled natively
dcp.async_save(state, checkpoint_id=f"s3://bucket/run/step-{step}")
```

**Choosing the interval.** The mechanics above say *how* to save; they do not say how often. Derive the cadence from the cluster's failure rate rather than picking a round number: per-device MTBF divides by device count, so a large cluster fails far more often than any one accelerator does, and the interval that balances checkpoint cost against expected lost work follows from that. Async save is what makes a short interval affordable. On spot instances the preemption rate, not hardware MTBF, is the number to work from. See [Failure Budget and Checkpoint Interval](references/failure-budget-and-checkpointing.md) for the fault taxonomy, the arithmetic, and the hedges on the published figures.

**Beyond checkpoint/restart: fault tolerance.** Checkpoint cadence bounds how much work a failure costs; it does not stop the failure from killing the job. `pytorch/torchft` (Meta/PyTorch, verified live 2026-08-31) does per-step fault tolerance instead — fault-tolerant DDP/HSDP plus LocalSGD/DiLoCo, with a "lighthouse" coordinator that lets replica-group membership change *at step granularity* so a lost node does not require a full-job restart. That is the natural successor to checkpoint-interval arithmetic on a large cluster where node loss is routine rather than exceptional. It is young and moving; verify the current API and maturity against the repo before building a run around it.

## Reproducibility and Determinism at Scale

Debugging a loss spike assumes you can reproduce it. At scale you usually cannot, and it is worth knowing why before you burn GPU-hours on a bisect:

- **Reduction order is not fixed.** NCCL collectives, atomics in fused kernels, and split-K matmuls sum in whatever order the schedule produces, so bitwise-identical reruns are not the default even at fixed seed. Changing the GPU count changes the reduction tree and therefore the numerics.
- **Seed every rank deliberately** — model init, dataloader shuffling, and dropout each need a policy about whether ranks share a seed or offset from it. Save RNG state with the checkpoint (as the DCP section says) so a *resume* is reproducible even when a fresh run is not.
- **`torch.use_deterministic_algorithms(True)`** plus a fixed cuBLAS workspace buys determinism at a real throughput cost. Turn it on to isolate a suspected numerical bug on a small repro, not for a production run.
- When a spike is not reproducible, prefer evidence that survives non-determinism: gradient-norm and activation-norm histories, per-layer max logits, and the data shard in flight — not "run it again and watch."

## Cost Estimation

```
cost ≈ $/GPU-hr × num_GPUs × training_hours
```

Example: 4×A100 80GB at $2.50/GPU-hr × 10 hours = **$100**

| Run Type | GPUs | Hours | Est. Cost |
|----------|------|-------|-----------|
| GPT-2 124M debug (single GPU) | 1×A10G | 2-4 h | $1-3 |
| GPT-2 124M full run | 4×A100 | 8-12 h | $80-150 |
| GPT-2 124M fast (H100 cluster) | 8×H100 | 1-2 h | $80-160 |
| 7B model pre-training (100B tok) | 8×A100 | ~100 h | ~$2000 |
| Frontier MoE / large dense (fp8/fp4) | GB200 or Rubin NVL72 | varies | rack-scale; reserve/quote pricing |

Always check current spot pricing on RunPod, Lambda Labs, Vast.ai, or Modal before budgeting. Spot/interruptible discounts are typically 30-70% off on-demand.

## Rented GPU Cost Discipline

- **Debug on the smallest GPU that fits** (A10G at ~$0.60/hr vs H100 at ~$4/hr).
- **Spot / interruptible instances**: 30-70% cheaper; checkpoint every N steps (not just every epoch).
- **Checkpoint to object storage immediately** (S3-compatible): rclone, aws-cli, or provider's SDK.
- **Per-second billing**: terminate as soon as training ends; do not leave instances idle.
- **Validate checkpoint restore** before starting a long run on spot.
- **Estimate before running**: use the formula above; add 20% buffer for profiling/debugging.

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
- **Skipping profiling and tuning MFU**: low MFU (below 30%) means the run is communication or dataloader bound, not compute bound. Fix before scaling. Check exposed collectives in the profiler trace before concluding the network is the limit — the fix is usually overlap, not less communication.
- **Checkpointing over FlashAttention**: wrapping a whole transformer block in `torch.utils.checkpoint` when the block uses FlashAttention recomputes attention twice in backward (once for the block recompute, once inside FA's own backward). Costs MFU silently on long context. Put the checkpoint boundary at the FA kernel output, or use selective recomputation.
- **Using FSDP1 in a new project**: deprecated since PyTorch 2.11; start on FSDP2 (`fully_shard`) or inherit unmaintained APIs.
- **Saving a full `state_dict` from sharded training**: all-gathers the whole model onto one rank and stalls every other GPU. Use DCP (`dcp.async_save`) instead.
- **Loss spikes at scale, then NaN**: not always the optimizer. Common causes are fp16 instead of bf16, missing/late LR warmup, no gradient clipping, or unstable attention logits — mitigate with bf16, grad-clip, QK-norm, and (for MoE) z-loss. Save a checkpoint immediately before resuming from a spike.
- **MoE without a load-balancing loss**: a few experts saturate while the rest idle, tanking effective throughput and quality. Use an aux load-balancing loss or DeepSeek-V3's bias-update scheme.
- **fp8/nvfp4 without a bf16 baseline**: low-precision training can silently degrade loss. Always validate against bf16 on your own workload before a long run.

## Common Anti-Patterns

- Adding more GPUs before understanding the current bottleneck.
- Using ZeRO-3 or tensor parallelism before the model is too large for simpler strategies.
- Training without a checkpoint on spot instances.
- Leaving an idle GPU instance running while reviewing results.
- Treating a DeepSpeed config from a blog post as production-ready without profiling on your workload.
- Using full fp32 training at scale (memory waste; use bf16 + loss scaling instead).

## Core Principles

1. **Profile before you scale**: identify the bottleneck (compute, memory, communication, or dataloader) at small scale before spending on more GPUs.
2. **Smallest GPU that fits for dev**: use A10G or L4 for debugging and architecture validation; reserve H100 for production runs.
3. **Understand one parallelism strategy fully before combining**: DDP → FSDP → 3-D parallel; do not combine before each layer is mastered.
4. **Checkpoint often on interruptible**: save to durable object storage every N steps; test restore before long runs.
5. **Stop the instance**: training end ≠ task end; terminate, verify persistence, confirm billing stopped.

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

## Fact-Checking

- GPU pricing, spot availability, and provider features change frequently. Always verify against current provider pricing pages before budgeting.
- FlashAttention version support varies by GPU architecture. Check the official repo for your target hardware.
- DeepSpeed ZeRO-Infinity NVMe offload performance depends heavily on NVMe bandwidth; benchmark before relying on it.
- Framework releases (torchtitan, nanotron, litgpt) move fast; verify current API against the repo's main branch.
- Known bugs, regressions, and framework footguns must be verified against current primary sources before being treated as fact.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
