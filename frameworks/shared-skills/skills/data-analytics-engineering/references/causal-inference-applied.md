---
description: Causal inference patterns for analytics engineering. Covers DAG-driven feature design, DML, propensity scoring, DiD, synthetic control, IV, and sensitivity gates — grounded in dbt/warehouse/product-analytics reality.
last_verified: 2026-05-02
status: stable
---

# Causal Inference Applied: From Warehouse to Causal Claims

> **Gate before invoking:** Check [`foundations-causal-inference` § When to Apply](../../foundations-causal-inference/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — DAG-Driven Feature Engineering](#p1--dag-driven-feature-engineering)
  - [P2 — Double Machine Learning for ATE/CATE](#p2--double-machine-learning-for-atecate)
  - [P3 — Propensity-Score Adjustment in Cohort Studies](#p3--propensity-score-adjustment-in-cohort-studies)
  - [P4 — Difference-in-Differences on Policy/Feature Rollout](#p4--difference-in-differences-on-policyfeature-rollout)
  - [P5 — Synthetic Control for Single-Unit Questions](#p5--synthetic-control-for-single-unit-questions)
  - [P6 — Instrumental Variables from Natural Experiments in Product Logs](#p6--instrumental-variables-from-natural-experiments-in-product-logs)
  - [P7 — Sensitivity Analysis as a Release Artifact](#p7--sensitivity-analysis-as-a-release-artifact)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Including a Mediator as a Control Variable](#a1--including-a-mediator-as-a-control-variable)
  - [A2 — Calling a Regression Coefficient "The Effect of X"](#a2--calling-a-regression-coefficient-the-effect-of-x)
  - [A3 — Selection Bias from Filtering on Outcome](#a3--selection-bias-from-filtering-on-outcome)
  - [A4 — Survivorship Bias in Cohort Analyses](#a4--survivorship-bias-in-cohort-analyses)
  - [A5 — Treating Correlation Strength as Causal Strength](#a5--treating-correlation-strength-as-causal-strength)
- [Recipes](#recipes)
  - [R1 — Observational Treatment Effect with ML](#r1--observational-treatment-effect-with-ml)
  - [R2 — Cohort Policy Impact with DiD](#r2--cohort-policy-impact-with-did)
  - [R3 — Single-Customer Impact Estimate via Synthetic Control](#r3--single-customer-impact-estimate-via-synthetic-control)
- [Composition](#composition)
- [Primitive Links](#primitive-links)
- [Sources](#sources)

---

## Framing Note

Analytics engineers sit at the intersection of data modeling and business decisions. The marts they build are routinely used to answer causal questions: "Did this feature increase retention?", "Did this pricing change reduce churn?" These questions cannot be answered by correlation alone, and the analyst who skips a causal framework will produce directionally wrong advice at a non-trivial rate.

This file is the applied layer of the `foundations-causal-inference` skill. It translates the 12 primitives into patterns that arise inside dbt projects, warehouse SQL, and product-analytics pipelines. Every pattern names the primitive it relies on and links to the corresponding template. Assumed stack: Snowflake or BigQuery, dbt or SQLMesh, Python (pandas / EconML) for estimation steps that go beyond SQL.

---

## Pattern Catalog

### P1 — DAG-Driven Feature Engineering

**Primitive**: #1 DAGs and Structural Causal Models → [`../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md`](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md)

**When to use.** Before building any dbt model whose output will be used as feature inputs to a causal or predictive model. Also before constructing any "analysis mart" where columns will be compared between treatment and control groups.

**The problem it solves.** Feature engineering for ML models is usually column-selection driven by correlation. When the model output is used to attribute causation — or when features are later used as controls in a regression — selecting the wrong columns produces biased estimates. The three types of variables require opposite treatment:

- **Confounder**: a common cause of treatment and outcome. Must be included in the adjustment set to close a back-door path.
- **Mediator**: a variable on the causal path from treatment to outcome. Including it as a control blocks the very effect you are trying to measure.
- **Collider**: a common effect of two variables. Conditioning on it opens a spurious association path and introduces bias where none existed.

**Mechanic.**

1. Draw the DAG before touching SQL. List all variables available in the warehouse for a given analysis. For each, determine its role: confounder, mediator, collider, or irrelevant.
2. Use the backdoor criterion (#3) to find the minimal adjustment set that closes all back-door paths between treatment T and outcome Y without conditioning on mediators or colliders.
3. In dbt: create a separate `causal_features` mart that contains only the adjustment set variables, with a column-level YAML comment explaining why each column is included and what role it plays (e.g., `# role: confounder — account_age affects both plan_upgrade and churn risk`).
4. Exclude mediators from this mart. Create a separate `mediation_variables` mart if mediation analysis is needed later.

**Worked example.** A B2B SaaS company wants to understand the causal effect of `onboarding_call_completed` (treatment T) on `retained_at_90d` (outcome Y). Variables available in the warehouse include `account_age_days`, `seat_count`, `support_tickets_in_first_30d`, and `feature_usage_score_week2`.

- `account_age_days` and `seat_count` → confounders (larger, older accounts are more likely to take the call *and* more likely to retain).
- `feature_usage_score_week2` → mediator (the call likely *causes* feature usage, which then causes retention). Conditioning on it blocks the causal path.
- `support_tickets_in_first_30d` → potential confounder *or* collider depending on DAG assumptions. If tickets are caused by poor onboarding (T causes tickets), conditioning on tickets is conditioning on a collider and should be avoided.

The `causal_features` mart includes `account_age_days` and `seat_count` only.

---

### P2 — Double Machine Learning for ATE/CATE

**Primitives**: #8 Propensity Score Methods, #9 CATE/Uplift → [`../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md`](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md), [`../../foundations-causal-inference/assets/templates/causal-inference/09-cate-uplift.md`](../../foundations-causal-inference/assets/templates/causal-inference/09-cate-uplift.md)

**When to use.** You have observational warehouse data, a well-drawn DAG, high-dimensional confounders (more than ~5 variables), and you need an ATE or CATE estimate. Standard OLS will either underfit (missing non-linear confounder effects) or overfit (p-hacking through manual variable selection).

**The problem it solves.** Double Machine Learning (DML, Chernozhukov et al. 2018) uses cross-fitting to produce a Neyman-orthogonal estimator: ML models absorb confounder effects on both the treatment and outcome, leaving a residual that is "locally linear" in the treatment effect. This removes regularization bias from the nuisance models without sacrificing the treatment effect estimate.

**Mechanic.**

Cross-fitting procedure (K folds, typically K = 5):

```
For each fold k:
  Train M_Y on folds ≠ k to predict Y from confounders X → get residuals ε_Y = Y - Ŷ
  Train M_T on folds ≠ k to predict T from confounders X → get residuals ε_T = T - T̂
  Predict on fold k using models trained on other folds (prevents overfitting bias)

ATE estimate: regress ε_Y on ε_T (one coefficient, no intercept)
CATE: use a meta-learner (X-learner, R-learner) on the residuals, or feed (ε_Y, ε_T, X) into EconML's LinearDML
```

In practice, use the `EconML` library (`econml.dml.LinearDML` or `econml.dml.CausalForestDML`) rather than re-implementing cross-fitting manually.

**dbt integration pattern.** DML runs in Python, not SQL, but the pattern fits cleanly into a dbt + Python notebook workflow:

1. dbt produces a mart `fct_treatment_cohort` with grain = one row per user/account, columns = treatment flag, outcome, and adjustment-set features.
2. A Python script or dbt Python model reads the mart, runs DML, and writes back `fct_causal_effect_estimates` with columns: `entity_id`, `ate_estimate`, `ate_se`, `cate_estimate`, `cate_se`, `model_version`.
3. The downstream dbt model joins this back to the main mart for dashboarding.

**Worked example.** A product team asks: "What is the effect of enabling the API integration feature (`T`) on 12-month NRR (`Y`)?" The confounders (from the DAG) are `industry`, `seat_count`, `prior_12m_nrr`, `time_to_first_integration_days`. Using `CausalForestDML` with `LightGBMRegressor` as the nuisance model on 50k accounts produces: ATE = +8.3pp on NRR (95% CI: +5.1, +11.5pp). Heterogeneity: CATE is concentrated in accounts with `seat_count > 50` (CATE = +14.2pp vs +3.1pp for smaller accounts).

---

### P3 — Propensity-Score Adjustment in Cohort Comparison Studies

**Primitive**: #8 Propensity Score Methods → [`../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md`](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md)

**When to use.** You are comparing two cohorts that were not randomly assigned (e.g., users who adopted a new feature vs. those who did not) and want to estimate the treatment effect while controlling for observed confounders. The confounder set is moderate (3–10 variables). DML is overkill; naive regression is insufficient.

**The problem it solves.** Cohort comparison studies in product analytics are almost always confounded by adoption bias: users who adopt new features tend to be more engaged, have larger accounts, or have different use-case profiles. A raw comparison overstates the effect of the feature.

**Mechanic.**

Three propensity-score estimators in increasing robustness:

1. **Matching**: for each treated unit, find the nearest control unit by propensity score (or Mahalanobis distance on the confounders). Estimate ATE or ATT on matched pairs. Simple and interpretable; loses data from unmatched controls.
2. **Inverse Probability Weighting (IPW)**: weight each unit by `1 / P(T=t|X)`. Treated units with low propensity get high weight (they are "surprising" adopters). Unbiased under correct propensity model; numerically unstable with extreme weights — clip or stabilize.
3. **Doubly Robust (DR) / AIPW**: combines outcome model and propensity model. Unbiased if *either* model is correctly specified. Recommended default.

**Overlap check (mandatory before reporting).** Plot propensity score distributions for treated and control groups. If the distributions do not overlap sufficiently (common support region is empty at the tails), IPW estimates are unreliable. Trim or clip units outside the common support before estimation.

**dbt + Python pattern.**

```sql
-- dbt: fct_propensity_cohort (grain: one row per account)
select
    account_id,
    case when feature_enabled_date is not null then 1 else 0 end as treated,
    outcome_90d_nrr,
    account_age_days,
    seat_count,
    plan_tier,
    prior_mrr
from {{ ref('dim_accounts') }}
left join {{ ref('fct_feature_adoption') }} using (account_id)
```

```python
# Python estimation
from sklearn.linear_model import LogisticRegression
from econml.dr import DRLearner

X = df[['account_age_days', 'seat_count', 'plan_tier_encoded', 'prior_mrr']]
T = df['treated']
Y = df['outcome_90d_nrr']

dr = DRLearner(model_propensity=LogisticRegression(), model_regression=LightGBMRegressor())
dr.fit(Y, T, X=X)
ate = dr.ate(X)
```

**Worked example.** An analytics team compares 90-day retention for accounts that adopted SSO (`treated = 1`, n=1,240) vs. those that did not (`treated = 0`, n=8,700). Raw lift: +12pp. After DR estimation with confounders `seat_count`, `plan_tier`, `account_age_days`, and `prior_support_tickets`: adjusted lift = +6.2pp (95% CI: +3.8, +8.6pp). The raw comparison overstated the effect nearly 2x due to adoption bias (larger enterprise accounts both adopted SSO and retained better independently).

---

### P4 — Difference-in-Differences on Policy/Feature Rollout

**Primitive**: #6 Difference-in-Differences → [`../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md`](../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md)

**When to use.** A feature or policy was rolled out to a defined group at a defined point in time, and you have pre-rollout data for both the treated group and a comparable control group. Classic for staged feature rollouts, pricing changes applied to specific geographies or plan tiers, and policy interventions.

**The problem it solves.** Pre/post comparisons for the treated group alone conflate the feature effect with secular trends (the world changes over time independent of the treatment). DiD removes time trends by differencing against a contemporaneous control group, producing the ATT under the parallel-trends assumption.

**Mechanic.**

```
DiD estimator:
  ATT = (Ȳ_treated_post - Ȳ_treated_pre) - (Ȳ_control_post - Ȳ_control_pre)

In regression form:
  Y_it = α + β·Treated_i + γ·Post_t + δ·(Treated_i × Post_t) + ε_it
  δ is the DiD estimate (ATT)
```

**Parallel-trend test (required before reporting).**

```sql
-- dbt: pre-period trend check (≥3 periods before rollout)
select
    period,
    group_type,
    avg(outcome_metric) as avg_metric
from {{ ref('fct_did_panel') }}
where period < rollout_date
group by 1, 2
order by 1
```

Plot the pre-period averages for treated and control groups. If lines are parallel (the difference is roughly constant), the parallel-trend assumption is plausible. If they diverge in the pre-period, DiD is biased — consider synthetic control (#7) instead.

**Staggered rollout (heterogeneous treatment timing).** If the rollout was phased across cohorts over multiple periods, the simple two-way fixed effects (TWFE) estimator is biased when treatment effects are heterogeneous across cohorts. Use Callaway-Sant'Anna or Sun-Abraham estimators instead (available in `csdid` / `staggered` Python packages).

**Unit-level fixed effects.** Add unit FE (`account_id` or `user_id`) to control for time-invariant unobserved confounders:

```
Y_it = α_i + γ_t + δ·(Treated_i × Post_t) + ε_it
```

This absorbs all stable account-level characteristics (industry, size, ACV at baseline) and improves precision in panel data.

**Worked example.** A SaaS company rolls out a new in-app guided tour to accounts on the Growth plan on a specific rollout date. Pro plan accounts serve as controls. Pre-period: 6 months of monthly engagement data. DiD estimate on 30-day activation rate: +9.1pp (p < 0.001). Pre-trend test: parallel across 5 pre-periods (max deviation 0.8pp, well within sampling noise). With unit-level FE, the estimate tightens to +8.7pp (SE = 0.9pp).

---

### P5 — Synthetic Control for Single-Unit Causal Questions

**Primitive**: #7 Synthetic Control → [`../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md`](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md)

**When to use.** The treated unit is a single entity — one major customer, one geographic market, one product SKU, one business segment — and there is no single natural control unit that is clearly comparable. A donor pool of untreated units exists.

**The problem it solves.** DiD requires a valid parallel-trend assumption between the treated unit and the control group. For a single major customer or segment, it is rarely the case that one other unit serves as a clean comparison. Synthetic control constructs a weighted average of donor units that best matches the treated unit's pre-treatment trajectory, producing a data-driven counterfactual.

**Mechanic.**

```
Synthetic control:
  Y^_0_t = Σ_j w_j · Y_jt   (for t < treatment date)

Weights w_j ≥ 0, Σ w_j = 1, chosen to minimize:
  ||Y_treated_pre - Σ w_j Y_j_pre||²  (pre-period fit)

Treatment effect: α_t = Y_treated_t - Y^_0_t   (for t ≥ treatment date)
```

**Inference via placebo permutation.** Apply the synthetic control to each donor unit in turn (as if it were the treated unit). The distribution of placebo effects is the null; the treated unit's result is meaningful if it falls in the tail (p = rank / n_donors).

**Practical constraints.** Donor pool: 10–50 units. Pre-period: ≥ as long as post-period (2–3× ideal). Pre-period RMSPE > 5% of outcome scale signals a poor fit — expand the pool or check for structural breaks.

**Worked example.** A top-10 customer (Acme Corp) experienced a major account expansion event tied to a bespoke data integration delivered on 2025-07-01. The product team wants to estimate incremental ARR attributable to the integration. Synthetic control is constructed from the 38 other enterprise accounts in the same vertical with similar pre-treatment ARR trajectory. Pre-period fit RMSPE = 2.1% of ARR scale. Post-treatment gap: +$420k ARR over 6 months vs. synthetic counterfactual. Placebo test on 38 donors: only 1/38 shows a gap this large by chance (p = 0.026). Robust to dropping the 3 highest-weight donors.

---

### P6 — Instrumental Variables from Natural Experiments in Product Logs

**Primitive**: #4 Instrumental Variables → [`../../foundations-causal-inference/assets/templates/causal-inference/04-instrumental-variables.md`](../../foundations-causal-inference/assets/templates/causal-inference/04-instrumental-variables.md)

**When to use.** Unobserved confounders make propensity or DML approaches unreliable, but a natural experiment in the product logs creates exogenous variation: partial-compliance A/B allocation, infrastructure rollout batches, randomized nudge campaigns, or geographic default variation.

**The problem it solves.** IV identifies LATE — the causal effect for compliers (units whose treatment status is changed by the instrument). Strong instrument + valid exclusion restriction → unbiased estimate despite unobservable confounding.

**Two validity conditions (both required).**

1. **Relevance**: F-statistic on first-stage regression `T ~ Z + X` > 10 (Stock & Yogo 2005 threshold).
2. **Exclusion restriction**: Z affects Y only through T. Untestable — argue from domain knowledge.

**Common instruments in warehouse logs:** randomized assignment flag with partial compliance; rollout-wave / infrastructure batch (exogenous conditional on time); randomized pricing email (Z = email received, T = plan upgrade, Y = NRR).

```sql
-- dbt: fct_iv_instrument (grain: one row per user)
select
    user_id,
    -- Instrument: was user in the batch that received the feature email?
    case when email_campaign_batch = 'treatment' then 1 else 0 end as z_instrument,
    -- Treatment: did user actually upgrade their plan?
    case when plan_upgraded_within_30d then 1 else 0 end as t_treated,
    -- Outcome
    nrr_90d,
    -- Covariates (for conditional IV / 2SLS)
    account_age_days, seat_count, plan_tier_at_send
from {{ ref('fct_email_campaign') }}
join {{ ref('dim_accounts') }} using (account_id)
```

```python
# 2SLS estimation
from linearmodels.iv import IV2SLS
import statsmodels.formula.api as smf

# First stage: check F-stat
first_stage = smf.ols('t_treated ~ z_instrument + account_age_days + seat_count', data=df).fit()
print(f"First-stage F = {first_stage.fvalue:.1f}")  # Must be > 10

# 2SLS
res = IV2SLS.from_formula(
    'nrr_90d ~ 1 + account_age_days + seat_count + [t_treated ~ z_instrument]', data=df
).fit()
print(res.summary)
```

**Worked example.** A growth team runs a pricing-email nudge campaign (50% random holdout). 34% of email recipients upgraded their plan vs. 11% of holdout — a strong instrument (F = 218). IV LATE estimate: upgrading plan causes +18.4pp 90-day NRR. OLS estimate (naive): +7.1pp — drastically understated because users who self-select into upgrading are already higher-intent. The IV corrects for this self-selection.

---

### P7 — Sensitivity Analysis as a Release Artifact

**Primitive**: #12 Sensitivity Analysis → [`../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md`](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md)

**When to use.** Before publishing any observational causal estimate to a business stakeholder or including it in a metric definition, a dashboard, or a decision document. Sensitivity analysis is not optional — it is the due-diligence gate that distinguishes an observational estimate from a causal claim.

**The problem it solves.** Every observational study has unobserved confounders. Sensitivity analysis answers: "How strong would an unmeasured confounder have to be to explain away the estimated effect?" If stronger than any observed confounder, the estimate is robust; if weaker, it is fragile and should not drive action.

**E-value (mandatory).** The E-value (VanderWeele & Ding 2017) is the minimum association strength an unmeasured confounder would need with *both* treatment and outcome to fully explain away the result:

```
E-value = RR + √(RR · (RR - 1))   where RR = estimated risk/rate ratio
```

Example: adjusted RR = 2.0 → E-value = 3.41. If the strongest observed confounder has RR ≈ 1.8, the estimate is reasonably robust.

**Rosenbaum bounds (matched designs).** Quantify how large hidden bias Γ must be to render the result non-significant. Report: "Robust to hidden bias Γ ≤ 2.4." Use `scipy.stats.wilcoxon` with iterative Γ from 1.0 to 3.0.

**Release artifact format.** Version this card in the dbt model's `description` YAML block:

```
Estimand: ATT — effect of [treatment] on [outcome] | Method: [DML/DR/DiD/IV/SynCon]
Population: [sample] | Estimate: [value] (95% CI: [lo, hi])
Identification: [DAG reference; assumptions] | E-value: [value]
Sensitivity: [Robust/Fragile] vs strongest observed confounder RR ≈ [value]
Data vintage: [date range] | Approved by: [owner]
```

---

## Anti-Pattern Catalog

### A1 — Including a Mediator as a Control Variable

**Primitives implicated**: #1 DAGs, #3 Backdoor Criterion, #11 Mediation Analysis

**Description.** A regression includes a variable that lies on the causal path between treatment and outcome — a mediator — as a "control" to "hold everything else constant."

**Why it fails.** Conditioning on a mediator blocks the causal path being estimated. The coefficient on the treatment variable then measures only the *direct* effect — the part of the treatment effect that does not operate through the mediator — while appearing to measure the total effect. Worse: if the mediator is also a collider for another pair of variables, conditioning on it opens a spurious back-door path, introducing bias in a direction that is hard to predict without the full DAG.

**Concrete example.** Estimating the effect of `onboarding_call_completed` on `retained_at_90d` while controlling for `feature_usage_score_week2`. If the call *causes* feature usage, which then causes retention, controlling for feature usage blocks the main mechanism and the coefficient on `onboarding_call` will understate the true causal effect — potentially to near zero.

**Fix.** Draw the DAG before running any regression. Use the backdoor criterion to identify the adjustment set. If the mechanism (the mediated path) is the question, use mediation analysis (#11) explicitly — do not run a regression that inadvertently conditions on the mediator.

---

### A2 — Calling a Regression Coefficient "The Effect of X"

**Primitives implicated**: #1 DAGs, #2 Do-Calculus, #3 Backdoor Criterion, #10 Simpson's Paradox

**Description.** An analyst runs `Y ~ T + X1 + X2 + X3` in SQL or Python and reports the coefficient on T as "the causal effect of T on Y."

**Why it fails.** A regression coefficient estimates the partial correlation of T with Y conditional on X1, X2, X3. This equals the causal effect only if the adjustment set {X1, X2, X3} satisfies the backdoor criterion relative to the DAG. If any confounder is omitted, the coefficient is biased. If a collider or mediator is included, the coefficient is biased in the opposite direction. The regression function has no mechanism to distinguish these cases — only the DAG does.

**Concrete example.** Running `churn_rate ~ support_tickets + account_age + seat_count` and reporting: "each additional support ticket causes a +2.1pp increase in churn." If `support_tickets` is partially a mediator (poor onboarding → tickets → churn) and partially a confounder proxy, the coefficient conflates both pathways. The "2.1pp" figure is not the interventional effect of reducing tickets; it is an associational partial correlation.

**Fix.** Draw the DAG. Verify the adjustment set with the backdoor criterion. State explicitly: "This estimate assumes {confounders included} block all back-door paths and no mediators were conditioned on." Compute the E-value (#12) before reporting.

---

### A3 — Selection Bias from Filtering on Outcome

**Primitives implicated**: #1 DAGs, #3 Backdoor Criterion (collider bias)

**Description.** An analysis restricts its sample based on a variable that is causally downstream of the treatment (or of both the treatment and a confounder), then interprets the effect in this filtered sample as the population effect.

**Classic product-analytics form.** Studying only converted users to understand what drives high LTV. Or: studying only users who reached the activation event to understand what caused activation. The filter (converted = yes; activated = yes) is an outcome variable — a collider in the DAG — and conditioning on it opens spurious associations between all of its causes.

**Why it fails.** Collider conditioning creates a statistical association between two variables that are causally independent in the unfiltered population. In the filtered sample (converted users only), product features and acquisition channels that both influence conversion appear correlated — even if they are independent in the real world. This produces recommendations that are wrong in direction for the unfiltered population.

**Concrete example.** An analysis of "what drives high NRR among churned accounts" filters to `churned = 1`. Within churned accounts, it finds that `heavy_support_users` have *higher* NRR than `light_support_users`. The team concludes: "support usage predicts retention even among churned accounts." This is likely collider bias — both support usage and NRR independently predict churn; conditioning on `churned = 1` induces a spurious positive correlation between them within the sample.

**Fix.** Never filter on outcome variables (or their causal descendants). If the question is about a specific subpopulation (e.g., churned accounts), acknowledge that the analysis is descriptive for that subgroup only and cannot be generalized causally to the full population. Use the DAG to check whether the filter variable is a collider before applying any restriction.

---

### A4 — Survivorship Bias in Cohort Analyses

**Primitives implicated**: #1 DAGs, #6 DiD, #7 Synthetic Control

**Description.** A cohort analysis measures outcomes only for users or accounts that "survived" long enough to be in the dataset at measurement time, ignoring those that churned before the measurement window.

**Why it fails.** Churned accounts are a censored sample: they were removed from the analysis by an event that is causally related to the treatment and the outcome. Any cohort metric computed on survivors systematically overstates treatment effects because the treatment may have prolonged survival — so the treated group has more survivors, but the survivors are not a representative sample of the original treated population.

**Concrete example.** A DiD analysis measures the effect of a new onboarding flow on "engagement score at 90 days" for users who are still active at day 90. If the new onboarding flow reduced early churn by 15%, the treated cohort has more survivors at day 90, and those survivors may be lower-engagement users who would have churned under the old flow. The measured engagement score is lower in the treated group not because the new onboarding hurts engagement, but because it retains a broader (less highly engaged) user base. The DiD estimate is wrong in direction.

**Fix.** Define cohort membership at treatment time (time zero), not at measurement time. For survival analyses, use time-to-event methods (Cox proportional hazard, Kaplan-Meier). For outcome analyses, use intent-to-treat (ITT) framing: include all units assigned to treatment at baseline, using imputed or censored outcomes for those who churned.

---

### A5 — Treating Correlation Strength as Causal Strength

**Primitives implicated**: #1 DAGs, #2 Do-Calculus, #10 Simpson's Paradox, #12 Sensitivity Analysis

**Description.** A strong correlation (R² = 0.7, β significant at p < 0.001) between feature usage and a business outcome is reported as evidence that the feature "strongly drives" the outcome. Teams then prioritize features for investment based on correlation magnitude.

**Why it fails.** Correlation magnitude is not evidence of causal effect magnitude. A confounded relationship can produce arbitrarily large correlations. A causal relationship can produce small correlations if the treatment has a small effect on a noisy outcome. The features most correlated with retention are typically adoption indicators — and adoption is driven by engagement which itself drives retention. The coefficient is measuring the engagement-retention relationship, not the feature-retention relationship.

**Concrete example.** A Looker dashboard shows: accounts with `data_export_enabled = true` have 40% higher NRR than those without. The product team concludes: "data export is our strongest NRR driver." But data export is adopted almost exclusively by enterprise accounts with dedicated data teams — and enterprise accounts have higher NRR independent of data export. The correlation is +0.6; the causal effect after DML adjustment is +2.1pp NRR (not +40%).

**Fix.** Report effect estimates from causal models (DML, IPW-DR, DiD, IV), not correlation coefficients. Include E-values for every observational estimate. Label dashboards with "observational correlation — not causal estimate" when the causal assumption has not been tested. Run a "what would we expect to see if the correlation were driven entirely by confounding?" stress test using the Omitted Variable Bias formula before citing any coefficient.

---

## Recipes

### R1 — Observational Treatment Effect with ML

**Scenario.** You have observational warehouse data. An A/B test was not run. You want a credible ATE (and optionally CATE) estimate. The confounder set is high-dimensional. The estimate will be used to inform a product investment decision.

**Stack**: #1 DAG → #3 Backdoor Criterion → #8 DR Estimation / #2 DML → #12 Sensitivity

**Step 1: Draw and validate the DAG.**

Before touching SQL, draw the DAG on paper or in a tool like DAGitty (dagitty.net). For each variable in the warehouse:
- [ ] Is it a confounder (common cause of T and Y)?
- [ ] Is it a mediator (on the path T → M → Y)?
- [ ] Is it a collider (caused by both T and some other variable)?
- [ ] Is it irrelevant (d-separated from both T and Y)?

Use the backdoor criterion to identify the minimal adjustment set. Document this in a `# causal_assumptions:` comment in the dbt model YAML.

**Step 2: Build the estimation mart.**

```sql
-- dbt: fct_causal_cohort
-- grain: one row per account at the relevant time window
-- CAUSAL ASSUMPTION: adjustment set is {account_age_days, seat_count, plan_tier, prior_nrr}
-- These block all backdoor paths from T to Y per DAG v2025-11-15
-- feature_usage_score_week4 is a MEDIATOR — excluded from this mart
select
    account_id,
    feature_enabled_flag                     as t_treatment,
    nrr_365d                                 as y_outcome,
    account_age_days,
    seat_count,
    plan_tier,
    nrr_prior_365d                           as prior_nrr
from {{ ref('dim_accounts') }}
join {{ ref('fct_feature_adoption') }} using (account_id)
where snapshot_date = '{{ var("cohort_date") }}'
```

**Step 3: Run DML with cross-fitting.**

```python
from econml.dml import CausalForestDML
from lightgbm import LGBMRegressor, LGBMClassifier
import pandas as pd, numpy as np

df = pd.read_sql("select * from analytics.fct_causal_cohort", conn)
X = df[['account_age_days', 'seat_count', 'plan_tier_encoded', 'prior_nrr']]
T = df['t_treatment'].values
Y = df['y_outcome'].values

est = CausalForestDML(
    model_y=LGBMRegressor(n_estimators=200),
    model_t=LGBMClassifier(n_estimators=200),
    n_estimators=1000,
    cv=5,         # 5-fold cross-fitting
    random_state=42
)
est.fit(Y, T, X=X)

ate, ate_lb, ate_ub = est.ate(X), *est.ate_interval(X, alpha=0.05)
print(f"ATE = {ate:.3f}  (95% CI: {ate_lb:.3f}, {ate_ub:.3f})")

# CATE for each account
cate = est.effect(X)
```

**Step 4: Run sensitivity bounds.**

```python
# E-value (VanderWeele & Ding 2017)
# Convert ATE to approximate risk ratio for E-value calculation
import math

rr = math.exp(ate / y_std)  # approximate if outcome is continuous
e_value = rr + math.sqrt(rr * (rr - 1))
print(f"E-value = {e_value:.2f}  (requires unmeasured confounder of RR >= {e_value:.2f} to explain away)")

# Compare to strongest observed confounder RR
strongest_obs_rr = ...  # compute from first-stage OLS
print(f"Strongest observed confounder RR ≈ {strongest_obs_rr:.2f}")
```

**Step 5: Produce release card.**

Fill in the Causal Estimate Release Card template (see P7) and attach it as a comment in the relevant dbt model YAML. Gate stakeholder communication on the E-value check: if E-value < 1.5× strongest observed confounder, flag the estimate as fragile and do not recommend action without stronger design evidence.

**Expected output.** ATE with 95% CI, CATE by account segment, E-value, and a documented adjustment set that a future analyst can audit. The mart `fct_causal_cohort` is a versioned, documented, reproducible artifact.

---

### R2 — Cohort Policy Impact with DiD

**Scenario.** A new pricing tier was rolled out to one segment of your customer base on a specific date. You want to estimate the causal impact on ARR over the next 12 months. Pre-period data is available for both treated and control segments.

**Stack**: #6 DiD → #1 DAG (parallel trends justification) → Unit FE → Permutation inference

**Step 1: Build the panel mart.**

```sql
-- dbt: fct_did_panel
-- grain: one row per (account, month)
-- treated: accounts on the Growth plan (received new pricing 2025-10-01)
-- control: accounts on the Pro plan (unchanged pricing throughout)
select
    account_id,
    date_trunc('month', snapshot_date)       as period,
    case when plan = 'growth' then 1 else 0 end as treated,
    case
        when snapshot_date >= '2025-10-01'
        and plan = 'growth' then 1
        else 0
    end                                      as post_treat,
    arr_usd,
    seat_count,
    industry
from {{ ref('fct_account_snapshots') }}
where plan in ('growth', 'pro')
  and snapshot_date between '2025-04-01' and '2026-09-30'
```

**Step 2: Parallel-trend test.**

Run in Python or directly in a BI tool:

```python
import statsmodels.formula.api as smf

pre = df[df['period'] < '2025-10-01']
pre_trend = smf.ols('arr_usd ~ C(period) * C(treated)', data=pre).fit()
# Check: interaction coefficients should be near zero and jointly insignificant
print(pre_trend.summary())
```

If the pre-trend F-test for the interaction terms is significant (p < 0.05), parallel trends is violated. Consider synthetic control (Recipe R3) as an alternative.

**Step 3: DiD with unit fixed effects.**

```python
from linearmodels.panel import PanelOLS
import pandas as pd

df = df.set_index(['account_id', 'period'])
mod = PanelOLS.from_formula(
    'arr_usd ~ post_treat + EntityEffects + TimeEffects',
    data=df
)
res = mod.fit(cov_type='clustered', cluster_entity=True)
print(res.summary)
# Coefficient on post_treat is the DiD ATT estimate
```

**Step 4: Permutation inference (robustness).**

Permute the treatment assignment 500 times and re-run the DiD estimator each time. The empirical p-value is the fraction of permuted estimates larger in absolute value than the observed estimate. This is distribution-free and robust to heteroskedasticity.

```python
import numpy as np

observed_att = res.params['post_treat']
perm_atts = []
for _ in range(500):
    df_perm = df.copy()
    # Permute treatment at account level (preserve panel structure)
    treated_ids = df_perm.index.get_level_values('account_id').unique()
    shuffled = np.random.permutation(treated_ids)
    treat_map = dict(zip(treated_ids, df_perm.groupby('account_id')['treated'].first()[shuffled].values))
    df_perm['treated_perm'] = df_perm.index.get_level_values('account_id').map(treat_map)
    df_perm['post_treat_perm'] = (df_perm['treated_perm'] == 1) & (df_perm.index.get_level_values('period') >= '2025-10-01')
    mod_perm = PanelOLS.from_formula('arr_usd ~ post_treat_perm + EntityEffects + TimeEffects', data=df_perm)
    perm_atts.append(mod_perm.fit(cov_type='clustered', cluster_entity=True).params['post_treat_perm'])

p_perm = np.mean(np.abs(perm_atts) >= np.abs(observed_att))
print(f"DiD ATT = {observed_att:,.0f}  permutation p = {p_perm:.3f}")
```

**Expected output.** DiD ATT with clustered standard errors, parallel-trend test result, permutation p-value, and a dbt mart that is reproducible and auditable. Document assumptions (which plans treated/control, rollout date, which confounders are absorbed by FE) in dbt YAML.

---

### R3 — Single-Customer Impact Estimate via Synthetic Control

**Scenario.** Your largest customer (or a major business segment) underwent a significant intervention — a bespoke integration delivered, a dedicated CSM assigned, or a major services engagement completed — and you want to estimate incremental ARR attributable to the intervention. There is no clean control account.

**Stack**: #7 Synthetic Control → Placebo tests → Donor-variation robustness

**Step 1: Build the donor pool mart.**

```sql
-- dbt: fct_synthetic_control_donors
-- grain: one row per (account, month)
-- exclude the treated account from this mart
-- include only accounts in the same vertical and ARR tier as the treated account
select
    account_id,
    date_trunc('month', snapshot_date)  as period,
    arr_usd,
    -- Optionally include other predictors for the pre-period fit
    product_usage_score,
    seat_count,
    support_ticket_volume
from {{ ref('fct_account_snapshots') }}
where account_id != '{{ var("treated_account_id") }}'
  and industry = '{{ var("treated_industry") }}'
  and arr_tier = '{{ var("treated_arr_tier") }}'
  and snapshot_date between
    '{{ var("pre_period_start") }}'
    and '{{ var("post_period_end") }}'
```

**Step 2: Fit the synthetic control.**

```python
from scipy.optimize import minimize
import numpy as np

# treated_pre: [T] pre-period outcome for treated unit
# donor_pre:   [T × N] matrix of donor pre-period outcomes

def sc_loss(w, treated_pre, donor_pre):
    synth = donor_pre @ w
    return np.sum((treated_pre - synth) ** 2)

N = donor_pre.shape[1]
w0 = np.ones(N) / N
constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
bounds = [(0, 1)] * N

res = minimize(sc_loss, w0, args=(treated_pre, donor_pre),
               method='SLSQP', bounds=bounds, constraints=constraints)
w_opt = res.x

# Synthetic control counterfactual (full period)
synth_full = donor_full @ w_opt

# Treatment effect: actual minus synthetic
effect = treated_full - synth_full
print(f"Pre-period RMSPE: {np.sqrt(np.mean((treated_pre - donor_pre @ w_opt)**2)):.2f}")
print(f"Cumulative post-treatment effect: {np.sum(effect[post_idx:]):.0f}")
```

**Step 3: Placebo tests on donors.**

```python
placebo_effects = []
for j in range(N):
    donor_j_pre = np.delete(donor_pre, j, axis=1)
    donor_j_full = np.delete(donor_full, j, axis=1)
    res_j = minimize(sc_loss, np.ones(N-1)/(N-1), args=(donor_pre[:, j], donor_j_pre), ...)
    synth_j = donor_j_full @ res_j.x
    placebo_effects.append(np.sum((donor_full[:, j] - synth_j)[post_idx:]))

p_value = np.mean(np.abs(placebo_effects) >= np.abs(np.sum(effect[post_idx:])))
print(f"Placebo p-value = {p_value:.3f}  (n_donors = {N})")
```

**Step 4: Donor-variation robustness.**

Refit the synthetic control with the top-5-weight donors dropped (leave-one-out and leave-five-out). If the post-treatment gap is stable across these variations, the estimate is robust. If removing a single high-weight donor collapses the gap, the result depends on that one donor and is fragile.

**Expected output.** Monthly counterfactual ARR trajectory, cumulative treatment effect with confidence from placebo distribution, pre-period RMSPE, and a robustness table showing the gap under donor variations. Version-control the weights (`w_opt`) in a dbt seed or in the mart metadata for reproducibility.

---

## Composition

| Workflow | Primary method | Fallback | Close with |
|----------|---------------|----------|-----------|
| Causal metric definition (observational) | P1 DAG → P2 DML (high-dim) or P3 DR (moderate) | P4 DiD if panel exists | P7 sensitivity card |
| Feature rollout impact | P4 DiD (treated + control segment, rollout date known) | P5 synthetic control (no control group) | P7 sensitivity card |
| Voluntary-adoption cohort | P3 propensity DR or P2 DML | P6 IV if natural experiment exists | P7 sensitivity card |
| Single unit / major customer | P5 synthetic control + placebo | — | P7 + donor robustness |

**Do not double-adjust.** Do not run propensity matching *and* regression adjustment on the same confounders — double-robustness is a statistical property, not a license to stack arbitrary methods. Do not DiD *and* propensity-match within periods. Pick one identification strategy per estimand.

---

## Primitive Links

| Pattern / Anti-Pattern | Primitive | File |
|------------------------|-----------|------|
| DAG-driven feature engineering | #1 DAGs and Structural Causal Models | [`../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md`](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md) |
| Adjustment set identification | #3 Backdoor / Frontdoor Criterion | [`../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md`](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md) |
| DML / CausalForest for ATE/CATE | #8 Propensity Score Methods + #9 CATE/Uplift | [`../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md`](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md), [`../../foundations-causal-inference/assets/templates/causal-inference/09-cate-uplift.md`](../../foundations-causal-inference/assets/templates/causal-inference/09-cate-uplift.md) |
| Difference-in-Differences | #6 Difference-in-Differences | [`../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md`](../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md) |
| Synthetic control | #7 Synthetic Control | [`../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md`](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md) |
| Instrumental variables | #4 Instrumental Variables | [`../../foundations-causal-inference/assets/templates/causal-inference/04-instrumental-variables.md`](../../foundations-causal-inference/assets/templates/causal-inference/04-instrumental-variables.md) |
| Sensitivity analysis release gate | #12 Sensitivity Analysis | [`../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md`](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md) |
| Including mediator as control (A1) | #1 DAGs, #3 Backdoor, #11 Mediation | [`../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md`](../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md) |
| Regression coefficient as causal effect (A2) | #2 Do-Calculus, #10 Simpson's Paradox | [`../../foundations-causal-inference/assets/templates/causal-inference/02-do-calculus.md`](../../foundations-causal-inference/assets/templates/causal-inference/02-do-calculus.md), [`../../foundations-causal-inference/assets/templates/causal-inference/10-simpsons-paradox.md`](../../foundations-causal-inference/assets/templates/causal-inference/10-simpsons-paradox.md) |
| Selection / survivorship bias (A3, A4) | #1 DAGs, #3 Backdoor (collider bias) | [`../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md`](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md) |

**Full primitive reference**: [`../../foundations-causal-inference/SKILL.md`](../../foundations-causal-inference/SKILL.md)

---

## Sources

- Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C., Newey, W., & Robins, J. (2018). *Double/debiased machine learning for treatment and structural parameters*. The Econometrics Journal, 21(1). [https://arxiv.org/abs/1608.00060](https://arxiv.org/abs/1608.00060). Canonical DML reference; cross-fitting, Neyman orthogonality.
- Abadie, A., Diamond, A., & Hainmueller, J. (2010). *Synthetic control methods for comparative case studies*. Journal of the American Statistical Association, 105(490). Foundation for synthetic control inference and placebo testing.
- Callaway, B., & Sant'Anna, P.H.C. (2021). *Difference-in-differences with multiple time periods*. Journal of Econometrics, 225(2). [https://arxiv.org/abs/1803.09015](https://arxiv.org/abs/1803.09015). Staggered DiD; Callaway-Sant'Anna estimator for heterogeneous treatment timing.
- VanderWeele, T.J., & Ding, P. (2017). *Sensitivity analysis in observational research: Introducing the E-value*. Annals of Internal Medicine, 167(4). E-value methodology and interpretation.
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. DAGs, do-calculus, backdoor/frontdoor criteria.
- Imbens, G.W., & Rubin, D.B. (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*. Cambridge University Press. Propensity score methods, matching, and IV in the potential-outcomes framework.
- Angrist, J.D., & Pischke, J.S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. Practical IV, DiD, and RDD; identification assumption heuristics.
- Microsoft EconML library: [https://econml.azurewebsites.net/](https://econml.azurewebsites.net/). Open-source Python library for DML, CausalForest, DR learners, and IV estimation.
- Rosenbaum, P.R. (2002). *Observational Studies* (2nd ed.). Springer. Rosenbaum bounds and sensitivity analysis for matched studies.
- Hernán, M.A., & Robins, J.M. (2020). *What If*. Chapman & Hall/CRC. [https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/). IPW, marginal structural models, and time-varying treatments.
