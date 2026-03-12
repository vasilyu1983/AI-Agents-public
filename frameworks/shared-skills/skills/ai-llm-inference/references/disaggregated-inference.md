# Disaggregated Inference (Prefill/Decode Separation)

Production architecture for separating prefill and decode phases onto specialized compute pools. Now the dominant pattern in high-throughput LLM serving (2025+).

---

## Why Disaggregation

LLM inference has two fundamentally different phases:

| Phase | GPU Utilization | Ops/Byte | Bottleneck |
|-------|-----------------|----------|------------|
| **Prefill** | 90-95% | 200-400 | Compute-bound |
| **Decode** | 20-40% | 60-80 | Memory bandwidth-bound |

**Problem**: Colocating both phases causes interference:
- Prefill jobs starve decode latency
- Decode jobs leave compute underutilized during prefill
- P99 latency explodes under load

**Solution**: Separate prefill and decode onto dedicated GPU pools, scale independently.

---

## Architecture Patterns

### Basic P/D Separation

```text
┌─────────────────┐     KV Cache      ┌─────────────────┐
│  Prefill Pool   │ ───────────────→  │  Decode Pool    │
│  (Compute-opt)  │    Transfer       │  (Memory-opt)   │
└─────────────────┘                   └─────────────────┘
        ↑                                     │
        │         ┌─────────────┐             │
        └─────────│   Router    │←────────────┘
                  └─────────────┘
                        ↑
                   User Requests
```

### Production Implementation (vLLM)

vLLM implements disaggregation with two instances connected via KV cache connector:

```python
# Prefill instance
vllm serve model --prefill-only \
    --kv-connector redis://kv-store:6379

# Decode instance
vllm serve model --decode-only \
    --kv-connector redis://kv-store:6379
```

### NVIDIA Dynamo (GTC 2025)

Data center scale disaggregation framework supporting vLLM, SGLang, TensorRT-LLM:

```yaml
# dynamo-config.yaml
prefill:
  replicas: 3
  gpu_type: h100
  optimization: compute
decode:
  replicas: 9
  gpu_type: h100
  optimization: memory_bandwidth
kv_transfer:
  protocol: rdma
  compression: none
```

---

## Decision Tree: When to Disaggregate

```text
Should you disaggregate prefill/decode?
│
├─ Throughput > 10k tokens/sec required?
│   └─ YES → Disaggregate
│
├─ P99 latency variance > 3x P50?
│   └─ YES → Disaggregate (queuing interference)
│
├─ Mixed workloads (short + long prompts)?
│   └─ YES → Disaggregate
│
├─ Single-user or batch-only workload?
│   └─ NO → Colocated may be simpler
│
├─ GPU count < 4?
│   └─ NO → Colocated (overhead not worth it)
│
└─ Fast interconnect available (NVLink, RDMA)?
    └─ NO → Colocated (KV transfer bottleneck)
```

---

## Performance Benchmarks (2025)

### SGLang on H100 (96 GPUs)

Configuration: 3 nodes (24 GPUs) prefill + 9 nodes (72 GPUs) decode

| Metric | Value |
|--------|-------|
| Input TPS | 52,300 tokens/sec |
| Output TPS | 22,300 tokens/sec per node |
| Latency variance | 20x reduction vs colocated |

### SGLang on GB200 NVL72 (September 2025)

| Metric | vs H100 |
|--------|---------|
| Prefill throughput | 3.8x faster |
| Decode throughput | 4.8x faster |

### vLLM with llm-d 0.3 (October 2025)

| Configuration | Tokens/sec per H200 |
|---------------|---------------------|
| 32-way Expert Parallelism | 2,200 |
| 96-way Expert Parallelism | 2,000 |

---

## KV Cache Transfer Strategies

### Transfer Protocols

| Protocol | Latency | Throughput | When to Use |
|----------|---------|------------|-------------|
| **RDMA** | <1ms | 400 GB/s | Multi-node, NVLink available |
| **TCP** | 2-5ms | 25 GB/s | Cross-rack, no RDMA |
| **Shared Memory** | <0.1ms | 900 GB/s | Same-node separation |

### Perplexity Implementation Pattern

```text
┌──────────────┐
│ KV Messenger │ ← Orchestrates transfers
└──────┬───────┘
       │
  ┌────┴────┐
  ↓         ↓
Prefiller  Decoder
  │           │
  └───────────┘
    Transfer blocks
    until complete
```

Key: Decoder blocks scheduling until KV transfer completes.

---

## When NOT to Disaggregate

**Avoid disaggregation when:**

1. **Small workloads**: <4 GPUs, overhead exceeds benefit
2. **Batch-only inference**: No latency sensitivity
3. **Slow interconnect**: KV transfer becomes bottleneck
4. **Simple deployment**: Operational complexity not justified

**Performance degradation risk**: 20-30% if misconfigured (overhead exceeds gains).

---

## Configuration Templates

### vLLM Disaggregated Setup

```bash
# Start KV store
redis-server --port 6379

# Prefill worker (compute-optimized)
CUDA_VISIBLE_DEVICES=0,1 vllm serve meta-llama/Llama-3-70B \
    --prefill-only \
    --tensor-parallel-size 2 \
    --max-num-seqs 256 \
    --kv-connector redis://localhost:6379

# Decode worker (memory-optimized)
CUDA_VISIBLE_DEVICES=2,3,4,5 vllm serve meta-llama/Llama-3-70B \
    --decode-only \
    --tensor-parallel-size 4 \
    --max-num-seqs 64 \
    --kv-connector redis://localhost:6379
```

### SGLang Disaggregated Setup

```bash
# Prefill cluster
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-70B \
    --tp 8 --dp 3 \
    --disagg-mode prefill \
    --kv-transfer-config kv_config.json

# Decode cluster
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-70B \
    --tp 8 --dp 9 \
    --disagg-mode decode \
    --kv-transfer-config kv_config.json
```

---

## Monitoring Disaggregated Systems

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| KV transfer latency | <2ms | >10ms |
| Prefill queue depth | <100 | >500 |
| Decode queue depth | <50 | >200 |
| KV cache hit rate | >80% | <50% |
| Transfer bandwidth | >100 GB/s | <50 GB/s |

### Prometheus Queries

```promql
# KV transfer latency P99
histogram_quantile(0.99,
  rate(kv_transfer_latency_seconds_bucket[5m]))

# Prefill/decode throughput ratio
rate(prefill_tokens_total[5m]) / rate(decode_tokens_total[5m])

# Queue depth imbalance
prefill_queue_depth / decode_queue_depth
```

---

## Framework Support Matrix

| Framework | P/D Disaggregation | KV Transfer | Production Ready |
|-----------|-------------------|-------------|------------------|
| **vLLM** | Yes (0.6+) | Redis, NCCL | Yes |
| **SGLang** | Yes | Custom, RDMA | Yes |
| **TensorRT-LLM** | Yes | Triton, NCCL | Yes |
| **NVIDIA Dynamo** | Native | RDMA, NVLink | Yes (GTC 2025) |
| **Ray Serve LLM** | Yes | Ray Object Store | Yes |
| **LMCache** | Partial | Custom | Beta |

---

## References

- [DistServe: Disaggregating Prefill and Decoding (OSDI 2024)](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf)
- [Hao AI Lab: Disaggregated Inference 18 Months Later](https://hao-ai-lab.github.io/blogs/distserve-retro/)
- [vLLM Disaggregated Prefilling Docs](https://docs.vllm.ai/en/latest/features/disagg_prefill/)
- [Ray Serve Prefill/Decode Disaggregation](https://docs.ray.io/en/latest/serve/llm/user-guides/prefill-decode.html)
- [Perplexity: Disaggregated Prefill and Decode](https://www.perplexity.ai/hub/blog/disaggregated-prefill-and-decode)
