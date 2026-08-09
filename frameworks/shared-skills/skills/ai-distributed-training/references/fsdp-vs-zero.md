# FSDP vs DeepSpeed ZeRO: Comparison Reference

## Table of Contents

- [Overview](#overview)
- [When to Pick FSDP](#when-to-pick-fsdp)
- [When to Pick DeepSpeed ZeRO](#when-to-pick-deepspeed-zero)
- [Stage / Strategy Mapping](#stage--strategy-mapping)
- [Memory Model Comparison](#memory-model-comparison)
- [Configuration Quick-Start](#configuration-quick-start)
- [Known Pitfalls](#known-pitfalls)
- [Canonical Sources](#canonical-sources)

## Overview

FSDP (Fully Sharded Data Parallel) is PyTorch-native sharding. DeepSpeed ZeRO is a separate library with more options and more configuration surface. Both achieve similar sharding semantics but differ in integration complexity, debugging experience, and ecosystem compatibility.

As of 2026, FSDP2 (the redesigned version in torchtitan) is the recommended starting point for new PyTorch-based pre-training projects. DeepSpeed ZeRO remains the reference for Hugging Face TRL/Accelerate workflows and when ZeRO-Infinity (NVMe offload) is needed.

## When to Pick FSDP

- Pure PyTorch stack; want to avoid additional dependencies.
- Using torchtitan, litgpt, or a custom training loop.
- Need tight integration with `torch.compile`.
- Model is large but fits on GPU cluster without NVMe offload.
- Team is comfortable debugging PyTorch distributed primitives.

## When to Pick DeepSpeed ZeRO

- Using Hugging Face Trainer / Accelerate (native DeepSpeed integration).
- Need ZeRO-Infinity (NVMe offload for extremely large models).
- Need ZeRO-Offload (CPU offload for optimizer state).
- Existing config management via `deepspeed_config.json`.
- Model or optimizer state genuinely does not fit in GPU memory even with full parameter sharding.

## Stage / Strategy Mapping

| DeepSpeed ZeRO Stage | FSDP2 equivalent (`fully_shard`) | What is Sharded |
|---------------------|-----------------------|-----------------|
| ZeRO-1 | (optimizer-state-only not a native FSDP2 mode) | Optimizer state |
| ZeRO-2 | `reshard_after_forward=False` | Optimizer state + gradients |
| ZeRO-3 | `reshard_after_forward=True` (default) | Optimizer state + gradients + parameters |
| ZeRO-Infinity | No FSDP equivalent | ZeRO-3 + NVMe offload |

(FSDP1 names `NO_SHARD` / `SHARD_GRAD_OP` / `FULL_SHARD` map to the same semantics but are deprecated since PyTorch 2.11.)

## Memory Model Comparison

For a model with `M` parameters and `N` GPUs, memory per GPU for fp32 training (approx):

| Strategy | Params | Gradients | Optimizer State | Total per GPU |
|----------|--------|-----------|-----------------|---------------|
| DDP | M | M | 2M (Adam) | ~4M |
| ZeRO-1 | M | M | 2M/N | ~(2M + 2M/N) |
| ZeRO-2 / FSDP2 (`reshard_after_forward=False`) | M | M/N | 2M/N | ~(M + 3M/N) |
| ZeRO-3 / FSDP2 (`reshard_after_forward=True`) | M/N | M/N | 2M/N | ~4M/N |

At N=8 GPUs, ZeRO-3 / FSDP2 full sharding reduces per-GPU memory to ~1/8 of the baseline.

The `2M` optimizer-state term assumes Adam/AdamW (two fp32 moments). Muon carries less optimizer state per matmul parameter, so the optimizer-state row shrinks if you use a Muon/AdamW hybrid — though the sharding mechanics are unchanged.

## Configuration Quick-Start

### FSDP2 (PyTorch native, >=2.11)

FSDP1 (`FullyShardedDataParallel` + `ShardingStrategy`) is deprecated as of PyTorch 2.11. Use `fully_shard`, which shards each parameter as a DTensor and composes with TP/PP/CP via DeviceMesh:

```python
from torch.distributed.fsdp import fully_shard, MixedPrecisionPolicy

mp = MixedPrecisionPolicy(param_dtype=torch.bfloat16, reduce_dtype=torch.float32)
for block in model.layers:                 # shard each transformer block
    fully_shard(block, mp_policy=mp)        # reshard_after_forward=True ≈ ZeRO-3
fully_shard(model, mp_policy=mp)            # shard the root module last
```

Set `reshard_after_forward=False` on a block for ZeRO-2-like behavior (keep params gathered after forward, fewer all-gathers, more memory). The deprecated FSDP1 equivalent was `ShardingStrategy.FULL_SHARD` / `SHARD_GRAD_OP`.

### DeepSpeed ZeRO-3 config excerpt

```json
{
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": {"device": "none"},
    "offload_param": {"device": "none"},
    "overlap_comm": true,
    "reduce_bucket_size": "auto"
  },
  "bf16": {"enabled": true}
}
```

## Known Pitfalls

- Do not mix FSDP and DeepSpeed in the same training run. They conflict at the distributed primitive level.
- FSDP2 full sharding (`reshard_after_forward=True`, ZeRO-3 equivalent) adds all-gather communication before each forward pass. This can become a bottleneck with high latency inter-node links — profile `dist.all_gather` overhead before scaling beyond one node.
- ZeRO-3 with Hugging Face `generate()` requires special handling; consult DeepSpeed docs on ZeRO-3 inference mode.
- FSDP checkpoint format differs from standard `state_dict` — use `FullStateDictConfig` / `StateDictType` for saving in a format compatible with non-FSDP loading.
- DeepSpeed ZeRO-Infinity NVMe offload is only beneficial if your NVMe bandwidth exceeds ~3 GB/s per GPU; otherwise it is a bottleneck.

## Canonical Sources

- PyTorch FSDP2 Tutorial: https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html
- DeepSpeed ZeRO docs: https://www.deepspeed.ai/docs/config-json/
- ZeRO paper (Rajbhandari et al. 2019): https://arxiv.org/abs/1910.02054
- FSDP2 design + docs in torchtitan: https://github.com/pytorch/torchtitan/blob/main/docs/fsdp.md
- torchtitan paper (FSDP2 + CP + compile in production): https://arxiv.org/abs/2410.06511
