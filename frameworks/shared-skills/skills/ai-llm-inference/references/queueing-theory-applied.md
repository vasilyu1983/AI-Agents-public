---
name: queueing-theory-applied
description: Queueing-theory primitives mapped to LLM inference problems — continuous batching, KV-cache sizing, prefill/decode disaggregation, admission control, speculative decoding, multi-tenant isolation, and token-budget backpressure.
type: reference
---

# Queueing Theory Applied to LLM Inference

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-03._

Applied patterns, anti-patterns, and recipes that translate queueing-theory primitives into LLM inference decisions. Use this reference when sizing clusters, tuning continuous batching, designing admission control, or diagnosing tail latency under load.

Primitives live in [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md). This reference assumes familiarity with Little's Law, M/M/c, M/G/1 (Pollaczek-Khinchine), Erlang-C, Kingman's formula, priority queues, and fork-join; it does not re-derive formulas — it shows how to apply them to LLM serving systems.

---

## Table of Contents

- [Why Queueing Theory for LLM Inference](#why-queueing-theory-for-llm-inference)
- [Patterns](#patterns)
  - [P1 — Continuous Batching as M/M/c with Batched Service](#p1--continuous-batching-as-mmc-with-batched-service)
  - [P2 — KV-Cache Warm-Pool Sizing via Little's Law](#p2--kv-cache-warm-pool-sizing-via-littles-law)
  - [P3 — Prefill/Decode Disaggregation as a Two-Stage Queue](#p3--prefillsdecode-disaggregation-as-a-two-stage-queue)
  - [P4 — Tail-Latency Admission Control with Erlang-C](#p4--tail-latency-admission-control-with-erlang-c)
  - [P5 — Speculative Decoding Under Contention as Preemptive Priority](#p5--speculative-decoding-under-contention-as-preemptive-priority)
  - [P6 — Multi-Tenant Isolation via Weighted Fair Queueing](#p6--multi-tenant-isolation-via-weighted-fair-queueing)
  - [P7 — Token-Budget-Aware Backpressure](#p7--token-budget-aware-backpressure)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Fixed Batch Size Under Variable Arrivals](#a1--fixed-batch-size-under-variable-arrivals)
  - [A2 — FIFO Across Mixed Prompt Lengths](#a2--fifo-across-mixed-prompt-lengths)
  - [A3 — No Head-of-Line Protection](#a3--no-head-of-line-protection)
  - [A4 — Ignoring Queue Depth in Autoscaler Triggers](#a4--ignoring-queue-depth-in-autoscaler-triggers)
- [Recipes](#recipes)
  - [R1 — Sizing a vLLM Cluster for a p99 Latency Target](#r1--sizing-a-vllm-cluster-for-a-p99-latency-target)
  - [R2 — Tuning Continuous Batching for the Throughput-Cost Frontier](#r2--tuning-continuous-batching-for-the-throughput-cost-frontier)
  - [R3 — Reproducing Tail Latency in a Load Test with Realistic Arrival Distribution](#r3--reproducing-tail-latency-in-a-load-test-with-realistic-arrival-distribution)
- [Composition](#composition)
- [Sources](#sources)

---

## Why Queueing Theory for LLM Inference

LLM inference is a queueing system. Requests arrive, wait for GPU capacity, are batched, and depart. The familiar saturation effects — latency exploding near ρ = 1, variance inflating p99, priority inversion under mixed workloads — all appear in LLM serving, but with LLM-specific structure:

- **Service time is not IID**: a 10-token prompt with a 10-token output and a 4,096-token prompt with a 2,000-token output occupy the same queue but have radically different service times. CV²_s is enormous.
- **KV cache is a finite resource with state**: the "server" carries per-request state (KV cache pages) that persists across the decode phase. Cache eviction is a service-time spike.
- **Batching changes the M/M/c model**: continuous batching does not process requests one at a time — it executes a dynamic batch in parallel. The effective service rate μ depends on batch size and token mix, not on a fixed per-request rate.
- **Two distinct phases**: prefill (prompt processing, compute-bound, high GPU utilization spike) and decode (token generation, memory-bandwidth-bound, lower per-token GPU utilization) have different service-time distributions. Treating them as one stage inflates CV²_s and misidentifies the bottleneck.

The four places where queueing theory pays off most in LLM inference:

1. **Cluster sizing**: Erlang-C gives the minimum replica count to meet a TTFT SLO before you buy GPUs.
2. **Batch and queue configuration**: Little's Law translates queue depth to latency; sizing queues without it produces bufferbloat.
3. **Admission control thresholds**: the Erlang-C wait probability gives a principled trigger for shedding load rather than a heuristic CPU threshold.
4. **Priority and isolation**: the P-K residual-time analysis explains why even a single long prompt can catastrophically delay subsequent short requests without head-of-line protection.

---

## Patterns

### P1 — Continuous Batching as M/M/c with Batched Service

**Primitive anchors**: M/M/c (Erlang-C) (#3), M/G/1 / P-K (#4), Kingman (#7)

**The inference framing.** In continuous batching (vLLM, SGLang, TGI), requests join a running batch at the next iteration boundary rather than waiting for the current batch to fully complete. The batch size b is dynamic: as requests finish, new ones join. The effective service rate per GPU server is not μ = 1/E[S_single_request] but μ_effective(b) = throughput_tokens/s / mean_output_tokens, which increases with b up to GPU memory saturation.

**Model.** Treat each GPU server as a multi-server M/G/1-like node. The service time for a request in a batch of size b is:

```
E[S(b)] ≈ (E[prompt_tokens] + E[output_tokens]) / (b × decode_tokens_per_step × steps_per_second)
```

At low b, E[S(b)] is dominated by individual prefill latency. At high b, the batch amortises the prefill cost and decode throughput rises, but KV cache pressure increases, causing evictions that spike service time (CV²_s rises).

**Effective utilization.** With c GPU replicas each running continuous batching at max batch size b_max:

```
a = λ × E[S(b_max)]         (offered load in Erlangs)
ρ = a / c                   (utilization)
```

Apply Erlang-C to find the probability a request must wait:

```
C(c, a) = Erlang-C formula (see foundations-queueing-theory #3)
Wq = C(c, a) / (c × μ_effective - λ)
```

Target ρ ≤ 0.70 for TTFT SLO compliance; continuous batching at ρ = 0.85 produces C(c, a) ≈ 0.5, meaning half of requests wait before even entering the batch.

**Kingman correction for real traffic.** Prompt lengths follow a power-law distribution in production (many short, a few very long). CV²_s is typically 3–8 for mixed workloads. Apply Kingman:

```
VF = (CV²_a + CV²_s) / 2
Wq_real ≈ Wq_erlang × VF
```

At VF = 4 and ρ = 0.70, Wq_real is 4× the M/M/c prediction. A service that appears correctly sized under M/M/c analysis violates TTFT SLOs in production because prompt length variance is ignored.

**Design rules:**
- Set max batch size b_max at the point where KV cache evictions begin — this is the effective service rate ceiling. Above it, service time spikes because evicted requests must re-prefill.
- Monitor CV²_s of output length in production. If CV²_s > 3, output-length bucketing (routing short and long outputs to separate replica pools) reduces effective variance per pool.
- Size c from Erlang-C at ρ = 0.70, then multiply Wq by VF. If Wq × VF > TTFT_SLO / 2, add replicas.
- Autoscaler should trigger at ρ = 0.65, not CPU 80% — GPU utilization in continuous batching is already near 100% at low ρ due to prefill spikes.

**When to use**: vLLM or SGLang cluster sizing; interpreting GPU utilization metrics; choosing max-batch-size and max-num-seqs parameters.

---

### P2 — KV-Cache Warm-Pool Sizing via Little's Law

**Primitive anchors**: Little's Law (#1), M/M/c (#3), Bufferbloat (#8)

**The inference framing.** The KV cache is not just a performance optimization — it is a bounded resource that determines system capacity. Requests whose KV cache pages are evicted must re-prefill, causing a service-time spike (the "cache miss" path). The cache behaves as a finite resource shared across concurrent requests: it is a server farm with per-request state.

**Little's Law for cache occupancy.** At any moment, the number of KV cache pages L occupied in steady state equals:

```
L = λ × W_per_request
W_per_request ≈ (E[prefill_tokens] + E[output_tokens]) × bytes_per_token / page_size
L = λ × W_per_request   (Little's Law: L = λW)
```

If the GPU has P_max total cache pages and L > P_max × utilization_ceiling (typically 0.90 of capacity), evictions begin. At that point, service time CV²_s spikes because evicted requests extend their service time by a full re-prefill.

**Warm-pool sizing.** To maintain a warm pool that prevents evictions:

```
P_required = λ × E[tokens_in_flight] / page_size × safety_factor (1.2–1.5)
E[tokens_in_flight] = E[prefill_tokens] + E[output_tokens] × fraction_still_decoding
```

If P_required > P_available, either reduce λ (admission control), increase GPU VRAM, or reduce precision (quantized KV cache) to fit more pages per GPU.

**Bufferbloat analogy.** An oversized KV cache pool without admission control is a form of bufferbloat: the cache absorbs spikes without emitting backpressure. Requests queue in KV cache pages; latency accumulates silently. The fix is the same as for network bufferbloat — bound the occupancy and apply backpressure (admission control, queue depth limit) before the cache fills.

**Design rules:**
- Compute L = λ × W_per_request before setting max-num-seqs. If steady-state L > 0.80 × P_max pages, the cache will thrash under any load spike.
- Set a KV cache usage alert at 75% occupancy. Cache usage × (page_size / throughput) is the leading latency indicator — it rises before p99 TTFT breaches.
- For prefix caching (vLLM automatic prefix caching, SGLang RadixAttention): the effective L per request is reduced by prefix hit rate. A 60% prefix hit rate reduces L by 0.6 × E[prefix_tokens], allowing proportionally more concurrent requests at the same P_available.
- Monitor cache hit rate per request class. Routing prefix-sharing requests to the same replica (sticky routing) increases hit rate and reduces effective per-request cache occupancy.

**When to use**: setting vLLM `--gpu-memory-utilization`, diagnosing cache eviction warnings in logs, sizing KV cache dtype (FP8 KV vs FP16 KV), planning multi-GPU KV cache partitioning.

---

### P3 — Prefill/Decode Disaggregation as a Two-Stage Queue

**Primitive anchors**: Jackson Networks (#6), M/G/1 / P-K (#4), M/M/c (#3)

**The inference framing.** Prefill (processing the prompt) and decode (generating tokens) are two distinct service phases with different compute profiles:
- Prefill: compute-bound, high GPU utilization for a short burst.
- Decode: memory-bandwidth-bound, lower GPU utilization per step, but long duration for long outputs.

In a colocated setup, both phases share the same GPU queue. Kingman's formula explains the tail-latency cost: CV²_s for combined prefill+decode is large because prefill can be 20–200 ms and decode can be 500 ms–60 s for long outputs. High CV²_s inflates Wq for all requests in the queue.

**Two-stage Jackson network.** When disaggregated, the request path becomes:

```
Arrival queue → [Prefill Server Pool, c_p GPUs, μ_p] → [Decode Server Pool, c_d GPUs, μ_d]
```

By Jackson's theorem, each stage can be analyzed independently with its own M/M/c model (assuming Poisson handoff between stages, which holds approximately):

```
Stage 1 (prefill):  ρ_p = λ × E[S_prefill] / c_p
Stage 2 (decode):   ρ_d = λ × E[S_decode]  / c_d
```

The bottleneck is the stage with higher ρ. For long-output workloads, decode is typically the bottleneck. For short-output, high-concurrency workloads (embedding generation, classification), prefill is the bottleneck.

**When disaggregation helps.** Disaggregation helps when:
- The prefill stage's compute burst is causing GPU queue interference with in-flight decode steps (measurable as ITL spikes during prefill events on colocated setup).
- The output length distribution has high CV²_s, and splitting stages isolates the variance — short outputs drain quickly from the decode pool, long outputs do not block the prefill stage.

**When disaggregation does not help.** For symmetric workloads (similar prefill and decode times, low CV²_s), disaggregation adds network transfer overhead (KV cache shipping between prefill and decode nodes) without reducing effective queue latency. Run the Jackson analysis with measured ρ_p and ρ_d before committing to disaggregation.

**Design rules:**
- Compute ρ_p and ρ_d from production traces. If abs(ρ_p − ρ_d) < 0.15, the workload is symmetric and disaggregation provides minimal queueing benefit.
- Size c_p and c_d separately from their respective Erlang-C targets. c_p should achieve ρ_p ≤ 0.70; c_d should achieve ρ_d ≤ 0.70.
- After disaggregation, re-run Jackson flow-balance. The KV cache transfer link between stages is now a queue with its own latency. Model it explicitly.
- vLLM disaggregated prefilling: treat as experimental (as noted in SKILL.md). Measure throughput improvement, not just latency — disaggregation does not increase throughput by itself unless one stage is the bottleneck.

**When to use**: deciding whether prefill/decode disaggregation is justified; sizing disaggregated replica ratios (how many prefill GPUs per decode GPU); diagnosing TTFT vs ITL tradeoffs.

---

### P4 — Tail-Latency Admission Control with Erlang-C

**Primitive anchors**: M/M/c (Erlang-C) (#3), Kingman (#7), Bufferbloat (#8)

**The inference framing.** Without admission control, a GPU server running continuous batching will accept all arriving requests, grow the queue, and produce unbounded TTFT as ρ → 1. Admission control is a principled mechanism to shed load before the latency SLO is breached, signalling the load balancer or client to retry or route elsewhere.

**Erlang-C admission trigger.** Compute the current offered load:

```
a_current = λ_measured × E[S_batch] / c
ρ = a_current / c
```

Use Erlang-C to compute the current expected wait:

```
Wq = C(c, a_current) / (c × μ_effective - λ_measured)
```

When Wq > TTFT_SLO × admission_fraction (e.g. 0.50), begin shedding new arrivals with HTTP 429. This is a leading indicator — it fires before the SLO is breached, giving load balancers time to reroute.

**Kingman-adjusted threshold.** Because real traffic has CV²_s > 1 (prompt length variance) and CV²_a > 1 (bursty HTTP traffic, retry storms):

```
Wq_real = Wq_erlang × VF
```

Set the admission trigger at Wq_real > 0.50 × TTFT_SLO. Equivalently, set it at ρ < ρ* where ρ* is solved from Wq_real(ρ*) = 0.50 × TTFT_SLO. For VF = 3, ρ* ≈ 0.60 — much lower than the naive "shed at ρ = 0.90" heuristic.

**Queue-depth backpressure.** Little's Law gives the queue depth at the admission threshold:

```
Lq_threshold = λ × Wq_threshold
```

Implement queue-depth monitoring and shed load when queue depth > Lq_threshold. Queue depth is computable in real time (it is a counter); Wq is derived and lagged. Use queue depth as the primary trigger, Wq as the secondary confirmation.

**Design rules:**
- Never rely solely on GPU utilization as the admission trigger. GPU utilization in continuous batching can be 95%+ even at ρ = 0.60 due to prefill spikes — it does not reflect queue depth.
- Set the admission control threshold conservatively (ρ* ≈ 0.60 for VF ≥ 3) and tune outward, not inward. Erring toward lower ρ* costs throughput; erring toward higher ρ* causes SLO breaches.
- Apply admission control at the request routing layer (API gateway or load balancer), not inside the inference engine. Shedding inside the engine wastes GPU cycles on requests that are rejected after prefill.
- For prompt length classes with very different E[S], compute ρ* per class. A class of 4,096-token prompts has a different ρ* than a class of 64-token prompts.

**When to use**: configuring vLLM `--max-num-seqs` and queue limits; designing API gateway rate limits for inference endpoints; setting autoscaler scale-up triggers for GPU replicas.

---

### P5 — Speculative Decoding Under Contention as Preemptive Priority

**Primitive anchors**: Priority Queues (#5), M/G/1 / P-K (#4), Fork-Join (#11)

**The inference framing.** Speculative decoding runs a small draft model to speculatively generate k tokens, then verifies them with the target model in a single forward pass. If accepted, latency is reduced by the factor (1 + acceptance_rate × k). If rejected, the draft tokens are discarded and the target model re-generates from the verification point.

This is a fork-join pattern with preemption semantics: the draft model and verification step are sequential, but the draft model is cheap and fast, while the verification step is expensive and shared with non-speculative requests.

**Priority structure.** Under contention, the verification step (target model forward pass) must be treated as high priority relative to non-speculative requests. If the verification is delayed by a queued non-speculative request, the draft tokens expire — the acceptance window closes and the full decode penalty is paid.

Model verification as class 1 (preemptive):
```
ρ₁ = λ_spec × E[S_verify] / c
Wq_1 = W₀ / (1 − ρ₁)    (wait at most one in-progress service period)
```

Non-speculative decode as class 2:
```
ρ₂ = λ_non_spec × E[S_decode] / c
```

Starvation check: ρ₁ + ρ₂ < 0.85 to ensure class 2 does not starve.

**Acceptance rate under load.** The acceptance rate α(t) of speculative decoding degrades under GPU contention: if the draft model is also resource-contended, draft quality drops (stale model state or deferred generation). At high ρ, speculative decoding overhead (draft model compute + verification pass) can exceed the savings.

Rule: speculative decoding is beneficial only when:
```
α × k × E[S_token] > E[S_draft] + E[S_verify_overhead]
```
where E[S_verify_overhead] is the incremental cost of verification versus direct generation. This inequality inverts at high ρ when draft model latency increases.

**Design rules:**
- Measure α under realistic load (not synthetic uniform prompts). α varies by prompt type — code generation has lower α than chat continuation.
- Reserve a dedicated compute allocation for the draft model. If the draft model is time-shared with decode traffic, the fork-join max-wait dominates and speculative decoding loses its latency benefit.
- At ρ > 0.75, verify that speculative decoding still provides net benefit. It is common to disable speculative decoding under peak load rather than allow it to degrade all other requests.

**When to use**: enabling/disabling speculative decoding in vLLM or SGLang under mixed load; sizing draft-model capacity; diagnosing acceptance-rate degradation under high concurrency.

---

### P6 — Multi-Tenant Isolation via Weighted Fair Queueing

**Primitive anchors**: Priority Queues (#5), M/G/1 / P-K (#4), M/M/c (#3)

**The inference framing.** A multi-tenant LLM API serves tenants with different SLOs, throughput quotas, and prompt length distributions. Without isolation, a single bursty tenant (high λ, long prompts) can monopolise the GPU batch, causing other tenants to miss their SLOs.

**Weighted fair queueing model.** Assign each tenant i a weight wᵢ such that Σwᵢ = 1. The effective throughput fraction for tenant i is:

```
fraction_i = wᵢ / Σwⱼ
```

Under WFQ, tenant i's effective service rate is:

```
μ_i_effective = μ_total × wᵢ
```

And tenant i's individual utilization is:

```
ρ_i = λ_i / μ_i_effective
```

For SLO compliance, each tenant's ρ_i must be below the per-tenant SLO threshold ρ*_i.

**Admission per tenant.** Apply per-tenant Erlang-C:

```
Wq_i = C(c_i_effective, a_i) / (c_i_effective × μ_i_effective − λ_i)
```

where c_i_effective ≈ c × wᵢ (fractional virtual servers). If any tenant's Wq_i exceeds its SLO, either increase that tenant's weight or reduce their λ via rate limiting.

**P-K variance isolation.** High-CV²_s tenants (those with mixed short/long prompts) contaminate the shared queue's effective service time. WFQ per-tenant isolation bounds the CV²_s that any one tenant can inject into another's queue. Two tenants can have radically different CV²_s and each still receive their SLO, because their queues are separated.

**Design rules:**
- Set weights proportional to SLO × quota. A premium tenant with 50 ms TTFT SLO and 100 QPS quota gets higher weight than a standard tenant with 200 ms TTFT and 20 QPS.
- Monitor per-tenant ρ_i in addition to global ρ. A global ρ of 0.70 can conceal tenant A at ρ_A = 0.95 and tenant B at ρ_B = 0.40.
- Implement WFQ in the request scheduler (not just at the API gateway rate limiter). Rate limiting at the gateway prevents overload but does not ensure SLO compliance within the admitted traffic. The scheduler must implement fair-weighted dispatch to the GPU batch.
- For tenants with very long prompts (E[S] >> median), cap their maximum concurrent requests independently of weight. Their large service time increases residual time for the entire queue even under WFQ.

**When to use**: multi-tenant inference API design; setting per-customer rate limits and SLO tiers; diagnosing SLO breaches on a shared inference cluster.

---

### P7 — Token-Budget-Aware Backpressure

**Primitive anchors**: Little's Law (#1), Bufferbloat (#8), M/M/c (#3)

**The inference framing.** GPU memory constrains both the KV cache (per-request state) and the model weights. Total token throughput is bounded by:

```
tokens_in_flight_max = KV_cache_pages × page_size_tokens
```

When tokens_in_flight approaches this limit, new requests cannot be admitted without evicting existing ones. Token budget is therefore the finite resource that determines the true service capacity — not just request count.

**Little's Law for token budget.** At steady state:

```
L_tokens = λ_tokens × W_per_token_in_system

where λ_tokens = λ_requests × E[output_tokens + prefill_tokens]
      W_per_token_in_system ≈ E[request_lifetime_in_system]
```

When L_tokens > tokens_in_flight_max, the system is over capacity and evictions cascade.

**Backpressure signal.** Define a token budget utilization metric:

```
budget_utilization = L_tokens_current / tokens_in_flight_max
```

Apply backpressure tiers:
- budget_utilization < 0.70: accept all requests
- budget_utilization 0.70–0.85: shed longest-prompt requests (highest token budget consumers)
- budget_utilization > 0.85: shed all new requests (HTTP 429)

This is a finer-grained admission control than request count alone: two 4,096-token requests consume 64× the token budget of two 64-token requests.

**Chunked prefill.** For very long prompts, chunked prefill (vLLM `--enable-chunked-prefill`) reduces the token budget spike during prefill by processing the prompt in chunks. This smooths the arrivals at the KV cache, reducing CV²_a for the cache occupancy queue. Model it as reducing E[prefill_tokens_in_flight] per step from E[full_prompt] to E[chunk_size].

**Design rules:**
- Implement token-budget monitoring as a first-class metric alongside request count and GPU utilization. Token budget utilization is a more direct predictor of KV cache evictions than any other metric.
- Set chunked prefill chunk size proportional to the GPU's decode batch capacity. A chunk size that matches the decode batch token rate prevents prefill from starving ongoing decode iterations.
- For long-context models (128k+ context), token budget pressure dominates over request count. The queue depth in tokens (L_tokens) is the correct Little's Law measure, not queue depth in requests.
- Alert on L_tokens > 0.75 × tokens_in_flight_max. By Little's Law, this is a leading indicator of eviction pressure: the queue is building faster than it is draining.

**When to use**: setting vLLM `--max-num-batched-tokens`; configuring chunked prefill; designing token-aware admission control for long-context models; diagnosing KV cache eviction spikes.

---

## Anti-Patterns

### A1 — Fixed Batch Size Under Variable Arrivals

**Symptom**: the team configures a static `max_batch_size` or `max_num_seqs`. At low load, GPU utilization is poor (small batches under-utilise compute). At high load, the fixed batch size creates a rigid admission queue — when the batch is full, requests stack up and TTFT spikes.

**Queueing diagnosis**: fixed batch size is equivalent to a D/G/1 queue (deterministic inter-service intervals) under a Poisson arrival process. At ρ < 0.50, a static batch size b_fixed produces batches with b_actual < b_fixed on average, wasting GPU compute. At ρ > 0.75, the batch is always full — the system behaves like a loss system (Erlang-B) for requests arriving when the batch is saturated, except those requests queue rather than drop, building unbounded waiting time.

**Harm**: the static batch size eliminates the continuous batching benefit at low load and produces head-of-line blocking at high load. GPU utilization oscillates between under-use and over-use rather than tracking the arrival rate.

**Fix**: use dynamic batch sizing (continuous batching with iteration-level scheduling). Monitor batch_size distribution in production. Set `max_num_seqs` as the upper bound (KV cache limit), not as the target batch size. Let the scheduler fill the batch up to this bound on each iteration.

---

### A2 — FIFO Across Mixed Prompt Lengths

**Symptom**: short-prompt requests (64 tokens) have 5-second TTFT while long-prompt requests (4,096 tokens) are processed normally. p99 TTFT is dominated by the occasional long-prompt request that blocks the entire queue.

**Queueing diagnosis**: FIFO scheduling with high CV²_s is the worst-case queueing policy for tail latency. By the P-K residual-time formula, the mean wait for any request includes the residual service time of the in-progress request:

```
W_residual = E[S²] / (2 × E[S]) = E[S] × (1 + CV²_s) / 2
```

At CV²_s = 8 (common for mixed 64-token and 4,096-token prompts), W_residual = 4.5 × E[S]. A 64-token request arriving just after a 4,096-token prefill begins waits the full 4,096-token prefill duration before it can start.

**Harm**: p99 TTFT is dominated by long-prompt residual service time even at low overall utilization. The SLO for short interactive requests is determined by the longest request in the batch, not the load level.

**Fix**: implement shortest-job-first (SJF) or prompt-length-bucketed priority queues. Route short-prompt requests (< 256 tokens) to a separate scheduling lane with higher priority. Apply P3's priority-queue analysis (non-preemptive priority, since mid-prefill preemption requires KV cache swap overhead).

---

### A3 — No Head-of-Line Protection

**Symptom**: a single malformed or extremely long request (e.g. 128k-token context) stalls all subsequent requests for tens of seconds. TTFT spikes systemically, not just for that request.

**Queueing diagnosis**: without head-of-line (HOL) protection, the inference scheduler treats the 128k-token request identically to a 128-token request. By the P-K formula, the residual service time of this request is:

```
W_residual(128k) = 128000 tokens / throughput_prefill_tokens_per_s
```

For a 100k tokens/s prefill throughput, W_residual ≈ 1.28 seconds. Every request arriving during this window waits at least 1.28 seconds for TTFT, regardless of its own prompt length. At 50 QPS, this is 64 requests adversely affected by a single outlier.

**Harm**: a single request causes a latency spike visible across all tenants and request classes. SLO burn is systemic rather than isolated.

**Fix**: implement maximum prompt length enforcement (configurable per tenant), chunked prefill (breaks the 128k prefill into chunks, interleaving decode iterations), and per-request timeout before admission. Apply admission control at the token-budget level (P7) rather than request count.

---

### A4 — Ignoring Queue Depth in Autoscaler Triggers

**Symptom**: the autoscaler triggers on GPU utilization > 80%. GPU utilization is consistently 90%+ even at low load (due to prefill spikes), so the autoscaler over-provisions. During a real load spike, the autoscaler does not respond because GPU utilization is already saturated in its monitoring window — by the time scale-out completes (2–5 minutes for GPU provisioning), the SLO breach has already occurred.

**Queueing diagnosis**: GPU utilization is a lagged, saturating signal. By Little's Law, queue depth Lq is a leading indicator:

```
Lq = λ × Wq
```

Lq rises before Wq breaches the SLO. GPU utilization rises after Lq is large. Setting the autoscaler trigger on Lq (or equivalently, on pending request count at the GPU server) fires earlier and more accurately than GPU utilization.

**Harm**: autoscaler under-reacts to actual load buildup (misses the leading indicator) and over-reacts to spurious GPU utilization spikes (prefill bursts). Scale-out cost is higher and SLO protection is weaker than a queue-depth trigger.

**Fix**: add request queue depth (pending_requests metric) and token budget utilization as autoscaler signals alongside GPU utilization. Set scale-up trigger at queue_depth > Lq_threshold (derived from Erlang-C at ρ* = 0.65), not GPU utilization threshold. Use GPU utilization as a secondary confirmation, not as the primary trigger.

---

## Recipes

### R1 — Sizing a vLLM Cluster for a p99 Latency Target

**Goal**: determine the minimum number of GPU replicas for a vLLM deployment to meet a TTFT p99 SLO at peak load.

**Primitive stack**: Erlang-C (#3) + Kingman (#7) + Little's Law (#1)

**Step 1: Collect workload inputs.**

```
From production traces or load test:
  λ_peak       = peak arrivals per second (requests/s)
  E[prompt]    = mean prompt token count
  E[output]    = mean output token count
  CV²_s        = service-time coefficient of variation squared
                 (estimate: (p99_service / p50_service - 1)² / 4, or measure from histogram)
  CV²_a        = inter-arrival variance (measure from request log; 2–4 for HTTP traffic)
  TTFT_SLO     = target TTFT p99 (e.g. 500 ms)
  throughput   = GPU decode tokens/s at target batch size (from vLLM benchmark)
```

**Step 2: Compute per-replica service rate and offered load.**

```
E[S_request] = (E[prompt] + E[output]) / (throughput_per_gpu / mean_batch_size)

# Approximate E[S] from profiling one GPU at realistic batch size
E[S] = measured mean end-to-end service time per request at b = b_target

a = λ_peak × E[S]          (offered load in Erlangs)
```

**Step 3: Run Erlang-C scan.**

```python
from math import factorial, exp

def erlang_c(c, a):
    """Erlang-C formula. Returns wait probability C(c, a)."""
    if a >= c:
        return 1.0  # unstable
    rho = a / c
    sum_terms = sum((a**k) / factorial(k) for k in range(c))
    last_term = (a**c / factorial(c)) * (1 / (1 - rho))
    return last_term / (sum_terms + last_term)

def wq_erlang(c, a, mu):
    """Mean wait in queue (seconds) for M/M/c."""
    C = erlang_c(c, a)
    lam = a * mu
    return C / (c * mu - lam)

# Scan for minimum c
mu = 1 / E_S
for c in range(int(a) + 1, int(a) + 30):
    rho = a / c
    if rho >= 1.0:
        continue
    Wq = wq_erlang(c, a, mu)
    VF = (CV2_a + CV2_s) / 2
    Wq_real = Wq * VF
    print(f"c={c}, rho={rho:.2f}, Wq={Wq*1000:.1f}ms, Wq_real={Wq_real*1000:.1f}ms")
    if Wq_real <= TTFT_SLO * 0.5:  # TTFT budget = Wq + E[prefill]
        c_min = c
        break
```

**Step 4: Apply safety margin and set autoscaler bounds.**

```
c_deploy = c_min + 1          # one replica headroom
autoscaler_min = c_deploy
autoscaler_max = c at 2× peak λ

# Scale-up trigger: queue_depth > Lq_threshold
Lq_threshold = lambda_peak * Wq_real   # Little's Law
```

**Step 5: Validate with load test.**

Run a load test with realistic prompt length distribution (not uniform synthetic). Confirm Wq_real from load test matches the Erlang-C prediction. If p99 TTFT > SLO at c_deploy, increase c by 1 and re-test. Typically, 1–2 extra replicas beyond c_min are sufficient for real traffic variability.

**Example** — chat API cluster sizing:
- λ_peak = 20 req/s, E[S] = 800 ms at b=8, μ = 1.25/s, a = 16 Erlangs
- CV²_a = 2.5, CV²_s = 4.0, VF = 3.25
- TTFT_SLO = 600 ms, TTFT budget for Wq = 200 ms (remaining for prefill = 400 ms)
- Erlang-C scan: c=18: ρ=0.89 (skip); c=20: ρ=0.80, Wq=120ms, Wq_real=390ms (too high); c=24: ρ=0.67, Wq=35ms, Wq_real=114ms ✓
- c_deploy = 25 GPUs. Autoscaler min=25, scale-up at queue_depth > 20 × 0.114 ≈ 3 pending requests.

---

### R2 — Tuning Continuous Batching for the Throughput-Cost Frontier

**Goal**: find the max-num-seqs and max-num-batched-tokens settings that maximise throughput for a cost target while staying within the TTFT SLO.

**Primitive stack**: M/G/1 / P-K (#4), Kingman (#7), Little's Law (#1), Bufferbloat (#8)

**Step 1: Profile service time vs batch size.**

```
For b = 1, 2, 4, 8, 16, 32, 64:
  Measure E[S(b)] and CV²_s(b) for representative prompt/output mix.
  Record KV cache eviction rate (evictions/min) at each b.
  Record GPU memory utilization at each b.

Stop at b_max where:
  - KV cache eviction rate > 0 (cache memory pressure begins), OR
  - E[S(b)] increase per doubling > 30% (memory bandwidth saturation)
```

**Step 2: Compute throughput-cost frontier.**

```python
results = []
for b in batch_sizes:
    mu_b = 1 / E_S_at_b[b]
    throughput_b = b * mu_b  # requests/s per GPU
    cost_per_req = 1 / throughput_b   # GPU-seconds per request
    results.append({
        'b': b,
        'throughput': throughput_b,
        'cost_per_req': cost_per_req,
        'CV2_s': cv2_s_at_b[b]
    })
```

Plot throughput vs b. The curve is concave — each doubling of b yields diminishing throughput gains. The "knee" of this curve is the efficient operating point.

**Step 3: Apply Kingman to find the p99-safe batch size.**

```
For each candidate b at the frontier:
  VF = (CV2_a + cv2_s_at_b[b]) / 2
  Wq_real = Wq_erlang(c, a_at_b) × VF

  If Wq_real > TTFT_budget: reject this b (p99 will breach at realistic load)
  Else: candidate for max-num-seqs
```

Note: larger b increases throughput but also increases CV²_s (more output length mixing per batch), which increases Wq_real. The optimal b for the throughput-cost frontier may not be the optimal b for the SLO.

**Step 4: Set parameters and monitor.**

```
vLLM configuration:
  --max-num-seqs = b_optimal
  --max-num-batched-tokens = b_optimal × E[prompt_tokens] × 1.5  (headroom for chunked prefill)
  --enable-chunked-prefill (if E[prompt_tokens] > 512)

Monitor in production:
  - batch_size_histogram (is b_actual near b_optimal?)
  - kv_cache_usage (is it below 0.75?)
  - ttft_p99 (within SLO?)
  - queue_depth (below Lq_threshold?)
```

**Strongest outcome**: step 3 (Kingman CV²_s check) frequently reveals that the batch size giving maximum raw throughput violates the p99 TTFT SLO because batch diversity increases CV²_s. The correct maximum batch size is typically 20–40% below the raw throughput maximum.

---

### R3 — Reproducing Tail Latency in a Load Test with Realistic Arrival Distribution

**Goal**: configure a load test that reproduces production p99 TTFT, not just mean TTFT, by using a realistic arrival distribution and prompt length distribution.

**Primitive stack**: Kingman (#7), M/G/1 / P-K (#4), Little's Law (#1)

**Step 1: Measure production arrival and service distributions.**

```
From production request logs:
  - inter_arrival_times[] → compute CV²_a = Var(IAT) / E[IAT]²
  - prompt_lengths[] → fit distribution (log-normal or Pareto often fits)
  - output_lengths[] → fit distribution
  - time-of-day shape (bursty sessions vs steady background)
```

**Step 2: Configure load test arrival process.**

```python
import numpy as np

def generate_poisson_arrivals(lambda_rate, duration_s):
    """Poisson arrivals: exponential inter-arrival times."""
    times = []
    t = 0
    while t < duration_s:
        iat = np.random.exponential(1 / lambda_rate)
        t += iat
        times.append(t)
    return times

def generate_bursty_arrivals(lambda_rate, cv2_a, duration_s):
    """Bursty arrivals with target CV²_a via Gamma inter-arrival times."""
    # Gamma IAT: mean=1/λ, variance=CV²_a/λ²
    shape = 1 / cv2_a
    scale = cv2_a / lambda_rate
    times = []
    t = 0
    while t < duration_s:
        iat = np.random.gamma(shape, scale)
        t += iat
        times.append(t)
    return times
```

Use `generate_bursty_arrivals` with measured CV²_a. A Poisson load test underestimates p99 latency when CV²_a > 1 (which it almost always is in production).

**Step 3: Configure prompt length distribution.**

```python
def sample_prompt_lengths(n, p50=128, p99=2048):
    """Log-normal prompt lengths matching production p50/p99."""
    import numpy as np
    # Fit log-normal: median = exp(mu), sigma from p99
    mu = np.log(p50)
    sigma = (np.log(p99) - mu) / 2.326  # 2.326 = z-score for 99th percentile
    samples = np.random.lognormal(mu, sigma, n).astype(int)
    return np.clip(samples, 16, 8192)  # enforce min/max
```

**Step 4: Run the load test and validate against Kingman.**

```
At the conclusion of the load test:
1. Compute measured CV²_s from service time histogram.
2. Compute measured CV²_a from inter-arrival histogram.
3. Compute VF = (CV²_a + CV²_s) / 2.
4. Compute predicted Wq_real = Wq_erlang × VF.
5. Compare predicted Wq_real to measured p99 TTFT − E[prefill_time].

If |predicted − measured| > 30%:
  - Check for non-stationarity (burst windows violate ergodicity assumed by Little's Law).
  - Check for KV cache evictions (service time spikes invalidate M/G/1 assumption).
  - Check for batch scheduling effects (batch composition changes effective service time).
```

**Step 5: Use the load test results to validate the cluster size from R1.**

```
Confirm: measured p99 TTFT ≤ TTFT_SLO at c_deploy from R1.
If violated: increase c and re-run. Typical cause is VF higher than estimated (production CV²_s > synthetic CV²_s).
```

**Strongest outcome**: step 2 (bursty arrivals with measured CV²_a) is the single change that most improves load test fidelity. A Poisson load test at the same QPS typically shows p99 latency 2–4× lower than production because it underestimates arrival burstiness. Using measured CV²_a closes most of this gap.

---

## Composition

The patterns and recipes compose into a sizing and tuning workflow:

| Starting Point | Natural Next Step |
|----------------|-------------------|
| P1 (continuous batching model) | Size c with R1; check KV cache with P2 |
| P2 (KV cache sizing) | Validate via Little's Law; set admission control with P4 |
| P3 (disaggregation decision) | Requires P1 ρ_p and ρ_d analysis as prerequisites |
| P4 (admission control) | Set thresholds from Erlang-C; monitor with Little's Law |
| P5 (speculative decoding) | Check acceptance rate under P4 admission control |
| P6 (multi-tenant WFQ) | Per-tenant P4 admission control and P1 utilization tracking |
| P7 (token budget backpressure) | Token-budget trigger feeds into P4 admission control |
| R1 (cluster sizing) | Feeds autoscaler parameters; validates with R3 |
| R2 (batch tuning) | Depends on R1 for operating ρ target |
| R3 (load test) | Validates R1 predictions; exposes CV²_s underestimation |

**Anti-patterns as guards**: run A1 check (dynamic vs static batch) before any throughput comparison. Run A2 check (FIFO across mixed lengths) before any p99 SLO analysis. Run A4 check (queue depth vs GPU utilization trigger) before finalizing autoscaler configuration.

---

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Chapters 24–26 (batching and scheduling).
- Yu, G. et al. (2022). "Orca: A Distributed Serving System for Transformer-Based Generative Models." *OSDI 2022*. (Continuous batching origin paper.)
- Kwon, W. et al. (2023). "Efficient Memory Management for Large Language Model Serving with PagedAttention." *SOSP 2023*. (KV cache paging and memory management.)
- Agrawal, A. et al. (2024). "Sarathi-Serve: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills." *OSDI 2024*. (Chunked prefill and decode-prefill interleaving.)
- Zheng, L. et al. (2024). "SGLang: Efficient Execution of Structured Language Model Programs." *NeurIPS 2024*. (RadixAttention and prefix caching.)
- [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) — canonical primitive definitions, formulas, and worked examples for all models referenced here.
