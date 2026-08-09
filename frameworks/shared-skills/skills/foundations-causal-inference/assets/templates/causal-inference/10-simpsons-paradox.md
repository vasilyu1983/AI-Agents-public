# Primitive 10: Simpson's Paradox and Confounding Traps

## Definition

**Simpson's paradox** occurs when an association present in aggregate data reverses or disappears when data is stratified by a third variable. The aggregate trend and subgroup trends point in opposite directions.

This is not a statistical anomaly — it is a consequence of aggregating across groups with different distributions of a confounding variable.

**The three confounding traps** identified by DAG theory:

1. **Confounder** (common cause): C → X, C → Y. Association X-Y at the aggregate level includes confounding from C. Fix: condition on C (adjust).

2. **Collider** (common effect): X → C, Y → C. No association between X and Y exists marginally, but conditioning on C *opens* a spurious path. Fix: do not condition on C. Example: among hospitalized patients (C), disease severity and other conditions appear negatively correlated — conditioning on hospitalization (a collider) creates the appearance.

3. **Mediator** (causal pathway): X → M → Y. Conditioning on M blocks the causal effect of X on Y. The "association disappears after adjustment" is not evidence that X has no effect — it is evidence that M is on the causal path.

**The correct rule**: which variables to condition on is determined entirely by the DAG, not by statistical criteria. Rules like "control for everything significant" and "more controls is better" are wrong.

## When to Use

Use this primitive:
- When an observed trend contradicts intuition or prior beliefs
- Before any regression specification to audit the variable list
- When someone proposes controlling for a variable without justification
- When a result disappears or reverses after adding a covariate
- When a subgroup analysis shows opposite effects from the overall analysis

## Inputs / Outputs

**Inputs**: a dataset showing an association X-Y; proposed conditioning variables; the DAG.

**Outputs**: the correct adjustment set (if any); identification of which variables are confounders, mediators, or colliders; the causal interpretation of the observed aggregated vs. stratified association.

## Worst Failure Modes

1. **Conditioning on a collider when diagnosing Simpson's paradox**: the paradox resolution requires *not* conditioning on the collider. Conditioning on it makes the paradox worse.
2. **Treating disappearance of an effect after adjustment as causal nullity**: if the adjusted variable is a mediator, the effect disappears because the pathway is blocked, not because X has no effect on Y.
3. **No DAG, resolution by intuition**: without a DAG, deciding whether C is a confounder, collider, or mediator is guesswork. Intuition fails in complex systems.
4. **M-bias**: a particular collider trap where adjusting for a variable that is not a confounder (not on a backdoor path) introduces bias by opening a previously closed collider path. Rare in practice but catastrophic when present.
5. **Ecological fallacy**: a group-level association (countries, firms) does not hold at the individual level. Aggregation produces confounding by group membership.

## Worked Example

**Setting**: A hospital reports that Treatment A has higher mortality than Treatment B overall. Is A harmful?

**Aggregate data**:
| Treatment | Deaths | Total | Mortality |
|-----------|--------|-------|-----------|
| A         | 20     | 100   | 20%       |
| B         | 80     | 400   | 20%       |

Wait — they're equal overall. But:

**Stratified by disease severity**:

Mild cases:
| Treatment | Deaths | Total | Mortality |
|-----------|--------|-------|-----------|
| A         | 2      | 50    | 4%        |
| B         | 65     | 325   | 20%       |

Severe cases:
| Treatment | Deaths | Total | Mortality |
|-----------|--------|-------|-----------|
| A         | 18     | 50    | 36%       |
| B         | 15     | 75    | 20%       |

**Paradox**: within each stratum, A has lower mortality for mild cases (4% vs 20%) but A appears worse for severe cases. Doctors assign Treatment A more often to severe cases — severity confounds treatment selection.

**DAG**:
```
Severity (C) → Treatment (X)
Severity (C) → Mortality (Y)
Treatment (X) → Mortality (Y)
```

Severity is a **confounder**. The correct analysis conditions on severity. Within mild cases, A is superior (4% vs. 20%). Within severe cases, A is worse (36% vs. 20%). The aggregate result (20% = 20%) masks this.

**Decision**: assign treatment A to mild cases; treatment B (or equal A/B) to severe cases.

## Sources

1. Pearl, J. (2009). *Causality*. Cambridge University Press. Chapter 6.3 (Simpson's paradox resolved).
2. Elwert, F., & Winship, C. (2014). Endogenous Selection Bias: The Problem of Conditioning on a Collider Variable. *Annual Review of Sociology*, 40, 31–53.
3. Hernán, M. A., Clayton, D., & Keiding, N. (2011). The Simpson's Paradox Unraveled. *International Journal of Epidemiology*, 40(3), 780–785.
