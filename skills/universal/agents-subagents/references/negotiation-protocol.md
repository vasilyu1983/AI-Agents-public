---
description: ZOPA/BATNA compromise-finding for tradeoff decisions when adversarial debate would force a false winner.
last_verified: 2026-09-02
status: stable
---

# Negotiation Protocol (ZOPA/BATNA)

When team members disagree and the right answer is a COMPROMISE (not a winner), run a negotiation instead of a debate. Each agent states their minimum acceptable outcome (BATNA), the orchestrator finds the zone of possible agreement (ZOPA), and the team converges on a solution within that zone.

## Why Debate Fails for Tradeoffs
Debate produces a winner and a loser. But many team decisions are genuine tradeoffs: performance vs. maintainability, growth vs. monetization, security vs. UX. The "right answer" is a blend, not picking one side. Negotiation finds the blend.

## Key Concepts
- BATNA (Best Alternative To Negotiated Agreement): each agent's walk-away point — the worst outcome they'd accept
- ZOPA (Zone Of Possible Agreement): the overlap between all agents' BATNAs — where a deal is possible
- Nash Bargaining Solution: the point in the ZOPA that maximizes the product of each agent's utility above their BATNA — the "fairest" compromise

## Mechanism
Phase 1: Each agent states their position AND their BATNA (minimum acceptable outcome)
Phase 2: Orchestrator maps the ZOPA — where all BATNAs overlap
Phase 3: If ZOPA exists → find the Nash point (maximize joint utility above BATNAs)
Phase 4: If no ZOPA → agents must relax their least important constraint and re-submit

## Protocol (detailed)
Round 1: Each agent states:
  - Ideal outcome (what they'd want if unconstrained)
  - BATNA (minimum acceptable — the worst they'd live with)
  - Priority ranking of their constraints (which ones they'd relax first)
  - Warm framing (explain WHY their position matters, not just WHAT it is)

Round 2: Orchestrator computes:
  - ZOPA exists? (all BATNAs overlap somewhere)
  - If yes: propose Nash point (or simple midpoint if utility functions unknown)
  - If no: identify which agent's BATNA is the tightest and ask them to relax their lowest-priority constraint

Round 3: Agents evaluate the proposed compromise:
  - Accept, counter-propose, or flag dealbreaker
  - One more round max. If no agreement: escalate to the user with the ZOPA map.

## When To Use
- `expert-board` monetization mode: pricing tradeoffs (revenue vs. user adoption)
- `expert-board` architecture-rfc mode: performance vs. maintainability vs. delivery speed
- `expert-board` ops-platform mode: reliability vs. cost
- Any decision where agents will disagree AND the answer is a blend, not a winner
- Product feature scoping (what to cut vs. keep)

## When NOT To Use
- Binary decisions (build vs. buy) — use Dialectical Inquiry
- When one agent is clearly the domain authority — defer, don't negotiate
- When there's no tradeoff (all agents agree) — just execute

## Key Findings
- 180K AI negotiations (Herle 2026): warm agents consistently outperformed cold rational optimizers
- Negotiation with injected empathy produces better joint outcomes than pure game-theoretic optimization
- Nash Bargaining Solution provides a principled fairness point when utility functions are known

## Common Mistakes
- Agents stating BATNA as their ideal (negotiating in bad faith — need honest minimums)
- Orchestrator averaging positions instead of finding ZOPA (averaging ignores constraints)
- Running negotiation when the question is binary (negotiation is for continuous tradeoffs)
- Not establishing priority ranking upfront (agents resist relaxing any constraint equally)

## Sources
- AI Negotiation: 180K Negotiations. Medium, Herle 2026.
- Nash Bargaining Solution and BATNA. Game theory foundations.
- ZOPA in AI agent systems. Prospeo 2026.
