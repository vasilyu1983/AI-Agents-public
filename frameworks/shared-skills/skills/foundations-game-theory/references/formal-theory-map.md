---
description: Formal game-theory map connecting classical concepts, assumptions, proof obligations, and AI-agent applied primitives.
last_verified: 2026-07-11
status: stable
---

# Formal Theory Map

## Table of Contents

- [Purpose](#purpose)
- [Game Forms](#game-forms)
- [Solution Concepts](#solution-concepts)
- [Mechanism Design and Auctions](#mechanism-design-and-auctions)
- [Information Economics](#information-economics)
- [Cooperative Game Theory](#cooperative-game-theory)
- [Market Design and Matching](#market-design-and-matching)
- [Bargaining](#bargaining)
- [Learning in Games](#learning-in-games)
- [Failure Traps](#failure-traps)
- [Proof Obligations](#proof-obligations)

---

## Purpose

This reference prevents the applied 22-primitives layer from pretending to be complete theory. Use it when a recommendation depends on formal assumptions, equilibrium language, incentive compatibility, or transfer from classical game theory into AI-agent workflows.

The practical rule: name the game form, name the solution concept, state the assumptions, then choose the applied primitive.

## Game Forms

| Form | What It Models | Use It For | Applied Bridge |
|---|---|---|---|
| Normal-form game | Simultaneous strategy choice with payoff matrix | Static routing, pricing, one-shot allocation | #3 auction, #9 Pareto-Nash |
| Extensive-form game | Sequential moves, information sets, histories | Debate, negotiation, staged review, escalation | #8 courtroom, #12 bargaining |
| Bayesian game | Players have private types or beliefs | Screening, hidden quality, uncertain capability | #1 ECON, #5 reputation, #14 credibility |
| Repeated game | Same strategic situation recurs | Partnerships, collusion risk, long-run cooperation | #6 cooperation, #5 reputation |
| Stochastic / Markov game | State evolves based on joint actions | MARL, self-play, policy search | #10 evolutionary search, CFR/PSRO |
| Cooperative game | Coalitions create transferable or non-transferable value | Attribution, revenue split, team value | #4 Shapley, #15 social choice |
| Mechanism design problem | Designer chooses rules under strategic reports | Auctions, allocation, synthesis protocol | #3 auction, #7 synthesis |

## Solution Concepts

| Concept | Meaning | Do Not Use When | Applied Use |
|---|---|---|---|
| Dominant strategy | Best action regardless of others | Payoffs are not specified | Vickrey/VCG-style truthful bidding |
| Nash equilibrium | No unilateral profitable deviation | Players do not have stable strategies/preferences | Static strategic analysis |
| Bayesian Nash equilibrium | Nash equilibrium under private types and beliefs | Beliefs/types are not modeled | ECON-style belief coordination |
| Subgame-perfect equilibrium | Sequential equilibrium robust in every subgame | Information sets are not explicit | Negotiation and staged debate |
| Perfect Bayesian equilibrium | Sequential rationality plus belief consistency | Belief updates are informal | Signaling and screening |
| Correlated equilibrium | Mediator recommends strategies and no one wants to deviate | No trusted recommendation device exists | Role routing, coordination hints |
| Minimax / maximin | Worst-case protection in adversarial games | Problem is not zero-sum or security-critical | Security, red-team planning |
| Pareto efficiency | No one can improve without hurting another | Distribution/fairness is the main question | Pareto frontier mapping |

**Nash existence — what's actually guaranteed**: Nash (1950) proves every *finite* game has at least one equilibrium, but the guarantee is in **mixed strategies**, not pure strategies — Matching Pennies has no pure-strategy Nash equilibrium at all. Existence is proved via Kakutani's fixed-point theorem. For *continuous* action spaces (pricing, bid amounts, resource shares), existence needs additional structure — quasi-concave payoffs and a convex, compact strategy space (Debreu-Glicksberg-Fan conditions) — which does not hold automatically just because the game is well-specified. Do not assert "a Nash equilibrium exists" for #9 or #3 without checking whether the game is finite (mixed-strategy guarantee applies) or continuous with the right convexity (see Convex Markov games below for the occupancy-measure generalization). [PNAS 1950 — doi.org/10.1073/pnas.36.1.48]

**Folk Theorem — what repeated games actually promise**: with sufficiently patient players (discount factor close enough to 1) and (near-)perfect monitoring of past actions, *any* feasible payoff profile that Pareto-dominates every player's minmax ("threat point") payoff can be sustained as a subgame-perfect equilibrium of the infinitely repeated game, via trigger/punishment strategies (Friedman 1971 for the restricted Nash-reversion case; Fudenberg & Maskin 1986 for the general discounting statement). This is the formal grounding behind "reputation sustains cooperation" claims in #5 and #6 — but read it precisely: it proves a **large multiplicity** of sustainable outcomes exists, not that Tit-for-Tat, grim-trigger, or any single strategy is the uniquely correct one. That multiplicity *is* the equilibrium-selection problem (see Failure Traps). Under imperfect *public* monitoring (players see a noisy signal, not raw actions), the theorem needs different, stronger identifiability conditions (Fudenberg, Levine & Maskin 1994) — do not assume the perfect-monitoring folk theorem transfers to noisy-observation settings (e.g., inferring a partner's effort from a proxy metric) without checking those conditions. [RES 1971 — doi.org/10.2307/2296617; Econometrica 1986 — doi.org/10.2307/1911307; Econometrica 1994 — doi.org/10.2307/2951757]

**CCE vs. CE computability**: No-regret learning (regret matching, Hart & Mas-Colell 2000) converges to **coarse correlated equilibrium (CCE)**, not correlated equilibrium (CE). CCE is polynomial-time computable in many game classes (Papadimitriou & Roughgarden 2008, JACM 55(3)); CE requires solving a linear program. In multi-agent LLM settings, CCE is the computationally feasible target — do not claim CE convergence from a regret-matching protocol. [JACM 2008 — doi.org/10.1145/1374376.1374380]

**Convex Markov games (ICML 2025)**: Standard Markov game Nash existence assumes scalar rewards. Convex Markov games (arXiv 2410.16600, ICML 2025) extend Nash existence to agents with convex preferences over occupancy measures — grounding fairness constraints, safety requirements, and behavioral diversity goals in #9 without requiring scalar reward reduction. Gradient descent on an exploitability upper bound approximates equilibria. Domains validated: fair coordination, robotic warehouse safety, repeated normal-form games. Calibration note: exploitability bound may be loose in practice. [ICML 2025 — `icml.cc/virtual/2025/poster/43543`]

## Mechanism Design and Auctions

| Concept | Use It For | Trap |
|---|---|---|
| Incentive compatibility | Truthful reporting is strategically optimal | Requires a concrete utility/payoff model |
| Individual rationality | Participants prefer joining to opting out | Ignoring outside options breaks adoption |
| Revelation principle | Analyze direct truthful mechanisms first | Does not mean every implementation is truthful |
| VCG / Groves mechanisms | Efficient allocation with externality payments | Payments may be impractical or unacceptable |
| Myerson auction | Revenue-optimal single-item auction under private values | Assumptions on distributions and risk matter |
| Revenue equivalence | Any standard auction (first-price, second-price, English, Dutch) that allocates to the highest bidder and gives the lowest-type bidder zero expected surplus yields the same expected seller revenue | Requires risk-neutral bidders, independent private values, symmetric bidder-value distributions — breaks under risk aversion, correlated/common values (winner's curse), bidder asymmetry, or budget constraints (Myerson 1981) |
| GSP / sponsored search | Practical ad auctions | Not generally truthful; bid shading matters; locally-envy-free equilibria exist but are not incentive-compatible in the VCG sense |
| Reserve pricing | Seller-side revenue control | Can reduce welfare and conversion |
| Budget constraints | Bidders cannot express full valuation | Truthful mechanisms can fail under hard budgets |
| False-name bids | Multiple identities submitted by one bidder to manipulate a combinatorial auction | VCG is **not** false-name-proof in combinatorial settings, and no false-name-proof mechanism achieves Pareto efficiency in general (Yokoo, Sakurai & Matsubara 2004); require attested identity before trusting "truthful" claims — see #21 |
| Bilateral-trade impossibility | Single buyer/seller, private values, want efficiency + no subsidy | No mechanism is simultaneously ex-post efficient, budget-balanced, and individually rational (Myerson & Satterthwaite 1983) — some efficiency loss or external subsidy is structurally unavoidable, not a design bug to be fixed away |

## Information Economics

| Concept | What It Catches | Applied Bridge |
|---|---|---|
| Signaling | Costly actions reveal hidden type | Pricing, hiring, partnership credibility |
| Screening | Designer elicits type through menu choices | Packaging, onboarding, qualification |
| Adverse selection | Bad types enter because quality is hidden | Reputation gating, evidence requirements |
| Moral hazard | Participant changes behavior after contract | Monitoring, milestone payments, audit trails |
| Principal-agent problem | Delegated actor has different incentives | Agent autonomy, supplier contracts |
| Cheap talk | Unverifiable messages can be strategically distorted | Debate claims need evidence binding |

## Cooperative Game Theory

| Concept | Use It For | Trap |
|---|---|---|
| Shapley value | Average marginal contribution across coalitions | Exact computation is exponential |
| Core | Allocations no coalition can improve on | Core may be empty |
| Nucleolus | Allocation minimizing coalition dissatisfaction | Requires well-defined coalition values |
| Banzhaf power index | Voting or influence power | Not the same as contribution value |
| Coalition formation | Who should group with whom | Stability differs from efficiency |

## Market Design and Matching

| Concept | Use It For | Trap |
|---|---|---|
| Stable matching | Two-sided matching without blocking pairs | Stability can trade off with welfare |
| Deferred acceptance | Strategy-resistant matching for one side under assumptions | Which side proposes changes outcomes |
| Matching with contracts | Assignment plus terms | Contract space must be manageable |
| Assignment / allocation | Resource allocation with fit scores | Fit scores can encode bias |
| Market thickness | Enough participants for robust matching | Thin markets need manual fallback |

## Bargaining

| Concept | Use It For | Trap |
|---|---|---|
| BATNA | Outside option per party | Weak BATNA means weak leverage |
| ZOPA | Overlap between acceptable ranges | No overlap means no deal, not harder debate |
| Nash bargaining | Split surplus with disagreement point | Requires comparable utilities |
| Rubinstein bargaining | Alternating offers with discounting | Delay costs drive outcomes |
| Credible commitment | Promise or threat believed by others | Empty threats distort analysis |

## Learning in Games

| Concept | Use It For | Trap |
|---|---|---|
| Fictitious play | Best-respond to empirical opponent mix | Can fail outside special classes |
| No-regret learning | Average regret goes to zero | Low regret does not always imply optimal welfare |
| Regret matching | Adaptive path toward correlated equilibrium | Needs repeated comparable decisions |
| CFR | Imperfect-information extensive games | Abstraction choices dominate quality |
| PSRO / double oracle | Population-based MARL and empirical games | Meta-solver choice shapes behavior |
| Self-play | Improve against current/past selves | Can overfit and exploit artifacts |
| Empirical game-theoretic analysis | Estimate payoff table from simulations | Simulation validity is the bottleneck |

**LLM-alignment bridge (INPO, ICLR 2025 Oral)**: No-regret self-play via online mirror descent converges to Nash policy in RLHF settings — framing RLHF as a two-player zero-sum game. INPO (arXiv 2407.00617) demonstrates this without requiring explicit win-rate estimation, achieving state-of-the-art results on AlpacaEval 2.0 and Arena-Hard. Bridges classic learning-in-games theory (#6, #10, #11) with LLM alignment. [ICLR 2025 Oral — `iclr.cc/virtual/2025/oral/31853`]

**Last-iterate convergence (NeurIPS 2025)**: Standard regret-matching (including RM+ used in CFR) achieves only average-iterate convergence — you must average historical strategies, which is impractical with function approximation. Smooth RM+ variants achieve last-iterate convergence to Nash equilibria in extensive-form games [NeurIPS 2025 — openreview.net/forum?id=JzWtqd9CGJ]. The linear-rate-for-restarted-variant result in two-player zero-sum matrix games is from the ICLR 2025 predecessor (arXiv:2311.00676): extragradient RM+ and smooth Predictive RM+ achieve asymptotic last-iterate convergence; combined with restarting, they achieve linear-rate last-iterate convergence. **Boundary**: linear-rate result is for two-player zero-sum matrix games; extension to general-sum or extensive-form games is not yet established — average-iterate remains necessary in general-sum settings.

**CFR lineage**: vanilla CFR (2007) → MCCFR sampling variants (2009) → Deep CFR (ICML 2019, arXiv:1811.00164) → ReBeL: deep RL + search (NeurIPS 2020, arXiv:2007.13544) → Pluribus superhuman poker (Science 2019). Use Deep CFR when the game tree is too large for tabular storage. Use ReBeL when combining search with learned value functions. SmoothRM+ (NeurIPS 2025) provides last-iterate convergence for RM+-based CFR — complements rather than replaces the deep-learning extensions.

## Failure Traps

- **Equilibrium selection**: multiple equilibria can imply opposite actions; state the selection criterion. The Folk Theorem (above) is the formal reason repeated-game and reputation claims are especially prone to this — a large payoff set is sustainable, so naming "the" equilibrium without a selection argument (focal point, precedent, explicit contract) is the single most common overclaim in this space.
- **Tacit collusion**: repeated pricing or bidding agents can coordinate without explicit communication.
- **False-name / sybil manipulation**: a mechanism proven truthful under "one identity per participant" can be defeated by an identity that costs nothing to fabricate — check identity cost before trusting a truthfulness proof (see mechanism-design table above).
- **Participation-constraint failure**: individual-rationality proofs assume the average or modeled outside option; in practice the *highest*-value participants have the best outside options and opt out first, adversely selecting the remaining pool.
- **Goodharting**: mechanisms optimize measured payoff while damaging unmeasured objectives.
- **Strategic manipulation**: once participants know the scoring rule, they may game it.
- **Off-equilibrium threats**: threats matter only when credible under the actual game tree.
- **Preference fiction**: LLM agents do not automatically have stable utility functions.
- **Transfer error**: a result from auctions, MARL, or debate does not transfer without checking assumptions.

## Proof Obligations

Before calling a mechanism "game-theoretic" in production, document:

1. Players: who can act strategically.
2. Actions: what choices each player controls.
3. Information: what each player knows or observes.
4. Payoffs: what each player optimizes.
5. Timing: simultaneous, sequential, repeated, or stochastic.
6. Solution concept: which equilibrium or selection rule is used.
7. Incentive claim: why the desired behavior is a best response.
8. Failure case: what breaks when assumptions fail.
