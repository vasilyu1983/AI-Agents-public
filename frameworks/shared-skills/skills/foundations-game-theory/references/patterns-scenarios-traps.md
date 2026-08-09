---
description: April 2026 operating patterns, scenario stacks, anti-patterns, and known traps for game-theory primitives in strategic decision systems.
last_verified: 2026-05-02
status: stable
---

# Patterns, Scenarios, and Known Traps

## Table of Contents

- [April 2026 Posture](#april-2026-posture)
- [Core Patterns](#core-patterns)
- [Scenario Stacks](#scenario-stacks)
- [Anti-Patterns](#anti-patterns)
- [Known Traps](#known-traps)
- [Classical Theory Gaps](#classical-theory-gaps)
- [Source Rules](#source-rules)

---

## Current Posture

Treat classical game theory as the durable mechanism layer and 2025-2026 LLM-agent papers as applied evidence. Auctions, Shapley attribution, repeated games, Pareto reasoning, BATNA/ZOPA, and mechanism design are stable concepts; ECON, AgentAuditor, BMV, RCS, dynamic role assignment, and credibility scoring are current applied patterns that still need task-level validation before production use.

Do not present a paper result as a universal benchmark. Accuracy deltas, token reductions, and sample-efficiency claims transfer only after a held-out eval on the target workflow.

## Core Patterns

| Pattern | Use When | Prefer |
|---|---|---|
| Fit auction | Multiple actors could perform the work and fit is context-dependent | #3 auction routing, then #16 role routing if a debate follows |
| Marginal contribution accounting | Shared output makes credit assignment ambiguous | #4 Shapley, approximated for teams larger than 6 |
| Evidence-first synthesis | Multiple agents produce claims with uneven support | #13 reasoning-tree audit + #7 synthesis |
| Trust by track record | Counterparties differ in reliability across runs | #5 reputation gating, fed by #14 per-claim credibility |
| Debate on divergence | Claims conflict and no hard oracle exists | #2 adversarial debate or #8 courtroom debate |
| Forecast weighting | Predictions need calibrated confidence | #11 prediction-market / confidence betting |
| Multi-objective selection | There is no single scalar winner | #9 Pareto-Nash, then #12 negotiation if parties can trade concessions |
| Best-of-N selection | Multiple generated answers need selection | #18 BMV for discrete answers, #19 RCS for open-ended answers |

## Scenario Stacks

| Scenario | Primary Stack | Trap to Check |
|---|---|---|
| Agent-team routing | #3 auction -> #16 meta-debate -> #7 synthesis | Static team choice that ignores role fit |
| High-stakes claim verification | #14 credibility -> #13 reasoning tree -> #8 courtroom | Majority vote over correlated hallucinations |
| Pricing or packaging | #9 Pareto-Nash -> #12 BATNA/ZOPA -> #7 dissent-preserving synthesis | Optimizing only revenue and hiding retention risk |
| Paid bidding | #3 auction -> #11 forecast weighting -> #4 Shapley attribution | Treating last-touch or highest bid as true value |
| Partnership design | #6 cooperation/defection -> #5 reputation -> #12 negotiation | Assuming cooperation before incentives are explicit |
| Open-ended synthesis | #19 RCS -> #13 audit of outliers -> #7 final synthesis | Discarding semantic outliers that carry minority-correct evidence |
| Discrete best-of-N | #18 BMV -> #11 calibration -> #13 audit if stakes are high | Confidence-weighting uncalibrated agents |
| Long-running optimization | #10 evolutionary search -> #9 frontier check -> #4 contribution signal | Evolving without a stable fitness function |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Safer Pattern |
|---|---|---|
| Majority vote as default synthesis | Correlated LLM errors become consensus | #13 reasoning-tree audit or #18 BMV |
| Debate for every decision | Cost rises and agents can converge through persuasion rather than evidence | Trigger debate only on material divergence |
| Single-agent judge as final truth | Judge inherits hidden bias and may reward fluency | Pair judge output with evidence audit and dissent |
| Shapley on large teams exactly | Exact Shapley is exponential | Use DAG/topology approximations and sample audits |
| Reputation as claim truth | Reliable members still produce local hallucinations | Score claims independently with #14 |
| RCS for security or edge cases | Centroid selection suppresses useful outliers | Keep outliers and route them to #13 |
| Prediction market without calibration | Wagers become confidence theater | Run #11 calibration and track historical error |
| Evolutionary search before evals | Search optimizes noise | Build a benchmark and fitness metric first |

## Known Traps

- **Primary-source drift**: secondary articles may describe an April 2026 result, but the canonical source may be a different arXiv paper. Store both only when each has a clear role.
- **Mechanism-name inflation**: do not call an applied recipe "truthful" or "incentive-compatible" unless the implemented payoff structure makes truth-telling the best response.
- **Cross-domain transfer**: an agent-team result does not automatically apply to pricing, security, or legal review. Re-run the decision checklist per domain.
- **Token-cost blind spot**: debate, meta-debate, RCS, BMV, and evolutionary search add overhead. Use them where expected error cost exceeds coordination cost.
- **Oracle bypass**: if a compile, test, SQL check, or deterministic validator exists, use it before game-theory synthesis.
- **Correlated proposer pool**: BMV, RCS, debate, and prediction markets all weaken when every candidate uses the same model, prompt, retrieval set, and temperature.
- **Untracked minority evidence**: every mechanism that suppresses an answer must preserve the runner-up, outlier, or dissent in the final artifact.

### Pricing-algorithm tacit collusion

When two or more autonomous pricing agents (Q-learning, RL, or LLM-based) can observe each other's prices, they can converge to supra-competitive equilibria without any explicit communication — documented empirically by Calvano et al. (AER 2020) for Q-learning agents and surveyed for LLM-specific contexts in AntiCollusionAI (KBS 2026, already in sources).

**Detection signal**: Run two agents against each other for 500 rounds on a simulated market with known marginal costs. Compute average markup over the Bertrand (marginal-cost) floor. Signal: markup exceeds floor by >10% in the final 100 rounds without coordination instructions.

**Mitigation**:
- Randomize pricing cadence to break synchronised observation cycles.
- Add hard price-floor enforcement in the orchestration layer.
- Audit agent reward objectives: any objective that rewards relative performance over a competitor (rather than absolute margin) is structurally collusion-prone.
- For LLM-based pricing: apply AntiCollusionAI governance controls — sanctions, leniency detection, monitoring, and market-design constraints.

**Applies to**: Any system where ≥2 autonomous pricing or bidding agents observe each other's outputs over repeated rounds, including ad-auction bidding agents, dynamic pricing APIs, and marketplace fee-setting agents.

**Sources**: Calvano et al. AER 2020 (`CalvanoAER2020`), AntiCollusionAI KBS 2026 (`AntiCollusionAI`).

---

### LLM rationality trap

LLMs do not reliably best-respond in strategic games. Documented deviations from Nash equilibrium:
- **Pro-social bias**: LLMs cooperate even when defection is the dominant strategy (NegotiationArena 2024, IJCAI-25 survey).
- **Framing sensitivity**: word choice shifts equilibrium play — the same payoff matrix elicits different strategies depending on framing (resource allocation vs. negotiation vs. trading).
- **Authority compliance**: LLMs follow coordinator or system-prompt instructions even when subgame-irrational (GameBench 2024).

**Consequence**: Mechanism incentive-compatibility proofs assume rational best-response. If the agents are LLMs, this assumption requires empirical validation on the target task — it does not transfer automatically.

**Detection**: Before production deployment, run a held-out payoff-matrix test on the target task class. Compare LLM play to theoretical Nash. Flag deviations >15% from Nash expected payoff as requiring mechanism redesign.

**Mitigation**:
- Use mechanism primitives (#3 auction, #7 synthesis) that are robust to irrational agents (dominant-strategy incentive-compatible mechanisms reduce reliance on best-response).
- Pair with #14 credibility scoring to detect agents that consistently deviate from stated strategies.
- Do not use prediction-market (#11) or cooperative game (#6) primitives in high-stakes settings without a prior behavioral eval.

**Sources**: NegotiationArena arXiv:2402.05863 (`NegotiationArena`), GameBench arXiv:2406.06613 (`GameBench`), IJCAI-25 survey arXiv:2503.16424 (`IJCAI-25`).

---

## Classical Theory Gaps

If a task asks for "complete game theory", load [`formal-theory-map.md`](formal-theory-map.md) before applying the 22 primitives. The applied primitives intentionally do not replace formal treatment of normal-form games, extensive-form games, Bayesian games, equilibrium refinements, matching, contract design, signaling/screening, principal-agent problems, correlated equilibrium, bargaining theory, or no-regret learning.

Do not add a new applied primitive when the missing item is a theory concept. Add it to the formal map unless it has an operational playbook, trigger condition, scenario stack, and source-backed failure mode.

## Source Rules

- Prefer primary papers, official docs, and stable canonical references in `data/sources.json`.
- Keep practitioner articles out of the source registry unless they are explicitly marked as secondary implementation commentary.
- Recheck papers with arXiv IDs, dates, and abstracts before copying numeric performance claims.
- Mark any April 2026 claim as current only for the verified date in the file frontmatter.
