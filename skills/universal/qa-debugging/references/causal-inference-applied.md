---
description: Causal inference patterns for root-cause analysis and post-mortems — counterfactual reasoning, DiD across services, DAG-driven blast-radius analysis, mediation on regressions, synthetic control for performance baselines, and sensitivity analysis on observational telemetry.
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

The failure these patterns prevent is **premature closure**: the symptom resolves, the team
declares a root cause, and the real cause recurs later. Estimation theory lives in the
foundation skill; this file covers when RCA needs it and how RCA gets it wrong.

## Contents

- [Proportionality: When Formal Methods Are Overkill](#proportionality-when-formal-methods-are-overkill)
- [Anti-Patterns](#anti-patterns)
- [Method Selection](#method-selection)
- [Recipe: Flaky-Test Attribution](#recipe-flaky-test-attribution)
- [Recipe: Regression or Incident Counterfactual](#recipe-regression-or-incident-counterfactual)
- [Primitives and Sources](#primitives-and-sources)

---

## Proportionality: When Formal Methods Are Overkill

Most incidents do not need DiD or synthetic control. **Default: mechanism evidence.** A
fail-before/pass-after reproduction with a targeted intervention, or direct forensic evidence
(core dump, trace, corrupt record) that rules out the alternatives, confirms a cause without
statistics.

Reach for the methods below only when:

- There is **no mechanism evidence** and the cause must be inferred from observational
  telemetry, **and**
- The attribution **matters**: a disputed cause, a repeated incident, a costly or irreversible
  rollback decision, or a post-mortem whose action items depend on which of several co-occurring
  changes was responsible.

If neither holds, apply the anti-pattern checks below as a mental checklist and label the cause
`confirmed` or `probable` per the SKILL.md evidence bar. Do not build a DiD table for a bug that
a unit test already reproduces.

## Anti-Patterns

**A1 — Conditioning on a downstream symptom (collider bias).** Filtering logs by a visible
downstream symptom ("connection pool exhausted") selects on a common effect of several possible
causes (slow query, bad timeout, traffic surge) and makes independent causes look jointly
present. Teams then fix both and cannot tell which fix mattered. *Fix:* search forward from the
suspect change through the dependency graph, using the first component to degrade as the lens,
not the loudest symptom. Symptoms on the same causal chain (A → B → C) are one piece of evidence,
not three.

**A2 — Temporal precedence as causation.** "Deploy at 14:03, errors at 14:05" shows the deploy
*could* be the cause. Cron jobs, autoscaling, and other pushes also preceded the incident. *Fix:*
for each candidate, ask the counterfactual: would the incident have occurred without it, with
everything else the same? If you cannot estimate that, the cause is a candidate.

**A3 — Ignoring confounding changes.** A parallel config push, schema migration, certificate
rotation, or scale-down in the same window affects the outcome independently. *Fix:* before
closing, enumerate every change to the affected services and their shared dependencies for a
window before onset (change log plus infrastructure event stream). Each change with an
independent path to the symptom is either adjusted for or listed as a co-cause.

**A4 — Symptom remission as verification.** A rollback or restart that resolves the symptom
also resets pools, caches, heap, and instance placement. The restart may have cleared the real
cause (a leak) while the rolled-back deploy is blamed; redeploying it later "brings the bug
back" days later when the leak re-accumulates. *Fix:* the verifying intervention changes only
the suspected variable. Write down: "the fix changed V; V has a direct path to symptom S; S
recovered when V was restored, not before." If you cannot write that, the cause is `probable`.

**A5 — First-hit-after-merge flaky attribution.** A flaky test failing right after a merge can
be the test's normal base rate. Investigating only when it fails selects on the outcome. *Fix:*
the recipe below; a PR is a suspect only if the post-merge failure rate exceeds the pre-merge
base rate by more than chance.

## Method Selection

| Situation | Default method | Switch or caveat |
|-----------|----------------|------------------|
| Change reached some services/instances/cohorts but not others at the same time | Difference-in-differences against the untouched cohort | Check pre-period parallel trends; if they diverge before the change, the cohort is not a valid control |
| Rollout was staggered across units over time | Staggered DiD (Callaway-Sant'Anna) | Standard two-way fixed-effects DiD is biased under staggered timing with heterogeneous effects |
| One affected unit, no clean twin (everything got the change, or the service is unique) | Synthetic control from a donor pool (other services, zones, or the same service's prior equivalent windows) | Pre-period fit must be within pre-period noise; validate with placebo runs on donors; temporal donors assume stationarity (check week-over-week growth, time-of-day) |
| A config or tuning layer sits between change and symptom (GitOps sync, Helm hooks, operators rewriting config on deploy) | Mediation: separate the code's direct effect from the config-mediated effect | Rolling back the code without fixing the mediated config does not fix a fully mediated regression; requires no unmeasured change between code and config |
| Conclusion rests only on observational telemetry | Sensitivity analysis on the estimate | E-value only for a genuine risk ratio (error or failure rate before/after), computed with `../../foundations-causal-inference/scripts/evalue.py`; for a continuous metric (p99 latency) use a partial-R² robustness value (sensemakr), never a made-up ratio |
| Only temporal association, no control, no baseline | None is identifiable | Label the cause "candidate, not confirmed" and state what data would confirm it |

Co-located services share infrastructure confounders (network, storage, autoscaling policy).
Pick control units that share the treated units' infrastructure, or those confounders
masquerade as the treatment effect.

## Recipe: Flaky-Test Attribution

1. **Base rate.** From CI history before the first failure under investigation, compute
   p0 = failures / runs for the test, over a window long enough to include enough failures to
   estimate it. If p0 is already non-trivial, the test was flaky before any candidate PR.
2. **Candidates.** List PRs in the window that touched the test's dependency closure: the test
   file, imports, mocks, fixtures, shared test infrastructure, CI runner images. PRs outside it
   are weak candidates regardless of timing.
3. **Test each candidate.** With k failures in n post-merge runs, compute the one-sided binomial
   P(K ≥ k | n, p0). Where run counts differ a lot between candidates or runner load varies,
   prefer a permutation test: place the merge at many random historical points and see how
   extreme the observed rate increase is.
4. **Decide.** A rate increase plus a plausible mechanism makes a PR a **probable contributor**;
   confirmation still requires the SKILL.md mechanism evidence bar. Account for uncertainty in
   the estimated base rate and multiple candidate comparisons. If none shows an increase, report
   no demonstrated change from baseline; that does not prove the PR has no effect. Route to the
   test's owner with the measured rates.

## Recipe: Regression or Incident Counterfactual

1. **Draw the change graph.** Outcome metric as the sink; every change in the window as a node;
   edges for plausible causal paths; mark mediators (config between code and metric) and shared
   confounders (autoscaling, traffic mix).
2. **Estimate the counterfactual** with the method from the selection table: DiD if a control
   cohort exists, synthetic control if not.
3. **Decompose** through any mediator before choosing the fix.
4. **Stress the estimate** with the sensitivity check matching the metric type, against the
   specific co-occurring changes enumerated in step 1.
5. **Trace the causal path edge by edge** (change → first-order effect → ... → SLO breach), each
   edge backed by a telemetry signal. The first broken edge is the root cause; the last is only
   the visible symptom.
6. **Check the fix** targets the node on the confirmed path, not a downstream symptom.

Post-mortem output: counterfactual chart (observed vs estimated baseline), the effect estimate
with uncertainty, the causal path with evidence per edge, the sensitivity result, and which node
the fix changes.

## Primitives and Sources

Estimation procedures and assumption checklists live in
[`foundations-causal-inference`](../../foundations-causal-inference/SKILL.md):
[DAG/SCM](../../foundations-causal-inference/assets/templates/causal-inference/01-dag-scm.md),
[backdoor/frontdoor](../../foundations-causal-inference/assets/templates/causal-inference/03-backdoor-frontdoor.md),
[difference-in-differences](../../foundations-causal-inference/assets/templates/causal-inference/06-diff-in-diff.md),
[synthetic control](../../foundations-causal-inference/assets/templates/causal-inference/07-synthetic-control.md),
[propensity scores](../../foundations-causal-inference/assets/templates/causal-inference/08-propensity-score.md),
[mediation](../../foundations-causal-inference/assets/templates/causal-inference/11-mediation-analysis.md),
[sensitivity analysis](../../foundations-causal-inference/assets/templates/causal-inference/12-sensitivity-analysis.md).

- Pearl, J. (2009). *Causality* (2nd ed.). Cambridge University Press. DAGs, counterfactuals, collider bias.
- VanderWeele, T. J., & Ding, P. (2017). Sensitivity Analysis in Observational Research: Introducing the E-Value. *Annals of Internal Medicine*, 167(4), 268–274.
- Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230.
- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic Control Methods for Comparative Case Studies. *JASA*, 105(490), 493–505.
- VanderWeele, T. J. (2015). *Explanation in Causal Inference: Methods for Mediation and Interaction*. Oxford University Press.
