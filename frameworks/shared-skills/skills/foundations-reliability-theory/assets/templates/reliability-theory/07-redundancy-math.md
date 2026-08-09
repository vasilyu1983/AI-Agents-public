# Primitive: Redundancy Math

## Definition

**Redundancy** is the provision of extra components or paths beyond the minimum needed for system function, so that the system continues operating when some components fail.

Four redundancy architectures and their reliability formulae:

### 1. Active (Hot) Redundancy — k-of-n

All n components operate simultaneously. The system works if at least k of n are working.

```
R_system = Σᵢ₌ₖⁿ C(n,i) × Rᵢ × (1-R)^(n-i)    [for identical components]
```

Special case (1-of-2, identical):

```
R = 2R - R²   =   1 - (1-R)²
```

Special case (1-of-n, identical):

```
R = 1 - (1-R)^n
```

### 2. Passive (Cold/Standby) Redundancy

One component is active; backups are powered off until needed. Requires a switchover mechanism.

```
R_standby(t) = e^(-λt) × [1 + λt + (λt)²/2! + ... + (λt)^(n-1)/(n-1)!]   [for n-unit system, identical λ]
```

Standby achieves **higher reliability than active redundancy** for the same n because standby units do not accumulate failure exposure while idle — provided the switching mechanism is reliable.

### 3. m-out-of-n (k-of-n general form)

The system requires at least m of n components to function. Computed by the binomial summation above with k = m.

```
R_m/n = Σᵢ₌ₘⁿ C(n,i) × Rᵢ × (1-R)^(n-i)
```

**2-of-3 majority vote** (common in safety systems):

```
R_2/3 = 3R² - 2R³
```

### 4. Imperfect Coverage Redundancy

The redundancy switch or detection mechanism fails with probability (1 - c):

```
R_covered = c × R_parallel + (1-c) × R_single
```

When coverage c is low, adding redundancy can *decrease* system reliability.

## When to Use

- Deciding how many replicas to provision for a target availability.
- Choosing between active and standby redundancy architectures.
- Evaluating whether a switchover mechanism's reliability undermines the redundancy benefit.
- Sizing k in a voting system (majority logic, quorum).
- Checking that adding redundancy actually helps — low-coverage architectures can hurt.

## Inputs

| Input | Description |
|-------|-------------|
| Component reliability R | Per-unit reliability at the mission time (from primitive 01/02) |
| Architecture type | Active, standby, m-of-n |
| n | Number of redundant units |
| Coverage probability c | Reliability of the detection/switchover mechanism |

## Outputs

- System reliability R_system for each architecture option.
- Minimum n required to achieve a reliability target.
- Coverage sensitivity: how much c must degrade before redundancy becomes harmful.

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Ignoring switchover failure | Standby redundancy appears better than it is; failover fails in production | Model switchover reliability explicitly; include in system reliability formula |
| Assuming independence of redundant components | Common-cause failures (shared power, shared software, same datacenter) are underestimated | Use beta-factor or alpha-factor common-cause models |
| Using active redundancy when standby is available | Wasted compute; higher component failure exposure during idle period | Evaluate standby architectures for non-performance-critical backups |
| Adding redundancy without fixing coverage | Low-coverage redundancy scheme reduces reliability | Measure and improve c before adding units; a reliable switchover beats more units |
| Confusing k-of-n with series/parallel | 2-of-3 is neither purely series nor purely parallel | Apply binomial formula; do not use simple series or parallel approximations |

## Worked Example

A quorum database cluster needs 99.999% (five nines) availability per year from nodes with individual availability A = 0.9999.

**2-of-3 majority (m=2, n=3):**

```
R_2/3 = 3(0.9999)² - 2(0.9999)³
      = 3 × 0.99980001 - 2 × 0.99970003
      = 2.99940003 - 1.99940006
      ≈ 0.9999999  (≈ seven nines)
```

**Switchover reliability c = 0.995:**

```
R_covered = 0.995 × 0.99999997 + 0.005 × 0.9999
          = 0.99499997 + 0.0049995
          ≈ 0.99999947   (five nines — coverage loss erases two orders of magnitude
                           relative to the uncovered ≈0.9999999 seven-nines figure)
```

The switchover mechanism at 99.5% reliability is the binding constraint. Improving switchover reliability from 99.5% to 99.9% recovers more reliability than adding a fourth node. (Corrected 2026-07-11: the previous version of this worked example contained an arithmetic transcription error in the intermediate step — the conclusion, five-nines, was directionally right but the displayed figure of 0.99990 undercounted by roughly two orders of magnitude.)

## Validation: Empirically Confirm Coverage Probability

The coverage probability `c` in the imperfect-coverage formula is a modelling assumption, not a measured fact. Validate it empirically before treating sized redundancy as live:

1. Trigger failover paths under realistic production-like load.
2. Measure switchover latency and success rate across ≥10 trials.
3. Compare the measured success rate against the `c` value used in the coverage formula.
4. If measured c is materially lower than assumed, improving switchover reliability delivers more benefit than adding units.

Controlled fault injection (chaos engineering) is the standard methodology for this validation. A 2025 multivocal literature review of 96 chaos engineering sources (Owotogbe et al., ACM Computing Surveys, Vol. 58, DOI:10.1145/3777375) confirms chaos engineering as the accepted practice for validating coverage assumptions, and identifies that no standardised MTTR/MTTD improvement metric yet exists — measure switchover success rate and latency as proxies.

**For agent/LLM architectures:** architecture choice is a redundancy-analogue decision. ReliabilityBench data (Gupta 2026) shows ReAct is more fault-tolerant than Reflexion under combined API stress (rate limiting, timeouts, schema drift). Select agent architecture by per-architecture fault-tolerance profiling, not by default.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- Owotogbe, J., Kumara, I., Van Den Heuvel, W.-J., & Tamburri, D. A. (2025). Chaos Engineering: A Multi-Vocal Literature Review. *ACM Computing Surveys*, 58(7), Article 164. DOI:10.1145/3777375.
- Gupta, A. (2026). ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions. arXiv:2601.06112.
