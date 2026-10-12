---
name: foundations-team-theory
description: "Team-theory primitives for cooperative agents: what each subagent sees, when to communicate, aggregation, Shapley credit, coalition topology. Use when organizing subagents."
compatibility: Portable core only.
version: "2.0"
last_validated: 2026-08-14
---

# Team Theory Foundations


10 canonical team-theory primitives, plus an aggregation rule (#11: vote, debate, route, credit assignment, or coalition topology), for *cooperative* multi-agent decision problems — agents share a payoff but each sees a different slice of the world. Game theory handles strategic conflict; decision theory handles solo choice under uncertainty; team theory handles the regime in between, which is exactly where subagents and orchestrated AI agents operate.

## When to Apply

**Apply team-theory when:**
- Multiple agents with **shared payoff** but **partitioned observations** (the canonical subagent setting)
- Designing what each subagent sees vs. what is centralized
- Choosing between centralized orchestrator, decentralized swarm, and hierarchical structures
- Costing communication: is it worth the latency / token / coordination overhead?
- Building agent teams where role specialization matters (each agent owns a different observation lane)
- Multi-agent RL or Dec-POMDP problem framing

**Skip and use simpler alternatives when:**
- Agents have **divergent incentives** → use [foundations-game-theory](../foundations-game-theory/SKILL.md) (mechanism design, auctions, negotiation, collusion). Debate/vote/aggregation for a *shared*-payoff team lives here, in primitive #11 — game theory only if the payoff is genuinely contested.
- Single agent / single-shot decision under uncertainty → use [foundations-decision-theory](../foundations-decision-theory/SKILL.md)
- Communication itself is the bottleneck on a known structure → use [foundations-information-theory](../foundations-information-theory/SKILL.md) (channel capacity)
- The problem is recursive control of a viable system, not a one-shot team decision → use [foundations-cybernetics-vsm](../foundations-cybernetics-vsm/SKILL.md)
- All agents see the same information — information partitioning offers no advantage by itself; compare a single decision-maker baseline while accounting for distinct capabilities and constraints (rule 1 below)
- The delegate's hidden action or effort is the problem (moral hazard, monitoring, contracts) → see [principal-agent-delegation](../agents-subagents/references/principal-agent-delegation.md); team theory assumes a shared payoff

## When Multi-Agent Pays

Check this before reaching for any aggregation mechanism. The full decision table, the aggregation rows and their scope limits are in [references/aggregation-and-multi-agent-evidence.md](references/aggregation-and-multi-agent-evidence.md).

1. **Information dominance.** Without new exogenous signals, a delegated multi-agent network is dominated by a centralized Bayes decision maker with the same information (Ao, Gao & Simchi-Levi, arXiv:2603.26993; abstract-level, theorems not read here). Delegate only when agents bring information the parent lacks (tools, retrieval, independent samples) or relieve a context limit; adding roles over the same evidence does not help. Tran & Kiela (arXiv:2604.02460, multi-hop reasoning only) find single agents match multi-agent systems at equal token budgets, and report multi-agent becoming competitive when single-agent context degrades or compute grows.
2. **Task structure and capability saturation.** Decomposable, parallel-verifiable subtasks are multi-agent candidates; sequential or interdependent planning defaults to one strong agent. Measure the single-agent baseline first: if it is already high, coordination gives diminishing or negative returns (Kim et al., arXiv:2512.08296, which reports the direction flipping by task type).
3. **Vote before debate.** A matched-token-budget majority-vote / self-consistency run is the baseline debate must beat (Choi, Zhu & Li, arXiv:2508.17536).
4. **Equal budgets must be equal.** Count all tokens, including retries and verification; API budget controls can distort single- vs multi-agent comparisons (Tran & Kiela).
5. **Route when one member is stronger.** If one participant is reliably stronger and identifiable, route or weight to it rather than pooling (Pappu et al., arXiv:2602.01011). Trade-off: the consensus-seeking that dilutes experts also makes a team more robust to adversarial members, so keep an independent check.
6. **Which regime each result covers.** Pappu: expert-relevant tasks with a stronger member, so route to the expert. Choi: comparable members on answerable tasks, so a vote is enough. Dochkina (arXiv:2603.28990): a single not-yet-accepted large-scale protocol comparison whose "drop the hierarchy" reading the other results contest, so self-organisation is a candidate to test, not a default.

---

## Quick Reference

| # | Primitive | When to Reach For It |
|---|-----------|----------------------|
| 1 | [Team Decision Problem](references/primitives-overview.md#1-team-decision-problem) | Frame any shared-goal multi-agent setup before designing it |
| 2 | [Information Structure](references/primitives-overview.md#2-information-structure) | Decide what each agent observes; classify centralized / decentralized / partial / nested |
| 3 | [Person-by-Person Optimality](references/primitives-overview.md#3-person-by-person-optimality) | Local optimality check — necessary but not sufficient for team optimum |
| 4 | [Value of Communication](references/primitives-overview.md#4-value-of-communication) | "Should agents share state?" — quantify expected payoff lift vs. cost |
| 5 | [Radner's LQG Theorem](references/primitives-overview.md#5-radners-lqg-theorem) | Classical convex LQG teams admit linear optimal rules under the theorem’s information assumptions |
| 6 | [Witsenhausen Counterexample](references/primitives-overview.md#6-witsenhausen-counterexample) | Why naive linearity fails when one agent's action signals to another |
| 7 | [Information Cost](references/primitives-overview.md#7-information-cost) | Bound observation/communication budgets; rationalize bounded rationality |
| 8 | [Organizational Forms](references/primitives-overview.md#8-organizational-forms) | Pick centralized vs. decentralized vs. hierarchical structure; see #8a (centralize/decentralize decision test) and #8b (team-size/coordination-cost curve) in `references/primitives-overview.md` |
| 9 | [Dec-POMDP / MARL Extension](references/primitives-overview.md#9-dec-pomdp--marl-extension) | Sequential team problems with state dynamics — modern computational form |
| 10 | [Common-Task Condition](references/primitives-overview.md#10-common-task-condition) | Boundary condition: when does shared payoff actually hold? |
| 11 | [Aggregation Rule (Vote / Debate / Route)](references/aggregation-and-multi-agent-evidence.md) | Combine agents' outputs: vote, debate, route to the strongest, calibrated selection; Shapley credit (templates 04, 17); coalition topology (22) |

Full definitions, inputs, outputs, failure modes, and worked examples: [references/primitives-overview.md](references/primitives-overview.md). Primitive #11 (aggregation): [references/aggregation-and-multi-agent-evidence.md](references/aggregation-and-multi-agent-evidence.md).

---

## Anti-Patterns

| Anti-Pattern | Team Theory Diagnosis | Fix |
|---|---|---|
| One central orchestrator reads everything, decides everything | Centralization may duplicate observations and communication cost | Compare centralized and decentralized policies under the actual information structure; invoke Radner-style linear optimality only after verifying the theorem's information and convexity assumptions |
| Each subagent given full system context "just in case" | Information cost (#7) ignored; redundant observations dominate token budget | Partition observations to what each agent's action depends on; redundancy must justify itself |
| Local optimization per subagent declared "team-optimal" | Person-by-person optimality (#3) confused with team optimum; PBPO is necessary, not sufficient | Search unilateral, pairwise and broader deviations to falsify candidate optimality; failed limited searches cannot certify a joint optimum |
| "Add a comms channel between agents" added without payoff analysis | Value of communication (#4) not computed; channel may cost more than it earns | Compute expected payoff with vs. without the channel; if delta < cost, drop it |
| "Multi-agent by default for complex tasks" | Coordination edges can grow quadratically under all-to-all coupling, but realized cost depends on topology; DPI only says post-processing cannot increase information about a target in a Markov chain, not that every routed message loses useful information | Measure the actual communication graph and compare against a single-agent baseline; use DPI only when its random variables and Markov condition are explicit |
| "Assume every text handoff is lossless" | Summaries may omit decision-relevant detail; LatentMAS is a specialized architecture, not a portable guarantee | Verify text/structured-artifact fidelity. Consider latent exchange only with embedding access, compatible representations and task-specific evidence; compare costs and outcomes locally |
| "Default to all-to-all communication between agents" | Dense graphs can increase cost and error propagation on evaluated tasks; no universal optimal sparsity follows | Compare sparse, dense and adaptive candidates under actual dependencies and matched budgets; preserve necessary channels |
| "Put the expert on the team and the team will use them" | Pappu et al. find expertise dilution; consensus-seeking also buys robustness to adversarial members | Compare competence routing and pooling against the best individual locally; also test robustness to unreliable contributions |
| Assume linear/affine policies optimal in non-LQG team | Witsenhausen (#6) shows nonlinear policies can dominate when signaling exists | Map action-dependent observations and information nestedness; consider nonlinear candidates when theorem premises fail, rather than excluding all signaling cases |
| Treat all multi-agent setups as game-theoretic | Common-task condition (#10) holds — agents share a goal — so mechanism-design overhead is wasted | Skip incentive compatibility; design for joint optimization directly |
| Treat all multi-agent setups as team problems | Common-task condition (#10) fails — agents have divergent goals — team theory underestimates conflict | Switch to game theory (auctions, mechanism design) |
| Importing human-team findings (c-factor, psychological-safety inverted-U) as agent-team design rules | These are contested human-team results, not team-theory primitives; they do not transfer to LLM agents without a local test | Use the observation partition (#2) and the aggregation rule (#11). Evidence and hedges live in `startup-operating-system/references/people/team-effectiveness-evidence.md` |
| Hierarchical orchestrator-worker with no information flow back up | Polyarchy/hierarchy structure (#8) chosen by default; loses bottom-up signal that decentralized form preserves | Add upward observation channel or switch to decentralized form; for tasks with parallelizable subtasks at suitable task scale, consider emergent self-organization protocols where agents self-assign roles (contested single preprint, Dochkina 2026; validate locally) |
| "Just add more agents/people, coordination scales for free" | Team-size/coordination-cost curve (#8b): pairwise channels grow ~n(n-1)/2 under high coupling (#8b) | Count how many existing members the new one must (not could) coordinate with; if most, cut coupling first (single owner for shared state) |
| "We are a centralized [org/agent system]" or "we are a decentralized one" applied blanket-wide | Centralize-vs-decentralize is a per-decision judgment (#8a: information compressibility, reversibility, coupling, blast radius of a wrong local call), not a company-wide or system-wide constant | Apply the four-question test per decision class; expect most real orgs and agent systems to be centralized on some decisions (shared state, brand, safety) and decentralized on others (local execution) |

---

## Decision Checklist

- [ ] **Does each agent bring information or capacity the single-agent baseline lacks?** If not, do not split (When Multi-Agent Pays, rules 1-2)
- [ ] **Shared payoff?** If no, exit to [foundations-game-theory](../foundations-game-theory/SKILL.md). If yes, continue (#10)
- [ ] **What does each agent observe?** Map the information structure explicitly (#2)
- [ ] **Are observations redundant?** Trim — observation has cost (#7)
- [ ] **Is communication channel justified?** Compute expected payoff lift; reject if < cost (#4)
- [ ] **Is the communication topology justified by actual dependencies and a matched-budget local comparison?** Moderate sparsity is a tested candidate, not a universal requirement.
- [ ] **Does the team meet the precise Gaussian/quadratic, convexity and information-structure assumptions?** Approximate resemblance alone does not license Radner’s linear-policy result (#5)
- [ ] **Does an action affect later observations, and what information is nested?** Classify the information sets before invoking non-classical results; action dependence alone is insufficient (#6)
- [ ] **Sequential decisions over time with state?** Frame as Dec-POMDP (#9)
- [ ] **Picked an organizational form?** Centralized / decentralized / hierarchical — justify choice against the alternatives (#8)
- [ ] **Tested joint alternatives, not just person-by-person tuning?** Vary joint policies; finite comparisons do not certify a global optimum (#3)
- [ ] **Did the aggregation beat a matched-budget majority-vote / self-consistency baseline?** If not, use the vote; debate or audit only when it beats that baseline or the audit trail is the product (#11)
- [ ] **Does the aggregation rule weight by competence, or does it pool?** If agents differ in task-relevant skill, opinion pooling destroys the expert's advantage; route or weight instead (#11, Pappu et al. 2026). Check the single-best-member baseline before shipping any team design
- [ ] **Human team rather than an agent team?** Out of scope; evidence lives in `startup-operating-system/references/people/team-effectiveness-evidence.md`. Human media findings do not establish LLM transport choices.

---

## Workflow

1. Run When Multi-Agent Pays: does a second agent add information or capacity? If not, stop at one agent.
2. Confirm the common-task condition (#10; exit to game theory if payoffs diverge), then map and cost the information structure (#2, #7) and channels (#4).
3. Pick the organizational form (#8) and the aggregation rule (#11) against a matched-budget single-agent and majority-vote baseline.
4. Check theorem premises before using #5 or #6; otherwise report the best tested joint policy (#3) with searched deviations and uncertainty.
5. For sequential problems with state, frame as Dec-POMDP (#9).

---

## Local Validation Artifact

- [Operational record, worked case and regression checks](references/local-team-comparison.md). Read before translating a mechanism into a deployment recommendation.

## Navigation

- Primitive #11, aggregation rule and the multi-agent evidence layer (moved from `foundations-game-theory`): [references/aggregation-and-multi-agent-evidence.md](references/aggregation-and-multi-agent-evidence.md)
- Aggregation mechanism playbooks (moved from `foundations-game-theory`): debate and audit — [adversarial debate](assets/templates/team-theory/02-adversarial-debate.md), [courtroom-style debate (PROClaim)](assets/templates/team-theory/08-courtroom-proclaim.md), [meta-debate role routing](assets/templates/team-theory/16-meta-debate-routing.md), [reasoning-tree audit](assets/templates/team-theory/13-reasoning-tree-audit.md); voting and consensus — [beyond majority voting](assets/templates/team-theory/18-beyond-majority-voting.md), [radial consensus score](assets/templates/team-theory/19-radial-consensus-score.md), [conformal social choice](assets/templates/team-theory/20-conformal-social-choice.md), [prediction market](assets/templates/team-theory/11-prediction-market.md); coordination and credit — [belief-driven coordination (ECON)](assets/templates/team-theory/01-econ-belief-driven.md), [coalition formation routing](assets/templates/team-theory/22-coalition-formation-routing.md), [Shapley contribution scoring](assets/templates/team-theory/04-shapley-contribution.md), [online Shapley prompt evolution](assets/templates/team-theory/17-online-shapley-prompt-evolution.md)
- Domain-agnostic primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Formal theory map and production boundaries: [references/formal-theory-map.md](references/formal-theory-map.md)
- Patterns, scenarios, and traps for multi-agent / subagent design: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Human-team evidence (owned by `startup-operating-system`; Westrum typology in `software-ux-research`): `team-effectiveness-evidence.md`
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

- [foundations-game-theory](../foundations-game-theory/SKILL.md) — exit here when payoffs diverge (incentives, auctions, collusion, bargaining); it also holds the Shapley worked example and `scripts/game_artifacts.py` self-test that template 04 relies on
- [foundations-decision-theory](../foundations-decision-theory/SKILL.md) — single-agent uncertain choice
- [foundations-information-theory](../foundations-information-theory/SKILL.md) — pricing the channel
- [foundations-cybernetics-vsm](../foundations-cybernetics-vsm/SKILL.md) — recursive viable-system control
- [foundations-grounding-communication](../foundations-grounding-communication/SKILL.md) — *how* agents share state once you decide they should 
- [agents-subagents](../agents-subagents/SKILL.md) — applied subagent patterns
- [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md) — applied multi-agent orchestration

---

## Citation Notes

- Marschak (1955) "Elements for a Theory of Teams." *Management Science* 1(2). Founded the field.
- Marschak and Radner (1972) *Economic Theory of Teams*. Yale. Canonical text.
- Radner (1962) "Team Decision Problems." *Annals of Mathematical Statistics* 33(3). LQG theorem.
- Ho and Chu (1972) "Team Decision Theory and Information Structures in Optimal Control Problems, Part I." *IEEE Trans. Automatic Control*. Partially nested information structures.
- Witsenhausen (1968) "A Counterexample in Stochastic Optimum Control." *SIAM J. Control* 6(1). Nonlinear-dominance result.
- Bernstein, Givan, Immerman, Zilberstein (2002) "The Complexity of Decentralized Control of Markov Decision Processes." *Math. of Operations Research*. Dec-POMDP framing, NEXP-complete.
- Oliehoek and Amato (2016) *A Concise Introduction to Decentralized POMDPs*. Springer.
- Brooks (1975/1995) *The Mythical Man-Month*: qualitative source for the team-size / coordination-cost curve (#8b).
- Human-team citations are owned by `startup-operating-system`: `team-effectiveness-evidence.md`.
- Pappu et al. (2026), "Multi-Agent Teams Hold Experts Back," arXiv:2602.01011. The abstract reports team losses on ML benchmarks and teams failing to match their expert agent. The comparator behind each loss figure sits in the paper's tables; read the table before quoting a magnitude or calling it an oracle gap or a best-member gap.
- Tran & Kiela (2026, arXiv:2604.02460): equal-token-budget comparison of single-agent and multi-agent architectures on multi-hop reasoning, with a Data Processing Inequality argument. Preprint; the paper flags that API budget-control artifacts can inflate apparent multi-agent gains.
- LatentMAS (Zou et al. 2025, arXiv:2511.20639): latent-space inter-agent exchange. Architecture- and benchmark-specific; not a portable guarantee for hosted agents.
- Dochkina (2026, arXiv:2603.28990): emergent self-organisation at scale. Submitted to IEEE Access, not accepted; contested, see rule 6.
- Ao, Gao & Simchi-Levi (2026, arXiv:2603.26993): decision-network formalisation of delegation. Abstract-level reading only.
- Numeric thresholds (cost of communication, observation budgets) are domain-specific. Verify against primary references before using as decision authority.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
