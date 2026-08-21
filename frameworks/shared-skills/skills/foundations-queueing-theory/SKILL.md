---
name: foundations-queueing-theory
description: Applies queueing theory (Little's Law, M/M/c, Erlang, Kingman, USL) to capacity and latency decisions. Use when load causes non-linear latency growth or queue overrun risk.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Queueing Theory Foundations

11 queueing-theory primitives for capacity planning, saturation prediction, and backpressure design. Each primitive addresses a specific failure mode that causes systems to degrade, saturate, or scale incorrectly. Primitives are domain-agnostic: the same M/M/c formula that sizes a call-center agent pool also sizes a database connection pool and a Kubernetes pod replica count.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Expert Judgment](#expert-judgment)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Navigation](#navigation)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Formula / Key Result | Use When |
|---|-----------|---------------------|----------|
| 1 | [Little's Law](assets/templates/queueing-theory/01-littles-law.md) | L = λW | Relating queue depth, rate, and latency at any stable system |
| 2 | [M/M/1](assets/templates/queueing-theory/02-mm1.md) | W = 1/(μ−λ) | Single-server baseline; understanding saturation curve |
| 3 | [M/M/c (Erlang-C)](assets/templates/queueing-theory/03-mmc.md) | C(c,a) Erlang-C formula | Multi-server pool sizing; wait-time SLO compliance |
| 4 | [M/G/1 / Pollaczek-Khinchine](assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) | Wq = ρ·E[S]·(1+CV²)/2(1−ρ) | Service-time variability inflating queue latency |
| 5 | [Priority Queues](assets/templates/queueing-theory/05-priority-queues.md) | Wq_1 < Wq_2 via P-K residual | Protecting high-priority workloads from low-priority batch |
| 6 | [Jackson Networks](assets/templates/queueing-theory/06-jackson-networks.md) | Product-form: π = Πᵢ πᵢ | Multi-stage pipeline bottleneck identification |
| 7 | [Kingman's Formula](assets/templates/queueing-theory/07-kingman-formula.md) | Wq ≈ (ρ/(1−ρ))·(CV²_a+CV²_s)/2·E[S] | G/G/1 under real bursty+variable traffic |
| 8 | [Bufferbloat](assets/templates/queueing-theory/08-bufferbloat.md) | Buffer > BDP → standing queue | Diagnosing high latency despite good throughput |
| 9 | [USL](assets/templates/queueing-theory/09-usl-universal-scalability.md) | X(N) = λN/(1+σ(N−1)+κN(N−1)) | Predicting retrograde throughput when scaling out |
| 10 | [Erlang-B (Loss)](assets/templates/queueing-theory/10-loss-systems-erlang-b.md) | B(c,a) blocking formula | Sizing channels/connections for drop-on-busy systems |
| 11 | [Fork-Join](assets/templates/queueing-theory/11-fork-join-parallel.md) | E[max] = E[S]·H_K | Fan-out latency dominated by slowest worker |

---

## When to Apply

**Apply queueing-theory when:**
- Latency at p95/p99 grows non-linearly with load (sign of utilisation > 0.7)
- Queue or buffer can fill faster than it drains (request queue, message broker, thread pool)
- Capacity planning: "how many servers/replicas/workers do we need?"
- Rate-limiter or admission-control design (token bucket, leaky bucket, backpressure)
- Multi-stage pipeline where one stage's variance hurts downstream throughput

**Skip and use simpler alternatives when:**
- System is stateless and load is constant — basic capacity math (peak QPS × CPU/req) suffices
- Question is about *correctness* under partition/failure — use foundations-distributed-systems
- Question is about reliability/availability budgets — use foundations-reliability-theory
- Question is about feedback control of a moving target — use foundations-control-theory
- Single-user dev tool with no concurrency — queueing math adds overhead with no payoff
- ρ < 0.3 sustained — system is over-provisioned, not queue-limited

---

## Primitive Index

| # | Mechanism | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Little's Law](assets/templates/queueing-theory/01-littles-law.md) | Misaligned depth/rate/latency metrics; hidden measurement gaps |
| 2 | [M/M/1](assets/templates/queueing-theory/02-mm1.md) | Underestimated latency at moderate utilization; hyperbolic saturation |
| 3 | [M/M/c (Erlang-C)](assets/templates/queueing-theory/03-mmc.md) | Under/over-provisioned parallel server pools; incorrect wait SLO |
| 4 | [M/G/1 / P-K](assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) | Variance-driven latency inflation invisible to M/M/1 |
| 5 | [Priority Queues](assets/templates/queueing-theory/05-priority-queues.md) | High-priority workload blocked by low-priority batch; head-of-line blocking |
| 6 | [Jackson Networks](assets/templates/queueing-theory/06-jackson-networks.md) | Pipeline bottleneck misidentified; scaling wrong stage |
| 7 | [Kingman's Formula](assets/templates/queueing-theory/07-kingman-formula.md) | M/M/1 underestimates real latency due to bursty arrivals and variable service |
| 8 | [Bufferbloat](assets/templates/queueing-theory/08-bufferbloat.md) | Oversized buffers accumulate standing queues; good throughput masks latency crisis |
| 9 | [USL](assets/templates/queueing-theory/09-usl-universal-scalability.md) | Retrograde scaling: adding servers reduces throughput past N_max |
| 10 | [Erlang-B](assets/templates/queueing-theory/10-loss-systems-erlang-b.md) | Blocking rate exceeds GoS target; call/connection loss uncontrolled |
| 11 | [Fork-Join](assets/templates/queueing-theory/11-fork-join-parallel.md) | Fan-out sized by mean worker time; completion dominated by slowest worker |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Conservation laws | Need universal consistency across rate, latency, and queue depth | #1 |
| Markovian queues | Need exact M/M/1, M/M/c, Erlang-B/C baselines | #2, #3, #10 |
| General service-time queues | Need variability effects beyond exponential assumptions | #4, #7 |
| Scheduling theory | Need priority lanes, preemption, or class-specific SLOs | #5. SOAP framework (Scully, Harchol-Balter & Scheller-Wolf 2018) unifies all M/G/1 age-based policies (SRPT, FCFS, FB, Gittins) under one response-time formula; use to compare policies for a given job-size distribution. SIGMETRICS 2025: Gittins policy with negative discount rate achieves strong tail optimality in light-tailed M/G/1 without known job sizes (Harlev, Yu, Scully 2025). Robust Gittins bounds degradation under distributional misspecification (Moseley et al. 2025). For multiserver, see the M/G/k caveats under [Fact-Checking](#fact-checking) — SRPT-k is no longer optimal for the mean, and tail-optimal policies are load-regime-dependent. |
| Memory-coupled service | Need stability where admitted work holds a growing, non-releasable resource until completion (KV cache, session state, long-lived connections with buffers) | #1, #8 — joint compute-and-memory stability conditions (Nie, Si & Zhou, ICML 2026); eviction limit cycles and the stabilizing role of service-time heterogeneity (Ao, Dong, Luo & Simchi-Levi 2026). Classical single-resource ρ is not sufficient for stability here. |
| Learning-augmented scheduling | Need to use ML-predicted job sizes to reduce mean response time while bounding degradation under prediction error | #4, #5 — SPRPT, Trail policy, consistency-robustness framework (Mitzenmacher & Shahout 2025); embedding-based output-length prediction for LLM scheduling (Shahout et al., arXiv 2410.01035). |
| Queueing networks | Need multi-stage pipeline flow balance | #6 |
| Active queue management | Need bounded latency under buffers and backpressure | #8 |
| Scalability laws | Need contention/coherency limits under scale-out | #9 |
| Parallel response time | Need fan-out, fork-join, or tail-latency analysis | #11 |

Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs stationarity, arrival-process, or distribution assumptions.

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Applying Little's Law to a burst window | The law requires stable long-run averages | Use steady windows or separate transient analysis |
| Using M/M/1 for real bursty traffic | Poisson/exponential assumptions understate latency under high CV | Use Kingman or simulation |
| Confusing Erlang-B and Erlang-C | Blocking and waiting are different systems | Choose loss model vs queueing model explicitly |
| Treating higher utilization as efficiency | Waiting time explodes near saturation | Set target rho below the SLO breach point |
| Adding buffers to fix overload | Buffers hide overload as latency | Bound queues and apply backpressure |
| Scaling out without USL fit | Coherency and contention can make throughput retrograde | Fit USL from load-test data |
| Applying Jackson product-form to LLM inference networks | KV-cache memory coupling violates independence between stages; product-form assumption does not hold | Model single-engine throughput optimality via work-conservation criterion (Dai, Deng, Li & Peng 2026); use MaxWeight-style routing for multi-engine networks |
| Deriving ρ < 1 from compute alone on a KV-cached LLM engine | Stability is jointly constrained by compute *and* GPU memory: each in-flight request's KV cache grows with every token it emits, so admitted work consumes a second, non-releasable resource until completion. A compute-only ρ can read comfortably below 1 while the memory constraint is already the binding one | Apply the joint compute-plus-memory stability condition (Nie, Si & Zhou, ICML 2026); size the cluster from the derived stable service rate, not from GPU FLOPs utilization |
| Assuming an eviction-free operating point is a stable equilibrium | Under saturation with homogeneous request lengths, decode completions synchronize, memory demand peaks together, and the system falls into a limit cycle of evict-and-restart — up to ~50% throughput loss. The eviction-free point is an unstable equilibrium, not a target | Desynchronize completions (heterogeneous or coprime decode lengths, staggered admission); admission-control on projected peak KV occupancy rather than instantaneous (Ao, Dong, Luo & Simchi-Levi 2026) |

Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before using formulas for capacity commitments.

---

## Expert Judgment

The formulas above are correct but mechanical. What separates an expert read of a capacity problem from a formula lookup is knowing *which number to distrust* and *why the textbook answer is usually optimistic*.

**Why "80% utilization" is a heuristic, not a law.** ρ ≤ 0.7–0.8 is a widely repeated rule of thumb, but it is not derived from M/M/1 — it is a scar tissue from postmortems. M/M/1's Wq = ρ/(μ(1−ρ)) is smooth and finite at ρ = 0.8 (only 5× service time); nothing in the pure math says 80% is special. What makes 80% the practical wall in real systems is that CV²_a and CV²_s are almost never 1 in production: Kingman's variability factor (CV²_a+CV²_s)/2 typically runs 1.5–5× for HTTP/LLM/DB workloads, and that factor multiplies the same ρ/(1−ρ) term. A system that "should" be fine at ρ=0.8 under M/M/1 is often already 2–4× over its real SLO because of variance the mean-based model doesn't see. Treat 70–80% as a starting guess to be replaced by a measured ρ* from Kingman (07) with real CV² inputs — never as a target that stands on its own.

**VUT decomposition — variance matters as much as utilization.** Kingman's formula factors cleanly into three independent levers: **V**ariability (CV²_a+CV²_s)/2, **U**tilization ρ/(1−ρ), **T**ime E[S]. When Wq blows up, an expert's first move is to ask *which factor moved*, not to assume it was utilization. The most common real-world regression is a variance shift with flat or even falling utilization: a new job class with a heavier tail, a noisy-neighbor GC pause, a cold-start penalty, a retry storm — all inflate CV²_s or CV²_a without moving ρ at all. Dashboards that show only "CPU 65%, looks fine" miss this entirely. If you have percentile telemetry, compare p99/p50 of service time over time — a widening ratio at flat utilization is the VUT variance term moving, and no amount of added capacity (which only fixes the U term) will help until the variance source is found and isolated (priority lane, timeout, or separate pool).

**Batch-size effects break the "μ is constant" assumption.** Every formula in this skill treats service rate μ as fixed. Batching (DB writes, Kafka consumer polls, LLM continuous batching, GPU inference) makes μ a function of the current queue state — larger batches raise throughput but also raise per-item latency and effective service-time variance (a request's completion now depends on what else is in its batch, not just its own size). This is closer to a batch-service queue (M[X]/M/1) or a vacation-queue model than to plain M/M/1/M/G/1, and naively plugging a batch system's mean service time into P-K or Kingman underestimates Wq because it ignores the correlation batching induces between co-scheduled jobs. Practical rule: if batch size is a tunable knob in the system, model it as a control variable feeding into E[S] and CV²_s, not as a constant absorbed into μ — and re-measure CV²_s at each candidate batch size rather than assuming it is batch-size-invariant.

**When Little's Law is the only tool you can still trust.** Every closed-form result above (M/M/1, Erlang-C, P-K, Kingman, USL) depends on distributional or stationarity assumptions — Poisson arrivals, exponential or known-moment service times, steady state, i.i.d. samples. Real production traffic routinely violates all of them at once: heavy-tailed service times where even the *variance* fails to converge (CV² is undefined, not just large), autocorrelated bursts from retries/cron/batch releases that a single CV²_a number cannot capture, and non-stationary regimes during incidents or autoscaling transitions. Little's Law (L = λW) is the one relationship in this skill that requires none of that — only that the system is stable and observed over a long-enough window. When you don't trust the distributional inputs a formula needs, don't force-fit Kingman or P-K anyway: fall back to measuring L, λ, and W directly and using L = λW purely as a **consistency check**, not as a way to derive the one unknown you can't measure. If L ≠ λW under direct measurement, the problem is measurement or population-mixing, not the formula.

**Two misapplications that produce confidently wrong capacity plans:**
- *M/M/1 (or P-K) applied to heavy-tailed service times.* Once CV²_s exceeds roughly 5, or the service-time distribution is Pareto-like with infinite or barely-finite variance, P-K's Wq — which is itself a function of the second moment E[S²] — becomes unreliable, not merely "a bit low." A handful of extreme requests can dominate E[S²] and make the formula's output swing wildly between similar-looking samples. This is a qualitatively different failure than "variance inflates wait" (primitive 04's normal case): the mean-based formula itself stops being a stable estimator. Escalate to percentile-based modeling or discrete-event simulation rather than trusting a P-K point estimate.
- *Ignoring arrival burstiness because "CV²_a looks close to 1."* CV²_a measures dispersion of inter-arrival times but says nothing about *correlation* between them. Self-similar / long-range-dependent traffic (see Leland, Taqqu, Willinger & Wilson, "On the Self-Similar Nature of Ethernet Traffic," SIGCOMM 1993 — a foundational, widely-replicated result on bursty network traffic) can have CV²_a near 1 while still producing much longer queueing episodes than an i.i.d. renewal process with the same CV²_a, because bursts cluster in time. Kingman's formula assumes renewal (uncorrelated) arrivals and will underestimate Wq under such traffic even after "correcting" for CV²_a. If arrival autocorrelation is suspected (batch releases, coordinated retries, diurnal micro-bursts), validate against a measured autocorrelation function or a trace-driven simulation, not just a single CV²_a plugged into Kingman.

---

## Decision Checklist

- [ ] **Is the system stable?** Compute ρ = λ/(c×μ). If ρ ≥ 1, no steady-state solution exists — scale capacity first.
- [ ] **Single-server baseline?** → M/M/1 (02). Establish the latency vs. ρ curve.
- [ ] **Multiple parallel servers?** → M/M/c / Erlang-C (03). Compute minimum c for wait-time SLO.
- [ ] **Service time non-exponential (CV² ≠ 1)?** → P-K (04) for Poisson arrivals; Kingman (07) for non-Poisson arrivals.
- [ ] **Bursty arrivals (CV²_a > 1)?** → Kingman (07). M/M/1 will underestimate latency.
- [ ] **Multi-stage pipeline?** → Jackson networks (06). Solve flow balance; find highest-ρ stage.
- [ ] **Scaling horizontally?** → USL (09). Fit σ and κ from load-test series; check N_max.
- [ ] **Mixed SLO classes in one pool?** → Priority queues (05). Separate classes; analyze each.
- [ ] **High latency but good throughput?** → Bufferbloat (08). Check queue depth; apply AQM or finite bounds.
- [ ] **Drop-on-busy (no queue)?** → Erlang-B (10). Compute blocking probability B(c, a).
- [ ] **Fan-out / parallel scatter-gather?** → Fork-join (11). Compute E[max] = E[S] × H_K.
- [ ] **Sanity-check any result?** → Little's Law (01). Verify L = λ × W is consistent with measurements.
- [ ] **Tail latency SLO on multi-stage pipeline with non-Poisson arrivals?** → Jackson networks (06) + Ciucu-Mehri tandem sojourn bounds (SIGMETRICS 2025). Mean Jackson analysis understates tail risk when CV²_a ≠ 1.
- [ ] **Does admitted work hold a growing resource until it completes (KV cache, session buffers)?** → Single-resource ρ is insufficient. Check the joint compute-and-memory stability condition and the eviction/limit-cycle risk before trusting any ρ < 1 result (see [Misuse Boundaries](#misuse-boundaries)).

---

## Anti-Patterns

| Anti-Pattern | Queueing Theory Diagnosis | Fix |
|-------------|--------------------------|-----|
| **Ignoring service-time variability (CV²) on G/G/1 systems** | M/M/1 assumes CV²=1; real CV²>1 inflates Wq by (1+CV²)/2 factor | Measure service-time distribution; apply P-K (04) or Kingman (07) |
| **M/M/1 used at ρ near 1 without USL retrograde check** | M/M/1 predicts infinite latency but doesn't account for coherency degradation when c is added | Fit USL (09) from multi-server load tests before committing to scaling decision |
| **Little's Law applied across non-stationary windows** | L = λW holds only at steady state; burst windows violate ergodicity assumption | Use a measurement window ≥ 10× mean service time; separate burst analysis |
| **Erlang-C confused with Erlang-B for queueing decisions** | Erlang-B models drop/loss (no queue); Erlang-C models queuing (wait, don't drop) | Determine whether the system queues or blocks; select model accordingly (03 vs 10) |
| **Fork-join sized by mean worker time rather than max** | Completion time = E[max(S₁,...,Sₖ)] = E[S]×H_K >> E[S] at moderate K | Apply H_K harmonic correction; model tail of maximum; use speculative execution for high-K |
| **Unbounded application queues (bufferbloat)** | Large buffers absorb spikes silently; latency accumulates without 503/backpressure signal | Set finite queue depth proportional to BDP; add AQM or backpressure |
| **Scaling pipeline stage without re-solving flow balance** | Jackson network bottleneck shifts to next highest-ρ stage after scaling | Re-run flow-balance equations after each scaling action; re-identify bottleneck |
| **Using FCFS when output-length predictions are available** | FCFS ignores size information; SPRPT with Trail degrades gracefully under bounded prediction error and approaches SRPT performance when predictions are accurate | Add lightweight output-length predictor (embedding-based); apply Trail policy (Mitzenmacher & Shahout 2025) with preemption age threshold to avoid KV-cache re-compute cost |

---

## Composition Recipes

### Recipe 1 — Capacity Plan for a New Service

_Goal: Size server pool before launch._

1. **Little's Law (01)**: derive initial L, λ, W relationship from design requirements.
2. **M/M/c (03)**: find minimum c so that Erlang-C wait probability meets SLO.
3. **P-K / Kingman (04, 07)**: inflate Wq by measured CV²_s and CV²_a; re-check c.
4. **USL (09)**: validate that the c-server pool achieves near-linear scaling (κ ≈ 0).

_Standout insight_: Kingman's variability factor (CV²_a + CV²_s)/2 can easily be 2–5×; a service meeting its SLO at ρ = 0.7 with M/M/c can violate SLO at the same ρ if CV² is ignored.

---

### Recipe 2 — Saturation SLO Alert Threshold

_Goal: Determine the utilization ρ* at which latency will breach SLO, and set an alert before it happens._

1. **M/M/1 (02)**: solve W(ρ) = SLO_target; find ρ* (first-pass, exponential baseline).
2. **Kingman (07)**: recompute ρ* with real CV²_a and CV²_s — typically ρ* is 10–20% lower.
3. **Bufferbloat (08)**: confirm that queue depth monitoring is in place; standing queues are the first signal.
4. **Little's Law (01)**: set alert on Lq = λ × Wq_threshold; queue depth is a leading indicator of latency breach.

_Standout insight_: Setting the alert on latency p99 is reactive; setting it on queue depth (via Little's Law) is proactive — the queue builds before p99 breaches.

---

### Recipe 3 — Multi-Stage Pipeline Bottleneck Hunt

_Goal: Find and fix the throughput bottleneck in a microservice chain, then verify the fix didn't shift the bottleneck._

1. **Jackson networks (06)**: instrument each stage; collect λᵢ, μᵢ, cᵢ; solve flow-balance equations; rank by ρᵢ.
2. **M/M/c (03)**: compute servers needed at bottleneck station i to achieve target ρ ≤ 0.70.
3. **USL (09)**: after scaling station i, verify new ρ distribution; check for retrograde at any stage.
4. **Priority queues (05)**: if multiple SLO classes converge at the bottleneck, separate into priority lanes.

_Standout insight_: The Jackson product-form result means each stage can be analyzed independently — but only after solving the traffic equations. Teams that scale one stage without re-solving flow balance routinely move the bottleneck downstream without knowing it.

---

### Recipe 4 — LLM Inference Capacity Sizing

_Goal: Size GPU/CPU capacity and select a scheduling policy for an LLM serving endpoint._

1. **M/G/1 / P-K (04)**: model the prefill phase with Poisson arrivals and near-deterministic service (prompt-token-proportional duration); compute Wq and verify ρ < 0.7 before queueing degrades.
2. **M/G/1 with SPRPT-Trail (04, 05)**: model the decode phase — service time = output_tokens × time_per_token, unknown at arrival. Use prediction-augmented SPRPT with Trail policy (Mitzenmacher & Shahout, Stochastic Systems 2025) to avoid KV-cache re-compute on preemption.
3. **Priority queues (05)**: if serving multiple tiers (interactive vs. batch), apply non-preemptive priority between tiers; verify low-priority class does not starve.
4. **Joint compute-and-memory stability (new, gates steps 1–3)**: KV cache is not a passive buffer. Each admitted request holds GPU memory that *grows* with every token it decodes and is released only at completion, so admitted work consumes a second resource whose demand is a function of service progress. Check the joint stability condition (Nie, Si & Zhou, ICML 2026) — a compute-side ρ well under 1 does not imply stability if memory is the binding constraint. Size the cluster from the derived stable service rate; the paper reports prediction error typically within 10% against production GPU measurements.
5. **Eviction dynamics under saturation (05, 08)**: if the workload is homogeneous in output length, decode completions synchronize and memory peaks align, producing an evict-and-restart limit cycle with up to ~50% throughput loss (Ao, Dong, Luo & Simchi-Levi 2026). Heterogeneity is stabilizing here: coprime or dispersed decode lengths desynchronize completions. Admission-control on *projected peak* KV occupancy over a request's remaining decode horizon, not on instantaneous occupancy.
6. **M/M/c autoscaling (03)**: for dynamic replica counts, apply SageServe multi-timescale control (Jaiswal et al., POMACS/SIGMETRICS 2026) — short-horizon routing + long-horizon GPU scaling via traffic forecasting.
7. **Fleet simulation escalation**: If the token-length distribution is heavy-tailed (measured CV² > 2), combine M/G/c analytical sizing from step 1 with discrete-event simulation (inference-fleet-sim, arXiv 2603.16054) before committing to fleet purchase. Analytical M/G/c alone produces incorrect sizing for split thresholds, GPU type selection, and utilization under heavy-tailed LLM workloads.

_Standout insight_: Two separate throughput-optimality results now cover this setting and they answer different questions. Work-conservation is *sufficient* for maximum throughput on a single engine and on DAG/fork-join agent topologies (Dai, Deng, Li & Peng 2026) — which is why Orca and Sarathi-serve are throughput-optimal and vanilla vLLM is not. But work-conservation alone does not tell you *how* to tile prefill against decode: RAD (Bari, Hegde & de Veciana, POMACS/SIGMETRICS 2026) shows optimal tiling plus dynamic resource allocation are the binding design principles, and its SLO-aware variant SLAI cuts median TTFT 53% versus Sarathi-serve. Throughput-optimality is the floor; tiling and scheduling decide tail latency.

---

## Workflow

1. Identify the failure mode (saturation, variance, scaling cliff, fan-out slowdown, blocking).
2. Use the [Decision Checklist](#decision-checklist) to map failure mode → primitive.
3. Open the primitive playbook in [`assets/templates/queueing-theory/`](assets/templates/queueing-theory/) for definition, inputs, outputs, worked example.
4. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) or the full [`assets/templates/queueing-theory/README.md`](assets/templates/queueing-theory/README.md).
5. Validate results with Little's Law (01) — the universal consistency check.
6. Escalate to simulation (SimPy, JMT) when distributions are empirical, buffers are finite, and priorities interact simultaneously.

---

## ASCII Flow

```text
Waiting, capacity, or throughput problem
  -> Measure arrivals, service time, concurrency, buffer, and blocking
  -> Classify queue shape: single server, multi-server, finite buffer, priority, network, fork-join
  -> Select primitive and compute baseline
  -> Validate with Little's Law
     +-- conservation fails -> fix measurement before optimizing
     +-- conservation holds -> size capacity or simulate
  -> Return bottleneck, wait estimate, utilization risk, and scaling limit
```

---

## Related Skills

_Consumer skills that apply queueing-theory recipes to domain problems will reference this skill. No cross-links to non-foundation skills are made here._

---

## Navigation

- Per-primitive playbooks: [`assets/templates/queueing-theory/`](assets/templates/queueing-theory/) (one file per primitive)
- Composition guide and scenario stacks: [`assets/templates/queueing-theory/README.md`](assets/templates/queueing-theory/README.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview, anti-patterns, decision checklist: [`references/primitives-overview.md`](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Fact-Checking

- All formulas (M/M/1, M/M/c, P-K, Erlang-B, Kingman, USL, fork-join) are derived from the primary textbook sources listed in `data/sources.json`. Verify against Kleinrock (1975, 1976), Harchol-Balter (2013), and Cooper (1981) before treating worked-example numbers as benchmarks.
- **2026-07-11 audit**: several Harchol-Balter (2013) chapter citations in `assets/templates/queueing-theory/*.md` were wrong (verified against the publisher's chapter list) and have been corrected in-file with dated notes; the Kleinrock Vol.1/Vol.2 publication years were transposed in primitive 05 and are now fixed; the Erlang-C table and worked example in primitive 03, and the Erlang-B required-server table in primitive 10, contained arithmetic errors and have been recomputed and replaced with code-verified values. Treat any un-dated numeric table in this skill as a starting estimate to be recomputed, not a citation-grade constant.
- **M/M/c finite-time bounds**: steady-state Erlang-C formulas are lower bounds on required capacity during transient windows (bursts, autoscaling transitions, cold starts). Nguyen, Varma, Maguluri (SIGMETRICS 2025) provide the first quantitative transient guarantees; apply when measurement windows are short relative to mixing time.
- USL parameters (σ, κ) are system-specific and must be fitted from load tests. Published σ/κ values for one system do not transfer to another.
- The Kingman formula is an asymptotic heavy-traffic approximation; errors increase at ρ < 0.5. Use P-K (primitive 04) for exact M/G/1 results.
- **M/G/k multiserver scheduling**: The prior assumption that SRPT-k achieves optimal mean response time in M/G/k queues across all loads has been superseded. Grosof & Hurtado-Lange (arXiv 2510.25963, SIGMETRICS 2026) introduce SEK-SMOD, the first policy provably achieving lower mean response time than SRPT-k across all loads and all job size distributions. Treat SRPT-k as a strong but no longer optimal baseline in M/G/k systems. Note the counterintuitive shared mechanism with the tail-latency result below: both gain by *de*prioritizing the shortest jobs in some regime, so "SRPT and its variants are always the right default" is no longer a safe assumption.
- **M/G/k tail latency is not monotone in the policy**: Yu, Harlev, Adakroy & Scully (POMACS/SIGMETRICS 2026, DOI 10.1145/3771561) prove γ-Boost is tail-constant-optimal for light-tailed M/G/k *in heavy traffic*, but show empirically it can be worse than plain FCFS at lighter loads. Their improved variant gives *more* priority to larger jobs and is both heavy-traffic optimal and stronger at light load. Practical consequence: a scheduling policy validated at peak load may be actively harmful off-peak — benchmark tail latency across the whole operating range, not only at the design point.
- **2026-08-14 audit**: the citation for Dai, Deng, Li & Peng was corrected. That work retains its original title ("Throughput-Optimal Scheduling Algorithms for LLM Inference and AI Agents", arXiv:2504.07347 v3, May 2026) and is *not* the paper at DOI 10.1145/3771574 — that DOI belongs to a distinct POMACS/SIGMETRICS 2026 paper by Bari, Hegde & de Veciana (arXiv:2508.01002). The two results are complementary, not the same paper under a new name; both are now cited separately.
- Erlang-B and Erlang-C assume Poisson arrivals. Real traffic with CV²_a > 1 will produce higher blocking / longer waits than these formulas predict. Treat as lower bounds on required capacity.
- Fork-join E[max] = E[S] × H_K is exact for exponential service times and independent workers. Correlated sub-tasks or non-exponential service require simulation.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
