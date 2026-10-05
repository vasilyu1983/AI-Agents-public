# Decision Theory Applied to Incident Response

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

This file maps decision-theory primitives to on-call decisions: paging thresholds, ambiguous severity, diagnostic investment, rollback timing, runbook-step ordering, and status-page framing. It is a link adapter: theory, formulas, and generic failure modes live in the foundation. This file keeps only the incident-response mapping, domain pitfalls, and checked worked examples.

**Foundation pointers**

- Root skill: [`foundations-decision-theory/SKILL.md`](../../foundations-decision-theory/SKILL.md)
- Cost-sensitive thresholds (`c_FP/(c_FP+c_FN)`), abstention, prevalence shift, best-arm identification vs regret, expected-loss stopping: [`thresholds-stopping-and-ope.md`](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)
- Utility-compatible costs and sensitivity: [`practical-contract.md`](../../foundations-decision-theory/references/practical-contract.md)
- Exact finite EVPI/EVSI: [`finite-state-calculator.md`](../../foundations-decision-theory/references/finite-state-calculator.md)
- Primitive templates: [EU #1](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md), [Bayesian #2](../../foundations-decision-theory/assets/templates/decision-theory/02-bayesian-decision.md), [Minimax regret #3](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md), [VoI #4](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md), [Risk aversion #6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md), [Real options #7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md), [Prospect theory #8](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md), [Bandits #10](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md)

All £ figures below are **illustrative**. Replace them with your own postmortem and SLO data.

---

## Table of Contents

- [Decision Map](#decision-map)
- [P1 — Paging Thresholds Under Cost Asymmetry](#p1--paging-thresholds-under-cost-asymmetry)
- [P2 — Minimax Regret for Ambiguous Severity](#p2--minimax-regret-for-ambiguous-severity)
- [P3 — Value of Information for Mid-Incident Diagnostics](#p3--value-of-information-for-mid-incident-diagnostics)
- [P4 — Rollback as a Real Option](#p4--rollback-as-a-real-option)
- [P5 — Runbook-Step Ordering as a Bandit](#p5--runbook-step-ordering-as-a-bandit)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
- [Composition](#composition)
- [Sources](#sources)

---

## Decision Map

| Incident decision | Primitive | Where |
|---|---|---|
| Page or stay silent on an alert | Bayes threshold with cost asymmetry (#1, #2) | P1, R1 |
| SEV2 vs SEV3 when probabilities are contested | Minimax regret (#3) | P2 |
| Run a diagnostic or act on the prior | EVSI vs delay cost (#4) | P3 |
| Roll back now or wait one minute | Option to defer (#7) | P4, R2 |
| Which runbook step first | Bandit on past outcomes (#10) | P5, R3 |
| Status-page wording | Reference points, loss aversion (#8) | A4 |

---

## P1 — Paging Thresholds Under Cost Asymmetry

**Decision.** An alert fires. You page (cost `C_page` whether or not the incident is real) or stay silent (cost `C_miss` if the incident is real, 0 if not). Page when the posterior `p(real | alert) > C_page / C_miss`. This is the general Bayes threshold `c_FP/(c_FP+c_FN)` with `c_FP = C_page` and `c_FN = C_miss − C_page`. Derivation, abstention, and prevalence-shift handling: [thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md).

**Domain costs.**

- `C_page`: engineer cost per hour × triage minutes / 60 × engineers paged. Include fatigue if you can price it.
- `C_miss`: minutes of late detection × damage per minute × blast radius. Take this from postmortems of late or missed detections.
- Use the **mean** `C_miss` for a risk-neutral threshold, not the median.

**Worked example (illustrative).** Payment service: damage £10K/min, 5 minutes of expected extra detection delay if silent, so `C_miss ≈ £50K`. `C_page ≈ £40`.

```
p* = 40 / 50,000 = 0.0008   (0.08%)
```

Page when the posterior is above 0.08%. For a SEV1-class payment path, almost any credible alert should page. The threshold matters most on low-impact services, where `C_miss` is small.

**Risk aversion.** If a single large miss can cause harm beyond its expected cost (regulatory reporting, customer churn cascade), the team is risk-averse over losses. The certainty-equivalent loss of a miss is then **larger** than its expected value, so the threshold moves **lower**. Do not apply a concave utility to positive "cost" numbers. That inverts the correction. Integrate losses into terminal outcomes per [practical-contract.md](../../foundations-decision-theory/references/practical-contract.md) and [#6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md).

**Postmortem check.** After every missed or late detection, recompute `C_miss` and compare it with the value implied by the current threshold. If the observed `C_miss` is larger, lower the threshold.

---

## P2 — Minimax Regret for Ambiguous Severity

**Decision.** In the first minutes of triage, you may not be able to defend `p(SEV2+)`. Symptoms can be ambiguous: p99 is up but errors are flat, or one region is hit with unclear blast radius. When the probabilities are genuinely contested, use minimax regret ([#3](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md)).

**Illustrative payoff matrix, not measured incident costs:**

| | θ_H (actually SEV1/2) | θ_L (actually SEV3/4) |
|---|---|---|
| **Escalate** | +100 (fast mitigation) | −15 (unneeded interruption) |
| **Hold** | −80 (outage grows) | +100 (on-call handles it) |

Regret (column max minus payoff): Escalate = (0, 115), max **115**; Hold = (180, 0), max **180**. Minimax regret picks **escalate for these payoffs**. Re-estimate the plausible harm from delayed coordination and the disruption of mobilizing responders; different payoffs can change the result.

**Domain rule.** Apply the service's escalation policy and mobilize when plausible user harm from delayed coordination exceeds responder disruption. [PagerDuty's severity guidance](https://response.pagerduty.com/before/severity_levels/) uses the higher plausible severity when uncertain and asks teams to define service-specific impact criteria; that operational policy is separate from this illustrative regret calculation. Once the probabilities become defensible (for example, calibrated alert history from A3), switch back to EU.

---

## P3 — Value of Information for Mid-Incident Diagnostics

**Decision.** You can pull traces, read the slow-query log, or check an anomaly model. Each one delays mitigation. Run a diagnostic only if its **EVSI** exceeds the delay cost (delay minutes × damage per minute). If **EVPI** (the value of a perfect reveal) is already below the delay cost, skip it without further analysis. EVPI is only a ceiling. A diagnostic can have EVPI above its cost and still not be worth running. Definitions and calculator: [#4](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md), [finite-state-calculator.md](../../foundations-decision-theory/references/finite-state-calculator.md).

**When EVPI = 0.** If the runbook action is the same under every plausible cause (for example, "restart the pod regardless"), no diagnostic before that step has value.

**Worked example (rough approximation).** p99 is elevated on payments. Prior: DB bottleneck 0.6 (scale read replicas), upstream API 0.4 (flip to the fallback path). Acting on the prior costs 3 extra minutes when it is wrong. The slow-query log takes 2 minutes and identifies the cause correctly 80% of the time. Assume a wrong read falls back to the prior action.

```
EVSI ≈ 0.4 × 0.8 × 3 min × £2K/min = £1.92K     Cost = 2 min × £2K = £4K    → skip
At £10K/min: EVSI ≈ £9.6K, Cost = £20K                                       → skip
```

The damage rate cancels out. What decides it is **minutes saved in expectation (0.4 × 0.8 × 3 = 0.96 min) vs minutes spent (2 min)**. A diagnostic that takes 30 seconds, or a prior closer to 50/50 with a larger wrong-action penalty, can flip the answer. This does not justify a blanket "never diagnose before mitigating" rule.

**Runbook implication.** Move slow diagnostics whose result would not change the mitigation (EVPI ≈ 0 or below delay cost) from active triage to the postmortem section.

---

## P4 — Rollback as a Real Option

**Decision.** Metrics degrade after a deploy. You can roll back now (exercise an option that costs execution time and secondary disruption) or wait one minute (keep the option alive while uncertainty resolves). Theory: [#7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md).

**Waiting has little value when:** p(regression) is already high, damage per minute is large relative to rollback cost, or another minute of data will not change your belief.

**Waiting has value when:** metrics are noisy and the trend is unclear, rollback carries meaningful secondary disruption, or a cheaper intermediate option exists.

**Feature flags are a compound option.** Flipping the flag is the small, reversible first stage. The full rollback is the larger, less reversible second stage. Use the flag first whenever it exists.

**Three-point check before ordering rollback**

```
1. p(regression | symptoms) high (team-set cut, e.g. > 0.7)?  → go to 2
2. damage/min × minutes of waiting > rollback cost?            → go to 3
3. Will one more minute reveal anything new?                   → NO: roll back now; YES: wait one minute
```

The 0.7 and 0.3 cuts here and in R2 are team policy choices, not derived constants. Calibrate them from past deploy incidents.

---

## P5 — Runbook-Step Ordering as a Bandit

**Decision.** A recurring-incident runbook lists candidate first steps. Each step is an arm, and the reward is "resolved when tried first." Thompson sampling on Beta posteriors orders steps and still explores the less-tried ones. Mechanics: [#10](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md).

**Why a bandit fits here.** The in-incident reward (faster resolution now) matters more than an unbiased estimate of each step's rate. If you need an unbiased per-step effect estimate, for example to decide whether to delete a step, use fixed or randomised assignment, or correct the adaptive log with off-policy methods ([thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)). Naive per-arm rates from an adaptive log are biased.

**Worked example.** Kafka consumer-lag runbook, Beta(1,1) priors:

| First step | Tries | Resolved | Posterior |
|---|---|---|---|
| Restart consumer group | 22 | 16 | Beta(17, 7) |
| Scale consumer replicas | 18 | 9 | Beta(10, 10) |
| Clear dead-letter queue | 8 | 3 | Beta(4, 6) |

Monte Carlo (200K draws): P(restart is best) ≈ **0.89**, scale ≈ 0.07, DLQ ≈ 0.04. The expected loss of always choosing restart first is ≈ **0.0074** (about 0.7 pp of resolution rate).

**Stopping exploration.** Do not stop on "P(best) > 0.95". That ignores how much is at stake. Fix the ordering when the **expected loss of choosing the leader** falls below a declared threshold of caring, for example 1 pp of resolution rate (a team choice). The example above meets that bar. Record: "Ordering fixed from N incidents; revisit after architecture change." Rule: [thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md).

**Domain pitfalls.** Resolution depends on root cause, so segment arms by incident signature (a contextual bandit) when causes differ. Only the first-tried step gets a clean outcome, so do not credit or penalise later steps from the same incident. The bandit tells you what resolves incidents, not why. Postmortems still prune obsolete steps.

---

## Anti-Patterns

### A1 — Paging Thresholds as Static Alert Counts

"Page at 50 errors/min" across every service embeds a linear, symmetric cost model. It ignores the fact that `C_miss/C_page` differs by orders of magnitude between a payment path and a dev dashboard, and between 2 AM and noon traffic. Warning signs: one threshold across services with very different revenue impact, a threshold never re-derived after traffic growth, or a threshold set by "try it and adjust." **Fix:** derive per-service thresholds from P1/R1.

### A2 — Rollback Policy Ignoring the Option Value of Waiting

- **Reflexive rollback:** rolling back within 90 s on a noisy spike wastes the value of waiting and adds a disruption of its own.
- **Rollback procrastination:** 12 minutes of diagnostics at £10K/min costs £120K when the symptoms were unambiguous by minute 2.

Both come from having no explicit trigger. **Fix:** put the P4 check and a per-service trigger in the runbook. Example: "p99 > 2× SLO for 90 s after deploy → roll back unless p(regression) < 0.3 and a diagnostic is already running."

### A3 — Treating an Alert as a Deterministic Signal

An alert is a noisy sensor, not a state. If an alert fires 50 times a month and 10 firings are real, the empirical posterior is 10/50 = **20%**. Treating it as 100% causes over-triage, alert fatigue, and in the end dismissed real incidents. **Fix:** log `alert_fires` and `confirmed_incidents` per rule. Recompute the posterior quarterly and when prevalence shifts (traffic, deploy cadence). Feed it into P1 and into the runbook preamble ("historically real in 40% of firings").

### A4 — Status-Page Communication Without Reference-Point Awareness

Customers read updates against their normal-service reference point ([#8](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md)). Losses loom larger than gains, but the size of loss aversion depends on the elicitation design. The often-quoted λ ≈ 2.25 is the Tversky & Kahneman (1992) median. A meta-analysis gives a mean of about 1.96 (Brown et al., 2024). Do not use any λ as a fixed multiplier in communication planning.

Failure modes:

1. **Over-hedging early.** "A small number of users may be affected" when impact is broad. When the next update widens the scope, the reference point shifts twice.
2. **No recovery anchor.** "Services are recovering" leaves customers in a loss frame. Post "fully restored at HH:MM UTC."
3. **Updates framed as continuing losses.** "Still investigating" vs "Cause identified; fix deploying" describe the same state, framed differently.

**Fix:** open with scope and start time, frame progress as movement toward restoration, close with a timestamped "fully restored," and avoid vague probabilistic hedges.

```
Before: "We are aware of an issue that may be affecting some payment transactions."
After:  "Payments are degraded for approximately 15% of transactions since 14:32 UTC.
         Our team has identified the cause. Fix deploying now. Next update: 15:15 UTC."
```

---

## Recipes

### R1 — Paging Threshold Tuning

1. **Measure costs** from 12 months of postmortems where the alert was late or missing: `C_miss` samples (duration × damage/min × blast radius) and `C_page`. Illustrative payments SEV1: mean `C_miss ≈ £30K`, `C_page ≈ £40`.
2. **Risk-neutral threshold:** `p* = 40 / 30,000 ≈ 0.0013` (0.13%). For the general form and prevalence adjustment, see the [thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md).
3. **Tail risk:** if p90 `C_miss` is far above the mean and a large miss has consequences beyond its cash cost, set a lower threshold. Price the tail with utility-compatible losses ([practical-contract.md](../../foundations-decision-theory/references/practical-contract.md)), not by applying concave utility to positive costs.
4. **Calibrate the alert.** For example, 80 firings/month with 12 real gives a whole-rule posterior of 12/80 = **0.15**. That is far above `p*`, so the rule may be too insensitive. What matters for tuning is the posterior **at the margin** (firings just above the metric threshold), not the average across all firings.
5. **Tune the metric threshold down** while the marginal posterior stays above `p*`. Validate with a 30-day shadow window: log what would have fired without paging, then measure recall on known incidents and the added page volume.
6. **Standing postmortem item:** "Compute the actual `C_miss` for this incident and compare it with the threshold's assumption."

### R2 — Rollback Decision via Real-Options Framing

**Pre-fill per deploy** (runbook YAML): `rollback_execution_minutes` (from the last 5 rollbacks), `rollback_disruption_cost`, `damage_rate_per_minute` (from the SLO model), `feature_flag_available`.

**Decision at T = 0 after a deploy-correlated degradation**

```
1. Feature flag available? → flip it, observe 60 s. Resolved → stop (no rollback).
2. Estimate p(regression) from error-rate change (strong), p99 change (medium), diff risk score (weak).
   p > 0.70 and damage non-trivial → roll back, stop diagnosing.
   p < 0.30                       → observe one more minute, re-evaluate.
   0.30–0.70                      → one targeted diagnostic only if its EVSI > delay cost (P3); else roll back.
```

**Worked example (illustrative).** Rollback takes 4 min at £8K/min damage plus £5K disruption, so rollback cost = 4 × 8,000 + 5,000 = **£37K**. At T+3 with p(regression) = 0.85: triggering now costs £24K (3 min observed) + £37K = **£61K**. Deferring to T+6 costs £48K + £37K = **£85K**. The extra 3 minutes cost £24K and add no option value once p is already high. Write this reasoning into the incident timeline so the postmortem sees a decision, not a panic.

### R3 — Runbook-Step Ordering via Thompson Sampling

1. **Arms and reward:** each candidate first step. Reward = 1 if trying it first resolved the incident within the observation window (for example, 10 min). Priors Beta(1,1).
2. **Update** only the step tried first: success → α+1, failure → β+1.
3. **Order at incident start:** draw one sample per step from its posterior and sort in descending order.
4. **Minimum-data gate** (not an EVPI check): until every step has about 15 tries, use the authored order. The 15 is a team heuristic.
5. **Non-stationarity:** after an architecture change, or monthly, shrink the posteriors toward the prior: `α ← 1 + (α−1)·d`, `β ← 1 + (β−1)·d`, for example d = 0.95.
6. **Stop exploring** when the expected loss of the leader falls below your threshold of caring (P5), not on P(best).
7. **Runbook header:** ordering method, last posterior reset and why, number of incidents contributing, current leader with its empirical rate and n, and the review trigger.

Measure time-to-first-correct-step before and after adoption. No general improvement figure is claimed here.

---

## Composition

The decision-theory layer chooses **actions**. [`control-theory-applied.md`](control-theory-applied.md) handles **signal feedback**. The two do not overlap:

| Mechanism | Decision-theory layer | Control-theory layer |
|---|---|---|
| Alert threshold | Cost-asymmetric Bayes threshold (P1, R1) | Sensitivity tuning |
| Rollback timing | Option to defer (P4, R2) | Recovery ramp rate limiting |
| Diagnostic investment | EVSI vs delay (P3) | Dead-time awareness |
| Step ordering | Bandit on outcomes (P5, R3) | — |
| Severity | Minimax regret (P2) | — |
| Status communication | Reference points (A4) | — |

**Incident flow:** alert → posterior vs threshold (P1, A3) → severity by regret if ambiguous (P2) → diagnostic only if EVSI > delay (P3) → flag, then rollback check (P4, R2) → bandit-ordered runbook (P5, R3) → recovery ramp (control-theory R3) → postmortem: re-check `C_miss` (R1), record first-step outcome (R3), review status framing (A4).

Related: [SKILL.md](../SKILL.md), [runbook-design-guide.md](runbook-design-guide.md), [on-call-practices.md](on-call-practices.md), [incident-metrics-guide.md](incident-metrics-guide.md) (damage-rate inputs), [postmortem-facilitation.md](postmortem-facilitation.md).

---

## Sources

- Tversky, A. and Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty." *Journal of Risk and Uncertainty* 5(4). (Source of the λ ≈ 2.25 median.)
- Brown, A. L., Imai, T., Vieider, F. M., and Camerer, C. F. (2024). "Meta-analysis of Empirical Estimates of Loss Aversion." *Journal of Economic Literature*. (λ is design-dependent; mean ≈ 1.96.)
- Decision-theory textbooks and primary papers (vNM, Savage, Raiffa–Schlaifer, Howard, Dixit–Pindyck, Pratt, Thompson-sampling and bandit texts): see [`foundations-decision-theory/data/sources.json`](../../foundations-decision-theory/data/sources.json).
