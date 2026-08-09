# Mechanism: Auction-Based Task Routing

**Source**: DySOMA framework, cost-effectiveness auctions (2025-2026).

## Domain Applications

- **Ad placement / programmatic bidding**: sealed-bid auction ranks candidates by value-per-cost; truthful bidding is incentive-compatible under second-price rules.
- **Cloud resource allocation**: compute slots allocated to workloads that bid based on urgency × expected yield; prevents priority inversion.
- **Agent team routing**: members bid on task-fit relevance when a question spans multiple specializations; orchestrator selects highest unique-value winner.
- **Freelance / contractor routing**: proposals rated on relevance score + unique contribution preview; static mapping supplemented only when ambiguity exceeds threshold.

## Problem

Static team selection (question → team mapping) doesn't account for context-dependent fit. A pricing question in a fintech context may need different members than the same question in e-commerce.

## Solution

Members "bid" for task relevance based on self-assessed fitness. The orchestrator or synthesis owner selects based on bids.

## Lightweight Auction for Team Selection

When the `team-selection-guide.md` decision map produces ambiguity (multiple teams could fit), run a micro-auction:

```
Orchestrator broadcasts: "[question] + [context summary]"

Each candidate member/team responds with:
  - Relevance score (0-10): how well does this match my specialization?
  - Key insight preview: one sentence of what I'd uniquely contribute
  - Evidence I'd need: what inputs would make my analysis strong?

Orchestrator selects: highest relevance + most unique contribution
```

## When to Use Auction vs. Static Routing

| Situation | Use Static Routing | Use Auction |
|-----------|:------------------:|:-----------:|
| Standard question with clear team match | Yes | No |
| Ambiguous question spanning 2+ teams | No | Yes |
| Novel question not in decision map | No | Yes |
| Recurring review with established team | Yes | No |
| Cross-domain question (e.g., pricing + compliance + growth) | No | Yes — compose custom team from auction winners |

## Launch Prompt Template

```
You are [CANDIDATE_ROLE] in a task auction.

Task: [TASK_DESCRIPTION]
Context summary: [CONTEXT_SUMMARY]

Respond with exactly three fields:
1. Relevance score (0–10): how well does this task match your specialization?
2. Key insight preview: one sentence of what you would uniquely contribute that no other candidate would.
3. Evidence I need: what inputs would make your analysis strong?

Do not explain your score. Do not comment on other candidates. Return only the three fields.
```

Orchestrator selection rule: choose the candidate with highest relevance score; break ties by uniqueness of key insight preview. If two candidates score within 1 point, run a lightweight debate round (#2) on the overlapping scope before final assignment.

## Kill Criteria

Skip this mechanism when:
- The question maps unambiguously to a single team in the static routing guide (no auction needed).
- All candidates are homogeneous (same model, same specialization) — auction produces noise, not signal.
- Latency budget is tight and the marginal routing benefit does not justify one extra LLM round-trip.
- Fewer than two viable candidates exist — an auction with one bidder is just a static assignment.

## Related

- [`../../../references/team-selection-guide.md`](../../../references/team-selection-guide.md) — static routing layer the auction supplements
- [`04-shapley-contribution.md`](04-shapley-contribution.md) — use historical Shapley scores as priors for bid weighting
