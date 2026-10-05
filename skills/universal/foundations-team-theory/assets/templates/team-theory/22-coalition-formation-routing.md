---
name: Coalition Formation Routing
mechanism_id: 22
layer: topology
status: emerging
sources:
  - https://arxiv.org/abs/2604.14386
---

# Coalition Formation Routing — Stable Subteams Before Synthesis

Coalition-forming mechanism for large agent teams where one flat panel creates overload, duplicated work, or unstable alliances of evidence.

**Scope note:** the fit-based coalition recipe below is an aggregation-layer topology choice for a shared-payoff team, so it lives with the other aggregation rules in `foundations-team-theory`. Its sole source (arXiv:2604.14386) grounds coalition formation in hedonic game theory with Nash-stable partitions and epsilon-rational preferences; the recipe itself is fit-based, not a hedonic-game core, and makes no stability guarantee. If members can gain by misreporting fit or preferences, that is a mechanism-design problem: see `foundations-game-theory`. When aggregation pays at all: [`references/aggregation-and-multi-agent-evidence.md`](../../../references/aggregation-and-multi-agent-evidence.md).

## Problem

Large teams often run as a flat broadcast panel. Every member sees the same brief, produces overlapping output, and the synthesizer absorbs the full conflict. This fails when the task naturally decomposes into workstreams and member preferences or expertise cluster by subproblem.

## Solution

Form coalitions around compatible subproblems, then synthesize coalition outputs.

Operationally:

1. Identify candidate workstreams.
2. Ask each member to rank which workstreams it can improve and which members it needs.
3. Build coalitions that are internally coherent and externally non-overlapping.
4. Run coalition-local analysis first.
5. Run final synthesis across coalition leads.

The design target is a stable partition: no member or subgroup has a strong reason to move to another coalition because the current grouping gives better contribution fit. The recipe checks this by inspection, it does not prove it.

## When to Use

- Measured coordination/synthesis cost, independent workstreams, or ownership gaps that a coalition structure could address; compare against a flat baseline.
- Legal departments with GC plus country/specialist counsel.
- Incident boards with containment, diagnosis, rollback, and comms workstreams.
- Enterprise readiness reviews spanning security, compliance, onboarding, billing, and support.
- Architecture or migration work with independent subsystems.

## When NOT to Use

- Team size is the only proposed justification; neither small nor large size alone establishes an advantage.
- Single cohesive question where every member must reason about the same evidence.
- Emergency decisions where coalition formation latency is worse than flat triage.
- Cases where a deterministic owner already exists for every subproblem.

## Protocol

```yaml
coordination:
  mode: coalition-formation
  coalition_inputs:
    workstreams: [legal, technical, operational, commercial]
    member_rankings: required
  stability_check:
    no_unassigned_load_bearing_workstream: true
    no_member_with_better_fit_elsewhere: true
  synthesis:
    local_first: true
    coalition_leads_only_round: true
```

## Agent-Team Pattern

For a large manifest, add a launch-time coalition step:

```
Before dispatch:
1. Name workstreams.
2. Assign each member to one primary coalition and optional consult role.
3. Each coalition produces local findings and dissent.
4. Synthesis owner compares coalition outputs, not raw member outputs.
```

## Anti-Patterns

- **Coalition by org chart**: grouping by job title instead of evidence dependency.
- **Hidden duplicate work**: two coalitions investigate the same issue without knowing.
- **No stability check**: a member is assigned to a coalition where it cannot change the result.
- **Coalition silos**: local findings never meet at a final cross-coalition synthesis.

## Composition

- **Pairs with 01 (Belief-Driven Coordination)** to give each coalition a unique belief lane.
- **Pairs with 04 (Shapley)** to evaluate coalition contribution, not only individual contribution.
- **Pairs with 20 (Conformal Social Choice)** for final act/escalate on high-stakes coalition verdicts.
- **Complements primitives #4 and #8** in this skill: price communication (#4) and pick the organizational form (#8), then use coalition formation to choose subteams.

## Sources

- arXiv 2604.14386 — *Coalition Formation in LLM Agent Networks: Stability Analysis and Convergence Guarantees*.
