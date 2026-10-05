---
name: foundations-causal-inference
description: "Tests whether changes caused a metric move without a clean A/B test: DiD, synthetic control, IV, RDD. Use when asking did a launch cause lift."
compatibility: Portable core only.
version: "1.4"
last_validated: 2026-08-14
---

# Causal Inference Foundations

## When to Apply

**Apply causal-inference when:**
- "Did the change cause the outcome, or just correlate?" question
- A/B test is impossible (rollout already happened, ethics, ramping risk) — observational methods needed
- Confounding suspected — non-random treatment assignment
- Heterogeneous treatment effects matter (CATE, uplift)
- Mediation question — "is the effect through path X or path Y?"
- Units interfere — marketplace, social graph, shared inventory, ranking model, or agents sharing a backend resource; randomization alone does not identify the launch effect
- LLM evaluation pipeline uses logged data — prompt distribution, judge bias, or user self-selection confound the quality signal (Pearl's Ladder applies: estimating P(Y|do(prompt)) is different from P(Y|prompt))
- A new router, ranker or bandit policy must be judged from logs of the old one, a short test must decide on a long-term metric, or outcomes are missing unequally by arm — see [Beyond the canonical 12](references/beyond-canonical-designs.md)

**Skip and use simpler alternatives when:**
- Clean RCT / A/B test is already running *and* units do not interfere — read the result, don't re-derive it observationally. If units share a marketplace, graph, or backend resource, the test is not clean: see [Interference and SUTVA](#interference-and-sutva-when-randomization-is-not-enough)
- Question requests an associational summary only — descriptive analytics is enough. The magnitude of a causal effect still requires identification
- No plausible causal mechanism — correlation is just measurement, not insight
- Effective sample size or treatment overlap is inadequate for the target estimand — narrow the population, change the design, or collect more data
- Sensitivity analysis shows that a substantively plausible omitted confounder could reverse the decision — qualify the claim or use a stronger design
- Question is about choosing an action under uncertainty rather than estimating an effect — use foundations-decision-theory; for test sizing and intervals, foundations-statistical-inference
- Question is about strategic interaction (multi-actor) — use foundations-game-theory

## Quick Reference: Primitives

Each primitive has a playbook under [assets/templates/causal-inference/](assets/templates/causal-inference/README.md). Use [references/formal-theory-map.md](references/formal-theory-map.md) for the theory area (SCM, potential outcomes, identification, quasi-experiments) that grounds each one.

| # | Primitive | Use When | Failure Mode It Addresses | Core Output |
|---|-----------|----------|---------------------------|-------------|
| 1 | [DAGs and Structural Causal Models](assets/templates/causal-inference/01-dag-scm.md) | Mapping assumed data-generating process | Implicit untested causal assumptions | Causal graph; confounders, mediators, colliders |
| 2 | [Do-Calculus](assets/templates/causal-inference/02-do-calculus.md) | Identifying causal effects from observational data | Treating P(Y\|X) as causal without identification | Identifiability check; expression for P(Y\|do(X)) |
| 3 | [Backdoor / Frontdoor Criterion](assets/templates/causal-inference/03-backdoor-frontdoor.md) | Choosing a valid adjustment set | Conditioning on the wrong variables; collider bias | Minimal sufficient adjustment set |
| 4 | [Instrumental Variables](assets/templates/causal-inference/04-instrumental-variables.md) | Unobserved confounders; a valid instrument exists | Omitted-variable bias | LATE for compliers |
| 5 | [Regression Discontinuity](assets/templates/causal-inference/05-rdd.md) | Treatment assigned by a threshold rule | Selection bias in threshold assignment | Local effect at the cutoff |
| 6 | [Difference-in-Differences](assets/templates/causal-inference/06-diff-in-diff.md) | Pre/post data with treated and comparison groups | Pre-existing trends misattributed as effects | ATT under parallel trends |
| 7 | [Synthetic Control (and SDiD)](assets/templates/causal-inference/07-synthetic-control.md) | One or few treated units, a donor pool | No valid single control unit | Counterfactual trajectory |
| 8 | [Propensity Score Methods](assets/templates/causal-inference/08-propensity-score.md) | Measured confounders only | Covariate imbalance | ATE/ATT via matching, IPW or DR; dose-response via DML for continuous treatment |
| 9 | [CATE / Uplift Modeling](assets/templates/causal-inference/09-cate-uplift.md) | Heterogeneous effects matter | ATE masking opposing subgroup effects | Subgroup CATE; uplift scores |
| 10 | [Simpson's Paradox and Confounding Traps](assets/templates/causal-inference/10-simpsons-paradox.md) | Aggregate trend contradicts subgroups | Aggregation reversals; collider conditioning | Correct stratification |
| 11 | [Mediation Analysis](assets/templates/causal-inference/11-mediation-analysis.md) | Decomposing direct and indirect paths | Total effect treated as direct | NDE, NIE, proportion mediated |
| 12 | [Sensitivity Analysis](assets/templates/causal-inference/12-sensitivity-analysis.md) | Robustness to unobserved confounding | Conclusions that collapse under modest hidden bias | Scale-compatible sensitivity (partial-R²/OVB, E-value for risk ratios, Rosenbaum Γ, HonestDiD) |

Designs outside these 12 — interrupted time series, off-policy evaluation, surrogate index, Manski/Lee bounds, negative controls and proximal inference — are in [references/beyond-canonical-designs.md](references/beyond-canonical-designs.md).

---

## Anti-Patterns and Misuse

| Anti-Pattern | Causal Diagnosis | Fix |
|-------------|-----------------|-----|
| Treating correlation, prediction or P(Y\|X) as a causal effect | Confounders invalidate effect direction, let alone magnitude | State the estimand; check identifiability (#2) before any regression |
| Drawing a DAG after seeing results, or adjusting for every available variable | Post-hoc graphs encode the desired conclusion; colliders and mediators add bias | Draw the DAG (#1) before modeling; use the backdoor adjustment set (#3) |
| Conditioning on a post-treatment variable | Blocks the causal path; collider bias on mediator proxies | Identify mediators in the DAG; use mediation analysis (#11) if the path is the target |
| Parallel-trends violation in DiD, or a passed pretest read as proof | Pre-trend tests have low power; the control group may not be a valid counterfactual | Report pretrends with uncertainty and bounded-trend sensitivity (HonestDiD), not a pass/fail gate; synthetic control (#7) is a different design with its own assumptions, not a drop-in repair |
| Weak instrument accepted on a first-stage F > 10 | With one instrument, a true 5% t-test needs F > 104.7; at F = 10 the valid critical value is 3.43, not 1.96 (Lee, McCrary, Moreira & Porter, *AER* 2022) | One instrument: report Anderson–Rubin intervals or tF-adjusted inference. Several instruments: report the effective F (Montiel Olea & Pflueger 2013) with weak-IV-robust (AR-type) inference; do not extend the 104.7 threshold beyond one instrument (#4) |
| Propensity-score overlap failure | Extreme propensities give unstable weights; effective sample collapses | Distinguish numerical tails from structural non-overlap; restrict and disclose the target estimand. Clipping, DR and matching do not identify absent counterfactuals (#8) |
| Averaging heterogeneous effects, or publishing CATE without overlap checks | Opposing subgroups cancel; CATE extrapolates outside support | Run CATE/uplift (#9) on an identified ATE; check positivity and subgroup N |
| Calling an observational estimate "proven impact" | Unmeasured confounding remains possible | Choose sensitivity for the effect scale: E-values for risk ratios (or explicitly justified conversions), Rosenbaum bounds for matched designs, partial-R²/OVB for continuous outcomes; for IV, IV robustness values (Cinelli & Hazlett 2025) (#12) |
| Reporting a unit-randomized marketplace or shared-backend test as the launch effect | Interference changes the identified contrast even under perfect randomization | Name the exposure mapping, assignment support and target contrast; cluster/switchback designs are options, not automatic identification of a global effect |

---

## Decision Checklist

Use this to pick the right method before modeling:

- [ ] **Can you draw the assumed DAG?** If not, stop — assumptions are implicit and untestable. Draw DAG (#1) first.
- [ ] **Is the effect you want interventional (do(X)) or conditional?** If interventional, check identifiability with do-calculus (#2).
- [ ] **Can one unit's treatment change another unit's outcome?** (marketplace supply/demand, social graph, shared inventory, ranking model, geographic proximity) If yes, specify direct, indirect, total or global estimand, exposure mapping and assignment support before choosing an estimator; redesign only when current support/assumptions do not identify the target. See [Interference and SUTVA](#interference-and-sutva-when-randomization-is-not-enough).
- [ ] **Do you have an RCT or clean natural experiment?** If yes, use the design directly. If outcomes are missing unequally by arm (attrition, timeouts), use Lee bounds ([beyond-canonical-designs](references/beyond-canonical-designs.md#partial-identification-bounds-instead-of-a-point)). If the decision metric arrives long after the test, consider a validated surrogate index. If no, continue.
- [ ] **Is there a threshold that determines treatment?** → RDD (#5). Report the robust bias-corrected interval, not the conventional one.
- [ ] **Is there pre/post data with a comparable untreated group?** → DiD (#6). Check parallel trends first.
  - [ ] **Is treatment staggered (units adopt at different times)?** → Use Callaway–Sant'Anna, Sun–Abraham, BJS imputation, or Gardner 2-stage. Use a heterogeneity-robust estimator aligned with the target ATT; dynamic effects can contaminate TWFE comparisons.
  - [ ] **Is the treatment a continuous dose?** → Continuous-treatment DiD (Callaway, Goodman-Bacon & Sant'Anna); parallel trends alone does not make comparisons across doses causal.
  - [ ] **Is parallel trends uncertain?** → Apply HonestDiD (Rambachan & Roth 2023) for honest CIs under bounded violations.
- [ ] **Pre/post data with donor pool but parallel trends uncertain?** → Synthetic DiD (Arkhangelsky et al. 2021, #7 extension).
- [ ] **Single treated unit with no clean control?** → Synthetic control (#7). **No donor units at all, only one series?** → Interrupted time series / BSTS, the weakest design here ([beyond-canonical-designs](references/beyond-canonical-designs.md#interrupted-time-series-its-and-bsts)).
- [ ] **Are there unobserved confounders and a valid instrument?** → IV (#4). Validate exclusion; use weak-IV-robust inference (AR or tF for one instrument), not an F > 10 gate.
- [ ] **Observational data with measured confounders only?** → Propensity score matching / IPW / DR (#8). Check overlap. If a known confounder is unmeasured, test with negative controls first.
- [ ] **Is the "treatment" a new decision policy evaluated on logs of the old policy?** → Off-policy evaluation; propensities must be logged ([beyond-canonical-designs](references/beyond-canonical-designs.md#off-policy-evaluation-from-logged-data)).
- [ ] **Do you need conditional average effects for covariate-defined groups?** → CATE / uplift (#9). Choose meta-learner by sample size.
- [ ] **Does the aggregate trend contradict subgroup evidence?** → Check for Simpson's paradox via DAG stratification (#10).
- [ ] **Is the total effect mediated by an intermediate variable?** → Mediation analysis (#11). Requires treatment and mediator exchangeability, consistency and positivity; natural effects also require no exposure-induced mediator–outcome confounding.
- [ ] **Is the conclusion actionable under unobserved confounding?** → Select a design- and scale-compatible sensitivity method (#12), name plausible confounders, and report it. If point identification fails, report bounds instead.
- **Before writing any number.** Verify every citation against a primary source before writing it; `data/sources.json` is the canonical citation list — do not restate it here. Never invent a coefficient, p-value, or weight; re-derive worked examples and hedge or omit what you cannot verify.

---

## Composition Recipes

Multi-method stacks for common scenarios; full stacks, worked examples and caveats are in [references/composition-recipes.md](references/composition-recipes.md).

| Recipe | Use When | Key Stack |
|---|---|---|
| Uplift from Observational Data | Conditional average effects, no RCT | DAG (#1) → propensity/DR, DML for continuous treatment (#8) → CATE/X-learner (#9) → sensitivity (#12); add IV (#4) if a valid instrument exists |
| Policy Evaluation with No Control Group | Single market/cohort, no comparison group | DAG (#1) → synthetic control with donors and donor/pre-fit checks; if no donors, ITS/BSTS with time-series sensitivity (#7, #12) |
| Mechanism Attribution | Decompose direct vs indirect (mediated) effect | DAG (#1) → backdoor adjustment (#3) → propensity/DR (#8) → mediation analysis (#11) → sensitivity (#12) |
| LLM Evaluation Pipeline | Deconfound a logged, judge-scored quality signal for a prompt/model/RLHF change | DAG (#1) → do-calculus/backdoor (#2, #3) → DR (#8), or off-policy evaluation if the change is a per-request policy → CATE (#9) → sensitivity (#12). LLM-proposed DAG edges are priors to validate, not identified structure. |

---

## Interference and SUTVA: When Randomization Is Not Enough

No-interference is part of SUTVA, which also concerns treatment versions. Many conventional unit-level formulas assume it, but DAGs/SCMs and potential-outcome models can explicitly include cross-unit causes. Interference does not make every estimand unrecoverable. Specify the exposure mapping, the direct/indirect/total/global intervention contrast, assignment probabilities and support, consistency of exposures, and remaining identification assumptions. Randomization alone does not turn a direct effect into the all-treated-versus-all-control launch effect.

**Counterexample:** independent Bernoulli(.5) assignments Z1,Z2 with Y1=3Z1+7Z2 and Y2=3Z2+7Z1 have interference. The Horvitz–Thompson direct-effect estimator averaging 2ZiYi−2(1−Zi)Yi over the two units has expectation 3 across the four equally likely assignments. The global all-treated-versus-all-control contrast is 10. Both contrasts exist; they answer different questions. Exposure-probability weighting requires positive probability for the exposures being contrasted. [Aronow & Samii (2017), design/exposure/estimand framework](https://arxiv.org/abs/1305.6156).

Identify the interference structure first, then pick the design:

| Interference structure | Design | Estimation note |
|---|---|---|
| Spatial or graph neighbors (social, geo, ride-hailing) | Cluster randomization on the graph's dense components | Difference-in-neighbors (Peng, Ye & Zheng 2025) attains second-order bias in interference magnitude with far lower variance than Horvitz–Thompson |
| Temporal carryover on a single shared system (pricing, matching, ranking) | Switchback: randomize treatment over time blocks | Align schedule and estimator with carryover order *m*. Under its horizon assumptions, [Bojinov et al., Theorem 3.7](https://arxiv.org/html/2009.00148v1) permits interior epochs of length *m* |
| Both spatial and temporal (delivery, marketplace supply) | Clustered switchback (Jia, Kallus & Yu 2025) | Truncated Horvitz–Thompson; MSE matches the lower bound up to log terms on sparse graphs |
| Market-level equilibrium effects (budget, inventory, auction) | Geo or market-level randomization; unit-level tests cannot see it | Few treated units — use randomization inference, not asymptotic SEs |

**The reporting distinction that matters**: under interference, the unit-level "treatment effect" and the effect of switching *everyone* (the global/total treatment effect) are different quantities. Cluster or switchback designs target contrasts defined by their allocation, carryover and exposure assumptions; neither automatically identifies the global rollout effect. Say which contrast was identified and justify any extrapolation.

Agent and LLM products hit this directly: agents sharing a rate limit, a retrieval index, a cache, or a tool backend interfere through the shared resource, so per-session randomization can identify a different contrast and may understate or invert the launch effect; establish this for the actual resource/exposure model.

---

## Expert Judgment

### Picking an Identification Strategy From Data Shape

- **One treated unit, a time series, and a pool of comparable untreated units** → synthetic control or synthetic DiD, not a hand-picked comparison unit. If pre-treatment fit is poor, say so and stop rather than force it.
- **A rule with a hard numeric cutoff and enough density of units near it** → RDD, not a linear control for the running variable. If the running variable is coarse (rounded scores, integer ages), check for heaping before trusting continuity.
- **Treatment rolled out at different times across units** → check whether never-treated or not-yet-treated units exist, then use a heterogeneity-robust staggered-DiD estimator (Callaway–Sant'Anna, Sun–Abraham, BJS, or Gardner). Dynamic effects can contaminate TWFE comparisons; cohort heterogeneity alone does not imply negative weights or bias for every target.
- **Confounders you can name and measure completely, with common support across treated/control** → propensity/DR. If you cannot name the confounders, no amount of covariate adjustment substitutes for a design — look for a natural experiment (IV, RDD) instead.
- **An exogenous shock or rule that shifts treatment for some units and not others, for a reason unrelated to the outcome** → IV, but only if the exclusion story survives being explained to a skeptical colleague in one sentence. If the one-sentence version needs three caveats, the instrument is probably not clean.
- **The real question is "who benefits," not "what's the average effect"** → CATE/uplift layered on top of an already-validated ATE/ATT, never as a substitute for identification. A confounded CATE just reports which subgroup has the most confounding.

### The Assumption That Actually Fails in Practice

The textbook assumption is rarely violated the way the textbook describes it. What experts actually watch for:

| Method | Textbook assumption | What breaks in real data |
|---|---|---|
| DiD | Parallel trends | Treated units were selected *because* they were already diverging (mean reversion, selection on trend) — pre-trend tests have low statistical power, so a "flat" pre-trend plot is weak evidence, not proof (Roth 2022) |
| IV | Exclusion restriction | The instrument is excludable in theory but leaks through an unmodeled common shock (e.g., a policy or cohort effect correlated with both the instrument and unobserved confounders) |
| RDD | Continuity / no manipulation | The running variable is granular (rounded, integer, self-reported) — heaping at the cutoff looks like a density blip, not manipulation, and a density test at one bandwidth can miss it |
| Synthetic control | Good pre-treatment fit | Low aggregate RMSPE is achieved by 2–3 donors carrying nearly all the weight (interpolation bias) — inspect the weight vector itself, not just RMSPE |
| Propensity / DR | Strong ignorability (all confounders measured) | Treatment was assigned by a human or algorithm using private information not in X (a manager's judgment, a salesperson's read on the customer) — balance tables on measured covariates cannot detect this, and it is the single most common real-world failure |
| CATE / uplift | Same ignorability as ATE, per subgroup | Overlap can fail in exactly the subgroup with the highest estimated CATE; the "best segment" is often the one with the least support and the most confounding, not the most persuadable one |
| Mediation | Sequential ignorability | Randomizing exposure alone does not establish mediator–outcome exchangeability. Defend mediation identification assumptions and report mediation-specific sensitivity; see [Imai et al., pp. 309–313](https://imai.fas.harvard.edu/research/files/BaronKenny.pdf) |

### Placebo and Robustness Checks an Expert Always Runs

- **Placebo-in-time**: rerun the design as if treatment happened one period earlier; expect a null effect.
- **Placebo-in-space / placebo-outcome**: rerun on units or outcomes the treatment should not affect.
- **Leave-one-out**: drop the highest-weight synthetic-control donor, or the strongest component of a composite instrument, and confirm the estimate does not collapse.
- **Specification / bandwidth curve**: show the estimate across a range of RDD bandwidths or DiD control sets, not just the one preferred specification.
- **Randomization inference**: use permutation p-values instead of asymptotic SEs when clusters or treated units are few (a handful of treated states or markets).
- **Sensitivity analysis as a routine output, not an appendix**: a scale-compatible method (partial-R²/OVB, E-value for risk ratios, Rosenbaum bounds, or HonestDiD) accompanies every observational or DiD point estimate, not just the ones that look fragile.

### When Causal ML Adds Nothing Over a Good Quasi-Experiment

- If a credible design already exists (valid IV, sharp RDD, staggered DiD with a heterogeneity-robust estimator) and the target is a single ATE/ATT/LATE, doubly-robust ML nuisance estimation buys efficiency, not identification. The design is doing the causal work; DML is just a better nuisance-function fitter.
- Causal ML (causal forests, DML, meta-learners) earns its complexity when: (a) covariates are high-dimensional with an unknown confounding functional form, (b) the question is heterogeneity (CATE/uplift) that a single quasi-experiment cannot answer without infeasible sample size, or (c) treatment is continuous/high-cardinality with no closed-form estimator.
- It does not repair a broken identification strategy. Running `econml` on top of a DiD with violated parallel trends, or a `dowhy` refutation suite on top of an IV with a leaky exclusion restriction, produces a precise, doubly-robust, wrong answer. Fix identification before reaching for machine learning.
- **Where the literature is genuinely unsettled** (state this plainly rather than picking a side): (1) which staggered-DiD estimator (Callaway–Sant'Anna, Sun–Abraham, BJS, Gardner) to prefer is setting-dependent, not resolved — the 2026 JEL practitioner's guide (Baker, Callaway, Cunningham, Goodman-Bacon & Sant'Anna) frames the choice by design and target estimand rather than naming a winner, and the estimators can disagree meaningfully on the same panel; (2) the best-practice sensitivity-analysis default for ML-based ATEs (Chernozhukov, Cinelli et al. 2026 vs. simpler partial-R² benchmarks) is still settling in applied practice; (3) using LLMs to propose or accelerate causal discovery had no consensus validation protocol in the sources reviewed for this skill — treat LLM-proposed edges as priors to test, not conclusions to report.

---

## Workflow

1. State the intervention, outcome, unit and estimand: intervention effect, mechanism, heterogeneous effect, or policy value?
2. Draw the DAG (#1). Identify confounders, mediators, and colliders.
3. Use the [Decision Checklist](#decision-checklist) to select the identification strategy.
4. Open [references/primitives-overview.md](references/primitives-overview.md) for the decision map, estimand taxonomy, assumption inventory and [Tooling Landscape](references/primitives-overview.md#tooling-landscape); open the matching template for inputs, failure modes and a worked example.
5. For multi-method stacks, use the [Composition Recipes](#composition-recipes) above.
6. Check [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) and always close with sensitivity analysis (#12) when reporting observational estimates. For risk ratios, `python3 scripts/evalue.py --rr RR --ci-low LOW --ci-high HIGH` validates the interval and uses the confidence bound closest to the null.
7. Report assumptions, effect, uncertainty and fragility; on unidentified effects report an association, bounds, or "inconclusive".

---

## Related Skills

Consumer skills keep domain adapters in `references/causal-inference-applied.md` (or a domain-named equivalent). Each gates on this skill's [When to Apply](#when-to-apply) and links back here for theory:

- `../marketing-cro/references/causal-inference-applied.md` and `causal-inference-experimentation.md` — CUPED, switchback and geo-experiments, CATE for personalization
- `../marketing-product-analytics/references/causal-inference-applied.md` and `causal-inference-analytics.md` — funnel and retention attribution
- `../marketing-paid-advertising/references/causal-inference-applied.md` — media-mix and geo-lift attribution
- `../marketing-email-automation/references/causal-inference-applied.md` — send-time and lifecycle-campaign lift
- [`../product-management/references/causal-inference-applied.md`](../product-management/references/causal-inference-applied.md) — feature-rollout impact
- `../startup-business-models/references/causal-inference-applied.md` — pricing and monetization lift
- [`../qa-debugging/references/causal-inference-applied.md`](../qa-debugging/references/causal-inference-applied.md) — regression root-cause attribution
- [`../foundations-decision-theory/references/thresholds-stopping-and-ope.md`](../foundations-decision-theory/references/thresholds-stopping-and-ope.md) — OPE estimators and acting on a policy-value estimate

---

## Navigation

- Designs beyond the 12 (ITS/BSTS, off-policy evaluation, surrogate index, bounds, negative controls/proximal) — read when the checklist lands outside the canonical primitives: [references/beyond-canonical-designs.md](references/beyond-canonical-designs.md)
- Practical completion contract and known-answer controls: [references/practical-contract.md](references/practical-contract.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Decision map, estimands, assumptions, tooling: [references/primitives-overview.md](references/primitives-overview.md)
- Per-primitive playbooks: [assets/templates/causal-inference/README.md](assets/templates/causal-inference/README.md)
- Sources: [`data/sources.json`](data/sources.json) is the citation register; verify a claim against the primary source it lists before quoting a number.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
