# Primitive 9: CATE / Uplift Modeling

## Definition

The **Conditional Average Treatment Effect (CATE)**: τ(x) = E[Y(1) − Y(0) | X = x]

CATE measures how the treatment effect varies across units with different characteristics x. The ATE = E[τ(X)] averages over the population. CATE reveals who benefits, who is harmed, and who is unaffected.

**Uplift modeling** (industry terminology) targets τ(x) directly for resource-allocation decisions: treat only those with τ(x) > cost threshold.

**Meta-learner taxonomy**:

| Learner | Description | When to Use |
|---------|-------------|-------------|
| S-learner | One model on (X, T); τ̂(x) = μ̂(x,1)−μ̂(x,0) | Simple baseline; may regularize T away |
| T-learner | Separate models per arm; τ̂(x) = μ̂_1(x)−μ̂_0(x) | Large samples, balanced arms |
| X-learner | Cross-imputed residuals from T-learner; weighted by propensity | Imbalanced treatment arms (e.g., 90/10 split) |
| DR-learner | Doubly-robust pseudo-outcomes as targets | Observational data; misspecification robustness |
| R-learner | Partialling out via cross-fitted residuals (Robinson 1988) | High-dimensional X; Neyman-orthogonal guarantees |

**Causal forests** (Wager & Athey 2018): a non-parametric tree-based R-learner variant with honest sample splitting, providing asymptotically normal pointwise CATE estimates.

## When to Use

- ATE is insufficient — subgroups have heterogeneous effects.
- Resource is constrained — only a fraction of units can be treated.
- You want to identify who to target (uplift), who to avoid (sleeping dogs, negative effect), and who is indifferent.
- Sample size is adequate: CATE estimation requires more data than ATE. Rule of thumb: at least 5,000 observations per arm for reliable subgroup estimates with tree-based methods.

## Inputs / Outputs

**Inputs**: treatment T, outcome Y, covariates X; propensity score estimates (for X-learner, DR-learner, R-learner); choice of base learner (gradient boosting, random forest, ridge).

**Outputs**: CATE estimates τ̂(x_i) for each unit; variable importance (which features drive heterogeneity); CATE confidence intervals (bootstrap or asymptotic for causal forests); uplift quantile analysis (Qini curve, AUUC).

## Worst Failure Modes

1. **Underpowered subgroup analysis**: CATE estimation with low sample sizes produces noisy estimates. Small subgroups are especially unreliable. Report confidence intervals and flag low-N subgroups.
2. **S-learner suppressing treatment heterogeneity**: if X is high-dimensional, regularization can shrink the treatment coefficient toward zero, hiding real heterogeneity. Use T-learner or X-learner as a check.
3. **Confounding inflating heterogeneity estimates**: CATE inherits the identification assumptions of the underlying estimator. Under unobserved confounding, CATE estimates are biased for all subgroups and the subgroup with the largest estimated effect may simply have the most confounding.
4. **Treating positive CATE as sufficient for targeting**: if the cost of treatment exceeds τ̂(x), targeting that unit is unprofitable even with positive CATE. Always subtract treatment cost from τ̂(x) for targeting decisions.
5. **Sleeping dogs**: units with negative CATE (harm from treatment). If the action-space is "treat or not treat," negative-CATE units should not be treated. Missing this can increase the harmful treated share.

## Worked Example

**Setting**: an e-commerce platform tests a 10% discount offer (T) on purchase completion (Y). ATE from RCT = 0.04 (4 pp). Marketing wants to send the discount only to users likely to respond.

**X-learner on RCT data** (N = 80,000; T=1: 40,000; T=0: 40,000):

```
Step 1: Fit μ̂_1(x) on treated arm, μ̂_0(x) on control arm (gradient boosting)
Step 2: Impute
  - For treated units: D̂_1(x) = Y_i − μ̂_0(x_i)
  - For control units: D̂_0(x) = μ̂_1(x_i) − Y_i
Step 3: Fit CATE models τ̂_1(x) on D̂_1(x) | treated units
                       τ̂_0(x) on D̂_0(x) | control units
Step 4: τ̂(x) = e(x) τ̂_0(x) + (1−e(x)) τ̂_1(x)
       (propensity e(x) ≈ 0.5 in RCT → average)
```

**Uplift distribution**:
- Top decile τ̂(x): 0.14 (14 pp above control)
- Bottom decile τ̂(x): −0.03 (sleeping dogs — discount reduces purchase completion for this segment)
- Users with τ̂(x) > cost threshold (0.02): 45% of population

**Business rule**: target top 45% → projected incremental purchases = 0.07 × 36,000 = 2,520 vs. 0.04 × 80,000 = 3,200 if everyone treated — but discounts are saved on 55% of users.

## Sources

1. Wager, S., & Athey, S. (2018). Estimation and Inference of Heterogeneous Treatment Effects Using Random Forests. *JASA*, 113(523), 1228–1242.
2. Athey, S., & Imbens, G. W. (2017). The State of Applied Econometrics: Causality and Policy Evaluation. *Journal of Economic Perspectives*, 31(2), 3–32.
3. Künzel, S. R., et al. (2019). Metalearners for Estimating Heterogeneous Treatment Effects Using Machine Learning. *PNAS*, 116(10), 4156–4165.
