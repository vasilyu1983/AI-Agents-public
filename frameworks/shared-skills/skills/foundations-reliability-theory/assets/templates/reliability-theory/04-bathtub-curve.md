# Primitive: Bathtub Curve

## Definition

The **bathtub curve** describes how the hazard rate of a population of items changes over their lifetime. It has three distinct phases:

| Phase | Also Called | Hazard Shape | Dominant Mechanism |
|-------|-------------|--------------|-------------------|
| Phase I | Infant mortality / Early failure | Decreasing (DFR) | Manufacturing defects, assembly errors, material flaws eliminated by early use |
| Phase II | Useful life / Chance failure | Approximately constant (CFR) | Random external stresses; no ageing or wear |
| Phase III | Wear-out | Increasing (IFR) | Fatigue, corrosion, degradation, material ageing |

The composite hazard function over a full lifecycle is the sum of three Weibull hazard contributions (β < 1, β = 1, β > 1), which produces the characteristic tub shape.

## When to Use

- Planning burn-in or acceptance testing to move units past Phase I before field deployment.
- Setting replacement schedules that pre-empt Phase III wear-out.
- Interpreting a change in observed failure rate — does it signal transition to a new phase?
- Allocating warranty cost: Phase I failures dominate early returns; Phase III failures dominate late returns.
- Explaining system reliability evolution to non-technical stakeholders.

## Inputs

| Input | Description |
|-------|-------------|
| Failure history | Time-stamped failures across the product/service lifetime |
| Phase boundaries | Known or estimated transition times between phases |
| Weibull parameter estimates | β and η per phase from primitive 09 (optional but recommended) |

## Outputs

- Phase classification for the current operating point.
- Recommended action per phase (burn-in, normal ops, proactive replacement).
- Transition time estimates: T₁ (end of infant mortality) and T₂ (start of wear-out).

## Phase Characteristics and Actions

### Phase I — Infant Mortality

- Short duration relative to product life.
- Caused by latent manufacturing defects that surface quickly under stress.
- **Mitigation**: burn-in testing (accelerated stress before deployment), enhanced incoming QA, early-life monitoring with tight alerting thresholds.
- **Software analog**: post-deploy canary window; new service instances are more likely to fail in the first hours after deployment.

### Phase II — Useful Life

- MTBF is approximately stable; exponential distribution is a reasonable model.
- Failures are random — not caused by age or wear.
- **Mitigation**: normal preventive maintenance; redundancy protects against random events (primitives 07, 10).
- **Software analog**: steady-state operation between deployments; random hardware faults, transient network errors.

### Phase III — Wear-Out

- Failure rate rises; remaining useful life shortens.
- Predictive maintenance or proactive replacement is cost-effective before the steep IFR rise.
- **Mitigation**: condition monitoring, replacement before threshold age T₂, root-cause analysis to extend T₂.
- **Software analog**: database tables filling up, memory leak accumulation, certificate expiry, tech debt reaching critical mass.

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Treating the entire lifecycle as a single exponential | Phase I and III risks invisible; wrong maintenance timing | Segment data by phase; fit separately |
| Skipping burn-in to save cost | Phase I failures hit customers instead of the test floor | Quantify expected Phase I failure cost vs. burn-in cost |
| Extending service beyond T₂ without monitoring | Rapidly increasing failure rate surprises operations | Set a Phase III entry threshold and a replacement rule |
| Applying bathtub thinking to software without adaptation | Software wear-out mechanisms differ (data accumulation, dependency drift) | Map software-specific wear-out signals to Phase III analogues |
| Treating T₁ and T₂ as known without data | Incorrect phase boundaries lead to wrong actions | Estimate from Weibull analysis (primitive 09) with confidence intervals |

## Worked Example

A fleet of 1,000 IoT sensors is deployed. Three-phase Weibull analysis (primitive 09) estimates:

```
Phase I  (β = 0.6): 0–90 days,  η = 200 days
Phase II (β = 1.0): 90–730 days, λ = 0.0008/day  (MTBF ≈ 1,250 days)
Phase III(β = 3.2): >730 days,  η = 900 days
```

**Actions**:
1. Run 72-hour accelerated burn-in on all sensors before shipping to advance past early Phase I.
2. During Phase II, apply standard redundancy (one spare per 50 units).
3. At day 700 (before Phase III onset), proactively replace sensors rather than waiting for failures — replacement cost is 60% of reactive failure + logistics cost.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- Weibull, W. (1951). A statistical distribution function of wide applicability. *Journal of Applied Mechanics*, 18(3), 293–297.
- MIL-HDBK-217 (1991). *Reliability Prediction of Electronic Equipment*. US DoD. (Note: field data from MIL-HDBK-217 should be validated against observed rates; known to overstate failure rates in modern components.)
