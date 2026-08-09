---
name: Coalition Formation Routing
mechanism_id: 22
layer: topology
status: emerging
last_verified: 2026-05-08
sources:
  - https://arxiv.org/abs/2604.14386
---

# Coalition Formation Routing — Stable Subteams Before Synthesis

Coalition-forming mechanism for large agent teams where one flat panel creates overload, duplicated work, or unstable alliances of evidence.

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

The game-theory target is a stable partition: no member or subgroup has a strong reason to defect to another coalition because the current grouping gives better contribution fit.

## When to Use

- 6+ member teams.
- Legal departments with GC plus country/specialist counsel.
- Incident boards with containment, diagnosis, rollback, and comms workstreams.
- Enterprise readiness reviews spanning security, compliance, onboarding, billing, and support.
- Architecture or migration work with independent subsystems.

## When NOT to Use

- Small teams with 2-4 members.
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

- **Pairs with G01 (Belief-Driven Coordination)** to give each coalition a unique belief lane.
- **Pairs with G04 (Shapley)** to evaluate coalition contribution, not only individual contribution.
- **Pairs with G20 (Conformal Social Choice)** for final act/escalate on high-stakes coalition verdicts.
- **Complements foundations-team-theory**: use team theory to price communication, then coalition formation to choose stable subteams.

## Sources

- arXiv 2604.14386 — *Coalition Formation in LLM Agent Networks: Stability Analysis and Convergence Guarantees*.
