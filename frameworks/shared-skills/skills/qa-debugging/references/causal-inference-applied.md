---
description: Causal inference patterns for root-cause analysis and post-mortems — counterfactual reasoning, DiD across services, DAG-driven blast-radius analysis, mediation on regressions, synthetic control for performance baselines, and sensitivity analysis on observational telemetry.
last_verified: 2026-05-02
status: stable
primitives:
  - foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md
  - foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md
  - foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md
  - foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md
  - foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md
  - foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md
  - foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md
---

# Causal Inference Applied — Root-Cause Analysis and Post-Mortems

> **Gate before invoking:** Check [`foundations-causal-inference` § When to Apply](../../foundations-causal-inference/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Why Causal Inference for RCA](#why-causal-inference-for-rca)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Counterfactual Reasoning in Incident Post-Mortems](#p1--counterfactual-reasoning-in-incident-post-mortems)
  - [P2 — DiD-Style Comparison Across Service Cohorts](#p2--did-style-comparison-across-service-cohorts)
  - [P3 — DAG-Driven Blast-Radius Analysis](#p3--dag-driven-blast-radius-analysis)
  - [P4 — Mediation Analysis on Performance Regressions](#p4--mediation-analysis-on-performance-regressions)
  - [P5 — Synthetic-Control Baseline for Performance Regressions](#p5--synthetic-control-baseline-for-performance-regressions)
  - [P6 — Sensitivity Analysis on Observational Telemetry](#p6--sensitivity-analysis-on-observational-telemetry)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Conditioning on a Downstream Symptom (Collider Bias)](#a1--conditioning-on-a-downstream-symptom-collider-bias)
  - [A2 — Temporal Correlation as Causation in Incident Timelines](#a2--temporal-correlation-as-causation-in-incident-timelines)
  - [A3 — Ignoring Confounding Deploys and Autoscaling Events](#a3--ignoring-confounding-deploys-and-autoscaling-events)
  - [A4 — Symptom Remission as Causal Verification](#a4--symptom-remission-as-causal-verification)
  - [A5 — First-Hit-After-Merge Attribution for Flaky Tests](#a5--first-hit-after-merge-attribution-for-flaky-tests)
- [Recipe Catalog](#recipe-catalog)
  - [R1 — Performance Regression Root-Cause](#r1--performance-regression-root-cause)
  - [R2 — Flaky-Test Attribution](#r2--flaky-test-attribution)
  - [R3 — Incident Post-Mortem Counterfactual](#r3--incident-post-mortem-counterfactual)
- [Composition Notes](#composition-notes)
- [Canonical Primitives Used](#canonical-primitives-used)
- [Sources](#sources)

---

## Why Causal Inference for RCA

Debugging and post-mortems already use causal language — "the deploy caused the spike," "the config change triggered the OOM," "the flaky test is caused by a race in the file system mock." But the reasoning is usually informal, which means it makes systematic errors: confusing correlation with causation in timelines, conditioning on downstream symptoms that open spurious attribution paths, and calling a fix verified when only a symptom went away.

Causal inference gives RCA a precise vocabulary and a set of tools that catch these errors before they close a post-mortem prematurely:

1. **DAGs** force explicit statement of which variables are causes, mediators, and colliders — so you condition on the right ones.
2. **Counterfactual framing** turns the post-mortem question ("would this have happened without X?") into a formal estimand rather than an informal guess.
3. **DiD and synthetic control** provide valid control groups when the service under investigation has no clean twin — the most common situation in incident analysis.
4. **Mediation analysis** distinguishes a direct regression-causing commit from one whose effect is entirely mediated by a downstream config that was also changed.
5. **Sensitivity analysis** quantifies how confident you should be in an RCA conclusion when telemetry is observational and cannot be replayed as an experiment.

The goal is not to add mathematical overhead to incident response. It is to prevent premature closure — the most expensive failure mode in post-mortems, where the symptom resolves, the team declares root cause, and the real cause deploys again three months later.

---

## Pattern Catalog

### P1 — Counterfactual Reasoning in Incident Post-Mortems

**Problem.** After an SLO breach, the team has a candidate cause — a deploy, a config change, a traffic spike. The question "did X cause the incident?" is being answered informally by seeing whether X preceded the incident in the timeline.

**Causal framing.** The correct question is counterfactual (Pearl's Ladder of Causation, Level 3): *P(incident = 1 | X had not occurred)*. Timeline precedence establishes association; the counterfactual question asks whether the incident would have occurred in a world where X did not happen, with everything else held constant. These are different questions and regularly produce different answers.

**Operationalization.**

1. State the candidate cause explicitly: "Deploy D at T=14:03 is the candidate."
2. Identify the counterfactual world: "In the world where D was not deployed, what would the p99 latency trajectory have looked like?" This requires a baseline — either a pre-deploy window from the same service or a comparable service that did not receive D.
3. Estimate the counterfactual baseline. If a comparable service exists, use DiD (#6 — P2 below). If the service has no clean twin, use synthetic control (#7 — P5 below). If the pre-incident window is long enough, use pre/post comparison with explicit parallel-trends check.
4. Compare the observed outcome under D to the estimated counterfactual baseline. The incident is causally attributable to D only if the observed outcome diverges from the counterfactual by more than background variance.
5. State confidence: "Under D, p99 reached 2400 ms. Our synthetic-control baseline for D-absent predicts 310 ms. The gap (2090 ms) is 8.3 SDs above the pre-incident noise floor."

**When the counterfactual is not estimable.** If the service has no pre-deploy baseline and no comparable control, the causal claim is unidentified. State this explicitly in the post-mortem: "We have strong temporal association but cannot construct a counterfactual baseline. Root cause is candidate-only, not confirmed." This is not a failure — it is accurate documentation that prevents the candidate from being treated as confirmed.

**Primitive link.** Counterfactual reasoning is Primitive #1 (DAG/SCM Level 3) and the foundation for Primitives #6 and #7. See [`01-dag-scm.md`](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md).

---

### P2 — DiD-Style Comparison Across Service Cohorts

**Problem.** A change was rolled out to a subset of services (or a feature flag was enabled on a subset of instances). Some services degraded; others did not. The team wants to know whether the change caused the degradation.

**Causal framing.** This is a natural experiment with a treatment group (services that received the change) and a control group (services that did not). Difference-in-Differences (#6) estimates the causal effect of the change under the parallel trends assumption: in the absence of the change, both groups would have had the same trajectory.

**Operationalization.**

1. Define the treatment cohort: services that received deploy D, flag F, or config C in the window [T_deploy − ε, T_deploy + ε].
2. Define the control cohort: services of the same tier, traffic profile, and dependency graph that did not receive the change.
3. Select the outcome metric: p99 latency, error rate, memory usage, or the SLO metric that triggered the incident.
4. Compute the DiD estimator:
   ```
   τ_DiD = (ȳ_treated,post − ȳ_treated,pre) − (ȳ_control,post − ȳ_control,pre)
   ```
   where pre/post is split at T_deploy.
5. Check parallel trends: plot the treated and control group metrics for [T − 2h, T_deploy]. If trends diverge before T_deploy, the control cohort is not a valid counterfactual for this metric. Fall back to synthetic control (P5) or document the limitation.
6. Test for statistical significance: use a two-sample t-test or permutation test on the DiD estimator across the service cohorts. With small cohorts (fewer than 10 services per group), prefer the permutation test.

**Practical note.** Services in the same availability zone often share infrastructure confounders (network, shared storage, autoscaling policies). Where possible, control cohort services should span the same infrastructure as treated services to avoid infrastructure-as-confounder bias.

**Primitive link.** See [`06-diff-in-diff.md`](../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md) for staggered rollout handling when the change was deployed to services at different times — standard TWFE DiD is biased in that case; use the Callaway-Sant'Anna estimator.

---

### P3 — DAG-Driven Blast-Radius Analysis

**Problem.** An incident is in progress. Multiple downstream symptoms are appearing: elevated error rates on Service A, increased queue depth on Service B, connection pool exhaustion on Service C. The team needs to determine which symptoms have a direct causal path back to the suspect change and which are downstream propagations.

**Causal framing.** Without a causal graph, every correlated symptom looks like independent evidence of the same root cause. With a DAG (#1), symptoms that are causally downstream of each other are identified as nodes on the same causal path — not as independent root-cause evidence. Conditioning on a downstream symptom when searching for the root cause is collider bias (see A1).

**Operationalization.**

1. Draw the service dependency DAG. Nodes are services/components; edges point from dependency to dependent (A → B means B depends on A, so A failing causes B symptoms).
2. Place the suspect change at the candidate root-cause node.
3. Trace all directed paths from the root-cause node. Every node reachable on a directed path is a downstream causal descendant.
4. Classify symptoms: symptoms on a direct path from the root-cause node are consistent with the hypothesis. Symptoms on a path that branches through an unrelated node are evidence of a second root cause or a confounding event.
5. Evaluate independence of symptoms: two symptoms on the same directed path (A → B → C) are not independent evidence. Do not count them as corroborating evidence separately. Two symptoms on diverging paths from the same root (A → B and A → C) are independent and do represent corroborating evidence.
6. Identify colliders: a symptom that is a common effect of two independent causes (both the suspect change and an autoscaling event) is a collider. Conditioning on it (e.g., using connection pool exhaustion as the lens for searching logs) opens a spurious association between the two causes. Do not use collider nodes as the primary search filter in log or trace queries.

**Output.** An annotated service dependency DAG with: root-cause candidate marked, all causal descendants identified, non-descendant symptomatic services flagged as "second cause or confound," and collider nodes explicitly labeled.

**Primitive link.** Backdoor criterion (#3) applies when determining which service metrics to adjust for in a regression model of incident impact. See [`03-backdoor-frontdoor.md`](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md).

---

### P4 — Mediation Analysis on Performance Regressions

**Problem.** A suspect commit is identified as a candidate cause of a latency regression. However, the commit also triggered an automated config redeployment that updated thread pool sizes. The question is whether the commit's effect on latency is direct (the code change itself is slower) or entirely mediated through the config delta (the config change is what increased latency, and the commit only caused the config change).

**Causal framing.** Mediation analysis (#11) decomposes the total effect of the commit on latency into:
- **Natural Direct Effect (NDE)**: the commit's effect on latency holding the config at its pre-commit value.
- **Natural Indirect Effect (NIE)**: the commit's effect on latency operating through the config change.
- **Total Effect (TE) = NDE + NIE**.

If NDE ≈ 0 and NIE ≈ TE, the latency regression is entirely mediated by the config change. Rolling back the commit without fixing the config will not resolve the regression. If NDE is large, the code change itself is the regression source and must be addressed in code.

**Operationalization.**

1. Identify the mediator: in the commit's causal path to latency, what intermediate variables changed? Candidates: config values, thread pool sizes, connection limits, cache parameters, JVM flags.
2. Verify the mediator is not a collider: draw the DAG. Mediator M is on the path Commit → M → Latency. Confirm there is no separate arrow from an external cause into M that would make M a collider.
3. Collect data for the four cells: (commit=0, config=pre), (commit=0, config=post), (commit=1, config=pre), (commit=1, config=post). This may require a controlled experiment or cherry-pick of the commit against both config states. If a controlled experiment is impossible, see sensitivity analysis (P6).
4. Estimate NDE and NIE:
   - NDE: deploy the commit but restore the pre-commit config. Measure latency delta.
   - NIE: deploy only the config change (without the commit). Measure latency delta.
   - Confirm NDE + NIE ≈ TE (the total observed regression).
5. Report the decomposition in the post-mortem: "The total regression is 340 ms p99. NDE = 40 ms (code path change in the serialization layer). NIE = 300 ms (thread pool size reduction triggered by the config redeployment). The fix is to restore thread pool size; the code change can be reviewed independently."

**Required assumption check.** Mediation analysis requires no unmeasured exposure-mediator confounders. In a deployment context: confirm that no other change was deployed between the commit and the config redeployment that could confound the M → Latency relationship. If another change exists in that window, flag it and apply sensitivity analysis.

**Primitive link.** See [`11-mediation-analysis.md`](../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md) for the full NDE/NIE estimation procedure and assumption checklist.

---

### P5 — Synthetic-Control Baseline for Performance Regressions

**Problem.** A single high-traffic service shows a latency regression after a deploy. There is no clean control service — all comparable services received the same deploy at the same time, or the service is unique in its traffic profile. There is no valid DiD control group.

**Causal framing.** Synthetic control (#7) constructs a counterfactual baseline for a single treated unit from a weighted combination of donor units that best matches its pre-treatment trajectory. Here, the "treated unit" is the regressed service, and the "donor pool" is a set of other services or time windows that were not affected by the change.

**Operationalization.**

1. Define the outcome metric and the treatment window: p99 latency, 30-minute pre-deploy window for pre-period, 30-minute post-deploy window for post-period.
2. Identify the donor pool. Options:
   - Other services on the same infrastructure that received a different deploy in this window (partial donors — weight them accordingly).
   - The same service in an equivalent traffic window from the prior 7 days (temporal donors — valid if traffic is stationary in that window).
   - Services from a different availability zone that did not receive the deploy.
3. Fit synthetic control weights: choose non-negative weights w_j that minimize mean squared error between the treated service's pre-deploy latency trajectory and the weighted average of donor trajectories. This can be done with a constrained least-squares solver or a purpose-built library (e.g., `pysynth`, `SparseSC`).
4. Validate pre-period fit: the synthetic control should match the treated service's pre-deploy trajectory within noise. If RMSE in the pre-period exceeds 2× the noise floor, the donor pool is not valid. Add donors or shorten the pre-period.
5. Compute the treatment effect estimate: for each post-deploy minute t, the regression magnitude is `y_treated(t) − ŷ_synthetic(t)`.
6. Inference via placebo tests: apply the same synthetic control algorithm to each donor unit (as if it were treated). The treated service's post-deploy gap should be an outlier in the distribution of placebo gaps. If it is not, the regression is within the noise of normal service variation and the deploy is not the causal source.

**Production note.** Temporal donors (same service, prior window) are convenient but fragile: they assume the service is stationary across the two windows. Always check for week-over-week traffic growth, time-of-day effects, or background infrastructure changes that would invalidate the stationarity assumption.

**Primitive link.** See [`07-synthetic-control.md`](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md) for weight-fitting procedure and permutation inference.

---

### P6 — Sensitivity Analysis on Observational Telemetry

**Problem.** The only data available for RCA is production telemetry — logs, metrics, traces — collected without experimental control. The team cannot replay the incident with and without the suspect change. Any RCA conclusion based on this observational data is potentially confounded by unobserved events (e.g., a database autovacuum, a CDN config push, a third-party API degradation that was not captured in internal metrics).

**Causal framing.** Sensitivity analysis (#12) quantifies how strong an unobserved confounder would need to be to explain away the observed association. It converts the question "is our RCA conclusion robust?" into a concrete number: the E-value, or the minimum confounder strength required to reduce the estimated effect to zero.

**Operationalization.**

1. State the observed association explicitly: "Services that received deploy D had a 4.2× higher error rate than those that did not, in the 30 minutes after deployment."
2. Compute the E-value for a risk ratio of RR = 4.2:
   ```
   E-value = RR + √(RR × (RR − 1))
   = 4.2 + √(4.2 × 3.2)
   = 4.2 + √13.44
   = 4.2 + 3.67
   ≈ 7.87
   ```
   Interpretation: an unobserved confounder would need to be associated with both the deploy and the error rate by a risk ratio of at least 7.87 to fully explain away the association.
3. Assess plausibility: in the deployment window, are there known co-occurring events that could have an RR of 7.87 with error rate? Common candidates: a CDN config push (which can affect error rates by 2–3×), a database connection limit change (which can spike error rates 5–10× on affected services), or a traffic surge on a shared upstream. If the most plausible confounder has RR < 3, the E-value of 7.87 provides strong evidence that the deploy is the root cause.
4. Document the sensitivity result in the post-mortem: "The observed effect has E-value = 7.87. No known confounder in this window has an estimated association with both the deploy and the error rate above RR = 3. The RCA conclusion is robust to plausible unobserved confounding."
5. When the E-value is small (e.g., RR = 1.4, E-value ≈ 1.8): acknowledge that plausible confounders could explain the association. Classify the root cause as "candidate, not confirmed" and identify what additional telemetry or a controlled rollback would be needed to increase confidence.

**Primitive link.** See [`12-sensitivity-analysis.md`](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md) for E-value computation, Rosenbaum bounds, and tipping-point analysis.

---

## Anti-Pattern Catalog

### A1 — Conditioning on a Downstream Symptom (Collider Bias)

**Description.** During an incident, the on-call engineer filters logs or queries metrics by a visible downstream symptom — for example, using "connection pool exhausted" as the primary search filter to find the root cause. This symptom is a downstream effect of the root cause, not an independent diagnostic lens.

**Causal diagnosis.** In the service dependency DAG, a downstream symptom S is a descendant of the root cause R. Conditioning on S (using it as a filter) can open spurious associations between independent upstream causes that both contribute to S. Example: both a slow database query and a misconfigured timeout can cause connection pool exhaustion. Filtering all logs by "connection pool exhausted" causes these two independent upstream causes to appear correlated, making it look like both are always present together when only one is the true cause of this incident. This is collider bias (Primitive #3, #10).

**How it manifests in post-mortems.** The team finds both the slow database query and the misconfigured timeout in the filtered logs, treats them as joint root causes, fixes both, and cannot tell which fix actually resolved the incident. In the next incident, the real cause (whichever was not the active one) reappears.

**Fix.** Draw the service dependency DAG before filtering. Identify which symptoms are downstream of the suspect root cause. Search for the root cause by querying from the suspect change forward through the DAG, not backward from downstream symptoms. Use upstream telemetry (the first service in the causal chain to degrade) as the search lens, not the most visible downstream effect.

**Primitive anchor.** Primitive #3 (Backdoor/Frontdoor) and #10 (Collider Bias). See [`03-backdoor-frontdoor.md`](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md).

---

### A2 — Temporal Correlation as Causation in Incident Timelines

**Description.** The post-mortem timeline is constructed from events in chronological order, and the event immediately preceding the incident onset is labeled the root cause. "Deploy D happened at 14:03. Error rate spiked at 14:05. Therefore Deploy D caused the error spike."

**Causal diagnosis.** Temporal precedence is necessary but not sufficient for causation. It establishes that D could be a cause, not that D is the cause. Multiple events routinely precede an incident: a deploy, a routine autoscaling event, a cron job, a CDN config push. All precede the incident; at most one (or a combination) caused it.

**How it manifests.** The team picks the most recent deploy because it is the most salient change. A confounding autoscaling event that actually caused the degradation by changing instance counts is overlooked because "it always happens." The deploy is rolled back, which also restarts the instances, and the incident resolves — confirming the wrong root cause. Next deploy, the same autoscaling event fires without the deploy context, and the incident recurs.

**Fix.** For every candidate event in the timeline, apply the counterfactual test (P1): would the incident have occurred if this event had not happened, with everything else the same? An autoscaling event that fires on every deploy cannot be isolated without additional analysis. Use DiD (P2) to compare services that received the deploy with and without the autoscaling event, or use the DAG to check whether the autoscaling event is on the causal path from the deploy to the symptom.

**Primitive anchor.** Primitive #1 (DAG/SCM, Level 3 counterfactual).

---

### A3 — Ignoring Confounding Deploys and Autoscaling Events

**Description.** The RCA attributes the incident to a single suspect change, but the analysis does not account for other changes that happened in the same window: a parallel config push, a database schema migration that completed at the same time, a routine autoscaling scale-down triggered by lower traffic just before the incident.

**Causal diagnosis.** These co-occurring events are confounders: they are correlated with the suspect change (they happened in the same deploy window) and independently affect the outcome metric. A DiD or counterfactual analysis that does not include them in the adjustment set produces a biased estimate of the suspect change's effect (Primitive #3, backdoor criterion).

**How it manifests.** The post-mortem closes with "deploy D was the root cause." The config push that ran simultaneously on the same services is not mentioned. Two weeks later, an identical config push runs without deploy D, and the same symptom reappears. The team is surprised.

**Fix.** Before closing any RCA, enumerate all changes in the window [T_incident − 2h, T_incident + 15min] for the affected services: deploys, config pushes, schema migrations, infrastructure changes, autoscaling events. Use the service's change log and the infrastructure event stream as sources. For each candidate change, apply the backdoor criterion: does it have a plausible path to the outcome metric independent of the suspect change? If yes, include it as a covariate in the DiD or note it as a co-cause in the post-mortem.

**Primitive anchor.** Primitive #3 (Backdoor criterion), Primitive #6 (DiD covariate adjustment).

---

### A4 — Symptom Remission as Causal Verification

**Description.** The team identifies a candidate root cause, applies a fix (rollback, config restore, restart), the symptom resolves, and the post-mortem is closed with "fix confirmed." The causal mechanism — why the fix worked — is not examined.

**Causal diagnosis.** Symptom remission after a fix is consistent with the fix being the correct cause, but it is not sufficient to confirm it. Alternative explanations: the incident self-resolved (traffic dropped, a dependent service recovered, a resource leak cleared after the restart that caused the restart to coincide with natural resolution). The rollback removed the suspected cause but also changed other variables (instance state, connection pools reset, caches cleared) that were the actual causes.

**How it manifests.** The fix "worked" because the restart cleared a memory leak that was the actual root cause. The rolled-back deploy is re-deployed three days later; the memory leak accumulates again; the incident recurs. The team is confused because "we already fixed this."

**Fix.** After a fix, verify the causal mechanism, not just the symptom. The causal mechanism test: does the fix change the variable that is causally upstream of the symptom in the DAG? A restart changes too many variables to be a reliable causal test. A targeted fix that changes only the suspected causal variable is a stronger test. Document: "The fix modified variable V. V has a direct edge to the symptom S in our service DAG. After the fix, V returned to its pre-incident value. The symptom resolved concurrent with V's restoration, not before it." If this documentation cannot be written, the root cause is still a candidate.

**Primitive anchor.** Primitive #1 (DAG/SCM), Primitive #2 (do-calculus: the fix is a surgical do-operation on the candidate variable).

---

### A5 — First-Hit-After-Merge Attribution for Flaky Tests

**Description.** A flaky test starts failing. The team looks at the merge timeline and attributes the flakiness to the most recent PR that touched the test file or its dependencies. "PR #4421 merged at 09:17. The test started failing at 09:22. PR #4421 is the cause."

**Causal diagnosis.** Flaky tests fail non-deterministically — that is the definition of flakiness. A non-deterministic failure immediately after a merge could be coincidence at the base rate of the test's flakiness. Without knowing the test's background failure rate, the temporal association cannot be evaluated. This is the observational equivalent of selecting on the outcome: the team only investigates PR timing when the test fails, which creates survivorship bias in the attribution. (Primitive #8: propensity score framing — what is the probability this PR would produce a flaky failure, compared to base rate?)

**How it manifests.** The team reverts PR #4421. The test continues to fail at the same rate. The actual cause was a non-deterministic race condition in the file system mock that was present before PR #4421 and has a natural 8% failure rate on CI runners with high load. PR #4421 was a false positive.

**Fix.** For flaky-test attribution, establish the background failure rate before the merge window (Recipe R2 provides the full procedure). The PR is a candidate cause only if the failure rate in the window [merge, merge + N runs] is statistically higher than the background rate. Use a one-sided binomial test: given background rate p_0 and k failures in n post-merge runs, compute P(K ≥ k | p_0). If p-value > 0.05, temporal association does not exceed chance and the PR is not confirmed as the cause.

**Primitive anchor.** Primitive #8 (Propensity Score), Primitive #12 (Sensitivity Analysis — the background rate is the null hypothesis).

---

## Recipe Catalog

### R1 — Performance Regression Root-Cause

**When to use.** A service's latency or error rate has degraded. There is a suspect commit or deploy. The team needs to confirm the cause, identify whether the effect is direct or mediated, and verify the fix targets the right mechanism.

**Steps.**

**Step 1: Draw the DAG of suspect changes.**
- List all changes in the window [T_regression_start − 2h, T_regression_start + 15min]: commits, deploys, config changes, infrastructure events.
- Draw a DAG with the regression metric (e.g., p99 latency) as the outcome node.
- Place each change as a node. Draw edges for direct causal paths (e.g., commit → binary → latency; deploy → config update → thread pool → latency).
- Identify mediators (intermediate variables on the causal path) and confounders (variables that affect both a change and the latency metric independently).

**Step 2: DiD across affected vs. unaffected services (Primitive #6).**
- Identify the treatment cohort: services that received the deploy.
- Identify the control cohort: services of the same tier and traffic class that did not receive the deploy in this window.
- Compute τ_DiD = (ȳ_treated,post − ȳ_treated,pre) − (ȳ_control,post − ȳ_control,pre) on p99 latency.
- Check parallel pre-trends. If parallel trends fail, note the limitation and continue to Step 3.

**Step 3: Mediation through identified config delta (Primitive #11).**
- If the DAG identified a config change as a mediator, decompose:
  - NDE: estimated latency change with the commit present but config restored to pre-deploy value. (Requires a controlled test deploy or a cherry-pick against both config states.)
  - NIE: estimated latency change from the config change alone (deploy the config change without the commit).
- If NDE is small relative to TE, the fix is in the config; the commit review can proceed at normal pace.
- If NDE is large, the code change itself is the regression source.

**Step 4: Sensitivity check on observational telemetry (Primitive #12).**
- Compute the E-value for the DiD effect size: `E-value = RR + √(RR × (RR − 1))` where RR is the ratio of post/pre change in the treated cohort relative to the control cohort.
- Enumerate plausible confounders in the window (see A3). For each, estimate its association strength with the deploy event and with latency. If all plausible confounders have strength < E-value, the RCA conclusion is robust.
- Document: "E-value = X. Most plausible confounder: Y with estimated RR = Z (< E-value). Root cause confirmed."

**Output.** Post-mortem section: DAG diagram, DiD table, NDE/NIE decomposition, E-value, and fix recommendation targeting the correct causal variable.

**Verify: fix resolves the correct DAG variable.** Before closing, confirm the fix modifies the variable identified as causally upstream of the latency metric in the DAG, not a downstream symptom.

---

### R2 — Flaky-Test Attribution

**When to use.** A test is failing intermittently after a set of recent PRs. The team needs to determine which PR (if any) caused the flakiness, or whether the flakiness is a pre-existing background failure rate.

**Steps.**

**Step 1: Establish the background failure rate.**
- Pull CI run history for the test for the 14 days before the first failure under investigation.
- Compute p_0 = (historical failure count) / (historical run count).
- If p_0 > 0.02 (2% base flakiness), the test is pre-existing flaky. Tag it as such. Any PR attribution requires demonstrating an elevated rate above p_0, not above zero.

**Step 2: Propensity model for which PRs touched suspect file paths (Primitive #8).**
- Define "treatment": a PR that modified files in the dependency graph of the failing test.
- For each PR in the analysis window, score its propensity for being treatment-adjacent: did it touch the test file, its imports, its mocks, its fixtures, or any shared test infrastructure?
- Compute propensity scores. PRs with high propensity are more likely to be causal if the failure rate is elevated; PRs with low propensity (they changed unrelated services) are less likely.

**Step 3: IPW estimate of failure rate per PR (Primitive #8).**
- For each high-propensity PR, collect the n post-merge CI runs for the flaky test.
- Compute k = failures in those n runs.
- Compute the inverse-probability-weighted failure rate estimate: this adjusts for the fact that high-traffic PRs get more runs and thus more failure opportunities.
- Rank PRs by IPW-adjusted failure rate. The top-ranked PR is the primary suspect.

**Step 4: Permutation null.**
- For each candidate PR, compute a test statistic: IPW failure rate in post-merge window vs. pre-merge background rate.
- Generate a permutation null distribution: randomly assign the merge event to 1000 other times in the CI history and recompute the test statistic each time.
- The p-value is the fraction of permuted statistics as extreme as or more extreme than the observed statistic.
- If p < 0.05: the PR is the confirmed contributor to elevated flakiness.
- If p > 0.05 for all PRs: the flakiness predates all candidates; label as pre-existing and escalate to the test infrastructure team.

**Output.** Ranked list of candidate PRs with IPW failure rate estimates and permutation p-values. For the confirmed PR: identification of the specific file path or test fixture that changed, and a targeted fix recommendation.

---

### R3 — Incident Post-Mortem Counterfactual

**When to use.** Writing or reviewing a post-mortem after an SLO breach. The team has a candidate root cause and needs to document the causal evidence formally rather than relying on timeline proximity.

**Steps.**

**Step 1: Synthetic control on similar services that did not deploy the change (Primitive #7).**
- Identify 3–10 donor services that: (a) are in the same service tier, (b) have similar traffic patterns, (c) did not receive the suspect deploy in the incident window.
- Fit synthetic control weights to minimize pre-incident RMSE between the affected service and the donor-weighted composite. Use a 2-hour pre-incident window for fitting.
- Validate fit: pre-incident RMSE should be < 10% of the post-incident signal amplitude. If RMSE is too high, add donors or reduce the pre-incident window.
- Compute the counterfactual trajectory: what would the affected service's metric have been in the absence of the deploy?

**Step 2: DiD on the symptom metric (Primitive #6).**
- Use the synthetic control as the control group (a single-unit comparison).
- Compute τ_DiD = (observed − synthetic_control) in the post-incident window.
- Quantify the gap: mean deviation, peak deviation, and time-to-onset (how many minutes post-deploy before the gap exceeds the noise floor).

**Step 3: Narrative of the causal path.**
- Using the DAG from P3, trace the causal path from the deploy to the SLO metric: deploy → [first-order effect: e.g., new code path in the hot loop] → [second-order effect: e.g., CPU saturation] → [third-order effect: e.g., request queuing] → p99 latency breach.
- For each edge in the causal path, identify the telemetry signal that confirmed the edge activated: "CPU utilization on affected hosts rose 18% in the 90 seconds following the deploy, consistent with the new code path being on the hot loop."
- Identify the first edge that broke: this is the primary root cause, not the final visible symptom.

**Output.** Post-mortem causal section:
1. Synthetic control chart: observed vs. counterfactual with gap annotated.
2. DiD estimate with confidence interval.
3. Causal path diagram with each edge labeled by supporting telemetry.
4. Sensitivity (E-value) for the DiD estimate.
5. Fix mapping: which DAG node does the fix target, and does it block the confirmed causal path?

---

## Composition Notes

The three recipes compose naturally into a single RCA workflow:

1. **Start with the DAG** (P3): draw the blast radius before analyzing any specific metric.
2. **Use DiD** (P2, R1 Step 2) as the primary effect-detection method when a control cohort is available.
3. **Switch to synthetic control** (P5, R3 Step 1) when no clean control cohort exists.
4. **Apply mediation** (P4, R1 Step 3) whenever the DAG shows a mediator between the suspect change and the outcome — mandatory when automated config systems (e.g., GitOps operators, Helm hooks, Argo CD sync) can intercept a deploy and change downstream config.
5. **Close with sensitivity analysis** (P6, R1 Step 4, R3 Step 2 annotation) on every observational estimate.

When timeline is the only evidence (no comparable services, no pre-deploy window, no control cohort), classify the RCA conclusion as "candidate, not confirmed" and document what data collection would be needed to confirm. Do not close the post-mortem with a confirmed root cause when the evidence is temporal association only.

---

## Canonical Primitives Used

| Primitive | Where Applied |
|-----------|--------------|
| [#1 DAGs and SCMs](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md) | Blast-radius analysis (P3); causal path narrative (R3 Step 3); counterfactual framing (P1) |
| [#3 Backdoor/Frontdoor Criterion](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md) | Collider identification (A1); confounder adjustment set (A3); DAG-based filter selection |
| [#6 Difference-in-Differences](../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md) | Service cohort comparison (P2); regression effect estimation (R1 Step 2); post-mortem DiD (R3 Step 2) |
| [#7 Synthetic Control](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md) | Performance baseline when no clean control group exists (P5); post-mortem counterfactual (R3 Step 1) |
| [#8 Propensity Score Methods](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md) | Flaky-test PR propensity scoring and IPW failure rate estimation (R2 Steps 2–3) |
| [#11 Mediation Analysis](../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md) | Decomposing commit effect from config-mediated effect (P4); NDE/NIE in regression RCA (R1 Step 3) |
| [#12 Sensitivity Analysis](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md) | E-value for observational telemetry (P6); RCA robustness check (R1 Step 4, R3 annotation) |

Full primitive library: [`foundations-causal-inference/SKILL.md`](../../foundations-causal-inference/SKILL.md).

---

## Sources

- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. DAGs, do-calculus, counterfactual reasoning, collider bias.
- Imbens, G. W., & Rubin, D. B. (2015). *Causal Inference for Statistics, Social, and Biomedical Sciences*. Cambridge University Press. Potential outcomes; propensity score; IPW.
- Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. DiD, parallel trends, identification in applied settings.
- VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, 167(4), 268–274. E-value formula and interpretation.
- Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230. Staggered DiD for services deployed at different times.
- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies. *Journal of the American Statistical Association*, 105(490), 493–505. Synthetic control weight fitting and placebo inference.
- VanderWeele, T. J. (2015). *Explanation in Causal Inference: Methods for Mediation and Interaction*. Oxford University Press. NDE/NIE decomposition and assumption inventory for mediation.
- Beyer, B., Jones, C., Petoff, J., & Murphy, R. (eds.). (2016). *Site Reliability Engineering*. O'Reilly Media. Chapter 15 (Postmortem Culture): incident documentation and blameless RCA context. Available at https://sre.google/sre-book/. Last verified 2026-05-02.
- Kim, G., Humble, J., Debois, P., & Willis, J. (2016). *The DevOps Handbook*. IT Revolution Press. Change management and deployment window analysis context.
