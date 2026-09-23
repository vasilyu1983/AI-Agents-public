#!/usr/bin/env python3
"""Check state-invariant safety in a fully enumerated finite directed graph."""
import argparse
from collections import deque
import json
from pathlib import Path
import sys


class ModelError(ValueError):
    """Malformed finite-model input."""


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ModelError(f"duplicate JSON field: {key}")
        obj[key] = value
    return obj


def reject_constant(value):
    raise ModelError(f"nonstandard JSON constant: {value}")


def load_model(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def names(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ModelError(f"{label} must be {'a nonempty' if nonempty else 'a'} list")
    if any(not isinstance(x, str) or not x.strip() for x in value):
        raise ModelError(f"{label} must contain nonempty string state names")
    if len(set(value)) != len(value):
        raise ModelError(f"{label} contains duplicate states")
    return set(value)


def check_model(model):
    fields = {"states", "initial_states", "transitions", "invariant_states"}
    if not isinstance(model, dict) or set(model) != fields:
        raise ModelError("expected exactly states, initial_states, transitions, invariant_states")
    states = names(model["states"], "states", True)
    initials = names(model["initial_states"], "initial_states", True)
    allowed = names(model["invariant_states"], "invariant_states")
    if not initials <= states or not allowed <= states:
        raise ModelError("initial_states and invariant_states must be subsets of states")
    edges = model["transitions"]
    if not isinstance(edges, list):
        raise ModelError("transitions must be a list of [source, target] pairs")
    adjacency = {state: set() for state in states}
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ModelError("each transition must be a two-element list")
        if any(not isinstance(x, str) or x not in states for x in edge):
            raise ModelError("transition endpoints must be known string states")
        source, target = edge
        if target in adjacency[source]:
            raise ModelError("duplicate transition")
        adjacency[source].add(target)
    queue = deque(sorted(initials))
    parent = {state: None for state in initials}
    first_violation = None
    while queue:
        current = queue.popleft()
        if current not in allowed and first_violation is None:
            first_violation = current
        for target in sorted(adjacency[current]):
            if target not in parent:
                parent[target] = current
                queue.append(target)
    trace = None
    if first_violation is not None:
        trace = []
        current = first_violation
        while current is not None:
            trace.append(current)
            current = parent[current]
        trace.reverse()
    return {
        "safety_holds": first_violation is None,
        "reachable_states": sorted(parent),
        "counterexample": trace,
        "terminal_states": sorted(state for state in parent if not adjacency[state]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="JSON file, or - for standard input")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.model == "-" else Path(args.model).read_text(encoding="utf-8")
        result = check_model(load_model(text))
    except (ModelError, json.JSONDecodeError, OSError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["safety_holds"] else 1


if __name__ == "__main__":
    sys.exit(main())
