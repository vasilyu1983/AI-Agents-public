---
description: Decision theory applied to product management — RICE/WSJF as utility specs, VoI gating before A/B tests, real options for irreversible launches, prospect theory in roadmap framing, bandits for adaptive resource allocation, minimax regret under ambiguous uncertainty, stochastic dominance to skip MCDA. Link adapter onto foundations-decision-theory.
status: stable
---

# Decision Theory Applied: Product Management

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

This file maps decision-theory primitives to PM decisions: backlog scoring, experiment approval, roadmap ranking, launch staging, stakeholder framing, and mid-quarter reallocation. It is a link adapter. Definitions, formulas, and generic failure modes live in the foundation. This file keeps only the PM mapping, domain pitfalls, and checked worked examples.

**Foundation pointers**

- Root skill: [`foundations-decision-theory/SKILL.md`](../../foundations-decision-theory/SKILL.md)
- Exact finite EVPI/EVSI: [`finite-state-calculator.md`](../../foundations-decision-theory/references/finite-state-calculator.md)
- Utility-compatible costs and sensitivity: [`practical-contract.md`](../../foundations-decision-theory/references/practical-contract.md)
- Best-arm identification vs regret, expected-loss stopping, off-policy evaluation: [`thresholds-stopping-and-ope.md`](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)
- Primitive templates: [EU #1](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md), [Minimax regret #3](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md), [VoI #4](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md), [MCDA #5](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md), [Risk aversion #6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md), [Real options #7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md), [Prospect theory #8](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md), [Ellsberg/Allais #9](../../foundations-decision-theory/assets/templates/decision-theory/09-ellsberg-allais.md), [Bandits #10](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md), [Stochastic dominance #11](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md)

All £ figures and priors below are **illustrative**. Replace them with your own estimates.

---

## Table of Contents

- [Decision Map](#decision-map)
- [Patterns](#patterns)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
- [Sources](#sources)

---

## Decision Map

| PM decision | Primitive | Where |
|---|---|---|
| Backlog scoring (RICE, ICE) | EU (#1), MCDA (#5), risk aversion (#6) | P1, A1 |
| Monetization/architecture choice when priors are contested | Minimax regret (#3) | P2 |
| Whether to run an A/B test | VoI (#4): EVPI to skip, EVSI to approve | P3, A2, R1 |
| Removing dominated roadmap items before weighting | Stochastic dominance (#11) | P4, R2 |
| WSJF sequencing | EU (#1), real options (#7) | P5 |
| Full launch vs staged rollout | Real options (#7) | P6 |
| Presenting cuts to stakeholders | Prospect theory (#8) | P7, A4 |
| Mid-quarter capacity reallocation | Bandits (#10), expected-loss stopping | P8, R3 |
| High-variance vs stable bets | Risk aversion (#6) | A3 |
| Multi-stakeholder ranking | MCDA (#5) | A5, R2 |

**Cross-cutting rule.** Every ranking or go/no-go ends with a sensitivity or robustness step: weight perturbation, a regret cross-check, or an EVPI skip test. An analysis without one is not ready for a planning review.

---

## Patterns

### P1 — RICE and WSJF as Utility Specifications

RICE = Reach × Impact × Confidence ÷ Effort is an informal "expected value per unit cost." Its hidden assumptions:

| RICE component | Decision-theory reading | Hidden assumption |
|---|---|---|
| Reach | Population affected | All affected users contribute equally |
| Impact | Utility per affected user | Ordinal scale treated as cardinal and linear |
| Confidence | Probability weight | Confidence discounts value proportionally |
| Effort | Cost denominator | Marginal cost is constant |

**PM action.** Before planning: (a) state the unit of Impact (ARR, activation points), (b) confirm that Reach × Impact should multiply rather than add, (c) when the team argues about what an Impact of 3 means, replace ordinal Impact with an elicited certainty equivalent in ARR ([#6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md)), and (d) perturb Confidence by ±0.2 on the top 5 items and check whether the ranking holds (A1).

### P2 — Minimax Regret for Ambiguous-Uncertainty Decisions

**When.** You are choosing a monetization architecture (subscription, usage-based, hybrid) before any willingness-to-pay or usage data exists, and stakeholder priors differ by more than 2×. EU then just rewards whoever states their prior most confidently. Mechanics: [#3](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md).

```
Payoff (£K)             θ₁ API-heavy   θ₂ seat-centric   Max regret
Subscription (a₁)          −400           +500              1,000
Usage-based (a₂)           +600           −200                700
Hybrid (a₃)                +200           +300                400   ← minimax-regret pick
(column max: θ₁ = 600, θ₂ = 500)
```

**PM action.** Record the regret matrix as the output of the planning session, not just the pick. When the first cohort of usage data arrives, check whether waiting for more data could pay off. If EVPI is below the cost of the delay, commit now. Otherwise, estimate the EVSI of the specific data you would collect before deciding to wait (P3). If ambiguity aversion is driving the room, see [#9](../../foundations-decision-theory/assets/templates/decision-theory/09-ellsberg-allais.md).

### P3 — VoI Gate Before Approving an A/B Test

**Problem.** Experiment slots are scarce, and some tests produce significant results that change nothing.

**Gate logic** (formulas in [#4](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md), exact numbers via [finite-state-calculator.md](../../foundations-decision-theory/references/finite-state-calculator.md)):

1. **Which decision changes?** If the same action follows every result, EVPI = 0. Kill the test.
2. **Payoff table** (ship vs hold, per state) in ARR or activation units.
3. **Skip test:** if EVPI is below the full cost, reject. Full cost means engineering cost, blocked slots, and the delay to the ship decision, all in the same money units.
4. **Approval test:** compute the **EVSI of this design** (sample size, MDE, error rates). Approve only if EVSI exceeds the full cost. EVPI above cost is **not** grounds to approve. It only means the test is not ruled out.

**Worked EVPI (checkout redesign).** Prior 0.65 that the redesign lifts conversion. Shipping pays +£200K if it works and −£120K (a quarter of delayed alternatives) if it does not. Holding pays £0.

```
EU(ship) = 0.65×200 − 0.35×120 = £88K ;  EU(hold) = 0
EVPI     = 0.65×200 + 0.35×0 − 88  = £42K
```

With 2 engineer-weeks plus 6 weeks of slots at about £18K, plus the value lost by delaying the ship decision 6 weeks, EVPI (£42K) does not rule the test out. Whether to **approve** depends on this design's EVSI, which must be computed, not assumed to be a fixed share of EVPI. R1 shows a case where EVSI = 0 even though EVPI > 0.

### P4 — Stochastic Dominance to Short-Circuit MCDA

Before arguing over MCDA weights, remove items that are first-order stochastically dominated on a **single** outcome metric, such as ARR impact. Every decision maker who prefers more of that metric agrees on the removal, whatever their risk attitude. Definition: [#11](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md).

```
ARR impact (£K)   p10   p25   p50   p75   p90
Feature X:         80   140   200   310   450
Feature Y:         20    60   110   200   320
Feature Z:         90   160   220   290   400

X ≥ Y at every elicited quantile → X dominates Y at these points; drop Y.
X vs Z: Z higher at p10–p50, X higher at p75–p90 → quantiles cross; keep both for MCDA.
```

**Caveats.** Five elicited quantiles only approximate the CDF. Treat a narrow margin at any quantile as "not dominated." FSD across several criteria (for example, ARR and delivery risk) is undefined unless you first combine them into one scale. Use MCDA (#5) for that.

### P5 — WSJF as a Cost-of-Delay Utility Function

WSJF = Cost of Delay ÷ Job Duration. CoD is an informal multi-attribute utility:

| CoD component | Decision-theory reading | Common mis-specification |
|---|---|---|
| User-business value | Expected value of the outcome | Scored ordinally; sensitivity ignored |
| Time criticality | Rate at which value decays with delay | Treated as binary |
| Risk reduction / opportunity enablement | Option value (#7) | Ignored, so platform work is undervalued |

**PM action.** Require cardinal, ARR-equivalent CoD estimates for the top 10 items. Price "opportunity enablement" as an option to expand ([#7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md); see R2 step 3). Break ties with risk aversion: prefer the lower-variance item unless the team explicitly accepts the variance.

### P6 — Real Options for Irreversible Launches

**Problem.** "We'll roll back if it hurts" assumes rollback is cheap. If rollback takes weeks, a 100% launch gives up the option value of staged rollout. Theory: [#7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md).

- A staged rollout (1% → 10% → 50% → 100%) is a compound option to expand. Each stage runs only if the previous stage clears the kill threshold.
- The abandonment option's payoff is the harm avoided for the rest of the user base.
- Option value rises with the uncertainty σ (the p10–p90 spread of impact) and with observation time T. It falls with the extra cost K of staging.

**PM action.** For any feature whose rollback costs more than about 1 engineer-day, require a staged plan and a written kill criterion before launch approval ([kill-criteria-template.md](../assets/prioritization/kill-criteria-template.md)). A kill criterion that nobody consults until after launch is an option you paid for but never used in the launch decision.

### P7 — Prospect Theory in Roadmap Stakeholder Framing

**Problem.** Dropping a sales-requested Feature X for a higher-EU platform Feature Y still triggers an escalation. Stakeholders evaluate against a reference point, and losses loom larger than gains ([#8](../../foundations-decision-theory/assets/templates/decision-theory/08-prospect-theory.md)). How strong this is depends on the design and the setting. The often-quoted λ ≈ 2.25 is the Tversky & Kahneman (1992) median. A meta-analytic mean is about 1.96 (Brown et al., 2024). Treat λ as something to elicit locally, not as a constant.

**Framing rules (honest reframing, not deception).**

1. Open with what is committed, then what is cut. Leading with cuts puts the whole discussion in the loss frame.
2. Replace "removed" with "deferred to Q_X with a commit date," where that is true. An indefinite deferral reads as a loss. That a dated commitment reduces this is a practitioner heuristic with no cited study; watch how your stakeholders react.
3. Frame trade-offs by the risk avoided ("not building X now removes the platform risk blocking three Q3 items") when that is the real reason.
4. Put numbers on small downside risks of Feature Y. Unquantified small risks tend to be overweighted.

### P8 — Bandits for Adaptive Resource Allocation Across Feature Bets

**When a bandit fits.** Several bets (for example, onboarding, referral, notifications) show weekly outcome signals, and capacity can move between them. In this case, value earned during the quarter matters more than a clean estimate of each bet's effect. Mechanics: [#10](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md).

**When fixed allocation is right.** Keep a fixed split, such as 4/4/4, when you need an unbiased comparison of the bets, when the outcomes that matter are long-horizon or guardrail metrics, or when rewards arrive after the quarter. Adaptive allocation biases naive per-bet estimates. Correct for it before reporting effect sizes ([thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)).

**Stopping.** Do not stop at "P(best) > 0.95 for 3 weeks." P(best) ignores magnitude. Concentrate capacity when the **expected loss of backing the current leader** drops below a declared threshold of caring, and when the EVPI of further exploration drops below the cost of keeping the split for another cycle.

**Guardrails.** Discount observations older than about 4 weeks when bets drift (competitor moves, seasonality). Segment by platform if effects differ by segment. Include context-switching cost in any reallocation.

**PM action.** At the mid-quarter check-in, show the posterior distributions and the expected-loss number (R3). "Expected loss of backing B ≈ 0.015 lift/eng-week" is a defensible basis for reallocating. "Gut feeling" is not.

---

## Anti-Patterns

### A1 — Treating Prioritization Scores as Objective Without Sensitivity Analysis

A rank-3 item scoring 8.4 and a rank-4 item scoring 8.1 are usually tied within the noise of the implicit weights. **Fix:** after every scoring pass, perturb Impact and Confidence by ±1 ordinal step for the top 10. Flag ranks that flip, and report near-ties as "effectively tied; decide on secondary criteria" ([#5](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md)).

### A2 — Running an Experiment When EVPI Is Below the Cost

A notification-copy test: prior 0.80 that the aggressive variant wins, 4 engineer-days plus 3 weeks of traffic, and the winner ships to 100%. EVPI ≈ P(prior wrong) × loss from shipping the worse variant = 0.20 × L. If 0.20 × L is below the full test cost (for example, EVPI of £15K vs a £20K cost), no test design can pay for itself. **Skip it and ship.** This is a valid skip rule, and low-EVPI tests are the main cause of congested experiment queues. **Fix:** require an explicit EVPI when prior concentration is above about 0.75. The reverse does not hold: EVPI above cost only lets the test proceed to an EVSI check (P3, R1).

### A3 — Ignoring Risk Aversion for High-Variance Bets

Bet A: +£300K ±£50K. Bet B: +£320K ±£250K. Each outcome has probability 0.5. Picking B on EV ignores that a £70K outcome may cause a runway or credibility event for a cash-constrained team. Illustrative CRRA with γ = 0.5 (u = √x, applied to incremental ARR, which ignores base wealth):

```
CE(A) = (0.5·√350K + 0.5·√250K)² ≈ £298K
CE(B) = (0.5·√570K + 0.5·√70K)²  ≈ £260K
```

Under this utility, A is preferred despite its lower EV. **Fix:** when an outcome's SD exceeds about 40% of its EV, report the CE next to the EV. Elicit γ from the organisation's actual risk tolerance rather than using a stage-based default ([#6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md), [practical-contract.md](../../foundations-decision-theory/references/practical-contract.md)).

### A4 — Equating Expected Value with Prospect Value Under Loss Aversion

A pricing test has a 60% chance of +5 pp NRR and a 40% chance of −3 pp. EV = 0.6×5 − 0.4×3 = **+1.8 pp**. A prospect-theory value using raw probabilities (no weighting), α = 0.88, and λ = 2.25 (illustrative T&K 1992 median; elicit locally):

```
V = 0.60 × 5^0.88 − 2.25 × 0.40 × 3^0.88
  = 0.60 × 4.12   − 2.25 × 0.40 × 2.63
  = 2.47 − 2.37
  ≈ 0.11   (barely positive)
```

With λ = 1.955 (meta-analytic mean), V ≈ 0.42. The conclusion is the same either way: the bet is EV-positive but close to neutral for someone who feels the NRR loss directly, such as customer success. Their opposition is descriptively predictable. **Fix:** when EV and prospect value diverge a lot, (a) reduce downside exposure (tighter guardrails, smaller initial exposure), or (b) reset the reference point honestly before presenting (P7). Use EV/EU, not prospect value, for the prescriptive decision.

### A5 — Treating Roadmap MCDA as a Single-Stakeholder Ranking

Averaging weights from sales (time-to-market), engineering (scalability), and product (retention) into one vector gives a ranking none of them would defend, and it hides the real trade-off. **Fix:** run MCDA with each stakeholder's weights separately and show the rank vectors side by side. Items in everyone's top 3 are consensus picks. Items ranked top 3 by one stakeholder and bottom 5 by another go to an executive decision, not to averaging.

---

## Recipes

### R1 — Should We Run This Experiment

**When:** before creating a ticket or allocating traffic in any experimentation platform.

1. **Decision check.** If the same action follows a positive and a negative result, EVPI = 0. Stop.
2. **Payoff table.** θ₁ = treatment better (prior p), θ₂ = not better. Ship: +U under θ₁, −D under θ₂. Hold: 0.
3. **EVPI (skip test).** With p = 0.60, U = £180K, D = £40K:
   ```
   EU(ship) = 0.60×180 − 0.40×40 = £92K ;  EU(hold) = 0
   EVPI     = 0.60×180 − 92      = £16K
   ```
   If the full cost (engineering, slots, decision delay) is above £16K, reject without further work.
4. **EVSI of the actual design (approval test).** Model the readout as a binary signal: "significant win" with power 0.80 under θ₁ and α = 0.05 under θ₂. Preposterior:
   ```
   P(win) = 0.6×0.8 + 0.4×0.05 = 0.50 → P(θ₁|win)  = 0.96 → EU(ship|win)  = £171.2K
   P(no)  = 0.50                      → P(θ₁|no)   = 0.24 → EU(ship|no)   = £12.8K  (> 0: still ship)
   EVSI = 0.5×171.2 + 0.5×12.8 − 92 = £0
   ```
   The test never changes the action, so **EVSI = 0 even though EVPI = £16K**. The old shortcut "EVSI ≈ EVPI × power × (1−α)" (≈ £12.2K) would have approved a worthless test. If the downside were D = £120K instead, a null result would flip the action to hold, and EVSI ≈ £24K (EVPI £48K). Compute EVSI per design with [finite-state-calculator.md](../../foundations-decision-theory/references/finite-state-calculator.md).
5. **Risk check.** If a metric regression is painful beyond its cash value, put losses into terminal outcomes on a utility scale and repeat steps 3–4 ([#6](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md), [practical-contract.md](../../foundations-decision-theory/references/practical-contract.md)).
6. **Prior robustness.** If the prior could plausibly be 0.3 instead of 0.6, rerun steps 3–4 at both values. If the decision differs, narrow the prior cheaply (qualitative signal) before designing the test ([#3](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md)).

| Condition | Recommendation |
|---|---|
| EVPI < full cost | Reject; ship the current best action |
| EVSI of this design < full cost | Reject or redesign (sample, MDE, exposure) |
| EVSI > cost, but a risk-adjusted CE of shipping < 0 | Reduce exposure or tighten guardrails |
| EVSI > cost, decision flips across plausible priors | Narrow the prior first |
| EVSI > cost, all checks pass | Approve |

### R2 — Roadmap Ranking with Sensitivity

**When:** quarterly or PI planning with more than 5 items competing for fixed capacity.

1. **Elicit p10/p25/p50/p75/p90** of one primary outcome metric per item, and back each quantile with an assumption ([assumption-test-template.md](../assets/discovery/assumption-test-template.md)).
2. **FSD pre-filter** on that single metric (P4). Record each eliminated item and the item that dominates it.
3. **Option value for platform items** ([#7](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md)). Rough screen with illustrative parameters: 3 unlocked future bets × £80K each × P(success) 0.55 × a 0.70 haircut for execution/timing risk = **£92.4K**. Shift the item's whole distribution by this amount, not only the p50. Replace the screen with a proper option valuation when the item is close to the cut line.
4. **MCDA** on the surviving items ([#5](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md)): weighted sum of option-adjusted p50, strategic alignment, and delivery confidence. Record who set each weight and in which forum.
5. **Weight sensitivity:** perturb each weight by ±20%. Pairs that swap are real trade-offs for leadership to resolve, not scoring artifacts. Example: "Items 3 and 4 swap if the strategic-alignment weight rises 15%."

**Output:** a ranked table with FSD eliminations and reasons, MCDA scores, sensitivity flags, and option-value adjustments. It feeds the key-bets section of [outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md).

### R3 — Adaptive Resource Allocator Across Initiatives

**When:** 3 or more initiatives with weekly outcome signals, and capacity can move between them at a tolerable context-switching cost. First confirm that a bandit fits rather than a fixed split (P8).

1. **Posteriors.** Use a normal–normal model on metric lift per engineer-week. Illustrative Week-6 posteriors: A ~ N(0.29, 0.10), B ~ N(0.44, 0.11), C ~ N(0.23, 0.09). These are approximately consistent with priors N(0.30, 0.15), N(0.35, 0.18), N(0.25, 0.12), observed means 0.28, 0.48, 0.22, and an observation SD of about 0.135. The exact updates give means 0.289, 0.433, and 0.237.
2. **Thompson allocation.** Monte Carlo with 200K draws gives P(A best) ≈ 0.14, P(B best) ≈ **0.81**, P(C best) ≈ 0.05. Allocating 12 engineers in proportion gives about 10/2/0. Keep a minimum crew (for example, 1) on any bet you are not ready to kill, so its signal keeps arriving.
3. **Stop or concentrate** when the expected loss of backing the leader drops below your threshold of caring. Here, E[max − B] ≈ **0.015** lift/eng-week. Also check the skip rule: if the EVPI of further exploration is below the cost of keeping the split another cycle, stop exploring ([thresholds reference](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)). Do not use "P(best) > 0.95" or stochastic dominance between posteriors as the stopping rule.
4. **Risk-averse view (optional, illustrative γ = 1.5).** Use the second-order CRRA approximation CE ≈ μ − (γ/2)·σ²/μ, where σ² here is posterior variance, not outcome variance. This gives CE(A) ≈ 0.264, CE(B) ≈ 0.419, CE(C) ≈ 0.204, so B still leads.
5. **Before reporting effect sizes**, correct for adaptive allocation (P8).

**Output:** a mid-quarter reallocation memo with posteriors, the Thompson allocation, expected loss vs threshold, the EVPI skip check, and the CE view. Use the check-in format in [okr-template.md](../assets/metrics/okr-template.md).

---

## Sources

- Kohavi, R., Tang, D., and Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*. Cambridge University Press. (Experiment design, MDE, power.)
- Leffingwell, D. (2010). *Agile Software Requirements*. Addison-Wesley. (WSJF in the SAFe context.)
- Tversky, A. and Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty." *Journal of Risk and Uncertainty* 5(4). (α = 0.88, λ ≈ 2.25 medians.)
- Brown, A. L., Imai, T., Vieider, F. M., and Camerer, C. F. (2024). "Meta-analysis of Empirical Estimates of Loss Aversion." *Journal of Economic Literature*. (λ is design-dependent; mean ≈ 1.96.)
- Decision-theory textbooks and primary papers (vNM, Savage, Raiffa–Schlaifer, Howard, Saaty, Pratt, Dixit–Pindyck, Kahneman–Tversky 1979, Hadar–Russell, Thompson-sampling tutorials): see [`foundations-decision-theory/data/sources.json`](../../foundations-decision-theory/data/sources.json).
