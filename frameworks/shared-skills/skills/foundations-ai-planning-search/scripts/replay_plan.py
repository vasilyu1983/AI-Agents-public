#!/usr/bin/env python3
"""Replay explicit boolean-fact plans; neither search nor real execution."""
import argparse
import json
import math


def facts(value):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() or x != x.strip() for x in value) or len(set(value)) != len(value):
        raise ValueError('facts must be unique nonblank trimmed strings')
    return set(value)


def replay(model):
    if not isinstance(model, dict) or set(model) != {'initial', 'goal', 'actions', 'plan'}:
        raise ValueError('require initial, goal, actions and plan only')
    state, goal = facts(model['initial']), facts(model['goal'])
    actions, plan = model['actions'], model['plan']
    if not isinstance(actions, dict) or not isinstance(plan, list):
        raise ValueError('actions must map names to schemas; plan must be a list')
    checked = {}
    for name, action in actions.items():
        if not isinstance(name, str) or not name.strip() or name != name.strip() or not isinstance(action, dict) or set(action) != {'requires', 'add', 'delete', 'cost'}:
            raise ValueError('invalid action schema')
        required, added, deleted = facts(action['requires']), facts(action['add']), facts(action['delete'])
        cost = action['cost']
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0 or added & deleted:
            raise ValueError('cost must be finite/nonnegative; effects must be disjoint')
        checked[name] = (required, added, deleted, cost)
    if any(not isinstance(name, str) or name not in checked for name in plan):
        raise ValueError('unknown plan action')
    total = 0
    for step, name in enumerate(plan):
        required, added, deleted, cost = checked[name]
        missing = sorted(required - state)
        if missing:
            return {'status': 'failed-precondition', 'step': step, 'action': name, 'missing': missing, 'state': sorted(state), 'cost': total, 'goal_satisfied': False}
        total += cost
        if not math.isfinite(total):
            raise ValueError('total cost exceeds finite output range')
        state = (state - deleted) | added
    return {'status': 'goal' if goal <= state else 'goal-unmet', 'state': sorted(state), 'cost': total, 'goal_satisfied': goal <= state}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model')
    args = parser.parse_args()
    try:
        with open(args.model, encoding='utf-8') as handle:
            result = replay(json.load(handle))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(result, allow_nan=False, indent=2))


if __name__ == '__main__':
    main()
