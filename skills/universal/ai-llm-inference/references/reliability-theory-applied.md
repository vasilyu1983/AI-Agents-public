---
name: reliability-theory-applied
description: Reliability-theory primitives mapped to LLM inference problems — SLO budget allocation across prompt classes, hedged requests, provider failover, cascading-failure prevention, KV-cache corruption rollback, and speculative-decode rollback semantics.
type: reference
---

# Reliability Theory Applied to LLM Inference

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

Link adapter: this file keeps only the LLM-serving decisions, thresholds, pitfalls, and worked examples. Definitions and formulas (MTBF/MTTR, series/parallel availability, imperfect coverage, beta-factor common cause, FTA, FMEA, error budgets, burn rate) live in [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md); validation discipline in [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md); agent-pipeline reliability in [ai-agent-reliability.md](../../foundations-reliability-theory/references/ai-agent-reliability.md). SLO design and alert implementation are owned by [qa-observability slo-design-guide.md](../../qa-observability/references/slo-design-guide.md).

Budget minutes below use the **average calendar month = 43,800 min** (8,760 h / 12). A 30-day window is 43,200 min and a 28-day window 40,320 min; make the window a parameter and label it.

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

LLM serving adds failure modes conventional APIs lack:

- **Cascaded model stacks**: planner → retrieval → synthesis in series. Three 99.9% models give 0.999³ ≈ 99.70% end to end — three times the unavailability of one model.
- **Soft failures**: valid-looking but wrong output (hallucination, schema violation, truncation). Track them as a separate availability dimension from hard failures (5xx, timeouts).
- **Stateful inference**: KV-cache corruption, speculative-decode rollback, and quantisation overflow have no stateless-microservice analogue and need their own rollback mechanics.
- **Provider dependency**: a managed provider's SLA caps what the consuming service can reach without redundancy (`A_system ≤ A_provider` for a series dependency).

Payoff points: SLO allocation across cascaded models (P1, R1), redundancy that actually covers (P2, P3, A4), pre-launch FMEA of LLM-specific modes (P5, P6), and multi-window burn-rate alerting per prompt class (R1 step 5).

---

## Patterns

### P1 — Per-Model SLO Budget Allocation for Cascaded Models

**Theory**: series composition and equal/weighted allocation → [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

**Inference decision.** A 99.9% product SLO over three synchronous models needs each at ≈ 99.967% under equal allocation (`0.999^(1/3) = 0.999667`) — above a managed provider's typical 99.9% SLA. Check each allocated Rᵢ against its provider's contractual SLA before committing the architecture.

**Allocate per prompt class, not per model globally.** Classes differ in composition:
- Short chat → single model, tight latency SLO, hard availability requirement.
- Multi-step agent trace → 3–5 models in series; cumulative availability drops.
- Long-context summarisation → model + retrieval; memory-error risk dominates.

Model owners must know which classes depend on them and how many budget minutes they hold in each. Put minutes, not percentages, on the dashboard: 99.97% ≈ 13 min per average month — "13 minutes, 5 already spent by the weekly deploy window" is actionable; "99.97%" is not.

**Design rules:**
- Run the series calculation before committing the pipeline; if A_pipeline < product SLO, add redundancy at the weakest node or relax the SLO pre-launch.
- Re-run allocation on every added series model. A fourth 99.9% model takes 99.70% → 99.60%, ≈ 33% more monthly downtime (0.399% vs 0.300% unavailability).
- Async calls (fire-and-forget enrichment) are outside the synchronous series product; they affect quality, not hard availability.
- Give soft-failure rate its own budget.

**When to use**: multi-model agent pipelines; RAG components (retriever + reranker + generator); provider SLA negotiation.

---

### P2 — Hedged Requests for Tail Latency with a Cost Ceiling

**Theory**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) (redundancy, coverage, common cause); Dean & Barroso (2013) for tail tolerance.

**Inference decision.** Issue a duplicate request after hedge timeout τ; use the first response and cancel the other. With independent, identically distributed replicas and a *delayed* hedge, `P(T ≤ t) = 1 − (1−F(t))(1−F(t−τ))` for t ≥ τ and `F(t)` before τ. With *simultaneous* independent duplicates, the combined p99 equals the single-replica p90 (`(1−F)² = 0.01 ⇒ F = 0.9`). There is no universal p99-to-p50 conversion; shared hosts, providers, caches, and queues correlate delays, so measure paired tail events on representative traces.

**Cost ceiling.** `fraction_hedged = 1 − F(τ)`; request-count multiplier = `1 + fraction_hedged`. τ at p90 bounds extra *requests* at ≈ 10% for an unchanged distribution — not extra tokens or compute, and not a guaranteed quantile gain.

**Design rules:**
- Set τ at p90–p95 of measured service time, recomputed as model version, prompt mix, and load change — never a fixed absolute value.
- Hedge only safe/idempotent operations. Cancel the loser immediately; orphaned hedges hold GPU compute and KV pages. Cancellation may not stop provider-side compute or billing.
- Cap duplicate concurrency and gate on tested spare capacity: hedging a saturated cluster raises load and can start a latency death spiral.
- On managed APIs a hedge can double tokens for the hedged fraction; confirm token budget and rate limits first.

**When to use**: p99 TTFT out of SLO while mean is fine; streaming where first-token latency dominates; agent traces blocked by one slow step.

---

### P3 — Provider Failover and Degraded-Quality Fallback

**Theory**: parallel availability, imperfect coverage, beta-factor → [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md); minimal cut sets and importance → [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md); ranking → [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md).

**Inference decision.** A single managed provider is a size-1 minimal cut set for "LLM API unavailable" (Fussell-Vesely importance ≈ 1.0). Paths to enumerate:
- Provider outage (capacity, maintenance, DDoS): P ≈ 1 − A_provider.
- Rate-limit exhaustion (429s beyond retry budget): depends on traffic shape.
- Model deprecation / API version removal: a discrete event, not steady state.

Two independent 99.9% providers give 1 − 0.001² = 0.999999 on paper. Providers sharing a region, backbone, or upstream model host are not independent; apply a common-cause adjustment (foundation 07). Any β you use (e.g. 0.01–0.05) is a local planning assumption, not a measured value — state it as such.

**Degraded-quality fallback.** A smaller/cheaper model as fallback only counts if it meets an explicit quality floor (schema compliance, task-specific eval score). Below the floor it converts "no answer" into "wrong answer" and adds no reliability.

**Coverage c for failover** = fraction of primary failures that end in a successful fallback within the RTO. LLM-specific coverage killers:
- Health-check interval longer than the RTO (slow detection).
- Fallback cold start treated as instant.
- Fallback quota/capacity below full primary traffic.

Measure c empirically; see the trial-count guidance in foundation 07 (ten successes cannot validate a high c).

**Design rules:**
- Separate 429 and 503 paths in the fault tree: 429 → bounded retry honouring `Retry-After`; 503/outage → provider failover.
- A fallback that fails schema validation on 40% of requests has c ≈ 0.60, not 1.0.
- Per-provider circuit breaker: after n consecutive primary failures, route to secondary for T_cooldown without retrying primary.
- Size self-hosted fallback for peak primary traffic with headroom (e.g. ×1.2, local choice); otherwise model it as partial failover.

**When to use**: multi-provider routing; self-hosted degradation fallback; provider circuit-breaker parameters.

---

### P4 — Cascading-Failure Prevention via Request Shedding

**Theory**: FTA gates and cut sets → [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md); budget arithmetic → [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md); circuit-breaker and bulkhead patterns → Nygard (2018).

**Inference decision.** Overloaded GPU servers raise latency → clients time out and retry → load rises further. Retry amplification is the primary cascade mechanism.

```
Top event: All GPU servers unresponsive
  OR
    ├── All replicas saturated (ρ → 1 simultaneously)
    └── Retry storm
         AND
           ├── Client timeout < server response time under load
           └── Client retries lack backoff/jitter
```

The cheapest cut is the client retry policy: a client that times out at 1 s against a 2 s response keeps roughly two attempts in flight per request.

**Shedding consumes budget.** Shed requests are failures to the user. `MTTR_cascade = T_detect + T_shedding_active + T_drain + T_recovery`; if time in OPEN state exceeds the remaining budget, one cascade exhausts it.

**Design rules:**
- Set the breaker's open threshold from budget arithmetic: open when continuing would burn the remaining budget faster than shedding.
- Exponential backoff with full jitter on all clients: `sleep = random(0, min(cap, base × 2^attempt))`, bounded attempts.
- Use in-flight count and queue depth as breaker inputs — queue depth rises before errors do.
- In multi-model pipelines, propagate shedding upstream so earlier stages stop producing work the last stage will discard.

**When to use**: vLLM or gateway circuit breakers; client retry policy for inference consumers; OPEN-state cooldown sizing.

---

### P5 — KV-Cache Corruption Detection and Rollback

**Theory**: [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md).

**Corruption sources**: GPU ECC errors (uncorrectable multi-bit); paged-attention eviction/restore (block-pointer corruption); FP8 KV overflow (inf/nan); tensor-parallel scatter/gather misalignment.

**Illustrative FMEA** (scores are examples to calibrate locally):

| Failure Mode | Effect | S | O | D | RPN | Detection |
|---|---|---|---|---|---|---|
| ECC uncorrectable error | Inf/nan in KV block, garbled output | 8 | 2 | 6 | 96 | NaN check on logits |
| Block pointer corruption | Wrong tokens for resumed sequence | 9 | 2 | 7 | 126 | Sequence hash check |
| FP8 KV overflow | Truncated or repeated tokens | 6 | 3 | 5 | 90 | Output perplexity monitor |
| Eviction-restore error | Re-prefill with wrong position IDs | 7 | 2 | 6 | 84 | Position-ID consistency check |

Do not rank by RPN alone: review every S ≥ 9 item (block-pointer corruption here) on its own merits, independent of RPN (foundation 06).

**Detection** (stacks do not expose KV integrity natively):
- NaN/inf logit check after each decode step → abort the sequence. Per-request abort latency is not service MTTR; measure detection and restoration separately.
- Repeated-token run (e.g. > 5 identical tokens with repetition penalty 1.0) → abort and retry; tune the threshold on your traffic.
- Post-generation schema validation for structured output catches structurally corrupted results.

**Rollback**: abort → mark the sequence's KV blocks invalid → full re-prefill from the original prompt (never resume from corrupt cache) → on repeat failure, route to another replica and log the GPU device ID.

**Worked example**: `MTTR_kv = T_detect + T_abort + T_reprefill`; a 2,048-token prompt at 50k tokens/s prefill gives T_reprefill ≈ 41 ms. A ~160 ms component sum is illustrative, not a validated recovery guarantee.

**Bathtub**: ECC error rates are elevated early (infant mortality) and rise again at end of life. Track ECC counts and abort events per GPU and set retirement/inspection thresholds from your fleet baseline (e.g. > 1 uncorrectable/day or > 3 aborts/hour are local starting points, not standards).

**Design rules:**
- Make the NaN/inf check mandatory; its cost is small relative to a decode step (measure on your stack).
- For 128k+ contexts, a full restart costs seconds of TTFT; prefer block-level checks and rollback to the last verified checkpoint.
- Never enable FP8 KV without overflow detection: FP8 E4M3 saturates at ±448, and long-context attention values can exceed it silently.

**When to use**: FP8/INT8 KV caches; vLLM KV swap settings; GPU fleet ECC monitoring; long-context retry policy.

---

### P6 — Speculative-Decode Rollback Semantics

**Theory**: [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md). Method: Leviathan et al. (2023); Chen et al. (2023).

**Inference decision.** A draft model proposes k tokens; the target verifies them in one pass; rejected tokens roll back to the divergence point. Rollback is a latency event, and an incorrectly implemented rollback is a correctness event.

**Illustrative FMEA:**

| Failure Mode | Effect | S | O | D | RPN |
|---|---|---|---|---|---|
| Draft model OOM during speculation | Falls back to standard decode mid-stream | 5 | 3 | 4 | 60 |
| Rollback position off-by-one | One wrong token persists in output | 8 | 2 | 5 | 80 |
| Draft/target version mismatch after update | Acceptance α collapses; full verify overhead every step | 7 | 3 | 3 | 63 |
| Partial acceptance while streaming | Client receives a token later retracted | 7 | 2 | 6 | 84 |

**Rollback invariants:**
1. **Determinism** — after rollback, position t equals what the target alone would produce given the accepted prefix (the lossless guarantee of speculative sampling).
2. **No state leakage** — no KV entries for rejected positions survive.
3. **Streaming correctness** — never transmit unverified tokens, or implement an explicit retraction protocol.

**Worked example (per-request penalty, not outage MTTR)**: k = 4, 3 rejected, E[S_token] = 20 ms, assumed verify pass 60 ms → ≈ 60 + 3×20 = 120 ms extra. At a 10% rollback rate with 60 ms mean cost, mean latency rises 6 ms — 3% of a 200 ms TTFT SLO. Budget it as a soft-failure SLO: "< X% of requests incur rollback latency > Y ms"; if exceeded, reduce k.

**Design rules:**
- Do not stream speculative tokens before verification; most client SDKs do not handle retraction.
- Alert on a drop in rolling α relative to the matched pair's measured baseline (baseline varies by model pair and task — measure it; a fixed threshold like 0.3 is a local choice). Verify draft/target compatibility on alert.
- Update draft and target atomically.
- Prefer small k (2–3) for high-reliability workloads: lower rollback cost, smaller speedup.

**When to use**: enabling speculative decode in vLLM/SGLang; spec-decode rollout procedures; debugging α degradation after model updates.

---

## Anti-Patterns

### A1 — Single-Region Deployment

**Symptom**: one cloud region; a regional incident (AZ partition, GPU capacity outage, control-plane failure) takes the service down, and MTTR is the provider's, not yours.

**Diagnosis**: size-1 cut set (foundation 05). Worked example: two 1-hour regional incidents/year → A_region = 1 − 120/525,600 ≈ 99.977%. Fine for 99.9%; for 99.99% the annual budget is 52.6 min, so one such incident exhausts it.

**Harm**: in-region HA (replicas, health checks, autoscaling) gives zero protection against this mode.

**Fix**: multi-region routing (DNS failover, global LB, or active-active), secondary sized for peak. Derive the required coverage with the foundation's c_min formula (07) and validate it with failover drills rather than assuming it.

---

### A2 — Infinite Retry on 429s

**Symptom**: 429s retried indefinitely with a short fixed sleep; retry traffic competes with organic traffic and the backlog outgrows the original queue.

**Diagnosis**: measure organic vs retry arrivals, admitted throughput, rejections, queue age, and recovery time under bounded retry. No general MTTR multiplier follows from retry rate, sleep, and limit-window length.

**Harm**: retry logic meant to improve reliability lengthens recovery.

**Fix**: exponential backoff with full jitter (P4); cap attempts (e.g. 3–5); use `Retry-After` as the base delay; after the cap, return an error — never silently queue; count retry exhaustion as a hard failure in the budget.

---

### A3 — No Kill-Switch on a Bad Model Version

**Symptom**: a checkpoint passes offline evals but fails in production for some prompt types (e.g. schema failures 0.5% → 15%); rollback needs a ~20-minute redeploy.

**Diagnosis**: `MTTR = T_detect + T_diagnose + T_remediate + T_verify`. Worked example (illustrative durations): cutting remediation from 20 min to 1 min for 2 events/month saves 38 min ≈ 0.087% of an average month — most of a 99.9% SLO's 43.8-min budget.

**Fix**: route by model version through a config flag/LB weight changeable in seconds; canary 1% → 10% → 100% with automated rollback when schema-validity or hallucination-rate thresholds are breached over a short window (e.g. 5 min). Validate actual rollback time.

---

### A4 — Treating Fallback Model Latency as Zero

**Symptom**: "primary fails → fallback model" is on the diagram but never load-tested; in production the fallback is cold (seconds of TTFT) and quota-limited far below rerouted traffic.

**Diagnosis**: `c = P(fallback serves within SLO | primary fails)`, roughly P(warm) × P(not rate-limited) × P(quality ≥ floor). Worked example: 10 QPS quota against 100 QPS rerouted → ~0.10 admitted; cold for the early window → c ≈ 0. With imperfect coverage (foundation 07), `A = c·A_pair + (1−c)·A_single` → at c ≈ 0, A = 0.999: identical to having no fallback.

**Harm**: the budget assumes a fallback that does not exist; the first real outage reveals it.

**Fix**: keep the fallback warm with a low-rate probe; size quota and capacity for peak primary traffic; run scheduled failover drills; route a small traffic slice to the fallback to measure success rate and p99; claim the mitigation only once measured c meets the target the allocation requires.

---

## Recipes

### R1 — Setting an LLM SLO with Prompt-Class Breakdown

**Objective**: per-prompt-class SLOs that roll up to a coherent product commitment, with budgets per class and per model. Theory: 02, 08, 10, 11.

**Step 1 — Enumerate classes and synchronous topologies** (example targets, set your own):

```
Class A — chat:          1 model,                             p99 TTFT 500 ms, availability 99.95%
Class B — RAG synthesis: 3 models (embedder, reranker, gen),  latency 3 s,     availability 99.9%
Class C — agent trace:   5 models (planner, 3 tools, synth),  latency 30 s,    availability 99.5%
```

**Step 2 — Per-model targets (equal allocation):**

```python
for name, target, n in [("B", 0.999, 3), ("C", 0.995, 5)]:
    print(name, round(target ** (1 / n), 6))
# B 0.999667  (≈ 99.967%)
# C 0.998998  (≈ 99.90%)
```

**Step 3 — Validate against provider SLAs.** If a provider's SLA is below the per-model target: add a parallel provider, relax the class SLO, or record an explicit risk acceptance. Worked example for Class B's generator on a 99.9%-SLA provider: two providers → 0.999999 independent; with an assumed β = 0.02 common-cause share, `0.999999 × 0.98 + 0.02 × 0.999 ≈ 0.99998` ≥ 0.99967 ✓ (β is an assumption — see P3).

**Step 4 — Budgets and owners** (window as a parameter):

```python
AVG_MONTH_MIN = 43_800   # 8,760 h / 12; use 43_200 for a 30-day window, 40_320 for 28 days

def budget_min(availability, window_min=AVG_MONTH_MIN):
    return (1 - availability) * window_min

budget_min(0.999)     # 43.8  (Class B composite)
budget_min(0.99967)   # 14.5  (each Class B model)
```

Publish a table of class, composite budget, per-model budget, owner, and current gap in the architecture review and SLO dashboard.

**Step 5 — Multi-window burn-rate alerts per class.** Use SRE Workbook ch. 5, Table 5-8 (99.9% SLO, 30-day period); alert only when **both** windows exceed the burn rate. Burn rate = error rate / (1 − SLO); budget consumed = burn rate × long window / period.

| Severity | Long window | Short window | Burn rate | Budget consumed |
|---|---|---|---|---|
| Page | 1 h | 5 min | 14.4 | 2% |
| Page | 6 h | 30 min | 6 | 5% |
| Ticket | 3 d | 6 h | 1 | 10% |

At 14.4× a 30-day budget is gone in 720/14.4 = 50 h; at 6×, in 120 h (5 days). Any other tier for an LLM class (e.g. a lower-sensitivity pair for batch summarisation) is a local choice, not from the Workbook — label it and record why. Low-traffic classes (few requests per window) give noisy burn rates; use the Workbook remedies (synthetic traffic, aggregating classes, reducing per-failure impact) and remember a zero-failure 95% upper bound on error rate is ≈ 3/n. Implementation: [qa-observability slo-design-guide.md](../../qa-observability/references/slo-design-guide.md).

---

### R2 — Wiring Hedged Requests with a Concurrency Cap

**Objective**: hedged requests with bounded overhead, correct cancellation, and load-aware gating. Theory: P2 and foundation 07.

**Step 1–2 — Measure, then simulate a *delayed* hedge from logs:**

```python
import numpy as np

def hedge_analysis(service_ms, tau_pct=90, seed=0):
    s = np.asarray(service_ms)
    tau = np.percentile(s, tau_pct)
    backup = np.random.default_rng(seed).choice(s, len(s))
    hedged = np.minimum(s, tau + backup)          # backup starts at tau
    return {"tau_ms": tau,
            "fraction_hedged": np.mean(s > tau),
            "request_multiplier": 1 + np.mean(s > tau),
            "p99_before": np.percentile(s, 99),
            "p99_after_iid_estimate": np.percentile(hedged, 99)}
```

The resample assumes independent replicas and no added load; treat the p99 estimate as an upper bound on benefit and confirm with a live canary.

**Step 3–4 — Hedge with cancellation, gated on utilisation and a semaphore:**

```python
import asyncio

async def hedged_request(primary_fn, secondary_fn, tau_ms, sem):
    async def secondary_after_tau():
        await asyncio.sleep(tau_ms / 1000)
        async with sem:
            return await secondary_fn()

    tasks = [asyncio.create_task(primary_fn()), asyncio.create_task(secondary_after_tau())]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    return done.pop().result()

async def complete(client, prompt, tau_ms, sem, max_util=0.75):
    if await client.primary.get_utilization() >= max_util:
        return await client.primary.complete(prompt)   # never amplify an overloaded primary
    return await hedged_request(lambda: client.primary.complete(prompt),
                                lambda: client.secondary.complete(prompt), tau_ms, sem)
```

Note: if the first-finished task raised, `result()` re-raises; decide whether to await the other task instead.

**Step 5 — Weekly review**: recompute from last week's traces. `fraction_hedged` drifting above target → p90 moved (model regression, load, hardware). Request/token multiplier above plan → raise τ or restrict hedging to critical classes. No p99 improvement → check correlation (same host/provider/queue for primary and backup).

---

### R3 — Defining a Degraded-Mode Fallback Policy for a Cascaded Agent Stack

**Objective**: partial component failures degrade to labelled partial answers rather than total unavailability. Theory: 05, 06, 07, 10.

**Step 1 — Fault tree:**

```
Top event: "Agent response unavailable"
  OR
    ├── Planner unavailable        (size-1 cut set)
    ├── ALL tools unavailable      (AND of tool1, tool2, tool3)
    └── Synthesizer unavailable    (size-1 cut set; includes quality-floor breach)
```

**Step 2 — Tier ladder** (label every non-Tier-0 response):

```
Tier 0 Full:     planner + all tools + synthesizer
Tier 1 Partial:  planner + ≥1 tool + synthesizer     "Some data sources unavailable"
Tier 2 Minimal:  synthesizer only                    "Model knowledge only; no real-time data"
Tier 3 Fallback: smaller fallback model, no tools    "Reduced quality mode"
Tier 4:          nothing up → 503
```

**Step 3 — Tier availability** (independent components assumed):

```python
from math import prod

a = {"planner": .9997, "tool1": .9995, "tool2": .9998, "tool3": .9996,
     "synthesizer": .9993, "fallback": .9990}
full = prod(a[k] for k in ["planner", "tool1", "tool2", "tool3", "synthesizer"])
any_tier = 1 - (1 - a["synthesizer"]) * (1 - a["fallback"])
# full ≈ 0.99790 (≈ 18.4 h/yr without a full answer); any_tier ≈ 0.9999993
```

The gap between the two numbers is the point: full-answer availability is below 99.8%, while some-answer availability is near six nines — which is why tier labels must be monitored.

**Step 4 — Routing:**

```python
async def route_with_degradation(self, request):
    up = await self.check_health_all()        # parallel checks; exceptions count as down
    tools = [t for t in ("tool1", "tool2", "tool3") if up[t]]
    if up["synthesizer"] and up["planner"] and len(tools) == 3:
        return await self.run_tier0(request)
    if up["synthesizer"] and up["planner"] and tools:
        return await self.run_tier1(request, tools)
    if up["synthesizer"]:
        return await self.run_tier2(request)
    if up["fallback"]:
        return await self.run_tier3(request)
    raise ServiceUnavailableError()
```

**Step 5 — Two SLOs**: full-response (Tier 0), e.g. 99.5% → 219 min per average month; any-response (Tiers 0–3), e.g. 99.9% → 43.8 min. Burn-rate alerts on both (R1 step 5).

**Highest-leverage step**: step 2. Explicit tier labels make partial failures visible; measure the detection-time gain locally rather than assuming one.

---

## Composition

```
1. SLO allocation (P1, R1)        → per-model budgets and provider SLA gaps
2. SPOF identification (P3, A1)   → single-provider, single-region cut sets
3. Redundancy (P2, P3, A4)        → hedges and failovers sized with measured coverage
4. Failure prevention (P4, A2)    → breakers and bounded, jittered retries
5. Failure-mode budgeting (P5, P6)→ LLM-specific modes mapped to latency/MTTR budgets
6. Degraded mode (R3, A3)         → tier ladder and fast version rollback
```

Central dependency: P1 → R1 → R3. A tier ladder needs per-component budgets; a hedge or failover needs the coverage the allocated target requires.

| Pattern | Failure mode addressed |
|---|---|
| P1 | Composite SLO breached silently while each model looks healthy |
| P2 | p99 TTFT breached by slow replicas |
| P3 | Single-provider SPOF |
| P4 | Retry amplification turning overload into a long outage |
| P5 | Silent garbled output from ECC errors or FP8 overflow |
| P6 | Draft/target mismatch degrading acceptance and latency |

---

## Sources

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4 (error budgets, SLOs).
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 5, "Alerting on SLOs", Table 5-8 (multi-window, multi-burn-rate alerts) — https://sre.google/workbook/alerting-on-slos/.
- Dean, J. & Barroso, L. A. (2013). "The Tail at Scale." *Communications of the ACM*, 56(2), 74–80.
- Nygard, M. (2018). *Release It!* (2nd ed.). Pragmatic Bookshelf. (Circuit breakers, bulkheads, retries.)
- Leviathan, Y., Kalman, M., & Matias, Y. (2023). "Fast Inference from Transformers via Speculative Decoding." ICML 2023.
- Chen, C. et al. (2023). "Accelerating Large Language Model Decoding with Speculative Sampling." arXiv:2302.01318.
- IEC 60812 (2018) FMEA; IEC 61025 (2006) FTA.
- [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md) — canonical definitions, formulas, and worked examples; templates [01](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [02](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [04](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md), [05](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [06](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [07](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [08](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [10](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md), [11](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md).
