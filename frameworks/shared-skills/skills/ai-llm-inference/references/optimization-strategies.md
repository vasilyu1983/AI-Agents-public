# Optimization Strategies: Latency, Throughput, Cost (Dec 2025)

Production patterns for optimizing LLM inference. This is intentionally **vendor-agnostic** and avoids benchmark numbers without context.

Core references:
- vLLM / PagedAttention (https://arxiv.org/abs/2309.06180)
- Orca scheduling (https://www.usenix.org/conference/osdi22/presentation/yu)
- FlashAttention (https://arxiv.org/abs/2205.14135)
- Speculative decoding (https://arxiv.org/abs/2302.01318)

---

## 0. Operating Principles (REQUIRED)

- Measure under **representative load**; single-request latency is not predictive.
- Optimize the **largest contributor** first (queueing vs prefill vs decode vs post-processing).
- Set and enforce budgets at the boundary: `max_input_tokens`, `max_output_tokens`, `max_concurrency`, `max_queue_depth`, `max_retries`.
- Treat every “optimization” as a **change**: validate quality, add rollback, and re-run the inference review checklist.

---

## 1. Measurement Protocol (REQUIRED)

### Define traffic shape

- Prompt length distribution (p50/p95/p99)
- Output length distribution
- Concurrency and QPS targets
- Streaming vs non-streaming and typical client behavior (cancellations, disconnects)

### Measure the right metrics

- **TTFT** (time to first token) p50/p95/p99
- **ITL / tok/s** (inter-token latency / token throughput)
- **Total latency** p50/p95/p99
- **Error rate** by class (timeout, overload, upstream, OOM, validation)
- **Saturation**: GPU memory headroom, GPU utilization, queue depth

### Tag every measurement run

- Model id + revision hash
- Serving config hash
- Hardware + driver/runtime versions
- Token limits + decoding settings

---

## 2. Latency Optimization (TTFT and Total)

### If TTFT is high

- Reduce prefill work:
  - Shrink prompt scaffolding and retrieved context (context budgets).
  - Use chunked prefill where supported.
- Reduce queueing:
  - Admission control: cap queue depth and return overload fast.
  - Autoscale on queue depth and p95 latency (not average utilization).

### If decode is slow (high ITL)

- Use more efficient kernels/runtime (FlashAttention-style kernels: https://arxiv.org/abs/2205.14135).
- Consider speculative decoding if your use case tolerates draft-model errors and you validate quality (https://arxiv.org/abs/2302.01318).
- Reduce output length: enforce `max_output_tokens`, add stop sequences, and prefer concise outputs where possible.

---

## 3. Throughput Optimization (QPS / tok/s)

### Scheduling and batching

- Use continuous batching / smart scheduling for high concurrency (Orca: https://www.usenix.org/conference/osdi22/presentation/yu).
- Use KV-cache aware serving and paging to avoid fragmentation and OOMs under load (vLLM/PagedAttention: https://arxiv.org/abs/2309.06180).

### Parallelism

- Choose parallelism based on bottleneck:
  - Tensor parallelism when the model does not fit one device.
  - Pipeline parallelism when depth dominates and interconnect is constrained.
  - Data parallelism (replicas) for throughput and availability.

---

## 4. Cost Optimization (Budget and Unit Economics)

- Model tiering: route easy traffic to smaller/cheaper models; reserve large models for hard cases.
- Caching with invalidation:
  - Prefix caching for repeated scaffolds (system/tool instructions).
  - Response caching only when you can invalidate safely (freshness/ACL correctness).
- Quantization/compression:
  - Treat as an optimization candidate only after you have a baseline and eval set.
  - Validate on: task success, refusal correctness, and long-context cases.
- Enforce budgets at the API boundary; do not rely on prompt text to cap spend.

---

## 5. Decision Tree: What to Optimize First?

```text
Latency/throughput regression: [Find the bottleneck]
    ├─ P99 spikes during load?
    │   ├─ Queue depth growing? → admission control + queue cap + autoscale
    │   └─ OOMs / evictions? → reduce context + improve KV management + adjust batching
    │
    ├─ TTFT too high?
    │   ├─ Long inputs? → context budgets + chunked prefill + retrieval trimming
    │   └─ Queueing? → concurrency caps + scale out
    │
    ├─ Decode slow (high ITL)?
    │   ├─ Kernel/runtime inefficiency? → attention kernel upgrades + runtime tuning
    │   └─ Output too long? → max_output_tokens + stop sequences
    │
    └─ Cost too high?
        ├─ High token usage? → prompt/context reduction + output caps
        ├─ Too-large model? → tiering/router + fallback strategy
        └─ Inefficient serving? → batching + caching + validated quantization
```

---

## 6. Anti-Patterns (AVOID)

- Unbounded context windows (latency and OOM explosions).
- Unbounded retries (cascading failures).
- Benchmarking without concurrency (false confidence).
- Optimizing throughput while violating TTFT SLOs (bad UX for interactive apps).
- Caching without invalidation and ACL enforcement (security/correctness failures).

---

## 7. Baseline Checklist (Before Shipping)

- [ ] Traffic model documented (prompt/output distributions, concurrency, streaming).
- [ ] Latency/cost budgets enforced at API boundary.
- [ ] Inference review checklist completed: `../assets/checklists/inference-review-checklist.md`.
- [ ] Telemetry exported for tokens/latency/errors/queue depth (OpenTelemetry GenAI semconv: https://opentelemetry.io/docs/specs/semconv/gen-ai/).
- [ ] Rollback plan tested (previous model/config still deployable).
