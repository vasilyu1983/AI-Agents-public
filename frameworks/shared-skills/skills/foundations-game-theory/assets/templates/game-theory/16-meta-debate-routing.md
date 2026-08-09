# Mechanism: Meta-Debate Role Routing

**Source**: *Dynamic Role Assignment for Multi-Agent Debate* ([arxiv 2601.17152](https://arxiv.org/abs/2601.17152), Jan 2026). Up to **+74.8% over uniform role assignment**, **+29.7% over random** assignment, depending on task.

## Problem

Debate frameworks assign roles (plaintiff, defense, judge, critic) at team launch using static rules — usually "the most relevant specialist gets plaintiff." But model specializations are not leveraged at the *role* level. A reviewer that's better at finding flaws than at building arguments is wasted as plaintiff. Capability-aware role assignment requires choosing roles **after** seeing the question.

## Solution

Run a brief **meta-debate** before the actual debate. Candidate members produce role-tailored proposals; peer review scores them; the orchestrator selects which member fills which role. Then the actual debate begins with the selected lineup.

This is the auction mechanism (3) generalized to **role-specific bidding** rather than team-membership bidding. Mechanism 3 picks who joins the team; mechanism 16 picks who plays which position.

## Distinction From Mechanism 3 (Auction Task Routing)

| Aspect | Auction Routing (3) | Meta-Debate Routing (16) |
|---|---|---|
| Question | Which members should be on the team? | Given the team, which member fills which role? |
| Bid content | Relevance score + insight preview | Role-tailored proposal demonstrating fit for the specific role |
| Selection criterion | Highest relevance + uniqueness | Best peer-reviewed proposal for that role |
| Output | Team composition | Role-to-member mapping |
| Cost | Single round, light | Two-stage (proposal + peer review), moderate |

The two mechanisms compose: auction first to pick the team, meta-debate second to assign roles within it.

## Protocol

```
Phase 1 — Proposal stage
  For each role R in the debate (plaintiff, defense, judge, critic, etc.):
    Each candidate member produces:
      - Role-tailored argument: "If I played R, here is the strongest
        opening I would make for THIS specific question."
      - Reasoning: why my specialization fits R for this question
      - Evidence preview: the key citation or signal I'd lead with

Phase 2 — Peer review
  Each candidate scores other candidates' proposals (NOT their own) on:
    - Argument quality for the assigned role
    - Distinctiveness from what other candidates offered
    - Evidence richness
    - Role fit (does the proposal demonstrate the role's distinct posture?)

  Self-scoring is excluded to prevent gaming.

Phase 3 — Role assignment
  Orchestrator picks the best-rated candidate per role.
  Conflicts (one candidate wins multiple roles) resolved by:
    1. Member's highest-scoring role goes first
    2. Their second-place roles go to the next-highest-rated alternative
    3. If no qualified backup exists for a role, escalate to parent thread

Phase 4 — Actual debate
  Run the chosen debate method (courtroom / dialectical / etc.) with the
  role-assigned members. Meta-debate output is logged but not re-litigated.
```

## When To Use

- Cross-domain questions where the "obvious" specialist may not be the best plaintiff
- Teams where multiple members have overlapping specializations and static rules underuse some of them
- High-stakes debates where +5pp accuracy is worth one extra meta-round
- Debates that recur — meta-debate logs reveal which members consistently win which roles, which feeds back into static routing for similar questions

## When NOT To Use

- Trivial debates where role assignment is unambiguous (one obvious plaintiff, one obvious defense)
- Time-pressured decisions — meta-debate adds a full round of latency
- Teams of 2 — only one valid role assignment, so meta-debate is pure overhead
- Synchronous debates with strict round budgets — eats into the actual debate

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Letting candidates self-score in peer review | Exclude self-scoring; manipulators always win otherwise |
| Generic proposals ("I'd argue thoroughly") | Require role-tailored content — opening line, citation, framing — to score |
| Treating meta-debate output as the actual debate | The meta-round is for *role selection only*; the real debate starts fresh |
| Skipping meta-debate when only one role is contested | If only one role is ambiguous, run meta-debate for that role only |
| Logging proposals without using them later | Track which member wins which role across runs to refine static routing for similar questions |

## Related

- [`03-auction-task-routing.md`](03-auction-task-routing.md) — pick the team first, then run meta-debate to assign roles within it
- [`02-adversarial-debate.md`](02-adversarial-debate.md) — meta-debate routing improves the role assignment for any debate mechanism
- [`08-courtroom-proclaim.md`](08-courtroom-proclaim.md) — courtroom is the highest-leverage place to apply meta-debate routing (5 distinct roles)
- [`05-reputation-gating.md`](05-reputation-gating.md) — reputation tier feeds peer-review weighting in meta-debate
