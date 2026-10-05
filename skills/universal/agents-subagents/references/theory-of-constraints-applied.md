---
description: Theory of Constraints applied to multi-agent teams: finding the bottleneck stage, drum-buffer-rope dispatch, throughput over activity, and policy-constraint detection.
last_verified: 2026-09-24
status: stable
---

# Theory of Constraints Applied to Multi-Agent Teams

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

The five focusing steps, drum-buffer-rope, throughput accounting, critical chain and policy constraints are explained in the [foundation's templates](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/). A team's output rate is set by its slowest stage, so speeding up any other stage changes nothing. This file keeps the rules that change team dispatch and retros.

## Decision rules

1. **Find the constraint before scaling the team.** It is often the synthesis owner, not a specialist. Try the free steps first: exploit it (prepared context, a structured synthesis template, off-loading non-synthesis work), then subordinate everyone else to its pace. Elevate (split synthesis into a separate aggregator, use a stronger model, add caching) only if exploit and subordinate give less than about 20% improvement. After elevating, look for the constraint again, because it moves.
2. **Rope the dispatch to the constraint.** Don't dispatch wave N+1 until wave N's synthesis is committed. Slower upstream dispatch can raise team throughput when it keeps the synthesis owner from overload. Take the capacity numbers from [queueing-theory-applied.md](queueing-theory-applied.md).
3. **Measure throughput, not activity.** Count decisions committed and actions adopted per session, net of token cost, latency and human review time. "We ran six members" is activity. A team that produces many summaries and few decisions is high-cost and low-throughput.
4. **If more capacity doesn't raise throughput, look for a policy constraint.** Typical culprits: synthesis waits for every member; every dissent triggers another round; all edits go through one owner; stop only on consensus. Replace synchronous all-must-finish gates with asynchronous ones that carry a deadline. Watch the synthesis owner's buffer (the reserve used per session): consumption routinely above two-thirds (the foundation's red zone) means elevate; routinely below one-third means the constraint has moved.

## Worked recipe — constraint sweep for a team with ≥10 logged sessions

```text
1. throughput = decisions committed per session (net of cost)
2. per-stage share of time and tokens: dispatch | member work | synthesis
3. constraint = the stage with the highest share AND the highest variance
4. exploit → subordinate; re-measure over the next sessions
5. gain < ~20%? → elevate the constraint; otherwise stop
6. elevation gave nothing? → list stop/proceed/escalate rules and ask of each:
   "does this serve throughput or appearance?"; make blocking gates async with a deadline
```

Team recipes deliberately don't carry constraint or buffer manifest blocks (see `agents/teams/README.md`). Record the diagnosis in the run's retro notes instead.

## Related

- [decision-theory-applied.md](decision-theory-applied.md): stopping rules at the synthesis stage.
- [team-prompt-patterns.md](team-prompt-patterns.md): admission-control wording.
- Primary sources: Goldratt, *The Goal* (1984); Cox & Spencer (1998), both cited in the foundation.
