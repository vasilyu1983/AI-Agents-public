# Primitive 04 — M/G/1 Queue and the Pollaczek-Khinchine (P-K) Formula

**Source**: Pollaczek, F. (1930); Khinchine, A. (1932); Kleinrock (1975), Vol. 1 Ch. 4.

## Definition

The **M/G/1 queue** relaxes the exponential service-time assumption:

- **M**: Poisson arrivals, rate λ.
- **G**: General (arbitrary) service-time distribution with mean E[S] = 1/μ and second moment E[S²].
- **1**: Single server.

**Coefficient of variation of service time**:

```
CV² = Var[S] / E[S]²  =  E[S²] / E[S]² − 1
```

### Pollaczek-Khinchine (P-K) Mean Value Formula

```
Wq = (λ × E[S²]) / (2 × (1 − ρ))
   = (ρ × E[S] × (1 + CV²)) / (2 × (1 − ρ))
```

The mean queue wait **Wq** depends on both utilization ρ and the second moment of service time. High variability (CV² > 1) directly inflates latency even at low utilization.

| Service distribution | CV² | Queue wait vs. M/M/1 |
|---------------------|-----|----------------------|
| Deterministic (D) | 0 | Wq(D) = ½ × Wq(M/M/1) |
| Exponential (M) | 1 | Wq(M) = Wq(M/M/1) (baseline) |
| Hyper-exponential | > 1 | Wq > Wq(M/M/1) |
| Long-tail / Pareto | >> 1 | Wq >> M/M/1; tail latency explodes |

## When to Use

- **Any real service with non-exponential durations**: disk I/O, LLM inference (highly variable completion lengths), batch jobs, GC pause times.
- **Identifying variance as the bottleneck**: when ρ is low but latency is high, CV² is the suspect.
- **Sizing effect of service-time capping**: if you cap large requests (reduce E[S²]), P-K quantifies the latency gain.
- **Database query latency modeling**: mixed fast and slow queries often give CV² > 1; measure it rather than assuming a value.

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Arrival rate | λ | Telemetry |
| Mean service time | E[S] = 1/μ | Profiling / APM |
| Second moment of service time | E[S²] | Computed from histogram or raw data |
| Coefficient of variation | CV² | E[S²]/E[S]² − 1 |

**Computing E[S²] in practice**: from a service-time histogram or sample, E[S²] = mean(s_i²) over all observations.

## Outputs

- **Wq**: mean wait time in queue.
- **W**: mean total time in system = Wq + E[S].
- **Sensitivity to variance**: (1 + CV²)/2 multiplier shows how much variance inflates latency.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Assuming M/M/1 when CV² >> 1 | Underestimates actual latency | Measure service-time distribution; apply P-K |
| Ignoring long-tail service times | A few large requests inflate E[S²] massively | Isolate outlier request classes; apply separate queues or priority (primitive 05) |
| Capping latency SLO at mean | P99 can be orders of magnitude above mean when CV² > 2 | Model tail with heavy-tail distributions; apply size-based scheduling |
| Using P-K for multi-server system | P-K is M/G/1 only | Use Allen-Cunneen (M/G/c approximation) or simulation for c > 1 |
| Applying P-K to a processor-sharing server | P-K is for FCFS; M/G/1-PS mean response is E[S]/(1−ρ), insensitive to CV² | Identify the discipline first; see [`multiserver-overload-and-disciplines.md`](../../../references/multiserver-overload-and-disciplines.md) |

## Worked Example

An LLM inference replica (one request in service at a time) receives **0.6 req/s** (λ = 0.6). Service times vary widely:

| Request type | Fraction | Duration |
|-------------|----------|---------|
| Short (chat) | 70% | 0.5 s |
| Long (document) | 30% | 3.0 s |

```
E[S]  = 0.7 × 0.5 + 0.3 × 3.0 = 1.25 s
E[S²] = 0.7 × 0.25 + 0.3 × 9.0 = 2.875 s²
CV²   = 2.875 / 1.25² − 1 = 0.84
ρ     = λ × E[S] = 0.6 × 1.25 = 0.75
Wq    = λ × E[S²] / (2(1 − ρ)) = 0.6 × 2.875 / 0.5 = 3.45 s
M/M/1 at the same ρ: Wq = ρ/(1−ρ) × E[S] = 3.75 s
```

The variability factor (1 + CV²)/2 = 0.92 is below 1, so this two-point mix *lowers* the wait by 8% relative to exponential service. A Pareto-like tail with CV² ≫ 1 would reverse the sign and dominate.

**If the same traffic were 10 req/s:** offered load a = λ·E[S] = 12.5 Erlangs, so no single server is stable and P-K no longer applies. At least **13** servers are needed for stability (a/c < 1). Size the pool for the wait SLO with Erlang-C plus the Allen-Cunneen variability correction, not with a fixed ρ target; see [`../../../references/multiserver-overload-and-disciplines.md`](../../../references/multiserver-overload-and-disciplines.md).

## LLM Inference as M/G/1 with Predicted Service Times

Use M/G/1 for LLM inference only when one request runs at a time, arrivals are Poisson, and service times are iid and independent of arrivals. Continuous batching and KV-memory coupling require a richer model (see SKILL.md, Memory-Coupled Service).

**Mapping:**
- Service time S = output_tokens × time_per_token. Because output length is unknown at request arrival, this is a G (general) service-time distribution — not exponential.
- Measure prefill and decode demands separately; neither decode dominance nor deterministic prefill follows from the queueing model. Check shared-resource coupling before treating phases as independent queues.

**Prediction-augmented scheduling (SPRPT):** When output lengths can be predicted, SPRPT (Shortest Predicted Remaining Processing Time) ranks jobs by predicted remaining size. Plain SPRPT does **not** guarantee graceful degradation: even with bounded multiplicative prediction error, its mean response time is not bounded within a constant factor of SRPT. The bound holds for the **SPRPT-with-bounce** variant, whose rank rises again after reaching zero (constant C = 3.5), and for PSPJF (C = 1.5), under bounded multiplicative error (Scully, Grosof & Mitzenmacher, ITCS 2022, as summarized in the Mitzenmacher & Shahout review, *Stochastic Systems* 2025, arXiv 2503.07545).

**Trail policy (KV-cache-aware):** Trail (Shahout, Malach, Liu, Jiang, Yu & Mitzenmacher, arXiv 2410.01035) combines embedding-based output-length prediction with limited preemption. Preemption is cheap early in a request, when its KV cache is small; late in a request, preempting means holding or re-allocating a large KV cache. Trail therefore disables preemption once a request's age exceeds `c × predicted_size` (0 ≤ c ≤ 1). The Mitzenmacher & Shahout review states this rule and notes that a simplified M/G/1 version is analyzable with SOAP methods.

**When not to use Trail:** if preemption is already cheap on your engine (small KV footprint, fast swap), the age threshold adds complexity for little gain. Measure the preemption memory cost before adopting it.

See also: primitive 05 (Trail policy in priority queue context); LLM serving capacity sizing is owned by `ai-llm-inference`.

## Composition

- **Kingman's formula** (primitive 07): the G/G/1 generalization — use Kingman when both arrivals and service are non-Poisson/non-exponential.
- **Priority queues** (primitive 05): separate high-variability request classes into priority lanes to protect low-CV classes.
- **M/M/1** (primitive 02): degenerate case CV² = 1; P-K reduces to M/M/1 result.

## Sources

- Pollaczek, F. (1930). "Über eine Aufgabe der Wahrscheinlichkeitstheorie." *Mathematische Zeitschrift*, 32(1), 64–100.
- Khinchine, A. Y. (1932). "Mathematical theory of a stationary queue." *Matematicheskii Sbornik*, 39(4), 73–84.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Chapter 4 (P-K formula derivation).
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Chapter 23 ("The M/G/1 Queue and the Inspection Paradox"); Chapters 25–26 for transform-based derivations. _(Corrected 2026-07-11: prior text cited Chapters 15–16, which cover server-farm capacity provisioning and time-reversibility, not M/G/1.)_
