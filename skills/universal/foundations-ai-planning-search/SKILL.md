---
name: foundations-ai-planning-search
description: Applies planning/search theory (A*, CSP, MCTS, PDDL, HTN) to agents. Use when ordering tool calls, enforcing preconditions before side effects, or validating a plan.
compatibility: Portable core only.
version: "1.6"
last_validated: 2026-08-14
---

# AI Planning And Search Foundations


## Quick Reference

Each primitive is expanded in [references/primitives-overview.md](references/primitives-overview.md). Use [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) for scenario recipes and [references/formal-theory-map.md](references/formal-theory-map.md) when completeness, optimality, or complexity claims matter.

| # | Primitive | Problem It Solves | Failure Mode Addressed | Key Parameters |
|---|-----------|------------------|----------------------|----------------|
| 1 | [Problem Formulation](references/primitives-overview.md#1-problem-formulation) | Vague tasks cannot be searched or verified | Agent cannot know what counts as legal progress | State, actions, transition model, goal test, path cost |
| 2 | [Uninformed Search](references/primitives-overview.md#2-uninformed-search) | Need complete baseline without domain heuristic | No baseline for completeness, optimality, or frontier explosion | Branching factor b; depth d; frontier policy |
| 3 | [Heuristic Search](references/primitives-overview.md#3-heuristic-search) | Large state spaces need directed exploration | State space explodes because exploration is undirected | Heuristic h(n); admissibility; consistency |
| 4 | [Local Search](references/primitives-overview.md#4-local-search) | State is large but path is irrelevant | Path-tracking wastes memory when only final configuration matters | Neighborhood; objective; restart/schedule |
| 5 | [Constraint Satisfaction](references/primitives-overview.md#5-constraint-satisfaction) | Need assignments satisfying hard constraints | Constraints are mixed into prompts instead of enforced structurally | Variables, domains, constraints, MRV/LCV, arc consistency |
| 6 | [Adversarial Search](references/primitives-overview.md#6-adversarial-search) | Opponent actions affect outcomes | Opponent response is ignored or treated as noise | Utility, depth, alpha-beta bounds, rollout policy |
| 7 | [Classical Planning](references/primitives-overview.md#7-classical-planning) | Need valid action sequence from symbolic preconditions/effects | Preconditions and effects are implicit, so invalid plans pass review | STRIPS/PDDL, progression/regression, plan graph |
| 8 | [Hierarchical Planning](references/primitives-overview.md#8-hierarchical-planning) | Tasks decompose into reusable subplans | Repeated task decomposition is ad hoc and inconsistent | Methods, subtasks, ordering constraints |
| 9 | [Contingent / Belief-State Planning](references/primitives-overview.md#9-contingent-and-belief-state-planning) | Partial observability or nondeterministic actions | Plan assumes full observability or deterministic actions | Belief state, sensing actions, policy vs sequence |
| 10 | [Planner-Agent Integration](references/primitives-overview.md#10-planner-agent-integration) | LLM agent needs explicit plan validity and search boundaries | LLM tool loop lacks plan validation, replanning, or bounded search | Planner tool, state abstraction, verifier, replanning trigger |

---

## When to Apply

**Apply this skill when:**
- The task can be stated as states, actions, transitions, goals, and costs.
- You need A*, uniform-cost search, beam search, backtracking, alpha-beta, MCTS, STRIPS/PDDL, HTN, or CSP reasoning.
- An LLM agent is hallucinating action sequences that need explicit validity checks.
- The workflow needs a planner as a tool, not only prompt decomposition.
- A search or planning algorithm choice changes runtime, completeness, optimality, or failure behavior.

**Skip or route elsewhere when:**
- It is product search, vector retrieval, ranking, or query matching -> use `software-search` or `ai-rag`.
- It is expected utility, value of information, real options, or bandits -> use `foundations-decision-theory`.
- It is feedback control, setpoint tracking, or MPC -> use `foundations-control-theory`.
- It is strategic incentive design or equilibrium -> use `foundations-game-theory`.
- It is cooperative subagent allocation with shared payoff and partitioned information -> use `foundations-team-theory`.
- It is general agent architecture, memory, tools, or MCP/A2A orchestration -> use `ai-agents` after this skill defines the planner boundary.

---

## Anti-Patterns

| Anti-Pattern | Planning/Search Diagnosis | Fix |
|-------------|---------------------------|-----|
| "Ask the LLM to plan" with no state model | No legal-action or goal-test boundary | Define state, action schema, preconditions, effects, and cost (#1, #7) |
| Greedy search used where optimality is promised | Heuristic is not an admissible cost lower bound | Use A* with admissible/consistent heuristic or stop promising optimality (#3) |
| BFS on high branching factor without depth bound | Frontier blowup | Use UCS/A*, iterative deepening, pruning, or abstraction (#2, #3) |
| Constraints buried in prompt prose | Violations are discovered after execution | Model as CSP with propagation and backtracking (#5) |
| Minimax for real-world negotiation | Payoffs and strategies are not a finite game tree | Route incentive/equilibrium design to `foundations-game-theory` (#6 boundary) |
| PDDL generated but never validated | Planner accepts malformed or semantically wrong domain | Run domain/problem validation and check plan preconditions/effects (#7) |
| Replanning on every token/tool call | Planner-agent boundary is too fine-grained | Replan only on state drift, failed precondition, or new observation (#10) |
| Treating a valid plan as a safe plan | Validity checks preconditions/effects; it does not check whether the goal or path is one that should be executed | Add a separate safety/permission gate over the action set — validity and safety are independent axes (#7, #10) |
| Adding tree search to raise accuracy without a verifier | Search amplifies the scoring signal; an unreliable scorer just finds higher-confidence errors faster | Establish scorer/verifier reliability first, then compare against best-of-N at matched compute, bucketed by difficulty, before adopting tree/beam search (#3, #6) |

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Calling a prompt outline a plan | It has no executable action model or validity check | Convert to state/action/precondition/effect model |
| Treating local optimum as global optimum | Local search is incomplete without strong assumptions | Use restarts, exact search for small instances, or state the approximation |
| Using A* with an overestimating heuristic while claiming optimality | A* optimality depends on admissibility/consistency | Prove h(n) <= true remaining cost or downgrade claim |
| Modeling soft preferences as hard CSP constraints | Search may become infeasible for avoidable reasons | Separate hard constraints from weighted objectives |
| Using adversarial search for cooperative teams | Cooperative information structure has different primitives | Route to `foundations-team-theory` |
| Treating partial observability as deterministic planning | Actions may need sensing and contingencies | Use belief-state or contingent planning (#9) |
| Inferring plan safety from planning competence | Measured separately, the two do not track each other: a model can be near-perfect at producing executable plans and still route a large fraction of tasks through dangerous actions | Gate the action set independently of the planner's success metric (#10) |

Before claiming a search guarantee, load the [guarantee matrix](references/practical-contract.md#guarantee-matrix): finite branching and nonnegative costs alone do not establish UCS/A* completeness in infinite spaces; the standard bound requires step costs bounded below by positive epsilon. A* graph search must reopen improved states with an admissible but inconsistent heuristic, or use consistency when permanently closing nodes. Planner validity requires correct action preconditions/effects. Do not invent benchmark numbers. If a planner or solver is recommended, report assumptions, problem size, and validation cases instead of generic speed claims.

LLM planning benchmark numbers move fast and are rarely comparable across papers: success rate depends on domain, instance size, prompt encoding, number of retries, and whether a verifier was in the loop. Cite the specific setup or state the result qualitatively; do not carry a headline percentage across domains.

---

## Composition Recipes

### LLM Agent With Valid Plans

**Failure**: Agent produces plausible steps that violate tool preconditions.

- Problem formulation (#1): define typed state and legal action schema.
- Classical planning (#7): encode preconditions/effects for tools.
- Planner-agent integration (#10): LLM proposes goals or abstractions; planner validates; executor runs only valid next action.
- Replanning trigger (#10): replan after failed precondition, external state drift, or new observation.

### Configuration Assistant That Respects Constraints

**Failure**: Recommendations violate compatibility, license, budget, or availability constraints.

- CSP (#5): model components as variables and compatibility rules as constraints.
- Local search (#4): if preferences are soft and space is too large for exact search.
- Decision theory boundary: route scoring tradeoffs to `foundations-decision-theory` when expected value or risk weighting matters.

### Game Or Simulation Agent

**Failure**: Agent picks locally good moves and misses opponent responses.

- Adversarial search (#6): minimax or alpha-beta for deterministic games.
- MCTS (#6): stochastic or high-branching games with rollout evaluation.
- Heuristic search (#3): evaluate states with domain heuristic.
- Game theory boundary: route equilibrium, mechanism, or incentive design to `foundations-game-theory`.

### Workflow Planner For Human Operations

**Failure**: Task decomposition is repeated manually and varies across runs.

- HTN (#8): encode standard decompositions and method selection.
- Classical planning (#7): validate preconditions for steps with tool or data dependencies.
- Grounding boundary: use `foundations-grounding-communication` for handoff repair and common-ground checks.

### "Works In The Demo, Fails In Production"

**Failure**: A planner or agent loop that passed every walkthrough degrades or breaks under real traffic.

- Diagnose in order of likelihood before assuming a logic bug: production branching factor vs. demo branching factor, heuristic/verifier fit to the demo distribution, unmodeled nondeterminism, missing or unbounded replanning triggers, a validator that exists in eval but not in the production executor path, and search budget (rollouts/nodes/beam width) silently shrunk by latency or cost limits.
- Full diagnostic checklist: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md#works-in-the-demo-fails-in-production).

---

## Workflow

1. Formulate the problem as state, actions, transition model, goal test, and cost.
2. Classify the dominant structure: path search, assignment/CSP, game tree, symbolic plan, hierarchy, or uncertainty.
3. Choose the simplest algorithm family that preserves required guarantees: completeness, optimality, bounded memory, or good-enough solution quality.
4. Write the search/planning assumptions explicitly before implementation.
5. For LLM agents, decide what the LLM may propose and what the planner/verifier must enforce.
6. Validate with small hand-checkable cases, impossible cases, and adversarial edge cases.

Before claiming a guarantee, record a one-row **guarantee ledger**:
`claim | algorithm | model assumptions | runtime limits | verifier | counterexample test`.
Completeness or optimality belongs to the modeled problem, not automatically to
the real executor. If preconditions, effects, costs, observability, or resource
limits differ in production, report the result as a validated heuristic plan
rather than inheriting the algorithm's theorem.

---

## Navigation

- [scripts/replay_plan.py](scripts/replay_plan.py) — deterministic support artifact.
- [scripts/test_replay_plan.py](scripts/test_replay_plan.py) — deterministic support artifact.
- [data/plan-fixtures.json](data/plan-fixtures.json) — deterministic support artifact.
- Practical completion contract and known-answer controls: [references/practical-contract.md](references/practical-contract.md).
- Primitives overview: [references/primitives-overview.md](references/primitives-overview.md)
- Patterns, scenarios, and traps: [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md)
- Formal theory map: [references/formal-theory-map.md](references/formal-theory-map.md)
- Sources: [`data/sources.json`](data/sources.json)

## Related Skills

- `foundations-decision-theory` - utility, value of information, regret, and bandits.
- `foundations-control-theory` - feedback loops, stability, and MPC.
- `foundations-game-theory` - incentives, equilibrium, mechanism design, and strategic actors.
- `foundations-team-theory` - cooperative multi-agent allocation with shared payoff.
- `foundations-grounding-communication` - handoff repair and common-ground checks for HTN workflow planners.
- `foundations-mathematical-optimization` - scheduling, allocation, and CP-SAT for duration/resource/precedence problems without state-dependent preconditions.
- `foundations-formal-methods` - LLM-generated formal specifications and sound-tool verification, the same pattern this skill applies to PDDL.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
