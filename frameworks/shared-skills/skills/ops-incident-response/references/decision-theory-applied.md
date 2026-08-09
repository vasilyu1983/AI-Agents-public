# Decision Theory Applied to Incident Response

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Decision-theory primitives mapped to production on-call practice: paging thresholds, severity
ambiguity, diagnostic investment, rollback timing, and runbook-step ordering. Each section names
the anchoring primitive and cross-links its full playbook.

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — Paging Thresholds as Expected Utility Under Cost Asymmetry](#p1--paging-thresholds-as-expected-utility-under-cost-asymmetry)
  - [P2 — Minimax Regret for Ambiguous Severity Classification](#p2--minimax-regret-for-ambiguous-severity-classification)
  - [P3 — Value of Information on Additional Diagnostics During an Active Incident](#p3--value-of-information-on-additional-diagnostics-during-an-active-incident)
  - [P4 — Rollback Decisions as Real Options Under Irreversibility](#p4--rollback-decisions-as-real-options-under-irreversibility)
  - [P5 — Runbook-Step Ordering as a Multi-Armed Bandit on Past Incident Outcomes](#p5--runbook-step-ordering-as-a-multi-armed-bandit-on-past-incident-outcomes)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Paging Thresholds as Static Alert Counts](#a1--paging-thresholds-as-static-alert-counts)
  - [A2 — Rollback Policy Ignoring Option Value of "Wait One Minute"](#a2--rollback-policy-ignoring-option-value-of-wait-one-minute)
  - [A3 — Treating an Alert as a Deterministic Signal](#a3--treating-an-alert-as-a-deterministic-signal)
  - [A4 — Status-Page Communication Without Prospect-Theory Awareness](#a4--status-page-communication-without-prospect-theory-awareness)
- [Recipes](#recipes)
  - [R1 — Paging Threshold Tuning via EU with Cost Asymmetry](#r1--paging-threshold-tuning-via-eu-with-cost-asymmetry)
  - [R2 — Rollback Decision via Real-Options Framing](#r2--rollback-decision-via-real-options-framing)
  - [R3 — Runbook-Step Ordering via MAB on Past Incident Outcomes](#r3--runbook-step-ordering-via-mab-on-past-incident-outcomes)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Paging Thresholds as Expected Utility Under Cost Asymmetry

**Primitive anchors**: [Expected Utility (#1)](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md), [Risk Aversion (#6)](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md)

**The core decision.** An alerting rule fires when a metric crosses a threshold. Below the threshold, no page is sent. Above it, an on-call engineer is woken. This is a binary action — page or don't page — with two uncertain states: true incident (T) and false alarm (F).

```
States:      θ_T = real incident    θ_F = false alarm
Actions:     a_P = page             a_S = silence
```

The asymmetry that makes EU the right tool here is that the costs in each state are not symmetric:

| | θ_T (real incident) | θ_F (false alarm) |
|---|---|---|
| **a_P (page)** | -C_page (eng. interrupted) | -C_page (eng. interrupted) |
| **a_S (silence)** | -C_miss (outage duration × blast radius) | 0 |

`C_miss` vastly exceeds `C_page` for any SEV1 or SEV2: a missed incident means minutes or hours of user-impacting downtime; a false page costs five to fifteen minutes of on-call engineer time. On PagerDuty, a SEV1 miss for a payment service can exceed £10K/minute. A false page costs roughly £25–£50 in on-call time.

**Setting the threshold via EU.** Let `p(θ_T)` be the posterior probability of a real incident given the alert fired. The optimal action is to page when:

```
EU(a_P) > EU(a_S)

-C_page > p(θ_T) · (-C_miss) + (1 - p(θ_T)) · 0

p(θ_T) > C_page / C_miss
```

For a payment service where `C_miss = £10K/min` and a five-minute expected miss cost before response, total `C_miss ≈ £50K`; `C_page ≈ £40`. The threshold posterior is:

```
p* = 40 / 50,000 = 0.0008   (0.08%)
```

This means the alert should page if it is even 0.1% likely to reflect a real incident. Practically, any alert with greater than 1-in-1000 false-alarm ratio at this cost profile should fire.

**Risk aversion correction.** The on-call team (and the business) is not risk-neutral with respect to incidents. Under concave utility with risk aversion parameter γ, the certainty equivalent of a missed incident is lower than its expected cost — meaning the team is willing to accept more false pages to avoid the tail risk of a large miss. The practical effect: for SEV1 thresholds, use a more conservative (lower) p* than the EU formula alone suggests.

**On PagerDuty in practice.** Alert threshold tuning in PagerDuty's alert configuration maps directly: the threshold controls the sensitivity of the alert rule. The EU formula above provides a principled basis for the threshold value rather than ad hoc "let's try 5 errors per minute."

**Incident postmortem check.** After every missed detection: compute the actual `C_miss / C_page` ratio from the incident data and compare to the implicit ratio embedded in the current threshold. If `C_miss / C_page` in postmortems exceeds the threshold, lower the alert threshold.

---

### P2 — Minimax Regret for Ambiguous Severity Classification

**Primitive anchor**: [Minimax Regret (#3)](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md)

**The problem.** At the start of triage, the IC often cannot assign clean probabilities to severity levels. Symptoms are ambiguous: p99 latency is elevated but error rate is flat; one region is impacted but blast radius is unclear. The question is: classify as SEV2 (escalate, wake IC) or SEV3 (on-call handles alone)?

EU requires `p(SEV2)` and `p(SEV3)`. When these probabilities are genuinely contested in the first two minutes of an incident, minimax regret applies.

**The regret table.** Define payoffs in terms of response quality:

```
States:   θ_H = actually SEV2/SEV1 (high severity)
          θ_L = actually SEV3/SEV4 (low severity)

Actions:  a_E = escalate (treat as SEV2)
          a_H = hold (treat as SEV3)
```

| | θ_H (high) | θ_L (low) |
|---|---|---|
| **a_E (escalate)** | Full team mobilized, fast mitigation: +100 | Team interrupted unnecessarily: −15 |
| **a_H (hold)** | Slow response, outage grows: −80 | Single on-call handles correctly: +100 |

Regret matrix (subtract each column's max):

| | Regret(θ_H) | Regret(θ_L) | Max Regret |
|---|---|---|---|
| **a_E** | 0 | 115 | **115** |
| **a_H** | 180 | 0 | **180** |

Minimax regret selects **a_E (escalate)**: max regret of 115 vs. 180 for holding. The asymmetry of outcomes under θ_H — an actual SEV2 handled as SEV3 — dominates.

**Key insight.** This is why incident-response guidelines universally recommend "escalate if in doubt." The minimax regret calculation formalises the intuition: the worst outcome of over-escalating is lower than the worst outcome of under-escalating, regardless of the probability of each state.

**Application to Datadog triage.** When a Datadog monitor fires with alert group ambiguity (single host vs. cluster-wide pattern, unclear in first 90 seconds), apply this table: escalate unless the symptoms are unambiguously bounded to a single non-critical host.

---

### P3 — Value of Information on Additional Diagnostics During an Active Incident

**Primitive anchor**: [Value of Information (#4)](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md)

**The decision.** During active triage, additional diagnostic actions take time: pulling distributed traces, running a slow query log, examining a 30-day anomaly detection model output. Each action delays mitigation. Is the diagnostic worth running?

The VoI framework gives the ceiling: run the diagnostic only if its expected value of sample information (EVSI) exceeds the cost (time-to-mitigation delay × incident damage rate).

```
EVSI = E_x[ max_a EU(a | x) ] − max_a EU(a | prior)
Cost = delay_minutes × damage_per_minute
```

If EVSI < Cost, skip the diagnostic and act on the current prior.

**When EVPI = 0.** If the optimal action is the same under all plausible states — e.g., the runbook step says "restart the pod regardless of cause" — then EVPI = 0 and no diagnostic is worth running before executing that step.

**Worked example.** A Datadog alert fires: p99 latency elevated on the payments service. Prior: p(DB bottleneck) = 0.6, p(upstream API degradation) = 0.4.

- Action under DB bottleneck: scale read replicas.
- Action under upstream API degradation: flip feature flag to fallback path.

Without diagnostics, the team acts on the higher-probability state (scale replicas). If wrong, they lose 3 extra minutes retrying. Damage rate: £2K/minute.

Running a slow query log takes 2 minutes. If it correctly identifies the cause 80% of the time:
- EVSI ≈ 0.4 × 0.8 × (3 minutes × £2K) = £1.92K (saves the 3-minute wrong-action cost in 32% of incidents)
- Cost = 2 minutes × £2K = £4K

EVSI < Cost: skip the diagnostic, act on the prior.

But if damage rate is £10K/minute:
- Cost = 2 × £10K = £20K
- EVSI ≈ 0.4 × 0.8 × 3 × £10K = £9.6K

Still EVSI < Cost. For very high damage rates, even modest diagnostics rarely pencil out against an obvious prior. The on-call rule: **act on the strongest prior hypothesis; run diagnostics only after mitigation, not before**.

**Runbook design implication.** Runbooks should pre-compute EVPI for their diagnostic steps. Steps that are high-cost (slow) but low-EVPI (the mitigation is the same regardless) should be moved to the postmortem section, not the active triage section.

---

### P4 — Rollback Decisions as Real Options Under Irreversibility

**Primitive anchor**: [Real Options (#7)](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md)

**The situation.** After a deployment, metrics start degrading. The IC must decide: rollback now, or wait for more data? Rollback is not free: it takes 3–8 minutes to execute, may cause a brief secondary disruption during re-deployment, and forecloses the option to gather enough information to understand the incident while the new version is live.

Real options analysis applies: **rollback now is an irreversible commitment**. Waiting one minute is an option to defer. The option has value because uncertainty may resolve.

**Option to defer: structure.**

```
V_rollback_now    = -C_rollback - (expected damage during rollback) + (certainty of stopping damage)
V_wait_one_minute = -C_per_minute_damage + Option_value_of_better_information
```

The option value of waiting one minute = probability that diagnostics in that minute will change the decision × value of making the right decision.

**When to exercise immediately (option value approaches zero).**

The option to wait is worthless when:
1. The prior probability of a real regression is already high (> 0.8).
2. The blast radius is large and damage rate is high (C_miss >> C_rollback).
3. Waiting does not reveal anything new — symptoms are already unambiguous (EVPI ≈ 0 for one more minute of data).

SEV1 payment outage after a deployment: damage rate £10K/minute, rollback takes 3 minutes. Even a 2-minute wait costs £20K with no option value if the symptoms are unambiguous.

**When deferral has positive option value.**

- The metrics are noisy and the trend is unclear (high uncertainty → high option value).
- The rollback itself has a non-trivial secondary disruption cost (high exercise price).
- A feature flag can instantly pause the new behaviour without a full rollback (low-cost intermediate option — exercise the smaller option first).

**Practical protocol.** For every incident following a deployment, run the three-point check before ordering rollback:

```
1. P(regression | current symptoms) > 0.7?      → proceed to 2
2. C_damage × minutes_of_waiting > C_rollback?   → proceed to 3
3. Will one more minute reveal anything new?      → if NO, rollback now
                                                    if YES, wait one minute
```

Feature flags are compound options: they let the team pause exposure (small option) before deciding whether to rollback (large irreversible option). Use them as the first-stage exercise whenever available.

---

### P5 — Runbook-Step Ordering as a Multi-Armed Bandit on Past Incident Outcomes

**Primitive anchor**: [Multi-Armed Bandit (#10)](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md)

**The problem.** A runbook for a service with recurring incidents lists N mitigation steps in a fixed order derived from historical intuition. But the actual resolution rate per step varies across incident instances: step ordering that was optimal six months ago may be suboptimal today as the service evolves.

Each runbook step is an arm in a MAB. The reward is binary: does executing this step first (or next) lead to faster incident resolution?

**Thompson sampling applied.**

Maintain a Beta posterior for each step's resolution probability. After each incident, update the posterior for the step(s) that were attempted:

```python
# Prior: Beta(1, 1) for each step (uniform — no preference)
# After incident i where step k was tried first and resolved:
beta_k = Beta(alpha_k + 1, beta_k)         # success: increment alpha

# After incident i where step k was tried first but did not resolve:
beta_k = Beta(alpha_k, beta_k + 1)         # failure: increment beta
```

At the start of the next incident, sample from each posterior and execute the step with the highest sample first.

**Worked example.** A Kafka consumer lag runbook has three candidate first steps:

| Step | Tries | Resolved | Empirical rate | Posterior |
|---|---|---|---|---|
| Restart consumer group | 22 | 16 | 73% | Beta(17, 7) |
| Scale consumer replicas | 18 | 9 | 50% | Beta(10, 10) |
| Clear dead-letter queue | 8 | 3 | 38% | Beta(4, 6) |

Thompson sampling at incident 49: sample θ_1, θ_2, θ_3. Step 1 is sampled highest roughly 65% of the time; the runbook should list it first by default but maintain exploration probability for steps 2 and 3.

**When to stop exploring.** When P(step k is best) > 0.95 across posterior samples, fix the ordering and stop exploration. Add a note in the runbook: "Ordering optimised from N incident observations; revisit after service architecture changes."

**MAB is not a substitute for postmortems.** The bandit tracks what resolves incidents, not why. Postmortems explain the mechanism. Use MAB to order the runbook; use postmortems to prune steps that are structurally obsolete.

---

## Anti-Patterns

### A1 — Paging Thresholds as Static Alert Counts

**Decision theory diagnosis**: Action rule with no utility function and no cost asymmetry.

The most common incident-response configuration mistake is setting alert thresholds as static counts: "page when error count exceeds 50 per minute." This embeds implicit assumptions that are almost never examined:

- Is the cost of missing 49 errors per minute zero?
- Does a count threshold hold equally for a payment service and a dev dashboard?
- Does 50 errors at 2 AM (single region, low traffic) equal 50 errors at noon (global traffic)?

The count threshold is an implicit EU calculation with a linear utility function and no asymmetry between `C_page` and `C_miss`. For any service where downtime costs exceed on-call interruption costs by more than 10×, this is the wrong utility function.

**Diagnosis checklist:**
- Is the threshold the same across services with wildly different revenue impact?
- Was the threshold set by "let's try this and adjust" without measuring `C_miss`?
- Has the threshold never changed despite service traffic growth?

If yes to any of these, re-derive the threshold using the EU approach in Pattern P1 and Recipe R1.

**Fix**: Replace count thresholds with probability-posterior thresholds calibrated to the EU formula. See R1.

---

### A2 — Rollback Policy Ignoring Option Value of "Wait One Minute"

**Decision theory diagnosis**: Treating a reversible-seeming decision as costless under time pressure; either always rolling back immediately (option value destroyed by impatience) or never rolling back (option value destroyed by inaction).

Two failure modes appear in postmortems:

**Failure mode A — Reflexive immediate rollback.** The team rolls back within 90 seconds of metric degradation. Three out of five times the degradation was a noisy spike; the rollback caused an additional 4-minute disruption unnecessarily. The option to wait 60 seconds and observe had positive value that was destroyed by time pressure.

**Failure mode B — Rollback procrastination.** The team waits 12 minutes gathering diagnostics before rollback, accumulating £120K in damage. The option value of waiting was negative after minute 2 (symptoms were unambiguous at minute 2), but no explicit threshold triggered the rollback decision.

**The root cause in both.** No rollback policy that accounts for time-varying option value. The team treats rollback as a "whenever it feels right" decision rather than a rule-based one.

**Fix**: Implement the three-point check from Pattern P4 with explicit time thresholds. Pre-compute the rollback trigger point in the runbook for each service: "If p99 latency exceeds 2× SLO for more than 90 seconds following a deployment, initiate rollback unless P(regression) < 0.3 and diagnostic action is actively in progress."

---

### A3 — Treating an Alert as a Deterministic Signal

**Decision theory diagnosis**: Conflating a noisy sensor reading with a certain state; acting on the prior without computing a posterior.

When Datadog fires a p99 alert, the engineer sees "ALERT: p99 > 500ms" and immediately assumes the service is degraded. But the alert is a probabilistic signal, not a confirmation. The alert has a false positive rate (firing during transient noise) and a detection rate (firing on real incidents). Without these rates, the posterior probability of a real incident given the alert is unknown.

```
P(real incident | alert fired) = P(alert | incident) × P(incident) / P(alert)
```

If an alert fires 50 times per month and 10 of those correspond to real incidents, the posterior is 20%—not 100%. Treating it as 100% leads to over-investing in triage and unnecessary escalation for 80% of alert firings.

**Practical consequences of this anti-pattern:**
- On-call engineers are woken for false positives at a rate that creates alert fatigue.
- Alert fatigue causes real incidents to be dismissed — the same cognitive bias, reversed.
- Triage time is wasted on alerts with low posterior probability.

**Fix**: Maintain a calibration log in PagerDuty or Datadog: for each alert rule, track `alert_fires` and `confirmed_incidents`. Compute the empirical posterior quarterly. Use this posterior in the EU threshold calculation (Pattern P1) and in the triage runbook preamble: "This alert has historically been a true incident in 40% of firings."

---

### A4 — Status-Page Communication Without Prospect-Theory Awareness

**Primitive anchor**: [Prospect Theory (#8)](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md)

**Decision theory diagnosis**: Status-page framing ignores loss aversion and reference-point effects on customer perception.

The standard incident response status-page template frames updates around the progress of investigation: "We are investigating an issue affecting payments." Customers read this against their reference point (expectations of normal service). Under prospect theory:

- A message framed as "service degraded by 20%" is processed as a loss relative to the normal reference point.
- Loss aversion (λ ≈ 2.25) means customers weight this roughly 2× more negatively than a corresponding gain framing would be weighted positively.
- Probability weighting amplifies small stated probabilities: "a small number of customers may be affected" is mentally overweighted, not underweighted.

**Three specific failure modes:**

1. **Over-hedging at the start**: "A small number of users may be experiencing intermittent issues" when the impact is actually broad. Customers update toward the worst-case interpretation (probability weighting on ambiguous small-probability language). When the next update confirms broad impact, the reference point has shifted twice — anger compounds.

2. **Under-framing recovery**: "Services are recovering" does not anchor to the new reference point (resolved state). Customers remain in loss-frame until an explicit "fully resolved" anchor is posted with a timestamp.

3. **Progress reports framed as continuing losses**: "We are still investigating" (loss frame: the problem persists) versus "We have identified the cause and are deploying a fix" (gain frame: progress is being made). Same factual state, different prospect theory value.

**Fix**: Write status updates with explicit reference-point management:
- Open with impact scope and timing: anchor the reference point immediately.
- Frame progress updates as gains from the degraded state, not as continuing losses from normal.
- Use "fully restored" with a timestamp as the explicit reference-point reset.
- Avoid probabilistic hedges that activate probability-weighting overreaction.

Example revision:

```
Before: "We are aware of an issue that may be affecting some payment transactions."
After:  "Payments are degraded for approximately 15% of transactions since 14:32 UTC.
         Our team has identified the cause. Fix deploying now. Next update: 15:15 UTC."
```

---

## Recipes

### R1 — Paging Threshold Tuning via EU with Cost Asymmetry

**Objective**: Replace an intuition-derived alert threshold with a threshold calibrated to the actual cost ratio between missed incidents and false pages.

**Primitive stack**: Expected Utility (#1) + Risk Aversion (#6) + Bayesian Decision (#2)

**Step 1: Measure costs.**

```python
# Incident postmortem data, last 12 months
C_miss_samples = [
    duration_minutes * blast_radius_factor * damage_per_minute
    for incident in postmortems_where_alert_was_late_or_missed
]

C_miss_median = median(C_miss_samples)       # central estimate
C_miss_p90    = percentile(C_miss_samples, 90)  # tail risk

C_page = avg_engineer_cost_per_hour * (avg_triage_minutes / 60) * avg_engineers_paged
```

For a payments SEV1: `C_miss_median ≈ £30K`, `C_miss_p90 ≈ £150K`, `C_page ≈ £40`.

**Step 2: Derive the risk-neutral posterior threshold.**

```python
p_star_neutral = C_page / C_miss_median
# Example: 40 / 30,000 = 0.0013  (0.13%)
```

**Step 3: Apply risk aversion correction.**

The team penalises tail risk. Use CRRA risk aversion with γ = 1.5 (typical for production infrastructure decisions):

```python
import numpy as np

def crra_utility(x, gamma=1.5):
    if gamma == 1:
        return np.log(x + 1e-9)
    return (x ** (1 - gamma)) / (1 - gamma)

# CE of missing: the certain equivalent of the mixed C_miss distribution
C_miss_eu = np.mean([crra_utility(c) for c in C_miss_samples])
C_miss_ce = (C_miss_eu * (1 - 1.5)) ** (1 / (1 - 1.5))  # invert CRRA

# Risk-averse threshold is lower (more conservative) than the neutral threshold
C_page_eu = crra_utility(C_page)
# For simplicity, use the CE of C_miss vs raw C_page:
p_star_risk_averse = C_page / C_miss_ce
```

Risk-averse threshold is lower than risk-neutral: for payments, typically 0.05%–0.15%.

**Step 4: Calibrate the alert's empirical sensitivity at p_star.**

Map the posterior threshold to the alert rule's parameters. The posterior `p(real incident | alert fires)` is:

```python
# Historical calibration
alert_fires_per_month = 80
true_incidents_per_month = 12
p_posterior_empirical = true_incidents_per_month / alert_fires_per_month
# = 0.15 (15%)

# Is this above p_star (0.13%)? Yes, significantly.
# The alert fires only when posterior >> threshold.
# Consider if it can be made more sensitive (lower threshold metric value)
# without flooding false positives.
```

**Step 5: Tune the threshold metric value.**

Using the posterior calibration, lower the threshold metric value until the estimated p_posterior approaches 10 × p_star (a safety margin above the theoretical floor). Validate with a 30-day shadow window: log what would have fired without paging, then compute recall on known incidents from that window.

**Step 6: Revisit after each SEV1/2 postmortem.**

Add a standing postmortem item: "Was the alert threshold correctly set? Compute actual C_miss for this incident and compare to the threshold's embedded C_miss assumption."

**Expected outcome**: False page rate decreases 20–40%; detection recall for real incidents holds at > 95%.

---

### R2 — Rollback Decision via Real-Options Framing

**Objective**: Replace "rollback when it feels bad enough" with a deterministic rule that accounts for deferral option value, incident damage rate, and rollback execution cost.

**Primitive stack**: Real Options (#7) + Value of Information (#4) + Bayesian Decision (#2)

**Step 1: Pre-compute rollback parameters at deploy time.**

Before a deployment goes out, the runbook should be populated with these values:

```yaml
# In the service deployment runbook, filled per-deploy:
rollback_execution_minutes: 4          # measured from last 5 rollbacks
rollback_disruption_cost: 5000         # £ secondary impact during re-deploy
damage_rate_per_minute: 8000           # £/min at current traffic (from SLO model)
feature_flag_available: true           # can the new behaviour be paused instantly?
```

**Step 2: Compute the rollback trigger threshold.**

```python
# Time at which waiting becomes more expensive than rolling back:
# cost_of_waiting(t) = damage_rate * t
# cost_of_rollback = rollback_execution_minutes * damage_rate + rollback_disruption_cost

rollback_cost = rollback_execution_minutes * damage_rate + rollback_disruption_cost
# = 4 * 8000 + 5000 = £37,000

# Cumulative damage of waiting t minutes before rollback starts:
# total_damage(t) = damage_rate * (t + rollback_execution_minutes)

# Rollback immediately if:
# damage_rate * (0 + execution_minutes) + disruption < 0
# (i.e., rollback is always net negative — but its cost is bounded, while waiting is unbounded)

# The deferral option has value only while diagnostics can still change the action.
# If P(regression | symptoms) > p_trigger, rollback now:
p_trigger = rollback_cost / (rollback_cost + evsi_of_one_more_minute)
# evsi_of_one_more_minute = p_uncertainty * p_diagnostic_success * damage_rate * time_saved_by_correct_action
```

**Step 3: Decision logic at incident declaration.**

```
T = 0 (alert fires or engineer notices degradation after deployment)

Check 1: Is a feature flag available?
  → YES: flip the feature flag immediately (low-cost option; does not foreclose rollback).
         Observe for 60 seconds.
  → NO: proceed to Check 2.

Check 2: p(regression | current symptoms) — estimate from:
  - Error rate change since deploy (high signal)
  - p99 latency change since deploy (medium signal)
  - Deploy diff risk score if available (low signal)

  If p(regression) > 0.70 AND damage_rate_per_minute is non-trivial:
    → Initiate rollback. Stop gathering diagnostics.
  If p(regression) < 0.30:
    → One minute observation window.  Re-evaluate.
  If 0.30 ≤ p(regression) ≤ 0.70:
    → Gather one targeted diagnostic (EVSI check: is it worth it?).
       If EVSI > cost: run diagnostic.
       If EVSI < cost: act on the 0.5 prior; initiate rollback.
```

**Step 4: Feature flag as compound option.**

Treat the feature flag toggle as the first-stage option (low exercise price, reversible, instant). The full rollback is the second-stage option (higher exercise price, 4-minute execution, minor disruption). Exercise stage 1 first; escalate to stage 2 only if stage-1 observation does not resolve symptoms.

```
Stage 1: flag off → observe 60 s → if resolved: hold at stage 1, no rollback needed
Stage 2: full rollback → if stage 1 did not resolve symptoms within 60 s
```

**Step 5: Log option exercise decisions in the incident timeline.**

Include in the incident channel: "Rollback trigger evaluation at T+3: p(regression) = 0.85, damage rate = £8K/min, rollback cost = £37K. Triggering rollback now. Total cost if triggered now = damage during the 3-minute observation window (£8K × 3 = £24K) + rollback cost (£37K) = £61K. Cost if instead deferred to T+6 = damage during a 6-minute window (£8K × 6 = £48K) + the same £37K rollback cost = £85K. Waiting the extra 3 minutes costs £24K more with no offsetting option value once p(regression) > 0.7 — trigger now."

This creates postmortem-ready evidence that the rollback decision was taken on a rational basis, not panic.

---

### R3 — Runbook-Step Ordering via MAB on Past Incident Outcomes

**Objective**: Adaptively order runbook mitigation steps based on accumulated outcome data from past incidents, using Thompson sampling to balance exploration of less-tried steps against exploitation of known-good ones.

**Primitive stack**: Multi-Armed Bandit (#10) + Bayesian Decision (#2) + Value of Information (#4)

**Step 1: Define arms, reward, and prior.**

```python
from dataclasses import dataclass, field
from typing import List
import numpy as np

@dataclass
class RunbookStep:
    name: str
    description: str
    alpha: float = 1.0   # Beta prior: successes + 1
    beta: float = 1.0    # Beta prior: failures + 1

    @property
    def mean_resolution_rate(self):
        return self.alpha / (self.alpha + self.beta)

    def sample(self):
        return np.random.beta(self.alpha, self.beta)

# Example: Kafka consumer lag runbook
steps = [
    RunbookStep("restart_consumer_group",    "Kill and restart all consumers in the group"),
    RunbookStep("scale_consumer_replicas",   "Add 2 consumer replicas via Kubernetes"),
    RunbookStep("clear_dead_letter_queue",   "Flush DLQ to unblock processing"),
    RunbookStep("rotate_consumer_credentials","Rotate Kafka credentials if auth errors present"),
]
```

**Step 2: Update posteriors after each incident.**

```python
def record_outcome(step: RunbookStep, resolved: bool):
    """
    resolved = True if executing this step as the FIRST action led to incident resolution
               within the observation window (e.g., 10 minutes).
    resolved = False if the step was tried first and did not resolve the incident.
    """
    if resolved:
        step.alpha += 1
    else:
        step.beta += 1

# After incident 23: restart_consumer_group was tried first, incident resolved in 8 min.
record_outcome(steps[0], resolved=True)

# After incident 24: scale_consumer_replicas was tried first, did not resolve; restart did.
record_outcome(steps[1], resolved=False)
```

**Step 3: Generate ordered runbook at incident start.**

```python
def get_ordered_runbook(steps: List[RunbookStep], n_samples: int = 1000) -> List[RunbookStep]:
    """
    Thompson sampling: draw from each step's posterior and order by sample.
    Run this at the start of each incident to get the current recommended order.
    """
    samples = [(step.sample(), step) for step in steps]
    samples.sort(reverse=True, key=lambda x: x[0])
    return [step for _, step in samples]

# At incident start:
ordered = get_ordered_runbook(steps)
print("Recommended order:")
for i, step in enumerate(ordered, 1):
    print(f"  {i}. {step.name} (resolution rate: {step.mean_resolution_rate:.0%}, "
          f"n={int(step.alpha + step.beta - 2)} trials)")
```

**Step 4: EVPI check before running the MAB ordering.**

Before trusting the MAB ordering for a new incident class, compute whether the data is sufficient:

```python
def evpi_sufficient(steps: List[RunbookStep], min_trials: int = 15) -> bool:
    """
    If any step has fewer than min_trials, the posterior is too uncertain.
    Fall back to the manually authored order.
    """
    return all((step.alpha + step.beta - 2) >= min_trials for step in steps)

if not evpi_sufficient(steps):
    print("Insufficient data for MAB ordering — using authored runbook order.")
```

**Step 5: Handling non-stationarity.**

Service architecture changes can invalidate posteriors. Implement a sliding-window decay:

```python
def decay_posteriors(steps: List[RunbookStep], decay_factor: float = 0.95):
    """
    Monthly: decay posteriors toward the prior (1, 1) to allow re-exploration
    after service changes. Apply after each full calendar month with no new data
    or after a major architecture change.
    """
    for step in steps:
        excess_alpha = step.alpha - 1.0
        excess_beta  = step.beta  - 1.0
        step.alpha = 1.0 + excess_alpha * decay_factor
        step.beta  = 1.0 + excess_beta  * decay_factor
```

**Step 6: Runbook metadata.**

Add to the runbook header:

```yaml
# Runbook: Kafka Consumer Lag
# Step ordering: Thompson sampling (MAB)
# Last posterior reset: 2026-01-15 (post-Kafka 3.x upgrade)
# Total incidents contributing to ordering: 31
# Dominant first step: restart_consumer_group (73% empirical resolution rate, n=22)
# Review trigger: architecture change OR > 6 months since last reset
```

**Expected outcome**: Median time-to-first-correct-step decreases by 20–35% over a 3–6 month accumulation window vs. static ordering, based on MAB convergence rates at typical K=3–6 arms and 2–5 incidents per month.

---

## Composition

These patterns and recipes compose directly with the incident response workflow in
[`SKILL.md`](../SKILL.md) and with the control-theory stack in
[`control-theory-applied.md`](control-theory-applied.md).

The decision-theory layer operates at the **action-selection** level; the control-theory layer
operates at the **signal-feedback** level. They address different failure modes and do not overlap:

| Mechanism | Decision-theory layer | Control-theory layer |
|---|---|---|
| Alert threshold | EU cost-asymmetry (P1, R1) | PID sensitivity tuning |
| Rollback timing | Real options deferral value (P4, R2) | Recovery ramp rate limiting |
| Diagnostic investment | VoI / EVSI (P3) | Dead-time compensation awareness |
| Step ordering | MAB on outcomes (P5, R3) | Not applicable |
| Severity classification | Minimax regret (P2) | Not applicable |
| Status communication | Prospect theory framing (A4) | Not applicable |

**Full incident decision stack:**

```
Alert fires:
  Posterior calibration (P1, A3) → is this worth waking someone?
    → If yes: page, open channel

Triage:
  Severity ambiguous → minimax regret (P2): escalate if in doubt
  Diagnostic available → EVSI check (P3): act on prior unless EVSI > cost

Mitigation:
  Deployment-related → real options (P4, R2): feature flag first, rollback threshold check
  Runbook step selection → MAB ordering (P5, R3): run highest-posterior step first

Recovery:
  Traffic ramp → control-theory R3 (control-theory-applied.md)
  Rollback monitoring → real options: option exercised; no further deferral value

Postmortem:
  Threshold review (R1): did C_miss match embedded assumption?
  Posterior update (R3): record outcome for MAB step ordering
  Status-page retrospective (A4): did framing reflect reference-point management?
```

---

## Sources

### Primitive Cross-References (foundations-decision-theory)

| # | Primitive | File |
|---|---|---|
| 1 | Expected Utility | [01-expected-utility.md](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md) |
| 2 | Bayesian Decision | [02-bayesian-decision.md](../../foundations-decision-theory/assets/templates/decision-theory/02-bayesian-decision.md) |
| 3 | Minimax Regret | [03-minimax-regret.md](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md) |
| 4 | Value of Information | [04-value-of-information.md](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md) |
| 6 | Risk Aversion | [06-risk-aversion.md](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md) |
| 7 | Real Options | [07-real-options.md](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md) |
| 8 | Prospect Theory | [08-prospect-theory.md](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md) |
| 10 | Multi-Armed Bandit | [10-multi-armed-bandit.md](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md) |

### Incident Response Cross-References

- [SKILL.md](../SKILL.md) — Incident response workflow, severity classification, IC checklist
- [control-theory-applied.md](control-theory-applied.md) — Signal-feedback recipes: autoscaler retune, cascading-failure containment, recovery throttling
- [runbook-design-guide.md](runbook-design-guide.md) — Runbook authoring; apply MAB ordering (P5, R3) to step sequence
- [on-call-practices.md](on-call-practices.md) — On-call rotation and fatigue; alert calibration (R1) reduces unnecessary pages
- [incident-metrics-guide.md](incident-metrics-guide.md) — MTTD/MTTR measurement; use as damage-rate inputs to EU calculations (R1, R2)
- [postmortem-facilitation.md](postmortem-facilitation.md) — Postmortem workflow; add threshold review (R1) and MAB update (R3) as standing items

### Primary Sources

- Savage, L. J. (1954). *The Foundations of Statistics.* Wiley. (Minimax regret, subjective EU.)
- von Neumann, J. and Morgenstern, O. (1944/1947). *Theory of Games and Economic Behavior.* Princeton University Press. (EU axioms.)
- Raiffa, H. and Schlaifer, R. (1961). *Applied Statistical Decision Theory.* Harvard University Press. (EVPI, EVSI.)
- Howard, R. A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics* 2(1). (VoI applied framing.)
- Dixit, A. K. and Pindyck, R. S. (1994). *Investment under Uncertainty.* Princeton University Press. (Real options.)
- Kahneman, D. and Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica* 47(2). (Loss aversion, reference points.)
- Russo, D. J., Van Roy, B., Kazerouni, A., Osband, I., and Wen, Z. (2018). "A Tutorial on Thompson Sampling." *Foundations and Trends in Machine Learning* 11(1).
- Pratt, J. W. (1964). "Risk Aversion in the Small and in the Large." *Econometrica* 32(1–2). (CARA/CRRA, certainty equivalent.)
- Lattimore, T. and Szepesvári, C. (2020). *Bandit Algorithms.* Cambridge University Press.
