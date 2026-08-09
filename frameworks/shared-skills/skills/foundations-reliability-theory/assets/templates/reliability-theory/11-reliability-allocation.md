# Primitive: Reliability Allocation

## Definition

**Reliability allocation** (also called reliability apportionment) is the process of distributing a system-level reliability target to individual subsystems and components, so that each team or supplier knows what their component must achieve for the whole system to meet its goal.

Allocation answers: **given R_system = 0.9999, what must each of our 5 subsystems achieve?**

Three main methods:

| Method | When to Use | Formula |
|--------|-------------|---------|
| Equal allocation | All subsystems similar in complexity and cost | Rᵢ = R_system^(1/n) for series |
| AGREE (weighted by complexity and importance) | Subsystems differ in function count and criticality | Rᵢ = exp(-nᵢ × ln(1/R_system) / (wᵢ × N)) |
| ARINC (proportional to current reliability) | Mature system with existing component data | Rᵢ_target = 1 - (1-R_system) × (λᵢ / Σλⱼ) |

**AGREE method inputs**: nᵢ = number of modules in subsystem i, wᵢ = weighting factor (importance × exposure), N = total mission time.

## When to Use

- Setting reliability requirements for each subsystem at the start of a design.
- Distributing an SLO target to microservices, infrastructure layers, or third-party dependencies.
- Renegotiating reliability contracts with suppliers — allocation gives the evidence-based target.
- After FTA (primitive 05) or system reliability analysis (primitive 10) reveals the weakest link — reallocate targets to fix the imbalance.
- Checking whether current component reliabilities add up to the system target.

## Inputs

| Input | Description |
|-------|-------------|
| System reliability target | R_system at mission time (from SLO or contract) |
| Subsystem count and topology | n components in series, parallel, or mixed |
| Component complexity weights | Number of modules or failure modes per subsystem |
| Importance weights | Criticality of each subsystem to mission success |
| Current reliability estimates | If available; used for ARINC method |

## Outputs

- Per-subsystem reliability target Rᵢ.
- Validation: R_system achieved when all subsystems meet their targets.
- Improvement gap: current Rᵢ vs. allocated target.
- Priority list: subsystems furthest from their target (largest improvement needed).

## Equal Allocation (Series)

For a series system with n subsystems:

```
Rᵢ = R_system^(1/n)
```

Example: 3 subsystems, R_system = 0.999:

```
Rᵢ = 0.999^(1/3) ≈ 0.99967 each
```

Verify: 0.99967³ ≈ 0.999 ✓

## ARINC (Failure-Rate Proportional) Allocation

Allocates more stringent targets to currently reliable components and allows relatively higher failure rates where they already occur (since those paths need less constraint):

```
λᵢ_target = (1 - R_system) × (λᵢ_current / Σλⱼ_current) / t_mission
Rᵢ_target = exp(-λᵢ_target × t_mission)
```

**Counterintuitive**: this preserves current failure-rate proportions rather than fixing them. Use equal or AGREE allocation if some subsystems are known to be already over-spec relative to their importance.

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Allocating equal targets without considering achievability | Some subsystems receive infeasible targets (e.g. 0.999999 for a third-party SaaS) | Check each allocated target against known achievable levels; renegotiate or add redundancy |
| Allocating to series structure when topology is mixed | Targets are too aggressive for components in parallel paths | Use the correct topology in primitive 10 before allocating |
| Over-allocating budget to already-reliable components | Cheap wins available elsewhere are ignored | Use ARINC or AGREE; weight by improvement cost vs. reliability gain |
| Treating allocation as static through the project | Design changes invalidate the allocation | Re-run allocation at each major architecture review |
| Allocating availability without separating MTBF and MTTR levers | Teams don't know whether to focus on preventing failures or recovering faster | Decompose allocated target into MTBF and MTTR sub-targets explicitly |

## Worked Example

A microservices platform must achieve 99.95% monthly availability (R_system = 0.9995) across 4 series subsystems: API Gateway, Auth Service, Core Service, Database.

**Equal allocation:**

```
Rᵢ = 0.9995^(1/4) = 0.999875  (each must achieve 99.9875%)
```

**Current measured reliabilities:**

| Subsystem | Current R | Target R | Gap |
|-----------|-----------|----------|-----|
| API Gateway | 0.9999 | 0.999875 | No gap (over-spec) |
| Auth Service | 0.9997 | 0.999875 | No gap (over-spec) |
| Core Service | 0.9995 | 0.999875 | −0.000375 (needs improvement) |
| Database | 0.9991 | 0.999875 | −0.000775 (critical gap) |

Database is furthest from its target. **Action**: focus reliability investment on database MTTR (current 45-min MTTR needs to fall to ~11 min to close the gap), then address Core Service. API Gateway and Auth Service require no immediate work.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*. (AGREE method derivation.)
