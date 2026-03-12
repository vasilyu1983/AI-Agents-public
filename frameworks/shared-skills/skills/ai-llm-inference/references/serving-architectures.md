# Serving Architectures for High-Performance LLM Inference

A library of operational architectures for deploying and scaling LLM inference services.

**Updated January 2026**: Added NVIDIA Dynamo (GTC 2025), SGLang, and disaggregated inference patterns.

---

## 1. Core Serving Stacks

### Framework Selection Guide (2026)

| Framework | Best For | Setup Complexity | Throughput | Latency |
|-----------|----------|------------------|------------|---------|
| **vLLM** | High-concurrency production | 1-2 days | Excellent | Good |
| **SGLang** | Chatbots, agents, RAG | Easy | Excellent | Best |
| **TensorRT-LLM** | Max NVIDIA performance | 1-2 weeks | Best | Best |
| **NVIDIA Dynamo** | Data center scale | Expert | Best | Best |
| **llama.cpp** | CPU/edge/mobile | Easy | Good | Good |

### A. vLLM (Production Default)

- Continuous batching
- PagedAttention
- Fast parallel token generation
- **Disaggregated prefill/decode support (0.6+)**
- **FlashInfer integration**

Use for:

- High-throughput APIs
- Multi-user environments
- RAG workloads
- High-concurrency (10-100+ users)

```bash
vllm serve meta-llama/Llama-3-70B \
    --tensor-parallel-size 4 \
    --enable-prefix-caching \
    --kv-cache-dtype fp8
```

---

### B. SGLang (Fastest for Chat/Agents)

- **RadixAttention** for KV cache reuse
- 6.4x throughput vs baseline on structured workloads
- 3.7x lower latency than vLLM on chat
- Native disaggregated inference support

Use for:

- Chatbots (conversation history caching)
- AI agents with tool use
- RAG with repeated few-shot examples
- Structured generation

```bash
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3-70B \
    --tp 8 \
    --enable-radix-attention
```

---

### C. TensorRT-LLM

- Kernel-level GPU optimization
- FP8/INT8/NVFP4 support
- Multi-GPU tensor parallelism
- **Best on Blackwell (B200, GB200)**

Use for:

- Maximum NVIDIA performance
- Latency-critical use cases
- When setup time is acceptable (1-2 weeks)

---

### D. NVIDIA Dynamo (Data Center Scale - GTC 2025)

**NEW**: NVIDIA's production-grade disaggregated inference framework.

- Native prefill/decode separation
- Supports vLLM, SGLang, TensorRT-LLM backends
- RDMA/NVLink KV cache transfer
- Data center scale orchestration

Use for:

- Large-scale production (100+ GPUs)
- Multi-node disaggregated inference
- Enterprise deployments

```yaml
# dynamo-config.yaml
prefill:
  replicas: 24  # 3 nodes × 8 GPUs
  backend: tensorrt-llm
  optimization: compute
decode:
  replicas: 72  # 9 nodes × 8 GPUs
  backend: tensorrt-llm
  optimization: memory_bandwidth
kv_transfer:
  protocol: rdma
  compression: none
```

---

### E. GGML / llama.cpp / GGUF

- CPU/edge inference
- Highly optimized C++ kernels
- Metal support for Apple Silicon

Use for:

- On-prem, mobile, browser, low-cost infra  

---

## 2. Architectural Patterns

### Pattern 1: Disaggregated Inference (P/D Separation)

**2025+ Standard** - Separate prefill and decode onto specialized GPU pools.

```text
┌─────────────────┐     KV Cache      ┌─────────────────┐
│  Prefill Pool   │ ───────────────→  │  Decode Pool    │
│  (Compute-opt)  │    Transfer       │  (Memory-opt)   │
└─────────────────┘                   └─────────────────┘
```

Use for:

- Throughput > 10k tokens/sec
- P99 latency variance > 3x P50
- Mixed workloads (short + long prompts)

See [disaggregated-inference.md](disaggregated-inference.md) for full guide.

**Checklist**

- [ ] Fast interconnect available (NVLink, RDMA)
- [ ] GPU count >= 4
- [ ] KV transfer latency < 10ms
- [ ] Prefill/decode ratio tuned for workload

---

### Pattern 2: API Replica Pool

- Multiple model replicas
- Fronted by load balancer
- Stateless API servers

**Checklist**

- [ ] Autoscaling rules defined
- [ ] GPU warmup applied

---

### Pattern 3: Hybrid GPU/CPU Offloading

Ideal for extremely long context windows.

- Cache KV on GPU
- Offload layers or cache segments to CPU
- Use DeepSpeed inference

---

### Pattern 4: Multi-Model Gateway

- One gateway
- Many models loaded lazily
- Route by model ID

Use for:

- Model hubs
- Multi-tenant systems  

---

## 3. High-Availability Requirements

- Health checks (liveness/readiness)  
- Restart-on-failure policy  
- Rolling deployments  
- Graceful shutdown (finish decode)  

---

## 4. Serving Architecture Checklist

- [ ] Chosen stack supports required context size  
- [ ] Streaming enabled if needed  
- [ ] Batching enabled  
- [ ] GPU memory footprint validated  
- [ ] Latency at P95 within SLO  
