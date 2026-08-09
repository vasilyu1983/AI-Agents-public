# KV Cache Optimization

Production strategies for optimizing key-value cache in LLM inference - the #1 latency and memory bottleneck for long-context workloads.

## Table of Contents

- [Overview](#overview)
- [KV Cache Memory Analysis](#kv-cache-memory-analysis)
- [Memory vs Context Length](#memory-vs-context-length)
- [Optimization Strategies](#optimization-strategies)
- [1. PagedAttention (vLLM)](#1-pagedattention-vllm)
- [2. FlashAttention-3 and FlashInfer](#2-flashattention-3-and-flashinfer)
- [SGLang RadixAttention](#sglang-radixattention)
- [3. KV Cache Quantization](#3-kv-cache-quantization)
- [4. KV Cache Offloading — 3-Tier Model](#4-kv-cache-offloading--3-tier-model)
- [5. Prefix Caching / Prompt Caching](#5-prefix-caching-prompt-caching)
- [6. Grouped Prefill](#6-grouped-prefill)
- [7. Sequence Parallelism](#7-sequence-parallelism)
- [Configuration Recommendations](#configuration-recommendations)
- [Monitoring & Debugging](#monitoring--debugging)
- [Validation Checklist](#validation-checklist)
- [References](#references)

## Overview

**What is KV Cache?**
- Cached key and value tensors from attention layers
- Prevents recomputing attention for previous tokens
- Essential for efficient autoregressive generation

**Why it's critical**:
- KV cache = largest memory consumer (often > model weights)
- Memory bandwidth bottleneck for long contexts (>8k tokens)
- Directly impacts: latency, throughput, cost, max batch size

**Key challenges**:
- Memory grows linearly with sequence length
- Fragmentation from variable-length sequences
- Bandwidth saturation on GPU → CPU transfers

> **June 2026 threshold update**: 1M-token context windows (Claude Fable 5, `claude-fable-5`; Claude Opus 4.8, `claude-opus-4-8`) and 2M-token windows (Gemini 3.1 Pro) are now operational at GA scale. These are new KV-cache sizing thresholds that invalidate planning figures derived from prior 200k–8k norms. At 1M tokens with Llama-scale parameter counts, KV cache can reach several TB of HBM equivalent — well beyond single-node GPU capacity. Production deployments serving these context lengths require: (a) explicit KV-cache budget allocation per context tier, (b) multi-GPU or disaggregated prefill/decode topologies (see `disaggregated-inference.md` and `parallelism-patterns.md`), and (c) KV offload tiers (CPU DRAM or NVMe) evaluated for latency SLO impact before enabling. Treat 1M/2M context as a distinct capacity-planning tier separate from sub-128k workloads.

---

## KV Cache Memory Analysis

### Size Calculation

**Formula**:
```
KV cache size = 2 (K+V) × num_layers × batch_size × seq_len × hidden_size × dtype_bytes
```

**Example: Llama-2-13B**:
```python
def calculate_kv_cache_size(
    num_layers=40,
    batch_size=32,
    seq_len=4096,
    hidden_size=5120,
    dtype_bytes=2  # FP16
):
    size_bytes = 2 * num_layers * batch_size * seq_len * hidden_size * dtype_bytes
    size_gb = size_bytes / (1024**3)
    return size_gb

# Result: 100GB for 32 sequences @ 4k context (worked through the formula above with
# Llama-2-13B's published config: 40 layers, hidden_size=5120, FP16).
# This is MORE than the model weights (~26GB for 13B FP16).
# NOTE: this formula assumes MHA (num_kv_heads == num_query_heads), which matches
# Llama-2. For GQA/MLA models substitute num_kv_heads (or the MLA latent dimension)
# for hidden_size — the reduction can be 4-8x (GQA) or ~2.7-4.7x vs GQA (MLA); see
# architecture-and-attention-serving.md §1 for those figures and their source.
```

**Memory breakdown** (Llama-2-13B, FP16, worked from the formula above):
- Model weights: ~26GB
- KV cache (batch=32, ctx=4096): ~100GB
- Activations: a few GB, workload-dependent — measure, don't assume
- **Total: ~126GB+** (order of magnitude — verify against actual GPU memory reporting for your deployment, not this static estimate)

### Memory vs Context Length

Figures below are the same formula scaled linearly by context length and model size (Llama-2-70B: 80 layers, hidden_size=8192) — not independently measured benchmarks. Recompute for your actual model config before capacity planning.

| Context Length | KV Cache (Llama-2-13B, batch=32) | KV Cache (Llama-2-70B, batch=32) |
|---------------|----------------------------------|----------------------------------|
| 2048 | 50GB | 160GB |
| 4096 | 100GB | 320GB |
| 8192 | 200GB | 640GB |
| 16384 | 400GB | 1280GB |

**Takeaway**: KV cache dominates memory budget for long contexts

---

## Optimization Strategies

### 1. PagedAttention (vLLM)

**What it is**: Dynamically allocate KV cache in fixed-size blocks

**Benefits**:
- Eliminates fragmentation (variable-length sequences)
- Enables massive batching (100+ concurrent requests)
- Memory sharing across requests (prefix caching)

**How it works**:
```
Traditional: Allocate max_seq_len for every request upfront
  → Wastes memory for short sequences
  → Fragmentation prevents optimal batching

PagedAttention: Allocate blocks on-demand as sequence grows
  → Only use memory actually needed
  → Reuse freed blocks immediately
```

**Configuration (vLLM)**:
```python
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-2-13b-hf",
    max_model_len=8192,
    block_size=16,  # KV cache block size (tokens per block)
    gpu_memory_utilization=0.95,  # Use 95% of GPU memory
    enable_prefix_caching=True  # Reuse KV cache for common prefixes
)
```

**Performance impact**:
- 2-4x higher throughput vs static allocation
- 80-90% memory utilization (vs 50-60% without paging)

**Validation**:
```python
# V0-only API — removed in current vLLM (V0 fully deprecated); verify V1 equivalent at docs.vllm.ai/en/stable/usage/v1_guide/
# engine = LLMEngine.from_engine_args(engine_args)
# stats = engine.get_stats()  # V0 dict-access pattern removed in V1

# V1: use Prometheus /metrics endpoint (vllm:kv_cache_usage_perc gauge)
# or LLM.get_metrics() — see docs.vllm.ai/en/stable/design/v1/metrics.html
```

---

### 2. FlashAttention-3 and FlashInfer

**What it is**: Memory-efficient attention algorithms with kernel-level optimization

**FlashAttention Evolution**:

| Version | GPU Utilization (H100, as reported in the FA-3 paper) | Key Features |
|---------|-----------------|--------------|
| FlashAttention-1 | not H100-benchmarked in the FA-3 paper — pre-Hopper era | Fused kernel, O(N) memory |
| FlashAttention-2 | ~35% | Improved tiling, better parallelism |
| **FlashAttention-3** | **~75% (740 TFLOPs/s, FP16)** | Async TMA, FP8, Hopper-optimized |

**FlashAttention-3 (Hopper GPUs)** — figures per Dao et al., "FlashAttention-3" (arXiv:2407.08608):
- **~75% utilization on H100 with FP16/BF16** (740 TFLOPs/s), vs ~35% for FA-2
- 1.5-2x speedup over FA-2
- **FP8 support**: approaches ~1.2 PFLOPs/s on H100
- Exploits NVIDIA Hopper features: async TMA, warp specialization
- These are the paper's reported figures on its benchmark configuration — re-verify against the current paper/blog and your own hardware before quoting a specific number in a customer-facing report.

**FlashInfer (MLSys 2025 Best Paper)**:
- NVIDIA's new kernel library for LLM inference
- Unified API for attention, GEMM, MoE operations
- Multiple backends: FlashAttention-2/3, cuDNN, CUTLASS, TensorRT-LLM
- **Integrated into vLLM and SGLang**

### Why FlashInfer Matters

- NVIDIA is releasing optimized kernels through FlashInfer (not just TensorRT-LLM)
- JIT compilation for custom attention patterns
- Supports RadixAttention (SGLang's KV reuse pattern)
- 29-69% inter-token-latency reduction vs compiler backends
- 28-30% latency reduction for long-context inference

### SGLang RadixAttention

**What it is**: Keep user prompts in KV cache for reuse across requests

**Benefits**:
- 6.4x higher throughput on structured workloads
- 3.7x lower latency vs baseline systems
- Excellent for chat, RAG, and few-shot scenarios

**How it works**:
```text
Request 1: [System] + [Few-shot examples] + [User query A]
Request 2: [System] + [Few-shot examples] + [User query B]

RadixAttention: Cache [System] + [Few-shot examples] separately
  → Only compute [User query] for each new request
  → Massive savings for repetitive prompt structures
```

**Configuration (Transformers)**:
```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-13b-hf",
    attn_implementation="flash_attention_2",  # FA-3 auto-selected on Hopper
    torch_dtype=torch.float16
)
```

**Configuration (vLLM with FlashInfer)**:
```bash
# Note: --enable-flashinfer flag and "FlashInfer is default in V1" status are unconfirmed
# against current vLLM V1 docs; verify at docs.vllm.ai/en/stable/usage/v1_guide/
# V0-only flag pattern — may be removed in current vLLM (V0 fully deprecated)
# vllm serve meta-llama/Llama-3-70B --enable-flashinfer

# Current approach: vLLM V1 integrates FlashAttention-3 internally; check current docs
# for attention backend configuration options
```

**Configuration (SGLang with RadixAttention)**:
```bash
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-70B \
    --enable-radix-attention
```

**Performance comparison** (illustrative shape only — these are not measured benchmark
numbers; run your own comparison at your model size, batch, and hardware before citing a
speedup ratio):
```
Directionally, going from unfused/standard attention -> FlashAttention-2 -> FlashAttention-3
on Hopper reduces latency and memory per batch and raises tok/s, roughly in that order of
magnitude improvement per step (each generation both faster and more memory-efficient than
the last). FA-3's H100 utilization and FP8/BF16 throughput gains over FA-2 are documented in
the FlashAttention-3 paper/blog (see References) — pull the exact figures from that source
for your target config rather than reusing a fixed ratio here.
```

---

### 3. KV Cache Quantization

**What it is**: Store cached keys/values in lower precision

**Benefits**:
- 2-4x memory reduction
- Minimal quality loss (<1% accuracy)
- Enables larger batches or longer contexts

**Precision options**:
- **FP16** → **FP8**: 2x compression, ~0.5% quality loss
- **FP16** → **INT8**: 2x compression, ~1% quality loss
- **FP16** → **INT4**: 4x compression, ~2-3% quality loss (experimental)

**Configuration (vLLM)**:
```python
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-2-13b-hf",
    kv_cache_dtype="fp8",  # or "auto" for automatic selection
    quantization="fp8"  # Also quantize model weights
)
```

**Memory savings example** (Llama-2-13B, batch=32, ctx=4096):
- FP16 KV cache: 100GB (from the corrected worked example above)
- FP8 KV cache: 50GB (2x reduction)
- INT8 KV cache: 50GB (2x reduction)

**Quality validation**:
```python
import numpy as np

def measure_quality_impact(prompts, model_fp16, model_fp8):
    """Compare outputs with FP16 vs FP8 KV cache"""
    results = []

    for prompt in prompts:
        output_fp16 = model_fp16.generate(prompt)
        output_fp8 = model_fp8.generate(prompt)

        # Compare token-by-token accuracy
        tokens_fp16 = tokenizer.encode(output_fp16)
        tokens_fp8 = tokenizer.encode(output_fp8)

        # Calculate token match rate
        min_len = min(len(tokens_fp16), len(tokens_fp8))
        matches = sum(t1 == t2 for t1, t2 in zip(tokens_fp16[:min_len], tokens_fp8[:min_len]))
        match_rate = matches / min_len

        results.append(match_rate)

    avg_match_rate = np.mean(results)
    print(f"Token match rate: {avg_match_rate * 100:.2f}%")
    # Expected: 98-99% for FP8, 96-98% for INT8

    return avg_match_rate
```

---

### 4. KV Cache Offloading — 3-Tier Model

**What it is**: Move KV cache down the memory hierarchy when GPU HBM is the bottleneck.

**When to use**:
- Very long contexts (>32k tokens) where KV cache exceeds available HBM
- Memory-constrained scenarios, offline/batch processing
- Not suitable for interactive real-time APIs (<1s TTFT requirement) at tier 2+

**3-Tier model**:

```
Tier 1 — GPU HBM (always active)
  Fast, no transfer overhead. Prefer keeping hot prefixes here.
  vLLM prefix caching (enable_prefix_caching=True) handles eviction automatically.

Tier 2 — CPU DRAM (production-deployed paths)
  Option A: LMCache (open-source KDN for vLLM and TGI)
    https://lmcache.ai/
    Offloads KV blocks from HBM to DRAM with streaming and compression.
    Integrates with vLLM; verify V1 compatibility at https://github.com/LMCache/LMCache
  Option B: vLLM V1 native CPU offload
    V1 removed GPU↔CPU KV-cache swapping used for preemption (confirmed: docs.vllm.ai/en/stable/usage/v1_guide/).
    Any CPU-offload path for long-context serving: verify current V1 docs before enabling.
    https://docs.vllm.ai/en/stable/

Tier 3 — NVMe SSD (research-stage, not production-recommended)
  Projects like Tutti and Mooncake have demonstrated NVMe KV offloading in research settings.
  Not validated for production latency SLOs. Treat as experimental — hedge all claims
  until you have verified current deployment status and latency profiles on your hardware.
```

**Trade-offs by tier**:
- Tier 1 → 2: PCIe transfer overhead (~several ms per block swap); measure actual impact
- Tier 2 → 3: NVMe bandwidth (~5–7 GB/s) is far below PCIe (~32 GB/s); suitable only for batch workloads

**Note on DeepSpeed `offload_kv_cache`**: The `deepspeed.inference.init_inference(offload_kv_cache=True)` API
is a DeepSpeed-specific flag, not a recommended production serving path for token generation.
See `assets/inference/template-deepspeed-inference.md` for scope context.

---

### 5. Prefix Caching / Prompt Caching

**What it is**: Reuse KV cache for common prompt prefixes

**Use cases**:
- System prompts (same for every request)
- Few-shot examples (repeated in every prompt)
- Conversation history (multi-turn chat)

**Example**:
```
Prompt 1: [System prompt] + [User: Hello]
Prompt 2: [System prompt] + [User: How are you?]
Prompt 3: [System prompt] + [User: Tell me a joke]

Without prefix caching: Recompute [System prompt] 3 times
With prefix caching: Compute [System prompt] once, reuse 3 times
```

**Configuration (vLLM)**:
```python
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-2-13b-hf",
    enable_prefix_caching=True
)

# Prompts with common prefix automatically benefit
system_prompt = "You are a helpful AI assistant. You are friendly and concise."

prompts = [
    system_prompt + "\n\nUser: Hello",
    system_prompt + "\n\nUser: How are you?",
    system_prompt + "\n\nUser: Tell me a joke"
]

# First request: computes full KV cache
# Next 2 requests: reuse cached system_prompt KV, only compute user message
outputs = model.generate(prompts)
```

**Performance impact**:
```
Scenario: System prompt = 500 tokens, user message = 50 tokens

Without prefix caching:
- Time per request: 550 tokens × 10ms = 5.5s

With prefix caching:
- First request: 550 tokens × 10ms = 5.5s
- Subsequent: 50 tokens × 10ms = 0.5s (11x faster!)
```

**Implementation tips**:
- Structure prompts with common prefixes first
- Use deterministic ordering (cache hit depends on exact match)
- Monitor cache hit rate

---

### 6. Grouped Prefill

**What it is**: Process multiple prefills together in single batch

**Benefits**:
- Better GPU utilization during prefill phase
- Reduced latency for concurrent requests
- Improves throughput for bursty traffic

**How it works**:
```
Traditional: Process each prefill sequentially
  Request 1 prefill → Request 1 decode → Request 2 prefill → Request 2 decode → ...

Grouped prefill: Batch prefills together
  [Request 1, 2, 3 prefills] → [Request 1, 2, 3 decode] → ...
```

**Configuration (vLLM)**:
```python
# Enabled by default in vLLM's continuous batching
# No explicit configuration needed

# Monitor prefill batch sizes
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-2-13b-hf",
    max_num_batched_tokens=8192,  # Max tokens in prefill batch
    max_num_seqs=256  # Max sequences in batch
)
```

---

### 7. Sequence Parallelism

**What it is**: Split sequence dimension across GPUs

**Benefits**:
- Reduces per-GPU memory for KV cache
- Enables longer sequences on same hardware
- Complements tensor parallelism

**When to use**:
- Very long contexts (>16k tokens)
- Multi-GPU setups
- Combined with tensor parallelism

**Implementation (Megatron-LM)**:
```python
# Megatron-LM sequence parallelism
args = {
    'tensor_model_parallel_size': 4,  # TP across 4 GPUs
    'sequence_parallel': True,  # Enable sequence parallelism
    'use_flash_attn': True
}
```

**Performance**:
```
Without sequence parallelism:
- Max context: 8k tokens (per-GPU memory limit)
- 4 GPUs × 8k = 32k total capacity (wasted)

With sequence parallelism:
- Max context: 32k tokens (split across 4 GPUs)
- 4 GPUs × 32k = 32k total capacity (fully utilized)
```

---

## Configuration Recommendations

### By Use Case

**1. High-throughput API (short contexts)**:
```python
LLM(
    model="meta-llama/Llama-2-13b-hf",
    max_model_len=2048,  # Limit context
    enable_prefix_caching=True,  # Cache system prompts
    kv_cache_dtype="auto",  # Auto FP8 if supported
    gpu_memory_utilization=0.95
)
```

**2. Long-context workloads (<16k)**:
```python
LLM(
    model="meta-llama/Llama-2-13b-hf",
    max_model_len=16384,
    kv_cache_dtype="fp8",  # Reduce memory
    enable_prefix_caching=True,
    tensor_parallel_size=2  # Split across GPUs
)
```

**3. Ultra-long context (>32k)**:
```python
LLM(
    model="meta-llama/Llama-2-13b-hf",
    max_model_len=65536,
    kv_cache_dtype="fp8",
    tensor_parallel_size=4,
    # Consider CPU offloading for very long sequences
)
```

**4. Memory-constrained (single GPU, large model)**:
```python
LLM(
    model="meta-llama/Llama-2-70b-hf",
    quantization="awq",  # INT4 model weights
    kv_cache_dtype="fp8",  # FP8 KV cache
    max_model_len=4096,  # Limit context
    gpu_memory_utilization=0.95
)
```

---

## Monitoring & Debugging

### Key Metrics

**Monitor these KV cache metrics**:
```python
# V0-only API — removed in current vLLM (V0 fully deprecated); verify V1 equivalent at docs.vllm.ai/en/stable/usage/v1_guide/
# stats = engine.get_stats()  # V0 dict-access pattern; fields like num_blocks_used no longer exposed this way

# V1: scrape Prometheus /metrics endpoint (enabled by default on the serve API)
# Relevant gauges:
#   vllm:kv_cache_usage_perc       — cache utilization fraction
#   vllm:prefix_cache_hits          — cumulative prefix cache hits
#   vllm:prefix_cache_queries       — cumulative prefix cache queries
# See: https://docs.vllm.ai/en/stable/design/v1/metrics.html
```

**GPU memory breakdown**:
```python
import torch

print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
print(f"Max allocated: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB")
```

### Common Issues

**Problem**: OOM during prefill
- Cause: Batch size too large for prompt length
- Fix: Reduce `max_num_batched_tokens` or enable KV cache quantization

**Problem**: OOM during decode
- Cause: KV cache grows beyond allocation
- Fix: Reduce `max_model_len` or use FP8 KV cache

**Problem**: Low cache hit rate (<20%)
- Cause: Variable prompt structure
- Fix: Standardize prompt templates, move common prefixes to start

**Problem**: High fragmentation (utilization <70%)
- Cause: Variable sequence lengths with static allocation
- Fix: Use PagedAttention (vLLM)

---

## Validation Checklist

- [ ] PagedAttention enabled (vLLM)
- [ ] FlashAttention enabled (check logs/config)
- [ ] KV cache quantization configured (FP8 for >4k context)
- [ ] Cache size appropriate for max batch × max context
- [ ] Prefix caching enabled for common prompts
- [ ] Offloading strategy chosen if memory-bound
- [ ] Cache hit rate > 50% (for workloads with common prefixes)
- [ ] Memory utilization > 80% (not fragmented)
- [ ] No OOM errors under max load

---

## References

- PagedAttention Paper: https://arxiv.org/abs/2309.06180
- FlashAttention-2: https://arxiv.org/abs/2307.08691
- FlashAttention-3: https://pytorch.org/blog/flashattention-3/
- FlashInfer (MLSys 2025): https://arxiv.org/abs/2501.01005
- FlashInfer GitHub: https://github.com/flashinfer-ai/flashinfer
- SGLang RadixAttention: https://lmsys.org/blog/2024-07-25-sglang-llama3/
- vLLM Documentation: https://docs.vllm.ai/
- vLLM V1 Engine Guide (V0 deprecated, removed APIs): https://docs.vllm.ai/en/stable/usage/v1_guide/
- vLLM V1 Metrics Design: https://docs.vllm.ai/en/stable/design/v1/metrics.html
- LMCache (CPU DRAM KV offload, vLLM integration): https://lmcache.ai/
- DeepSpeed Inference: https://www.deepspeed.ai/tutorials/inference-tutorial/
- NVIDIA Attention Optimizations: https://docs.nvidia.com/deeplearning/performance/
