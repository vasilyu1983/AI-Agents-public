---
description: Decision theory applied to product management — RICE/WSJF as utility specs, VoI gating before A/B tests, real options for irreversible launches, prospect theory in roadmap framing, MAB for adaptive resource allocation, minimax regret under ambiguous uncertainty, stochastic dominance to skip MCDA. Anchored to 11 primitives from foundations-decision-theory.
last_verified: 2026-05-02
status: stable
---

# Decision Theory Applied: Product Management

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — RICE and WSJF as Utility Specifications](#p1--rice-and-wsjf-as-utility-specifications)
  - [P2 — Minimax Regret for Ambiguous-Uncertainty Decisions](#p2--minimax-regret-for-ambiguous-uncertainty-decisions)
  - [P3 — VoI Gate Before Approving an A/B Test](#p3--voi-gate-before-approving-an-ab-test)
  - [P4 — Stochastic Dominance to Short-Circuit MCDA](#p4--stochastic-dominance-to-short-circuit-mcda)
  - [P5 — WSJF as a Cost-of-Delay Utility Function](#p5--wsjf-as-a-cost-of-delay-utility-function)
  - [P6 — Real Options for Irreversible Launches](#p6--real-options-for-irreversible-launches)
  - [P7 — Prospect Theory in Roadmap Stakeholder Framing](#p7--prospect-theory-in-roadmap-stakeholder-framing)
  - [P8 — MAB for Adaptive Resource Allocation Across Feature Bets](#p8--mab-for-adaptive-resource-allocation-across-feature-bets)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Treating Prioritization Scores as Objective Without Sensitivity Analysis](#a1--treating-prioritization-scores-as-objective-without-sensitivity-analysis)
  - [A2 — Running an Experiment When EVPI Is Below the Cost](#a2--running-an-experiment-when-evpi-is-below-the-cost)
  - [A3 — Ignoring Risk Aversion for High-Variance Bets](#a3--ignoring-risk-aversion-for-high-variance-bets)
  - [A4 — Equating Expected Value with Expected Utility Under Loss Aversion](#a4--equating-expected-value-with-expected-utility-under-loss-aversion)
  - [A5 — Treating Roadmap MCDA as a Single-Stakeholder Ranking](#a5--treating-roadmap-mcda-as-a-single-stakeholder-ranking)
- [Recipes](#recipes)
  - [R1 — Should We Run This Experiment](#r1--should-we-run-this-experiment)
  - [R2 — Roadmap Ranking with Sensitivity](#r2--roadmap-ranking-with-sensitivity)
  - [R3 — Adaptive Resource Allocator Across Initiatives](#r3--adaptive-resource-allocator-across-initiatives)
- [Composition](#composition)
- [Sources](#sources)

---

## Framing Note

Prioritization frameworks (RICE, ICE, WSJF) give PMs the appearance of rigor while hiding the decision-theoretic assumptions underneath. RICE scores are informal expected utility calculations with implicit weights and no risk aversion. WSJF is a cost-of-delay ratio with no acknowledgement of probability mis-calibration. A/B tests are approved or rejected on instinct rather than on whether the value of the resulting information exceeds the cost of running them.

This file applies the 11 primitives from `foundations-decision-theory` to the specific situations that arise in backlog prioritization, roadmap planning, experiment approval, and stakeholder communication. The primitives are domain-agnostic; this file is the PM-specific application layer. For underlying mechanics — definitions, worked derivations, and failure modes — open the linked playbooks.

Tool references throughout are Statsig, Eppo, and OKR planning because they are the platforms and rituals most likely to be in use. The methods generalize to any experiment platform or planning cycle.

---

## Pattern Catalog

### P1 — RICE and WSJF as Utility Specifications

**The PM problem.** A team uses RICE (Reach × Impact × Confidence ÷ Effort) to rank the backlog. The output looks quantitative and defensible. A senior stakeholder asks: "Why does increasing Impact by 1 point matter as much as cutting Effort in half?" No one has an answer.

**What is actually happening.**

RICE is an informal expected utility calculation. The score:

```
RICE = (Reach × Impact × Confidence) / Effort
```

can be rewritten as:

```
RICE ≈ EU(feature) / cost   where EU = Σᵢ pᵢ · u(xᵢ)
```

Here Reach × Confidence is a proxy for the probability-weighted population affected, Impact is a proxy for the utility per affected user, and Effort is the cost denominator. The formula implicitly assumes a linear utility function (no risk aversion), multiplicative outcome aggregation, and equal weight on Reach and Impact.

**Making it rigorous.** State the implicit parameters explicitly before scoring:

| RICE component | Decision-theory mapping | Hidden assumption |
|----------------|------------------------|-------------------|
| Reach | Population-weighted probability | All affected users contribute equally |
| Impact | Utility per affected user | Utility is linear in ordinal scale |
| Confidence | Probability calibration weight | Confidence discounts EU proportionally |
| Effort | Cost normalization | Marginal cost is constant |

When the team disagrees on Impact weights (is a 3 really 3× a 1?), replace ordinal Impact with an elicited CE in ARR or engagement points. This converts a score argument into a utility-curve argument — the right argument to have.

**PM action.** Before the next planning cycle: (a) document what unit of utility Impact represents, (b) confirm that Reach and Impact should be multiplicative (not additive), and (c) run a sensitivity check — perturb Confidence ±0.2 on the top-5 items and see if the ranking holds.

**Primitive links.** EU (#1) → Risk aversion / CE (#6) for high-variance items → MCDA (#5) if criteria are incommensurable.

---

### P2 — Minimax Regret for Ambiguous-Uncertainty Decisions

**The PM problem.** A team must choose a monetization architecture (subscription, usage-based, or hybrid) before they have reliable data on customer willingness to pay, competitive pricing, or API consumption patterns. EU cannot be applied because probabilities are genuinely unknown, not just uncertain.

**When probabilities are contested.**

EU degrades when internal probability disagreement is irreconcilable — it anchors on whoever states their prior most confidently. Minimax regret sidesteps the argument: "Which decision do we most regret having made under the worst realized scenario?"

**Applying minimax regret to architecture choices.** Enumerate scenarios conservatively, build the payoff matrix in ARR or retention points, compute the regret matrix (best-in-scenario minus each option's payoff per scenario), and select the option with the smallest maximum regret.

```
Example: monetization architecture selection

Scenarios:             θ₁ (API-heavy)   θ₂ (seat-centric)   Max regret
Subscription (a₁)     -£400K           +£500K               £700K  ← worst
Usage-based (a₂)      +£600K           -£200K               £700K  ← tied
Hybrid (a₃)           +£200K           +£300K               £400K  ← minimax pick

Hybrid minimizes the maximum opportunity loss.
```

5. Cross-check: once demand signals arrive (even one cohort of usage data), compute EVPI (#4) to determine whether collecting more information before committing is worth the delay.

**PM action.** Use minimax regret in Q3/Q4 planning for any architectural decision where internal probability disagreement exceeds 2× across stakeholders. Document the regret matrix as the explicit output of the planning session, not just the ranked recommendation.

**Primitive links.** Minimax regret (#3) → VoI (#4) for cross-check on whether to wait → Ellsberg/Allais (#9) if ambiguity aversion is known to be present.

---

### P3 — VoI Gate Before Approving an A/B Test

**The PM problem.** The experiments backlog has 12 pending tests. Statsig or Eppo can run them, but slots are constrained. Some tests run for six weeks and produce statistically significant results that change nothing — the winning variant was already the plan.

**Applying EVPI before the test slot is allocated.**

For each proposed experiment, compute the Expected Value of Perfect Information before approving it.

```
EVPI = E_θ[ max_a u(a, θ) ] − max_a E_θ[ u(a, θ) ]
```

If the prior over the experiment outcome already concentrates on one action (i.e., "we're going to ship this regardless of result"), EVPI ≈ 0. A zero-EVPI experiment wastes the slot.

**PM-facing decision logic:**

```
Step 1: Identify the decision the experiment is meant to inform.
        If no decision changes based on the result → EVPI = 0 → kill the experiment.

Step 2: Estimate the two-outcome payoff table (ship vs. hold, per state).
        Use ARR impact or activation-rate impact as the utility unit.

Step 3: Compute EVPI in those units.
        Compare to: (a) experiment engineering cost, (b) opportunity cost of blocked
        experiment slots, (c) time-to-decision delay in sprint weeks.

Step 4: Compute EVSI for the proposed design (account for sample size and
        false-positive rate from the MDE specification).
        EVSI ≤ EVPI always.

Step 5: Approve iff EVSI > total experiment cost.
        Document the EVPI ceiling: "This experiment is worth running only
        if we believe the design can deliver > 60% of perfect information."
```

**Concrete PM example.** The team proposes a six-week test of a checkout flow redesign (cost: 2 engineer-weeks + 6 weeks of experiment slots for ~80K users). The prior is: 65% chance the redesign improves conversion by ≥1 pp, 35% chance it is neutral or negative. Shipping a neutral/negative change costs £0 in direct harm but delays a better alternative by one quarter (£120K opportunity cost).

```
EVPI = E_θ[max_a u] - max_a E_θ[u]
     = [0.65 × (ship, +£200K) + 0.35 × (hold, £0)] - max(0.65×200K + 0.35×(-120K), £0)
     = [£130K + £0] - max(£88K, £0)
     = £130K - £88K
     = £42K

EVSI at 80K users ≈ £28K (60% of EVPI, given MDE and noise estimates).
Experiment cost ≈ £18K (2 eng-weeks + Statsig/Eppo platform cost).

Decision: EVSI (£28K) > cost (£18K) → approve. Net VoI = £10K.
```

**PM action.** Add a VoI gate as the first step of the experiment approval checklist. Any test with an estimated EVPI below experiment cost gets kicked back with the note: "What decision changes based on this result?"

**Primitive links.** VoI / EVPI / EVSI (#4) → EU (#1) for the post-experiment decision → Risk aversion (#6) if the team is averse to false positives.

---

### P4 — Stochastic Dominance to Short-Circuit MCDA

**The PM problem.** The roadmap ranking meeting spends 45 minutes debating whether to weight "strategic alignment" at 0.25 or 0.30 in the MCDA scorecard. Two engineers check out. The PM needs a way to end the argument when it is unnecessary.

**Stochastic dominance as a pre-filter.**

Before running any weighted scoring, check whether one option First-Order Stochastically Dominates (FSD-dominates) all others across the relevant outcome distribution. If it does, no utility specification is needed — every rational decision maker, regardless of risk attitude, prefers the dominant option.

FSD check for PM roadmap items:

```
Option A FSD-dominates Option B iff:
  CDF_A(x) ≤ CDF_B(x) for all x (outcome levels)
  with strict inequality for at least one x

In PM terms: for every performance threshold (retention improvement,
ARR impact, activation lift), the probability that A exceeds the threshold
is weakly higher than B — across all thresholds.
```

**Concrete application.** Represent each roadmap item as a distribution over its projected outcome (e.g., ARR impact) with five quantile estimates (p10, p25, p50, p75, p90). If item X has a higher estimate at every quantile than item Y, X FSD-dominates Y and the MCDA debate about Y is moot.

```
ARR impact distributions (£K):
              p10   p25   p50   p75   p90
Feature X:    80    140   200   310   450
Feature Y:    20    60    110   200   320
Feature Z:    90    160   220   290   400

FSD check:
  X vs Y: X > Y at every quantile → X FSD-dominates Y. Remove Y from MCDA.
  X vs Z: Z > X at p10, p25, p50 but X > Z at p75, p90 → CDFs cross → no FSD.
  → Run MCDA only on {X, Z}. Y is eliminated without weight arguments.
```

**PM action.** Make distribution elicitation (5-point quantile estimates per item) the first step of any roadmap scoring session. Run FSD checks to eliminate dominated items. Only items that survive FSD filtering enter weighted MCDA.

**Primitive links.** Stochastic dominance (#11) as pre-filter → MCDA (#5) for surviving items → Sensitivity analysis (#5 failure modes) on the remaining rank.

---

### P5 — WSJF as a Cost-of-Delay Utility Function

**The PM problem.** A team applies Weighted Shortest Job First (WSJF) to sequence their SAFe backlog:

```
WSJF = Cost of Delay / Job Duration
```

Cost of Delay (CoD) aggregates user-business value, time criticality, and risk reduction. Two items with identical WSJF scores compete for the same sprint. The team has no principled way to break the tie and defaults to whoever advocated most recently.

**Reframing CoD as a utility specification.**

WSJF is a ratio of expected value loss per unit time to cost. CoD is an informal multi-attribute utility function with three components:

| CoD component | EU mapping | Common mis-specification |
|---------------|-----------|--------------------------|
| User-business value | E[u(outcome)] | Scored ordinally; sensitivity ignored |
| Time criticality | Discount rate on utility | Treated as binary ("urgent" or not) |
  | Risk reduction / opportunity enablement | Option value (#7) | Ignored entirely |

The "risk reduction / opportunity enablement" component is a real option — the present value of future flexibility that a delivered item creates. Ignoring it under-values platform investments and over-values features with immediate user value but no compounding.

**Making WSJF rigorous.**

1. Replace ordinal CoD sub-scores with elicited ARR-equivalent values for each sub-component.
2. For items with "opportunity enablement" value, compute the option to expand (#7) — what future bets does this item unlock, and what is their option value given current uncertainty?
3. Run WSJF with cardinal CoD. Ties are broken by risk aversion (#6): prefer the lower-variance item unless the risk premium justifies the variance.

**PM action.** Before the next PI planning or sprint review: map each CoD component to a decision-theory primitive. Require cardinal estimates (not 1–10 ordinal scales) for the top-10 backlog items. Use the option value formula to score platform and infrastructure items that generate future flexibility.

**Primitive links.** EU (#1) for the CoD utility spec → Real options (#7) for opportunity enablement → Risk aversion (#6) for tie-breaking under variance.

---

### P6 — Real Options for Irreversible Launches

**The PM problem.** A feature is ready to ship to 100% of users. The team is 65% confident it will improve activation by 2 pp. The PM wants to ship. The engineering lead asks: "What if it hurts power users?" The PM answers: "We'll roll back if it does." But rollback takes three weeks and requires a hotfix deploy. The feature is not reversible at the speed the PM implied.

**Pricing irreversibility.**

Any feature launch with non-trivial rollback cost should be treated as an irreversible commitment. Committing to 100% rollout destroys the option value of staged rollout — the option to observe early performance, update beliefs, and either expand or abandon before full exposure.

```
Option-adjusted launch value:

NPV_full_launch_now = NPV_feature − Option_value_of_staged_rollout

Option value of staged rollout = f(σ, T, K)
  σ = uncertainty about activation impact (standard deviation of outcome distribution)
  T = time available to observe before full commitment (weeks to feature freeze / next release)
  K = cost of staged rollout vs. full rollout (engineering overhead)
```

**Staged rollout as a compound option.**

Each stage of a staged rollout (1% → 10% → 50% → 100%) is an option to expand:

- Stage 1 (1%): buy the option to observe real-world behavior before committing.
- Stage 2 (10%): exercise only if Stage 1 data is above the kill threshold. Each stage's exercise is conditional on passing the previous stage.
- Abandonment option: if activation drops below the kill criterion at any stage, revert. The salvage value is "avoided harm to the full user base."

**Concrete PM application.**

Before the launch decision: estimate σ (activation range between p10 and p90), T (weeks available before full commit), and K (extra cost of staged vs. full rollout). If σ is high (range > 4 pp) and K is low (< 1 engineer-day), staged rollout dominates full launch on option-adjusted NPV.

**Kill criterion as the exercise threshold.** The kill criterion from [assets/prioritization/kill-criteria-template.md](../assets/prioritization/kill-criteria-template.md) defines the threshold below which the option to abandon is exercised. A kill criterion that is never consulted until post-launch is an option that was purchased but never priced into the launch decision.

**PM action.** For any feature with rollback cost > 1 day of engineering work, require a staged rollout plan and document the kill criterion before approving launch. Price the option: "We are spending K in extra engineering to preserve the option to abandon, which is worth V given our uncertainty σ."

**Primitive links.** Real options (#7) → EU (#1) for each stage decision → Risk aversion (#6) for the CE of the abandonment option.

---

### P7 — Prospect Theory in Roadmap Stakeholder Framing

**The PM problem.** The PM presents the quarterly roadmap to the executive team. The roadmap drops Feature X (a sales-requested item) and adds Feature Y (a platform investment). The sales stakeholder reacts negatively to losing Feature X, even though Feature Y has a higher RICE score. The PM presents EU-optimal reasoning; the stakeholder escalates anyway.

**What is actually happening.**

The sales stakeholder is not evaluating the roadmap under EU. They are evaluating it under prospect theory (#8): the loss of Feature X is weighted more heavily than the gain of Feature Y, because losses loom larger than gains (λ ≈ 2.25). The PM's EU-optimal ranking is correct prescriptively but fails descriptively as a communication tool.

**Using prospect theory to reframe without deception.**

Prospect theory predicts that the reference point determines whether an outcome is experienced as a loss or a gain. The PM controls the reference point in how the roadmap is presented.

| Reference frame | Stakeholder experience | Prospect theory prediction |
|----------------|----------------------|---------------------------|
| "We dropped Feature X" | Loss frame: -1 feature | High negative weight (λ × loss aversion) |
| "We protected the top 3 sales requests and added a platform investment" | Gain frame: +3 sales + platform | Lower negative weight (diminishing sensitivity in gain domain) |
| "Feature X moved to Q4; here is the commitment" | Delayed gain frame | Loss aversion reduced; certainty of future gain increases |

**Concrete roadmap framing rules derived from prospect theory.**

1. Never open with what is cut. Open with what is committed. Losses presented first anchor the entire discussion in the loss domain.
2. Convert "removed from roadmap" to "deferred to Q_X with a commit date." Prospect theory research shows that a certain future gain ("ships Q4") reduces loss aversion vs. an indefinite deferral.
3. When presenting trade-offs, frame as risk reduction, not feature elimination: "By not building Feature X now, we reduce the platform risk that would have blocked three features in Q3." This reframes the reference point from "sales got fewer features" to "team avoided a costly risk."
4. Probability weighting: stakeholders overweight small probabilities of large negative outcomes. If Feature Y carries any risk of regression to existing users, proactively quantify it — do not leave it as an unspecified fear. Overweighted fears drive more opposition than calibrated ones.

**PM action.** Before any roadmap presentation with a stakeholder who has a known loss: (a) identify their reference point, (b) map which items fall in their gain vs. loss domain, (c) reframe the narrative to minimize the number of items presented as losses, and (d) provide certainty signals (commit dates, kill criteria) on deferred items.

**Primitive links.** Prospect theory (#8) → Ellsberg/Allais (#9) if the stakeholder exhibits ambiguity aversion about platform risk → MCDA (#5) if weight elicitation is needed to show the trade-off transparently.

---

### P8 — MAB for Adaptive Resource Allocation Across Feature Bets

**The PM problem.** Three product bets are running in parallel: a new onboarding flow (Bet A), a referral loop redesign (Bet B), and a notifications engine (Bet C). Engineering capacity is 12 engineers. The allocation was set at the start of the quarter (4/4/4) and has not changed despite early signals that Bet B is outperforming.

**Framing as a multi-armed bandit.**

Each bet is an arm with an unknown reward distribution (conversion rate improvement, activation lift, or ARR impact). The fixed 4/4/4 allocation is equivalent to running a fixed-allocation experiment — it ignores the exploration value already captured in early results and foregoes the exploitation of the apparently superior arm.

**Thompson sampling for quarterly resource allocation.**

```
1. Initialize priors: Beta(α₀, β₀) for each bet's success rate.
   Use pre-quarter estimates: Bet A prior mean 0.30, Bet B prior mean 0.35, Bet C prior mean 0.25.

2. After Week 4: observe interim outcomes (activation lift per engineer-week invested).
   Update posteriors:
     Bet A: 4 eng-weeks × observed lift → Beta(α_A, β_A)
     Bet B: 4 eng-weeks × observed lift → Beta(α_B, β_B)
     Bet C: 4 eng-weeks × observed lift → Beta(α_C, β_C)

3. Thompson sampling allocation for Week 5–8:
   For each reallocation decision, sample θ_A, θ_B, θ_C from posteriors.
   Allocate capacity proportionally to the probability each arm is currently best.
   Example: P(Bet B is best) = 0.62 → 7 engineers on Bet B, 3 on Bet A, 2 on Bet C.

4. Stopping rule: when P(arm X is best) > 0.95 across 3 consecutive weeks,
   reallocate all remaining capacity to X. Deprioritize other bets.
```

**Guardrails for PM application.**

- Non-stationarity: bet performance can change mid-quarter (competitor move, seasonal shift). Use a sliding-window prior that discounts observations older than 4 weeks.
- Contextual structure: if bet performance varies by user segment (mobile vs. web), use contextual Thompson sampling segmented by platform.
- EVPI cap: before the reallocation, compute EVPI (#4) to check whether the information value of continued exploration justifies the opportunity cost of not concentrating on the best arm. If EVPI is below the cost of another two weeks of split allocation, stop exploring.

**PM action.** At the mid-quarter check-in (Week 6–7), present the posterior distributions over each bet's impact to the leadership team. Use the Thompson sampling posterior to justify a reallocation rather than advocating based on narrative alone. "P(Bet B is best) = 0.72 after 6 weeks" is a defensible basis for reallocating 3 engineers; "I have a gut feeling" is not.

**Primitive links.** MAB / Thompson sampling (#10) → VoI / EVPI (#4) for the exploration budget cap → Stochastic dominance (#11) as the stopping criterion when one arm dominates → Risk aversion (#6) for CE adjustment if the team penalizes downside variance.

---

## Anti-Pattern Catalog

### A1 — Treating Prioritization Scores as Objective Without Sensitivity Analysis

**Description.** The team runs RICE scoring, produces a ranked list, and treats the ranking as settled. The item at rank 3 scores 8.4 and the item at rank 4 scores 8.1. These are presented in the roadmap as a definitive ordering.

**Why it fails.** RICE scores embed weights (Impact multiplier, Confidence discount, Effort denominator) that were never explicitly elicited and are sensitive to small changes. A 0.1-point change in the Confidence estimate of rank-3 item can reverse the ordering. The MCDA failure mode — hidden weights, no sensitivity analysis — applies directly (#5). The team believes they are looking at an objective ranking; they are looking at an artifact of implicit weight choices.

**Concrete damage.** Items that lose on a sensitivity-unstable score get deprioritized based on spurious precision. Engineers spend time on rank-3 items that would be rank-5 under any of three plausible Confidence re-estimates.

**Fix.** Run a sensitivity check after every prioritization pass: perturb the Impact and Confidence scores ±1 ordinal step for the top-10 items and observe which rank positions are stable and which are fragile. Flag fragile rankings explicitly in the roadmap document. For items within 1 score point of each other, report the range as "effectively tied — decision by secondary criteria" rather than a definitive rank.

---

### A2 — Running an Experiment When EVPI Is Below the Cost

**Description.** The team proposes an A/B test to compare two notification copy variants (aggressive push vs. gentle nudge). The prior is: 80% confident that the aggressive variant performs better. The test requires 4 engineer-days to instrument and 3 weeks of traffic. The decision is: whichever variant wins ships to 100% of users.

**Why it fails.** With a prior of 0.80 on one option, the optimal action (ship the aggressive variant) is robust — it is the same regardless of what the test reveals with overwhelming probability. EVPI for a near-certain prior is approximately:

```
EVPI ≈ P(prior is wrong) × (loss from choosing incorrectly)
     = 0.20 × (cost of shipping the suboptimal variant for one quarter)
```

If this is £15K and the experiment costs £20K in engineer time and opportunity cost, EVPI < cost. The experiment is a net loss.

**Concrete damage.** The three-week experiment delay costs the team experiment slots that could gate decisions where EVPI is genuinely high. Running low-EVPI tests is the main mechanism by which experimentation pipelines become congested.

**Fix.** Apply the VoI gate from Pattern P3 to every proposed experiment before it enters the queue. Any experiment with a prior concentration above 0.75 on one action requires an explicit EVPI calculation before approval. If EVPI < cost, move directly to the shipping decision and use the saved capacity for higher-EVPI tests.

---

### A3 — Ignoring Risk Aversion for High-Variance Bets

**Description.** The PM is choosing between two growth bets for the quarter: Bet A (expected +£300K ARR, low variance: ±£50K) and Bet B (expected +£320K ARR, high variance: ±£250K). The team picks Bet B because it has higher expected ARR.

**Why it fails.** For a startup below PMF or a product team with a cash-constrained runway, the utility function is not linear. A £70K shortfall may trigger a runway event or a forced pivot; a £370K upside on a bet that did not pan out is symmetric in probability but not in consequences. The certainty equivalent of Bet B under any reasonable concave utility is lower than its EV:

```
u(x) = √x (CRRA γ = 0.5 proxy)

CE(Bet A) ≈ √(300K - 50K×risk_weight) → close to £300K for low variance
CE(Bet B): EU(Bet B) = 0.5×√570K + 0.5×√70K ≈ 0.5×755 + 0.5×264 ≈ 510
           CE = 510² ≈ £260K

Under risk aversion, Bet A (CE ≈ £290K) dominates Bet B (CE ≈ £260K)
despite lower EV.
```

**Concrete damage.** Teams that prioritize by EV without risk adjustment systematically over-invest in high-variance bets and under-invest in stable compounding bets. This pattern is most damaging in the quarters closest to a funding event or a retention crisis.

**Fix.** For any bet with an outcome standard deviation exceeding 40% of the EV, compute the certainty equivalent using a CRRA utility function with γ calibrated to the organization's effective risk tolerance. For startups pre-Series B, γ between 0.5 and 1.5 is typical. Report the CE alongside the EV in the planning brief.

---

### A4 — Equating Expected Value with Expected Utility Under Loss Aversion

**Description.** A PM calculates that a pricing experiment has a 60% chance of improving NRR by 5 pp and a 40% chance of reducing it by 3 pp. Expected value: 0.6×5 − 0.4×3 = 1.8 pp expected NRR improvement. The PM presents this as clearly worth pursuing.

**Why it fails.** The EU calculation assumes a linear utility function. Under prospect theory (#8), losses are weighted more heavily than equivalent gains (λ ≈ 2.25). The prospect-theory value of this bet is:

```
V = w(0.6) × v(+5pp) + w(0.4) × v(-3pp)
  ≈ 0.60 × (5)^0.88 − 2.25 × 0.40 × (3)^0.88
  ≈ 0.60 × 4.55 − 2.25 × 0.40 × 2.78
  ≈ 2.73 − 2.50
  = 0.23  (barely positive under prospect theory)
```

The EU calculation gives 1.8 pp. The prospect theory value gives 0.23 — a near-zero net prospect value even though EV is positive. In practice, the customer success team (who experience the NRR loss directly and immediately) will oppose the experiment regardless of the PM's EV math because they are evaluating it as a mixed-domain gamble with loss aversion.

**Concrete damage.** PMs who present EV-positive but PT-negative decisions as obvious approvals face escalations from stakeholders who are correctly (descriptively) applying loss aversion. The result is conflict that could be avoided by either framing the bet differently or pricing the loss-aversion cost into the experiment design.

**Fix.** For any experiment with a meaningful downside probability, compute both the EV and the prospect-theory value. If they diverge by more than 30%, either (a) redesign the experiment to reduce downside exposure (tighter guardrail metrics, smaller initial exposure), or (b) reframe the reference point before presenting it (Pattern P7).

---

### A5 — Treating Roadmap MCDA as a Single-Stakeholder Ranking

**Description.** The PM runs a weighted MCDA on roadmap items using weights agreed in a planning meeting attended by three stakeholders: engineering lead, sales lead, and product lead. The output is presented as "the team's ranking."

**Why it fails.** MCDA weights embed stakeholder preferences. Three stakeholders with different utility functions over different objectives produce different optimal rankings under any honest weight elicitation. Averaging their preferences into a single weight vector suppresses legitimate disagreement about what the product should optimize for. The result is a ranking that satisfies no one's actual preferences and obscures the trade-off.

The MCDA failure mode here (#5): sales weights time-to-market heavily, engineering weights scalability, product weights retention. A single averaged weight vector is a political compromise that satisfies none of their actual utility functions.

**Concrete damage.** Roadmap commitments built on averaged weights are ones no stakeholder would defend individually. Accountability diffuses; post-mortems cannot attribute decisions to anyone.

**Fix.** Run MCDA with each stakeholder's explicit weights separately. Present the resulting rank vectors side by side. Items that appear in the top 3 of every stakeholder's ranking are robust consensus picks. Items that appear in the top 3 of one and the bottom 5 of another are genuine trade-offs requiring executive decision, not averaging. Use the rank divergence as the input to the stakeholder alignment conversation, not the averaged output.

---

## Recipes

### R1 — Should We Run This Experiment

**Goal.** Determine whether a proposed A/B test generates more value than it costs, using formal VoI logic before committing experiment infrastructure and traffic.

**When to use.** Any proposed experiment in Statsig, Eppo, or equivalent platform, before the ticket is created and traffic allocated.

**Stack.**

**Step 1: Identify the decision the experiment informs** (primitive #4, see [04-value-of-information.md](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md)).

Ask: "What action changes if the experiment result is positive? What action changes if it is negative?" If the answer is "the same action either way," EVPI = 0. Stop here.

**Step 2: Build the payoff table.**

```
States:   θ₁ = treatment wins (p = prior confidence)
          θ₂ = control wins or neutral (p = 1 - prior)

Actions:  a₁ = ship treatment
          a₂ = ship control / hold

Payoffs (in ARR impact or activation rate points):

          θ₁              θ₂
a₁        +U (win)        -D (ship a worse variant)
a₂         0 (foregone)    0 (correct hold)
```

**Step 3: Compute EVPI.**

```
prior = 0.60, U = £180K (win), D = £40K (loss if worse variant ships)

EU(ship)  = 0.60×180K − 0.40×40K = £92K   ← current best action
EU(hold)  = £0

EVPI = E_θ[max_a u] − EU(ship)
     = (0.60×180K + 0.40×0) − 92K
     = 108K − 92K = £16K
```

**Step 4: Compute EVSI for the proposed design.**

Account for the experiment's false-positive and false-negative rates given the proposed MDE and sample size. EVSI ≤ EVPI. A rough approximation:

```
EVSI ≈ EVPI × (1 − β) × (1 − α)

where β = Type II error rate (miss rate), α = Type I error rate (false positive)

At 80% power (β = 0.20) and α = 0.05:
EVSI ≈ £16K × 0.80 × 0.95 ≈ £12,160
```

**Step 5: Apply EU and risk-aversion check** (primitive #1, primitive #6).

If the team is risk-averse to metric regression (D is a painful loss), compute CE of the post-experiment decision using CRRA γ calibrated to the team's variance tolerance. If CE of "ship" < 0, prefer hold even when EU > 0.

**Step 6: Minimax regret cross-check** (primitive #3, see [03-minimax-regret.md](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md)).

If the team is uncertain about the prior (e.g., "we think 60% but it might be 30%"), construct a regret matrix over two prior scenarios. Check whether the experiment decision is the same under both scenarios. If it is, the decision is robust. If not, gather the minimum required information to narrow the prior before committing to the experiment design.

**Decision gate.**

| Condition | Recommendation |
|-----------|---------------|
| EVSI < experiment cost | Reject; ship the current best action directly |
| EVSI > experiment cost, CE < 0 under risk aversion | Reduce experiment exposure or redesign guardrails |
| EVSI > experiment cost, minimax regret conflict | Resolve prior uncertainty first (qualitative signal) |
| EVSI > experiment cost, all checks pass | Approve experiment |

---

### R2 — Roadmap Ranking with Sensitivity

**Goal.** Produce a roadmap ranking that is defensible under stakeholder weight variation, filters dominated items without running MCDA, and prices real-option value for platform bets.

**When to use.** Quarterly roadmap planning, PI planning, or any session where more than five items compete for a fixed capacity across multiple objectives.

**Stack.**

**Step 1: Elicit 5-point outcome distributions per item** (primitive #11, see [11-stochastic-dominance.md](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md)).

For each candidate item, gather p10, p25, p50, p75, p90 estimates of the primary outcome metric (ARR impact, activation lift, retention improvement). Use the [assets/discovery/assumption-test-template.md](../assets/discovery/assumption-test-template.md) format for backing each quantile estimate with an assumption.

**Step 2: Run FSD pre-filter.**

Compare each item's outcome distribution to every other item. Remove FSD-dominated items (those where another item's distribution is weakly higher at every quantile). This eliminates the bottom tier without any weight elicitation.

```
For items X, Y, Z:
If X_p10 ≥ Y_p10 AND X_p25 ≥ Y_p25 AND ... AND X_p90 ≥ Y_p90:
  Y is FSD-dominated by X → remove Y from MCDA.
```

**Step 3: Price option value for platform and infrastructure items** (primitive #7, see [07-real-options.md](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md)).

For any item classified as "platform" or "technical foundation," add an option-value component to its distribution:

```
Option value = (number of future bets unlocked) × (estimated ARR per bet) × (option probability)
             × (discount factor for uncertainty)

Example: Platform logging infrastructure unlocks 3 future A/B tests.
  Each test expected to deliver £80K ARR if positive (probability 0.55).
  Option value = 3 × £80K × 0.55 × 0.70 (discount for uncertainty) = £92.4K

Add £92.4K to the platform item's p50 distribution estimate.
```

**Step 4: Run MCDA on the surviving items** (primitive #5, see [05-multi-criteria.md](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md)).

Use weighted sum on criteria: outcome distribution p50 (adjusted for option value), strategic alignment, and delivery confidence. Document weight provenance — who assigned each weight and in what forum.

**Step 5: Sensitivity analysis on MCDA weights.**

Perturb each weight ±20% and observe rank-reversals. Any pair that reverses under ±20% perturbation is a genuine trade-off requiring stakeholder alignment, not a scoring artifact. Present rank-reversals explicitly:

```
"Items 3 and 4 swap rank if strategic-alignment weight increases by 15%.
This reflects a real trade-off between near-term retention and platform strategy.
We recommend resolving this at the leadership layer, not in the scoring model."
```

**Output artifact.** A ranked roadmap table showing: FSD-filtered items (with reason for elimination), surviving items with MCDA scores, sensitivity flags, and option-value adjustments. Anchors to [assets/roadmap/outcome-roadmap.md](../assets/roadmap/outcome-roadmap.md) key-bets section.

---

### R3 — Adaptive Resource Allocator Across Initiatives

**Goal.** Reallocate engineering capacity across parallel product initiatives mid-quarter based on posterior evidence rather than original plan, using MAB logic with an EVPI cap and CE adjustment for risk-averse teams.

**When to use.** Any quarter where 3+ initiatives are running in parallel with measurable weekly or bi-weekly outcome signals, and where re-allocation is feasible (engineers can shift focus without prohibitive context-switching costs).

**Stack.**

**Step 1: Frame as a multi-armed bandit** (primitive #10, see [10-multi-armed-bandit.md](../../foundations-decision-theory/assets/templates/decision-theory/10-multi-armed-bandit.md)).

Each initiative is an arm. Reward signal: weekly activation lift, ARR contribution, or primary metric movement per engineer-week invested. Use a continuous-outcome variant of Thompson sampling (normal-normal conjugate update for continuous rewards):

```
Priors (pre-quarter estimates):
  Bet A: Normal(μ=0.30, σ=0.15)
  Bet B: Normal(μ=0.35, σ=0.18)
  Bet C: Normal(μ=0.25, σ=0.12)

After Week 6 observations (metric lift per eng-week):
  Bet A observed: 0.28 → posterior Normal(μ≈0.29, σ≈0.10)
  Bet B observed: 0.48 → posterior Normal(μ≈0.44, σ≈0.11)
  Bet C observed: 0.22 → posterior Normal(μ≈0.23, σ≈0.09)

Thompson sampling (1000 draws per arm):
  P(Bet B is best) ≈ 0.62  →  7 engineers on Bet B
  P(Bet A is best) ≈ 0.28  →  3 engineers on Bet A
  P(Bet C is best) ≈ 0.10  →  2 engineers on Bet C

Stopping rule: when P(arm X is best) > 0.95 across 3 consecutive weeks,
reallocate all remaining capacity to X.
```

**Step 2: Apply EVPI cap to the exploration budget** (primitive #4, see [04-value-of-information.md](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md)).

Before authorizing continued split allocation, check whether the expected value of continued exploration exceeds the opportunity cost of concentrating on the current best arm:

```
EVPI at Week 6 = E[value if we knew the true best arm now] − E[value under current posterior allocation]

If EVPI < (cost of 2 more weeks of split allocation):
  Stop exploring. Reallocate fully to the arm with the highest posterior mean.
  In the example: Bet B (posterior mean 0.44 after Week 6 update) → full allocation.
```

**Step 3: Check stochastic dominance as a hard stopping criterion** (primitive #11, see [11-stochastic-dominance.md](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md)).

If one arm's posterior distribution FSD-dominates all others — i.e., P(Bet B > x) ≥ P(Bet A > x) for all x, with strict inequality at some x — reallocate fully immediately regardless of the EVPI calculation. FSD dominance is a criterion that holds for all utility functions; no further exploration is needed.

**Step 4: Apply certainty-equivalent adjustment for risk-averse teams** (primitive #6, see [06-risk-aversion.md](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md)).

If the team has low variance tolerance (e.g., close to a board review or funding milestone), compute CE using the second-order CRRA approximation:

```
CE ≈ E[x] − (γ/2) × Var[x] / E[x]    (CRRA γ = 1.5 for a risk-averse team)

At Week 6 posteriors (γ = 1.5):
  CE(Bet A) ≈ 0.29 − (0.75 × 0.01 / 0.29) ≈ 0.26
  CE(Bet B) ≈ 0.44 − (0.75 × 0.012 / 0.44) ≈ 0.42
  CE(Bet C) ≈ 0.23 − (0.75 × 0.008 / 0.23) ≈ 0.20

Even under risk aversion, Bet B dominates. Weight allocation by CE rather than
posterior mean when the team penalizes downside variance.
```

**Output artifact.** A mid-quarter reallocation memo with: posterior distributions per initiative, Thompson sampling allocation recommendation, EVPI cap calculation, FSD check result, and CE-adjusted allocation for risk-averse scenario. Anchors to [assets/metrics/okr-template.md](../assets/metrics/okr-template.md) mid-quarter check-in format.

---

## Composition

The patterns and recipes above compose across the product planning lifecycle:

| Stage | Pattern / Recipe | Primitives |
|-------|-----------------|------------|
| Backlog scoring | P1: RICE/WSJF as utility specs | #1, #5, #6, #7 |
| Pre-experiment approval | P3: VoI gate | #4, #1, #6 |
| Pre-experiment approval | R1: Should we run this experiment | #4, #1, #6, #3 |
| Roadmap planning | P4: Stochastic dominance pre-filter | #11, #5 |
| Roadmap planning | P5: WSJF as CoD utility | #1, #7, #6 |
| Roadmap planning | R2: Roadmap ranking with sensitivity | #11, #5, #7, #5 sensitivity |
| Architecture / monetization decisions | P2: Minimax regret | #3, #4, #9 |
| Launch decisions | P6: Real options for irreversible launches | #7, #1, #6 |
| Stakeholder communication | P7: Prospect theory in roadmap framing | #8, #9, #5 |
| Mid-quarter resource reallocation | P8: MAB adaptive allocation | #10, #4, #11, #6 |
| Mid-quarter resource reallocation | R3: Adaptive resource allocator | #10, #4, #11, #6 |

**Primitive coverage in this file:**

| Primitive | Where used |
|-----------|-----------|
| #1 Expected Utility | P1, P3, P5, P6, R1, R2 |
| #2 Bayesian Decision | (embedded in Thompson sampling in P8, R3) |
| #3 Minimax Regret | P2, R1 |
| #4 Value of Information | P3, A2, R1, R3 |
| #5 MCDA | P1, P4, A1, A5, R2 |
| #6 Risk Aversion / CE | P1, P5, P6, P8, A3, R1, R3 |
| #7 Real Options | P5, P6, A3 (implicitly), R2 |
| #8 Prospect Theory | P7, A4 |
| #9 Ellsberg / Allais | P2 (ambiguity trigger), P7 |
| #10 Multi-Armed Bandit | P8, R3 |
| #11 Stochastic Dominance | P4, R2, R3 |

**Cross-cutting rule.** Every recipe closes with a sensitivity or robustness check — either a weight perturbation (MCDA), a minimax regret cross-check, or an EVPI ceiling. A PM analysis that produces a ranking or a go/no-go without a sensitivity step is not ready to present at a planning review.

---

## Sources

1. von Neumann, J. and Morgenstern, O. (1944/1947). *Theory of Games and Economic Behavior*. Princeton University Press. — EU axioms and vNM theorem.
2. Savage, L. J. (1954). *The Foundations of Statistics*. Wiley. — Minimax regret, subjective probability.
3. Raiffa, H. and Schlaifer, R. (1961). *Applied Statistical Decision Theory*. Harvard University Press. — EVPI, EVSI, Bayesian decision.
4. Howard, R. A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics* 2(1). — VoI foundation.
5. Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill. — AHP, MCDA weights.
6. Pratt, J. W. (1964). "Risk Aversion in the Small and in the Large." *Econometrica* 32(1–2). — CARA, CRRA, certainty equivalent.
7. Dixit, A. K. and Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press. — Real options, option to defer and abandon.
8. Kahneman, D. and Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica* 47(2). — Loss aversion, probability weighting, reference points.
9. Russo, D. J., Van Roy, B., Kazerouni, A., Osband, I., and Wen, Z. (2018). "A Tutorial on Thompson Sampling." *Foundations and Trends in Machine Learning* 11(1). — Thompson sampling.
10. Hadar, J. and Russell, W. R. (1969). "Rules for Ordering Uncertain Prospects." *American Economic Review* 59(1). — Stochastic dominance.
11. Kohavi, R., Tang, D., and Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*. Cambridge University Press. — Experiment design, MDE, power, Statsig and Eppo context.
12. Leffingwell, D. (2010). *Agile Software Requirements*. Addison-Wesley. — WSJF definition and SAFe context.
