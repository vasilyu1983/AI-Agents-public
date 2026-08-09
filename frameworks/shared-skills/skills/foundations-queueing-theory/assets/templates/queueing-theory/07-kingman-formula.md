# Primitive 07 — Kingman's Formula (Heavy-Traffic G/G/1 Approximation)

**Source**: Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.

## Definition

**Kingman's formula** approximates the mean queue wait for a **G/G/1** queue — general inter-arrival times and general service times — under moderate-to-heavy traffic. It is the standard formula for real-world systems where neither arrivals nor service are Poisson/exponential.

```
Wq ≈ (ρ / (1 − ρ)) × ((CV²_a + CV²_s) / 2) × E[S]
```

| Symbol | Meaning |
|--------|---------|
| ρ | Server utilization = λ / μ |
| CV²_a | Coefficient of variation squared of inter-arrival times |
| CV²_s | Coefficient of variation squared of service times |
| E[S] | Mean service time = 1/μ |

### Relationship to M/M/1

When CV²_a = CV²_s = 1 (Poisson arrivals, exponential service):
```
Wq = (ρ / (1 − ρ)) × E[S]  =  ρ / (μ − λ)
```
— which exactly matches the M/M/1 result. Kingman is a generalization.

### The Variability Factor

```
VF = (CV²_a + CV²_s) / 2
```

| VF | Queue wait vs. M/M/1 |
|----|----------------------|
| 0.5 | 50% of M/M/1 (less variable) |
| 1.0 | Equal to M/M/1 |
| 2.0 | 2× M/M/1 |
| 5.0 | 5× M/M/1 — common in LLM/batch systems |

## When to Use

- **Real-world service timing**: HTTP request arrivals are bursty (CV²_a > 1); LLM/DB/batch service times are variable (CV²_s >> 1).
- **SLO prediction for heterogeneous workloads**: when M/M/1 under-predicts observed latency.
- **Backpressure tuning**: quantify how much queue depth reduces if arrival burstiness is smoothed.
- **Capacity planning under real traffic**: measure CV²_a and CV²_s from production histograms, apply Kingman.

Do NOT treat Kingman as exact; it is an asymptotic (heavy-traffic) approximation. For ρ < 0.5, errors can be significant. For ρ > 0.9, Kingman is tightest. Use simulation for critical capacity decisions.

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Mean arrival rate | λ | Telemetry |
| Mean service time | E[S] | APM / profiling |
| CV² of inter-arrival times | CV²_a | Compute from inter-arrival time histogram |
| CV² of service times | CV²_s | Compute from service-time histogram |

**Computing CV²_a in practice**: collect a sample of inter-arrival times {t₁, t₂, ...}. CV²_a = Var/Mean² = σ²/μ².

For Poisson arrivals, CV²_a = 1. For scheduled batch releases, CV²_a ≈ 0. For bursty HTTP, CV²_a often 2–5.

## Outputs

- **Wq**: approximated mean queue wait.
- **W**: Wq + E[S] (total latency).
- **Sensitivity analysis**: how much Wq changes with ±1 CV² unit.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Applying Kingman at low ρ | Heavy-traffic approximation inaccurate for ρ < 0.5 | Use simulation or M/G/1 P-K formula (primitive 04) |
| Ignoring CV²_a (assuming Poisson arrivals) | Bursty arrivals inflate Wq beyond M/M/1 prediction | Measure and include CV²_a; smooth arrivals with rate-limiting |
| Treating Kingman as exact | Up to 30% error possible even in valid regime | Treat as order-of-magnitude guide; validate with simulation |
| Using Kingman for multi-server G/G/c | Formula is G/G/1 only | Scale E[S] by 1/c as an approximation, or use Whitt's heavy-traffic G/G/c bound |

## Worked Example

A task-processing service:
- λ = 80 jobs/s, E[S] = 10 ms → ρ = 0.80
- Inter-arrival times are bursty (cloud function triggers): CV²_a = 3.0
- Job durations vary widely (database lookups): CV²_s = 2.0

```
VF   = (3.0 + 2.0) / 2 = 2.5
Wq ≈ (0.80 / 0.20) × 2.5 × 0.010
   = 4.0 × 2.5 × 0.010
   = 0.100 s = 100 ms
W   = 100 + 10 = 110 ms
```

Compare to M/M/1 (VF = 1.0):
```
Wq(M/M/1) = (0.80/0.20) × 1.0 × 0.010 = 40 ms
```

The actual queue wait is **2.5× higher** than M/M/1 would predict, due to variability in arrivals and service. The fix is to smooth arrivals (rate-limit to reduce CV²_a) or reduce variance in job size (split into fast/slow lanes with priority).

## Composition

- **M/M/1** (primitive 02): Kingman generalizes M/M/1; use M/M/1 when CV²_a = CV²_s = 1.
- **P-K formula** (primitive 04): M/G/1 case (Poisson arrivals, general service). Kingman further generalizes to non-Poisson arrivals.
- **Bufferbloat** (primitive 08): Kingman Wq at high ρ shows why large buffers accumulate: queue depth L = λ × Wq.
- **Little's Law** (primitive 01): verify Lq = λ × Wq after computing Wq.

## Sources

- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Chapter 4.
- Whitt, W. (1993). "Approximations for the GI/G/m queue." *Production and Operations Management*, 2(2), 114–161.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. _(Corrected 2026-07-11: a prior version cited "Ch. 27," which is the book's power-optimization application chapter and does not cover the G/G/1 heavy-traffic approximation. This book does not have a dedicated chapter matching Kingman's result; treat Kingman (1961) and Whitt (1993) below as the primary sources for this primitive.)_
