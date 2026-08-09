---
description: Causal inference applied to product management — feature impact attribution, cohort confounding, heterogeneous effects, mediation in onboarding chains, quasi-experiments, sensitivity analysis, and counterfactual post-mortems. Anchored to primitives #1–#12 from foundations-causal-inference.
last_verified: 2026-05-02
status: stable
---

# Causal Inference Applied: Product Management

> **Gate before invoking:** Check [`foundations-causal-inference` § When to Apply](../../foundations-causal-inference/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Feature-Impact Attribution: Separating Treatment Effect from Selection](#p1--feature-impact-attribution-separating-treatment-effect-from-selection)
  - [P2 — Cohort Confounding in Pre/Post Rollouts (DiD)](#p2--cohort-confounding-in-prepost-rollouts-did)
  - [P3 — Heterogeneous-Effect Analysis: Who Benefits, Who Is Hurt (CATE)](#p3--heterogeneous-effect-analysis-who-benefits-who-is-hurt-cate)
  - [P4 — Onboarding and Retention Causal Chains via Mediation Analysis](#p4--onboarding-and-retention-causal-chains-via-mediation-analysis)
  - [P5 — Quasi-Experiments When Proper A/B Is Impossible](#p5--quasi-experiments-when-proper-ab-is-impossible)
  - [P6 — Sensitivity Analysis Before Claiming a Feature Moved the Needle](#p6--sensitivity-analysis-before-claiming-a-feature-moved-the-needle)
  - [P7 — Counterfactual Reasoning in Product Reviews and Post-Mortems](#p7--counterfactual-reasoning-in-product-reviews-and-post-mortems)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Power-User Bias: Treating Adopters as the Treatment Population](#a1--power-user-bias-treating-adopters-as-the-treatment-population)
  - [A2 — Conditioning on Retention When Measuring Retention (Collider)](#a2--conditioning-on-retention-when-measuring-retention-collider)
  - [A3 — Calling Correlated Metric Uplift Caused by the Launch](#a3--calling-correlated-metric-uplift-caused-by-the-launch)
  - [A4 — Ignoring Novelty Effects (Treatment Effect That Decays)](#a4--ignoring-novelty-effects-treatment-effect-that-decays)
  - [A5 — Attributing Churn Drop Without a Parallel-Trends Control](#a5--attributing-churn-drop-without-a-parallel-trends-control)
- [Recipes](#recipes)
  - [R1 — Feature Impact Under Non-Random Adoption](#r1--feature-impact-under-non-random-adoption)
  - [R2 — Funnel-Stage Mediation: Find the Activation Bottleneck](#r2--funnel-stage-mediation-find-the-activation-bottleneck)
  - [R3 — Regional Rollout Retention Analysis](#r3--regional-rollout-retention-analysis)
- [Composition](#composition)
- [Sources](#sources)

---

## Framing Note

Most PM causal claims fail before they reach a statistician. The failure is upstream: the question is not "was the p-value right?" but "was the estimand the right one, and was the identification strategy valid for the data-generating process the product team believes is true?"

This file applies the 12 primitives from `foundations-causal-inference` to the specific situations that arise in feature launches, retention analyses, and product post-mortems. The primitives are domain-agnostic; this file is the PM-specific application layer. For the underlying mechanics of each primitive — definitions, worked derivations, and failure modes — open the linked playbooks.

Platform references throughout are Statsig, Eppo, and Optimizely because they are the experimentation platforms most likely to be in use. The methods generalize to any A/B or observational setup.

---

## Pattern Catalog

### P1 — Feature-Impact Attribution: Separating Treatment Effect from Selection

**The PM problem.** A new collaboration feature ships. Usage is tracked. Users who open the feature have 22% higher 30-day retention. The PM presents this as proof the feature drives retention. The analyst objects. Both are half-right.

**What actually happened.** Users who adopt a new feature are not a random draw from the user population. They are typically more engaged, more experienced, or more aligned with the product's core value. This selection means the observed retention gap between adopters and non-adopters conflates (a) the causal effect of the feature and (b) the pre-existing engagement advantage of the adopters. Naive comparison gives a biased, almost always upward-inflated estimate of the feature's causal effect.

**The causal fix.**

Draw the DAG first (primitive #1): the assumed data-generating process has `Engagement Level → Feature Adoption` and `Engagement Level → Retention`, making Engagement Level a confounder. The feature's causal arrow is `Feature Adoption → Retention`, and the goal is to isolate it.

If adoption was randomized (e.g., a proper A/B test with forced or gated exposure), the randomization breaks the confounder arrow and the comparison is clean. If adoption was organic — the typical case — use propensity score methods (primitive #8): model the probability of adopting the feature as a function of pre-adoption engagement, tenure, plan type, and other measured confounders. Then use a doubly robust (DR/AIPW) estimator to produce a debiased ATE. For subgroup effects, layer CATE estimation (primitive #9) on top.

**Concrete output.** After propensity adjustment, the 22% retention gap typically compresses to 6–12% in practice. The compressed estimate is the one that belongs in the feature review. The original 22% does not disappear as a fact — it tells you something about who uses the feature — but it is not the causal effect.

**Platform note.** Statsig supports CUPED variance reduction natively; Eppo supports CUPED and pre-experiment covariate adjustment. Both reduce variance without changing the estimand. They do not replace propensity adjustment for non-random adoption — CUPED is a variance reduction technique, not a debiasing technique for selection.

**Primitive links.** DAG (#1) → Propensity / DR (#8) → CATE (#9) → Sensitivity analysis (#12).

---

### P2 — Cohort Confounding in Pre/Post Rollouts (DiD)

**The PM problem.** A pricing change, onboarding redesign, or new default setting is rolled out to all users on a specific date. The PM measures average retention before the rollout and after the rollout and reports the difference as the effect of the change.

**What actually happened.** Pre/post comparison without a control group conflates the feature effect with everything else that changed in the same period: seasonality, a competitor move, a simultaneous marketing campaign, an algorithm change by an app store. All of these produce pre/post differences that have nothing to do with the feature.

**The causal fix.**

Difference-in-differences (primitive #6) solves this when a comparable untreated group exists. The DiD estimand is:

```
ATT = (Ȳ_treated,post − Ȳ_treated,pre) − (Ȳ_control,post − Ȳ_control,pre)
```

The control group absorbs the time trend. The critical assumption is **parallel trends**: in the absence of the rollout, the treated and control groups would have moved in parallel. Check this explicitly by plotting pre-rollout trends for both groups across at least 4–6 pre-period cohorts. A diverging pre-trend invalidates DiD and signals that a different control strategy is needed.

**Common control group choices in product analytics:**
- A holdout region (geographic DiD): the rollout covers some markets but not others.
- A waitlist cohort: users who signed up during the rollout window but experienced the old onboarding because of assignment timing.
- Staggered rollout: some teams or plans received the change earlier. Use Callaway–Sant'Anna estimators when timing is staggered and treatment effects are heterogeneous across cohorts.

**When parallel trends fails.** If the treated and control groups were trending differently before the rollout — common when the rollout targeted a specific segment — switch to synthetic control (primitive #7) to construct a weighted counterfactual that matches the pre-treatment trajectory of the treated group.

**Primitive links.** DAG (#1) → DiD (#6) → Synthetic control (#7) as fallback → Sensitivity analysis (#12).

---

### P3 — Heterogeneous-Effect Analysis: Who Benefits, Who Is Hurt (CATE)

**The PM problem.** An A/B test reports a +5% activation lift for the treatment. The PM ships it. Three weeks later, the mobile team notices that mobile new-user activation dropped 8%. The aggregate A/B result masked opposing subgroup effects.

**The causal fix.**

CATE estimation (primitive #9) decomposes the average treatment effect (ATE) into subgroup-level effects, τ(x) = E[Y(1) − Y(0) | X = x]. In product analytics the relevant subgroups are: platform (iOS vs Android vs Web), acquisition channel, plan tier, user tenure bucket, geography, and feature usage history.

**Meta-learner selection by sample size:**
- Large samples (> 50k per arm): DR-learner or R-learner — doubly robust, low regularization bias.
- Medium samples (5k–50k per arm): X-learner — handles imbalanced arms and moderately heterogeneous effects.
- Small samples (< 5k per arm): T-learner with regularized base learners (ridge or gradient boost) — avoid overfitting.

**Uplift framing for product decisions.** For features with optional adoption (notifications opt-in, premium upsell prompts, referral nudges), reframe CATE as uplift: who responds positively to the treatment, who is indifferent, and who reacts negatively? Targets for rollout are the "persuadables" — users with positive uplift. Forcing the feature on users with negative uplift (e.g., an annoying prompt for expert users) hurts the aggregate metric even when the population ATE is positive.

**Reporting standard.** Do not report an aggregate ATE without running at least a pre-specified subgroup analysis on the primary acquisition channels and platforms. An ATE that is positive overall but negative for one major acquisition channel is not a clear ship decision.

**Primitive links.** DAG (#1) → Propensity / DR (#8) to deconfound → CATE / uplift (#9) → Sensitivity (#12) for the strongest subgroup claim.

---

### P4 — Onboarding and Retention Causal Chains via Mediation Analysis

**The PM problem.** The activation metric improved after a new onboarding flow shipped. The PM wants to know which step in the onboarding funnel is responsible, and whether the improvement flows through the aha-moment action or through some other path.

**The causal fix.**

Mediation analysis (primitive #11) decomposes the total effect of the onboarding change (X) on 30-day retention (Y) into:
- **Natural Direct Effect (NDE)**: the part of the effect that bypasses the proposed mechanism.
- **Natural Indirect Effect (NIE)**: the part mediated through the aha-moment action M (e.g., first collaborative session, first export, first connection).

DAG example:
```
Onboarding redesign (X) → Aha-moment completion (M) → 30-day retention (Y)
                        ↘ (direct, e.g., faster time-to-value, reduced confusion) ↗
```

**Where this breaks.** Mediation analysis requires no unmeasured exposure–mediator confounders. If user intent or prior product familiarity affects both whether users complete the aha-moment step and their long-term retention — and this variable is not measured — the mediation decomposition is biased. This is common in B2C onboarding, where user intent at signup varies widely and is rarely captured.

Mitigation: use the backdoor criterion (primitive #3) to identify the minimal sufficient adjustment set for the M → Y relationship, and check whether intent proxies (signup source, plan selected, referral code) can close the gap. Report sensitivity bounds on the NIE (primitive #12) to quantify how large unmeasured confounding would need to be to flip the bottleneck diagnosis.

**Practical output.** "The redesigned step 3 (connecting a data source) accounts for 68% of the activation lift (NIE). The remaining 32% flows through other paths (NDE), possibly through faster loading speed." This directs the next experiment: invest in the data-source connection step.

**Primitive links.** DAG (#1) → Backdoor criterion (#3) for adjustment set → Propensity / DR (#8) for balanced estimates → Mediation (#11) → Sensitivity (#12).

---

### P5 — Quasi-Experiments When Proper A/B Is Impossible

**The PM problem.** A proper randomized experiment is infeasible: the feature gates on account-level thresholds (seat count, storage usage, API call volume), was rolled out to an entire market, or is a platform-level change where user-level randomization violates product integrity. The PM still needs a causal estimate.

**Two quasi-experiment designs for product analytics:**

**Regression Discontinuity (RDD) on engagement thresholds (primitive #5).** When a feature is unlocked at a hard threshold (e.g., "users with > 100 lifetime events get access to the analytics dashboard"), users just above and just below the threshold are similar in all pre-threshold characteristics by continuity. The local ATE at the cutoff is identified by comparing outcomes for users just above vs. just below the threshold. This estimate is local — it applies to users at the margin of the threshold, not to all users — but it is often the most policy-relevant estimate: it answers "should we lower the threshold to extend access?"

Setup checklist for product RDD:
- [ ] Confirm the threshold is not manually gamed (users cannot inflate the running variable strategically).
- [ ] Check for a density discontinuity at the threshold (McCrary test) — if there is one, sorting is present and identification fails.
- [ ] Use MSE-optimal bandwidth selection (Calonico–Cattaneo–Titiunik), not a manually chosen window.
- [ ] Report the local ATE with robust bias-corrected confidence intervals.

**Synthetic Control for regional feature rollouts (primitive #7).** When a feature ships to one market, geography, or product line before others, and no valid control region exists, synthetic control constructs a weighted combination of donor units (other markets or product lines) that best matches the treated unit's pre-rollout trajectory. The donor weights are chosen to minimize pre-period prediction error.

Inference uses permutation tests: apply the synthetic control algorithm to each donor unit in turn and compare their placebo effect distributions to the treated unit's estimated effect. If the treated unit's post-period deviation is an extreme outlier in the placebo distribution, the effect is statistically significant.

**Platform note.** Neither Statsig nor Eppo natively supports RDD or synthetic control — these require custom analysis in Python (the `rdrobust` library for RDD; the `pysyncon` or `synth` packages for synthetic control).

**Primitive links.** DAG (#1) → RDD (#5) for threshold-gated features → Synthetic control (#7) for single-market rollouts → Sensitivity (#12).

---

### P6 — Sensitivity Analysis Before Claiming a Feature Moved the Needle

**The PM problem.** An observational analysis shows that users who completed the new "team invite" step have 18% higher 90-day retention. The PM wants to put this in the board deck. Before it goes in, it needs a sensitivity check.

**The causal fix.**

Every observational claim rests on unverifiable assumptions about unobserved confounders. Sensitivity analysis (primitive #12) quantifies how strong an unobserved confounder would need to be to explain away the result. The E-value is the standard tool:

```
E-value = RR + √(RR × (RR − 1))

For RR = 1.18 (18% retention uplift expressed as a risk ratio):
E-value = 1.18 + √(1.18 × 0.18) = 1.18 + √0.2124 ≈ 1.18 + 0.46 = 1.64
```

An E-value of 1.64 means an unobserved confounder would need to be associated with both the team-invite completion and retention by a risk ratio of at least 1.64 on both margins to fully explain away the 18% retention uplift. Is there a plausible unobserved confounder with that strength? In this example: yes — "invited to the product by a team lead" is a plausible strong confounder for both completing the team-invite step and long-term retention. The E-value is not large enough to dismiss the concern.

**PM-facing language for the board deck.**
- Acceptable: "Users who completed the team-invite step show 18% higher 90-day retention. An unobserved confounder would need an effect size of 1.6× on both margins to explain away this result — consistent with team-lead invitation as a driver."
- Not acceptable: "The team-invite step causes an 18% retention lift."

**Additional check: tipping-point analysis.** State explicitly what level of confounding would reduce the estimate to zero. For continuous outcomes, use the Robins–Rotnitzky sensitivity framework instead of the E-value.

**Primitive links.** DAG (#1) → Sensitivity analysis (#12) → Report E-value alongside every observational point estimate.

---

### P7 — Counterfactual Reasoning in Product Reviews and Post-Mortems

**The PM problem.** A feature launched in Q3. Retention went up 4 points in Q4. The feature review presents this as the feature's impact. But the product also ran a major marketing campaign in October, improved load times, and fixed two critical bugs. The post-mortem attributes the retention gain to the feature because it was the biggest change.

**The causal fix.**

A post-mortem that attributes an outcome to a single intervention without controlling for concurrent changes is doing naive causal attribution — it conflates correlation with causation in exactly the way do-calculus (primitive #2) was designed to prevent.

**Structured counterfactual framing.**

For each candidate cause of the observed outcome change, ask:
1. What would retention have been if only this intervention had happened, and everything else had stayed constant?
2. Does the timing and magnitude of the retention change match the hypothesized mechanism?

Tools:
- **DiD with a holdout** (#6): if any subset of users, cohorts, or markets did not receive the feature, compare their Q4 trajectory to treated users. The counterfactual trajectory for the treated group is estimated by the control group's trend.
- **Synthetic control** (#7): if no clean holdout exists, construct a synthetic control from historical data and donor markets.
- **DAG-based causal attribution** (#1, #2): draw the DAG of all concurrent interventions. Identify which interventions are d-connected to retention through paths that share confounders. Adjust for those confounders to isolate each intervention's effect.

**Post-mortem output standard.**

A rigorous post-mortem states:
- The causal question explicitly: "Did feature X cause the Q4 retention improvement?"
- The identification strategy: "We use DiD with the 20% holdout cohort that did not receive the feature until Q1."
- The estimate with uncertainty: "ATT = +2.1 pp (95% CI: 0.8–3.4 pp)."
- What alternative explanations remain: "The load-time improvement happened simultaneously in both groups, so it is absorbed by the DiD design. The marketing campaign was targeted at new users and did not affect the existing-user cohort used here."

**Primitive links.** DAG (#1) → Do-calculus identifiability check (#2) → DiD (#6) or Synthetic control (#7) → Sensitivity (#12) for residual uncertainty.

---

## Anti-Pattern Catalog

### A1 — Power-User Bias: Treating Adopters as the Treatment Population

**Description.** An analyst computes the retention difference between users who used a feature at least once in the first week and users who never used it. This comparison is presented as the feature's treatment effect.

**Why it fails.** "Users who adopted the feature" is not a randomly assigned treatment group — it is a self-selected group that was already more engaged before the feature existed. This is confounding by prior engagement (a classic example of primitive #10, Simpson's Paradox and Confounding Traps). The measured gap between adopters and non-adopters reflects both the feature effect and the selection effect of who chose to adopt. The estimate is almost always upward biased: power users are more likely to adopt new features and more likely to be retained regardless of any feature.

**Concrete damage.** A feature with zero causal effect on retention will appear to have a large effect because adopters have higher baseline retention. PMs who rely on this estimate will over-invest in features that serve power users and under-invest in features that could broaden the user base.

**Fix.** Define the treatment population as all users who were exposed to the feature (either by randomization or by a well-defined eligibility criterion), not as users who chose to engage. For non-random adoption, use propensity score matching or a doubly robust estimator (primitive #8) to control for pre-adoption engagement signals. Report the intent-to-treat (ITT) estimate alongside the effect on adopters.

---

### A2 — Conditioning on Retention When Measuring Retention (Collider)

**Description.** An analysis of "what drives long-term retention" restricts the analysis sample to users who are still active at day 30 and then measures correlates of their day 90 retention. Or: a feature's impact on engagement is measured only in the cohort of users who were retained past the initial churn risk window.

**Why it fails.** "Still active at day 30" is a collider: it is a common effect of both (a) the feature's impact and (b) baseline user quality. Conditioning on a collider opens a spurious association between all of its causes (primitive #3 and the collider discussion in primitive #10). In this case, conditioning on day-30 retention creates a spurious negative correlation between feature usage and day-90 retention because the only users who are retained at day 30 without using the feature are those who had very high baseline quality — a selected group that outperforms even feature users at day 90.

**Concrete damage.** This pattern routinely produces the finding "feature X is negatively correlated with day-90 retention in retained users" when the feature has a positive causal effect on population-level retention. It causes abandonment of genuinely valuable features.

**Fix.** Never restrict the analysis sample to users who survived the outcome window you are measuring. The analysis population must be defined at a point prior to the outcome of interest. Use the DAG (primitive #1) to identify all variables that are downstream of the treatment or mediators on the causal path, and do not condition on them.

---

### A3 — Calling Correlated Metric Uplift "Caused by" the Launch

**Description.** After a feature launch, several product metrics improve: activation rate, session length, feature discovery, and 14-day retention. The launch review concludes "the feature improved all four metrics."

**Why it fails.** Correlated metric improvements after a launch can arise from: (a) the feature actually causing all four metrics, (b) the feature causing one metric, and the others being downstream effects of the same mechanism, (c) a concurrent intervention causing all four, or (d) regression to the mean if the launch followed a bad period. Without an identification strategy for each metric, the causal claim is not justified. Specifically, metrics that are downstream of each other in the causal graph should not both be claimed as direct effects of the feature — that double-counts the causal impact.

**Concrete damage.** If the launch review credits the feature with 4 metric improvements that are actually 1 root improvement and 3 downstream consequences, the PM has inflated the feature's impact. Future bets will be calibrated against an inflated baseline.

**Fix.** Draw the DAG for the metric tree (primitive #1). Identify which metrics are on causal paths downstream of others. Report the effect on the most upstream metric as the direct effect, and decompose the downstream metric improvements via mediation analysis (primitive #11) to quantify what fraction flows through the upstream metric versus independently.

---

### A4 — Ignoring Novelty Effects (Treatment Effect That Decays)

**Description.** A new UI pattern, notification type, or content feed algorithm is tested for 2 weeks. It shows a significant engagement lift. The PM ships it based on the 2-week result.

**Why it fails.** Novelty effects produce transient engagement lifts that decay to baseline or below baseline after the novelty wears off (typically 4–8 weeks for UI changes, longer for algorithm changes that reshuffle content). An effect estimated in the first 2 weeks of a test conflates the causal effect of the feature with the transient novelty response. Shipping based on a novelty-inflated estimate produces a feature that appears to hurt metrics in the weeks after launch, creating confusion and eroding trust in the experimentation system.

**Concrete damage.** Over-attribution of causal effects to novelty-driven features leads to an intervention backlog full of changes that degrade at steady state. Each shipped novelty adds complexity with no durable benefit.

**Fix.** Segment the test result by user exposure cohort date. Compare the treatment effect for users who first saw the variant in week 1 vs. week 3. If the effect is significantly larger for week-1 users, novelty contamination is present. Extend the test until the cohort effects stabilize — typically at least 4 weeks for UI-heavy changes. Report the week-3-onward cohort effect as the durable estimate. This is a form of sensitivity analysis (primitive #12): how much of the observed effect disappears when the novelty cohort is excluded?

---

### A5 — Attributing Churn Drop to a Feature Without a Parallel-Trends Control

**Description.** A retention or churn metric improves in the 30 days following a retention feature launch (re-engagement emails, in-app nudges, session-restart prompts). The PM attributes the improvement to the feature.

**Why it fails.** Retention metrics are seasonal, macro-sensitive, and influenced by concurrent changes across the product and marketing stack. Without a control group that experienced everything except the feature, the pre/post comparison is unidentified. The DiD identification assumption — parallel trends — is not tested and may be violated. This is the pre/post fallacy at the product level (related to primitive #6).

**Concrete damage.** If the churn improvement was driven by a seasonal pattern, a marketing push, or a bug fix rather than the retention feature, the PM will continue investing in an ineffective intervention. The false-positive attribution also suppresses willingness to test alternatives.

**Fix.** Run retention feature tests with an explicit holdout group whenever possible — a small percentage of eligible users who do not receive the re-engagement nudge or retention email. If a holdout is not possible, use a geographic or plan-tier split to create a control group. Apply DiD (primitive #6), verify parallel trends in pre-launch data, and report the ATT rather than the raw pre/post change. If parallel trends fails, use synthetic control (primitive #7) to construct the counterfactual retention trajectory.

---

## Recipes

### R1 — Feature Impact Under Non-Random Adoption

**Goal.** Estimate the causal effect of a feature on a target metric (activation, retention, revenue per user) when adoption was organic, not randomized.

**When to use.** The feature shipped to all eligible users at once (or in a phased rollout with no formal holdout), and engagement with the feature was voluntary. Statsig or Eppo cannot provide a clean experiment result.

**Stack.**

**Step 1: Draw the DAG** (primitive #1, see [01-dag-scm.md](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md)).

Identify:
- Treatment: feature adoption (binary or continuous engagement score)
- Outcome: target metric (e.g., 30-day retention)
- Confounders: variables that predict both adoption and the outcome, measured before adoption. Common candidates: user tenure, pre-adoption engagement score, plan tier, acquisition channel, number of prior features adopted, team size (for B2B).
- Mediators: variables causally downstream of adoption and upstream of the outcome. Do not include in the adjustment set — conditioning on mediators blocks the causal path.
- Colliders: downstream effects of adoption. Never condition on these.

**Step 2: Model the propensity score** (primitive #8, see [08-propensity-score.md](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md)).

```python
# Fit a logistic regression or gradient-boosted classifier on pre-adoption features
# Target: adopted_feature (0/1)
# Covariates: user_tenure_days, pre_adoption_events_7d, plan_tier, channel, ...

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Use cross-fitted propensity scores to avoid overfitting
propensity_model = GradientBoostingClassifier(n_estimators=100, max_depth=3)
# Fit on train fold, predict on holdout fold; concatenate predictions

# Check overlap: propensity score distributions for treated and control
# Flag: if any propensity scores are < 0.02 or > 0.98, overlap is poor
# Action: trim or clip extreme weights; reconsider scope
```

**Step 3: Apply a doubly robust (DR/AIPW) estimator.**

The DR estimator is consistent if either the propensity model or the outcome model is correctly specified — a critical hedge in noisy product data.

```python
# Using EconML or CausalML
from econml.dr import LinearDRLearner

dr_model = LinearDRLearner(model_propensity=propensity_model,
                            model_regression=outcome_model)
dr_model.fit(Y, T, X=covariates)
ate = dr_model.ate(covariates)
ate_interval = dr_model.ate_interval(covariates, alpha=0.05)
```

**Step 4: Estimate CATE for key segments** (primitive #9, see [09-cate-uplift.md](../../foundations-causal-inference/assets/templates/causal-inference/09-cate-uplift.md)).

Segment by acquisition channel, platform, plan tier, and user tenure bucket. Use the X-learner or DR-learner depending on sample size per segment. Flag any segment where the treatment effect estimate has the opposite sign from the ATE — these require investigation before a global ship decision.

**Step 5: Compute the E-value** (primitive #12, see [12-sensitivity-analysis.md](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md)).

```python
import numpy as np

def e_value(rr):
    """E-value for a risk ratio estimate."""
    if rr < 1:
        rr = 1 / rr  # convert to > 1 scale
    return rr + np.sqrt(rr * (rr - 1))

rr_ate = 1 + ate  # approximate for small effects
print(f"E-value: {e_value(rr_ate):.2f}")
# Report: "An unobserved confounder would need effect size ≥ {e_value} on
# both margins to explain away this result."
```

**Decision gate.** Ship only if: (a) ATE is positive and the CI excludes zero, (b) no major subgroup has a negative CATE, (c) the E-value exceeds the threshold for a plausible confounder (use domain knowledge to set the threshold), and (d) the propensity model has acceptable overlap.

---

### R2 — Funnel-Stage Mediation: Find the Activation Bottleneck

**Goal.** Decompose the total effect of an onboarding redesign on 30-day retention into contributions from each funnel stage. Identify which stage is the primary mediator and which is the bottleneck.

**When to use.** An onboarding A/B test (or a pre/post rollout with a DiD design) shows a positive total effect on retention. The team wants to know which stage to invest in next.

**Stack.**

**Step 1: Map the activation DAG** (primitive #1).

Typical B2C/B2B SaaS onboarding chain:
```
Treatment (new onboarding) → Step A (profile complete)
                           → Step B (aha-moment action, e.g., first export or first share)
                           → Step C (collaboration invite sent)
                           → Outcome (30-day retention)

Additional DAG edges:
  User intent → Step A (confounders)
  User intent → Step B
  User intent → Outcome
  Step A → Step B (sequential dependency)
  Step B → Step C
```

**Step 2: Identify the adjustment set for each mediator path** (primitive #3, see [03-backdoor-frontdoor.md](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md)).

For each mediator M_i in {Step A, Step B, Step C}, identify the minimal sufficient adjustment set for the M_i → Outcome relationship. Include only pre-treatment confounders. Exclude downstream variables (which are themselves potential mediators or colliders).

**Step 3: Estimate the total effect and mediated effects** (primitive #11, see [11-mediation-analysis.md](../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md)).

```python
# Sequential mediation with product of coefficients (linear approximation)
# For binary or continuous outcomes, use the potential outcomes framework

# Total Effect (TE): from the A/B test result or DiD estimate
te = 0.042  # 4.2 pp retention lift (example)

# Indirect Effect via Step B (aha-moment):
# IE_B = effect of treatment on Step B completion × effect of Step B on retention
# Estimated from the mediation decomposition (use the mediation package or EconML)

# Proportion mediated by Step B = NIE_B / TE
# If proportion > 0.5: Step B is the primary bottleneck
```

**Step 4: Identify the bottleneck.**

```
Rank mediators by proportion of total effect mediated:
  1. Step B (aha-moment): 61% of TE mediated
  2. Step C (invite sent): 22% of TE mediated
  3. Step A (profile): 9% of TE mediated
  4. Direct effect (other paths): 8%

→ Next experiment: invest in improving Step B completion rate
```

**Step 5: Sensitivity check on the NIE** (primitive #12).

Report the E-value for the NIE of the primary mediator. If the E-value for the "aha-moment drives retention" indirect effect is low (< 1.5), the finding is fragile and should not drive a major investment decision without further validation via an instrument or a dedicated experiment that randomizes Step B completion.

**Output artifact.** A one-page mediation summary for the product review: total effect, proportion mediated by each stage, bottleneck identification, and sensitivity bounds. Feeds directly into the [assets/ops/a3-debrief.md](../assets/ops/a3-debrief.md) debrief format.

---

### R3 — Regional Rollout Retention Analysis

**Goal.** Estimate the causal effect of a feature rolled out to one market or region on user retention, without a clean experimental holdout. Detect novelty effects that would contaminate the estimate if unaddressed.

**When to use.** A feature shipped to one country, one platform, or one product tier before expanding. No formal A/B test was run. The team needs a causal retention estimate before deciding on global rollout.

**Stack.**

**Step 1: Define the treated unit and donor pool** (primitive #7, see [07-synthetic-control.md](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md)).

Treated unit: the region/market that received the feature.
Donor pool: other regions/markets that are comparable on pre-rollout retention trajectory, user mix, and seasonal patterns. Minimum recommendation: 5 donor units with at least 12 weeks of pre-rollout data.

Exclude donors that experienced a correlated shock during the post-rollout window (e.g., a localized competitor entry or regulatory change).

**Step 2: Construct the synthetic control.**

```python
# Using pysyncon or the synth_control function in custom analytics
# Minimize pre-rollout RMSPE (root mean squared prediction error)
# on the pre-rollout retention curve

# Weights are non-negative and sum to 1
# The synthetic control is the weighted average of donor retention curves
# that best matches the treated region's pre-rollout curve
```

Fit quality check: the synthetic control should explain ≥ 85% of the pre-rollout variance in the treated unit's retention. If not, the donor pool is not comparable and the synthetic control estimate is unreliable.

**Step 3: Estimate the treatment effect and run permutation inference.**

```
Effect in week t = Actual retention_treated(t) - Synthetic control retention(t)

Permutation test:
  For each donor unit d:
    Construct a synthetic control for d using all other donors + treated unit
    Compute the placebo effect in the post-rollout window

  p-value = fraction of donor placebo effects that exceed the treated unit's effect
  Threshold: p < 0.10 for exploratory rollout decisions; p < 0.05 for investment decisions
```

**Step 4: Novelty-decay check at +30, +60, +90 days.**

Split the post-rollout window into three 30-day periods. Plot the synthetic control residual (actual − synthetic) over time:

```
+1 to +30 days:  effect = X.X pp  (potentially novelty-inflated)
+31 to +60 days: effect = Y.Y pp  (novelty-decay period)
+61 to +90 days: effect = Z.Z pp  (steady-state estimate)

If Z.Z < 0.5 × X.X: significant novelty decay; use Z.Z as the rollout estimate
If Z.Z ≈ X.X: stable effect; use the full post-period average
```

The steady-state (+61 to +90 day) estimate is the one that should drive the global rollout decision. Novelty-inflated estimates from the first 30 days should be explicitly discounted in the rollout memo.

**Step 5: Sensitivity via placebo-in-time test** (primitive #12).

Apply the synthetic control algorithm to a placebo intervention date set to 8 weeks before the actual rollout. If the synthetic control shows a false positive effect at the placebo date, the donor pool or pre-rollout window is insufficient — extend the pre-rollout window or revise the donor pool before reporting.

**Output artifact.** A retention analysis memo with: synthetic control fit plot, treatment effect trajectory by 30-day window, permutation p-value, novelty-decay assessment, and a single recommended estimate for the rollout model. Anchors directly to the [assets/roadmap/outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md) "key bets" section with the retention lift and CI.

---

## Composition

The three recipes above compose naturally into a full feature lifecycle:

| Stage | Recipe / Pattern | Primitives |
|-------|-----------------|------------|
| Post-launch (organic adoption) | R1: Feature impact under non-random adoption | #1, #8, #9, #12 |
| Onboarding optimization | R2: Funnel-stage mediation | #1, #3, #8, #11, #12 |
| Regional rollout evaluation | R3: Regional rollout retention analysis | #1, #7, #6, #12 |
| Subgroup harm detection | P3: CATE analysis | #1, #8, #9, #12 |
| Board-level attribution | P6: Sensitivity analysis | #1, #12 |
| Post-mortem | P7: Counterfactual framing | #1, #2, #6, #7, #12 |

**Cross-cutting rule.** Every recipe and pattern closes with sensitivity analysis (primitive #12). This is not optional. An observational PM analysis without an E-value or tipping-point statement is not ready to present at a product review.

**Primitive coverage in this file:**

| Primitive | Where used |
|-----------|-----------|
| #1 DAGs / SCM | P1, P2, P3, P4, P5, P6, P7, R1, R2, R3 |
| #2 Do-calculus | P7 |
| #3 Backdoor / Frontdoor | P4, R2 |
| #4 Instrumental Variables | (referenced in R1 sensitivity discussion) |
| #5 RDD | P5 |
| #6 DiD | P2, P7, A5, R3 |
| #7 Synthetic Control | P2, P5, P7, A5, R3 |
| #8 Propensity Scores | P1, P3, P4, R1, R2 |
| #9 CATE / Uplift | P1, P3, R1 |
| #10 Simpson's Paradox | A1, A3 |
| #11 Mediation Analysis | P4, A3, R2 |
| #12 Sensitivity Analysis | P1, P6, R1, R2, R3, all anti-patterns |

---

## Sources

1. Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. — DAGs, do-calculus, backdoor/frontdoor criteria.
2. Imbens, G. W., & Rubin, D. B. (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*. Cambridge University Press. — Propensity scores, matching, LATE, ITT.
3. Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. — IV, RDD, DiD in applied settings.
4. Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies. *Journal of the American Statistical Association*, 105(490), 493–505. — Synthetic control foundation.
5. Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230. — Staggered DiD estimators.
6. Chernozhukov, V., et al. (2018). Double/Debiased Machine Learning for Treatment and Structural Parameters. *The Econometrics Journal*, 21(1), C1–C68. — DR-learner, DML framework.
7. Wager, S., & Athey, S. (2018). Estimation and Inference of Heterogeneous Treatment Effects Using Random Forests. *JASA*, 113(523), 1228–1242. — Causal forests, CATE estimation.
8. VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, 167(4), 268–274. — E-value derivation.
9. Imai, K., Keele, L., & Tingley, D. (2010). A General Approach to Causal Mediation Analysis. *Psychological Methods*, 15(4), 309–334. — Mediation analysis framework.
10. Kohavi, R., Tang, D., & Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*. Cambridge University Press. — SRM, CUPED, novelty effects, experiment trustworthiness at scale.
11. Larsen, N., et al. (2023). *Statistical Challenges in Online Controlled Experiments*. The American Statistician. — Novelty effects, carryover, and variance in product experimentation.
