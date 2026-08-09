# Primitive: Availability Formulas

## Definition

**Availability** is the fraction of time a system is operational and capable of performing its required function. It is the fundamental metric that bridges MTBF/MTTR to contractual SLOs.

Three availability concepts matter:

- **Inherent availability (Ai)**: excludes logistics and administrative delays; uses only active repair time.
- **Operational availability (Ao)**: includes all downtime sources; the number users experience.
- **Steady-state availability (A)**: the standard engineering approximation, used when the system is repairable and has reached statistical steady state.

## When to Use

- Translating MTBF/MTTR figures into a service-level percentage.
- Combining component availabilities into system availability (series and parallel).
- Checking whether a proposed redundancy scheme achieves an availability target.
- Allocating an availability requirement to subsystems (feeds into primitive 11).

## Inputs

| Input | Description |
|-------|-------------|
| MTBF | Mean time between failures (primitive 01) |
| MTTR | Mean time to repair (primitive 01) |
| Topology | Series, parallel, or mixed (primitive 10) |

## Outputs

### Point Formula

```
A = MTBF / (MTBF + MTTR)
```

Equivalently:

```
A = 1 - (MTTR / (MTBF + MTTR))
```

### Series Composition

Components in series all must be up for the system to work:

```
A_series = A1 × A2 × A3 × ... × An
```

Each component degrades availability multiplicatively. A series system is always less available than its least-available component when any A < 1.

### Parallel Composition (Active Redundancy)

At least one of n identical, independent components must be up:

```
A_parallel = 1 - (1 - A)^n
```

For two non-identical components:

```
A_parallel = 1 - (1 - A1)(1 - A2)
```

### Mixed (Typical Service Stack)

Decompose into series paths and parallel groups, apply series formula within each path, then parallel formula across redundant paths.

```
Example: Load balancer (series) → two redundant app servers (parallel) → DB cluster
A_system = A_lb × [1 - (1-A_app)^2] × A_db
```

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Treating correlated failures (same DC, shared power) as independent | Parallel formula drastically overstates availability | Model common-cause factor; use primitive 10's imperfect-coverage extension |
| Mixing inherent and operational availability in the same formula | Inconsistent results that confuse SLO design | Pick one definition and apply it uniformly |
| Forgetting switchover time in active/standby redundancy | Actual MTTR includes failover time; availability is lower than formula implies | Add switchover latency to MTTR before computing |
| Treating the series formula as additive | Series availability is not the average; each component multiplies | Use A1 × A2, not (A1 + A2)/2 |
| Applying steady-state formula to brand-new systems | Infant-mortality phase (bathtub left tail) has higher failure rates | Run burn-in or apply Weibull early-phase adjustment (primitives 03, 04) |

## Worked Example

A three-tier web service: CDN, two app servers (active-active), and one database.

```
CDN availability:      A_cdn  = 0.9999
App server (each):     A_app  = 0.9990
Database:              A_db   = 0.9995

Parallel app layer:    A_apps = 1 - (1 - 0.9990)^2 = 1 - (0.001)^2 = 1 - 0.000001 = 0.999999

System availability:   A = 0.9999 × 0.999999 × 0.9995
                         = 0.9999 × 0.999999 × 0.9995
                         ≈ 0.99940

Annual downtime:       (1 - 0.99940) × 8,760 h = 0.0006 × 8,760 ≈ 5.3 hours/year
```

The database at 0.9995 is the availability bottleneck. Redundancy on the app layer bought only ~0.9 hours of improvement. To reach 0.9999 system availability, the database must improve.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- Beyer, B. et al. (2016). *Site Reliability Engineering*. O'Reilly. Chapter 4 (error-budget model).
