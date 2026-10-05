# Parallelism Strategies Reference

## Table of Contents

- [Overview](#overview)
- [Decision Tree](#decision-tree)
- [Data Parallelism (DDP)](#data-parallelism-ddp)
- [Sharded Data Parallelism (FSDP / ZeRO)](#sharded-data-parallelism-fsdp--zero)
- [Tensor Parallelism](#tensor-parallelism)
- [Pipeline Parallelism](#pipeline-parallelism)
- [3-D Parallelism (Tensor + Pipeline + Data)](#3-d-parallelism-tensor--pipeline--data)
- [Context Parallelism](#context-parallelism)
- [Combining Strategies](#combining-strategies)
- [Canonical Sources](#canonical-sources)

## Overview

Parallelism in distributed training addresses two distinct constraints: **compute scaling** (throughput) and **memory scaling** (fitting the model). Choose the minimum combination that solves your constraint.

| Strategy | Addresses | Communication Pattern | Complexity |
|----------|-----------|----------------------|------------|
| DDP | Compute scaling | AllReduce (gradients) | Low |
| FSDP / ZeRO | Memory + compute | AllGather + ReduceScatter | Medium |
| Tensor Parallel | Memory + compute (intra-node) | AllReduce (per layer) | High |
| Pipeline Parallel | Memory (inter-node) | Point-to-point (activations) | High |
| 3-D Parallel | Very large models | All of the above | Very high |
| Context Parallel | Long sequences | Ring P2P of K/V blocks, or all-to-all over heads (Ulysses) | Medium |
| Expert Parallel | MoE capacity (sparse params) | All-to-all (token dispatch/combine) | High |

## Decision Tree

```text
Can the model fit on one GPU with bf16 + gradient checkpointing?
  YES → use DDP (replicate on all GPUs)
  NO  →
    Can it fit with FSDP2 full shard / ZeRO-3?
      YES → use FSDP / ZeRO-3 (simpler than TP+PP)
      NO  →
        Are GPUs on the same node (NVLink)?
          YES → add tensor parallelism (TP=8 within node)
          NO  → add pipeline parallelism (PP across nodes)
                combine with TP within node
                → 3-D parallelism (TP + PP + DP)
```

## Data Parallelism (DDP)

All workers hold a full model replica. Each processes a different mini-batch. After backward, `AllReduce` synchronizes gradients across all workers. Workers then update identical local copies.

**When it works**: model fits in one GPU; linear scaling up to ~64 GPUs before AllReduce dominates.

**Effective batch size**: `global_batch = micro_batch × grad_accum_steps × num_gpus`. Prefer holding `global_batch` fixed when the GPU count changes (adjust `micro_batch` or `grad_accum_steps`). If it must change, Adam-family optimizers follow the square-root rule, `lr = base_lr × sqrt(global_batch / reference_batch)` (Malladi et al. 2022, arXiv 2205.10287), not the linear rule used for SGD; stay below the critical batch size. See [Changing GPU Count](../SKILL.md#changing-gpu-count-hold-the-global-batch).

```python
torch.distributed.init_process_group(backend="nccl")
model = DistributedDataParallel(model.cuda(), device_ids=[local_rank])
```

## Sharded Data Parallelism (FSDP / ZeRO)

See [fsdp-vs-zero.md](fsdp-vs-zero.md) for detailed comparison. In summary: shards optimizer state, gradients, and/or parameters across workers. Each worker holds a fraction of the model at rest; parameters are all-gathered on demand during forward/backward passes.

## Tensor Parallelism

Splits individual weight matrices across GPUs within a node. For a linear layer `Y = XA` (where A is `[d_model, d_ff]`):

- **Column-parallel**: each GPU holds `A[:, j:j+d_ff/N]`; result is split across GPUs.
- **Row-parallel**: each GPU holds `A[i:i+d_model/N, :]`; inputs must be pre-split; outputs are AllReduced.

Transformer blocks alternate column-parallel (first linear in FFN, Q/K/V projections) and row-parallel (second linear in FFN, output projection). Megatron-style TP (Shoeybi et al. 2019, arXiv 1909.08053) needs two all-reduces in the forward pass (after attention, after the MLP) and two in the backward pass per transformer layer, which is acceptable inside an NVLink domain and expensive over Ethernet.

**Per-GPU NVLink bandwidth by generation** (check the datasheet for the generation you rent):

| Generation | Per-GPU NVLink bandwidth |
|------------|--------------------------|
| A100 / NVLink 3 | 600 GB/s |
| H100 / NVLink 4 | 900 GB/s |
| B200 / NVLink 5 | 1.8 TB/s |

Reason about the rule as a *ratio*, not an absolute: NVLink is roughly an order of magnitude or more above inter-node InfiniBand per GPU, which is why TP stays intra-node. That framing survives the next hardware generation; a quoted GB/s figure does not.

Megatron-LM adds **sequence parallelism (SP)**: shards layernorm and dropout computations across the sequence dimension, reducing per-GPU activation memory proportionally.

**Best for**: model layers that cannot fit on one GPU; same-node high-bandwidth links (NVLink/NVSwitch).

**Typical TP degree**: 4 or 8 (matching GPUs per node).

## Pipeline Parallelism

Assigns contiguous layers (a "stage") to each GPU or node group. Input activations flow forward; gradients flow backward. The "pipeline bubble" is idle GPU time at the start and end of each batch. The 1F1B schedule does not shrink it relative to GPipe; it caps in-flight activations at about `pp_degree` micro-batches. **Interleaved 1F1B** (v model chunks per stage) divides the bubble by v at the cost of more point-to-point communication (Narayanan et al. 2021, arXiv 2104.04473).

**Pipeline bubble fraction** (naive): `(pp_degree - 1) / (num_micro_batches + pp_degree - 1)`. More micro-batches → smaller bubble.

**When to use**: model is too large for FSDP even with TP; inter-node bandwidth is the bottleneck.

Convert to the same units before reasoning about topology — link rates are quoted in **Gb/s** and NVLink in **GB/s**, an 8× difference that has fooled people into thinking cross-node TP is viable. Check the current generation's datasheet: InfiniBand **NDR is 400 Gb/s = 50 GB/s** per link and **XDR is 800 Gb/s = 100 GB/s** per link; HDR's 200 Gb/s = 25 GB/s is the previous generation. Against H100 NVLink 4 at 900 GB/s per GPU that is roughly an 18× gap in GB/s — which is why TP must stay intra-node.

**Complexity cost**: layer assignment, activation checkpointing at stage boundaries, variable memory across stages (first/last stages hold embedding tables).

## 3-D Parallelism (Tensor + Pipeline + Data)

Combines:
- **TP** within a node (e.g., 8 GPUs on one node, TP=8)
- **PP** across nodes (e.g., 4 nodes, PP=4, each stage = one node)
- **DP** across PP-TP groups (e.g., 4 replica groups)

Total GPUs = TP × PP × DP. Used by Megatron-LM and nanotron for models >100B parameters.

Requires careful micro-batch sizing to fill the pipeline and minimize bubble. Megatron-LM's config exposes `tensor-model-parallel-size`, `pipeline-model-parallel-size`, `num-micro-batches`.

## Context Parallelism

Shards the sequence dimension across GPUs. Orthogonal to TP/PP/DP/EP and composes with all of them as another mesh dimension. Attention is the hard part: every query needs every key up to its position, so the shards must exchange K/V. Two families do that differently, and torchtitan ships both:

- **Ring Attention** (arXiv 2310.01889) passes K/V blocks **point-to-point around a ring**, overlapping each transfer with local attention compute on the block already in hand. Bandwidth-bound but with no hard degree limit. Note this is *not* an all-gather — materializing the full sequence on every rank would defeat the purpose.
- **DeepSpeed-Ulysses** does an **all-to-all over the head dimension** instead: each rank ends up with all sequence positions for a subset of heads. Latency-friendlier, but it imposes a hard constraint — **CP degree ≤ number of KV heads**, which bites immediately on GQA models with 8 KV heads.

**Causal load balance.** With causal masking and naive contiguous sharding, rank 0's chunk attends to almost nothing while the last rank attends to the whole prefix — roughly a 2× imbalance, and the slowest rank sets step time. **Zigzag / striped** assignment fixes it by pairing an early chunk with a late chunk on the same rank so every rank carries comparable work. Assume your framework does this only after checking; the naive form is a common default.

**Ordering.** Apply sequence parallelism (SP, the Megatron-style sharding of norm/dropout alongside TP) first — it is close to free. Reach for CP when activation memory along the sequence dimension still dominates after SP. The old ">32k tokens" rule of thumb is not the trigger: frontier runs train at 128k–1M where CP is unavoidable, and CP is also chosen well below 32k when activation memory rather than context length is what binds.

## Expert Parallelism (MoE)

Mixture-of-Experts (MoE) models keep total parameters huge (e.g. 1T) while activating only a few experts per token (e.g. 32B activated). **Expert parallelism (EP)** distributes the experts of an MoE layer across GPUs. The router scores each token, then an **all-to-all** dispatch sends every token to the GPU(s) holding its chosen experts; after the expert FFN, a second all-to-all combines results back to the token's original rank.

**Communication pattern**: all-to-all, not all-reduce. Its cost scales with cross-node bandwidth, so EP is happiest inside a high-bandwidth NVLink domain (e.g. GB200 NVL72). DeepSeek-V3 overlapped this all-to-all with compute via **DualPipe**, achieving near-zero exposed communication and training a 671B MoE with no tensor parallelism.

**MoE-specific tuning**:
- **Load balancing**: an auxiliary loss (or DeepSeek-V3's auxiliary-loss-free bias updates) keeps tokens spread across experts; otherwise a few experts saturate.
- **Dropless routing (modern default)**: block-sparse / grouped GEMM over variable-size expert batches — no capacity factor, no dropped tokens. This is what Megatron-Core and torchtitan default to since MegaBlocks. **Capacity factor / token dropping** is the legacy alternative: it caps tokens per expert and drops or reroutes the overflow to keep GEMM shapes static, trading quality for a fixed throughput and memory envelope. Use it only when you want that cap deliberately.
- **Composes as a mesh dimension** alongside DP/TP/PP/CP. Frameworks: Megatron-Core, DeepSpeed-MoE, nanotron.

**When to use**: the model is sparse (MoE) and its experts exceed one GPU's memory. EP is the cheapest way to scale total capacity because it moves tokens, not weights.

## Combining Strategies

Strategies compose along independent dimensions:

```
                  DP (data parallel replicas)
                 /
model replica ──── TP (weight shards within a node)
                 \
                  PP (layer pipeline across nodes)
```

Start with the simplest strategy that fits the model. Add the next layer of complexity only when profiling shows you are memory-bound and the simpler strategy fails.

Typical progression:
1. DDP (model fits on one GPU)
2. FSDP2 full shard / ZeRO-3 (model doesn't fit, but no need for TP)
3. FSDP + TP (model is very large, same-node NVLink available)
4. FSDP + TP + PP (model exceeds one node's memory)
5. Full 3-D parallel via Megatron-LM or nanotron

## Canonical Sources

- Megatron-LM paper (tensor parallelism): https://arxiv.org/abs/1909.08053
- Reducing activation recomputation (selective checkpointing + sequence parallel): https://arxiv.org/abs/2205.05198
- PyTorch FSDP2 Tutorial: https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html
- DeepSpeed ZeRO paper: https://arxiv.org/abs/1910.02054
- DeepSeek-V3 (DualPipe + expert parallelism + fp8): https://arxiv.org/abs/2412.19437
- Ring Attention (context-parallel foundation): https://arxiv.org/abs/2310.01889
- nanotron 3-D parallel implementation: https://github.com/huggingface/nanotron
- torchtitan context parallelism: https://github.com/pytorch/torchtitan
