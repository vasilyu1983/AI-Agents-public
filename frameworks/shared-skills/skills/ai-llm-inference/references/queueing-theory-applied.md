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

LLM inference is a queueing system. **Model boundary:** Erlang-C assumes a stationary pooled M/M/c queue with independent exponential request service; Kingman estimates mean wait for a GI/G/1 single-server queue. Continuous batching shares GPU work, so reciprocal request latency is not replica throughput. Multiplying multi-server Erlang-C by a variability factor is an unvalidated approximation, not Kingman's theorem. None of these mean-wait formulas proves a p99 TTFT SLO. Measure end-to-end quantiles on representative arrivals and prompt/output mixes, including failure and retry load. Little's Law relates stationary averages, not instantaneous queue-depth limits. Requests arrive, wait for GPU capacity, are batched, and depart. The familiar saturation effects — latency exploding near ρ = 1, variance inflating p99, priority inversion under mixed workloads — all appear in LLM serving, but with LLM-specific structure:

- **Service time is not IID**: a 10-token prompt with a 10-token output and a 4,096-token prompt with a 2,000-token output occupy the same queue but have radically different service times. CV²_s is enormous.
- **KV cache is a finite resource with state**: the "server" carries per-request state (KV cache pages) that persists across the decode phase. Cache eviction is a service-time spike.
- **Batching changes the M/M/c model**: continuous batching does not process requests one at a time — it executes a dynamic batch in parallel. The effective service rate μ depends on batch size and token mix, not on a fixed per-request rate.
- **Two distinct phases**: prefill (prompt processing, compute-bound, high GPU utilization spike) and decode (token generation, memory-bandwidth-bound, lower per-token GPU utilization) have different service-time distributions. Treating them as one stage inflates CV²_s and misidentifies the bottleneck.

The four places where queueing theory pays off most in LLM inference:

1. **Cluster sizing**: Erlang-C can screen candidate replica counts when its request-service assumptions fit; load tests establish observed TTFT quantiles.
2. **Batch and queue configuration**: Little's Law translates queue depth to latency; sizing queues without it produces bufferbloat.
3. **Admission control thresholds**: the Erlang-C wait probability gives a principled trigger for shedding load rather than a heuristic CPU threshold.
4. **Priority and isolation**: the P-K residual-time analysis explains why even a single long prompt can catastrophically delay subsequent short requests without head-of-line protection.

---

## Patterns

### P1 — Continuous Batching as M/M/c with Batched Service

**Primitive anchors**: M/M/c (Erlang-C) (#3), M/G/1 / P-K (#4), Kingman (#7)

**The inference framing.** Requests share GPU iterations in continuous batching. Measure completed requests/s for the actual prompt/output mix and batching settings. Aggregate decode tokens/s divided by output length omits prefill and scheduler contention, so it is at most a workload-specific capacity approximation. Request residence time is not reciprocal capacity when multiple requests overlap.

**Candidate model.** If a pooled request-level M/M/c abstraction fits, a=λ/μ and ρ=λ/(cμ), with μ in completed requests/s per replica. Erlang-C estimates wait probability and mean wait only within this abstraction. Kingman estimates a single-server mean; a variability-scaled multi-server mean is a separate heuristic requiring calibration.

**Design rules.** Record capacity, memory pressure, queue wait, and TTFT quantiles across measured settings. Validate candidate replica count and batch limits with representative bursts, retries, and failures. No universal 0.70 utilization, 0.65 scale threshold, or variability factor certifies the SLO. Return an assumption/unit contract, measured candidate table, chosen settings, and overload recovery evidence.

**When to use**: vLLM or SGLang cluster sizing; interpreting GPU utilization metrics; choosing max-batch-size and max-num-seqs parameters.

---

### P2 — KV-Cache Warm-Pool Sizing via Little's Law

**Primitive anchors**: Little's Law (#1), M/M/c (#3), Bufferbloat (#8)

**The inference framing.** The KV cache is not just a performance optimization — it is a bounded resource that determines system capacity. Requests whose KV cache pages are evicted must re-prefill, causing a service-time spike (the "cache miss" path). The cache behaves as a finite resource shared across concurrent requests: it is a server farm with per-request state.

**Occupancy contract.** Little's Law gives mean active requests E[N]=λE[T], with residence T in seconds; pages/request is not residence time. For evolving allocations, mean pages equal λE[∫pages_request(t)dt] under a stationary matched population, with retained shared-prefix pages accounted separately without double counting. Measure actual page allocation traces, lifetimes, shared-prefix references, eviction policy, and allocator rounding. Pages and bytes must use the runtime's actual page definition.

**Sizing artifact.** Return measured average and peak occupancy, workload/lifetime window, available pages, sharing/invalidation semantics, and tested admission/headroom policy. Average occupancy does not certify burst safety. Prefix hit rate alone does not determine memory saved; cached prefixes may remain allocated after requests end. Distinguish waiting requests from admitted active allocations. Select occupancy alerts and limits from measured failure behavior rather than universal percentages.

**When to use**: setting vLLM `--gpu-memory-utilization`, diagnosing cache eviction warnings in logs, sizing KV cache dtype (FP8 KV vs FP16 KV), planning multi-GPU KV cache partitioning.

---

### P3 — Prefill/Decode Disaggregation as a Two-Stage Queue

**Primitive anchors**: Jackson Networks (#6), M/G/1 / P-K (#4), M/M/c (#3)

**The inference framing.** Prefill (processing the prompt) and decode (generating tokens) are two distinct service phases with different compute profiles:
- Prefill: compute-bound, high GPU utilization for a short burst.
- Decode: memory-bandwidth-bound, lower GPU utilization per step, but long duration for long outputs.

In a colocated setup, both phases share the same GPU queue. Service variability can worsen mean waits and tails; Kingman does not quantify the p99 cost: CV²_s for combined prefill+decode is large because prefill can be 20–200 ms and decode can be 500 ms–60 s for long outputs. High CV²_s inflates Wq for all requests in the queue.

**Two-stage Jackson network.** When disaggregated, the request path becomes:

```
Arrival queue → [Prefill Server Pool, c_p GPUs, μ_p] → [Decode Server Pool, c_d GPUs, μ_d]
```

Only under stable Jackson assumptions (Poisson external arrivals, exponential independent service, and probabilistic routing) may these stages use independent M/M/c product form. Real batching, KV transfers, and dependent workloads require measurement; Poisson handoff is not automatic:

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
- Compare measured interference, transfer cost, capacity, and latency of colocated versus disaggregated candidates; utilization similarity alone does not determine benefit.
- Size pools from measured stage capacity and load-test latency; no universal stage utilization certifies the SLO.
- After disaggregation, re-run Jackson flow-balance. The KV cache transfer link between stages is now a queue with its own latency. Model it explicitly.
- vLLM disaggregated prefilling: treat as experimental (as noted in SKILL.md). Measure throughput improvement, not just latency — disaggregation does not increase throughput by itself unless one stage is the bottleneck.

**When to use**: deciding whether prefill/decode disaggregation is justified; sizing disaggregated replica ratios (how many prefill GPUs per decode GPU); diagnosing TTFT vs ITL tradeoffs.

---

### P4 — Tail-Latency Admission Control with Erlang-C

**Primitive anchors**: M/M/c (Erlang-C) (#3), Kingman (#7), Bufferbloat (#8)

**The inference framing.** Without admission control, a GPU server running continuous batching will accept all arriving requests, grow the queue, and produce unbounded TTFT as ρ → 1. Admission control is a principled mechanism to shed load before the latency SLO is breached, signalling the load balancer or client to retry or route elsewhere.

**Erlang-C admission trigger.** Compute the current offered load:

```
a_current = λ_measured / μ_request   # offered load; matched request units
ρ = a_current / c
```

Use Erlang-C to compute the current expected wait:

```
Wq = C(c, a_current) / (c × μ_effective - λ_measured)
```

Use mean wait only to screen candidate admission settings. Tune actual thresholds using measured p99 TTFT, rejected-request rate, fairness, recovery behavior, and allowed retry load. Queue-depth and GPU utilization can be diagnostics, but neither is a universal early SLO guarantee. Set explicit bounded queue capacity and timeouts; reject before expensive work where runtime semantics allow.

**Return artifact:** assumed queue model and units, candidate capacity, measured mean queue wait separately from end-to-end quantiles, validated admission policy, and overload/recovery tests.

**When to use**: configuring vLLM `--max-num-seqs` and queue limits; designing API gateway rate limits for inference endpoints; setting autoscaler scale-up triggers for GPU replicas.

---

### P5 — Speculative Decoding Under Contention as Preemptive Priority

**Primitive anchors**: Priority Queues (#5), M/G/1 / P-K (#4), Fork-Join (#11)

**The inference framing.** Draft generation and target verification are dependent stages; their sequential execution is not a fork-join queue or automatic preemption. Acceptance does not imply a speed factor 1+αk: performance depends on accepted-prefix distribution, draft time, verification cost, scheduler contention, and output equivalence. Delayed verification alone does not make immutable draft tokens expire.

Compare speculative and ordinary decoding on matched workloads and concurrency. Record accepted tokens/cycle, draft and verification latency, target compute, memory, throughput, TTFT/ITL quantiles, and output/distribution correctness under the runtime's acceptance algorithm. Any priority policy needs explicit fairness and starvation tests; no utilization percentage alone prevents starvation. Return measured net benefit and bounded enable/disable criteria, not a universal acceptance threshold.

**When to use**: enabling/disabling speculative decoding in vLLM or SGLang under mixed load; sizing draft-model capacity; diagnosing acceptance-rate degradation under high concurrency.

---

### P6 — Multi-Tenant Isolation via Weighted Fair Queueing

**Primitive anchors**: Priority Queues (#5), M/G/1 / P-K (#4), M/M/c (#3)

**The inference framing.** A multi-tenant LLM API serves tenants with different SLOs, throughput quotas, and prompt length distributions. Without isolation, a single bursty tenant (high λ, long prompts) can monopolise the GPU batch, causing other tenants to miss their SLOs.

**Weighted scheduling contract.** Choose weights from explicit fairness/quota requirements and measured resource cost per class; multiplying SLO duration by quota is not a justified weight rule. Shared GPU batches couple tenants. A nominal fraction of throughput is a planning heuristic, not an isolated M/M/c queue. Fractional virtual replicas cannot be inserted into ordinary Erlang-C, and multiplying both replica count and rate by a weight double-counts its capacity reduction.

Use actual dedicated integer pools if an isolated queue model is needed. For shared scheduling, measure per-tenant throughput, rejection, queue wait, TTFT quantiles, and starvation under cross-tenant bursts. Return scheduling/admission policy, resource accounting units, tested fairness tradeoffs, and remaining shared-resource interference. Separate admission quotas from execution fairness.

---

### P7 — Token-Budget-Aware Backpressure

**Primitive anchors**: Little's Law (#1), Bufferbloat (#8), M/M/c (#3)

**Resource contract**: Distinguish scheduler iteration token budget, actual allocated KV pages, and pending request tokens. These are different resources. Generated output tokens enter cache later than prompt tokens; λ_tokens times full request lifetime is not a valid occupancy estimate without a matching token-arrival and token-residence model. Use the P2 request page-time integral and measured allocator traces for KV sizing.

Record token/page allocation changes, lifetimes, workload mix, memory limits, and scheduling interference under ordinary and chunked prefill. Chunking changes compute scheduling, not automatically total retained prompt KV memory. Set admission/alerts from measured memory pressure, queue age, TTFT/ITL quantiles, and rejection fairness; omit universal 70/85/75-percent thresholds or leading-indicator claims derived from Little's Law. Return the resource units, trace-based occupancy/capacity table, tested policy, and failure/rollback evidence.

**When to use**: setting vLLM `--max-num-batched-tokens`; configuring chunked prefill; designing token-aware admission control for long-context models; diagnosing KV cache eviction spikes.

---

## Anti-Patterns

### A1 — Fixed Batch Size Under Variable Arrivals

**Symptom**: the team configures a static `max_batch_size` or `max_num_seqs`. At low load, GPU utilization is poor (small batches under-utilise compute). At high load, the fixed batch size creates a rigid admission queue — when the batch is full, requests stack up and TTFT spikes.

**Queueing diagnosis**: fixed batching requires a batch-service model; deterministic arrival notation D/G/1 does not describe Poisson arrivals. At ρ < 0.50, a static batch size b_fixed produces batches with b_actual < b_fixed on average, wasting GPU compute. At ρ > 0.75, the batch is always full — queued arrivals are not Erlang-B loss traffic; model waiting capacity and stability explicitly.

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

For a 100k tokens/s prefill throughput, W_residual ≈ 1.28 seconds. In a strictly serial non-preemptive model, arrivals wait the remaining portion of this 1.28-second service, not at least the full duration. Actual interleaving can change the delay. At 50 QPS, this is 64 requests adversely affected by a single outlier.

**Harm**: a single request causes a latency spike visible across all tenants and request classes. SLO burn is systemic rather than isolated.

**Fix**: implement maximum prompt length enforcement (configurable per tenant), chunked prefill (breaks the 128k prefill into chunks, interleaving decode iterations), and per-request timeout before admission. Apply admission control at the token-budget level (P7) rather than request count.

---

### A4 — Ignoring Queue Depth in Autoscaler Triggers

**Symptom**: the autoscaler triggers on GPU utilization > 80%. GPU utilization is consistently 90%+ even at low load (due to prefill spikes), so the autoscaler over-provisions. During a real load spike, the autoscaler does not respond because GPU utilization is already saturated in its monitoring window — by the time scale-out completes (2–5 minutes for GPU provisioning), the SLO breach has already occurred.

**Queueing diagnosis**: GPU utilization is a lagged, saturating signal. By Little's Law, queue depth Lq is a leading indicator:

```
Lq = λ × Wq
```

Little's Law concerns steady-state averages and establishes no temporal leading/lagging ordering. Test queue-depth, queue-age, and utilization signals against actual bursts and scale-out delays.

**Harm**: autoscaler under-reacts to actual load buildup (misses the leading indicator) and over-reacts to spurious GPU utilization spikes (prefill bursts). Scale-out cost is higher and SLO protection is weaker than a queue-depth trigger.

**Fix**: add request queue depth (pending_requests metric) and token budget utilization as autoscaler signals alongside GPU utilization. Calibrate scale-up/admission triggers using measured queue-age and TTFT quantiles, burst duration, and provisioning delay; there is no universal ρ*=0.65 threshold. Use GPU utilization as a secondary confirmation, not as the primary trigger.

---

## Recipes

### R1 — Sizing a vLLM Cluster for a p99 Latency Target

**Goal**: determine the minimum number of GPU replicas for a vLLM deployment to meet a TTFT p99 SLO at peak load.

**Primitive stack**: Erlang-C (#3) + Kingman (#7) + Little's Law (#1)

**Step 1: Measure arrivals and capacity.** Collect per-request queue arrival, service start, first-token, completion, prompt/output lengths, cancellations, and retry counts. Estimate variance from observations; p50/p99 alone cannot determine CV². Measure saturated completed requests/s per replica for the actual workload mix. Do not divide aggregate decode token throughput by request latency or treat batch duration as request service without stating the model.

**Step 2: Screen candidates.** Under a defensible pooled M/M/c abstraction, use offered load a=λ/μ, utilization ρ=a/c, and mean queue wait E[Wq]=C(c,a)/(cμ−λ) for stable cμ>λ. In this exact model the queue-wait survival is P(Wq>t)=C(c,a)exp(−(cμ−λ)t), for t>=0. Its quantile is not the full TTFT quantile; do not add a prefill mean and claim an end-to-end p99. For continuous batching, prefer trace replay/simulation and measured capacity if the abstraction fails.

**Step 3: Load-test candidates.** Replay representative arrival bursts and prompt/output joint distributions across replica/batching settings. Record mean queue wait separately from queue-wait and TTFT p99, throughput, errors, rejections, and recovery. Quantiles need adequate observations and uncertainty; include the rejected population in the policy assessment. Increase candidate capacity or alter admission only according to measured results, deployment delay, and failure scenarios.

**Step 4: Return the sizing artifact.** Provide workload traces/window, capacity definition, assumptions, tested candidate table, observed TTFT quantiles and uncertainty, headroom rationale, and bounded autoscaler/admission settings. Name an observed passing candidate rather than a theorem-guaranteed minimum. Little's Law validates average counters under stable matched populations; it does not prescribe a burst-safe queue-depth threshold.

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

Record cache-pressure and latency changes; stop at measured memory/correctness limits or failed SLO criteria. An arbitrary percent increase does not establish bandwidth saturation.
```

**Step 2: Compute throughput-cost frontier.**

```python
results = []
for b in batch_sizes:
    throughput_b = measured_completed_requests_per_second[b]
    cost_per_req = 1 / throughput_b   # GPU-seconds per request
    results.append({
        'b': b,
        'throughput': throughput_b,
        'cost_per_req': cost_per_req,
        'CV2_s': cv2_s_at_b[b]
    })
```

Plot throughput vs b. Inspect the measured curve; concavity is not guaranteed. The "knee" of this curve is the efficient operating point.

**Step 3: Screen mean waits, then test p99 for each batch setting.**

```
For each candidate b at the frontier:
  VF = (CV2_a + cv2_s_at_b[b]) / 2
  Wq_real = Wq_erlang(c, a_at_b) × VF

  Treat Wq_real as a heuristic mean-wait screen only.
  Measure end-to-end TTFT p99 under representative arrivals before accepting b.
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

**Strongest outcome**: step 3 (Kingman CV²_s check) frequently reveals that the batch size giving maximum raw throughput violates the p99 TTFT SLO because batch diversity increases CV²_s. No universal percentage below the raw throughput maximum is justified; select from the measured candidate table.

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

Use `generate_bursty_arrivals` with measured CV²_a. A Poisson load test can miss bursts; measure variability and temporal dependence instead of assuming CV²_a > 1.

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
5. Compare predicted mean queue wait to measured mean queue wait under matched populations and assumptions. Evaluate measured p99 TTFT separately; never subtract a mean from a quantile and call it mean wait.

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

**Strongest outcome**: step 2 (bursty arrivals with measured CV²_a) is the single change that most improves load test fidelity. No universal p99 multiplier follows from CV²_a. Matching a variance alone can still miss autocorrelation, workload coupling, and retry storms; verify trace fidelity against measured tails.

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
