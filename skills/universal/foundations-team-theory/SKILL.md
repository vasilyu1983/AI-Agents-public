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
- All agents see the same information — information partitioning offers no advantage by itself; compare a single decision-maker baseline while accounting for distinct capabilities and constraints

## When Multi-Agent Pays

Check this before reaching for any aggregation mechanism. The full decision table, the aggregation rows and their scope limits are in [references/aggregation-and-multi-agent-evidence.md](references/aggregation-and-multi-agent-evidence.md).

- **Task structure first.** Decomposable, parallel-verifiable subtasks are multi-agent candidates; sequential or interdependent planning defaults to one strong agent. Kim et al. (arXiv:2512.08296) report relative changes from +80.8% to −70.0% against a single-agent baseline across task types.
- **Vote before debate.** A matched-token-budget majority-vote / self-consistency run is the baseline debate must beat (Choi, Zhu & Li, arXiv:2508.17536).
- **Equal budgets must be equal.** Count all tokens, including retries and verification; API budget controls can distort single- vs multi-agent comparisons (Tran & Kiela, arXiv:2604.02460).
- **Route when one member is stronger.** If one participant is reliably stronger and identifiable, route or weight to it rather than pooling (Pappu et al., arXiv:2602.01011; see Fact-Checking for the exact figures).

---

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Navigation](#navigation)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

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
| 11 | [Aggregation Rule (Vote / Debate / Route)](references/aggregation-and-multi-agent-evidence.md) | How to combine multiple agents' outputs into one: vote, debate, route to the strongest, or a calibrated selection rule; also Shapley credit assignment (templates 04, 17) and coalition topology (22). Covers the shared-payoff aggregation templates formerly indexed in `foundations-game-theory` |

Full definitions, inputs, outputs, failure modes, and worked examples: [references/primitives-overview.md](references/primitives-overview.md). Primitive #11 (aggregation): [references/aggregation-and-multi-agent-evidence.md](references/aggregation-and-multi-agent-evidence.md).

---

## Primitive Index

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | Team Decision Problem | Modeling cooperative agents as either a single decision-maker (loses decentralization value) or as strategic players (overstates conflict) |
| 2 | Information Structure | Agents observing redundant signals; missing observations; uncosted communication assumed free |
| 3 | Person-by-Person Optimality | Local-optimum trap: each agent optimal given others' fixed rules, but the joint policy is suboptimal |
| 4 | Value of Communication | "Add a Slack channel between agents" with no expected-payoff justification; channel may cost more than it earns; inter-agent message routing also degrades information efficiency via Data Processing Inequality even at zero explicit channel cost |
| 5 | Radner's LQG Theorem | Reinventing optimization for LQG teams when a closed-form linear rule exists |
| 6 | Witsenhausen Counterexample | Assuming linear policies are optimal when an agent's action carries signaling content |
| 7 | Information Cost | Designing perfect-observation agents in a world where observation has latency, token, and money cost |
| 8 | Organizational Forms | Defaulting to a central orchestrator when a decentralized or hierarchical form would dominate |
| 9 | Dec-POMDP / MARL Extension | Treating each timestep as a fresh team problem; ignoring history and state |
| 10 | Common-Task Condition | Calling a system a "team" when payoffs actually diverge — game theory regime, not team regime |
| 11 | Aggregation Rule (Vote / Debate / Route) | Unweighted vote over a correlated (same-family) pool; debate used without a baseline it must beat; pooling when routing to the strongest agent would do better; no credit signal for which member contributed; a team topology fixed by habit rather than fit |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Marschak–Radner team theory | Need normative framing of cooperative multi-agent decisions | #1, #2, #3, #4, #5, #8 |
| Decentralized stochastic control | Action of one agent affects information of another | #6, #9 |
| Information economics | Need to cost observation and communication | #4, #7 |
| Organization economics | Compare centralized hierarchy, decentralized markets, polyarchy | #8 |
| Dec-POMDP and MARL | Sequential team problems with state dynamics | #9 |
| Mechanism design boundary | Where shared payoff breaks down | #10 (then exit to game-theory) |
| Social choice and forecast aggregation | Combine member outputs into one answer: vote, weight, route, or calibrated selection | #11 |
| Cooperative game theory (Shapley value) | Credit assignment for a shared payoff; exact cost grows as 2^N, so approximate for larger teams | #11 (templates 04, 17, 22) |

See [references/primitives-overview.md](references/primitives-overview.md) for the formal-theory map and theorem statements.

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
| "Put the expert on the team and the team will use them" | Pappu et al. find expertise dilution in controlled tasks; their ML benchmark synergy gaps use an oracle bound, distinct from the best fixed individual | Compare competence routing and pooling against the best individual locally; also test robustness to unreliable contributions |
| Assume linear/affine policies optimal in non-LQG team | Witsenhausen (#6) shows nonlinear policies can dominate when signaling exists | Map action-dependent observations and information nestedness; consider nonlinear candidates when theorem premises fail, rather than excluding all signaling cases |
| Treat all multi-agent setups as game-theoretic | Common-task condition (#10) holds — agents share a goal — so mechanism-design overhead is wasted | Skip incentive compatibility; design for joint optimization directly |
| Treat all multi-agent setups as team problems | Common-task condition (#10) fails — agents have divergent goals — team theory underestimates conflict | Switch to game theory (auctions, mechanism design) |
| Importing human-team findings (c-factor, psychological-safety inverted-U) as agent-team design rules | These are contested human-team results, not team-theory primitives; they do not transfer to LLM agents without a local test | Use the observation partition (#2) and the aggregation rule (#11). Evidence and hedges live in `startup-operating-system/references/people/team-effectiveness-evidence.md` |
| Hierarchical orchestrator-worker with no information flow back up | Polyarchy/hierarchy structure (#8) chosen by default; loses bottom-up signal that decentralized form preserves | Add upward observation channel or switch to decentralized form; for tasks with parallelizable subtasks at suitable task scale, consider emergent self-organization protocols where agents self-assign roles — reported advantages in particular evaluated settings need matched local validation (Dochkina 2026) |
| "Just add more agents/people, coordination scales for free" | Team-size/coordination-cost curve (#8b): pairwise coordination channels grow ~n(n-1)/2 with team size under high coupling; the marginal member's coordination cost can exceed their contribution (Brooks's Law) | Before adding a member/agent, count how many existing members it must (not could) coordinate with; if most, cut coupling first (modularize, assign a single owner for shared state) rather than adding capacity |
| "We are a centralized [org/agent system]" or "we are a decentralized one" applied blanket-wide | Centralize-vs-decentralize is a per-decision judgment (#8a: information compressibility, reversibility, coupling, blast radius of a wrong local call), not a company-wide or system-wide constant | Apply the four-question test per decision class; expect most real orgs and agent systems to be centralized on some decisions (shared state, brand, safety) and decentralized on others (local execution) |

---

## Decision Checklist

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

## Composition Recipes

### Designing a subagent team for a research task

_Context_: Orchestrator needs to dispatch N subagents on a multi-source research task with a shared answer goal.

1. Verify common-task condition (#10): all subagents and orchestrator share the payoff "produce one accurate answer." If not, exit to game-theory.
2. Map information structure (#2): which sources/files/tools does each subagent observe? Avoid redundant assignment. For human-in-the-loop teams: the temporal ordering of observation matters — simultaneous presentation of human and AI outputs outperforms sequential (human-first then AI) on average (npj Artificial Intelligence 2025, N=52 clinical studies). Design observation lanes with this moderator in mind. **CTP conditions (Hemmer et al. 2024, EJIS 2025)**: human-AI complementarity — performance exceeding either agent or human alone — requires either (a) information asymmetry (human has local context AI lacks) or (b) capability asymmetry (human provides judgment on novel cases AI cannot handle). These are candidate performance-complementarity conditions, not permission to remove oversight: human participation may be required for authority, rights, accountability or safety even without an accuracy gain. Test local performance and preserve those duties.
3. Cost observations (#7): each tool call has token + latency cost. Compare the joint value and cost of observation bundles. Diminishing marginal value requires assumptions; complementary observations can have increasing value.
4. Compute value of communication (#4): does mid-task chatter between subagents lift expected payoff more than its cost? Test communication when observations, constraints or intermediate decisions interact; late synthesis is a candidate for low coupling, not a theorem-backed default.
5. Pick organizational form (#8): compare single-agent, split-and-merge, centralized and hierarchical candidates at matched total budgets. Use split-and-merge for separable work only when aggregation and shared constraints remain adequate; LQG analogy supplies no default.
6. Compare bounded joint-policy candidates (#3). An improving pairwise deviation disproves team optimality but does not establish prior person-by-person optimality; report the best tested candidate and uncertainty, with no global certificate.

### Choosing between orchestrator-led and swarm forms

_Context_: A product team must pick between a single planner agent that delegates everything (centralized) and a peer-to-peer agent network (decentralized).

1. Invoke #5 only for an explicitly modeled problem satisfying the exact quadratic, Gaussian, convexity and information-structure premises of the applicable theorem. Similarity to LQG gives no upper bound for LLM architectures; otherwise compare matched-budget candidates.
2. Cost the communication channel: orchestrator-led requires every observation to flow up and every decision to flow down. Decentralized requires only local observation but needs convergence on the synthesis.
3. Apply #8: high information cost and low coupling motivate a decentralized candidate; low information cost and high coupling motivate a centralized candidate. Compare them locally; these heuristics do not prove dominance. For parallelizable subtasks where feasible, add a fourth candidate: emergent self-organization with minimal structure (sequential protocol + autonomous role assignment). Reported scaling results are architecture-, benchmark- and budget-dependent; do not infer a universal four-agent threshold or hierarchy disadvantage. Justified by Dochkina (2026, arXiv:2603.28990) and CARD (Wu et al., ICLR 2026).
4. Worked example: code review across 5 files. Files are independent (no signaling, low coupling). A decentralized candidate (5 parallel reviewers + final aggregator) may reduce duplicated observations; compare total cost and verification quality against an orchestrator-led baseline. Code review across one tightly-coupled module: signaling is high (one agent's finding changes another's interpretation); test centralized or hierarchical coordination rather than assuming a winner.

### Sizing the orchestrator's context budget

_Context_: How much should the orchestrator observe vs. push down to subagents?

1. Apply #7: every token in the orchestrator's context has cost. Give the orchestrator the information needed for assignment, synthesis and verification, including domain evidence when its conclusions depend on that evidence.
2. Apply #2: start with task graph, roster and status, then add decision-relevant object-level evidence and provenance needed to check worker claims.
3. Anti-pattern: orchestrator reads all source files and then asks subagents to summarize them — observation paid for twice. Fix: delegate first-pass source reading, then return claims with source locations, assumptions and counterevidence; the orchestrator reads underlying contents where synthesis or verification needs them.

### Designing subagent context as an information-structure problem (AI app builders)

_Context_: You are building a multi-agent AI application and must decide what context (system prompt, retrieved docs, tool permissions, conversation history) each subagent receives.

1. **Name the information structure first (#2).** For each subagent, write a one-row entry: `agent | observation sources | action produced`. This is the `η` partition — make it explicit before writing any code.
2. **Apply the task-type rule.** For separable subtasks, consider partitioned observations with shared goal, acceptance criteria, constraints and necessary interfaces. For coupled subtasks, compare centralized, hierarchical or communicating candidates; pass decision outputs with evidence, uncertainty and provenance needed downstream. A raw reasoning trace is not required, but verified source evidence may be.
3. **Strip context to decision-relevant signals (#7).** Each token in a subagent's context window is an observation cost. Give the subagent only what changes its action. If a document section never alters the subagent's output, remove it from its context.
4. **Check for signaling (#6).** If A’s output affects B’s context, inspect whether B also knows A’s relevant information; output dependence alone does not establish non-classical territory. Do not assume A's optimal policy is the same as if it were working in isolation — A should write with B's downstream use in mind (nonlinear policy).
5. **Compute value of communication before adding agent-to-agent messaging (#4).** Does mid-task chatter between subagents increase the joint answer quality by more than the latency + token cost? Use task coupling and missing information to motivate communication candidates; compare costs and quality locally rather than imposing a blanket no-communication rule.
6. **Compare decentralized + late synthesis with a central baseline at matched budgets.** Count total observation, communication and synthesis costs; O(1) per-agent work does not imply O(1) total system cost. No universal four-agent threshold is established.

---

## Workflow

1. Confirm common-task condition (#10). If payoffs diverge, exit to game-theory.
2. Map the information structure (#2): one agent per row, one observation source per column, fill the matrix.
3. Cost the observations (#7) and the communication channels (#4).
4. Pick organizational form (#8) — centralized, decentralized, hierarchical — justified against alternatives.
5. Verify the exact theorem premises before applying a linear-policy result (#5). Inspect information nestedness when actions affect observations (#6); dependence alone does not disqualify partially nested cases. Otherwise evaluate bounded policy candidates.
6. Report best tested joint policy (#3), searched deviations and uncertainty. Do not certify global optimality from unilateral or pairwise search.
7. For sequential problems with state, frame as Dec-POMDP (#9) and pick an MARL solver.

---

## ASCII Flow

```text
Cooperative multi-agent decision
  -> Confirm shared payoff and common-task condition
     +-- payoff diverges -> exit to game theory
     +-- shared payoff holds -> map information structure
  -> Cost observation and communication channels
  -> Choose centralized, decentralized, or hierarchical form
  -> Compare bounded joint policies and sequential-state needs
  -> Return team design, information lanes, communication rule, and solver path
```

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
- [foundations-grounding-communication](../foundations-grounding-communication/SKILL.md) — *how* agents share state once you decide they should (see also: temporal information structure in human-AI teams — primitive #2, npj AI 2025)
- [agents-subagents](../agents-subagents/SKILL.md) — applied subagent patterns
- [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md) — applied multi-agent orchestration

---

## Citation Notes

- Marschak (1955) "Elements for a Theory of Teams." *Management Science* 1(2). Founded the field.
- Marschak and Radner (1972) *Economic Theory of Teams*. Yale. Canonical text.
- Radner (1962) "Team Decision Problems." *Annals of Mathematical Statistics* 33(3). LQG theorem.
- Witsenhausen (1968) "A Counterexample in Stochastic Optimum Control." *SIAM J. Control* 6(1). Nonlinear-dominance result.
- Bernstein, Givan, Immerman, Zilberstein (2002) "The Complexity of Decentralized Control of Markov Decision Processes." *Math. of Operations Research*. Dec-POMDP framing — NEXP-complete.
- Oliehoek and Amato (2016) *A Concise Introduction to Decentralized POMDPs*. Springer.
- Numeric thresholds (cost-of-communication, observation budgets) are domain-specific. Verify against primary references before using as decision authority.
- Brooks, F.P. (1975/1995) *The Mythical Man-Month*. Addison-Wesley. Source for the team-size / coordination-cost curve (#8b): pairwise coordination links grow combinatorially with team size, used here as a qualitative mechanism, not a quantitative team-theory result.
- Human-team citations and their source entries are owned by `startup-operating-system`: `team-effectiveness-evidence.md`.
- Expertise aggregation failure: Pappu et al. (2026), "Multi-Agent Teams Hold Experts Back," arXiv:2602.01011. In [Table 2 and §4.2](https://arxiv.org/html/2602.01011#S4.SS2), the 41.1% relative synergy gap is HLE Text-Only, Expert Not Mentioned: team accuracy 28.0% versus the At Least One Correct oracle bound 47.5%. It is not a 41.1% loss against the best fixed individual (29.0%); the Reveal Expert team scores 36.0%. Controlled psychology tasks separately show expertise dilution and team-size effects. Do not transfer the abstract's broad comparator wording into a benchmark claim.
- DPI argument for single-agent dominance: Tran & Kiela (2026, arXiv:2604.02460) demonstrate empirically across **three** model families (Qwen3, DeepSeek-R1-Distill-Llama, Gemini 2.5) and five MAS architectures (Sequential, Subtask-parallel, Parallel-roles, Debate, Ensemble) that single-agent systems match or exceed multi-agent on multi-hop reasoning under equal token budgets, with theoretical grounding in the Data Processing Inequality. Preprint; the paper itself flags that "artifacts in API-based budget control ... distort effective computation," which can inflate apparent MAS gains — control for this before citing the comparison as decisive.
- Latent-space inter-agent communication: LatentMAS (Zou et al. 2025, arXiv:2511.20639). [Section 4.1](https://arxiv.org/html/2511.20639#S4.SS1) reports an average 14.6% accuracy improvement over the single-model baseline in its sequential setting; the reported sequential gain over text-based MAS is 2.8%, with 4× average inference speedup against sequential TextMAS. These are architecture- and benchmark-specific results, not a portable guarantee for arbitrary agents. Preserve the authors' units rather than converting to percentage points without table-level calculation.
- Emergent self-organization at scale: Dochkina (2026, arXiv:2603.28990, **submitted to IEEE Access**, not yet accepted) demonstrates across 25,000 tasks, 8 models, and 4-256 agents that a sequential hybrid protocol outperforms **centralized coordination** by 14% (p<0.001); a separate statistic — a 44% quality spread between protocols — carries Cohen's d=1.86. Do not attach d=1.86 to the 14% figure; they measure different things. "Corroboration" by CARD (Wu et al., ICLR 2026) and MegaAgent (ACL 2025) is unverified — treat as a lead, not a confirmed citation.
- Human-AI teaming mode as information structure: Systematic review (npj AI, Nature portfolio, December 2025, N=52 clinical studies) finds simultaneous human-AI observation outperforms sequential mode; corroborated by PRISMA review of 104 studies (Kargarnovin et al., Frontiers in Robotics and AI, 2026) and PNAS Nexus complementarity framework (Gonzalez et al., 2026).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
