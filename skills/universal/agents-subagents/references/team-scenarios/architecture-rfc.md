---
description: Architecture RFC — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Architecture RFC

**Typical scenario**

You need a design recommendation for splitting a subsystem or changing core boundaries.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "architecture-rfc"`.

Scenario: Decide whether to split billing from the monolith into a separate service or keep it inside the modular monolith with stronger boundaries.

Required context:
- Current pain: billing changes are slowing unrelated releases
- Constraints: team size is small, PCI scope must stay controlled, rollout must happen within 2 quarters
- Optional artifacts if present: profiles/*.json, graphs/system-edges.json, graphs/code-graph.json

Instructions:
- software-solution-architect: compare target-state options and transition paths
- dev-api-designer: define interface and contract implications
- data-architect: assess data ownership, consistency, and migration risk
- software-risk-reviewer: assess security, resilience, and operational risks
- Run analysis in parallel, then synthesize into one RFC recommendation
- Include a decision matrix, top risks, and phased migration path
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for solution architecture, API design, data architecture, and software risk in parallel.

Task: Evaluate whether billing should move out of the monolith into a separate service or remain inside the modular monolith with stronger internal boundaries.

Context:
- small team
- PCI scope must stay controlled
- rollout window is 2 quarters
- use system/code graph artifacts first if available

Each agent should return:
- preferred option
- strongest tradeoff
- hard constraints that must shape the design

Wait for all four agents, then synthesize an RFC-style recommendation with a phased plan and explicit dissent.
```

**Debate-first variant**

```text
Before final synthesis, run a debate round with perspectives: architecture, delivery, security, operations.

Debate question: Is the operational and boundary clarity of a dedicated billing service worth the delivery and migration overhead right now?

Produce a decision log with:
- recommendation
- strongest opposing argument
- reversible fallback
- consequences if we delay the split
Then use that decision log in the final RFC synthesis.
```
