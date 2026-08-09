# Causal Inference Primitives — Index and Composition Guide

12 domain-agnostic causal inference primitives. Each file is a standalone playbook (definition, when to use, inputs/outputs, worst failure modes, worked example, sources). Cross-cutting guidance — decision map, assumption inventory, estimand taxonomy — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

Consumer skills that build applied-recipe layers on top of these primitives (CRO, paid ads, analytics, product, business models, QA debugging) are planned for Wave 2 and will reference these files directly.

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-dag-scm.md](01-dag-scm.md) | Implicit untested causal assumptions; confounders, mediators, colliders misidentified |
| 2 | [02-do-calculus.md](02-do-calculus.md) | Treating observational P(Y\|X) as causal without identification |
| 3 | [03-backdoor-frontdoor.md](03-backdoor-frontdoor.md) | Conditioning on the wrong variables; collider bias; over-adjustment |
| 4 | [04-instrumental-variables.md](04-instrumental-variables.md) | Omitted-variable bias when confounders are unobservable |
| 5 | [05-rdd.md](05-rdd.md) | Selection bias in threshold-based treatment assignment |
| 6 | [06-diff-in-diff.md](06-diff-in-diff.md) | Pre-existing trends misattributed as treatment effects |
| 7 | [07-synthetic-control.md](07-synthetic-control.md) | No valid control group for a single treated unit |
| 8 | [08-propensity-score.md](08-propensity-score.md) | Covariate imbalance inflating treatment effect estimates in observational data |
| 9 | [09-cate-uplift.md](09-cate-uplift.md) | ATE masking heterogeneous or opposing subgroup effects |
| 10 | [10-simpsons-paradox.md](10-simpsons-paradox.md) | Aggregation reversals; collider conditioning; mediator adjustment |
| 11 | [11-mediation-analysis.md](11-mediation-analysis.md) | Total effect treated as direct; pathway blocked by incorrect conditioning |
| 12 | [12-sensitivity-analysis.md](12-sensitivity-analysis.md) | Conclusions that collapse under modest unobserved confounding |

---

## Agent-Team Stack Guidance

Causal inference tasks map naturally to specialist agent roles:

**Design agent**: owns DAG construction (#1), identification check (#2, #3), method selection (Decision Checklist in SKILL.md).

**Estimation agent**: owns the chosen identification method (#4–#9). Handles data preparation, model fitting, and output formatting.

**Validation agent**: owns assumption testing (parallel trends for DiD, first-stage F for IV, overlap for propensity) and sensitivity analysis (#12).

**Interpretation agent**: owns translating CATE / uplift (#9) or mediation (#11) results into actionable subgroup or pathway findings.

For observational studies: always pair Estimation with Validation. A single agent should not both estimate and validate — the incentive to under-scrutinize one's own assumptions is too strong.

---

## Composition Stacks

### Uplift from Observational Data
1. DAG (#1) — map confounders
2. Propensity / DR (#8) — balance and debiased ATE
3. CATE / X-learner (#9) — heterogeneous effects
4. Sensitivity analysis (#12) — E-value on strongest claim

### Policy Evaluation (Single Treated Unit)
1. DAG (#1) — map treatment and outcome structure over time
2. Synthetic control (#7) — construct counterfactual trajectory
3. DiD robustness check (#6) — pre-trend validation
4. Sensitivity: placebo permutation test (synthetic control built-in)

### Mechanism Attribution
1. DAG (#1) — identify mediator path
2. Backdoor criterion (#3) — adjustment set for total effect
3. Propensity / DR (#8) — balance for mediation estimation
4. Mediation analysis (#11) — NDE, NIE, proportion mediated
5. Sensitivity analysis (#12) — E-value for indirect effect

### A/B Test Augmentation (Heterogeneity)
1. RCT result for ATE (use the experimental design)
2. CATE / T-learner or X-learner (#9) — subgroup HTE
3. Simpson's paradox check (#10) — verify subgroup results not reversed by aggregation
4. Sensitivity analysis (#12) — optional for weakly randomized or high-attrition experiments

### Threshold Policy Audit
1. DAG (#1) — check for sorting or anticipation effects at the threshold
2. RDD (#5) — local ATE at the cutoff
3. Sensitivity: bandwidth robustness + placebo cutoff tests

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — identification decision map, estimand taxonomy, assumption inventory
- [`../../../data/sources.json`](../../../data/sources.json) — all academic references
