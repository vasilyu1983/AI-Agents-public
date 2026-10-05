---
name: foundations-queueing-theory
description: "Sizes queues and worker pools. Use when estimating Kingman G/G/1 mean waiting time, Erlang or Little's Law sizing, p99 under load, retry storms, worker counts."
compatibility: Portable core only.
version: "1.5"
last_validated: 2026-09-08
---

# Queueing Theory Foundations

11 queueing-theory primitives for capacity planning, saturation prediction, and backpressure design. Each primitive addresses a specific failure mode that causes systems to degrade, saturate, or scale incorrectly.

## Contents

- [Quick Reference](#quick-reference)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Expert Judgment](#expert-judgment)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [Trace-Driven Simulation](#trace-driven-simulation)
- [Related Skills](#related-skills)
- [Navigation](#navigation)
- [Domain Verification Notes](#domain-verification-notes)

## Quick Reference

| # | Primitive | Formula / Key Result | Use When | Failure Mode It Addresses |
|---|-----------|---------------------|----------|---------------------------|
| 1 | [Little's Law](assets/templates/queueing-theory/01-littles-law.md) | L = λW | Relating queue depth, rate, and latency at any stable system | Misaligned depth/rate/latency metrics |
| 2 | [M/M/1](assets/templates/queueing-theory/02-mm1.md) | W = 1/(μ−λ) | Single-server baseline; understanding saturation curve | Hyperbolic saturation underestimated |
| 3 | [M/M/c (Erlang-C)](assets/templates/queueing-theory/03-mmc.md) | C(c,a) Erlang-C formula | Multi-server pool sizing; wait-time SLO compliance | Pool under/over-provisioned for wait SLO |
| 4 | [M/G/1 / Pollaczek-Khinchine](assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) | Wq = ρ·E[S]·(1+CV²)/2(1−ρ) | Service-time variability inflating queue latency | Variance-driven FCFS wait inflation |
| 5 | [Priority Queues](assets/templates/queueing-theory/05-priority-queues.md) | Wq_1 < Wq_2 via P-K residual | Protecting high-priority workloads from low-priority batch | High-priority work blocked by batch |
| 6 | [Jackson Networks](assets/templates/queueing-theory/06-jackson-networks.md) | Product-form: π = Πᵢ πᵢ | Multi-stage pipeline bottleneck identification | Wrong bottleneck stage scaled |
| 7 | [Kingman's Formula](assets/templates/queueing-theory/07-kingman-formula.md) | Wq ≈ (ρ/(1−ρ))·(CV²_a+CV²_s)/2·E[S] | G/G/1 under real bursty+variable traffic | Bursty arrivals + variable service underestimated |
| 8 | [Bufferbloat](assets/templates/queueing-theory/08-bufferbloat.md) | Persistent occupied queue / drain rate → delay | Diagnosing high latency despite good throughput | Standing queue hidden by good throughput |
| 9 | [USL](assets/templates/queueing-theory/09-usl-universal-scalability.md) | X(N) = λN/(1+σ(N−1)+κN(N−1)) | Predicting retrograde throughput when scaling out | Retrograde throughput past N_max |
| 10 | [Erlang-B (Loss)](assets/templates/queueing-theory/10-loss-systems-erlang-b.md) | B(c,a) blocking formula | Sizing channels/connections for drop-on-busy systems | Blocking above GoS target |
| 11 | [Fork-Join](assets/templates/queueing-theory/11-fork-join-parallel.md) | E[max]=E[S]·H_K only for iid exponential services; include waiting | Fan-out latency dominated by slowest worker | Completion gated by slowest branch |

Multi-server sizing (Allen-Cunneen, square-root staffing), discipline sensitivity (FCFS vs processor sharing) and overload (retries, goodput, shedding): [references/multiserver-overload-and-disciplines.md](references/multiserver-overload-and-disciplines.md).

## When to Apply

**Apply queueing-theory when:**
- Latency at p95/p99 grows non-linearly with load (investigate workload-specific saturation and variability)
- Queue or buffer can fill faster than it drains (request queue, message broker, thread pool)
- Capacity planning: "how many servers/replicas/workers do we need?"
- Rate-limiter or admission-control design (token bucket, leaky bucket, backpressure)
- Multi-stage pipeline where one stage's variance hurts downstream throughput

**Skip and use simpler alternatives when:**
- A measured latency model already meets the decision's accuracy requirement; statelessness alone does not remove queueing
- Question is about *correctness* under partition/failure — use foundations-distributed-systems
- Question is about reliability/availability budgets — use foundations-reliability-theory
- Question is about feedback control of a moving target — use foundations-control-theory
- Single-user dev tool with no concurrency — queueing math adds overhead with no payoff
- Measured waiting and tails are immaterial to the decision across representative load; low mean utilization alone is insufficient
- Load-test tooling and methodology → qa-testing-performance; LLM engine tuning and TTFT/TPOT SLOs → ai-llm-inference

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Conservation laws | Need universal consistency across rate, latency, and queue depth | #1 |
| Markovian queues | Need exact M/M/1, M/M/c, Erlang-B/C baselines | #2, #3, #10 |
| General service-time queues | Need variability effects beyond exponential assumptions | #4, #7 |
| Scheduling theory | Need priority lanes, preemption, or class-specific SLOs | #5. SOAP unifies M/G/1 age-based policies; M/G/k mean and tail results are load-regime-dependent. Paper notes: [references/formal-theory-map.md](references/formal-theory-map.md#scheduling-research-notes-moved-from-skillmd) |
| Memory-coupled service | Need stability where admitted work holds a growing, non-releasable resource until completion (KV cache, session state, long-lived connections with buffers) | #1, #8 — joint compute-and-memory stability conditions (Nie, Si & Zhou, ICML 2026); eviction limit cycles and the stabilizing role of service-time heterogeneity (Ao, Dong, Luo & Simchi-Levi 2026). Classical single-resource ρ is not sufficient for stability here. |
| Learning-augmented scheduling | Need ML-predicted job sizes with bounded degradation under prediction error | #4, #5. Bounded degradation is proven for SPRPT-with-bounce and PSPJF (Scully, Grosof & Mitzenmacher, ITCS 2022), not plain SPRPT. Trail (Shahout et al., arXiv 2410.01035) limits preemption to young requests. |
| Queueing networks | Need multi-stage pipeline flow balance | #6 |
| Active queue management | Need bounded latency under buffers and backpressure | #8 |
| Scalability laws | Need contention/coherency limits under scale-out | #9 |
| Parallel response time | Need fan-out, fork-join, or tail-latency analysis | #11 |
| Multi-server and overload | Need G/G/c sizing, pooling, discipline choice, or behaviour at ρ ≥ 1 | #3, #7, #8 via [multiserver-overload-and-disciplines.md](references/multiserver-overload-and-disciplines.md) |

Use [references/formal-theory-map.md](references/formal-theory-map.md) when the task needs stationarity, arrival-process, or distribution assumptions.

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Treating higher utilization as efficiency | Waiting time explodes near saturation | Derive c or ρ from the SLO (square-root staffing), not a fixed target |
| Applying P-K/Kingman variance inflation to a processor-sharing or loss system | The (1+CV²)/2 penalty is an FCFS result; M/G/1-PS mean response E[S]/(1−ρ) and Erlang-B blocking are insensitive to CV²_s | Identify the discipline first |
| Treating ρ ≥ 1 with retries as "add capacity" | Timed-out requests retry and waste capacity; goodput can reach zero at 100% CPU and persist (metastable) | Shed by delay (CoDel), adaptive LIFO, deadlines, retry budgets; then scale |
| Applying Jackson product-form to LLM inference networks | KV-cache memory coupling violates independence between stages; product-form assumption does not hold | Model single-engine throughput optimality via work-conservation criterion (Dai, Deng, Li & Peng 2026); use MaxWeight-style routing for multi-engine networks |
| Deriving ρ < 1 from compute alone on a KV-cached LLM engine | Stability is jointly constrained by compute *and* GPU memory: each in-flight request's KV cache grows with every token it emits, so admitted work consumes a second, non-releasable resource until completion. A compute-only ρ can read comfortably below 1 while the memory constraint is already the binding one | Apply the joint compute-plus-memory stability condition (Nie, Si & Zhou, ICML 2026); size the cluster from the derived stable service rate, not from GPU FLOPs utilization |
| Assuming an eviction-free operating point is a stable equilibrium | Under saturation with homogeneous request lengths, decode completions synchronize, memory demand peaks together, and the system falls into a limit cycle of evict-and-restart — up to ~50% throughput loss. The eviction-free point is an unstable equilibrium, not a target | Desynchronize completions (heterogeneous or coprime decode lengths, staggered admission); admission-control on projected peak KV occupancy rather than instantaneous (Ao, Dong, Luo & Simchi-Levi 2026) |

Check [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before using formulas for capacity commitments.

## Expert Judgment

**Why "80% utilization" is a heuristic, not a law.** No fixed utilization target follows from M/M/1. The acceptable ρ depends on the latency SLO, arrival and service variability, autocorrelation, batching, transient duration, and scaling delay. Derive a workload-specific threshold from measured traces and validate it across the operating range; published utilization bands are scenario examples, not portable targets.

**VUT decomposition — variance matters as much as utilization.** Kingman's formula factors cleanly into three independent levers: **V**ariability (CV²_a+CV²_s)/2, **U**tilization ρ/(1−ρ), **T**ime E[S]. When Wq blows up, an expert's first move is to ask *which factor moved*, not to assume it was utilization. The most common real-world regression is a variance shift with flat or even falling utilization: a new job class with a heavier tail, a noisy-neighbor GC pause, a cold-start penalty, a retry storm — all inflate CV²_s or CV²_a without moving ρ at all. Dashboards that show only "CPU 65%, looks fine" miss this entirely. If you have percentile telemetry, compare p99/p50 of service time over time — a widening ratio at flat utilization is a diagnostic clue to investigate the full second moment, workload mix and dependence; p99/p50 does not identify variance or prove which VUT factor moved, and extra capacity can reduce the U term while leaving the variance cause unresolved; compare capacity changes with variance isolation (priority lane, timeout, or separate pool).

**Batch-size effects break the "μ is constant" assumption.** Every formula in this skill treats service rate μ as fixed. Batching (DB writes, Kafka consumer polls, LLM continuous batching, GPU inference) makes μ a function of the current queue state — larger batches raise throughput but also raise per-item latency and effective service-time variance (a request's completion now depends on what else is in its batch, not just its own size). This is closer to a bulk-service queue (distinct from M[X]/M/1, whose X denotes batch arrivals) or a vacation-queue model than to plain M/M/1/M/G/1, and naively plugging a batch system's mean service time into P-K or Kingman can misestimate Wq in either direction because it ignores state-dependent service and correlation between co-scheduled jobs. Practical rule: if batch size is a tunable knob in the system, model it as a control variable feeding into E[S] and CV²_s, not as a constant absorbed into μ — and re-measure CV²_s at each candidate batch size rather than assuming it is batch-size-invariant.

**Little's Law under weak distributional assumptions.** Every closed-form result above (M/M/1, Erlang-C, P-K, Kingman, USL) depends on distributional or stationarity assumptions — Poisson arrivals, exponential or known-moment service times, steady state, i.i.d. samples. Real production traffic routinely violates all of them at once: heavy-tailed service times where even the *variance* fails to converge (CV² is undefined, not just large), autocorrelated bursts from retries/cron/batch releases that a single CV²_a number cannot capture, and non-stationary regimes during incidents or autoscaling transitions. Little's Law needs matched populations and finite long-run rate and mean sojourn-time limits; stationarity is sufficient, not necessary. For a finite trace, account for work crossing the observation boundaries before comparing averages (see primitive 01). When you don't trust the distributional inputs a formula needs, don't force-fit Kingman or P-K anyway: fall back to measuring L, λ, and W directly and using L = λW purely as a **consistency check**, not as a way to derive the one unknown you can't measure. A finite-window mismatch can reflect boundary work, incompatible populations or unconverged averages; it does not by itself prove a telemetry error.

**Overload is a different regime, not a high-ρ point.** Above capacity, the useful metric is goodput (completions within the caller's deadline), not throughput. Under FCFS with a backlog Q, every arrival waits Q/μ; once that exceeds the client timeout, the server works only on abandoned requests while the callers retry. Remedies act on the queue, not the fleet: delay-bounded queues, adaptive LIFO, deadline propagation, retry budgets. Details and sources: [references/multiserver-overload-and-disciplines.md](references/multiserver-overload-and-disciplines.md).

**Two misapplications that produce confidently wrong capacity plans:**
- *M/M/1 (or P-K) applied to heavy-tailed service times.* When the estimated second moment is unstable across windows, P-K's Wq is not a stable capacity input. A handful of extreme requests can dominate E[S²] even when a sample CV² looks finite. Inspect tail and moment stability, then use trace-driven simulation or robust percentile analysis rather than relying on an arbitrary CV² cutoff.
- *Ignoring arrival burstiness because "CV²_a looks close to 1."* CV²_a measures dispersion of inter-arrival times but says nothing about *correlation* between them. Self-similar / long-range-dependent traffic (see Leland, Taqqu, Willinger & Wilson, "On the Self-Similar Nature of Ethernet Traffic," SIGCOMM 1993 — a foundational, widely-replicated result on bursty network traffic) can have CV²_a near 1 while still producing much longer queueing episodes than an i.i.d. renewal process with the same CV²_a, because bursts cluster in time. Kingman's formula assumes renewal (uncorrelated) arrivals and will underestimate Wq under such traffic even after "correcting" for CV²_a. If arrival autocorrelation is suspected (batch releases, coordinated retries, diurnal micro-bursts), validate against a measured autocorrelation function or a trace-driven simulation, not just a single CV²_a plugged into Kingman.

## Decision Checklist

- [ ] **Is the system stable?** Compute ρ = λ/(c×μ), including retries in λ. For an unbounded queue without abandonment, ρ ≥ 1 rules out the usual stable steady state: shed or bound the queue first, then scale (overload section of the multi-server reference).
- [ ] **Single-server baseline?** → M/M/1 (02). Establish the latency vs. ρ curve.
- [ ] **Multiple parallel servers?** → M/M/c / Erlang-C (03) for minimum c; Allen-Cunneen for non-exponential service; square-root staffing to sanity-check the scale effect.
- [ ] **Which discipline?** FCFS, processor sharing, or loss. Variance inflation (P-K, Kingman) applies to FCFS waits only.
- [ ] **Service time non-exponential (CV² ≠ 1)?** → P-K (04) for Poisson arrivals; Kingman (07) for non-Poisson arrivals.
- [ ] **Bursty arrivals (CV²_a > 1)?** → Kingman (07). M/M/1 will underestimate latency.
- [ ] **Multi-stage pipeline?** → Jackson networks (06). Solve flow balance; find highest-ρ stage.
- [ ] **Scaling horizontally?** → USL (09). Fit σ and κ from load-test series; check N_max.
- [ ] **Mixed SLO classes in one pool?** → Priority queues (05). Separate classes; analyze each.
- [ ] **High latency but good throughput?** → Bufferbloat (08). Check queue depth; apply AQM or finite bounds.
- [ ] **Drop-on-busy (no queue)?** → Erlang-B (10). Compute blocking probability B(c, a).
- [ ] **Fan-out / parallel scatter-gather?** → Fork-join (11). Compute the joint maximum; use E[S] × H_K only for iid exponential service.
- [ ] **Sanity-check any result?** → Little's Law (01). Verify L = λ × W is consistent with measurements.
- [ ] **Tail latency SLO on multi-stage pipeline with non-Poisson arrivals?** → Jackson networks (06) + Ciucu-Mehri tandem sojourn bounds (SIGMETRICS 2025). Mean Jackson analysis understates tail risk when CV²_a ≠ 1.
- [ ] **Does admitted work hold a growing resource until it completes (KV cache, session buffers)?** → Single-resource ρ is insufficient. Check the joint compute-and-memory stability condition and the eviction/limit-cycle risk before trusting any ρ < 1 result (see [Misuse Boundaries](#misuse-boundaries)).

## Anti-Patterns

| Anti-Pattern | Queueing Theory Diagnosis | Fix |
|-------------|--------------------------|-----|
| **Ignoring service-time variability (CV²) on G/G/1 systems** | M/M/1 assumes CV²=1; under Poisson arrivals, service CV²>1 inflates FCFS mean Wq by (1+CV²)/2; general arrivals also need CV²_a | Measure service-time distribution; apply P-K (04) or Kingman (07) |
| **M/M/1 used at ρ near 1 without USL retrograde check** | M/M/1 predicts infinite latency but doesn't account for coherency degradation when c is added | Fit USL (09) from multi-server load tests before committing to scaling decision |
| **Little's Law applied across non-stationary windows** | Long-run Little's Law also covers time-varying sample paths; naive finite-window products omit boundary work | Check stationarity and boundary effects across representative windows; analyze transients separately |
| **Erlang-C confused with Erlang-B for queueing decisions** | Erlang-B models drop/loss (no queue); Erlang-C models queuing (wait, don't drop) | Determine whether the system queues or blocks; select model accordingly (03 vs 10) |
| **Fork-join sized by mean worker time rather than max** | Completion depends on the joint maximum of branch response times | Use the iid-exponential harmonic baseline only under its assumptions; include worker waiting and dependence |
| **Unbounded application queues (bufferbloat)** | Large buffers absorb spikes silently; latency accumulates without 503/backpressure signal | Set finite queue depth from a delay budget and measured drain rate; add AQM or backpressure |
| **Scaling pipeline stage without re-solving flow balance** | Jackson network bottleneck shifts to next highest-ρ stage after scaling | Re-run flow-balance equations after each scaling action; re-identify bottleneck |
| **Using FCFS when job-size predictions are available** | FCFS ignores size information; prediction-based size scheduling can cut mean response time, but plain SPRPT has no constant-factor guarantee under prediction error | Use a variant with a proven bound (SPRPT-with-bounce or PSPJF; Scully, Grosof & Mitzenmacher, ITCS 2022). For LLM serving, Trail limits preemption to young requests (Shahout et al., arXiv 2410.01035) |

## Composition Recipes

### Recipe 1 — Capacity Plan for a New Service

_Goal: Size server pool before launch._

1. **Little's Law (01)**: derive initial L, λ, W relationship from design requirements.
2. **M/M/c (03)**: find minimum c so that Erlang-C wait meets the SLO.
3. **Allen-Cunneen**: inflate Wq(M/M/c) by measured (CV²_a + CV²_s)/2; re-check c.
4. **USL (09)**: validate that the c-server pool achieves near-linear scaling (κ ≈ 0).

_Standout insight_: size c from the SLO, not from a ρ target. At λ = 0.5/s and E[S] = 240 s (a = 120 Erlangs) with a mean-wait SLO of 3 s, Erlang-C needs 134 servers (Wq ≈ 2.48 s, ρ ≈ 0.90; 133 gives 3.15 s) while a ρ ≤ 0.70 rule buys 172 ([worked example](references/multiserver-overload-and-disciplines.md)); a variability factor above 1 then adds servers back (Allen-Cunneen).

### Recipe 2 — Saturation SLO Alert Threshold

_Goal: Determine the utilization ρ* at which latency will breach SLO, and set an alert before it happens._

1. **M/M/1 (02)**: solve W(ρ) = SLO_target; find ρ* (first-pass, exponential baseline).
2. **Kingman (07)**: recompute ρ* with measured CV²_a and CV²_s. The drop in ρ* depends on the SLO and the variability; compute it, do not assume a percentage.
3. **Bufferbloat (08)**: confirm that queue depth monitoring is in place; standing queues are the first signal.
4. **Little's Law (01)**: set alert on Lq = λ × Wq_threshold; queue depth is a leading indicator of latency breach.

Queue depth can give an earlier signal than an aggregated latency percentile, but Little's Law relates means. Validate the alert threshold against observed p99; it cannot certify a percentile SLO.

### Recipe 3 — Multi-Stage Pipeline Bottleneck Hunt

_Goal: Find and fix the throughput bottleneck in a microservice chain, then verify the fix didn't shift the bottleneck._

1. **Jackson networks (06)**: instrument each stage; collect λᵢ, μᵢ, cᵢ; solve flow-balance equations; rank by ρᵢ.
2. **M/M/c (03)**: compute servers needed at bottleneck station i for the stated waiting/service SLO, arrival/service assumptions and uncertainty margin; choose utilization headroom from workload validation.
3. **USL (09)**: after scaling station i, verify new ρ distribution; check for retrograde at any stage.
4. **Priority queues (05)**: if multiple SLO classes converge at the bottleneck, separate into priority lanes.

_Standout insight_: The Jackson product-form result means each stage can be analyzed independently — but only after solving the traffic equations. Teams that scale one stage without re-solving flow balance routinely move the bottleneck downstream without knowing it.

### Recipe 4 — Memory-Coupled Service (LLM serving and similar)

When admitted work holds a resource that grows with service progress and frees only at completion (KV cache, session buffers), a compute-only ρ < 1 does not prove stability. Check the joint compute-and-memory condition (Nie, Si & Zhou, ICML 2026), admission-control on projected peak occupancy, and watch for eviction limit cycles under homogeneous lengths (Ao, Dong, Luo & Simchi-Levi 2026). Mean-wait formulas cannot certify TTFT or TPOT percentiles. The full LLM serving recipe (scheduling policy, Trail, autoscaling, fleet simulation) lives in `ai-llm-inference/references/queueing-theory-applied.md`.

## Workflow

1. Identify the failure mode (saturation, variance, scaling cliff, fan-out slowdown, blocking).
2. Use the [Decision Checklist](#decision-checklist) to map failure mode → primitive.
3. Open the primitive playbook in [assets/templates/queueing-theory/](assets/templates/queueing-theory/) for definition, inputs, outputs, worked example.
4. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) or the full [assets/templates/queueing-theory/README.md](assets/templates/queueing-theory/README.md).
5. Validate results with Little's Law (01) — the universal consistency check.
6. Use the bundled finite-trace simulator when measured arrival/service pairs and fixed FCFS capacity are enough. Extend the event model or use a specialist simulator when finite buffers, priorities, retries, changing capacity, or shared resources matter.

## Trace-Driven Simulation

Use this mode when observed burstiness or service-time variation makes a closed-form approximation too weak, while a fixed-capacity FCFS replay can answer the decision.

- **Input:** CSV rows with `arrival_time,service_time` and optional `job_id`; paired row values remain together.
- **Command:** Run from this skill directory: `python3 scripts/queue_trace_simulator.py --input data/example-fcfs-trace.csv --servers 1`
- **Output:** JSON with the explicit observation interval, busy/capacity time, utilization, queue integral and maximum, empirical wait/response quantiles, and deterministic job assignments.
- **Boundary:** This is one finite trace from an empty initial state. It provides no steady-state estimate or confidence interval. Use algebra when its assumptions suffice; define a validated stochastic model with warm-up, seeds, replications, and diagnostics before making population uncertainty claims.

Read [references/trace-driven-simulation.md](references/trace-driven-simulation.md) for validation rules, tie handling, the measurement denominator, output semantics, limitations, and a hand-computed example.

## Related Skills

- `foundations-distributed-systems`: the retry/timeout sustaining loop behind metastable failures.
- `foundations-theory-of-constraints`: bottleneck management once the queueing model has named the constraint.
- `foundations-reliability-theory`: availability and error-budget arithmetic.
- Domain applications: `*/references/queueing-theory-applied.md` in consuming skills link back here.

## Navigation

- Decision and validation worksheet (intake, model boundaries, checkable examples): [references/decision-and-validation.md](references/decision-and-validation.md); regression prompts: [`data/regression-cases.json`](data/regression-cases.json)
- Per-primitive playbooks: [assets/templates/queueing-theory/](assets/templates/queueing-theory/); composition guide: [README.md](assets/templates/queueing-theory/README.md)
- Multi-server sizing, disciplines and overload: [references/multiserver-overload-and-disciplines.md](references/multiserver-overload-and-disciplines.md)
- Formal theory map and scheduling research notes: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Primitives overview by domain: [references/primitives-overview.md](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json)

## Domain Verification Notes

- Formulas come from the primary sources in `data/sources.json` (Kleinrock 1975/1976, Harchol-Balter 2013, Cooper 1981). Recompute any worked-example number with a script before reusing it as a benchmark.
- Stationary Erlang-C is not a universal bound on transient capacity. Initial backlog, server state, horizon and target decide whether it over- or underestimates need; use a transient model or trace simulation.
- USL σ and κ are system-specific and must be fitted (with residuals) from load tests.
- Kingman and Allen-Cunneen are approximations; accuracy degrades at low ρ. Use P-K for exact M/G/1 FCFS means.
- Erlang-B and Erlang-C assume Poisson arrivals. With bursty or dependent arrivals, compare against a fitted non-Poisson model or trace simulation.
- Fork-join E[max] = E[S] × H_K is exact only for independent exponential service without waiting.
- Multiserver scheduling results (SRPT-k no longer mean-optimal; tail-optimal policies depend on load) are summarized in [references/formal-theory-map.md](references/formal-theory-map.md).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
