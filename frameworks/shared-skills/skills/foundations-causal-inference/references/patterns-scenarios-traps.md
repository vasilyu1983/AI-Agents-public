---
description: Applied patterns, scenarios, anti-patterns, and known traps for causal-inference foundations.
last_verified: 2026-08-14
status: stable
---

# Causal Inference Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Observational impact estimate | No RCT, confounders are measured | DAG -> backdoor -> propensity/DR -> sensitivity |
| Natural experiment | Assignment has external shock or threshold | Design check -> IV/RDD/DiD -> robustness diagnostics |
| Single treated unit | One market, one feature, one region | Synthetic control -> placebo tests -> sensitivity |
| Heterogeneous treatment targeting | Need who benefits, not just average impact | DR estimate -> CATE/uplift -> overlap audit |
| Mechanism attribution | Need why the effect happened | DAG -> total effect -> mediation -> sensitivity |
| Conflicting aggregate/subgroup results | Aggregate trend reverses by segment | DAG -> confounder/collider check -> stratified estimand |
| Interfering units | Marketplace, social graph, shared backend, ranking model | Name interference structure -> cluster/geo or switchback design -> bias-aware estimator -> report global effect |

## Scenarios

| Scenario | First Question | Correct Primitive |
|---|---|---|
| Feature users retain better than non-users | What caused feature adoption? | DAG/backdoor or instrument |
| Discount recipients buy more | Was discount assignment random or targeted? | RCT, IV, or propensity methods |
| Launch in one country lifts revenue | What is the counterfactual country trajectory? | Synthetic control |
| Metric jumps after policy date | Would treated and control trends have stayed parallel? | Difference-in-differences |
| Eligibility threshold determines access | Is there manipulation around the cutoff? | Regression discontinuity |
| ATE is flat but some users improve | Is there overlap within subgroups? | CATE/uplift |
| A/B test on a two-sided marketplace shows lift | Did treated users take supply from control users? | Cluster/geo or switchback design, not unit randomization |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Safer Move |
|---|---|---|
| Regression with many controls as proof | Bad controls can add collider or mediator bias | Use DAG-derived adjustment set |
| DAG drawn after results | Encodes confirmation bias | Draw graph before model selection |
| DiD without pre-trends | Parallel trends is the design assumption | Show event study or choose another design |
| Pre-trend test pass treated as proof of parallel trends | Pre-trend tests have low power; a passing test does not validate the parallel-trends assumption for the post-period | Use HonestDiD (Rambachan & Roth 2023) to produce confidence intervals that remain valid under bounded violations of parallel trends |
| TWFE on staggered panel without heterogeneity check | TWFE weights can be negative under heterogeneous treatment effects (Goodman-Bacon 2021 decomposition); result may be sign-flipped | Use heterogeneity-robust estimator: Callaway–Sant'Anna, Sun–Abraham, BJS imputation, or Gardner 2-stage |
| Weak IV accepted because p-value is significant | Weak first stage magnifies bias | Report first-stage strength and robust intervals |
| Synthetic control with poor pre-fit | Donor pool is not a credible counterfactual | Improve donor pool or do not claim effect |
| CATE used for targeting without support checks | Model extrapolates to sparse regions | Enforce overlap and minimum subgroup N |
| Sensitivity omitted because estimate is "significant" | Statistical significance does not address hidden bias | Report E-value, Rosenbaum bounds, or tipping point |
| "It was randomized, so it is causal" on an interfering system | Randomization removes confounding, not interference; the control group is contaminated by the treatment | Cluster, geo, or switchback the design; report the global treatment effect and the assumed interference structure |

## Known Traps

- Conditioning on post-treatment variables changes the estimand.
- Time-varying confounding can invalidate simple adjustment.
- Staggered DiD with heterogeneous effects can make TWFE weights negative (Goodman-Bacon 2021 decomposition); use BJS imputation, Callaway–Sant'Anna, Sun–Abraham, or Gardner 2-stage instead.
- BJS imputation estimator requires no always-treated units in the panel; verify panel structure before applying.
- IV estimates LATE for compliers unless stronger assumptions are justified.
- RDD is local to the cutoff, not a global ATE.
- Propensity scores balance observed covariates only.
- Mediation requires stronger assumptions than total-effect estimation.
- Switchback block length must exceed the carryover order; too-short blocks leak treatment across blocks and bias the estimate toward null.
- Clustering reduces interference bias but raises variance and cuts the effective sample to the number of clusters — power is set by cluster count, not user count.

## Exit Checklist

- [ ] Estimand is named: ATE, ATT, LATE, CATE, NDE/NIE, or local cutoff effect.
- [ ] Treatment, outcome, time window, and unit of analysis are fixed before modeling.
- [ ] DAG or design diagram is written down.
- [ ] Identification assumptions are explicit and falsifiable where possible.
- [ ] Balance, overlap, pre-trends, first-stage, bandwidth, or pre-fit diagnostics are reported as applicable.
- [ ] Interference is ruled out, or the design accounts for it and the reported estimand says whether it is unit-level or global.
- [ ] Sensitivity analysis is included for observational estimates.
