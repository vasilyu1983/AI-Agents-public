# Primitive 11: Mediation Analysis

## Definition

Mediation analysis decomposes the **total causal effect** of an exposure X on an outcome Y into:
- **Direct effect**: X → Y (not through the mediator M)
- **Indirect effect**: X → M → Y (through the mediator)

**Potential outcomes notation** (VanderWeele 2015):

- Y(x, m): outcome if X set to x and M set to m
- M(x): mediator value if X set to x
- Y(x, M(x')): outcome if X = x but M takes its natural value under X = x'

**Natural Direct Effect (NDE)**:
NDE = E[Y(1, M(0)) − Y(0, M(0))]

**Natural Indirect Effect (NIE)**:
NIE = E[Y(1, M(1)) − Y(1, M(0))]

**Total Effect (TE) = NDE + NIE**

**Proportion mediated**: NIE / TE

**Four no-unmeasured-confounders assumptions** (required for identification):
1. No unmeasured confounders of X-Y (after conditioning on covariates C)
2. No unmeasured confounders of M-Y (after conditioning on C)
3. No unmeasured confounders of X-M (after conditioning on C)
4. No confounders of M-Y affected by X (no X-induced M-Y confounders)

Assumption 4 is often violated; when it is, use **interventional (stochastic) indirect effects** or **principal stratification** as alternatives.

## When to Use

- You have estimated a total effect and want to understand the mechanism.
- An intermediate variable M is plausibly on the causal path from X to Y.
- The mechanism matters for intervention design (blocking M vs. changing X directly).
- You are designing a multi-stage intervention and need to know which stage is effective.

Do not use mediation analysis when:
- Assumption 4 is clearly violated (M-Y confounders exist that are themselves caused by X) without switching to interventional effects.
- The mediator is not directly manipulable (mechanistic interpretation requires counterfactual manageability).

## Inputs / Outputs

**Inputs**: exposure X; outcome Y; mediator M; baseline covariates C (pre-treatment); sample size (mediation requires larger N than total-effect estimation); model for E[Y | X, M, C] and E[M | X, C].

**Outputs**: NDE estimate; NIE estimate; TE = NDE + NIE; proportion mediated NIE/TE; 95% CIs via bootstrap; sensitivity analysis for assumption violations.

## Worst Failure Modes

1. **Conditioning on a post-treatment variable that is not the intended mediator**: adjusting for a confounder of M-Y that is affected by X (assumption 4 violation) biases both NDE and NIE. It can even reverse the sign of the direct effect.
2. **Product-of-coefficients method under non-linearity**: the classic α×β mediation formula (Baron-Kenny) is only valid for linear models with continuous outcomes. For binary or count outcomes, use the potential-outcomes formulas with Monte Carlo integration or parametric g-computation.
3. **Multiple mediators treated as one**: if there are multiple mediators M_1, M_2 on different pathways, the standard formula applies to each pathway separately. Treating them jointly without accounting for their inter-correlations biases both.
4. **Proportion mediated > 1 or < 0**: this occurs when NDE and NIE have opposite signs (inconsistent mediation — the direct and indirect effects work in opposite directions). Report the contradiction; do not normalize.
5. **Conflating statistical mediation with causal mediation**: a variable that reduces the X-Y coefficient in regression is not necessarily a causal mediator. It could be a collider. Always consult the DAG first.

## Worked Example

**Setting**: Does a 3-month exercise program (X) reduce depression (Y) partly through improved sleep quality (M)?

**DAG**:
```
X (Exercise) → M (Sleep quality) → Y (Depression score)
X (Exercise) → Y (Depression score) [direct]
C (Baseline health, age) → X, M, Y
```

**Assumptions checked**:
1. Baseline health + age adjust for X-Y confounding ✓
2. Baseline health + age adjust for M-Y confounding ✓
3. Baseline health + age adjust for X-M confounding ✓
4. No M-Y confounders caused by X — no obvious mediator-outcome confounder caused by exercise ✓

**Linear models**:
- E[M | X, C]: M = 0.8 + 2.1X + 0.3C (β_1 = 2.1, s.e. = 0.4)
- E[Y | X, M, C]: Y = 15.2 − 1.6X − 0.9M + 0.1C (β_X = −1.6, β_M = −0.9)

**Effects** (linear case, Baron-Kenny + potential outcomes consistent):
- NIE = β_1 × β_M = 2.1 × (−0.9) = −1.89 (reduction in depression via sleep)
- NDE = β_X = −1.6 (direct reduction not through sleep)
- TE = −1.89 + (−1.6) = −3.49

**Proportion mediated** = NIE / TE = 1.89 / 3.49 = 54%

**Bootstrap 95% CI for NIE**: [−2.8, −0.9] (via 1,000 bootstrap samples)

**Interpretation**: exercise reduces depression by ~3.5 points on average. About 54% of this effect is mediated through improved sleep quality. Interventions targeting sleep (e.g., sleep hygiene coaching alongside exercise) may amplify the total benefit.

## Sources

1. VanderWeele, T. J. (2015). *Explanation in Causal Inference: Methods for Mediation and Interaction*. Oxford University Press.
2. Pearl, J. (2001). Direct and Indirect Effects. *Proceedings of UAI*, 411–420.
3. Imai, K., Keele, L., & Tingley, D. (2010). A General Approach to Causal Mediation Analysis. *Psychological Methods*, 15(4), 309–334.
