# Primitive: System Reliability

## Definition

**System reliability** is the probability that a system performs its required function for a specified time under specified conditions. It is the aggregate reliability produced by the arrangement and individual reliabilities of the system's components.

The three canonical structural models:

| Model | Topology | System works when... | Formula |
|-------|----------|---------------------|---------|
| Series | All components in a single chain | Every component works | R_s = ∏ Rᵢ |
| Parallel | All components in a redundant bank | At least one component works | R_p = 1 - ∏(1 - Rᵢ) |
| Mixed | Nested series and parallel sub-systems | Depends on topology | Decompose recursively |

An extension adds **imperfect coverage** — the switchover/detection mechanism that allows the parallel path to activate may itself fail. See primitive 07.

## When to Use

- Computing system-level reliability from component-level data before building the system.
- Comparing design alternatives with different topologies.
- Identifying the weakest link in a series chain.
- Checking whether adding parallel redundancy achieves the target — and whether the topology assumption holds.
- Input to reliability allocation (primitive 11): allocate targets based on where the topology constrains the system.

## Inputs

| Input | Description |
|-------|-------------|
| Component reliabilities Rᵢ | Per-component reliability at mission time t (from primitive 01 or 09) |
| System block diagram | Topology: which components are in series vs. parallel paths |
| Common-cause beta factor | β_CCF: fraction of parallel failures attributable to common cause |
| Coverage probability c | For standby redundancy (primitive 07) |

## Outputs

- R_system at the specified mission time.
- Block diagram annotated with per-block contributions.
- Sensitivity ranking: which components, if improved, most increase R_system.
- Required component reliability to meet a system target (inverse allocation).

## Core Formulas

### Series

```
R_series(t) = R₁(t) × R₂(t) × ... × Rₙ(t)
```

The series system is weakest-link: improving the weakest component yields the largest gain.

### Parallel (Active, Independent)

```
R_parallel(t) = 1 - (1 - R₁(t))(1 - R₂(t))...(1 - Rₙ(t))
```

For identical components:

```
R_parallel = 1 - (1 - R)^n
```

### Mixed — Recursive Decomposition

1. Identify independent blocks (sub-networks that share no components with the rest).
2. Compute each block's reliability using series or parallel formula.
3. Treat each block as a single component; repeat until only top-level series or parallel remains.

### Common-Cause Failure Adjustment (Beta-Factor Model)

When redundant components share a failure mechanism (same software version, same power rail):

```
R_adjusted = R_independent × (1 - β) + β × R_single
```

where β is the fraction of failure rate attributable to common cause. Typical β values: 0.02–0.20 depending on diversity of design.

### Series System with IFR Components

When components have β > 1 (Weibull, primitive 09), the exponential series formula is incorrect. Use:

```
R_series(t) = ∏ exp(-(t/ηᵢ)^βᵢ)
```

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Treating correlated failures as independent in parallel formula | Overestimates R_parallel by orders of magnitude | Apply beta-factor or explicit common-cause model |
| Applying series formula to a mixed topology | Wrong result; may underestimate or overestimate system reliability | Draw the reliability block diagram first; decompose into blocks |
| Using availability (time-averaged) when the mission-time model is needed | Confuses A = MTBF/(MTBF+MTTR) with R(t) = exp(-λt) | Use R(t) for mission-time analysis; use A for steady-state operations |
| Ignoring interface reliability | Physical connectors, APIs, and network paths have their own failure rates | Explicitly model interfaces as series components |
| Treating the whole system as series when parallel paths exist | Underestimates reliability; wrong improvement investments | Enumerate all paths through the system; use path-tracing or inclusion-exclusion |

## Worked Example

A data pipeline has:
- Ingestion service: R = 0.9990 (in series — must work)
- Processing cluster: two nodes active-active, R = 0.9980 each (parallel)
- Storage layer: R = 0.9995 (in series — must work)

**Parallel processing block:**

```
R_proc = 1 - (1 - 0.9980)^2 = 1 - (0.002)^2 = 1 - 0.000004 = 0.999996
```

**Series composition:**

```
R_system = R_ingest × R_proc × R_storage
         = 0.9990 × 0.999996 × 0.9995
         = 0.99850   (99.85%)
```

**Common-cause adjustment for processing cluster (β = 0.05, same codebase):**

```
R_proc_cc = 0.999996 × (1 - 0.05) + 0.05 × 0.9980
          = 0.999996 × 0.95 + 0.05 × 0.9980
          = 0.94999620 + 0.04990
          ≈ 0.99990
```

Revised system: 0.9990 × 0.99990 × 0.9995 ≈ **0.99840**. The common-cause adjustment costs ~0.001 availability.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment*.
- IEC 61508-6 (2010). *Functional safety of E/E/PE safety-related systems — Part 6: Guidelines on IEC 61508-2 and IEC 61508-3*. (Common-cause failure beta-factor guidance.)
