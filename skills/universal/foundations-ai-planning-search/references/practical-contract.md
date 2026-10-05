# Executable Planning Contract

## Guarantee matrix

| Method | Required conditions | Limit |
|---|---|---|
| BFS | finite branching, finite goal depth | shortest path only for equal step cost |
| UCS | finite branching, step costs bounded below by positive epsilon for standard infinite-space completeness | nonnegative costs alone do not ensure termination in an infinite graph |
| A* tree search | admissible heuristic, finite branching, suitable positive-cost conditions | resource limits can destroy completeness |
| A* graph search | consistency if permanently closing nodes; otherwise reopen improved states with admissible heuristic | sampled heuristic checks cannot establish global admissibility |
| Weighted A* | stated weight and underlying admissibility/reopening conditions | bounded-suboptimal guarantee needs those conditions; arbitrary LLM heuristic has no such bound |
| Beam search | explicit width and scorer | generally incomplete and nonoptimal |

## Runnable finite-state replay

Run `python3 scripts/replay_plan.py data/plan-fixtures.json`. The fixture uses boolean facts, named actions, preconditions, add/delete effects and nonnegative costs. The helper rejects duplicate JSON fields, unknown actions and overlapping effects, replays only legal steps, and reports goal satisfaction, total cost and the first violated precondition. It verifies a supplied sequence in its supplied model; it neither searches for a plan nor certifies actual tool effects or action safety.

## Executor handoff

Write state abstraction, goal, legal actions, modeled effects, observed-state refresh, safety/authorization gate and execution receipt before integration. Recheck actual preconditions immediately before each side effect. After an unexpected observation, mark the old plan stale and replan from observed state, rather than continuing from predicted effects.

Budget contract: record node/rollout/token/latency ceilings, repair round limit, and termination status (`goal`, `infeasible-proven`, `budget-exhausted`, `model-invalid`, `stale-state`). Budget exhaustion means unknown feasibility unless a separate certificate exists. Stop with the last verified state and unmet goals; never execute an unverified fallback.

`scripts/test_replay_plan.py` covers valid sequence, impossible supplied goal, first-step failure, state drift removing a precondition, malformed/unknown actions and duplicate JSON preconditions rejected by the CLI. Run `python3 scripts/test_replay_plan.py`. It has no gate or veto logic — `replay_plan.py` checks validity only. The legal-but-dangerous sequence vetoed by a separate operator gate is the consumer's responsibility: that gate is a distinct component (see the Executor handoff safety/authorization gate above) and belongs in the consumer's own test suite, not in this helper.
