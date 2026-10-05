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

> **Context window is per model**: read the model card for the served checkpoint's maximum context; do not plan from a remembered list. At long context (hundreds of thousands of tokens and up), KV cache per sequence can exceed a single node's HBM. Serving that tier requires: (a) an explicit KV-cache budget per context tier, (b) multi-GPU or disaggregated prefill/decode topologies (see `disaggregated-inference.md` and `parallelism-patterns.md`), and (c) KV offload tiers (CPU DRAM or NVMe) evaluated for latency SLO impact before enabling. Size each tier with the formula below and treat very long context as a separate capacity-planning tier.

---

## KV Cache Memory Analysis

### Size Calculation

**Formula** (read every term from the model's `config.json`; never infer KV heads from `hidden_size`):
```
bytes_per_token = 2 (K+V) × num_hidden_layers × num_key_value_heads × head_dim × dtype_bytes
KV cache size   = bytes_per_token × seq_len × batch_size
head_dim        = hidden_size / num_attention_heads   (unless config.json sets head_dim)
```

For MHA models `num_key_value_heads == num_attention_heads`, so `num_key_value_heads × head_dim == hidden_size`. For GQA models it is several times smaller. Plugging `hidden_size` into a GQA model overstates KV memory by `num_attention_heads / num_key_value_heads`. MLA models store a compressed latent instead; use the latent dimension from the model's config or technical report (see architecture-and-attention-serving.md §1).

```python
def kv_cache_gib(num_layers, num_kv_heads, head_dim, seq_len, batch_size, dtype_bytes=2):
    bytes_per_token = 2 * num_layers * num_kv_heads * head_dim * dtype_bytes
    return bytes_per_token * seq_len * batch_size / 1024**3

# Llama-2-13B (MHA: 40 layers, 40 KV heads, head_dim 128, FP16)
kv_cache_gib(40, 40, 128, seq_len=4096, batch_size=32)   # 819,200 B/token -> 100.0 GiB
# Llama-2-70B (GQA: 80 layers, 8 KV heads, head_dim 128, FP16)
kv_cache_gib(80, 8, 128, seq_len=4096, batch_size=32)    # 327,680 B/token -> 40.0 GiB
```

**Memory breakdown** (Llama-2-13B, FP16, batch=32, ctx=4096, worked from the formula above):
- Model weights: ~26 GB (13B params × 2 bytes)
- KV cache: 100 GiB ≈ 107 GB (more than the weights)
- Activations: a few GB, workload-dependent — measure, don't assume
- **Total: ~133 GB+** (order of magnitude — verify against actual GPU memory reporting for your deployment, not this static estimate)

### Memory vs Context Length

Figures below are the formula scaled linearly by context length — not measured benchmarks. The 70B model has more layers than the 13B one but needs less KV per token, because GQA stores 8 KV heads instead of 64. Recompute for your model's `config.json` before capacity planning.

| Context Length | KV Cache (Llama-2-13B, MHA, batch=32) | KV Cache (Llama-2-70B, GQA-8, batch=32) |
|---------------|----------------------------------|----------------------------------|
| 2048 | 50 GiB | 20 GiB |
| 4096 | 100 GiB | 40 GiB |
| 8192 | 200 GiB | 80 GiB |
| 16384 | 400 GiB | 160 GiB |

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
    model="<model-id>",  # pick from the provider's model list
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

**Configuration (SGLang with RadixAttention)**: the radix cache is on by default; there is no flag to enable it.
```bash
python -m sglang.launch_server \
    --model-path <model-id>
# Turn prefix reuse off only for A/B measurement or debugging:
#   --disable-radix-cache
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
    model="<model-id>",  # pick from the provider's model list
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
    model="<model-id>",  # pick from the provider's model list
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

Prefill is one parallel forward pass over the prompt, not a per-token loop.
Decode is the serial part: one step per OUTPUT token.

Without prefix caching:
- Every request prefills all 550 prompt tokens (one parallel pass), then decodes.

With prefix caching:
- First request: prefills 550 tokens and stores the 500-token prefix KV.
- Later requests: prefill only the 50 uncached tokens; the prefix KV is reused.
- Saving: prefill linear-layer FLOPs drop ~11× (550 -> 50 tokens; the new tokens still
  attend over the cached prefix). TTFT falls, but by less than
  11× when prefill is short enough to be memory-bound or fixed overhead dominates.
- Decode time per output token is unchanged; end-to-end latency on long outputs
  improves only by the TTFT saving.
```
Measure TTFT with and without the cache at your prompt lengths; do not multiply
token counts by a per-token latency.

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
    model="<model-id>",  # pick from the provider's model list
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
    model="<model-id>",  # pick from the provider's model list
    max_model_len=2048,  # Limit context
    enable_prefix_caching=True,  # Cache system prompts
    kv_cache_dtype="auto",  # Auto FP8 if supported
    gpu_memory_utilization=0.95
)
```

**2. Long-context workloads (<16k)**:
```python
LLM(
    model="<model-id>",  # pick from the provider's model list
    max_model_len=16384,
    kv_cache_dtype="fp8",  # Reduce memory
    enable_prefix_caching=True,
    tensor_parallel_size=2  # Split across GPUs
)
```

**3. Ultra-long context (>32k)**:
```python
LLM(
    model="<model-id>",  # pick from the provider's model list
    max_model_len=65536,
    kv_cache_dtype="fp8",
    tensor_parallel_size=4,
    # Consider CPU offloading for very long sequences
)
```

**4. Memory-constrained (single GPU, large model)**:
```python
LLM(
    model="<model-id>",  # pick from the provider's model list
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
