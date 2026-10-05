---
description: Marschak–Radner team theory applied to agent orchestration: observation-budget sizing, organizational-form choice, value-of-communication tests, and avoiding the person-by-person-optimal trap.
last_verified: 2026-09-24
status: stable
---

# Team Theory Applied to Agent Orchestration

> **Gate before invoking:** Check [`foundations-team-theory` § When to Apply](../../foundations-team-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

A subagent fan-out is a team decision problem: members share one payoff but each sees only part of the context. Information structure, value of communication, person-by-person optimality, organizational forms and the common-task condition are explained in the foundation's [primitives overview](../../foundations-team-theory/references/primitives-overview.md). This file keeps the rules that change a fan-out design.

## Decision rules

1. **Before a fan-out of 3+ subagents, draw the information-structure matrix** (rows: subagents and synthesis; columns: sources). Keep a cell only if that agent's action depends on that observation. If several agents need the same large observation, consider centralizing that decision instead of copying the observation into each context.
2. **Add an inter-agent channel only if you can name the receiver's action it would change.** Compare the channel's cost per run (tokens, latency) with the expected cost of the counterfactual. If the receiver does the same thing either way, drop the channel. Judge operator auditing and recovery benefits separately.
3. **Pick the organizational form by coupling × information cost**, as candidates to compare locally, not as a theorem. Low coupling with low cost: either, pick by operational simplicity. Low coupling with high cost: decentralized with late synthesis. High coupling with low cost: orchestrator-led. High coupling with high cost: hierarchical with explicit escalation. If you depart from the framework's default, record why.
4. **Tuning each prompt separately is not tuning the team.** Run a joint ablation (baseline, each single change, the joint change, on identical tasks and seeds, independently graded) only when you have a concrete interaction hypothesis that could change the decision. Use the foundation's [local comparison contract](../../foundations-team-theory/references/local-team-comparison.md). When members share acceptance criteria, fix the specification, tools and evaluation before adding votes, auctions or incentives. Route to game theory only when there is a named strategic conflict.

## Worked recipe — observation budget and a channel decision

```text
Fan-out: 4 subagents, 100K-token shared context
Naive:    4 × 100K                              = 400K tokens of observation
Audited:  sub-1 needs 30K; sub-2..4 need 15K each =  75K tokens
Saved:    325K (81%) → spend it on per-subagent task context

Proposed channel: planner streams plan revisions to the executor
  Receiver action changed: executor updates its working plan mid-run
  Channel cost:        ~3 revisions × 500 tokens              = 1.5K tokens/run
  Counterfactual cost: follow-up dispatch 2K × 30% of runs    = 0.6K tokens/run
  1.5K > 0.6K → reject the channel
```

The token counts are illustrative. Take the real ones from your run logs before quoting a saving.

## Related

- [grounding-communication-applied.md](grounding-communication-applied.md): how to ground meaning once a channel is justified.
- [game-theory-agent-teams.md](game-theory-agent-teams.md): the exit when the common-task condition fails.
- [queueing-theory-applied.md](queueing-theory-applied.md): sizing the fan-out itself.
- Primary sources: Marschak & Radner (1972); Radner (1962), both cited in the foundation.
