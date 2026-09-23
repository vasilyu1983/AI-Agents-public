# Finite checker input/output contract

The helper accepts one file path or `-` for stdin. Input must be a JSON object containing exactly these four fields:

```json
{
  "states": ["idle", "running", "done", "lost"],
  "initial_states": ["idle"],
  "transitions": [["idle", "running"], ["running", "done"], ["running", "lost"]],
  "invariant_states": ["idle", "running", "done"]
}
```

`states` and `initial_states` are nonempty lists. Every state name is a nonempty, non-whitespace string; names are exact and are not normalized. Each name list must contain no duplicates. Initial and invariant names must belong to states. `invariant_states` may be empty. Transitions are a list of distinct two-element lists of known string endpoints; self-loops are permitted. Unknown/missing fields, duplicate JSON object keys, nonstandard numeric constants, duplicate states/edges, and malformed endpoints are rejected.

Output for this example:

```json
{
  "safety_holds": false,
  "reachable_states": ["done", "idle", "lost", "running"],
  "counterexample": ["idle", "running", "lost"],
  "terminal_states": ["done", "lost"]
}
```

Breadth-first traversal sorts initial states and neighbors lexicographically, independently of input edge order. It returns the first violating state reached in this deterministic traversal and a shortest trace to it, including an initial-state violation as a one-state trace. Traversal continues to enumerate all reachable states. No violation gives a null counterexample. Terminal states are reachable states with no outgoing transitions; they are not labeled deadlocks.

Exit status: 0 = invariant holds in this graph; 1 = reachable violation; 2 = input/file error with a JSON error on stderr. Success/result JSON is on stdout. This is a safety-membership check only. Completeness depends on the supplied graph representing all intended executions. There is no expression evaluation, probabilistic analysis, fairness check, liveness result, symbolic exploration, or implementation-correctness guarantee.

Run [tests](../scripts/test_check_finite_model.py) for cycles, multiple initial states, unreachable violations, deterministic shortest paths, strict inputs, and CLI status semantics.
