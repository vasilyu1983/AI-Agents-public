---
description: Applied patterns, scenarios, anti-patterns, and known traps for behavioral-economics foundations.
status: stable
---

# Behavioral Economics Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Ethical pricing page | Need plan choice without dark patterns | Anchoring -> decoy -> choice architecture -> harm test |
| Churn save flow | Need persuasion without blocking cancellation | Loss aversion -> mental accounting -> easy exit |
| Activation onboarding | Need adoption of valuable defaults | Defaults -> social proof -> reduced cognitive load |
| Commitment design | User wants long-term benefit but defers action | Hyperbolic discounting -> commitment device -> reminder |
| Trust repair | User lacks confidence in action | Accurate social proof -> transparent framing |

## Known Traps

- Scarcity must be real, time-bound, and auditable.
- Defaults must be easy to reverse.
- Social proof can backfire when it normalizes the undesired behavior.
- Anchors need a relevant comparison class.
- Decoys are safest when they clarify tradeoffs, not when they hide true value.
- Published coefficients are not product constants; measure locally.
- An AI agent acting for a user is itself a nudge target, and typically a more susceptible one than the user. Audit per model.
- Instructing an agent to avoid dark patterns does not make it resistant — it may detect one and proceed anyway. Constrain scope and gate irreversible actions instead.
- Conversational manipulation (sycophantic agreement, biased framing, privacy probing) is a dark pattern even with a clean interface. The harm test applies to generated turns.

## Edge-over-appetite business models

Where a business monetises *demand for variance* rather than a bias in a retention loop, the primitives stop being a UX technique and become the revenue model itself. This section is the business-model layer for primitive #1.

**The canonical rule:**

> Durable money comes from taking the other side of someone's demand for variance — where the edge is mechanically collected rather than modelled, you pool enough independent draws that your outcome is near-deterministic, the counterparty is better off in their own utility after seeing the odds, no cohort's ruin is your revenue, and you can survive the correlated event that breaks the independence assumption.

**π, not greed, is the variable.** The exploitable primitive across the casino / lottery / insurance class is probability weighting — overweighting of small probabilities — not appetite. See primitive #1's "Probability weighting (π) vs loss aversion (λ)" block: a single greed variable cannot sell both the lottery ticket and the insurance policy, and π is flat for near-certain outcomes, so the edge lives in the tails.

**Greed vs hope.** Lotteries, MLM, and payday lending sell *hope* — downside escape — not upside appetite, and the base self-selects on financial distress. Three consequences that change the model, not just the copy:

- **Churn**: exit is by exhaustion, not satiety. Cohort curves terminate rather than decay, and reactivation targets people who ran out of money.
- **Elasticity**: demand rises in downturns rather than falling with discretionary spend — the opposite of a consumer-discretionary revenue profile.
- **Legal classification**: a base selected on distress is a vulnerable-customer population. Under the UK Consumer Duty the foreseeable-harm test applies to that cohort specifically, not to the average customer.

**Whale concentration inverts the law of large numbers.** Payouts have large n and are near-deterministic; revenue has small n and is not. Track as a *risk* metric, not a growth metric: **share of revenue from users whose spend exceeds plausible disposable income.** Rising top-decile revenue concentration is simultaneously the leading indicator of whale-churn risk and of duty-of-care enforcement exposure — the same chart, read two ways.

### The regulatory response ladder

Regulation arrives in rungs, and distribution usually fails before statute does.

| Rung | Trigger | Dies here | Survives, why |
|---|---|---|---|
| 1 Disclosure (odds display; app-store loot-box odds disclosure; US PFOF disclosure Rule 606; DSA Art. 25 / AI Act Art. 5 on manipulative design) | Information asymmetry is the edge | Models whose only edge is the customer's miscalculation | Insurance, exchanges — publishing the spread doesn't kill the trade |
| 2 Duty of care / suitability (UK Consumer Duty "foreseeable harm"; gambling affordability checks; FTC §5 + ROSCA dark-patterns enforcement) | Profit concentrates in a harmed minority | Whale-dependent models | Broad-book models with diffuse revenue |
| 3 Product reclassification (loot-box actions in Belgium and the Netherlands; CFTC vs prediction markets; PFOF prohibited in the EU and UK) | Category becomes gambling or a derivative | Anything whose defence is "it's not gambling" | Models already inside a licensed category |
| 4 Platform gatekeepers (Apple/Google real-money gambling geo-restrictions; acquirer and card-scheme de-risking, MCC 7995) | Distribution depends on a duopoly plus a card network | Consumer-facing models that can't clear payments | B2B / institutional; bank-to-bank settlement |
| 5 Licensing / state capture | Margin is large, stable, politically visible | Private operators become capped licensees | The state lottery is the terminal form: the state owns the edge and you rent it |
| 6 Ban | Harm legible, customer gets nothing back | Pure extraction with no service story | Nothing survives as designed |

Rung-3 status notes: Belgium has treated paid loot boxes as games of chance since 2018 and the Netherlands has acted under its gambling framework, but enforcement in both is contested — a Dutch penalty against EA was overturned on the ground that an in-gameplay mechanic was not a standalone gambling product. Cite the direction (reclassification is live), not an outcome. PFOF: prohibited in the EU under MiFIR Art. 39a (inserted by Regulation (EU) 2024/791), with member-state transitional carve-outs — check whether any still apply; prohibited in the UK since 2012 — check the FCA's current position before citing it; still permitted in the US subject to SEC Rule 606 disclosure. CFTC vs prediction markets — check current status before stating an outcome.

**Falsifier:** Publish the edge. If disclosure materially reduces demand, the edge was information asymmetry, not a service, and you are on the ladder.

### Founder failure modes

- **Whale concentration read as a cohort chart.** Rising revenue-per-top-decile is presented in the board deck as evidence of monetisation depth. It is a regulatory time bomb: the same concentration is what a duty-of-care regulator uses to establish that profit depends on a harmed minority, and what makes revenue fragile when a handful of accounts stop.
- **Planning for the statute and losing the checkout.** Rung 4 moves in weeks, not legislative cycles. An app-store policy change or an acquirer de-risking decision (MCC 7995 recoding, scheme refusal) removes distribution and payments long before any rung-5 or rung-6 instrument is drafted. Model gatekeeper risk as the near-term threat and statute as the slow one.

**Related:** `../../startup-business-models/references/pricing-patterns.md` § Pattern 11 — Risk-Transfer / Variance-Pooling.

## Exit Checklist

- [ ] The signal is true.
- [ ] The target choice benefits the user by their stated goal.
- [ ] The user can opt out or reverse easily.
- [ ] The copy can be disclosed without embarrassment.
- [ ] The team is measuring retention, refunds, complaints, and trust, not only conversion.
- [ ] If an AI agent acts in or on this flow, its susceptibility was tested and irreversible actions are structurally gated.
