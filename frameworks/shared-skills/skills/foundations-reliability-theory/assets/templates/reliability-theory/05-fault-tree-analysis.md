# Primitive: Fault Tree Analysis (FTA)

## Definition

**Fault Tree Analysis (FTA)** is a top-down, deductive failure analysis technique. Starting from an undesired **top event** (a system failure), it traces backwards through combinations of lower-level failure causes using Boolean logic gates to identify all root-cause paths that can produce the top event.

Core gate types:

| Gate | Symbol | Meaning |
|------|--------|---------|
| AND | ∧ | All input events must occur for the output event to occur |
| OR | ∨ | Any single input event is sufficient for the output event |
| NOT | ¬ | Output occurs when input does not |
| Inhibit | Conditional AND | Output requires a basic event AND a condition |

**Minimal cut sets (MCS)** are the smallest combinations of basic events whose joint occurrence causes the top event. Finding all MCS is the primary analytical output of FTA.

## When to Use

- Pre-launch reliability assessment of safety-critical or high-value systems.
- Root-cause investigation after a major incident — FTA reveals why the same sequence recurred.
- Quantitative probability computation for the top event when basic event probabilities are known.
- Regulatory compliance or certification work (IEC 61508, ISO 26262, DO-178C contexts).
- Identifying single points of failure (MCS of size 1) and two-way dependencies (MCS of size 2).

## Inputs

| Input | Description |
|-------|-------------|
| Top event definition | Precisely worded undesired system state |
| System architecture | Component list, dependencies, interfaces |
| Basic event probabilities | Per-component failure probability or rate (from primitive 01 or 09) |
| Common-cause failure data | Shared dependencies that invalidate independence assumptions |

## Outputs

- Fault tree diagram (logical structure).
- Minimal cut sets (enumerated and ranked by probability).
- Top event probability (if basic event probabilities supplied).
- Importance measures (Birnbaum, Criticality, Fussell-Vesely) ranking which basic events most drive top-event probability.

## Analysis Procedure

```
1. Define top event precisely (not "system failure" — say "API returns 5xx for >30s")
2. Identify immediate necessary causes and connect with AND/OR gates
3. Decompose each intermediate event recursively until reaching basic events
4. Enumerate minimal cut sets (use MOCUS algorithm or BDD for large trees)
5. Assign basic event probabilities
6. Compute top event probability: P(top) = 1 - ∏(1 - P(MCSᵢ)) for rare events
7. Compute importance measures to rank remediation priorities
```

## Importance Measures (Quick Reference)

| Measure | What It Answers |
|---------|----------------|
| Birnbaum importance | How sensitive is top-event probability to component i's reliability? |
| Criticality importance | What fraction of top-event probability is attributable to component i? |
| Fussell-Vesely | What fraction of top-event probability involves at least one MCS containing i? |

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Vague top event definition | Tree is ambiguous; analysis is not reproducible | Write top event as a specific, measurable system state with threshold |
| Missing common-cause failures | MCS independence assumption fails; top-event probability underestimated | Audit shared power, network paths, and software dependencies explicitly |
| Cutting the tree too shallow | Root causes not reached; MCS are intermediate events, not fixable | Decompose until basic events are testable and preventable |
| Treating FTA as a one-time activity | System architecture changes invalidate the tree | Schedule FTA reviews at each major architecture change |
| Confusing FTA with FMEA direction | FTA is top-down (effect → causes); FMEA is bottom-up (cause → effects) | Use both: FMEA for coverage, FTA for quantifying top-event risk (primitive 06) |

## Worked Example

**Top event**: Payment processing service unavailable for >60 seconds.

```
Top event: Payment service unavailable >60s
└─ OR
   ├─ Database layer unavailable (AND: primary DB fails AND replica fails)
   │  ├─ Primary DB failure  [P = 0.001/day]
   │  └─ Replica DB failure  [P = 0.001/day, independent]
   ├─ Application tier fully down (AND: both app servers fail)
   │  ├─ App server A failure [P = 0.005/day]
   │  └─ App server B failure [P = 0.005/day]
   └─ Network path unavailable (single ISP dependency)
      └─ ISP outage            [P = 0.0002/day]
```

Minimal cut sets:
- {Primary DB, Replica DB} — probability 0.000001/day
- {App A, App B} — probability 0.000025/day
- {ISP outage} — probability 0.0002/day (single-element MCS — SPOF)

**ISP outage is the dominant risk** (0.0002 vs. 0.000001/day — 200× more likely than the DB MCS, and 8× more likely than the App MCS). Adding a second ISP eliminates the only single-point-of-failure MCS. This prioritisation would not be visible without FTA.

## When FTA Is Not Enough — Augment with STPA

FTA identifies **component failures** and logical combinations that produce a top event. It does not find:

- **Unsafe control actions**: a component behaves correctly but issues a command at the wrong time or in the wrong context.
- **Timing and ordering failures**: correct events in the wrong sequence cause the hazard.
- **Human-automation coupling failures**: the human and the automated system each work as designed but their interaction is hazardous.
- **Design flaws in the control structure**: hazards arising from how the system is architected, not from component unreliability.

For software-intensive, autonomous, or sociotechnical systems where these failure types dominate, **augment FTA with STPA (System-Theoretic Process Analysis)**. STPA is based on STAMP (System-Theoretic Accident Model and Processes, Leveson 2011), which models accidents as control-loop failures rather than component-chain failures.

STPA complements FTA: use FTA for hardware-failure probability quantification and MCS ranking; use STPA to derive hazardous control actions from the system's control structure, particularly when software errors, design errors, and unsafe interactions are the primary risk.

Reference: Leveson, N. G. (2011). *Engineering a Safer World*. MIT Press. (Free PDF via MIT STAMP project; STPA Handbook 2018 also freely available.)

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- IEC 61025 (2006). *Fault tree analysis (FTA)*. International Electrotechnical Commission.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Leveson, N. G. (2011). *Engineering a Safer World*. MIT Press. [STAMP/STPA source for the "When FTA is not enough" section above.]
