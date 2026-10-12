---
name: foundations-game-theory
description: "Game-theory primitives for divergent incentives: Nash equilibrium, auctions, mechanism design, collusion, bargaining, reputation. Use when modeling strategic play."
compatibility: Claude Code + Codex. Portable core — primitives apply across domains.
version: "2.0"
last_validated: 2026-09-17
---

# Game Theory Foundations


22 numbered applied game-theory primitives for strategic decision systems, backed by a formal theory map. Numbering is kept for stable links: the shared-payoff primitives (#1, #2, #4, #8, #11, #13, #16-#20, #22: aggregation, Shapley credit assignment, coalition routing) now live in `foundations-team-theory`, because nobody in them gains by misreporting. Each applied primitive solves a specific incentive or coordination failure. Primitives are domain-agnostic: the same mechanism that prevents free-riding in agent teams prevents cost-shifting in partnership contracts; the same auction that routes tasks routes ad placements.

For the agent-team applied recipe layer (team.yaml manifest fields, agent-team anti-patterns, agent-team decision checklist, composition recipes for typical agent-team scenarios), see [`agents-subagents/references/game-theory-agent-teams.md`](../agents-subagents/references/game-theory-agent-teams.md).

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Expert Judgment: When the Model Helps vs Misleads](#expert-judgment-when-the-model-helps-vs-misleads)
- [Anti-Patterns](#anti-patterns)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [Navigation](#navigation)

---

## Quick Reference

| Primitive | Domain | Recipe Stub |
|-----------|--------|-------------|
| [Belief-Driven Coordination (ECON)](../foundations-team-theory/assets/templates/team-theory/01-econ-belief-driven.md) | Multi-party teams, distributed analysis, agent teams | Members optimize against beliefs about co-members; reduces redundant work and inter-member chat |
| [Auction-Based Routing](assets/templates/game-theory/03-auction-task-routing.md) | Ad placement, task delegation, resource allocation | Sealed-bid truthful auction; highest-value-per-cost wins |
| [Reputation-Gated Autonomy](assets/templates/game-theory/05-reputation-gating.md) | Supplier qualification, agent oversight, fraud gating | Tiered trust: proven → standard → probationary; oversight inversely proportional |
| [Cooperation and Defection](assets/templates/game-theory/06-cooperation-defection.md) | Partnership design, incentive alignment, compliance | Iterated PD structure; payoff-scale to detect defection tendency |
| [Mechanism Design for Synthesis](assets/templates/game-theory/07-mechanism-design-synthesis.md) | Decision aggregation, voting, policy-making | Evidence-synthesis protocol (no incentive guarantee); dissent is a required section |
| [Pareto-Nash Multi-Objective](assets/templates/game-theory/09-pareto-nash.md) | Product tradeoffs, regulatory vs growth, pricing tiers | Map Pareto frontier; pick dominant options; flag non-dominated set |
| [Evolutionary Coordination Search](assets/templates/game-theory/10-alphaevolve.md) | Algorithm selection, prompt tuning, rule evolution | LLM-mutated program + fitness signal; ShinkaEvolve for sample efficiency |
| [Negotiation ZOPA/BATNA](assets/templates/game-theory/12-negotiation-zopa-batna.md) | Pricing, partnership terms, resource contention | Map BATNA/ZOPA per party; target overlap zone; use interests not positions |
| [Per-Claim Credibility Scoring](assets/templates/game-theory/14-credibility-scoring.md) | Misinformation detection, adversarial content, security | Evidence quality × corroboration weight per claim; isolate high-risk claims |
| [Generative Social Choice](assets/templates/game-theory/15-generative-social-choice.md) | Multi-stakeholder policy, diverse-user product decisions | Maximin selection across candidate outputs; preserve minority-signal coverage |
| [Attested Delegation Contracts](assets/templates/game-theory/21-attested-delegation-contracts.md) | Cross-trust subagent routing, agent marketplaces, external tools | Route by verified capability and bounded contract, not self-claimed quality |

---

## When to Apply

**Apply game-theory primitives when:**
- Multiple agents/teams/users with potentially divergent incentives
- Synthesis where participants could gain by misreporting their claim, confidence, or vote
- Auctions, bidding, mechanism design, or pricing where strategic behaviour exists
- Repeated interactions where reputation, cooperation, or trust evolves
- Cross-trust delegation, dynamic agent pools, or high-stakes act/escalate decisions

**Skip and use simpler alternatives when:**
- Single agent / single-shot task — game theory is about *interactions*, not solo work
- Shared-payoff aggregation (vote, debate, best-of-N, BMV/RCS) where nobody gains by misreporting — use `foundations-team-theory`
- Routine task with high majority-correct rate — a deterministic check or oracle is cheaper
- Hard verification exists (test suite, schema, calculator) — use the oracle, not voting
- Team < 3 members on a low-stakes call — overhead exceeds diversity gain
- Information-only retrieval / pure compression — use foundations-information-theory instead
- Single-system reliability/SLO question — use foundations-reliability-theory or queueing-theory

---

## Primitive Index

The Quick Reference table lists the primitives that stay here. Handled by [foundations-team-theory](../foundations-team-theory/SKILL.md) (shared payoff; live playbooks in `../foundations-team-theory/assets/templates/team-theory/`). Redirect stubs, listed once: [#1](assets/templates/game-theory/01-econ-belief-driven.md), [#2](assets/templates/game-theory/02-adversarial-debate.md), [#4](assets/templates/game-theory/04-shapley-contribution.md), [#8](assets/templates/game-theory/08-courtroom-proclaim.md), [#11](assets/templates/game-theory/11-prediction-market.md), [#13](assets/templates/game-theory/13-reasoning-tree-audit.md), [#16](assets/templates/game-theory/16-meta-debate-routing.md), [#17](assets/templates/game-theory/17-online-shapley-prompt-evolution.md), [#18](assets/templates/game-theory/18-beyond-majority-voting.md), [#19](assets/templates/game-theory/19-radial-consensus-score.md), [#20](assets/templates/game-theory/20-conformal-social-choice.md), [#22](assets/templates/game-theory/22-coalition-formation-routing.md).

---

## Formal Supporting Theory

The 22 primitives are the applied layer, not the whole field. Use [references/formal-theory-map.md](references/formal-theory-map.md) when the task needs formal assumptions, proof obligations, or classical theory coverage.

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Game forms | Need to classify normal-form, extensive-form, Bayesian, repeated, stochastic, or cooperative structure | #6, #9, #10, #12 |
| Solution concepts | Need dominance, minimax, Nash, Bayesian Nash, subgame-perfect, perfect Bayesian, or correlated equilibrium | #6, #9, #10 |
| Mechanism and auction design | Need incentive compatibility, individual rationality, revelation principle, VCG, Myerson, reserves, or bid shading | #3, #7, #21 |
| Information economics | Need signaling, screening, adverse selection, moral hazard, principal-agent framing, or attestation | #5, #7, #12, #14, #21 |
| Cooperative game theory | Need Shapley, core, nucleolus, Banzhaf, coalition formation, or surplus sharing | #6, #15 (Shapley credit assignment and coalition routing: team-theory #4, #22) |
| Market design and matching | Need stable matching, deferred acceptance, matching with contracts, or allocation without prices | #3, #7, #12, #15 |
| Bargaining theory | Need Nash bargaining, Rubinstein bargaining, BATNA/ZOPA, outside options, or alternating offers | #12 |
| Learning in games | Need no-regret, fictitious play, CFR, PSRO, self-play, or empirical game-theoretic analysis — including no-regret Nash policy convergence in RLHF (INPO, ICLR 2025 Oral) and smooth RM+ last-iterate convergence [NeurIPS 2025] | #6, #10 |
| Strategic failure analysis | Need collusion, equilibrium selection, Goodharting, manipulation, or off-equilibrium threats | all primitives |

---

## Expert Judgment: When the Model Helps vs Misleads

Applying a primitive correctly is mechanical. Knowing whether the game-theoretic frame is the right frame at all — and which game — is the actual expert skill. This section is judgment, not a lookup table.

### The equilibrium selection problem

Most interesting games (repeated games especially — see the Folk Theorem in [formal-theory-map.md](references/formal-theory-map.md)) have **many** equilibria, not one. A non-expert computes an equilibrium and reports it as "the" prediction. An expert checks multiplicity first and asks what actually selects among the candidates in this specific situation — precedent, an explicit contract, a public commitment, a focal point, or repeated-play reputation. Reporting "the Nash equilibrium is X" without naming the selection mechanism is a tell that the analysis stopped one step too early.

### Common-knowledge assumptions failing in practice

Nash equilibrium, Bayesian Nash equilibrium, and most mechanism-design proofs assume common knowledge of rationality, of payoffs (or their distribution), and of the rules of the game itself. Real organizations violate all three routinely:

- A "competitor" may be a satisficer bound by an internal OKR or a legacy contract, not a profit-maximizing best-responder — modeling them as rational invites a confidently wrong prediction.
- Bidders or negotiating parties often do not share a common prior on value — private information about downstream use, not risk attitude, is driving the gap.
- LLM agents do not reliably best-respond at all: pro-social bias, framing sensitivity, and authority compliance are documented, repeated deviations from Nash play (see the LLM rationality trap in [patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)). Any incentive-compatibility argument built on "agents best-respond" needs a held-out behavioral check before it is trusted for LLM participants.
- The deviation runs in both directions, and over-truthfulness breaks proofs the same way strategic misreporting does. LLM agents in matching markets reveal preferences truthfully at *higher* rates than human subjects, but truth-telling does not track strategy-proofness — a strategy-proof mechanism did not elicit more truthful reports than a manipulable one (Hoshino, Kitadai & Nishino, arXiv:2606.03030, June 2026). Mechanism-based markets still beat free negotiation on stability and efficiency; the conclusion is that matching theory is a useful but incomplete guide for LLM-agent institutions, not that the guarantees transfer.

**Self-assessment is the binding constraint on agent markets.** Auctions, task routing (#3), and confidence staking (#11) all consume agent self-reports of cost and success probability. MarketBench (Fradkin & Krishnan, arXiv:2604.23897, April 2026) measured six recent models on 93 SWE-bench Lite tasks and found them poorly calibrated on both success rate and token consumption; auctions built from those self-reports diverged from the full-information allocation, and supplying prior-capability context improved calibration only modestly. Before routing real work by agent bids, measure calibration on held-out tasks — an incentive-compatible mechanism fed miscalibrated valuations allocates badly without anyone misreporting strategically.

Habit: before invoking a solution concept, ask "would every party recognize this as the same game I do?" If not, either model it explicitly as a game of incomplete information (Bayesian game) or drop equilibrium language and use the frame as a heuristic only.

### Mapping a business situation to the right game

Non-experts reach for "prisoner's dilemma" or "Nash equilibrium" as a generic label for any tense multi-party situation. An expert asks a short sequence of diagnostic questions before naming a game form or picking a primitive:

1. **Who are the real strategic actors?** Not every interested party is a strategic player — a regulator reacting on a multi-year lag is closer to an exogenous constraint than a player in a weekly pricing game.
2. **One-shot or repeated — do the players expect to meet again?** A single vendor negotiation is a bargaining problem (#12); an ongoing supplier relationship is a repeated game where reputation and folk-theorem-style cooperation are available — analyzing it as one-shot recommends defection that is actually irrational given the relationship's shadow of the future.
3. **Simultaneous or sequential, and who commits first?** Prices set quarterly and observed by competitors before they respond is closer to Stackelberg (sequential, first-mover) than Cournot/Bertrand (simultaneous) — the right model changes the recommendation from "best-respond" to "commit and signal."
4. **Is value created cooperatively or contested?** Cooperative-game tools (Shapley, core) fit attribution and surplus-sharing (Shapley, team-theory #4); competitive tools (auctions, Nash) fit contested allocation (#3, #9). Applying auction logic to a joint-venture split, or Shapley logic to a zero-sum negotiation, produces answers that are precise and wrong.
5. **Is there a credible commitment device?** A threat or promise only constrains behavior if the counterparty believes it will be carried out even against the threatener's own later interest. A pricing "war" threat with no sunk cost or public commitment behind it is cheap talk — treat it as information about intent, not as a binding constraint on the game tree.
6. **Is this actually a game, or an oracle-verifiable fact?** The most common non-expert error in this whole domain is running a debate, auction, or negotiation protocol over a question that has a deterministic answer — a test suite, a contract clause, a calculator. See [Misuse Boundaries](#misuse-boundaries).

### Mechanism-design failure modes that only surface in production

Textbook mechanism design proves *existence* of a truthful, efficient, individually rational mechanism under an idealized participant model. Each row below is a normal way real deployments break that idealization — not an edge case to footnote.

| Failure Mode | What Breaks | Real-World Trigger | Mitigation |
|---|---|---|---|
| **Collusion / bidder rings** | Dominant-strategy truthfulness assumes independent bidders; a ring that agrees off-mechanism to suppress bids and split the surplus defeats VCG and second-price auctions alike | Repeated auctions with a small, stable, identifiable bidder pool | Reserve prices, bidder-pool rotation, anti-collusion monitoring ([AntiCollusionAI](references/patterns-scenarios-traps.md)); detect via a rising profit gain Δ = (π − π_Nash)/(π_monopoly − π_Nash) over many rounds, not a spot price or a fixed markup over cost (LLM pricing agents reach supracompetitive prices: Fish, Gonczarowski & Shorrer, arXiv:2404.00806) |
| **False-name bids** | A single bidder submits multiple identities; VCG is provably **not** false-name-proof in combinatorial auctions, and no false-name-proof mechanism is Pareto efficient in general (Yokoo, Sakurai & Matsubara, *Games and Economic Behavior*, 2004) | Any auction where identity is cheap to fabricate — email-based registration, sybil-able agent pools, unverified marketplace accounts | Require attested identity before bidding (mirrors #21 Attested Delegation Contracts) — price identity verification into the mechanism, not as an afterthought |
| **Participation constraints failing** | Individual rationality assumes the average outside option; when the *highest*-value participants have the best outside options, they opt out first and adversely select the remaining pool | A mechanism designed around expected participants, not the marginal one who is deciding whether to walk | Check IR against the highest-value participant's outside option; In the standard bilateral-trade model with independent private values and overlapping support, Myerson & Satterthwaite (1983) rule out jointly Bayesian incentive-compatible, individually rational, ex-post efficient and budget-balanced mechanisms; state these assumptions and the property relaxed |
| **Budget imbalance** | VCG is efficient and truthful but generally runs a deficit or surplus that must land somewhere | Multi-sided mechanisms with no natural residual claimant | Decide upfront who absorbs the imbalance (platform take-rate, budget-neutral variant, or accept the inefficiency) rather than discovering it at settlement |
| **Computational infeasibility** | Exact VCG for combinatorial allocation requires solving an often NP-hard optimization for the winning allocation and every counterfactual-without-bidder-*i* allocation | Task/resource routing over bundles, not single-item slots | Use approximate/greedy VCG variants and disclose the resulting efficiency loss, or restrict to single-item/separable settings where exact VCG is tractable |
| **Rules stated only in the prompt** | A policy the participants can read but nothing enforces is cheap talk; under optimization pressure agents route around it | LLM participants told "do not collude" in a system prompt, with no state machine, sanction, or audit log behind it | Enforce in the orchestration layer, not the prompt — declare legal states, transitions, and sanctions outside the agents and have a controller apply them (Institutional AI, arXiv:2601.11369, Jan 2026: prompt-only constitutional policy was ineffective; governance-graph enforcement cut severe-collusion incidence in its simulated Cournot markets only) |

**Practical tell**: if a mechanism is called "truthful" or "incentive-compatible" but nobody can name (a) the participation constraint being satisfied, (b) how false identities are prevented, (c) who absorbs budget imbalance, and (d) what enforces the rules other than the prompt, the claim has not actually been checked.

**Communication channels are a collusion dial, not a neutral feature.** Direct seller-to-seller messaging raises collusive tendency in simulated continuous double auctions, with the effect varying by model and modulated by oversight and authority pressure (Agrawal et al., arXiv:2507.01413, 2025). The same channel that reduces conflict in coordination games raises coordinated overpricing in market games — decide which game you are actually running before granting agents a side channel. A related abstract-level 2026 result: two agents set to verify each other over repeated rounds drifted into mutual approval across most models tested, sooner in stronger ones, and less shared history or narrower scope reduced it (arXiv 2609.24967; one environment, unreplicated). Lesson for review loops: the verifier gets a fresh context with no shared log with the author, and verification is paid on outcome, not on agreement.


---

## Anti-Patterns

| Anti-Pattern | Game Theory Diagnosis | Fix |
|-------------|----------------------|-----|
| Unweighted majority vote over a correlated pool in high-stakes aggregation | Correlated errors pass; LLMs share biases | Keep majority/self-consistency as the matched-budget baseline that debate must beat (Choi, Zhu & Li, arXiv:2508.17536); add a reasoning-tree audit (#13, team theory) to trace each claim to evidence |
| Single-objective optimization on a tradeoff decision | Pareto-dominant alternatives go unexamined | Map Pareto frontier (#9) before committing |
| Attribution by seniority or loudness | Free-riding goes undetected; poor performers stay | Shapley marginal-contribution scoring (team-theory #4) |
| Flat trust applied uniformly | High-risk counterparties get same autonomy as proven ones | Reputation-gated tiers (#5) calibrate oversight to track record |
| Adversarial debate forced on genuine compromises | Positions harden; ZOPA never located | Switch to negotiation protocol (#12) when there is a continuous tradeoff |
| Confidence staking without calibration | Overconfident participants dominate synthesis | Self-critique calibration step (CritiCal-inspired) before prediction-market (#11) staking |
| Synthesis suppresses dissent | Minority-correct signal is erased | Dissent required as a section in mechanism-design synthesis (#7) |
| Uniform cooperation assumed in partnerships | Defection undetected until costly | Iterated payoff-scale test (#6) surfaces defection tendency early |
| All members read same context, produce overlapping analysis | Pooling equilibrium — no belief differentiation | Belief-driven coordination (#1) gives each member a unique lane |
| Static debate role assignment regardless of question | Wrong-specialist assignment dominates outcome | Meta-debate role routing (#16) — propose + peer-review picks plaintiff/defense/judge |
| Best-of-N collapsed by majority vote | Calibration and minority-correct signal lost | Shared payoff → Beyond Majority Voting (#18) in [foundations-team-theory](../foundations-team-theory/SKILL.md); conflicting incentives → model the game here |
| Open-ended generation scored by lexical overlap | Semantically equivalent answers split the vote | Shared payoff → Radial Consensus Score (#19) in [foundations-team-theory](../foundations-team-theory/SKILL.md); conflicting incentives → model the game here |
| Consensus treated as permission to act | Wrong agreement becomes automated harm | Validate the candidate and permission independently; a conformal singleton (#20) is only a selection result |
| Routing by self-claimed delegate quality | Strategic or misconfigured delegates attract work | Attested Delegation Contracts (#21) — verify identity/capability and bound authority |
| Large team run as one flat panel | Duplicate work, coalition instability, synthesis overload | Coalition Formation Routing (team-theory #22) — explicit subteams before final synthesis |

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Applying game theory when a deterministic validator exists | Hard oracles beat strategic synthesis | Run tests, compilers, schema checks, SQL, or calculators first |
| Calling a workflow incentive-compatible without payoffs | Truth-telling is not a label; it requires a payoff structure | State the mechanism, utility model, and best-response argument |
| Treating LLM agents as economic agents with stable preferences | Models follow prompts and context, not durable utility functions | Reframe as an operational heuristic unless preferences are explicit |
| Using Shapley (team-theory #4) when contribution is not measurable | Attribution becomes story-telling | Define the value function and approximation before scoring |
| Using debate when disagreement is caused by missing data | Debate amplifies uncertainty instead of resolving it | Retrieve, measure, or ask for missing evidence first |
| Using RCS/BMV when a hard oracle exists | Selection mechanisms can suppress the verifiable answer | Use the oracle, then optionally synthesize explanations; without one, shared payoff → foundations-team-theory, conflicting incentives → game theory |
| Using reputation as proof of claim truth | Strong participants can make local errors | Run per-claim credibility scoring |
| Using equilibrium language without checking equilibrium selection | Multiple equilibria can imply opposite recommendations | List candidate equilibria and the selection assumption |
| Optimizing one metric in a multi-party mechanism | Goodharting shifts harm to unmeasured parties | Add Pareto and stakeholder checks before launch |
| Hiding minority evidence in synthesis | Minority-correct answers are a common failure case | Preserve dissent, runner-up, and outlier evidence |
| Calling a multi-principal synthesis incentive-compatible without designing a payment scheme | Truthful reporting is strictly dominated without payments in multi-stakeholder settings (NeurIPS 2024 proof) | Add affine maximizer (weighted VCG) payment or explicitly scope to a single-principal setting |
| Running an auction over uncalibrated agent self-reports | Allocation quality is bounded by valuation accuracy, not by mechanism truthfulness — miscalibrated bids misallocate even under honest reporting | Measure bid calibration on held-out tasks before routing real work (MarketBench) |
| Encoding mechanism rules as prompt instructions | Declarative prohibitions have no binding force under optimization pressure | Enforce legal states, transitions, and sanctions in the orchestration layer with an audit log |
| Scoring a negotiation agent on deal rate | Frontier models saturate deal rate while diverging widely on surplus extraction, belief calibration, and constraint compliance | Score surplus captured, cue use, and compliance separately (TERMS-Bench) |

---

## Decision Checklist

- [ ] **Routing**: Is the problem multi-option with measurable fit signal? → auction (#3)
- [ ] **Aggregation**: Does synthesis combine claims with varying quality? → reasoning-tree audit (#13) + mechanism-design synthesis (#7)
- [ ] **Trust calibration**: Are participants heterogeneous in track record? → reputation gating (#5)
- [ ] **Tradeoff detection**: Are there multiple incommensurable objectives? → Pareto-Nash (#9) or negotiation (#12)
- [ ] **Adversarial context**: Claims may be injected or manipulated? → per-claim credibility scoring (#14)
- [ ] **Multi-stakeholder output**: Multiple user types with different needs? → generative social choice (#15)
- [ ] **Long-running coordination rule**: Has a measurable quality signal over many runs? → evolutionary coordination search (#10)
- [ ] **Shared payoff** (attribution, debate, best-of-N, act/escalate, topology): use `foundations-team-theory`, not this checklist
- [ ] **Cross-trust delegation**: Delegate can self-claim quality or authority? → attested delegation contract (#21)

---

## Composition Recipes

See [assets/templates/game-theory/README.md](assets/templates/game-theory/README.md) for full domain-scenario stacks.

Quick stacks:

- **Pricing / monetization**: #9 (Pareto-Nash for objective mapping) + #12 (BATNA/ZOPA for negotiation range) + #7 (synthesis dissent required)
  **Inputs:** Competitor price points, own marginal cost, demand elasticity estimate, switching cost for buyer.
  **Rules:** Map Pareto frontier across price/margin/volume objectives (#9); compute BATNA floor and ZOPA ceiling per party (#12); run Bertrand floor check — if product is undifferentiated, price collapses to marginal cost; differentiation (feature, brand, lock-in) is required to hold above floor; synthesis must surface dissenting price band (#7).
  **Outputs:** Price band (floor = marginal cost or BATNA, ceiling = ZOPA upper bound), differentiation requirement to sustain above-floor pricing, dissent note if any Pareto-dominated option was preferred by a stakeholder.

- **Ad bidding / task routing**: #3 (auction routing) + team-theory #4 (Shapley ROI attribution) + #11 (confidence-weighted forecast)
  **Inputs:** Bidder count, valuation distribution (private or correlated), bid visibility (sealed vs. open), budget constraints.
  **Rules:** A sealed second-price auction has truthful bidding as a weakly dominant strategy under the standard independent private-value, quasi-linear, no-budget-constraint model. Otherwise choose the format from private/common/interdependent values, information revelation, dynamics, risk and budget constraints, collusion/shill exposure, and seller objective. Public bid visibility alone does not select first price or imply overbidding. Set a reserve only from a value-distribution model or calibrated market evidence; attribute ROI and calibrate forecasts separately.
  **Outputs:** Mechanism choice with assumptions, reserve rationale if any, expected objective estimate and uncertainty, per-component attribution, and incentive/abuse risks.

  **Worked example — marketplace comparing sealed-bid formats.** Bidders have private values [10, 8, 6, 4]. In a second-price auction, truthful bidding makes the value-10 bidder win and pay 8. A first-price comparison cannot infer equilibrium bids or revenue from these four values alone: bid shading depends on the bidders' value distribution, risk preferences, information, and number of bidders. Estimate those primitives or simulate calibrated bidding behavior before comparing revenue. Publicly revealing live bids also changes the game and invalidates the sealed-bid proof.

- **Security / adversarial context**: #14 (per-claim credibility) + #13 (reasoning-tree audit) + #8 (courtroom for go/no-go)
  **Inputs:** Claim set under review, evidence sources per claim, adversarial threat model (injection vector, attacker capability), go/no-go decision stakes.
  **Rules:** Score each claim independently on evidence quality × corroboration weight (#14); trace every claim to its First Point of Disagreement in the reasoning tree (#13); run courtroom plaintiff/defense/judge only after per-claim scoring — debate over unsupported claims amplifies uncertainty rather than resolving it.
  **Outputs:** Per-claim credibility score, reasoning-tree audit trail, go/no-go recommendation with dissent preserved, list of claims that failed credibility threshold and require retrieval before re-evaluation.

- **Partnership design**: #6 (cooperation-defection payoff test) + #5 (reputation gating) + #12 (ZOPA negotiation)
  **Inputs:** Partner track record (prior-interaction count n, defection incidents), payoff matrix cells for cooperation vs. defection on the proposed arrangement, each party's BATNA and stated interests.
  **Rules:** Infer cooperation risk from the payoff structure, observability of defection, error/noise, continuation probability, and recovery path; interaction count alone is not a trust threshold. Tit-for-tat is a benchmark strategy, not a sufficient contract: accidental defections can trigger retaliation cycles. Use proportionate safeguards (milestones, escrow, audit, cure periods, or clawbacks) when exposure warrants them; locate ZOPA from reservation values and flag when none exists.
  **Outputs:** Recommended safeguards with their trigger, reputation evidence and uncertainty, ZOPA range or no-deal flag, and payoff-scale test result.
  **If an LLM runs the negotiation:** do not accept deal rate as the success metric — it saturates across frontier models while surplus extraction, belief calibration, and constraint compliance still diverge sharply (TERMS-Bench, arXiv:2605.13909, 2026, 13 systems). Score surplus captured against the counterpart's latent payoff, and treat a high close rate with low surplus as conceding, not winning.

- **Cross-trust delegation**: #21 (attested delegation contracts) + #3 (auction routing) + #5 (reputation gating)
  **Inputs:** Delegate pool, attested capabilities, authority boundary, acceptance criteria, failure policy.
  **Rules:** Filter by verified capability before any bidding; never route by self-claimed quality; give the winner a bounded contract; update reputation only from verified outcomes.
  **Outputs:** Eligible delegate set, chosen delegate, delegation contract, typed failure/recovery path, reputation update.

Shared-payoff stacks (multi-party teams, best-of-N, act/escalate, high-frequency prompt evolution, large-team coalitions, full-stack multi-agent applications): see "When Multi-Agent Pays" in [foundations-team-theory](../foundations-team-theory/SKILL.md); add reputation gating (#5) and attested delegation (#21) here only where members can game their standing or self-claim quality.

---

## Navigation

- [Evidence tiers, verified finite-game/Shapley artifacts and uncertainty contract](references/verified-artifacts.md)

- Per-mechanism playbooks: [assets/templates/game-theory/](assets/templates/game-theory/) (one file per primitive)
- Composition guide: [assets/templates/game-theory/README.md](assets/templates/game-theory/README.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Current patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Domain-agnostic primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Sources: [`data/sources.json`](data/sources.json). Source links and verified dates in each per-mechanism file are the canonical evidence tier.

---

## Workflow

1. Identify the strategic failure mode in your system (attribution, routing, synthesis, trust, negotiation, adversarial risk). If actors share a single payoff (no divergent incentives), use team theory instead of a game-theory primitive.
2. Use the [Quick Reference](#quick-reference) table to map failure mode → primitive.
3. Open the per-mechanism playbook in [assets/templates/game-theory/](assets/templates/game-theory/) for the full problem/solution/launch-prompt template.
4. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) or the full [assets/templates/game-theory/README.md](assets/templates/game-theory/README.md) to stack primitives.
5. Check [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) for trap coverage before shipping the mechanism.
6. For agent-team applied recipes (team.yaml manifest fields, agent-team anti-patterns, decision checklist for team launches), load [`agents-subagents/references/game-theory-agent-teams.md`](../agents-subagents/references/game-theory-agent-teams.md).
7. For other domain applied recipes — pricing, paid advertising, CRO, security, market intel — see each domain skill's `references/game-theory-applied.md` (or `game-theory-pricing.md` for `startup-business-models`).

## Related Skills

- [`agents-subagents`](../agents-subagents/SKILL.md) — agent-team applied recipes: team.yaml manifest fields, agent-team anti-patterns, decision checklist
- `marketing-paid-advertising` — paid auction recipes (GSP/VCG, bid shading, budget pacing)
- `startup-business-models` — pricing recipes (VCG, Hotelling, Folk Theorem, signaling)
- `marketing-cro` — experimentation recipes (Thompson, MAB, sequential testing)
- [`software-security-appsec`](../software-security-appsec/references/game-theory-applied.md) and [`qa-security-testing`](../qa-security-testing/references/game-theory-applied.md) — defender/attacker recipes (Stackelberg, honeypots)
- `startup-market-intel` — competitive recipes (Stackelberg, Bertrand, Cournot, Hotelling positioning)

---

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
