---
description: Full multi-method stacks, worked examples and caveats for the composition recipes summarized in SKILL.md.
status: stable
---

# Composition Recipes

Detailed stacks for the four scenarios summarized in [`../SKILL.md`](../SKILL.md#composition-recipes). Each stack composes primitives from the [Quick Reference table](../SKILL.md#quick-reference-primitives); always close with sensitivity analysis (#12).

## Uplift from Observational Data

**Objective**: estimate conditional average treatment effects without an RCT; these are not identified individual counterfactual effects.

**Stack**:
1. DAG (#1) — draw the assumed data-generating process; identify confounders.
2. Propensity score + doubly robust estimator (#8) — balance covariates; estimate the ATE under identification, overlap and nuisance-model conditions; double robustness is a consistency property, not unconditional finite-sample unbiasedness. When treatment is continuous (dosage, spend, exposure level), use kernel-based DML for the average dose-response function — Colangelo & Lee (2025, JBES).
3. CATE / X-learner (#9) — estimate conditional average effects using the selected learner’s nuisance models and pseudo-outcomes; evaluate targeting policy value on held-out data.
4. Sensitivity analysis (#12) — use outcome-scale-compatible sensitivity for the strongest subgroup claim; use an E-value only for a risk-ratio estimand or a documented justified conversion. For DML/doubly robust pipelines, additionally apply OVB bounds via Chernozhukov et al. (2026, REStat) to assess robustness of the ATE claim.

**Worked example:** 50 k users; 15 k treated by a 20%-off discount (self-selected). Propensity model (logistic, 12 covariates) yields p̂ ∈ [0.05, 0.95] for 91% of treated; 9% is trimmed. DR-ATE = +$2.40/user (SE $0.31, 95% CI [$1.79, $3.01]). X-learner surfaces a high-value segment (top quintile by LTV) with CATE = +$4.10 (SE $0.52). These dollar mean differences do not supply the risk ratio required for an E-value. Use partial-R2/OVB sensitivity against named plausible confounders, and label the post-trimming population separately from the original user population. All numbers in this example are hypothetical.

**When to add IV (#4)**: a defensible instrument exists; use an IV identification strategy and report its estimand (often LATE), rather than inserting an instrument into the propensity stage. Geographic variation alone does not establish instrument validity.

---

## Policy Evaluation with No Control Group

**Objective**: estimate the impact of a policy or feature applied to a single market or cohort.

**Stack**:
1. DAG (#1) — map treatment, outcomes, and potential confounders over time.
2. Synthetic control (#7) — construct a weighted donor pool to serve as the counterfactual. With no donors at all, fall back to ITS/BSTS and say it is the weaker design.
3. Check counterfactual fit — with donors, inspect pre-treatment fit and donor-placebo outcomes. With no donors, assess pre-policy trend and seasonality for the ITS/BSTS branch; a DiD check cannot run without a comparison series.
4. Sensitivity analysis (#12) — with donors, use donor leave-one-out, pre-fit and time-window sensitivity, with placebo/rank inference under explicitly justified exchangeability assumptions. With no donors, vary the pre-policy fitting window and time-series assumptions. Rosenbaum matched-assignment bounds do not directly apply to donor permutations.

---

## Mechanism Attribution (Why Did the Effect Happen?)

**Objective**: decompose a total causal effect into direct and indirect (mediated) components.

**Stack**:
1. DAG (#1) — identify the mediator path and potential treatment–outcome, treatment–mediator and mediator–outcome confounders.
2. Backdoor criterion (#3) — determine the adjustment set for total effect identification.
3. Identify mediation effects separately: total-effect propensity/DR estimation does not identify mediator pathways. Justify treatment and mediator exchangeability, consistency, positivity and absence of exposure-induced mediator–outcome confounding for natural effects.
4. Mediation analysis (#11) — estimate NDE and NIE only under those assumptions; report proportion mediated only when interpretable (in particular, the total effect is not near zero).
5. Sensitivity analysis (#12) — mediation-specific sensitivity for mediator-outcome confounding on the declared effect scale; an ordinary total-effect E-value is not automatically an indirect-effect sensitivity analysis.

---

## LLM Evaluation Pipeline — Deconfounding the Quality Signal

**Objective**: estimate the causal effect of a prompt change, model update, or RLHF policy on output quality, when evaluation data are logged (non-randomised) and judge scores are potentially biased.

**Context**: user prompt distribution, conversation history, judge identity and user self-selection all confound logged quality metrics; comparing average scores before and after a model update conflates the treatment effect with distributional shift (see arXiv 2605.25998, "Causal Methods for LLM Development and Evaluation", May 2026).

**Stack**:
1. DAG (#1) — draw: Prompt → LLM_response → Quality_score; annotate confounders (prompt difficulty, user type, judge identity) and potential colliders (filtered output).
2. Do-calculus / backdoor (#2, #3) — check whether P(Quality | do(model_update)) is identified given available logs; identify the minimal adjustment set.
3. Propensity / DR estimator (#8) — balance on prompt covariates and user context; use doubly robust ATE. For continuous interventions (e.g., RLHF reward weight), use kernel-based DML (Colangelo & Lee 2025).
4. If the change is a per-request *policy* (router, model selector, retrieval ranker), the estimand is policy value, not an ATE: use off-policy evaluation with logged propensities and report weight ESS ([beyond-canonical-designs](beyond-canonical-designs.md#off-policy-evaluation-from-logged-data)); timeouts or crashes that differ by version need bounds, not complete-case scores.
5. CATE (#9) — surface heterogeneous effects by prompt category, task type, or user cohort; avoid reporting a flat ATE that masks regressions in a subgroup.
6. Sensitivity analysis (#12) — choose OVB/partial-R2 or other scale-compatible sensitivity for continuous quality scores; use an E-value only if quality is modeled as a risk ratio or a justified conversion is documented. Benchmark named judge-bias confounders.

**LLM-proposed DAG edges are priors, not identified structure.** Validate them against data; published benchmark graphs (Sachs, Asia, Alarm) are plausibly memorized, so benchmark accuracy is weak evidence of causal reasoning (arXiv:2506.00844; CausalBench arXiv:2404.06349).
