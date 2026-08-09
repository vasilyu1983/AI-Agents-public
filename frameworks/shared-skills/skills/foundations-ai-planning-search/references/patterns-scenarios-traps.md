# AI Planning And Search Patterns, Scenarios, And Traps

## Contents

- [Planner-As-Verifier](#planner-as-verifier)
- [Constraint-First Recommendations](#constraint-first-recommendations)
- [A* Design Checklist](#a-design-checklist)
- [Adversarial Search Boundary](#adversarial-search-boundary)
- [PDDL / Symbolic Planning Trap List](#pddl--symbolic-planning-trap-list)
- [Works In The Demo, Fails In Production](#works-in-the-demo-fails-in-production)
- [Choosing A Planner Family Under Production Constraints](#choosing-a-planner-family-under-production-constraints)

## Planner-As-Verifier

Use this pattern when an LLM is good at interpreting the user but weak at maintaining valid action sequences.

1. LLM converts the user request into a candidate goal and state abstraction.
2. Planner verifies the current state, legal actions, and goal reachability.
3. Executor runs only the next validated action.
4. Observation updates state.
5. Replan only when the precondition fails, state drifts, or the goal changes.

## Constraint-First Recommendations

Use CSP modeling before ranking when recommendations have hard compatibility constraints.

- Hard constraints: license, budget ceiling, hardware compatibility, legal restriction, dependency incompatibility.
- Soft preferences: price, convenience, performance, taste, aesthetics.
- Solver output should return infeasible reasons when no assignment exists.

## A* Design Checklist

- Is every step cost nonnegative?
- Is the heuristic admissible if optimality is claimed?
- Is the heuristic consistent if graph-search A* avoids reopening nodes?
- Is the branching factor manageable?
- Are duplicate states canonicalized?
- Is the goal test exact enough to prevent near-miss plans?

## Adversarial Search Boundary

Use minimax, alpha-beta, expectimax, or MCTS for finite games, simulations, and bounded lookahead. Do not use them as a substitute for strategic market or organizational modeling. If the issue is incentives, mechanism design, repeated interaction, or equilibrium, route to `foundations-game-theory`.

## PDDL / Symbolic Planning Trap List

- Preconditions omit required external state.
- Effects update only the happy path.
- Negative preconditions are modeled inconsistently.
- Numeric fluents are used where a CSP/optimization solver would be clearer.
- Planner output is not replayed against the state transition model.
- Problem instance overfits one example instead of the domain.

## Works In The Demo, Fails In Production

A planning system that looked solid in a walkthrough and then degrades or fails once real traffic hits it almost always fails for one of a small number of reasons. Diagnose in this order — cheapest and most common causes first:

1. **The demo's branching factor was not the production branching factor.** Demos are usually run on hand-picked, small, well-behaved instances. Real inputs (larger inventories, more tool options, messier user requests) can blow up the search tree by orders of magnitude even though the algorithm did not change. Check: what was the state/action count in the demo vs. the p95 production instance? If it is 10-100x larger, the failure is search-space explosion, not a logic bug — the fix is a tighter heuristic, hierarchical decomposition (#8), abstraction, or a hard node/time budget with graceful degradation, not more debugging of the demo case.
2. **The heuristic or verifier was implicitly fit to the demo distribution.** A heuristic (hand-tuned, learned, or LLM-generated per the 2025 note in `primitives-overview.md`) that was accepted because it worked on the cases the team tried is a heuristic that was model-selected against those cases, whether anyone intended that or not. In production it silently loses admissibility or informativeness on inputs unlike the demo set. Check: was the heuristic ever run against adversarial or out-of-distribution instances before ship, or only against the happy-path demo set?
3. **Nondeterminism that the demo never exercised was modeled as deterministic.** Tool calls that occasionally fail, retry, time out, or return partial results are nondeterministic effects; a plan built assuming a single deterministic outcome per action will desync from real state the first time a tool call does something the demo script never triggered. Check: does the executor re-observe state after every action, or does it trust the pre-planned effect blindly (see #9, belief-state/contingent planning, and the replanning triggers in #10)?
4. **Replanning is either absent or unbounded.** Two opposite failures share a root cause — no explicit replanning trigger. Absent: the plan silently continues after a precondition fails, producing invalid downstream actions. Unbounded: the system replans on every tool response or token, causing latency blowup, cost blowup, or oscillation between near-equivalent plans (thrashing). Check: is there a named, finite list of replanning triggers (failed precondition, state drift beyond tolerance, new observation, changed goal, budget exhaustion), or is replanning frequency an emergent property of the loop?
5. **The plan validator that caught bad plans in the demo is not wired into the production executor path.** It is common to validate plans in a notebook or eval harness and then ship an executor that calls the LLM or planner directly without the same validation gate. Check: does the exact validation code path that ran in the demo/eval also run before every action in production, or was it reimplemented (or dropped) somewhere along the way?
6. **Latency or cost budget in production forces a shallower search than the demo used.** MCTS rollout counts, A* node expansion limits, and beam widths are often generous in a demo run with no SLA and tight in production once a per-request time or token budget is enforced. A shallow search under budget pressure degrades quietly — it still returns an answer, just a worse one — so this failure mode is easy to miss without instrumentation. Check: log search depth/rollout count/nodes-expanded per production request and compare the distribution to what the demo actually used, not what the code allows in principle.
7. **LLM planners hallucinate infeasible steps under distribution shift.** An LLM proposing plan steps (goal decomposition, tool argument construction, PDDL-like action selection) will fabricate a plausible-sounding action that violates an unstated precondition more often as the request moves away from patterns in its training or few-shot examples — not because the model got "worse," but because plausibility and feasibility diverge exactly where the input is novel. This is why #7/#10 insist on validating every proposed action against the actual transition model rather than trusting fluency as a proxy for validity; a plan that reads well is not evidence it is executable.

When a stakeholder says "it worked when I tried it," treat that as a report about one point in the input distribution, not a validation result — ask what fraction of production traffic resembles the demo case, not whether the demo case still passes.

## Choosing A Planner Family Under Production Constraints

The Decision Checklist in `SKILL.md` picks a primitive from problem structure. In production, two more constraints usually decide the real build, independent of structure:

- **Latency/cost budget available per decision.** Classical planners (STRIPS/PDDL solvers) and CSP solvers are usually cheapest and most predictable once the domain is encoded, but the encoding cost is high and one-time. MCTS and best-first search trade a tunable, per-request cost (rollouts, node expansions) for accuracy — appropriate when the budget can flex per request and a verifier/execution signal is cheap. LLM-only planning is cheapest per call but has the weakest validity guarantees; it belongs at the bottom of the build-vs-skip threshold in #10, not as a default.
- **How costly a wrong action is.** If a wrong step is irreversible, expensive, or hard to detect (spend, data loss, safety), invest in the strongest available validity guarantee even at higher engineering cost: a symbolic planner with a replayed validator, or CSP with hard constraints, rather than an inadmissible heuristic or an unverified LLM proposal. If a wrong step is cheap to detect and retry, a lighter-weight approach (typed function-call schemas with precondition checks in code) is proportionate and the full planning stack is over-engineering.

Route the "should we even build a planner" question through both axes before picking an algorithm: structure tells you the family, budget and failure cost tell you how much rigor within that family is worth paying for.
