# KV Cache Optimization

Production strategies for optimizing key-value cache in LLM inference - the #1 latency and memory bottleneck for long-context workloads.

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

# Result: 80GB for 32 sequences @ 4k context
# This is MORE than the model weights (26GB for 13B FP16)
```

**Memory breakdown** (Llama-2-13B, FP16):
- Model weights: 26GB
- KV cache (batch=32, ctx=4096): 80GB
- Activations: ~4GB
- **Total: 110GB** (vs 26GB without batching/context)

### Memory vs Context Length

| Context Length | KV Cache (Llama-2-13B, batch=32) | KV Cache (Llama-2-70B, batch=32) |
|---------------|----------------------------------|----------------------------------|
| 2048 | 40GB | 137GB |
| 4096 | 80GB | 274GB |
| 8192 | 160GB | 548GB |
| 16384 | 320GB | 1096GB |

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
# Check block utilization
from vllm import EngineArgs

engine_args = EngineArgs(...)
engine = LLMEngine.from_engine_args(engine_args)

# Monitor block usage
stats = engine.get_stats()
print(f"Blocks used: {stats['num_blocks_used']} / {stats['num_blocks_total']}")
print(f"Block utilization: {stats['num_blocks_used'] / stats['num_blocks_total'] * 100:.1f}%")
```

---

### 2. FlashAttention-3 and FlashInfer (2025+ Standard)

**What it is**: Memory-efficient attention algorithms with kernel-level optimization

**FlashAttention Evolution**:

| Version | GPU Utilization | Key Features |
|---------|-----------------|--------------|
| FlashAttention-1 | ~25% | Fused kernel, O(N) memory |
| FlashAttention-2 | ~35% | Improved tiling, better parallelism |
| **FlashAttention-3** | **~85%** | Async TMA, FP8, Hopper-optimized |

**FlashAttention-3 Breakthrough (Hopper GPUs)**:
- **85% utilization on H100** (vs 35% for FA-2)
- 1.5-2x speedup over FA-2 with BF16 (840 TFLOPs/s)
- **FP8 support**: 1.3 PFLOPs/s on H100
- Exploits NVIDIA Hopper features: async TMA, warp specialization

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
# FlashInfer is now the default attention backend in vLLM
pip install flashinfer -i https://flashinfer.ai/whl/cu121/torch2.4/

# vLLM auto-detects and uses FlashInfer/FA-3 if available
vllm serve meta-llama/Llama-3-70B --enable-flashinfer
```

**Configuration (SGLang with RadixAttention)**:
```bash
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-70B \
    --enable-radix-attention
```

**Performance comparison**:
```
Benchmark: Llama-2-13B, batch=32, seq_len=4096

Standard Attention:
- Latency: 2.5s per batch
- Memory: 160GB
- Throughput: 800 tok/s

FlashAttention-2:
- Latency: 0.9s per batch (2.8x faster)
- Memory: 90GB (1.8x reduction)
- Throughput: 2200 tok/s (2.75x higher)

FlashAttention-3 (H100):
- Latency: 0.45s per batch (5.5x faster)
- Memory: 85GB
- Throughput: 4400 tok/s (5.5x higher)
- GPU utilization: 85% (vs 35% FA-2)
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
- FP16 KV cache: 80GB
- FP8 KV cache: 40GB (2x reduction)
- INT8 KV cache: 40GB (2x reduction)

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

### 4. KV Cache Offloading

**What it is**: Move KV cache to CPU memory or disk when GPU memory full

**When to use**:
- Very long contexts (>32k tokens)
- Memory-constrained scenarios
- Offline/batch processing (latency less critical)

**Trade-offs**:
- Frees GPU memory for more batching
- Adds latency (PCIe transfer overhead)
- Requires high CPU ↔ GPU bandwidth

**Implementation (DeepSpeed)**:
```python
from deepspeed.inference import init_inference

model = init_inference(
    model,
    mp_size=1,
    dtype=torch.float16,
    checkpoint=None,
    enable_cuda_graph=False,
    replace_with_kernel_inject=True,
    kv_cache_dtype=torch.float16,
    offload_kv_cache=True  # Enable CPU offloading
)
```

**Performance impact**:
```
Without offloading:
- Max batch size: 16 (GPU memory limit)
- Latency: 1.2s
- Throughput: 512 tok/s

With CPU offloading:
- Max batch size: 64 (4x larger)
- Latency: 2.5s (2x slower due to transfers)
- Throughput: 1280 tok/s (2.5x higher)
```

**When offloading makes sense**:
- Batch size increase > latency penalty
- Offline workloads (batch prediction)
- Not suitable for real-time APIs (<1s latency requirement)

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
# vLLM engine stats
stats = engine.get_stats()

print(f"KV cache blocks used: {stats['num_blocks_used']}")
print(f"KV cache blocks total: {stats['num_blocks_total']}")
print(f"KV cache utilization: {stats['num_blocks_used'] / stats['num_blocks_total'] * 100:.1f}%")
print(f"Prefix cache hit rate: {stats.get('prefix_cache_hit_rate', 0) * 100:.1f}%")
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
- DeepSpeed Inference: https://www.deepspeed.ai/tutorials/inference-tutorial/
- NVIDIA Attention Optimizations: https://docs.nvidia.com/deeplearning/performance/
