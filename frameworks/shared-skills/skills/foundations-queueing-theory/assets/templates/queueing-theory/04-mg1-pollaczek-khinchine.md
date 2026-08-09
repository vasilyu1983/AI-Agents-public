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
- **Database query latency modeling**: query times typically have CV² > 2 due to mixed fast and slow queries.

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
| Using P-K for multi-server system | P-K is M/G/1 only | Use M/G/c approximation or simulation for c > 1 |

## Worked Example

An LLM inference service receives **10 req/s** (λ = 10). Service times vary widely:

| Request type | Fraction | Duration |
|-------------|----------|---------|
| Short (chat) | 70% | 0.5 s |
| Long (document) | 30% | 3.0 s |

```
E[S]  = 0.7 × 0.5 + 0.3 × 3.0 = 0.35 + 0.90 = 1.25 s
E[S²] = 0.7 × 0.25 + 0.3 × 9.0 = 0.175 + 2.70 = 2.875 s²
CV²   = 2.875 / 1.25² − 1 = 2.875/1.5625 − 1 = 1.84 − 1 = 0.84
ρ     = λ × E[S] = 10 × 1.25 = 12.5  ← UNSTABLE (ρ > 1)
```

Capacity insufficient for 10 req/s. Scale to 2 servers or reduce E[S]. Suppose service is capped to 5 req/s (λ = 5):

```
ρ     = 5 × 1.25 = 6.25  ← still unstable
```

Needs at minimum **9 servers** for M/M/c (ρ per server < 1) or a **14-server pool** for ρ = 0.7. CV² = 0.84 increases wait by factor (1 + 0.84)/2 = 0.92 vs. exponential — a modest 8% savings over pure M/M/1 at same load. But note: if the long-tail fraction were heavy (Pareto), CV² >> 1 would dominate.

## LLM Inference as M/G/1 with Predicted Service Times

LLM inference is a canonical M/G/1 system: Poisson (or near-Poisson) request arrivals, highly variable service times (output token count unknown at arrival).

**Mapping:**
- Service time S = output_tokens × time_per_token. Because output length is unknown at request arrival, this is a G (general) service-time distribution — not exponential.
- The decode phase (token-by-token generation) is the dominant service component; the prefill phase (prompt processing) has more deterministic duration and can be modeled separately as a near-deterministic M/G/1.

**Prediction-augmented scheduling (SPRPT):** When output token lengths can be predicted (e.g., from prompt features or a length predictor), use SPRPT (Shortest Predicted Remaining Processing Time) — an extension of SRPT to the case of uncertain job sizes. Mitzenmacher & Shahout (Stochastic Systems 2025) prove graceful degradation under bounded multiplicative prediction error: if predictions are within a factor β of true lengths, mean wait time degrades by at most a function of β.

**Trail policy (KV-cache-aware):** Standard preemptive SRPT would re-compute KV cache on resumption, incurring significant overhead. The "Trail" policy (Mitzenmacher & Shahout 2025) disables preemption after a request has been in service for `c × predicted_size` time units, converting to non-preemptive beyond that age threshold. This is analyzable via the SOAP framework and avoids KV-cache re-compute cost.

**Kill criterion for Trail policy:** Drop if KV-cache re-compute cost is less than ~5% of total request latency for the specific model/hardware — the age-threshold rule then adds scheduling complexity without latency benefit.

See also: primitive 05 (Trail policy in priority queue context), Recipe 4 (LLM Inference Capacity Sizing).

## Composition

- **Kingman's formula** (primitive 07): the G/G/1 generalization — use Kingman when both arrivals and service are non-Poisson/non-exponential.
- **Priority queues** (primitive 05): separate high-variability request classes into priority lanes to protect low-CV classes.
- **M/M/1** (primitive 02): degenerate case CV² = 1; P-K reduces to M/M/1 result.

## Sources

- Pollaczek, F. (1930). "Über eine Aufgabe der Wahrscheinlichkeitstheorie." *Mathematische Zeitschrift*, 32(1), 64–100.
- Khinchine, A. Y. (1932). "Mathematical theory of a stationary queue." *Matematicheskii Sbornik*, 39(4), 73–84.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Chapter 4 (P-K formula derivation).
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Chapter 23 ("The M/G/1 Queue and the Inspection Paradox"); Chapters 25–26 for transform-based derivations. _(Corrected 2026-07-11: prior text cited Chapters 15–16, which cover server-farm capacity provisioning and time-reversibility, not M/G/1.)_
