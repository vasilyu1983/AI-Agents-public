---
name: queueing-theory-applied
description: Queueing-theory primitives mapped to LLM inference problems — continuous batching, KV-cache sizing, prefill/decode disaggregation, admission control, speculative decoding, multi-tenant isolation, token-budget backpressure, and the LLM serving capacity and scheduling recipe.
type: reference
---

# Queueing Theory Applied to LLM Inference

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. Its skip-conditions route you to a different foundation if queueing is the wrong tool.

How queueing primitives apply to LLM serving decisions: cluster sizing, continuous batching, admission control, scheduling, and tail latency. Formulas and derivations live in the foundation; this file only says where they fit and where they break.

| Primitive | Owner |
|---|---|
| Little's Law | [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| M/M/c, Erlang-C | [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md) |
| M/G/1, Pollaczek-Khinchine, residual service | [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Priority queues, SRPT-family policies | [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) |
| Jackson networks | [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |
| Kingman (single server) | [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) |
| Bufferbloat, queue bounds | [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| Fork-join | [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md) |
| Allen-Cunneen G/G/c, square-root staffing, overload, goodput, retries, tail at scale | [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) |
| Trace-driven simulation | [trace-driven-simulation.md](../../foundations-queueing-theory/references/trace-driven-simulation.md) |

---

## Table of Contents

- [Why Queueing Theory for LLM Inference](#why-queueing-theory-for-llm-inference)
- [Patterns](#patterns)
  - [P1 — Continuous Batching as M/M/c with Batched Service](#p1--continuous-batching-as-mmc-with-batched-service)
  - [P2 — KV-Cache Warm-Pool Sizing via Little's Law](#p2--kv-cache-warm-pool-sizing-via-littles-law)
  - [P3 — Prefill/Decode Disaggregation as a Two-Stage Queue](#p3--prefilldecode-disaggregation-as-a-two-stage-queue)
  - [P4 — Tail-Latency Admission Control with Erlang-C](#p4--tail-latency-admission-control-with-erlang-c)
  - [P5 — Speculative Decoding Under Contention](#p5--speculative-decoding-under-contention)
  - [P6 — Multi-Tenant Isolation via Weighted Fair Queueing](#p6--multi-tenant-isolation-via-weighted-fair-queueing)
  - [P7 — Token-Budget-Aware Backpressure](#p7--token-budget-aware-backpressure)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
  - [R1 — Sizing a vLLM Cluster for a p99 Latency Target](#r1--sizing-a-vllm-cluster-for-a-p99-latency-target)
  - [R2 — Tuning Continuous Batching for the Throughput-Cost Frontier](#r2--tuning-continuous-batching-for-the-throughput-cost-frontier)
  - [R3 — Reproducing Tail Latency in a Load Test](#r3--reproducing-tail-latency-in-a-load-test)
  - [R4 — LLM Serving Capacity and Scheduling](#r4--llm-serving-capacity-and-scheduling)
- [Composition](#composition)
- [Sources](#sources)

---

## Why Queueing Theory for LLM Inference

**Objective.** The targets are TTFT and TPOT (inter-token latency) percentiles and SLO-goodput: the rate of requests that finish inside their TTFT and TPOT SLOs. Raw tokens/s is supporting evidence. Existing SLO and goodput material: [SKILL.md § Capacity Promotion Gate](../SKILL.md#capacity-promotion-gate) and [profiling-and-capacity-planning.md § Performance Budgets & SLOs](profiling-and-capacity-planning.md#performance-budgets--slos).

**Model boundary.** Erlang-C, P-K, Kingman, and Allen-Cunneen give mean waits under stationary assumptions. Mean-Wq formulas cannot certify a p99 TTFT. Use them to screen candidates, then measure end-to-end quantiles on representative arrivals, prompt/output mixes, failures, and retries.

LLM-specific structure that breaks the textbook models:

- **Service time is not IID.** Prompt and output lengths vary by orders of magnitude, so CV²_s is large. Compute CV²_s from the service-time sample; p99/p50 does not identify it.
- **The KV cache is state.** Each admitted request holds memory that grows while it decodes and frees only at completion. Eviction forces re-prefill, which is a service-time spike.
- **Batching changes the server.** Continuous batching runs a dynamic batch per iteration. Effective μ depends on batch size and token mix, not a fixed per-request rate.
- **Two phases.** Prefill is compute-bound; decode is memory-bandwidth-bound. Pooling them into one stage inflates CV²_s and hides the bottleneck.

---

## Patterns

### P1 — Continuous Batching as M/M/c with Batched Service

**Anchors**: M/M/c (03), M/G/1 (04), Kingman (07).

Measure completed requests/s per replica for the real prompt/output mix and batching settings. Aggregate decode tokens/s divided by output length ignores prefill and scheduler contention. Residence time is not reciprocal capacity when requests overlap.

If a pooled request-level M/M/c abstraction fits, a = λ/μ and ρ = λ/(cμ). For variable service, use Allen-Cunneen (Erlang-C Wq × (CV²_a + CV²_s)/2), not Kingman with E[S]/c. There is no portable ρ target: derive c from the SLO and measured variability (square-root staffing), then load-test.

**Use for**: vLLM/SGLang cluster sizing; reading GPU utilization; choosing `max-num-seqs`.

---

### P2 — KV-Cache Warm-Pool Sizing via Little's Law

**Anchors**: Little's Law (01), M/M/c (03), Bufferbloat (08).

The KV cache bounds concurrency. Little's Law gives mean active requests E[N] = λE[T], with T in seconds. For growing allocations, mean pages = λ·E[∫pages(t)dt] under a stationary matched population. Account retained shared-prefix pages separately.

Measure page-allocation traces, lifetimes, prefix sharing, eviction policy, and allocator rounding. Average occupancy does not certify burst safety; admission must use projected peak occupancy (see [R4](#r4--llm-serving-capacity-and-scheduling) step 2). Prefix hit rate alone does not give memory saved. Set occupancy alerts from measured failure behavior, not universal percentages.

**Use for**: `--gpu-memory-utilization`, eviction warnings, FP8 vs FP16 KV, multi-GPU KV partitioning.

---

### P3 — Prefill/Decode Disaggregation as a Two-Stage Queue

**Anchors**: Jackson networks (06), M/G/1 (04), M/M/c (03).

Colocated prefill and decode share one queue with a mixed service distribution. Illustrative spread: prefill tens to hundreds of ms, decode seconds to a minute for long outputs. High CV²_s inflates Wq for everyone (P-K).

Disaggregated path:

```
Arrivals → [Prefill pool, c_p, μ_p] → [KV transfer] → [Decode pool, c_d, μ_d]
ρ_p = λ·E[S_prefill]/c_p      ρ_d = λ·E[S_decode]/c_d
```

Product-form independence holds only under Jackson assumptions. Batching, KV transfer, and dependent workloads need measurement. The KV transfer link is its own queue.

- Disaggregation helps when prefill bursts cause measurable ITL spikes in colocated decode, or when isolating output-length variance frees the prefill stage.
- It does not help for symmetric, low-variance workloads: it adds KV shipping cost without cutting queue delay.
- It does not raise throughput unless one stage is the bottleneck. Compare measured interference, transfer cost, capacity, and latency; re-solve flow balance after the change.
- vLLM disaggregated prefilling is experimental (see SKILL.md).

---

### P4 — Tail-Latency Admission Control with Erlang-C

**Anchors**: M/M/c (03), Bufferbloat (08), overload and goodput ([multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md)).

Without admission control, the queue grows and TTFT is unbounded as ρ → 1. Once backlog wait Q/μ exceeds client timeouts, the server works on abandoned requests and goodput collapses; retries feed the backlog.

- Screen candidate settings with Erlang-C mean wait at measured λ and μ (matched request units).
- Bound the queue from the delay budget: limit ≈ μ × (TTFT budget − E[S]). Do not size it as a multiple of Lq.
- A FCFS arrival behind backlog Q waits Q/μ. The drain time Q/(μ−λ) is not the latency.
- Tune thresholds on measured p99 TTFT, rejection rate, fairness, retry load, and recovery. Reject before expensive prefill where the runtime allows.

**Return**: queue model and units, candidate capacity, mean queue wait reported separately from end-to-end quantiles, admission policy, overload/recovery test evidence.

---

### P5 — Speculative Decoding Under Contention

**Anchors**: Priority queues (05), M/G/1 (04).

Draft and verify are dependent sequential stages, not a fork-join queue. Speedup is not 1 + αk: it depends on the accepted-prefix distribution, draft time, verification cost, and scheduler contention. Compare against ordinary decoding on matched workloads and concurrency. Record accepted tokens/cycle, draft and verify latency, memory, throughput, TTFT/ITL quantiles, and output correctness. Return measured net benefit and enable/disable criteria; there is no universal acceptance threshold.

---

### P6 — Multi-Tenant Isolation via Weighted Fair Queueing

**Anchors**: Priority queues (05), M/G/1 (04), M/M/c (03).

A bursty tenant with long prompts can monopolise shared batches. Choose weights from explicit quota requirements and measured per-class resource cost. Shared batches couple tenants: a weight share is not an isolated M/M/c queue, and fractional virtual replicas cannot go into Erlang-C. Use dedicated integer pools when you need an isolated queue model. Otherwise measure per-tenant throughput, rejection, queue wait, TTFT quantiles, and starvation under cross-tenant bursts. Keep admission quotas separate from execution fairness.

---

### P7 — Token-Budget-Aware Backpressure

**Anchors**: Little's Law (01), Bufferbloat (08).

Scheduler iteration token budget, allocated KV pages, and pending request tokens are different resources. Output tokens enter the cache later than prompt tokens, so λ_tokens × request lifetime is not occupancy. Use the P2 page-time integral and allocator traces. Chunked prefill changes compute scheduling, not total retained prompt KV. Set admission and alerts from measured memory pressure, queue age, and TTFT/ITL quantiles; no universal percentage thresholds.

**Use for**: `--max-num-batched-tokens`, chunked prefill, long-context admission control, eviction spikes.

---

## Anti-Patterns

### A1 — Fixed Batch Size Under Variable Arrivals

A static batch target under-fills at low load and blocks at high load. Queued arrivals are not Erlang-B loss traffic; model waiting capacity explicitly. **Fix**: iteration-level continuous batching; set `max_num_seqs` as the KV-cache upper bound, not a target; monitor the batch-size distribution.

### A2 — FIFO Across Mixed Prompt Lengths

Under FIFO, every arrival waits out the residual service of the request in progress. The P-K mean residual is E[S]·(1 + CV²_s)/2 (see 04). Illustrative: at CV²_s = 8 it is 4.5 × E[S]. Short interactive requests then inherit the tail of the longest prompts, even at low load. **Fix**: length-bucketed lanes or size-based scheduling (see [R4](#r4--llm-serving-capacity-and-scheduling) step 1 and primitive 05). Prefer non-preemptive priority for prefill; mid-prefill preemption costs a KV swap or recompute.

### A3 — No Head-of-Line Protection

One 128k-token prompt at 100k tokens/s prefill occupies the server for 1.28 s. In a serial non-preemptive model, arrivals during that window wait its remaining portion; at 50 QPS that is about 64 arrivals. Real interleaving changes the number. **Fix**: per-tenant max prompt length, chunked prefill, pre-admission timeouts, token-level admission (P7).

### A4 — Ignoring Queue Depth in Autoscaler Triggers

GPU utilization saturates and reads high during prefill bursts at low load, so it both over- and under-reacts. Little's Law relates averages; it does not make queue depth a leading indicator by itself. **Fix**: add queue depth, queue age, and token-budget use as signals; calibrate triggers on measured TTFT quantiles, burst duration, and provisioning delay (GPU scale-out takes minutes; measure yours). Keep GPU utilization as secondary confirmation.

---

## Recipes

### R1 — Sizing a vLLM Cluster for a p99 Latency Target

1. **Measure.** Log per-request arrival, service start, first token, completion, prompt/output lengths, cancellations, and retries. Compute CV²_a and CV²_s from the samples. Measure saturated completed requests/s per replica for the real mix.
2. **Screen.** Under a pooled M/M/c abstraction, compute Erlang-C mean wait; in that exact model P(Wq > t) = C(c,a)·exp(−(cμ−λ)t). Correct for variability with Allen-Cunneen. The queue-wait quantile is not the TTFT quantile.
3. **Load-test.** Replay representative bursts and joint prompt/output distributions across candidates. Record queue wait, TTFT/TPOT p99 with uncertainty, SLO-goodput, rejections, and recovery.
4. **Return** the workload window, capacity definition, assumptions, candidate table, observed quantiles, headroom rationale, and autoscaler/admission settings. Name an observed passing candidate, not a theorem-guaranteed minimum.

### R2 — Tuning Continuous Batching for the Throughput-Cost Frontier

1. **Profile** for each batch limit b: completed requests/s, E[S(b)], CV²_s(b), eviction rate, memory use. Stop at measured memory or SLO failure.
2. **Frontier.** cost per request = 1 / throughput(b). Inspect the measured curve; concavity is not guaranteed.
3. **Screen then test.** Allen-Cunneen mean wait per b is a screen only. Larger b raises throughput and often CV²_s, so the throughput-optimal b may fail the TTFT SLO. Accept b only on measured TTFT/TPOT p99.
4. **Configure** `--max-num-seqs`, `--max-num-batched-tokens`, and chunked prefill from the measured table. Monitor batch-size histogram, KV usage, TTFT/TPOT p99, and queue depth against thresholds chosen from the load test.

### R3 — Reproducing Tail Latency in a Load Test

1. **Measure** inter-arrival times (CV²_a, autocorrelation), prompt and output lengths (joint), and time-of-day shape.
2. **Arrivals.** Prefer trace replay. For synthetic load with target CV²_a, use gamma inter-arrivals with shape = 1/CV²_a and scale = CV²_a/λ (mean 1/λ, CV² = CV²_a). Poisson load tests miss bursts.
3. **Lengths.** Resample empirical (prompt, output) pairs. A log-normal fit from p50/p99 (σ = (ln p99 − ln p50)/2.326) is a fallback that assumes the family.
4. **Validate.** Compare predicted and measured mean queue wait under matched assumptions; judge p99 TTFT separately. A large gap points to non-stationarity, KV evictions, or batch-composition effects. Matching variance can still miss autocorrelation and retry storms.
5. **Close the loop** with R1: if measured p99 TTFT fails the SLO at the chosen c, increase c or change admission and re-run.

### R4 — LLM Serving Capacity and Scheduling

Goal: size capacity and pick a scheduling policy for an LLM endpoint against TTFT/TPOT percentiles and SLO-goodput. Mean-Wq formulas cannot certify p99 TTFT; every step ends in measurement.

1. **Decode scheduling with unknown size (04, 05).** Decode service = output_tokens × time_per_token, unknown at arrival. Use prediction-augmented size-based scheduling. Trail (Shahout, Malach, Liu, Jiang, Yu & Mitzenmacher, arXiv 2410.01035, ICLR 2025) disables preemption once a request's age exceeds c × predicted size (0 ≤ c ≤ 1), because preempting old requests holds a large KV cache in memory. Plain SPRPT has no graceful-degradation guarantee under bad predictions; SPRPT-with-bounce and PSPJF do (Scully, Grosof & Mitzenmacher, ITCS 2022). Mitzenmacher & Shahout (Stochastic Systems 2025, arXiv 2503.07545) is a review of this area.
2. **Joint compute-and-memory stability (gates the rest).** Admitted requests hold KV memory that grows per decoded token and frees only at completion. A compute-side ρ < 1 does not imply stability when memory binds. Check the joint condition of Nie, Si & Zhou (ICML 2026, arXiv 2605.04595); their predicted stability conditions deviate from GPU measurements "typically within 10%". Size from the derived stable rate.
3. **Eviction limit cycles under saturation (05, 08).** Homogeneous output lengths synchronize completions and align memory peaks, giving an evict-and-restart cycle with "throughput losses as large as 50%" (Ao, Dong, Luo & Simchi-Levi, arXiv 2606.15555). Dispersed lengths desynchronize. Admit on projected peak KV occupancy over the remaining decode horizon, not instantaneous occupancy.
4. **Autoscaling (03).** For dynamic replica counts, SageServe (Jaiswal et al., POMACS 9(3), Dec 2025, presented at SIGMETRICS 2026) combines short-horizon routing with forecast-driven GPU scaling and reports up to 25% GPU-hour savings.
5. **Simulate before buying.** If tail instability, batching, memory coupling, or dependence makes the analytic model unreliable, pair analytic sizing with discrete-event simulation (inference-fleet-sim, arXiv 2603.16054; see [trace-driven-simulation.md](../../foundations-queueing-theory/references/trace-driven-simulation.md)). Analytic M/G/c alone mis-sizes split thresholds, GPU type, and utilization under heavy-tailed LLM workloads.

**Standout insight.** Two results answer different questions. Work conservation suffices for maximum throughput on a single engine and on DAG/fork-join agent topologies (Dai, Deng, Li & Peng, arXiv 2504.07347): Orca and Sarathi-Serve are throughput-optimal, while "FasterTransformer and vanilla vLLM are not maximally stable". Work conservation does not say how to tile prefill against decode. RAD (Bari, Hegde & de Veciana, arXiv 2508.01002) shows optimal tiling plus dynamic resource allocation are the binding design choices; its SLO-aware variant SLAI "reduces the median TTFT by 53% and increases the maximum serving capacity by 26%" versus Sarathi-Serve. Throughput-optimality is the floor; tiling and scheduling decide tail latency.

---

## Composition

| Start | Next |
|---|---|
| P1 continuous batching | Size with R1; check KV with P2 |
| P2 KV sizing | Joint stability and peak-occupancy admission (R4 steps 2–3); admission via P4 |
| P3 disaggregation | Needs measured ρ_p and ρ_d from P1 |
| P4 admission control | Screen with Erlang-C; tune on measured p99 TTFT and goodput |
| P6 multi-tenant | Per-tenant P4 admission and P1 tracking |
| P7 token backpressure | Feeds P4 |
| R1 sizing | Validated by R3; scheduling and autoscaling from R4 |
| R2 batch tuning | Uses R1 capacity; accepted only on measured p99 |

Guards: check A1 before throughput comparisons, A2 before p99 analysis, A4 before finalizing autoscaler config.

---

## Sources

- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Yu, G. et al. (2022). "Orca: A Distributed Serving System for Transformer-Based Generative Models." *OSDI 2022*.
- Kwon, W. et al. (2023). "Efficient Memory Management for Large Language Model Serving with PagedAttention." *SOSP 2023*.
- Agrawal, A. et al. (2024). "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve." *OSDI 2024*.
- Zheng, L. et al. (2024). "SGLang: Efficient Execution of Structured Language Model Programs." *NeurIPS 2024*.
- Shahout, Malach, Liu, Jiang, Yu & Mitzenmacher (2025). "Don't Stop Me Now: Embedding Based Scheduling for LLMs" (Trail). *ICLR 2025*; arXiv 2410.01035.
- Scully, Z., Grosof, I. & Mitzenmacher, M. (2022). "Uniform Bounds for Scheduling with Job Size Estimates." *ITCS 2022*.
- Mitzenmacher, M. & Shahout, R. (2025). "Queueing, Predictions, and Large Language Models: Challenges and Open Problems" (review). *Stochastic Systems* 15(3); arXiv 2503.07545.
- Dai, Deng, Li & Peng. "Throughput-Optimal Scheduling Algorithms for LLM Inference and AI Agents." arXiv 2504.07347.
- Bari, Hegde & de Veciana. "Optimal Scheduling Algorithms for LLM Inference: Theory and Practice" (RAD/SLAI). arXiv 2508.01002; *POMACS*, presented at SIGMETRICS 2026.
- Nie, Si & Zhou. "A Queueing-Theoretic Framework for Stability Analysis of LLM Inference with KV Cache Memory Constraints." *ICML 2026*, arXiv 2605.04595.
- Ao, Dong, Luo & Simchi-Levi. "Service-Induced Congestion in Memory-Constrained LLM Serving." arXiv 2606.15555.
- Jaiswal et al. "SageServe: Optimizing LLM Serving on Cloud Data Centers with Forecast Aware Auto-Scaling." *POMACS* 9(3), Dec 2025; SIGMETRICS 2026.
- inference-fleet-sim. arXiv 2603.16054.
- [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) — canonical primitives, formulas, and worked examples.
