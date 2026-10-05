# Serving Architectures for Modern LLM Inference

Runtime selection guide. Separate three decisions that often get conflated:

1. token engine
2. request placement and routing
3. topology for prefill, encoder, decode, and adapters

Use current official docs before committing to a runtime-specific feature.

## Table of Contents

- [Engine Selection](#engine-selection)
- [Control Plane Selection](#control-plane-selection)
- [Architecture Patterns](#architecture-patterns)
- [1. Colocated Replica Pool](#1-colocated-replica-pool)
- [2. Router Plus Replica Pool](#2-router-plus-replica-pool)
- [3. Prefill and Decode Separation](#3-prefill-and-decode-separation)
- [4. Encoder and Decode Separation](#4-encoder-and-decode-separation)
- [5. Multi-LoRA Gateway](#5-multi-lora-gateway)
- [6. llama.cpp Server for Multi-User GGUF Serving](#6-llamacpp-server-for-multi-user-gguf-serving)
- [Operational Checklist](#operational-checklist)
- [What To Avoid](#what-to-avoid)
- [Primary Sources](#primary-sources)

## Engine Selection

| Runtime | Strong Fit | Watchouts |
|---|---|---|
| **vLLM** | general text serving, OpenAI-compatible APIs, structured outputs, LoRA, broad quantization support | some advanced disaggregation features are still evolving or experimental |
| **SGLang** | chat, agents, repeated prefixes, multimodal serving, HiCache, PD or EPD disaggregation, multi-LoRA | feature surface is broad; verify the exact server mode and model support |
| **TensorRT-LLM** | NVIDIA-only low-latency serving, explicit precision control, KV cache reuse, tightly tuned GPU stacks | higher setup and integration cost, especially outside NVIDIA-centric environments |
| **llama.cpp** | CPU, edge, desktop, Apple Silicon, GGUF-based packaging | weaker fit for large multi-tenant clusters and advanced server-side routing |

## Control Plane Selection

Do not assume the runtime also solves cluster-level request placement.

| Need | Recommended Direction |
|---|---|
| single host or a few replicas | keep routing simple and colocated |
| many replicas with prefix reuse | add cache-aware or sticky routing |
| adapter-heavy multi-tenant serving | route by adapter locality and cold-load cost |
| Kubernetes-scale fleet | use a dedicated control plane or router layer |

For detailed guidance see [routing-and-control-planes.md](routing-and-control-planes.md).

## Architecture Patterns

### 1. Colocated Replica Pool

Best default when you are still establishing a baseline.

```text
client -> gateway -> model replicas
```

Use when:

- one modality
- no adapter churn
- queueing is acceptable
- a simple autoscaler can hold the SLO

### 2. Router Plus Replica Pool

Use when locality affects cost or latency.

```text
client -> router -> selected replica
```

Route on:

- model ID
- prompt prefix reuse
- active LoRA adapter
- modality
- current queue depth

### 3. Prefill and Decode Separation

Use only when colocated serving shows real interference between long prefills and ongoing decode.

```text
client -> router -> prefill pool -> decode pool
```

This is not an automatic throughput win. Measure queueing, transfer cost, and operational overhead first.

### 4. Encoder and Decode Separation

Use for VLM or multimodal serving when the encoder path scales differently from token generation.

```text
client -> router -> encoder pool -> decode pool
```

Prefer this over generic prefill or decode splitting when vision or audio encoders are the real bottleneck.

### 5. Multi-LoRA Gateway

Use when many tenants share a base model but switch adapters frequently.

```text
client -> router -> base model replicas + adapter cache
```

Critical controls:

- cap loaded adapters per replica
- route by adapter locality
- observe cold-load latency separately from TTFT

### 6. llama.cpp Server for Multi-User GGUF Serving

Use when a GGUF model serves several users from CPU or small-GPU nodes. Single-box, desktop, and edge tuning (threads, SIMD, BLAS, quant choice, device builds) belongs to [ai-local-model-ops edge-cpu-optimization.md](../../ai-local-model-ops/references/edge-cpu-optimization.md).

```text
client -> router -> llama.cpp server replicas (one model load per process)
```

Critical controls:

- serve through llama.cpp's own HTTP server (OpenAI-compatible) with parallel slots and continuous batching, rather than calling the Python binding per request; check the current server docs for the slot, context, and batching flags
- load the model once per process; in serverless, load it at init outside the handler. Model load dominates cold start, so serverless CPU fits only low-QPS, latency-tolerant traffic
- size memory from GGUF file size + KV cache for (context × concurrent slots) + runtime overhead; set memory and CPU requests equal to limits, and threads to the physical cores allotted
- build the image from a pinned llama.cpp release tag, not a moving clone of the default branch; take SIMD/BLAS build options from the current build docs, because the build system and flag names change across releases
- scale out with replicas behind a router: one CPU server's decode rate is bounded by memory bandwidth, so more threads stop helping long before more replicas do

## Operational Checklist

- [ ] Engine selection matches task shape, not generic popularity
- [ ] Routing policy is explicit once more than one replica matters
- [ ] Structured outputs are validated if they are part of the SLA
- [ ] Adapter locality is handled if LoRAs are involved
- [ ] Encoder saturation is measured separately on multimodal workloads
- [ ] Colocated baseline exists before disaggregation is proposed
- [ ] Precision and kernel choices are tied to the actual runtime

## What To Avoid

- Avoid choosing an engine from old benchmark leaderboards alone.
- Avoid using round-robin once prefix reuse or adapter reuse dominates cost.
- Avoid introducing PD or EPD topology without transfer metrics and rollback criteria.
- Avoid assuming "best on Blackwell" or "best on H100" without matching software support and workload.

## Primary Sources

- vLLM docs: https://docs.vllm.ai/
- SGLang docs: https://docs.sglang.io/
- TensorRT-LLM docs: https://nvidia.github.io/TensorRT-LLM/
- llama.cpp: https://github.com/ggml-org/llama.cpp
- vLLM Production Stack: https://docs.vllm.ai/projects/production-stack/
- llm-d: https://github.com/llm-d/llm-d
