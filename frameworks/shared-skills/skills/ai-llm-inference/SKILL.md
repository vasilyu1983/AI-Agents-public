---
name: ai-llm-inference
description: "Operational patterns for LLM inference: latency budgeting, tail-latency control, caching, batching/scheduling, quantization/compression, parallelism, and reliable serving at scale. Emphasizes production-grade performance, cost control, and observability."
---

# LLMOps - Inference & Optimization - Production Skill Hub

**Modern Best Practices (January 2026)**:

- Treat inference as a **systems problem**: SLOs, tail latency, retries, overload, and cache strategy.
- Use **continuous batching / smart scheduling** when serving many concurrent requests (Orca scheduling: https://www.usenix.org/conference/osdi22/presentation/yu).
- Use **KV-cache aware serving** (PagedAttention/vLLM: https://arxiv.org/abs/2309.06180) and **efficient attention kernels** (FlashAttention: https://arxiv.org/abs/2205.14135).
- Use **speculative decoding** when latency is critical and draft-model quality is acceptable (speculative decoding: https://arxiv.org/abs/2302.01318).
- Quantize only with **measured** quality impact and rollback plan (quantization must be validated on your eval set).

This skill provides **production-ready operational patterns** for optimizing LLM inference performance, cost, and reliability. It centralizes **decision rules**, **optimization strategies**, **configuration templates**, and **operational checklists** for inference workloads.

No theory. No narrative. Only what Codex can execute.

---

## When to Use This Skill

Codex should activate this skill whenever the user asks for:

- Optimizing LLM inference latency or throughput
- Choosing quantization strategies (FP8/FP4/INT8/INT4)
- Configuring vLLM, TensorRT-LLM, or DeepSpeed inference
- Scaling LLM inference across GPUs (tensor/pipeline parallelism)
- Building high-throughput LLM APIs
- Improving context window performance (KV cache optimization)
- Using speculative decoding for faster generation
- Reducing cost per token
- Profiling and benchmarking inference workloads
- Planning infrastructure capacity
- CPU/edge deployment patterns
- High availability and resilience patterns

## Scope Boundaries (Use These Skills for Depth)

- **Prompting, tuning, datasets** -> [ai-llm](../ai-llm/SKILL.md)
- **RAG pipeline construction** -> [ai-rag](../ai-rag/SKILL.md)
- **Deployment, APIs, monitoring** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Safety, governance** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Performance monitoring** -> [qa-observability](../qa-observability/SKILL.md)
- **Infrastructure operations** -> [ops-devops-platform](../ops-devops-platform/SKILL.md)

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Latency budget | SLO + load model | TTFT/ITL + P95/P99 under load | Any production endpoint |
| Tail-latency control | Scheduling + timeouts | Admission control + queue caps + backpressure | Prevent p99 explosions |
| Throughput | Batching + KV-cache aware serving | Continuous batching + KV paging | High concurrency serving |
| Cost control | Model tiering + caching | Cache (prefix/response) + quotas | Reduce spend and overload risk |
| Long context | Prefill optimization | Chunked prefill + prompt compression | Long inputs and RAG-heavy apps |
| Parallelism | TP/PP/DP | Choose by model size and interconnect | Models that do not fit one device |
| Reliability | Resilience patterns | Timeouts + circuit breakers + idempotency | Avoid cascading failures |

---

## Decision Tree: Inference Optimization Strategy

```text
Need to optimize LLM inference: [Optimization Path]
    │
    ├─ High throughput (>10k tok/s) OR P99 variance > 3x P50?
    │   └─ YES -> Disaggregated inference (prefill/decode separation)
    │            See references/disaggregated-inference.md
    │
    ├─ Primary constraint: Throughput?
    │   ├─ Many concurrent users? -> batching + KV-cache aware serving + admission control
    │   ├─ Chat/agents with KV reuse? -> SGLang (RadixAttention)
    │   └─ Mostly batch/offline? -> batch inference jobs + large batches + spot capacity
    │
    ├─ Primary constraint: Cost?
    │   ├─ Can accept lower quality tier? -> model tiering (small/medium/large router)
    │   └─ Must keep quality? -> caching + prompt/context reduction before quantization
    │
    ├─ Primary constraint: Latency?
    │   ├─ Draft model acceptable? -> speculative decoding
    │   └─ Long context? -> prefill optimizations + FlashAttention-3 + context budgets
    │
    ├─ Large model (>70B)?
    │   ├─ Multiple GPUs? -> Tensor parallelism (NVLink required)
    │   └─ Deep model? -> Pipeline parallelism (minimize bubbles)
    │
    ├─ Hardware selection?
    │   ├─ Memory-bound? -> more HBM, higher bandwidth
    │   ├─ Latency-bound? -> faster clocks + kernel support
    │   └─ Multi-node? -> prioritize interconnect (NVLink/RDMA) and topology
    │
    │   Notes: treat GPU/SKU advice as time-sensitive; verify with vendor docs and your own benchmarks.
    │   See references/gpu-optimization-checklists.md and references/infrastructure-tuning.md
    │
    └─ Edge deployment?
        └─ CPU + quantization -> llama.cpp/GGUF for constrained resources
```

---

## Intake Checklist (REQUIRED)

Before recommending changes, collect (or infer) these inputs:

- Model + variant (size, context length, precision/quantization, tokenizer)
- Traffic shape (prompt/output length distributions, concurrency, QPS, streaming vs non-streaming)
- SLOs and budgets (TTFT/ITL/total latency targets, error budget, cost per request)
- Serving stack (engine/version, batching/scheduling settings, caching, parallelism, autoscaling)
- Hardware and topology (GPU type/count, VRAM, NVLink/RDMA, CPU/RAM, storage, cluster/runtime)
- Constraints (quality floor, safety requirements, rollout/rollback constraints)

## Core Concepts & Practices

### Core Concepts (Vendor-Agnostic)

- **Latency components**: queueing + prefill + decode; optimize the largest contributor first.
- **Tail latency**: p99 is dominated by queuing and long prompts; fix with admission control and context budgets.
- **Retries**: retries can multiply load; bound retries and use hedged requests only with strict budgets.
- **Caching**: prefix caching helps repeated system/tool scaffolds; response caching helps repeated questions (requires invalidation).
- **Security & privacy**: prompts/outputs can contain sensitive data; scrub logs, enforce auth/tenancy, and rate-limit abuse (OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/).

### Implementation Practices (Tooling Examples)

- **Measure under load**: benchmark TTFT/ITL and p95/p99 with realistic concurrency and prompt lengths.
- **Separate environments**: dev/stage/prod model configs; promote only after passing the inference review checklist.
- **Export telemetry**: request-level tokens, TTFT/ITL, queue depth, GPU memory headroom, and error classes (OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/).

### Do / Avoid

**Do**
- Do enforce `max_input_tokens` and `max_output_tokens` at the API boundary.
- Do cap concurrency and queue depth; return overload errors quickly.
- Do validate quality after any quantization or kernel change.

**Avoid**
- Avoid unbounded retries (amplifies outages).
- Avoid unbounded context windows (OOM + latency spikes).
- Avoid benchmarking on single requests; always test with realistic concurrency.

---

## Accuracy Protocol (REQUIRED)

- Treat performance ratios (for example, "2x faster") as hypotheses unless a source is cited and the workload is comparable.
- Do not recommend hardware/SKU changes without stating assumptions (model size, context length, concurrency, interconnect).
- Prefer a measured baseline + checklist-driven rollout over "best practice" claims.

---

## Resources (Detailed Operational Guides)

For comprehensive guides on specific topics, see:

### Infrastructure & Serving

- [Disaggregated Inference](references/disaggregated-inference.md) - Prefill/decode separation (2025+ standard)
- [Infrastructure Tuning](references/infrastructure-tuning.md) - OS, container, Kubernetes optimization for GPU workloads
- [Serving Architectures](references/serving-architectures.md) - Production serving stack patterns (vLLM, SGLang, TensorRT-LLM, NVIDIA Dynamo)
- [Resilience & HA Patterns](references/resilience-ha-patterns.md) - Multi-region, failover, traffic management

### Performance Optimization

- [Quantization Patterns](references/quantization-patterns.md) - FP8/FP4/INT8/INT4 decision trees (FP8 first, INT8 not on Blackwell)
- [KV Cache Optimization](references/kv-cache-optimization.md) - PagedAttention, FlashAttention-3, FlashInfer, RadixAttention
- [Parallelism Patterns](references/parallelism-patterns.md) - Tensor/pipeline/expert parallelism strategies
- [Optimization Strategies](references/optimization-strategies.md) - Throughput, cost, memory optimization
- [Batching & Scheduling](references/batching-and-scheduling.md) - Continuous batching and throughput patterns

### Deployment & Operations

- [Edge & CPU Optimization](references/edge-cpu-optimization.md) - llama.cpp, GGUF, mobile/browser deployment
- [GPU Optimization Checklists](references/gpu-optimization-checklists.md) - Hardware-specific tuning
- [Speculative Decoding Guide](references/speculative-decoding-guide.md) - Advanced generation acceleration
- [Profiling & Capacity Planning](references/profiling-and-capacity-planning.md) - Benchmarking, SLOs, replica sizing

---

## Templates

### Inference Configs

Production-ready configuration templates for leading inference engines:

- [vLLM Configuration](assets/inference/template-vllm-config.md) - Continuous batching, PagedAttention setup
- [TensorRT-LLM Configuration](assets/inference/template-tensorrtllm-config.md) - NVIDIA kernel optimizations
- [DeepSpeed Inference](assets/inference/template-deepspeed-inference.md) - PyTorch-friendly inference

### Quantization & Compression

Model compression templates for reducing memory and cost:

- [GPTQ Quantization](assets/quantization/template-gptq.md) - GPU post-training quantization
- [AWQ Quantization](assets/quantization/template-awq.md) - Activation-aware weight quantization
- [GGUF Format](assets/quantization/template-gguf.md) - CPU/edge optimized formats

### Serving Pipelines

High-throughput serving architectures:

- [LLM API Server](assets/serving/template-llm-api.md) - FastAPI + vLLM production setup
- [High-Throughput Setup](assets/serving/template-high-throughput-setup.md) - Multi-replica scaling patterns

### Caching & Batching

Performance optimization templates:

- [Prefix Caching](assets/caching/template-prefix-caching.md) - KV cache reuse strategies
- [Batching Configuration](assets/batching/template-batching-config.md) - Continuous batching tuning

### Benchmarking

Performance measurement and validation:

- [Latency & Throughput Testing](assets/benchmarking/template-latency-throughput-test.md) - Load testing framework

### Checklists

- [Inference Performance Review Checklist](assets/checklists/inference-review-checklist.md) - Baseline, bottlenecks, rollout readiness

## Navigation

**Resources**

- [references/disaggregated-inference.md](references/disaggregated-inference.md)
- [references/serving-architectures.md](references/serving-architectures.md)
- [references/profiling-and-capacity-planning.md](references/profiling-and-capacity-planning.md)
- [references/gpu-optimization-checklists.md](references/gpu-optimization-checklists.md)
- [references/speculative-decoding-guide.md](references/speculative-decoding-guide.md)
- [references/resilience-ha-patterns.md](references/resilience-ha-patterns.md)
- [references/optimization-strategies.md](references/optimization-strategies.md)
- [references/kv-cache-optimization.md](references/kv-cache-optimization.md)
- [references/batching-and-scheduling.md](references/batching-and-scheduling.md)
- [references/quantization-patterns.md](references/quantization-patterns.md)
- [references/parallelism-patterns.md](references/parallelism-patterns.md)
- [references/edge-cpu-optimization.md](references/edge-cpu-optimization.md)
- [references/infrastructure-tuning.md](references/infrastructure-tuning.md)

**Templates**
- [assets/serving/template-llm-api.md](assets/serving/template-llm-api.md)
- [assets/serving/template-high-throughput-setup.md](assets/serving/template-high-throughput-setup.md)
- [assets/inference/template-vllm-config.md](assets/inference/template-vllm-config.md)
- [assets/inference/template-tensorrtllm-config.md](assets/inference/template-tensorrtllm-config.md)
- [assets/inference/template-deepspeed-inference.md](assets/inference/template-deepspeed-inference.md)
- [assets/quantization/template-awq.md](assets/quantization/template-awq.md)
- [assets/quantization/template-gptq.md](assets/quantization/template-gptq.md)
- [assets/quantization/template-gguf.md](assets/quantization/template-gguf.md)
- [assets/batching/template-batching-config.md](assets/batching/template-batching-config.md)
- [assets/caching/template-prefix-caching.md](assets/caching/template-prefix-caching.md)
- [assets/benchmarking/template-latency-throughput-test.md](assets/benchmarking/template-latency-throughput-test.md)
- [assets/checklists/inference-review-checklist.md](assets/checklists/inference-review-checklist.md)

**Data**
- [data/sources.json](data/sources.json) - Curated external references

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about LLM inference, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best inference engine for [use case]?"
- "What should I use for [serving/quantization/batching]?"
- "What's the latest in LLM inference optimization?"
- "Current best practices for [vLLM/TensorRT/quantization]?"
- "Is [inference tool] still relevant in 2026?"
- "[vLLM] vs [TensorRT-LLM] vs [SGLang]?"
- "Best quantization method for [model size]?"
- "What GPU should I use for inference?"

### Required Searches

1. Search: `"LLM inference optimization best practices 2026"`
2. Search: `"[vLLM/TensorRT-LLM/SGLang] comparison 2026"`
3. Search: `"LLM quantization trends January 2026"`
4. Search: `"LLM serving new releases 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What serving engines are popular NOW (not 6 months ago)
- **Emerging trends**: New inference optimizations gaining traction
- **Deprecated/declining**: Techniques or tools losing relevance
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Inference engines (vLLM 0.7+, TensorRT-LLM, SGLang, llama.cpp)
- Quantization methods (FP8, AWQ, GPTQ, GGUF, bitsandbytes)
- Attention kernels (FlashAttention-3, FlashInfer, xFormers)
- Speculative decoding advances
- KV cache optimization techniques
- New GPU architectures (H200, Blackwell) and their optimizations

---

## Related Skills

This skill focuses on **inference-time performance**. For related workflows:

- See "Scope Boundaries" above.

---

## External Resources

See [data/sources.json](data/sources.json) for:

- Serving frameworks (vLLM, TensorRT-LLM, DeepSpeed-MII)
- Quantization libraries (GPTQ, AWQ, bitsandbytes, LLM Compressor)
- FlashAttention, FlashInfer, xFormers
- GPU hardware guides and optimization docs
- Benchmarking frameworks and tools

---

Use this skill whenever the user needs **LLM inference performance, cost reduction, or serving architecture** guidance.
