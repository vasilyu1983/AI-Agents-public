# Parallelism Patterns for Large Model Inference

Production strategies for distributing LLM inference across multiple GPUs, optimizing for different model architectures and hardware configurations.

## Overview

**Choose parallelism type based on:**
- Model architecture (wide vs deep vs sparse MoE)
- GPU interconnect bandwidth (NVLink, PCIe, InfiniBand)
- Inference latency requirements
- Memory constraints per GPU

## Tensor Parallelism (TP)

**What it is**: Split individual layers across multiple GPUs (horizontal sharding)

**Best for**:
- Wide models with large hidden dimensions
- High-bandwidth interconnects (NVLink required)
- Low-latency inference (minimal communication overhead)

**How it works**:
- Split weight matrices column-wise or row-wise
- Distribute computation within each layer
- Synchronize activations after each layer

**Configuration example (vLLM)**:
```python
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,  # Split across 4 GPUs
    dtype="float16"
)
```

**Performance characteristics**:
- Communication: High (all-reduce after every layer)
- Latency impact: Low (NVLink bandwidth ~600 GB/s)
- Scaling efficiency: 80-95% with NVLink

**Hardware requirements**:
- NVLink or NVSwitch for multi-GPU nodes
- 600+ GB/s interconnect bandwidth recommended
- GPUs on same physical node preferred

**Validation checklist**:
- [ ] NVLink topology verified: `nvidia-smi topo -m`
- [ ] TP degree divides model dimensions evenly
- [ ] Communication overhead < 15% of compute time
- [ ] Memory balanced across GPUs (±5%)

## Pipeline Parallelism (PP)

**What it is**: Distribute different layers to different GPUs (vertical sharding)

**Best for**:
- Deep models with many layers
- Cross-node inference (lower bandwidth OK)
- Memory-constrained scenarios

**How it works**:
- Split model into stages (consecutive layer groups)
- Process micro-batches in pipeline fashion
- Overlap computation and communication

**Configuration example (DeepSpeed)**:
```python
ds_config = {
    "pipeline": {
        "stages": 8,  # 8 pipeline stages
        "micro_batch_size": 4,
        "partition_method": "uniform"
    }
}
```

**Pipeline bubble mitigation**:
- Use multiple micro-batches per batch
- Overlap forward and backward passes (for training)
- Schedule: GPipe, 1F1B (one-forward-one-backward)

**Performance characteristics**:
- Communication: Low (only at stage boundaries)
- Latency impact: Medium (pipeline fill/drain overhead)
- Scaling efficiency: 60-75% (depends on bubble size)

**Bubble calculation**:
```
Bubble time = (num_stages - 1) / num_microbatches * stage_time
```

**Validation checklist**:
- [ ] Micro-batch count ≥ 4 × num_stages
- [ ] Stage compute times balanced (±10%)
- [ ] Pipeline bubble < 20% of total time
- [ ] Memory usage balanced across stages

## Expert Parallelism (EP) - Mixture of Experts

**What it is**: Distribute expert networks across GPUs

**Best for**:
- MoE models (Mixtral, GPT-4 style architectures)
- Sparse activation patterns
- Large model capacity with controlled compute

**How it works**:
- Each GPU hosts subset of experts
- Route tokens to appropriate expert GPUs
- Experts process in parallel

**Configuration example (Megatron-LM)**:
```python
moe_config = {
    "expert_parallel_size": 8,  # 8 GPUs for experts
    "num_experts": 64,
    "top_k": 2,  # Activate top-2 experts per token
    "capacity_factor": 1.25
}
```

**Performance characteristics**:
- Communication: Variable (depends on routing)
- Load balancing: Critical (use auxiliary losses)
- Scaling efficiency: 70-90% (depends on load balance)

**Load balancing strategies**:
- Auxiliary load balancing loss during fine-tuning
- Dynamic capacity factors
- Expert choice routing (instead of token choice)

**Validation checklist**:
- [ ] Expert utilization balanced (coefficient of variation < 0.3)
- [ ] Capacity factor prevents token dropping
- [ ] Routing overhead < 10% of expert compute
- [ ] Top-k selection appropriate for task

## Data Parallelism (DP)

**What it is**: Replicate model on multiple GPUs, process different batches

**Best for**:
- High-throughput serving (many concurrent requests)
- Independent requests (no shared KV cache)
- Horizontal scaling

**How it works**:
- Each GPU has full model copy
- Load balancer distributes requests
- No inter-GPU communication during inference

**Configuration example**:
```yaml
# Kubernetes deployment
replicas: 4  # 4 independent model replicas
resources:
  limits:
    nvidia.com/gpu: 1
```

**Performance characteristics**:
- Communication: None (fully independent)
- Latency impact: None (per-replica)
- Scaling efficiency: ~100% (linear)

**Validation checklist**:
- [ ] Load balancer configured (round-robin or least-connections)
- [ ] Health checks on all replicas
- [ ] Autoscaling policies defined
- [ ] Model weights synced across replicas

## Fully Sharded Data Parallel (FSDP)

**What it is**: Shard model parameters, optimizer states, and gradients

**Best for**:
- Training large models (less common for inference)
- Inference on modified/adapters
- Memory-constrained multi-GPU setups

**How it works**:
- Shard model parameters across GPUs
- All-gather for computation
- Reduce-scatter for gradients (training)

**Configuration example (PyTorch)**:
```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = FSDP(
    model,
    sharding_strategy="FULL_SHARD",
    cpu_offload=False
)
```

**Validation checklist**:
- [ ] Sharding strategy matches use case
- [ ] All-gather bandwidth adequate
- [ ] Memory reduction verified

## Hybrid Parallelism Strategies

### TP + PP (Most Common)

**Pattern**: Tensor parallel within nodes, pipeline parallel across nodes

**Example**: 70B model on 16 GPUs (4 nodes × 4 GPUs)
- TP=4 (within each node via NVLink)
- PP=4 (across 4 nodes via InfiniBand)

**Configuration (vLLM)**:
```python
model = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,
    pipeline_parallel_size=4
)
```

### TP + EP (MoE Models)

**Pattern**: Tensor parallel for dense layers, expert parallel for MoE layers

**Example**: Mixtral 8x7B on 8 GPUs
- TP=2 for dense layers
- EP=8 for expert layers (each GPU hosts 8 experts)

### 3D Parallelism: TP + PP + DP

**Pattern**: Combine all three for massive scale

**Example**: 175B model on 64 GPUs
- TP=8 (within node)
- PP=4 (across nodes)
- DP=2 (replicas for throughput)

## Decision Matrix

| Model Size | GPUs | Interconnect | Recommended Strategy |
|------------|------|--------------|---------------------|
| <7B | 1 | N/A | Single GPU |
| 7-13B | 2-4 | NVLink | TP=2-4 |
| 13-70B | 4-8 | NVLink | TP=4-8 |
| 70-175B | 8-16 | NVLink + IB | TP=8 + PP=2-4 |
| >175B | 16+ | NVLink + IB | TP=8 + PP=4+ |
| MoE (Mixtral) | 8+ | NVLink | TP=2-4 + EP=4-8 |
| High throughput | Any | Any | DP (multiple replicas) |

## Communication Overhead Analysis

**Measure communication cost**:
```python
import torch.distributed as dist

# Profile all-reduce time
start = time.time()
dist.all_reduce(tensor)
torch.cuda.synchronize()
comm_time = time.time() - start

# Compare to compute time
compute_ratio = compute_time / comm_time
# Target: ratio > 10 for efficient parallelism
```

**Optimization strategies**:
- Overlap communication with computation
- Use gradient accumulation to reduce sync frequency
- Compress gradients (FP16/BF16)
- Use NCCL for multi-GPU communication

## Troubleshooting

**Problem**: Poor TP scaling (< 80% efficiency)
- Check: NVLink bandwidth saturation
- Check: Unbalanced layer sizes
- Fix: Reduce TP degree or use PP instead

**Problem**: High PP bubble overhead
- Check: Micro-batch count too low
- Check: Stage compute times unbalanced
- Fix: Increase micro-batches or rebalance stages

**Problem**: Expert load imbalance in MoE
- Check: Routing distribution (`expert_counts`)
- Fix: Add load balancing loss or adjust capacity factor

**Problem**: FSDP slow all-gather
- Check: Network bandwidth between nodes
- Fix: Use faster interconnect or reduce sharding degree

## Performance Validation

```python
# Benchmark script
import time
import torch

def benchmark_parallelism(model, inputs, warmup=10, iterations=100):
    # Warmup
    for _ in range(warmup):
        _ = model(inputs)

    torch.cuda.synchronize()
    start = time.time()

    for _ in range(iterations):
        _ = model(inputs)

    torch.cuda.synchronize()
    end = time.time()

    throughput = iterations / (end - start)
    return throughput

# Expected results
# Single GPU: 10 tok/s
# TP=4: 35-40 tok/s (ideal: 40, efficiency: 87.5-100%)
# TP+PP: varies by configuration
```

## References

- Megatron-LM Parallelism: https://arxiv.org/abs/2104.04473
- vLLM Multi-GPU: https://docs.vllm.ai/en/latest/serving/distributed_serving.html
- DeepSpeed Pipeline: https://www.deepspeed.ai/tutorials/pipeline/
- NCCL Performance: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html
