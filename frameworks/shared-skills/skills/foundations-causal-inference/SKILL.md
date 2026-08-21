---
name: foundations-causal-inference
description: Causal-inference primitives: DAGs, IV, RDD, DiD, synthetic control, propensity, CATE, interference. Use when attributing confounded impact or rollout and LLM-eval confounding.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Causal Inference Foundations


12 applied causal inference primitives for impact attribution and experiment design, backed by a formal theory map. Each primitive solves a specific identification or estimation problem. Primitives are domain-agnostic: the same instrumental-variable logic that handles omitted-variable bias in econometrics handles it in product analytics; the same difference-in-differences framework that evaluates policy interventions evaluates feature rollouts.

## When to Apply

**Apply causal-inference when:**
- "Did the change cause the outcome, or just correlate?" question
- A/B test is impossible (rollout already happened, ethics, ramping risk) — observational methods needed
- Confounding suspected — non-random treatment assignment
- Heterogeneous treatment effects matter (CATE, uplift)
- Mediation question — "is the effect through path X or path Y?"
- Units interfere — marketplace, social graph, shared inventory, ranking model, or agents sharing a backend resource; randomization alone does not identify the launch effect
- LLM evaluation pipeline uses logged data — prompt distribution, judge bias, or user self-selection confound the quality signal (Pearl's Ladder applies: estimating P(Y|do(prompt)) is different from P(Y|prompt))

**Skip and use simpler alternatives when:**
- Clean RCT / A/B test is already running *and* units do not interfere — read the result, don't re-derive it observationally. If units share a marketplace, graph, or backend resource, the test is not clean: see [Interference and SUTVA](#interference-and-sutva-when-randomization-is-not-enough)
- Question is "how big is the effect?" rather than "does it cause" — descriptive analytics is enough
- No plausible causal mechanism — correlation is just measurement, not insight
- Sample size too small for propensity overlap (n < 1000 typical) — flag and collect more data
- E-value < 1.5 from sensitivity analysis — claim is fragile; do not ship as causal
- Question is about strategic interaction (multi-actor) — use foundations-game-theory

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Anti-Patterns](#anti-patterns)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Interference and SUTVA](#interference-and-sutva-when-randomization-is-not-enough)
- [Expert Judgment](#expert-judgment)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Navigation](#navigation)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Use When | Core Output |
|---|-----------|----------|-------------|
| 1 | [DAGs and Structural Causal Models](#1-dags-and-structural-causal-models) | Mapping assumed data-generating process | Causal graph; identifies confounders, mediators, colliders |
| 2 | [Do-Calculus](#2-do-calculus) | Identifying causal effects from observational data | Identifiability check; expression for P(Y\|do(X)) |
| 3 | [Backdoor / Frontdoor Criterion](#3-backdoor--frontdoor-criterion) | Choosing a valid adjustment set | Minimal sufficient adjustment set |
| 4 | [Instrumental Variables](#4-instrumental-variables) | Unobserved confounders present; randomized experiment infeasible | LATE or ATE estimate |
| 5 | [Regression Discontinuity](#5-regression-discontinuity) | Treatment assigned by a threshold rule | Local ATE at the cutoff |
| 6 | [Difference-in-Differences](#6-difference-in-differences) | Pre/post data with treated and control groups | ATT under parallel trends |
| 7 | [Synthetic Control](#7-synthetic-control) | Single treated unit; no clean control group | Counterfactual trajectory for the treated unit |
| 8 | [Propensity Score Methods](#8-propensity-score-methods) | Observational data; balancing covariates needed | ATE or ATT via matching, IPW, or DR estimation (for continuous treatment: dose-response curve via DML) |
| 9 | [CATE / Uplift Modeling](#9-cate--uplift-modeling) | Heterogeneous treatment effects across subgroups | Individual or subgroup CATE; uplift scores |
| 10 | [Simpson's Paradox and Confounding Traps](#10-simpsons-paradox-and-confounding-traps) | Observed aggregated trend contradicts subgroup trends | Correct stratification; DAG-based decomposition |
| 11 | [Mediation Analysis](#11-mediation-analysis) | Decomposing total effect into direct + indirect paths | NDE, NIE, proportion mediated |
| 12 | [Sensitivity Analysis](#12-sensitivity-analysis) | Assessing robustness of conclusions to unobserved confounding | E-value, Rosenbaum bounds, tipping-point analysis |

---

## Primitive Index

Each primitive is summarized here, expanded in [`references/primitives-overview.md`](references/primitives-overview.md), and covered by standalone playbooks under [`assets/templates/causal-inference/`](assets/templates/causal-inference/). Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs identification assumptions, estimand distinctions, or design boundaries.

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | DAGs and Structural Causal Models | Implicit untested causal assumptions producing biased estimates |
| 2 | Do-Calculus | Treating observational P(Y\|X) as causal without identification |
| 3 | Backdoor / Frontdoor Criterion | Conditioning on the wrong variables; collider bias |
| 4 | Instrumental Variables | Omitted-variable bias when confounders are unobservable |
| 5 | Regression Discontinuity | Selection bias in threshold-based assignment |
| 6 | Difference-in-Differences | Pre-existing trends misattributed as treatment effects |
| 7 | Synthetic Control | No valid control group for single treated unit |
| 8 | Propensity Score Methods | Covariate imbalance inflating treatment effect estimates |
| 9 | CATE / Uplift Modeling | ATE masking heterogeneous subgroup effects |
| 10 | Simpson's Paradox and Confounding Traps | Aggregation reversals; conditioning on colliders |
| 11 | Mediation Analysis | Treating total effect as direct; pathway blocked by conditioning |
| 12 | Sensitivity Analysis | Conclusions that collapse under modest unobserved confounding |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Structural causal models | Need graphs, do-operator, counterfactuals, or transportability | #1, #2, #3, #10 |
| Potential outcomes | Need estimands, SUTVA, ignorability, compliance, or randomization logic | #4, #5, #6, #8, #9 |
| Identification theory | Need to know whether the causal effect is learnable from data | #2, #3, #4, #11 |
| Quasi-experimental design | Need threshold, timing, or donor-pool identification | #5, #6, #7 |
| Observational adjustment | Need propensity scores, weighting, matching, doubly robust estimation | #3, #8 |
| Heterogeneous effects | Need CATE, uplift, policy learning, or subgroup effect estimates | #9 |
| Mediation/counterfactual pathways | Need direct/indirect effects and pathway assumptions | #11 |
| Interference / experimental design | Need cluster, geo, or switchback randomization because units affect each other | All — SUTVA is a precondition |
| Robustness/sensitivity | Need unobserved-confounding bounds or tipping-point analysis | #12 |

---

## Anti-Patterns

| Anti-Pattern | Causal Diagnosis | Fix |
|-------------|-----------------|-----|
| Conditioning on a collider | Opens a spurious association path; introduces bias where none existed | Draw the DAG (#1); block conditioning on non-confounders identified by backdoor criterion (#3) |
| Using P(Y\|X) as a causal estimate without identification | Confounders in the distribution invalidate effect direction, let alone magnitude | Apply do-calculus (#2) to check identifiability before any regression |
| Parallel-trends violation in DiD | Pre-treatment trends differ; the control group is not a valid counterfactual | Test pre-trends explicitly; consider synthetic control (#7) as a drop-in replacement |
| Weak-instrument bias | IV estimate amplifies noise when the instrument is weakly correlated with treatment; collapses to OLS bias in small samples | Check first-stage F > 10; use LIML or Anderson-Rubin confidence sets (#4) |
| Propensity-score overlap failure | Extreme propensity scores (near 0 or 1) produce unstable IPW weights; effective sample collapses | Check overlap; trim or clip weights; switch to DR estimator or matching (#8) |
| Conditioning on a post-treatment variable | Blocks the causal pathway; introduces collider bias on mediator or mediator-proxy | Identify mediators in the DAG before adjusting; use mediation analysis (#11) if the path is the target |
| Averaging heterogeneous effects into one ATE | Subgroups with opposing effects cancel; action on ATE harms some users | Run CATE/uplift (#9); segment before averaging |
| Ignoring unmeasured confounding in observational studies | Effect estimate is unidentified; direction may flip under plausible confounders | Report E-value and Rosenbaum bounds (#12) alongside every observational point estimate. For IV estimates, also compute IV robustness values (Cinelli & Hazlett 2025, *Biometrika*) |
| Treating a marketplace or social-graph A/B test as unit-randomized | SUTVA fails: treated units change control units' outcomes, so the difference-in-means is biased even under perfect randomization | Name the interference structure before estimating. Cluster or switchback the design; estimate with a bias-aware estimator rather than difference-in-means |

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Treating correlation or prediction as causal effect | Association does not identify intervention effects | State estimand and identification strategy |
| Drawing a DAG after seeing results | Post-hoc graphs encode the desired conclusion | Draw assumptions before modeling |
| Adjusting for every available variable | Colliders and mediators can introduce bias | Use DAG/backdoor criteria |
| Reporting DiD without pre-trend diagnostics | Parallel trends is the core identifying assumption | Show pre-trends, event study, or use synthetic control |
| Using weak IVs | Weak instruments amplify bias and uncertainty | Report first-stage strength and robust intervals |
| Publishing CATE without overlap checks | Heterogeneous effects extrapolate outside support | Check positivity and subgroup sample size |
| Calling observational estimates “proven impact” | Unmeasured confounding remains possible | Report sensitivity analysis |
| Conditioning on post-treatment variables | Blocks or distorts the causal path | Separate total, direct, and mediated effects |
| Reporting a unit-level A/B result as the launch effect under interference | Unit-level and global treatment effects differ when SUTVA fails | Name the interference structure; use a cluster/geo/switchback design and say which estimand it targets |

---

## Decision Checklist

Use this to pick the right method before modeling:

- [ ] **Can you draw the assumed DAG?** If not, stop — assumptions are implicit and untestable. Draw DAG (#1) first.
- [ ] **Is the effect you want interventional (do(X)) or conditional?** If interventional, check identifiability with do-calculus (#2).
- [ ] **Can one unit's treatment change another unit's outcome?** (marketplace supply/demand, social graph, shared inventory, ranking model, geographic proximity) If yes, SUTVA fails and randomization alone does not save you — fix the *design* (cluster, geo, or switchback) before choosing an estimator. See [Interference and SUTVA](#interference-and-sutva-when-randomization-is-not-enough).
- [ ] **Do you have an RCT or clean natural experiment?** If yes, use the design directly. If no, continue.
- [ ] **Is there a threshold that determines treatment?** → RDD (#5).
- [ ] **Is there pre/post data with a comparable untreated group?** → DiD (#6). Check parallel trends first.
  - [ ] **Is treatment staggered (units adopt at different times)?** → Use Callaway–Sant'Anna, Sun–Abraham, BJS imputation, or Gardner 2-stage (see primitives-overview Primitive 6). Do NOT use plain TWFE — negative-weight bias.
  - [ ] **Is parallel trends uncertain?** → Apply HonestDiD (Rambachan & Roth 2023) for honest CIs under bounded violations.
- [ ] **Pre/post data with donor pool but parallel trends uncertain?** → Synthetic DiD (Arkhangelsky et al. 2021, #7 extension). Bridges SC and DiD.
- [ ] **Single treated unit with no clean control?** → Synthetic control (#7).
- [ ] **Are there unobserved confounders and a valid instrument?** → IV (#4). Validate exclusion restriction and check first-stage F.
- [ ] **Observational data with measured confounders only?** → Propensity score matching / IPW / DR (#8). Check overlap.
- [ ] **Do you need individual-level or subgroup effect estimates?** → CATE / uplift (#9). Choose meta-learner by sample size.
- [ ] **Does the aggregate trend contradict subgroup evidence?** → Check for Simpson's paradox via DAG stratification (#10).
- [ ] **Is the total effect mediated by an intermediate variable?** → Mediation analysis (#11). Requires no unmeasured exposure-mediator confounders.
- [ ] **Is the conclusion actionable under unobserved confounding?** → Compute E-value (#12). Report it.

---

## Composition Recipes

### Uplift from Observational Data

**Objective**: estimate individual-level treatment effects without an RCT.

**Stack**:
1. DAG (#1) — draw the assumed data-generating process; identify confounders.
2. Propensity score + doubly robust estimator (#8) — balance covariates; produce unbiased ATE. When treatment is continuous (dosage, spend, exposure level), use kernel-based DML for the average dose-response function — Colangelo & Lee (2025, JBES).
3. CATE / X-learner (#9) — estimate heterogeneous effects using the debiased residuals.
4. Sensitivity analysis (#12) — compute E-value for the strongest subgroup claim. For DML/doubly robust pipelines, additionally apply OVB bounds via Chernozhukov et al. (2026, REStat) to assess robustness of the ATE claim.

**Worked example:** 50 k users; 15 k treated by a 20%-off discount (self-selected). Propensity model (logistic, 12 covariates) yields p̂ ∈ [0.05, 0.95] for 91% of treated — overlap is acceptable; 9% trimmed. DR-ATE = +$2.40/user (SE $0.31, 95% CI [$1.79, $3.01]). X-learner surfaces a high-value segment (top quintile by LTV) with CATE = +$4.10 (SE $0.52). E-value for the overall ATE = 2.8 — an unobserved confounder would need to ~2.8× both the treatment-odds and the outcome-odds to fully nullify the estimate. Benchmark: E-value < 2 → don't ship without an RCT; E-value ≥ 3 → actionable with documented assumptions.

**When to add IV (#4)**: a valid instrument exists (e.g., randomized discount assignment, geographic variation); use it instead of propensity methods for the first-stage.

---

### Policy Evaluation with No Control Group

**Objective**: estimate the impact of a policy or feature applied to a single market or cohort.

**Stack**:
1. DAG (#1) — map treatment, outcomes, and potential confounders over time.
2. Synthetic control (#7) — construct a weighted donor pool to serve as the counterfactual.
3. DiD robustness check (#6) — apply DiD on the synthetic control residual to quantify pre-trend fit.
4. Sensitivity analysis (#12) — Rosenbaum bounds on the placebo distribution from donor permutations.

---

### Mechanism Attribution (Why Did the Effect Happen?)

**Objective**: decompose a total causal effect into direct and indirect (mediated) components.

**Stack**:
1. DAG (#1) — identify the mediator path; confirm no unmeasured exposure-mediator confounders.
2. Backdoor criterion (#3) — determine the adjustment set for total effect identification.
3. Propensity / DR estimator (#8) — produce balanced outcome estimates for mediation.
4. Mediation analysis (#11) — decompose NDE and NIE; report proportion mediated.
5. Sensitivity analysis (#12) — E-value for the indirect effect claim.

### LLM Evaluation Pipeline — Deconfounding the Quality Signal

**Objective**: estimate the causal effect of a prompt change, model update, or RLHF policy on output quality, when evaluation data are logged (non-randomised) and judge scores are potentially biased.

**Context**: LLM development pipelines generate observational logs. User prompt distribution, conversation history, judge LLM identity, and user self-selection all confound quality metrics. Simply comparing average scores before and after a model update conflates the treatment effect with distributional shift. (Reference: arxiv 2605.25998, "Causal Methods for LLM Development and Evaluation", May 2026.)

**Stack**:
1. DAG (#1) — draw: Prompt → LLM_response → Quality_score; annotate confounders (prompt difficulty, user type, judge identity) and potential colliders (filtered output).
2. Do-calculus / backdoor (#2, #3) — check whether P(Quality | do(model_update)) is identified given available logs; identify the minimal adjustment set.
3. Propensity / DR estimator (#8) — balance on prompt covariates and user context; use doubly robust ATE. For continuous interventions (e.g., RLHF reward weight), use kernel-based DML (Colangelo & Lee 2025).
4. CATE (#9) — surface heterogeneous effects by prompt category, task type, or user cohort; avoid reporting a flat ATE that masks regressions in a subgroup.
5. Sensitivity analysis (#12) — compute E-value on the key quality claim; judge-bias is a plausible unmeasured confounder — report how strong it would need to be to nullify the finding.

**Note on LLM-assisted causal discovery**: LLMs can propose DAG edges from domain knowledge but cannot replace data-driven identification checks — autoregressive next-token modeling has no mechanism for establishing direction. Use LLM outputs as priors to seed a DAG; validate edges with statistical tests (faithfulness, independence). Do not treat LLM-generated graphs as identified causal models. The restriction is on *decisional* authority, not on all LLM involvement: LLM-guided heuristic search over the structure space is a legitimate accelerator, since the search result is still validated against data. Reported LLM causal-discovery accuracy is separately confounded by memorization: the standard bnlearn benchmark graphs (Sachs, Asia, Alarm, Child) are widely published and plausibly in pretraining corpora, so benchmark scores are weak evidence of causal reasoning — prefer a graph your own domain generated. (Wu, Yu, Wu & Tan 2025, arXiv:2506.00844; contamination caveat per CausalBench, arXiv:2404.06349.)

---

## Interference and SUTVA: When Randomization Is Not Enough

Every primitive above assumes SUTVA: one unit's treatment does not affect another unit's outcome. In marketplaces, social graphs, shared-inventory systems, and ranking models this is false by construction, and a clean randomized A/B test is still biased — the control group is contaminated by the treatment. This is a *design* problem; no estimator applied afterwards recovers the estimand.

Identify the interference structure first, then pick the design:

| Interference structure | Design | Estimation note |
|---|---|---|
| Spatial or graph neighbors (social, geo, ride-hailing) | Cluster randomization on the graph's dense components | Difference-in-neighbors (Peng, Ye & Zheng 2025) attains second-order bias in interference magnitude with far lower variance than Horvitz–Thompson |
| Temporal carryover on a single shared system (pricing, matching, ranking) | Switchback: randomize treatment over time blocks | Block length must exceed the carryover order *m*; optimal design in Bojinov, Simchi-Levi & Zhao (2023, *Management Science*) |
| Both spatial and temporal (delivery, marketplace supply) | Clustered switchback (Jia, Kallus & Yu 2025) | Truncated Horvitz–Thompson; MSE matches the lower bound up to log terms on sparse graphs |
| Market-level equilibrium effects (budget, inventory, auction) | Geo or market-level randomization; unit-level tests cannot see it | Few treated units — use randomization inference, not asymptotic SEs |

**The reporting distinction that matters**: under interference, the unit-level "treatment effect" and the effect of switching *everyone* (the global/total treatment effect) are different quantities. A cluster or switchback design estimates the latter, which is usually the decision-relevant one for a launch. Say which one you estimated.

Agent and LLM products hit this directly: agents sharing a rate limit, a retrieval index, a cache, or a tool backend interfere through the shared resource, so per-session randomization understates or inverts the launch effect.

---

## Expert Judgment

What separates an expert from a checklist-follower is not knowing more formulas — it is reading the shape of the data before picking a formula, and knowing which textbook assumption is the one that actually breaks.

### Picking an Identification Strategy From Data Shape

- **One treated unit, a time series, and a pool of comparable untreated units** → synthetic control or synthetic DiD, not a hand-picked comparison unit. If pre-treatment fit is poor, say so and stop rather than force it.
- **A rule with a hard numeric cutoff and enough density of units near it** → RDD, not a linear control for the running variable. If the running variable is coarse (rounded scores, integer ages), check for heaping before trusting continuity.
- **Treatment rolled out at different times across units** → check whether never-treated or not-yet-treated units exist, then use a heterogeneity-robust staggered-DiD estimator (Callaway–Sant'Anna, Sun–Abraham, BJS, or Gardner). Plain TWFE is a bug, not a baseline, once adoption is staggered and effects can vary by cohort.
- **Confounders you can name and measure completely, with common support across treated/control** → propensity/DR. If you cannot name the confounders, no amount of covariate adjustment substitutes for a design — look for a natural experiment (IV, RDD) instead.
- **An exogenous shock or rule that shifts treatment for some units and not others, for a reason unrelated to the outcome** → IV, but only if the exclusion story survives being explained to a skeptical colleague in one sentence. If the one-sentence version needs three caveats, the instrument is probably not clean.
- **The real question is "who benefits," not "what's the average effect"** → CATE/uplift layered on top of an already-validated ATE/ATT, never as a substitute for identification. A confounded CATE just reports which subgroup has the most confounding.

### The Assumption That Actually Fails in Practice

The textbook assumption is rarely violated the way the textbook describes it. What experts actually watch for:

| Method | Textbook assumption | What breaks in real data |
|---|---|---|
| DiD | Parallel trends | Treated units were selected *because* they were already diverging (mean reversion, selection on trend) — pre-trend tests have low statistical power, so a "flat" pre-trend plot is weak evidence, not proof (Roth 2022) |
| IV | Exclusion restriction | The instrument is excludable in theory but leaks through an unmodeled common shock (e.g., a policy or cohort effect correlated with both the instrument and unobserved confounders) |
| RDD | Continuity / no manipulation | The running variable is granular (rounded, integer, self-reported) — heaping at the cutoff looks like a density blip, not manipulation, and the McCrary test at one bandwidth can miss it |
| Synthetic control | Good pre-treatment fit | Low aggregate RMSPE is achieved by 2–3 donors carrying nearly all the weight (interpolation bias) — inspect the weight vector itself, not just RMSPE |
| Propensity / DR | Strong ignorability (all confounders measured) | Treatment was assigned by a human or algorithm using private information not in X (a manager's judgment, a salesperson's read on the customer) — balance tables on measured covariates cannot detect this, and it is the single most common real-world failure |
| CATE / uplift | Same ignorability as ATE, per subgroup | Overlap can fail in exactly the subgroup with the highest estimated CATE; the "best segment" is often the one with the least support and the most confounding, not the most persuadable one |
| Mediation | No exposure-induced mediator-outcome confounder | Almost always violated when the mediator is a downstream behavior nobody randomized — default to reporting the total effect with a caveat instead of NDE/NIE unless both stages are experimental |

### Placebo and Robustness Checks an Expert Always Runs

- **Placebo-in-time**: rerun the design as if treatment happened one period earlier; expect a null effect.
- **Placebo-in-space / placebo-outcome**: rerun on units or outcomes the treatment should not affect.
- **Leave-one-out**: drop the highest-weight synthetic-control donor, or the strongest component of a composite instrument, and confirm the estimate does not collapse.
- **Specification / bandwidth curve**: show the estimate across a range of RDD bandwidths or DiD control sets, not just the one preferred specification.
- **Randomization inference**: use permutation p-values instead of asymptotic SEs when clusters or treated units are few (a handful of treated states or markets).
- **Sensitivity analysis as a routine output, not an appendix**: E-value, Rosenbaum bounds, or HonestDiD accompany every observational or DiD point estimate, not just the ones that look fragile.

### When Causal ML Adds Nothing Over a Good Quasi-Experiment

- If a credible design already exists (valid IV, sharp RDD, staggered DiD with a heterogeneity-robust estimator) and the target is a single ATE/ATT/LATE, doubly-robust ML nuisance estimation buys efficiency, not identification. The design is doing the causal work; DML is just a better nuisance-function fitter.
- Causal ML (causal forests, DML, meta-learners) earns its complexity when: (a) covariates are high-dimensional with an unknown confounding functional form, (b) the question is heterogeneity (CATE/uplift) that a single quasi-experiment cannot answer without infeasible sample size, or (c) treatment is continuous/high-cardinality with no closed-form estimator.
- It does not repair a broken identification strategy. Running `econml` on top of a DiD with violated parallel trends, or a `dowhy` refutation suite on top of an IV with a leaky exclusion restriction, produces a precise, doubly-robust, wrong answer. Fix identification before reaching for machine learning.
- **Where the literature is genuinely unsettled** (state this plainly rather than picking a side): (1) which staggered-DiD estimator (Callaway–Sant'Anna, Sun–Abraham, BJS, Gardner) to prefer is setting-dependent, not resolved — the 2026 JEL practitioner's guide (Baker, Callaway, Cunningham, Goodman-Bacon & Sant'Anna) frames the choice by design and target estimand rather than naming a winner, and the estimators can disagree meaningfully on the same panel; (2) the best-practice sensitivity-analysis default for ML-based ATEs (Chernozhukov, Cinelli et al. 2026 vs. simpler partial-R² benchmarks) is still settling in applied practice; (3) using LLMs to propose or accelerate causal discovery has no consensus validation protocol as of mid-2026 — treat LLM-proposed edges as priors to test, not conclusions to report.

---

## Workflow

1. Identify the causal question: intervention effect, mechanism, or heterogeneous effect?
2. Draw the DAG (#1). Identify confounders, mediators, and colliders.
3. Use the [Decision Checklist](#decision-checklist) to select the identification strategy.
4. Open [`references/primitives-overview.md`](references/primitives-overview.md) for inputs, assumptions, and worked conceptual examples. Its [Tooling Landscape](references/primitives-overview.md#tooling-landscape) table maps each primitive to the maintained Python/R library that implements it.
5. For multi-method stacks, use the [Composition Recipes](#composition-recipes) above.
6. Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) and always close with sensitivity analysis (#12) when reporting observational estimates.

---

## ASCII Flow

```text
Causal claim or impact question
  -> State intervention, outcome, unit, and estimand
  -> Draw DAG and mark confounders, mediators, colliders
  -> Select identification strategy
     +-- randomized evidence exists -> analyze experiment directly
     +-- observational only -> choose IV, RDD, DiD, synthetic control, or propensity design
  -> Estimate effect and run sensitivity analysis
  -> Report assumptions, effect, uncertainty, and fragility
```

---

## Related Skills

Wave 2 has landed. These consumer skills build applied-recipe layers on top of these primitives via their own `references/causal-inference-applied.md` (or domain-named equivalent) files. Each gates on this skill's [When to Apply](#when-to-apply) before invoking:

- [`../marketing-cro/references/causal-inference-applied.md`](../marketing-cro/references/causal-inference-applied.md) and [`causal-inference-experimentation.md`](../marketing-cro/references/causal-inference-experimentation.md) — CUPED, switchback and geo-experiments, CATE for personalization
- [`../marketing-product-analytics/references/causal-inference-applied.md`](../marketing-product-analytics/references/causal-inference-applied.md) and [`causal-inference-analytics.md`](../marketing-product-analytics/references/causal-inference-analytics.md) — funnel and retention attribution
- [`../marketing-paid-advertising/references/causal-inference-applied.md`](../marketing-paid-advertising/references/causal-inference-applied.md) — media-mix and geo-lift attribution
- [`../marketing-email-automation/references/causal-inference-applied.md`](../marketing-email-automation/references/causal-inference-applied.md) — send-time and lifecycle-campaign lift
- [`../data-analytics-engineering/references/causal-inference-applied.md`](../data-analytics-engineering/references/causal-inference-applied.md) — metric-layer causal contracts
- [`../product-management/references/causal-inference-applied.md`](../product-management/references/causal-inference-applied.md) — feature-rollout impact
- [`../startup-business-models/references/causal-inference-applied.md`](../startup-business-models/references/causal-inference-applied.md) — pricing and monetization lift
- [`../qa-debugging/references/causal-inference-applied.md`](../qa-debugging/references/causal-inference-applied.md) — regression root-cause attribution

New consumer domain layers should follow the same gate-then-recipe pattern rather than duplicating the primitives themselves.

---

## Navigation

- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Full primitives overview with TOC: [`references/primitives-overview.md`](references/primitives-overview.md)
- Per-primitive playbooks: [`assets/templates/causal-inference/README.md`](assets/templates/causal-inference/README.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Fact-Checking

- Pearl (2009) *Causality* is the canonical source for DAGs, do-calculus, and the backdoor/frontdoor criteria. Verify structural claims against that text.
- Imbens & Rubin (2015) *Causal Inference for Statistics, Social, and Biomedical Sciences* is the canonical source for potential-outcomes framework, IV, and matching.
- Angrist & Pischke (2009) *Mostly Harmless Econometrics* covers IV, RDD, and DiD in applied settings; use for identification assumption checks.
- Athey & Imbens (2017) machine-learning–based CATE estimation is the source for meta-learner claims; verify heterogeneous-effect benchmarks against that paper.
- Hernán & Robins *What If* (2020, freely available) is the canonical reference for time-varying treatments, IPW, and marginal structural models.
- Chernozhukov et al. (2018) on double/debiased machine learning (DML) is the source for doubly robust and Neyman-orthogonal estimator claims. For continuous treatments, the DML extension is Colangelo & Lee (2025, *Journal of Business & Economic Statistics*, doi:10.1080/07350015.2025.2505487). For omitted-variable sensitivity analysis of DML estimates, see Chernozhukov, Cinelli et al. (2026, *Review of Economics and Statistics*, doi:10.1162/REST.a.1705). Implemented in dml.sensemakr.
- Sensitivity analysis E-values: VanderWeele & Ding (2017); Rosenbaum bounds: Rosenbaum (2002) *Observational Studies*. Sensitivity analysis for IV estimates: Cinelli & Hazlett (2025, *Biometrika*, doi:10.1093/biomet/asaf004) extends the partial-R² OVB framework to handle exclusion-restriction violations and instrument confounding. Implemented in iv.sensemakr R package.
- For staggered DiD, the canonical method set (as of 2026) is: Callaway & Sant'Anna (2021, *JoE*, doi:10.1016/j.jeconom.2020.12.001); Sun & Abraham (2021, *JoE*, doi:10.1016/j.jeconom.2020.09.006); Borusyak, Jaravel & Spiess (2024, *RES*, doi:10.1093/restud/rhae011) imputation estimator; Gardner (2022, arXiv:2207.05943) two-stage DiD. Goodman-Bacon (2021, *JoE*, doi:10.1016/j.jeconom.2021.03.014) decomposition explains why plain TWFE fails. Navigational synthesis: Roth, Sant'Anna, Bilinski & Poe (2023, *JoE*, doi:10.1016/j.jeconom.2022.11.001). The current practitioner-facing reference is Baker, Callaway, Cunningham, Goodman-Bacon & Sant'Anna (2026, *JEL* 64(2), 498–557, doi:10.1257/jel.20251650) — organizes DiD designs by estimand, covariates, weights, and timing rather than prescribing one estimator.
- For parallel-trends robustness: Rambachan & Roth (2023, *RES*, doi:10.1093/restud/rhad018) HonestDiD. Pre-trend tests have low power; HonestDiD provides honest CIs under bounded violations without the binary pass/fail logic.
- For Synthetic DiD (bridging SC and DiD): Arkhangelsky et al. (2021, *AER*, doi:10.1257/aer.20190159). R package `synthdid`.
- For doubly robust DiD with covariates: Sant'Anna & Zhao (2020, *JoE*, doi:10.1016/j.jeconom.2020.06.003) DR-DiD; underpins the Callaway–Sant'Anna estimator.
- For interference and SUTVA violations: Bojinov, Simchi-Levi & Zhao (2023, *Management Science* 69(7), 3759–3777, doi:10.1287/mnsc.2022.4583) for optimal switchback design under carryover; Jia, Kallus & Yu (2025, arXiv:2312.15574) for clustered switchback under joint spatio-temporal interference; Peng, Ye & Zheng (2025, arXiv:2503.02271) for the differences-in-neighbors estimator under network interference. These are design methods — verify the assumed interference structure before citing an estimator's guarantees.
- Method effectiveness is sample-size and domain dependent. Validate identification assumptions explicitly before reporting estimates.
- Source links and verified dates in each per-primitive file are the canonical evidence tier.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
