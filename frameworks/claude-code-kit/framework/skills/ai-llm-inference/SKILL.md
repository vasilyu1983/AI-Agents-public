---
name: ai-llm-inference
description: >
  Operational patterns for LLM inference (recent advances): vLLM with 24x throughput gains,
  FP8/FP4 quantization (30-50% cost reduction), FlashInfer kernels, advanced fusions,
  PagedAttention, continuous batching, model compression, speculative decoding, and
  GPU/CPU scheduling. Emphasizes production-ready performance and cost optimization.
---

# LLMOps – Inference & Optimization – Production Skill Hub

**Modern Best Practices**: vLLM optimizations (24x throughput), FP8/FP4 quantization (30-50% cost reduction), FlashInfer integration, PagedAttention, continuous batching, and production serving patterns.

This skill provides **production-ready operational patterns** for optimizing LLM inference performance, cost, and reliability. It centralizes **decision rules**, **optimization strategies**, **configuration templates**, and **operational checklists** for inference workloads.

No theory. No narrative. Only what Claude can execute.

---

## When to Use This Skill

Claude should activate this skill whenever the user asks for:

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

- **Prompting, tuning, datasets** → [ai-llm](../ai-llm/SKILL.md)
- **RAG pipeline construction** → [ai-rag](../ai-rag/SKILL.md)
- **Deployment, APIs, monitoring** → [ai-mlops](../ai-mlops/SKILL.md)
- **Safety, governance** → [ai-mlops](../ai-mlops/SKILL.md)

---

## Quick Reference

| Task | Tool/Framework | Command/Pattern | When to Use |
|------|----------------|-----------------|-------------|
| Max throughput | vLLM | Continuous batching + PagedAttention | API serving, 24x throughput gain |
| Cost optimization | FP8/FP4 quantization | LLM Compressor, TensorRT Model Optimizer | 30-50% cost reduction, 99% accuracy |
| GPU inference | TensorRT-LLM | Custom kernels, FlashInfer | Kernel-level optimization needed |
| CPU inference | llama.cpp, GGUF | Q4_K_M, Q8_0 formats | Edge devices, no GPU available |
| Multi-GPU | vLLM, DeepSpeed | Tensor parallelism, pipeline parallelism | Large models, distributed serving |
| Latency optimization | Speculative decoding | Draft model + target model | 2-5x speedup with quality |
| Long context | PagedAttention + FlashAttention-2 | KV cache optimization | >8k token contexts |
| Memory optimization | KV cache quantization | FP8 KV cache | Fit larger batches/longer contexts |

---

## Decision Tree: Inference Optimization Strategy

```text
Need to optimize LLM inference: [Optimization Path]
    ├─ Primary constraint: Throughput?
    │   ├─ GPU available? → vLLM (24x gain, continuous batching)
    │   └─ CPU only? → llama.cpp + GGUF (Q4_K_M format)
    │
    ├─ Primary constraint: Cost?
    │   ├─ GPU serving? → FP8/FP4 quantization (30-50% reduction)
    │   └─ Needs quality? → FP8 + calibration (99% accuracy retention)
    │
    ├─ Primary constraint: Latency?
    │   ├─ Can use draft model? → Speculative decoding (2-5x speedup)
    │   └─ Long context? → FlashAttention-2 + PagedAttention
    │
    ├─ Large model (>70B)?
    │   ├─ Multiple GPUs? → Tensor parallelism (NVLink required)
    │   └─ Deep model? → Pipeline parallelism (minimize bubbles)
    │
    └─ Edge deployment?
        └─ CPU + quantization (GGUF Q4_K_M) → Optimized for constrained resources
```

---

## Modern Best Practices (Current Standards)

### vLLM Optimizations

- **24x higher throughput** vs HuggingFace Transformers
- Continuous batching with PagedAttention
- FlashInfer library integration (NVIDIA collaboration)
- FP8 attention kernels and FP4 GEMMs
- Advanced kernel fusions (AllReduce + RMSNorm + quantization)

### Quantization Performance

- **FP8/FP4**: 30-50% cost reduction, ~99% accuracy retention
- **FP4 on large models**: 40-50% performance boost (Qwen3-32B)
- **GPTQ optimization**: 2-3x faster throughput vs default vLLM config
- **BF16 → FP8/INT8**: ~30% improvement in cost-per-token

### Key Tools

- **LLM Compressor** (vLLM project) - optimized model serving
- **NVIDIA TensorRT Model Optimizer** - PTQ framework with HuggingFace export
- **vLLM + NVIDIA collaboration** - FlashInfer kernels, FP8/FP4 support

---

## Resources (Detailed Operational Guides)

For comprehensive guides on specific topics, see:

### Infrastructure & Serving

- [Infrastructure Tuning](resources/infrastructure-tuning.md) - OS, container, Kubernetes optimization for GPU workloads
- [Serving Architectures](resources/serving-architectures.md) - Production serving stack patterns
- [Resilience & HA Patterns](resources/resilience-ha-patterns.md) - Multi-region, failover, traffic management

### Performance Optimization

- [Quantization Patterns](resources/quantization-patterns.md) - FP8/FP4/INT8/INT4 decision trees and validation
- [KV Cache Optimization](resources/kv-cache-optimization.md) - PagedAttention, FlashAttention, prefix caching
- [Parallelism Patterns](resources/parallelism-patterns.md) - Tensor/pipeline/expert parallelism strategies
- [Optimization Strategies](resources/optimization-strategies.md) - Throughput, cost, memory optimization
- [Batching & Scheduling](resources/batching-and-scheduling.md) - Continuous batching and throughput patterns

### Deployment & Operations

- [Edge & CPU Optimization](resources/edge-cpu-optimization.md) - llama.cpp, GGUF, mobile/browser deployment
- [GPU Optimization Checklists](resources/gpu-optimization-checklists.md) - Hardware-specific tuning
- [Speculative Decoding Guide](resources/speculative-decoding-guide.md) - Advanced generation acceleration
- [Profiling & Capacity Planning](resources/profiling-and-capacity-planning.md) - Benchmarking, SLOs, replica sizing

---

## Templates

### Inference Configs

Production-ready configuration templates for leading inference engines:

- [vLLM Configuration](templates/inference/template-vllm-config.md) - Continuous batching, PagedAttention setup
- [TensorRT-LLM Configuration](templates/inference/template-tensorrtllm-config.md) - NVIDIA kernel optimizations
- [DeepSpeed Inference](templates/inference/template-deepspeed-inference.md) - PyTorch-friendly inference

### Quantization & Compression

Model compression templates for reducing memory and cost:

- [GPTQ Quantization](templates/quantization/template-gptq.md) - GPU post-training quantization
- [AWQ Quantization](templates/quantization/template-awq.md) - Activation-aware weight quantization
- [GGUF Format](templates/quantization/template-gguf.md) - CPU/edge optimized formats

### Serving Pipelines

High-throughput serving architectures:

- [LLM API Server](templates/serving/template-llm-api.md) - FastAPI + vLLM production setup
- [High-Throughput Setup](templates/serving/template-high-throughput-setup.md) - Multi-replica scaling patterns

### Caching & Batching

Performance optimization templates:

- [Prefix Caching](templates/caching/template-prefix-caching.md) - KV cache reuse strategies
- [Batching Configuration](templates/batching/template-batching-config.md) - Continuous batching tuning

### Benchmarking

Performance measurement and validation:

- [Latency & Throughput Testing](templates/benchmarking/template-latency-throughput-test.md) - Load testing framework

## Navigation

**Resources**
- [resources/serving-architectures.md](resources/serving-architectures.md)
- [resources/profiling-and-capacity-planning.md](resources/profiling-and-capacity-planning.md)
- [resources/gpu-optimization-checklists.md](resources/gpu-optimization-checklists.md)
- [resources/speculative-decoding-guide.md](resources/speculative-decoding-guide.md)
- [resources/resilience-ha-patterns.md](resources/resilience-ha-patterns.md)
- [resources/optimization-strategies.md](resources/optimization-strategies.md)
- [resources/kv-cache-optimization.md](resources/kv-cache-optimization.md)
- [resources/batching-and-scheduling.md](resources/batching-and-scheduling.md)
- [resources/quantization-patterns.md](resources/quantization-patterns.md)
- [resources/parallelism-patterns.md](resources/parallelism-patterns.md)
- [resources/edge-cpu-optimization.md](resources/edge-cpu-optimization.md)
- [resources/infrastructure-tuning.md](resources/infrastructure-tuning.md)

**Templates**
- [templates/serving/template-llm-api.md](templates/serving/template-llm-api.md)
- [templates/serving/template-high-throughput-setup.md](templates/serving/template-high-throughput-setup.md)
- [templates/inference/template-vllm-config.md](templates/inference/template-vllm-config.md)
- [templates/inference/template-tensorrtllm-config.md](templates/inference/template-tensorrtllm-config.md)
- [templates/inference/template-deepspeed-inference.md](templates/inference/template-deepspeed-inference.md)
- [templates/quantization/template-awq.md](templates/quantization/template-awq.md)
- [templates/quantization/template-gptq.md](templates/quantization/template-gptq.md)
- [templates/quantization/template-gguf.md](templates/quantization/template-gguf.md)
- [templates/batching/template-batching-config.md](templates/batching/template-batching-config.md)
- [templates/caching/template-prefix-caching.md](templates/caching/template-prefix-caching.md)
- [templates/benchmarking/template-latency-throughput-test.md](templates/benchmarking/template-latency-throughput-test.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## Related Skills

This skill focuses on **inference-time performance**. For related workflows:

- **[ai-llm](../ai-llm/SKILL.md)** - Prompting, fine-tuning, datasets
- **[ai-llm](../ai-llm/SKILL.md)** - LLM application architecture, RAG pipelines
- **[ai-rag](../ai-rag/SKILL.md)** - RAG pipeline construction and optimization
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment, APIs, monitoring
- **[ai-mlops](../ai-mlops/SKILL.md)** - Safety, governance, security
- **[qa-observability](../qa-observability/SKILL.md)** - Performance monitoring and optimization
- **[ops-devops-platform](../ops-devops-platform/SKILL.md)** - Infrastructure and platform operations

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
