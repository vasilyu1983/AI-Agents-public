---
name: ai-llm-inference
description: "LLM inference patterns for latency, batching, caching, quantization, routing, and serving stacks. Use when optimizing throughput, tail latency, or serving cost."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# LLM Inference Production Skill Hub

Operational guidance for choosing and tuning modern inference stacks. Focus on runtime fit, routing, output guarantees, adapter loading, multimodal serving, and measured performance under load.

Use current primary sources for volatile facts such as versions, hardware support, benchmarks, pricing, and release status.

## ASCII Flow

```text
serving workload
  |
  v
intake
  model + modality + context + QPS + latency SLO + hardware + output contract
  |
  v
serving design
  engine + router + batching + cache + quantization + structured outputs
  |
  v
benchmark
  TTFT + ITL + throughput + error rate + quality floor
  |
  v
production serving path
  capacity plan + rollout + monitoring + rollback thresholds
```

## When to Use This Skill

Use this skill when the user asks for:

- inference engine selection or stack comparison
- latency, TTFT, ITL, or throughput optimization
- cache-aware routing or control-plane design
- quantization strategy by runtime and hardware
- multi-GPU or multi-node serving
- structured outputs or constrained decoding at serve time
- multimodal or encoder-decoder serving patterns
- LoRA or multi-adapter serving
- cost reduction for self-hosted or API inference
- benchmarking, profiling, or capacity planning
- CPU or edge deployment with GGUF or llama.cpp

## Scope Boundaries

- Prompting, fine-tuning, eval sets -> [ai-llm](../ai-llm/SKILL.md)
- RAG pipeline design -> [ai-rag](../ai-rag/SKILL.md)
- Deployment automation, monitoring, incident response -> [ai-mlops](../ai-mlops/SKILL.md)
- Infrastructure operations -> [ops-devops-platform](../ops-devops-platform/SKILL.md)
- Observability design -> [qa-observability](../qa-observability/SKILL.md)

## Quick Reference

| Decision | Primary Question | Default Starting Point | Escalate When |
|---|---|---|---|
| Engine | Which runtime should execute tokens? | vLLM for general text serving | Need stronger KV reuse, multimodal split, or NVIDIA-specific kernels |
| Router | How should requests be placed? | Simple replica pool first | Multiple replicas, sticky prefixes, multi-LoRA, or mixed workloads |
| Output control | Must responses obey a schema? | Use native structured outputs | JSON validity or grammar constraints are part of the SLA |
| Multimodal | Is there a separate encoder path? | Keep colocated first | Encoder saturation differs from decode saturation |
| Adapters | Will many LoRAs or tenants share the base model? | Use native multi-LoRA support | Cold-load latency or adapter churn affects p95 |
| Quantization | Which precision is safe in this runtime? | Runtime-native FP8 or weight-only path | Hardware support or model quality is uncertain |
| Disaggregation | Should prefill/encoder/decode be split? | Only after colocated baseline | Queueing interference or resource asymmetry is proven |

## Intake Checklist (Required)

Collect or infer these inputs before recommending changes:

- model family, size, context length, tokenizer, modality, and adapter usage
- request contract: streaming, tool use, reasoning mode, schema or grammar constraints
- prompt and output length distribution, concurrency, QPS, and burst profile
- prompt reuse patterns: prefix reuse, session reuse, retrieval reuse, LoRA reuse
- current engine, version, router, autoscaler, and cache settings
- hardware and topology: GPU SKU, VRAM, interconnect, node count, CPU and RAM
- SLOs: TTFT, ITL, end-to-end latency, availability, and error budget
- acceptance criteria: quality floor, JSON validity, long-context accuracy, rollback window

## Workflow

1. Collect the workload shape, runtime contract, hardware, and SLOs before recommending changes.
2. Route prompt strategy, RAG design, or platform operations to the adjacent skill when inference tuning is not the primary problem.
3. Choose the serving stack, routing policy, quantization path, and output-control strategy from the decision flow.
4. Benchmark the baseline, change one lever at a time, and compare throughput, latency, and quality against the acceptance criteria.
5. Verify volatile engine, hardware, and release facts with the navigation sources before final recommendations.

## Decision Flow

```text
Need to improve inference:
    |
    |- Is the workload text-only?
    |   |- No -> evaluate multimodal runtime support and encoder separation
    |   `- Yes -> continue
    |
    |- Is schema validity or constrained decoding part of the SLA?
    |   |- Yes -> prefer runtimes with native structured outputs
    |   `- No -> continue
    |
    |- Are there multiple replicas, tenants, or adapters?
    |   |- Yes -> design routing and placement explicitly
    |   `- No -> simple replica pool may be enough
    |
    |- Is there high prefix or session reuse?
    |   |- Yes -> prefer KV-aware routing and native prefix reuse
    |   `- No -> standard load balancing is acceptable
    |
    |- Are long prompts or mixed prompt lengths hurting p95?
    |   |- Yes -> test admission control first, then prefill or encoder disaggregation
    |   `- No -> keep colocated
    |
    |- Is this a MoE model (DeepSeek-V3/V4, Qwen3-MoE, Kimi-K2, Mixtral)?
    |   |- Yes -> assess EP degree, EPLB support, and all-to-all topology
    |   |         see references/moe-expert-parallelism.md
    |   `- No -> continue
    |
    `- Does the model fit latency and cost targets at current precision?
        |- No -> choose runtime-supported quantization and re-run evals
        `- Yes -> keep the simpler stack
```

## Stack Guidance

### vLLM

- Good default for OpenAI-compatible text serving, structured outputs, LoRA serving, and broad quantization support.
- Strong fit for teams that want one runtime for text inference plus production router patterns.
- Official docs now expose separate pages for structured outputs, disaggregated prefilling, disaggregated encoder serving, LoRA, and quantization. Treat those features independently instead of assuming one toggle solves all performance issues.
- Important caveat: disaggregated prefilling is documented as experimental and does not improve throughput by itself; use it only after measuring real queueing or resource contention.

### SGLang

- Strong fit for chat, agents, repeated prefixes, multimodal serving, and adapter-heavy workloads.
- Current docs emphasize RadixAttention, HiCache, PD and EPD disaggregation, Model Gateway, DP Router, structured outputs for reasoning models, and LoRA serving.
- Prefer SGLang when prompt reuse, multimodal encoder pressure, or adapter churn is the main bottleneck rather than raw kernel speed alone.

### TensorRT-LLM

- Strong fit for NVIDIA-only deployments where explicit precision control, KV cache reuse, and low-latency GPU execution matter more than portability.
- Current docs expose precision-specific guidance, KV cache reuse, disaggregated serving, and `trtllm-serve`.
- Treat precision recommendations as runtime-scoped: TensorRT-LLM documents more INT8 and low-bit paths than a blanket hardware-only rule suggests.

### Router And Control Plane

- Separate token generation from request placement once you have more than a single box or a single replica.
- Use [routing-and-control-planes.md](references/routing-and-control-planes.md) for cache-aware routing, sticky placement, multi-LoRA request steering, and control-plane selection.
- vLLM-centric clusters: start with vLLM Router or the vLLM Production Stack.
- Kubernetes and cache-aware scale-out: evaluate llm-d.
- SGLang-centric clusters: use Model Gateway or DP Router patterns.
- Multi-cloud or on-premise data-center environments: consider Dynamo (open-source Apache 2.0, supports AWS EKS, GKE, and NVIDIA hardware; confirmed 2026-05-17 via github.com/ai-dynamo/dynamo).

## Quantization Rules

- Choose quantization inside the runtime you will actually deploy, not from a generic hardware table.
- On vLLM, prefer the runtime-native path first. Current docs expose FP8, INT4 W4A16, AWQ, GPTQ, and INT8 W8A8, with INT8 W8A8 explicitly excluding Blackwell (compute capability >= 10.0) in vLLM docs — FP8 is the documented Blackwell substitute.
- On TensorRT-LLM, select from the precision modes the engine documents for that stack: FP8, INT8 SmoothQuant, weight-only INT4 or INT8, GPTQ or AWQ, and NVFP4 for supported Blackwell flows.
- On SGLang, verify model-specific quantizer support in current docs before committing to FP4, FP8, AWQ, GPTQ, or quantized KV cache.
- For CPU or edge deployment, use GGUF with llama.cpp and tune quant level, thread count, and `n_gpu_layers` explicitly.
- After any quantization change, re-run latency, long-context, and structured-output validation before rollout.

### Expert Judgment: When Quantization Actually Hurts Quality

- Quality risk is not evenly distributed across formats. Weight-only formats (AWQ, GPTQ, INT4 W4A16) rarely move task accuracy more than a point or two on general chat/instruct evals, but they degrade disproportionately on: long-context retrieval (needle-in-haystack style tasks), multi-step arithmetic and code, and low-resource languages — test those specifically, not just a generic eval average.
- W8A8 and other activation-quantized paths carry outlier risk that weight-only paths do not: a small number of hidden-state channels can dominate the error budget (see SmoothQuant calibration in [architecture-and-attention-serving.md](references/architecture-and-attention-serving.md) §6). If the calibration set does not match production traffic, W8A8 can look fine on a benchmark and fail on production long-tail inputs — calibrate on production-representative samples, not generic corpora.
- KV cache quantization (FP8/INT8 KV) is usually safer than weight quantization for quality, because it compresses an intermediate activation rather than model parameters — but it interacts with speculative decoding and long-context RoPE scaling in ways that are runtime-specific; validate the combination, not each piece alone.
- Structured-output and tool-call validity are often the first thing to regress under aggressive quantization, before generic quality metrics move — treat schema-valid rate as a leading indicator, not an afterthought.
- Stacking quantization changes (weight format + KV dtype + speculative decoding) in one rollout makes root-causing a regression nearly impossible. Change one lever, measure, then stack.
- If quality regresses only on a narrow task class (e.g., code, non-English, long documents) rather than broadly, the fix is usually a mixed-precision or per-layer scheme, not a wholesale rollback to full precision — check whether the runtime supports keeping specific layers or the LM head at higher precision.

## Expert Judgment: Batching vs Latency

- Continuous batching raises throughput almost for free until the GPU crosses from memory-bandwidth-bound to compute-bound decode (see the roofline model in [architecture-and-attention-serving.md](references/architecture-and-attention-serving.md) §3). Below that crossover, adding concurrency barely changes per-token latency — above it, added concurrency directly inflates TTFT and inter-token latency because requests now queue for compute, not just memory bandwidth.
- The practical tell: if p50 latency is flat while p95/p99 climb as load increases, the batch scheduler is admitting more concurrent sequences than the compute budget supports at the target latency SLO — cap `max_num_seqs` / concurrent-request limits rather than tuning kernels first.
- Do not chase throughput by raising batch or concurrency caps without a latency budget attached — throughput-optimal and latency-optimal operating points are different points on the same curve, and the "best" batch size is an SLO decision, not a hardware-maximization decision.
- Mixed short/long prompt traffic in one queue is the most common cause of p99 collapse that looks like a batching bug but is actually a scheduling/admission-control gap — bucket by prompt-length class or add chunked prefill before concluding the engine is misconfigured.
- When a stakeholder asks for "lower latency and higher throughput" without a concurrency ceiling, push back: those two goals trade off past the compute-bound crossover, and the SLO (not the engine) has to decide where the line sits.

## Expert Judgment: Capacity Planning Heuristics

- Do not size GPUs from raw parameter count alone. Size from three numbers together: weight memory at the target precision, KV cache memory at the target max-context × max-concurrency, and headroom for activations and framework overhead (roughly 10-20% of the total, verify against your runtime's actual footprint) — KV cache, not weights, is usually the first thing that runs out at real concurrency and long context.
- Treat "GPUs needed" as a queueing problem, not a peak-throughput division problem: use Little's Law and expected burst behavior (see [queueing-theory-applied.md](references/queueing-theory-applied.md)) to size for the tail, not the mean, or the fleet will meet average-load SLOs and fail every burst.
- A colocated baseline sized correctly beats a disaggregated topology sized on guesswork — get capacity numbers from the simple deployment first, then decide whether splitting phases is what actually buys back headroom.
- Reserve explicit capacity margin for cold-start and adapter-load events (autoscaling lag, LoRA cold loads, MoE weight loading) — steady-state utilization targets that ignore these events under-provision for real p99 behavior.

## Operational Rules

**Do**

- Measure TTFT, ITL, end-to-end latency, queueing delay, tokens per second, and schema-valid rate under realistic load.
- Cap queue depth and concurrency at the API boundary.
- Keep routing logic explicit once prefix reuse or adapter locality matters.
- Treat multimodal encoder saturation separately from decode saturation.
- Log request IDs, model ID, precision, cache hit data, and overload reason.

**Avoid**

- Avoid universal claims about the "best" engine without a workload profile.
- Avoid using stale benchmark ratios as architecture proof.
- Avoid disaggregation before proving colocated interference.
- Avoid switching precision without a rollback plan and eval set.
- Avoid generic round-robin when prefix or adapter locality drives most of the cost.

## Known Traps

- Benchmarking with synthetic prompts that do not match production prefix reuse, output length, schema-validity requirements, or concurrency bursts.
- Introducing prefill or encoder disaggregation before tightening queue limits, admission control, and placement policy on a colocated baseline.
- Optimizing only tokens/sec while TTFT, structured-output validity, or long-context quality regresses.
- Swapping engines or tokenizer stacks without validating compatibility for stop conditions, function/tool contracts, and schema-constrained decoding.
- Treating quantization as a pure hardware choice instead of a runtime-specific capability with quality and feature caveats.

## Common Anti-Patterns

- Chasing headline benchmark deltas as if they transfer directly to a different workload shape.
- Using round-robin routing on prefix-heavy or multi-LoRA workloads where locality determines most of the latency and cost.
- Mixing many prompt-length classes in one queue with no admission-control policy, then blaming the runtime for p95 collapse.
- Rolling out a new precision or kernel path without a schema-validity suite, long-context checks, and an explicit rollback window.

## Accuracy Protocol (Required)

- Treat benchmark ratios as workload-specific unless you have a current primary source and comparable conditions.
- State runtime assumptions whenever recommending hardware or precision changes.
- Mark experimental or beta features explicitly.
- Prefer official docs and release notes over secondary blogs whenever both exist.

## Navigation

### Core References

- [Serving Architectures](references/serving-architectures.md) - engine selection and serving patterns
- [Routing And Control Planes](references/routing-and-control-planes.md) - placement, stickiness, cache-aware routing
- [Disaggregated Inference](references/disaggregated-inference.md) - when to split prefill, encoder, or decode
- [Quantization Patterns](references/quantization-patterns.md) - runtime-scoped precision choices
- [KV Cache Optimization](references/kv-cache-optimization.md) - paging, reuse, cache dtypes, and reuse patterns
- [Architecture and Attention Serving](references/architecture-and-attention-serving.md) - serving-time limitation→workaround for attention variants (MHA/MQA/GQA/MLA KV footprint), SSM/hybrid serving, roofline/arithmetic intensity, long-context (StreamingLLM/sliding-window/ring), RoPE-scaling-at-serve traps, SmoothQuant outliers, draft-free spec-decode, FlashAttention decode-vs-prefill
- [MoE and Expert Parallelism](references/moe-expert-parallelism.md) - EP degree, EPLB, all-to-all topology for MoE models
- [Speculative Decoding Guide](references/speculative-decoding-guide.md) - EAGLE, MTP, draft model, Medusa algorithm families and deployment checklist
- [Parallelism Patterns](references/parallelism-patterns.md) - TP, PP, DP, EP tradeoffs
- [GPU Optimization Checklists](references/gpu-optimization-checklists.md) - hardware fit and production tuning
- [Profiling & Capacity Planning](references/profiling-and-capacity-planning.md) - benchmark design and sizing
- [Streaming Patterns](references/streaming-patterns.md) - SSE, WebSocket, and client streaming
- [Cost Optimization Patterns](references/cost-optimization-patterns.md) - routing, caching, batching, and FinOps

### Applied Foundations

- [Queueing Theory Applied](references/queueing-theory-applied.md) - continuous batching, KV-cache sizing, admission control, disaggregation, multi-tenant isolation, and token-budget backpressure — grounded in foundations-queueing-theory primitives (Little's Law, M/M/c, Erlang-C, Kingman, P-K)
- [Reliability Theory Applied](references/reliability-theory-applied.md) - SLO budget allocation across cascaded models, hedged requests, provider failover, cascading-failure prevention, KV-cache corruption rollback, and spec-decode rollback semantics — grounded in foundations-reliability-theory primitives (MTBF/MTTR, error budgets, FTA, redundancy math)

### Templates

- [vLLM Configuration](assets/inference/template-vllm-config.md)
- [TensorRT-LLM Configuration](assets/inference/template-tensorrtllm-config.md)
- [DeepSpeed Inference](assets/inference/template-deepspeed-inference.md)
- [LLM API Server](assets/serving/template-llm-api.md)
- [High-Throughput Setup](assets/serving/template-high-throughput-setup.md)
- [Disaggregated Serving](assets/serving/template-disaggregated-serving.md)
- [GGUF Format](assets/quantization/template-gguf.md)
- [AWQ Quantization](assets/quantization/template-awq.md)
- [GPTQ Quantization](assets/quantization/template-gptq.md)
- [Batching Configuration](assets/batching/template-batching-config.md)
- [Prefix Caching](assets/caching/template-prefix-caching.md)
- [Latency & Throughput Testing](assets/benchmarking/template-latency-throughput-test.md)
- [Inference Performance Review Checklist](assets/checklists/inference-review-checklist.md)

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/latency_benchmark.py` | Issue N concurrent requests against an OpenAI-compatible `/v1/chat/completions` endpoint and report p50/p95/p99 latency and throughput. stdlib-only (urllib + threading). |

### Data

- [data/sources.json](data/sources.json) - current primary sources and foundational papers

## Trend Awareness Protocol

When the user asks for the latest, best, current, recommended, or still-relevant inference tooling:

- use available browsing or web search
- prefer official runtime docs, release notes, and vendor docs
- verify feature status before recommending it
- report dated assumptions and runtime-specific caveats

Check at least these source types before final recommendations:

- engine docs for vLLM, SGLang, TensorRT-LLM, or llama.cpp
- router or control-plane docs when request placement matters
- vendor precision docs when hardware or quantization is involved
- current pricing docs when cost decisions depend on managed APIs

## Related Skills

- [ai-llm](../ai-llm/SKILL.md)
- [ai-rag](../ai-rag/SKILL.md)
- [ai-mlops](../ai-mlops/SKILL.md)
- [qa-observability](../qa-observability/SKILL.md)
- [ops-devops-platform](../ops-devops-platform/SKILL.md)
- huggingface-skills: plugin (external) — HF model evaluation with inspect-ai and lighteval

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current external facts, versions, pricing, and hardware support before final answers.
- Prefer primary sources and include links for volatile recommendations.
- If browsing is unavailable, label time-sensitive guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

