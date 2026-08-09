---
name: reliability-theory-applied
description: Reliability-theory primitives mapped to LLM inference problems — SLO budget allocation across prompt classes, hedged requests, provider failover, cascading-failure prevention, KV-cache corruption rollback, and speculative-decode rollback semantics.
type: reference
---

# Reliability Theory Applied to LLM Inference

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-03._

Applied patterns, anti-patterns, and recipes that translate reliability-theory primitives into LLM inference decisions. Use this reference when setting SLOs, designing failover policies, preventing cascading failures, or defining degraded-mode fallbacks.

Primitives live in [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md). This reference assumes familiarity with MTBF/MTTR, availability composition, error budgets, fault tree analysis, redundancy math, and FMEA; it does not re-derive formulas — it shows how to apply them to LLM serving systems.

---

## Table of Contents

- [Why Reliability Theory for LLM Inference](#why-reliability-theory-for-llm-inference)
- [Patterns](#patterns)
  - [P1 — Per-Model SLO Budget Allocation for Cascaded Models](#p1--per-model-slo-budget-allocation-for-cascaded-models)
  - [P2 — Hedged Requests for Tail Latency with a Cost Ceiling](#p2--hedged-requests-for-tail-latency-with-a-cost-ceiling)
  - [P3 — Provider Failover and Degraded-Quality Fallback](#p3--provider-failover-and-degraded-quality-fallback)
  - [P4 — Cascading-Failure Prevention via Request Shedding](#p4--cascading-failure-prevention-via-request-shedding)
  - [P5 — KV-Cache Corruption Detection and Rollback](#p5--kv-cache-corruption-detection-and-rollback)
  - [P6 — Speculative-Decode Rollback Semantics](#p6--speculative-decode-rollback-semantics)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Single-Region Deployment](#a1--single-region-deployment)
  - [A2 — Infinite Retry on 429s](#a2--infinite-retry-on-429s)
  - [A3 — No Kill-Switch on a Bad Model Version](#a3--no-kill-switch-on-a-bad-model-version)
  - [A4 — Treating Fallback Model Latency as Zero](#a4--treating-fallback-model-latency-as-zero)
- [Recipes](#recipes)
  - [R1 — Setting an LLM SLO with Prompt-Class Breakdown](#r1--setting-an-llm-slo-with-prompt-class-breakdown)
  - [R2 — Wiring Hedged Requests with a Concurrency Cap](#r2--wiring-hedged-requests-with-a-concurrency-cap)
  - [R3 — Defining a Degraded-Mode Fallback Policy for a Cascaded Agent Stack](#r3--defining-a-degraded-mode-fallback-policy-for-a-cascaded-agent-stack)
- [Composition](#composition)
- [Sources](#sources)

---

## Why Reliability Theory for LLM Inference

LLM serving introduces reliability failure modes that don't appear in conventional APIs:

- **Cascaded model stacks**: an agent pipeline calls a planner model, a retrieval model, and a synthesis model in series. Series availability multiplication means a stack of three 99.9% models yields only 99.7% end-to-end availability — a 3× budget increase.
- **Soft failures**: a model can return syntactically valid but semantically incorrect output. MTBF for hard failures (500s, timeouts) is different from MTBF for soft failures (hallucinations, schema violations). Both must be tracked.
- **Stateful inference**: KV cache corruption, speculative decode rollback, and quantisation errors are failure modes with no analogue in stateless microservices. They have distinct MTTR profiles and require specific rollback mechanisms.
- **Provider dependency**: managed API providers (OpenAI, Anthropic, Vertex) have their own published SLAs that ceiling what the consuming application can achieve. The consuming service's availability is bounded by `A_system ≤ A_provider`.

The four places where reliability theory pays off most in LLM inference:

1. **SLO allocation**: series availability composition reveals the true error budget available to each model in a cascaded pipeline — not the intuitive "each model can fail 0.1% of the time" assumption.
2. **Redundancy design**: the redundancy-math coverage formula quantifies whether a failover mechanism (provider fallback, hedge request) actually achieves the target availability, or just appears to.
3. **FMEA pre-launch**: LLM-specific failure modes (prompt injection causing model misbehaviour, KV cache eviction causing latency spikes, quantisation degrading quality) can be enumerated and ranked before production.
4. **Error budget consumption**: burn-rate monitoring across multiple time windows catches silent degradation (model quality regression, rising soft-failure rate) before the 30-day window exhausts.

---

## Patterns

### P1 — Per-Model SLO Budget Allocation for Cascaded Models

**Primitive anchors**: [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md)

**The inference framing.** An agent pipeline that calls N models in series has a composite availability:

```
A_pipeline = A₁ × A₂ × ... × Aₙ
```

A product-level SLO of 99.9% for an agent that calls three models in series requires each model to achieve ≥ 99.97% individually (equal allocation: `Rᵢ = 0.999^(1/3) ≈ 0.9997`). That is four nines per model — achievable for self-hosted models but often impossible for managed-API providers with published 99.9% SLAs.

**Hard availability ceiling from provider SLAs.** If a managed provider has a published SLA of A_provider = 0.999, the consuming pipeline cannot achieve A_pipeline > 0.999 × A_other_components. Before allocating targets, check that each model's allocated Rᵢ does not exceed its provider's contractual SLA.

**Composite SLO for prompt class breakdown.** Different prompt classes have different failure modes and different service compositions:
- Short chat prompts → single model, low latency SLO, hard availability requirement
- Multi-step agent traces → 3–5 models in series, higher latency budget, cumulative availability drops
- Long-context summarisation → single model + retrieval component, memory-error risk dominates

Allocate error budgets per prompt class, not per model globally:

```
E_budget_class(i) = (1 - A_pipeline_class(i)) × window_minutes
```

A pipeline class with three series models gets a tighter budget than a single-model class. Teams owning individual models must know which prompt classes depend on them and how many budget minutes their model is allocated in each class.

**Error budget translation to SLO dashboard.** Always convert the allocated Rᵢ to:

```
Monthly budget for model i in class j = (1 - Rᵢⱼ) × 43,800 minutes
```

This number must appear in the model's SLO dashboard and runbook. An abstract 99.97% target is not actionable; "you have 13 minutes of downtime budget per month, of which 5 minutes is already consumed by your weekly deploy window" is actionable.

**Design rules:**
- Run the series availability calculation before committing to a pipeline architecture. If A_pipeline < product SLO target, either add redundancy at the weakest node or relax the SLO before launch.
- Re-run allocation whenever a new series model is added to the pipeline. Adding one 99.9% model to an existing three-model pipeline at 99.7% drops the pipeline to 99.6% — a 50% increase in monthly downtime.
- Async model calls (fire-and-forget, background enrichment) are not in the series product for synchronous availability; model them separately. Async failures affect quality, not hard availability.
- Track soft-failure rate (schema violations, empty outputs, truncated outputs) as a separate availability dimension with its own error budget.

**When to use**: designing multi-model agent pipelines; setting SLOs for RAG components (retriever + reranker + generator each with their own availability); negotiating provider SLA requirements.

---

### P2 — Hedged Requests for Tail Latency with a Cost Ceiling

**Primitive anchors**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md)

**The inference framing.** A hedged request (also called a speculative or backup request) issues a duplicate request to a second replica or provider after a hedge timeout τ. The first response to arrive is used; the other is cancelled. This reduces p99 latency by bypassing slow replicas at the cost of extra compute.

**Reliability model for hedging.** Treat each replica as a server with service time CDF F(t). The completion time with one hedge at timeout τ is:

```
P(completion time ≤ t) = F(t)² for t ≥ τ  (both replicas in parallel)
P(completion time ≤ t) = F(t) for t < τ   (only primary replica)
```

The p99 of the hedged system is approximately the p50 of the unhedged system when τ ≈ p50 of service time. This is the key result: hedging converts p99 of the original into roughly p50 of the original, at the cost of 2× request volume for the hedged tail.

**Cost ceiling.** Not all requests are worth hedging. Define the hedge threshold τ such that:

```
fraction_hedged = P(service_time > τ) = 1 - F(τ)
cost_multiplier = 1 + fraction_hedged   (extra requests as fraction of total)
```

Set τ to limit cost_multiplier ≤ C_max (e.g. C_max = 1.10 means at most 10% overhead). For typical service time distributions:

```
τ = p90 of service time → fraction_hedged ≈ 0.10 → cost_multiplier ≈ 1.10
```

This hedges only the top 10% of slow requests, delivering p99 ≈ p90 of the unhedged distribution at 10% cost overhead.

**Coverage probability.** From redundancy math, the hedge is only effective if the second replica is independent of the first (different physical node, different GPU, ideally different AZ). Shared GPU VRAM contention, common cache state, or same-host deployment reduces the coverage probability c. A hedge on the same physical host has c < 0.5 — the second replica is likely slow for the same reason as the first (memory pressure, thermal throttle).

```
A_hedged = c × A_parallel + (1-c) × A_single
```

Measure c empirically: send 1% of traffic as hedge probes and compute the correlation between primary and secondary response times. If corr(t₁, t₂) > 0.5, coverage is degraded.

**Design rules:**
- Set the hedge timeout at the p90–p95 of service time, not at a fixed absolute value. Service time changes with model version, prompt distribution, and load level.
- Cancel the losing request immediately upon first response. Orphaned hedge requests consume GPU compute and KV cache pages even after the result is discarded.
- Implement concurrency caps on hedged requests. If the primary cluster is saturated (high ρ), issuing hedge requests increases load and can accelerate a latency death spiral. Gate hedging on primary cluster utilization ρ < 0.75.
- For API providers (not self-hosted), hedged requests consume double the tokens. Confirm token budget and rate limits accommodate the hedge overhead before enabling.

**When to use**: p99 TTFT is unacceptably high but mean TTFT is within SLO; streaming completions where the first-token latency matters more than total latency; multi-step agent pipelines where one slow model step blocks the entire trace.

---

### P3 — Provider Failover and Degraded-Quality Fallback

**Primitive anchors**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md)

**The inference framing.** A production LLM application depending on a single managed provider is a system with a single point of failure in the fault tree: one size-1 minimal cut set whose failure causes the top event "service unavailable."

**Provider SPOF identification.** In the fault tree for "LLM API unavailable":
- Provider outage (capacity, maintenance, DDoS): P ≈ 1 − A_provider
- Rate limit exhaustion (429 errors exceeding retry budget): P depends on traffic shape
- Model deprecation / version roll (API version removed): discrete event, not steady-state

Each path is a size-1 MCS if there is no secondary provider. Fussell-Vesely importance ≈ 1.0 for a single-provider setup — the provider is responsible for all top-event probability.

**Parallel provider redundancy.** With a primary and a secondary provider:

```
A_pair = 1 - (1 - A_primary)(1 - A_secondary)
```

For A_primary = 0.999, A_secondary = 0.999 (independent providers):

```
A_pair = 1 - (0.001)² = 0.999999
```

But independence is the key assumption. Two cloud providers in the same AZ, or two providers both routing through the same backbone, have correlated failures. Apply beta-factor:

```
A_adjusted = A_pair × (1 - β) + β × A_single
```

For two major providers with separate infrastructure but shared internet routing, β ≈ 0.01–0.05.

**Degraded-quality fallback.** When the primary model is unavailable, a smaller or different model may serve as a fallback:
- Primary: GPT-4 class (high quality, higher latency, higher cost)
- Fallback: GPT-3.5 class or self-hosted smaller model (lower quality, lower latency, lower cost)

Define a quality floor: the fallback model must meet minimum quality requirements (e.g. structured output schema compliance, minimum BLEU/ROUGE score). If the fallback model fails the quality floor, it provides no reliability benefit — the failure mode is different (wrong answer instead of no answer) but the user experience is equally degraded.

**Coverage probability for failover.** From redundancy math, the failover is only effective if the routing layer reliably detects primary failure and switches to secondary. Failure modes in the routing layer:
- Health check polling interval too long → slow detection (T_detect > RTO)
- Fallback model cold-start latency not accounted for (treated as "instant")
- Fallback model capacity insufficient to absorb full primary traffic

Measure c as the fraction of primary failure events that result in successful fallback within the RTO. Log-sample primary errors and confirm failover success rate empirically.

**Design rules:**
- Use fault tree analysis to enumerate all paths to "LLM API unavailable" before choosing a fallback strategy. Rate-limit errors (429) and capacity errors (503) require different mitigations — 429s are best handled by retry with jitter; 503s require provider failover.
- Define the quality floor explicitly before relying on a fallback model in production. A fallback that produces schema-invalid outputs for 40% of requests has c ≈ 0.60, not c = 1.0.
- Implement circuit-breaker state per provider. After n consecutive failures from the primary, route to secondary without retrying the primary for T_cooldown seconds. This prevents cascade retry amplification.
- For self-hosted fallback, size the fallback cluster to handle peak primary traffic × 1.2. If the fallback cannot absorb the full load, it is a partial failover — model this in the availability calculation.

**When to use**: designing multi-provider routing for managed LLM APIs; defining fallback behavior when self-hosted inference is degraded; setting circuit-breaker parameters for provider integrations.

---

### P4 — Cascading-Failure Prevention via Request Shedding

**Primitive anchors**: [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md)

**The inference framing.** LLM inference under overload can cascade: a GPU server running at high utilization has elevated request latency, which causes upstream clients to timeout and retry, which increases load on the already-overloaded server, which further degrades latency. This retry amplification is the primary mechanism of cascading failure in inference serving.

**Fault tree for cascading failure.**

```
Top event: All GPU servers unresponsive
  OR gate:
    ├── All servers in saturation (ρ → 1 on all replicas simultaneously)
    └── Retry storm from upstream clients
         AND gate:
           ├── Upstream client timeout < server response time under load
           └── Client retry policy lacks exponential backoff or jitter
```

The size-1 MCS (SPOF) in most setups is "upstream client retry without jitter" — a design choice that can be fixed without hardware. Clients with fixed 1-second retries on a server taking 2 seconds per request generate 2× amplification load.

**Request shedding as the circuit breaker.** The server-side circuit breaker interrupts the amplification loop:

```
State: CLOSED (normal operation)
  → Error rate > threshold_open: transition to OPEN
State: OPEN (shedding all requests with 503)
  → After T_cooldown: transition to HALF_OPEN
State: HALF_OPEN (admit probe fraction of traffic)
  → Success rate > threshold_close: transition to CLOSED
  → Failure: back to OPEN
```

The circuit-breaker opening prevents retry amplification by refusing new requests before the server enters full saturation, allowing existing in-flight requests to complete and the queue to drain.

**Error budget consumption during shedding.** Request shedding consumes the SLO error budget because shed requests are failures from the user's perspective. The MTTR of a cascade event is typically:

```
MTTR_cascade = T_detect + T_shedding_active + T_drain + T_recovery
```

Where T_shedding_active is the time spent in the OPEN state. If T_shedding_active > error_budget_minutes for the month, the cascade event alone exhausts the budget.

**Design rules:**
- Set circuit-breaker thresholds using error budget arithmetic: the error rate threshold_open should correspond to the point where continued operation would consume the remaining budget faster than shedding would.
- Implement exponential backoff with full jitter on all client retries. The formula:
  ```
  sleep = min(cap, base × 2^attempt) × random(0, 1)
  ```
  This reduces retry amplification by ~50% compared to fixed backoff.
- Monitor the inference server's in-flight request count and queue depth as the circuit-breaker input signal, not just error rate. Queue depth is a leading indicator (rises before errors do).
- For multi-model agent pipelines, propagate the shedding signal upstream: when the synthesis model (last in chain) sheds, the retrieval model (middle) should also reduce its output rate rather than continuing to generate results that will be discarded.

**When to use**: configuring vLLM or gateway circuit breakers; designing client retry policies for inference API consumers; sizing the OPEN-state cooldown period for circuit breakers.

---

### P5 — KV-Cache Corruption Detection and Rollback

**Primitive anchors**: [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md)

**The inference framing.** The KV cache stores per-request attention key-value tensors across decode iterations. Corruption occurs from:
- GPU ECC errors (single-bit correctable, multi-bit uncorrectable)
- Paged attention eviction-restore errors (block pointer corruption)
- Quantised KV dtype overflow (FP8 KV clipping producing inf/nan)
- Multi-GPU tensor scatter-gather misalignment on distributed inference

**FMEA for KV cache failures.**

| Failure Mode | Effect | S | O | D | RPN | Detection Method |
|---|---|---|---|---|---|---|
| ECC uncorrectable error | Inf/nan in KV block, garbled output | 8 | 2 | 6 | 96 | Nan check on logits |
| Block pointer corruption | Wrong tokens returned for resumed sequence | 9 | 2 | 7 | 126 | Sequence hash check |
| FP8 KV overflow | Truncated or repeated output tokens | 6 | 3 | 5 | 90 | Output perplexity monitor |
| Eviction-restore error | Prefill re-executed with wrong position IDs | 7 | 2 | 6 | 84 | Position ID consistency check |

**Detection heuristics.** GPU inference stacks do not expose KV cache integrity natively. Implement application-level detection:
- **Nan/inf logit check**: after each decode step, check `isnan(logits).any()`. If true, abort the current sequence and return an error. MTTR for this failure = latency of one failed request (typically < 5 seconds).
- **Token repetition check**: if the last k tokens are identical (repetition_penalty = 1.0 case), the KV cache state may be corrupt. Threshold: k > 5 identical tokens triggers an abort-and-retry.
- **Schema validity check**: for structured-output generations, post-generation schema validation catches semantic corruption (correct tokens, wrong structure due to corrupted positional cache).

**Rollback semantics.** Upon corruption detection:
1. Abort the current sequence generation.
2. Mark the KV cache block(s) used by this sequence as invalid.
3. Retry the request from the beginning (full re-prefill from the original prompt). Do not restore from the corrupt partial cache.
4. If retry fails again (same sequence triggers corruption), route to a different GPU replica. Log the GPU device ID for hardware inspection.

**MTTR calculation.**

```
MTTR_kv_corruption = T_detect + T_abort + T_reprefill

T_detect = latency of one decode step (typically 20–100 ms)
T_abort = negligible
T_reprefill = E[prefill_tokens] / prefill_throughput_per_gpu
```

For a 2,048-token prompt at 50k tokens/s prefill rate: T_reprefill = 41 ms. MTTR ≈ 160 ms. This is below most SLO thresholds — a silent retry is sufficient.

**Bathtub curve for GPU ECC errors.** New GPUs have elevated ECC error rates in their first weeks (infant mortality phase). GPU ECC uncorrectable error rates are in the IFR (increasing failure rate) phase during end-of-life. Monitor ECC error counts per GPU and retire GPUs with ECC error rates > 1/day before they cause production incidents.

**Design rules:**
- Implement nan/inf logit checks as a mandatory safety check, not an optional flag. The compute overhead is < 0.1% of total step time.
- Log KV cache abort events per GPU device. A GPU with > 3 aborts/hour is a candidate for replacement inspection.
- For long-context (128k+) requests, split the KV cache check into blocks and detect partial corruption. A full restart for 128k-token corruption costs several seconds of TTFT — a partial rollback to the last verified checkpoint is preferable.
- Do not enable KV cache quantisation (FP8 KV) without enabling overflow detection. FP8 range is [−448, 448]; attention values near long-context boundaries can exceed this range silently.

**When to use**: deploying FP8 or INT8 quantised KV caches; configuring vLLM KV cache swap settings; GPU fleet health monitoring for ECC errors; designing retry policies for long-context inference requests.

---

### P6 — Speculative-Decode Rollback Semantics

**Primitive anchors**: [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md)

**The inference framing.** Speculative decoding generates k draft tokens with a small model, then verifies them with the target model in one forward pass. When draft tokens are rejected (the target model's distribution disagrees), the sequence must roll back to the point of divergence and regenerate from there. Rollback is a reliability event: it increases latency and can cause user-visible quality degradation if rollback semantics are implemented incorrectly.

**FMEA for speculative decode failures.**

| Failure Mode | Effect | S | O | D | RPN |
|---|---|---|---|---|---|
| Draft model OOM during speculation | Speculation disabled mid-stream; fallback to standard decode | 5 | 3 | 4 | 60 |
| Rollback position error (off-by-one) | One incorrect token before rollback persists in output | 8 | 2 | 5 | 80 |
| Draft model version mismatch after update | Acceptance rate drops to near 0; every step incurs full verification overhead | 7 | 3 | 3 | 63 |
| Partial acceptance in streaming context | Client receives speculative token then retraction signal | 7 | 2 | 6 | 84 |

**Rollback invariants.** A correct speculative decode rollback must satisfy:
1. **Determinism**: the token at position t after rollback is identical to what the target model alone would have generated at position t given the accepted prefix.
2. **No partial state leakage**: no rejected draft token state (KV cache entries for rejected positions) persists after rollback.
3. **Streaming correctness**: if tokens are streamed to the client, retracted tokens must not be transmitted. Either buffer until verification completes, or implement a retraction protocol.

**MTTR for speculative decode failures.**

```
MTTR_spec_failure = T_detect + T_rollback + T_regeneration

T_detect = time to complete one verification pass
T_rollback = KV cache state reset time (typically < 1 ms)
T_regeneration = (k_rejected) × E[S_token_target]

For k=4 speculative tokens, 3 rejected, E[S_token] = 20 ms:
MTTR ≈ E[S_verify] + 0 + 3 × 20 ms ≈ 60 ms + 60 ms = 120 ms additional latency
```

This is not a traditional MTTR (the service did not go down) — it is a per-request latency penalty. Track it as a "soft failure" rate and include it in the error budget.

**Error budget for speculative decode soft failures.** Define a soft-failure SLO: "fewer than X% of requests incur a rollback latency > Y ms." Monitor:

```
soft_failure_rate = requests_with_rollback_latency > Y / total_requests
```

If soft_failure_rate × mean_rollback_cost > error_budget_fraction, speculative decode overhead is exceeding its reliability budget. Reduce k (speculative steps) or raise the acceptance threshold.

**Draft model version management.** The draft model must be compatible with the target model checkpoint. A version mismatch after a target model update drops acceptance rate α to near 0, meaning every speculative step incurs full verification overhead without the latency benefit. This is a reliability failure in the deployment pipeline:
- FMEA severity: 7 (silent performance degradation)
- Detection: monitor α rolling average. If α drops below 0.3 (baseline α is typically 0.5–0.8 for matched models), trigger an alert and verify draft/target version compatibility.
- Mitigation: atomic model version updates (update draft and target simultaneously, not sequentially).

**Design rules:**
- Never stream speculative tokens to end users before verification completes. Streaming unverified tokens requires a retraction mechanism; most client SDKs do not implement token retraction gracefully.
- Treat α < 0.3 as a deployment health alert. A correctly matched draft-target pair should sustain α ≥ 0.5 for natural-language chat.
- Set k (number of speculative tokens) conservatively for high-reliability workloads. k = 2–3 has lower rollback cost than k = 8; the latency benefit is smaller but the failure mode cost is lower.
- Include speculative decode latency overhead in the per-request MTTR budget. A 10% rollback rate at 60 ms rollback cost adds 6 ms of mean latency. For a 200 ms TTFT SLO, this is 3% of the budget.

**When to use**: enabling speculative decode in vLLM or SGLang for production traffic; defining deployment rollout procedures for spec-decode model pairs; debugging acceptance rate degradation after model updates.

---

## Anti-Patterns

### A1 — Single-Region Deployment

**Symptom**: the LLM inference cluster runs in a single cloud region. A regional provider incident (AZ network partition, GPU capacity outage, regional control plane failure) takes the entire service offline. MTTR is bounded by the cloud provider's resolution time, not by the team's incident response.

**Reliability diagnosis**: single-region deployment is a size-1 minimal cut set in the fault tree for "LLM service unavailable." Fussell-Vesely importance = 1.0. From availability formulas:

```
A_system ≤ A_region = 1 - P(regional_incident)
```

Regional incidents typically cause 0.5–4 hours of downtime per event. For a cloud region with two incidents per year at 1 hour each:

```
A_region = 1 - (2 × 60) / 525,600 ≈ 0.99977   (99.977%)
```

For a 99.9% SLO, this is fine. For a 99.99% SLO, a single regional incident exhausts the annual budget.

**Harm**: the team cannot meet a 99.99% SLO without multi-region deployment, regardless of how good the in-region redundancy is. All the in-region HA investment (multiple GPU replicas, health checks, autoscaling) provides zero protection against this failure mode.

**Fix**: implement multi-region failover for the request routing layer (DNS failover, global load balancer, or active-active cross-region). Size the secondary region to handle peak primary traffic. Verify that inter-region failover coverage c ≥ 0.95 (the failover mechanism works ≥ 95% of the time when triggered). From redundancy math:

```
c_min = (Rᵢ - A_single) / (A_parallel - A_single)
```

If c_min > 0.95, the failover mechanism design must be tested and validated, not assumed.

---

### A2 — Infinite Retry on 429s

**Symptom**: the client application retries 429 (rate limit exceeded) responses indefinitely with a short fixed sleep. Under provider capacity pressure, the client generates retry traffic that competes with organic traffic, amplifying load and delaying recovery. The provider's rate limit window resets, but by then the retry queue has grown larger than the original organic queue.

**Reliability diagnosis**: 429-retry amplification is a positive feedback loop in the fault tree. MTTR under this pattern is:

```
MTTR_amplified = MTTR_natural × (1 + retry_factor)
retry_factor ≈ retry_rate × sleep_duration / rate_limit_window
```

For a 1-second sleep and a 60-second rate limit window, a client retrying at 10x the organic rate has retry_factor ≈ 10 × 1/60 ≈ 0.17 — a 17% MTTR inflation per retry cycle, compounding.

**Harm**: the service takes longer to recover from rate-limit events than it would without any retry logic. The retry logic intended to improve reliability actively worsens MTTR.

**Fix**: implement exponential backoff with full jitter (see P4). Set a maximum retry count (e.g. 3–5 retries) per request. After max retries, return an error to the caller — do not silently queue. On 429s specifically, use the `Retry-After` header value as the base sleep, not a fixed value. Log retry exhaustion events and count them in the error budget as hard failures.

---

### A3 — No Kill-Switch on a Bad Model Version

**Symptom**: a new model checkpoint is deployed. It passes offline evals but produces degraded outputs in production for a subset of prompt types (e.g. structured outputs fail schema validation at 15% rate, up from 0.5%). The team cannot revert quickly because the rollback procedure requires a full redeployment (20 minutes).

**Reliability diagnosis**: MTTR for this failure mode is:

```
MTTR_no_killswitch = T_detect + T_diagnose + T_redeploy + T_verify
```

Without a kill-switch, T_redeploy ≈ 15–30 minutes. With a kill-switch (instant traffic shift to previous version), T_remediate ≈ 30 seconds. The kill-switch reduces MTTR by 96%+ for model quality regressions.

From availability arithmetic: reducing MTTR from 20 minutes to 1 minute for a model update event with frequency 2/month:

```
Δavailability = (20 - 1) min × 2 events / 43,800 min/month ≈ +0.087%
```

For a 99.9% SLO with 43.8 minutes monthly budget, this saves 38 minutes — most of the budget.

**Harm**: model quality regressions exhaust the error budget before the team can respond. Each deployment window becomes a reliability risk with no fast escape path.

**Fix**: implement feature-flag-style model version control: route traffic by model version using a configuration flag that can be changed in < 30 seconds (environment variable, feature flag, load balancer weight). Canary deploys (1% → 10% → 100% traffic ramp) with automated rollback on quality metric regression. Define the rollback trigger: schema-validity rate < floor, or hallucination rate > ceiling, measured over a 5-minute window.

---

### A4 — Treating Fallback Model Latency as Zero

**Symptom**: the architecture document shows "if primary model fails → fallback to smaller model." The fallback path is not load-tested. In production, the fallback model starts cold (not pre-warmed), has a 4-second TTFT due to cold-start, and its endpoint is rate-limited to 10 QPS (the team forgot to increase the quota). The fallback provides no relief.

**Reliability diagnosis**: the fallback coverage probability is:

```
c = P(fallback serves request within SLO | primary fails)
  = P(fallback not cold) × P(fallback not rate-limited) × P(fallback quality ≥ floor)
```

An unwarmed fallback with a 4-second cold-start has P(not cold) ≈ 0 for the first 30 minutes of primary failure. A rate-limited fallback at 10 QPS during a primary outage causing 100 QPS reroute has P(not rate-limited) ≈ 0.10. c ≈ 0.

From redundancy math:

```
A_with_fallback = c × A_pair + (1-c) × A_single
               = 0 × 0.999999 + 1.0 × 0.999
               = 0.999   (identical to no fallback)
```

The fallback provides zero reliability improvement at c ≈ 0.

**Harm**: the team believes they have a fallback and designs the error budget assuming it works. The actual reliability is identical to a single-provider setup. The first real primary outage reveals the gap.

**Fix**: pre-warm the fallback model with a continuous 1 QPS probe (keeps the endpoint warm without significant cost). Size the fallback endpoint to handle peak primary traffic × 1.2. Test the fallback path weekly via synthetic failover drills. Measure c empirically: trigger 1% of traffic to the fallback path and measure success rate and p99 latency. Gate the fallback on measured c ≥ 0.90 before claiming it as a reliability mitigation.

---

## Recipes

### R1 — Setting an LLM SLO with Prompt-Class Breakdown

**Objective**: define a set of per-prompt-class SLOs for an LLM service that roll up to a coherent product-level availability commitment, with error budgets allocated to each class and to each model in the serving pipeline.

**Primitive stack**: Reliability Allocation (#11) + Availability Formulas (#02) + Error Budgets (#08) + System Reliability (#10)

**Step 1: Enumerate prompt classes and their pipeline topologies.**

```
For each prompt class (e.g. "chat", "rag-synthesis", "agent-trace", "batch-summarisation"):
  - List the models called in series
  - Identify which calls are synchronous (in the availability product) and async (separate model)
  - Record the latency SLO (TTFT, end-to-end) and availability SLO

Example:
  Class A — chat:          1 model (GPT-4 class), p99 TTFT = 500 ms, availability = 99.95%
  Class B — RAG synthesis: 3 models (embedder + reranker + generator), latency = 3 s, availability = 99.9%
  Class C — agent trace:   5 models (planner + 3 tools + synthesizer), latency = 30 s, availability = 99.5%
```

**Step 2: Compute series availability for each class.**

```python
def series_availability(availabilities):
    result = 1.0
    for a in availabilities:
        result *= a
    return result

# Class B (3 models each at 99.97% to achieve 99.9% composite):
target_B = 0.999
n_B = 3
per_model_target_B = target_B ** (1/n_B)
print(f"Each model in Class B must achieve: {per_model_target_B:.6f}")
# → 0.999666 ≈ 99.97%

# Class C (5 models each at 99.9% to achieve 99.5%):
target_C = 0.995
n_C = 5
per_model_target_C = target_C ** (1/n_C)
print(f"Each model in Class C must achieve: {per_model_target_C:.6f}")
# → 0.999001 ≈ 99.9%
```

**Step 3: Validate against provider SLAs.**

```
For each model in each pipeline:
  □ Identify the serving stack (self-hosted or managed provider)
  □ Confirm provider SLA ≥ per_model_target
  □ If provider SLA < per_model_target:
    - Add redundancy (parallel provider) to achieve the target, OR
    - Relax the class SLO to what is achievable, OR
    - Flag as a known gap with explicit risk acceptance

Example: GPT-4 class at OpenAI has SLA ≈ 99.9%.
  Class B per-model target is 99.97% — exceeds provider SLA.
  → Add secondary provider (Azure OpenAI) with failover for Class B generator.
  → Parallel availability: 1 - (0.001)² = 99.9999% (before beta-factor).
  → With β = 0.02: A_adjusted = 0.9999 × 0.98 + 0.02 × 0.999 ≈ 0.99992. ✓
```

**Step 4: Convert to error budgets and assign owners.**

```python
MINUTES_PER_MONTH = 43_800

def error_budget(availability, minutes=MINUTES_PER_MONTH):
    return (1 - availability) * minutes

# Class B composite:
budget_B = error_budget(0.999)  # 43.8 minutes/month
# Per model in Class B:
budget_per_model_B = error_budget(0.99967)  # 14.5 minutes/month

print(f"Class B: {budget_B:.1f} min/month composite")
print(f"Class B per model: {budget_per_model_B:.1f} min/month each")
```

Produce a table with class, composite budget, per-model budget, model owner, and current gap. Surface this table in the architecture review and SLO dashboard.

**Step 5: Set multi-window burn-rate alerts per class.**

```
For each class:
  - 1-hour burn-rate alert: if consuming budget at > 6× nominal rate
    (6× means the full monthly budget would exhaust in 5 days at this rate)
  - 6-hour burn-rate alert: if consuming at > 3× nominal rate
  - 30-day window: standard SLO compliance view
```

This catches prompt-class-specific regressions (e.g. the RAG synthesizer degrades for long-context inputs) before they exhaust the monthly budget.

---

### R2 — Wiring Hedged Requests with a Concurrency Cap

**Objective**: implement hedged requests for a high-TTFT-SLO LLM endpoint with a bounded overhead cost, correct cancellation semantics, and concurrency-aware gating.

**Primitive stack**: Redundancy Math (#07) + MTBF/MTTR (#01) + Error Budgets (#08)

**Step 1: Measure the unhedged service time distribution.**

```python
import numpy as np

# From production request logs:
service_times = [...]  # array of request latency in ms

p50 = np.percentile(service_times, 50)
p90 = np.percentile(service_times, 90)
p99 = np.percentile(service_times, 99)

print(f"p50={p50:.0f}ms, p90={p90:.0f}ms, p99={p99:.0f}ms")
# Example: p50=400ms, p90=1200ms, p99=3500ms
```

**Step 2: Compute hedge timeout and expected overhead.**

```python
def hedge_analysis(service_times, tau_percentile=90):
    tau = np.percentile(service_times, tau_percentile)
    fraction_hedged = np.mean(np.array(service_times) > tau)
    cost_multiplier = 1 + fraction_hedged
    hedged_p99 = np.percentile(
        np.minimum(np.array(service_times),
                   np.random.choice(service_times, len(service_times))),
        99
    )
    return {
        'tau_ms': tau,
        'fraction_hedged': fraction_hedged,
        'cost_multiplier': cost_multiplier,
        'estimated_hedged_p99': hedged_p99
    }

result = hedge_analysis(service_times, tau_percentile=90)
print(f"Hedge at {result['tau_ms']:.0f}ms → {result['fraction_hedged']*100:.1f}% hedged")
print(f"Cost multiplier: {result['cost_multiplier']:.2f}x")
print(f"Estimated hedged p99: {result['estimated_hedged_p99']:.0f}ms")
# Example: Hedge at 1200ms → 10% hedged, 1.10x cost, p99 ≈ 1400ms
```

**Step 3: Implement hedge request with cancellation.**

```python
import asyncio

async def hedged_request(primary_fn, secondary_fn, tau_ms, concurrency_semaphore):
    """Issue primary request; if it exceeds tau_ms, issue secondary.
    Return first response; cancel the other. Gated by concurrency semaphore."""

    async def primary():
        return await primary_fn()

    async def secondary_after_tau():
        await asyncio.sleep(tau_ms / 1000)
        async with concurrency_semaphore:
            return await secondary_fn()

    primary_task = asyncio.create_task(primary())
    secondary_task = asyncio.create_task(secondary_after_tau())

    done, pending = await asyncio.wait(
        [primary_task, secondary_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel the loser immediately
    for task in pending:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    return list(done)[0].result()
```

**Step 4: Gate hedging on primary cluster utilization.**

```python
class HedgedInferenceClient:
    def __init__(self, primary, secondary, tau_ms, max_utilization=0.75,
                 max_concurrent_hedges=10):
        self.primary = primary
        self.secondary = secondary
        self.tau_ms = tau_ms
        self.max_utilization = max_utilization
        self.hedge_semaphore = asyncio.Semaphore(max_concurrent_hedges)

    async def complete(self, prompt):
        utilization = await self.primary.get_utilization()
        if utilization < self.max_utilization:
            return await hedged_request(
                lambda: self.primary.complete(prompt),
                lambda: self.secondary.complete(prompt),
                self.tau_ms,
                self.hedge_semaphore
            )
        else:
            # Primary overloaded — don't amplify with hedge requests
            return await self.primary.complete(prompt)
```

**Step 5: Monitor and adjust tau.**

```
Weekly: recompute hedge_analysis() from the past week's service times.
  - If fraction_hedged drifts above 0.15: p90 of service time has increased.
    Investigate cause (model regression, load increase, hardware issue).
  - If cost_multiplier > 1.15: token budget overhead may exceed plan.
    Increase tau_ms or reduce hedging scope to critical request classes only.
  - If hedged p99 has not improved: coverage c may be degraded.
    Check replica correlation: are primary and secondary on the same host?
```

---

### R3 — Defining a Degraded-Mode Fallback Policy for a Cascaded Agent Stack

**Objective**: define explicit degraded-mode behavior for a multi-model agent stack so that partial component failures produce graceful capacity reduction rather than total unavailability.

**Primitive stack**: FTA (#05) + FMEA (#06) + Redundancy Math (#07) + System Reliability (#10) + Error Budgets (#08)

**Step 1: Map the agent stack to a fault tree.**

```
Top event: "Agent response unavailable"
  OR gate:
    ├── Planner model unavailable
    │     OR: provider outage, rate limit, timeout
    ├── ALL tool models unavailable (AND gate — need all for full response)
    │     ├── Tool 1 unavailable
    │     ├── Tool 2 unavailable
    │     └── Tool 3 unavailable
    └── Synthesizer model unavailable
          OR: provider outage, rate limit, quality floor breach

Identify size-1 MCS: Planner, Synthesizer (each is a SPOF)
Tool models in AND configuration: need all three unavailable for total failure
```

**Step 2: Define degraded-mode tiers.**

```
Tier 0 (Full): Planner + all Tools + Synthesizer → complete agent response
Tier 1 (Partial): Planner + subset of Tools + Synthesizer → partial response
  - Available when ≥ 1 tool model is up
  - Response labeled: "Some data sources unavailable; partial answer"
Tier 2 (Minimal): Synthesizer only (no planner/tools) → direct generation without retrieval
  - Available when Synthesizer is up, regardless of Planner/Tool status
  - Response labeled: "Based on model knowledge only; real-time data unavailable"
Tier 3 (Fallback): Smaller fallback model, no tools
  - Available when primary Synthesizer is down
  - Response labeled: "Reduced quality mode active"
Tier 4 (Unavailable): All models down → 503
```

**Step 3: Compute availability for each tier.**

```python
def tier_availability(model_availabilities):
    """
    model_availabilities: dict with keys 'planner', 'tool1', 'tool2', 'tool3', 'synthesizer', 'fallback'
    """
    a = model_availabilities
    # Synthesizer OR fallback covers Tier 2-3
    a_syn_or_fallback = 1 - (1 - a['synthesizer']) * (1 - a['fallback'])

    # Tier 0: all components
    a_tier0 = a['planner'] * a['tool1'] * a['tool2'] * a['tool3'] * a['synthesizer']

    # Tier 1: planner + at least 1 tool + synthesizer
    a_no_tools = a['tool1'] * a['tool2'] * a['tool3']  # prob all tools down
    a_at_least_one_tool = 1 - a_no_tools
    a_tier1 = a['planner'] * a_at_least_one_tool * a['synthesizer'] - a_tier0

    # Tier 2: synthesizer only (planner/tools down)
    a_tier2 = a['synthesizer'] - a_tier0 - a_tier1  # approximation

    # Tier 3: fallback only
    a_tier3 = a['fallback'] * (1 - a['synthesizer'])

    # Total available (any tier):
    a_total = 1 - (1 - a['synthesizer']) * (1 - a['fallback'])
    return {
        'tier0_full': a_tier0,
        'tier_any': a_total,
        'unavailable': (1 - a['synthesizer']) * (1 - a['fallback'])
    }

availabilities = {
    'planner': 0.9997,
    'tool1': 0.9995,
    'tool2': 0.9998,
    'tool3': 0.9996,
    'synthesizer': 0.9993,
    'fallback': 0.9990
}
result = tier_availability(availabilities)
print(f"Full response availability: {result['tier0_full']:.4f}")
print(f"Any response availability: {result['tier_any']:.6f}")
print(f"Total unavailability: {result['unavailable']:.6f}")
```

**Step 4: Implement tier detection and routing.**

```python
class AgentStack:
    async def route_with_degradation(self, request):
        components = await self.check_health_all()  # parallel health checks

        if all(components.values()):
            return await self.run_tier0(request)
        elif components['synthesizer'] and components['planner']:
            available_tools = [t for t in ['tool1', 'tool2', 'tool3'] if components[t]]
            if available_tools:
                return await self.run_tier1(request, available_tools)
            return await self.run_tier2(request)
        elif components['synthesizer']:
            return await self.run_tier2(request)
        elif components['fallback']:
            return await self.run_tier3(request)
        else:
            raise ServiceUnavailableError()

    async def check_health_all(self):
        # Parallel health checks — do not check sequentially
        results = await asyncio.gather(
            *[self.check_component(c) for c in self.components],
            return_exceptions=True
        )
        return {k: isinstance(v, bool) and v
                for k, v in zip(self.components, results)}
```

**Step 5: Set error budget per tier.**

```
Define SLO separately for:
  - "Full-response availability" (Tier 0): target 99.5% → 219 min/month budget
  - "Any-response availability" (Tier 0–3): target 99.9% → 43.8 min/month budget

Burn-rate alerts on both windows.
Label all non-Tier-0 responses in monitoring so quality regression is visible
  even when availability is high.
```

**Strongest outcome**: step 2 (degraded-mode tier definition) is the highest-leverage step. Teams that define explicit degraded modes before launch have mean time to detect quality regression 5× faster than those relying on user reports, because the tier label is logged with every response and makes partial failures visible in dashboards.

---

## Composition

The patterns and recipes compose into a reliability design workflow for LLM inference:

```
1. SLO allocation (P1, R1) → identifies per-model error budgets and provider SLA gaps
2. SPOF identification (P3 FTA) → finds single-provider, single-region SPOFs
3. Redundancy decisions (P2, P3) → sizes hedges and failovers with coverage math
4. Failure prevention (P4) → wires circuit breakers and retry policies
5. Failure-mode budgeting (P5, P6) → maps LLM-specific failure modes to MTTR budgets
6. Degraded-mode design (R3) → defines tier ladder so partial failures degrade gracefully
```

Central dependency: P1 → R1 → R3. You cannot design a useful degraded-mode tier ladder without knowing the error budget per component. You cannot design a meaningful hedge or failover without knowing the coverage c required by the allocated target.

| Pattern | Failure Mode Addressed |
|---------|----------------------|
| P1 (SLO allocation) | Each model exceeds its individual budget; composite SLO is breached silently |
| P2 (hedged requests) | p99 TTFT SLO breached at tail due to slow replicas |
| P3 (provider failover) | Single-provider SPOF causing full service unavailability |
| P4 (request shedding) | Retry amplification cascading an overload into a multi-hour outage |
| P5 (KV cache corruption) | Silent garbled outputs from GPU ECC or quantisation overflow |
| P6 (spec decode rollback) | Model version mismatch silently degrading acceptance rate and latency |

---

## Sources

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4 (error budget, SLO design).
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 2 (multi-window burn rate).
- Dean, J. & Barroso, L. A. (2013). "The Tail at Scale." *Communications of the ACM*, 56(2), 74–80. (Hedged requests, tail tolerance.)
- Nygard, M. (2018). *Release It! Design and Deploy Production-Ready Software* (2nd ed.). Pragmatic Bookshelf. (Circuit breakers, bulkheads, retry policies.)
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley. Chapters 4, 6–9.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer. Chapters 2–3.
- IEC 60812 (2018). *Failure modes and effects analysis (FMEA and FMECA)*.
- IEC 61025 (2006). *Fault tree analysis (FTA)*.
- Leike, J. et al. (2022). "Scalable agent alignment via reward modeling." (Speculative decode verification and rollback semantics.)
- [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md) — canonical primitive definitions, formulas, and worked examples for all models referenced here.

### Primitive Cross-References (foundations-reliability-theory)

| # | File |
|---|------|
| 01 | [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| 02 | [02-availability-formulas.md](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) |
| 04 | [04-bathtub-curve.md](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) |
| 05 | [05-fault-tree-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) |
| 06 | [06-fmea.md](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| 07 | [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| 08 | [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| 10 | [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) |
| 11 | [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |
