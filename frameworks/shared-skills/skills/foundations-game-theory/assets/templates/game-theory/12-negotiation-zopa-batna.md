# Mechanism: Negotiation Protocol (ZOPA/BATNA)

**Source posture**: Nash bargaining and BATNA/ZOPA theory are the durable core. Practitioner AI-negotiation datasets are useful heuristics, not portable benchmarks.

## Domain Applications

- **SaaS pricing negotiation**: map BATNA (next-best alternative for each party) and ZOPA (overlap of acceptable ranges); negotiate on interests (total cost of ownership, integration speed) not positions (list price).
- **Partnership contract terms**: revenue share, exclusivity periods, data rights; ZOPA mapping identifies tradeable items where parties have asymmetric valuations.
- **Resource contention (engineering prioritization)**: two teams competing for shared infrastructure capacity; BATNA = workaround cost; ZOPA = shared roadmap alignment range.
- **Agent team genuine tradeoffs**: when members disagree on a continuous tradeoff (not a binary right/wrong question), switch from adversarial debate (#2) to negotiation protocol to locate the ZOPA.

## Problem

Adversarial debate produces a winner and a loser. Many team decisions are genuine tradeoffs where the right answer is a blend.

## Solution

Each agent states their minimum acceptable outcome (BATNA). Orchestrator finds the zone of possible agreement (ZOPA) and converges on a compromise within that zone.

## How It Works

```
Phase 1: Each agent states:
  - Ideal outcome
  - BATNA (minimum they'd accept)
  - Priority ranking (which constraints they'd relax first)

Phase 2: Orchestrator maps ZOPA
  - ZOPA exists? → propose Nash point (maximize joint utility)
  - No ZOPA? → agent with tightest BATNA relaxes lowest-priority constraint

Phase 3: Agents evaluate proposed compromise
  - Accept / counter-propose / flag dealbreaker
  - One round max. If no deal: escalate to user with ZOPA map.
```

## Operating Rule

Practitioner negotiation datasets suggest "warm" agents that explain why a position matters can produce better joint outcomes than purely numeric bargaining. Treat value-framed BATNAs as a useful default, then verify against the run's actual constraints.

## When To Use

| Team | Negotiation fits when... |
|------|--------------------------|
| startup-monetization-board | Revenue vs. user adoption tradeoff |
| software-architecture-rfc | Performance vs. maintainability vs. delivery speed |
| ops-platform | Reliability vs. cost |
| Any | The answer is a compromise, not a winner |

## Related

- [`09-pareto-nash.md`](09-pareto-nash.md) — Pareto frontier mapping when ZOPA is multi-dimensional
- [`02-adversarial-debate.md`](02-adversarial-debate.md) — use debate when there is a right answer; use negotiation when the answer is a compromise
- [`../../../references/negotiation-protocol.md`](../../../references/negotiation-protocol.md) — full negotiation protocol
