# Mechanism: Generative Social Choice Synthesis

**Source posture**: *Generative Social Choice* ([2309.01291](https://arxiv.org/html/2309.01291v3)) and *Representative Social Choice* ([2410.23953](https://arxiv.org/abs/2410.23953)) — useful as a synthesis discipline, not a guaranteed accuracy gain.

## Domain Applications

- **Product design with diverse user segments**: generate candidate feature descriptions per user segment; maximin selection picks the option that best satisfies the least-satisfied segment; prevents majority-user dominance.
- **Policy or regulatory guidance synthesis**: multiple stakeholder perspectives (regulator, industry, consumer); maximin selection over candidate summaries preserves minority-segment signal that averaging would erase.
- **Content recommendation for heterogeneous audiences**: generate candidates per taste cluster; select the slate that maximizes coverage across the least-represented cluster.
- **Agent team multi-stakeholder decisions**: when the team's output must satisfy multiple downstream user types, generative social choice ensures minority-position evidence survives synthesis.

## Problem

Mechanism-design synthesis (mechanism 7) handles agreed and contradicted findings cleanly, but tends to flatten genuine multi-perspective tradeoffs into the dominant view. Two specific failure modes recur:

- **Averaging** produces middling syntheses that no member would endorse, but each rates as 5/10
- **Loudest-wins** discards minority insight even when it carries unique evidence

The fix is to treat synthesis as a **social-choice problem**: find the candidate statement every member can live with, not the one that maximizes average rating.

## Solution

Generate multiple candidate synthesis statements that take **different stances on disagreement** (compromise / sequential / escalate / defer). Have each member rate each candidate on faithfulness to their evidence. Select by **maximin** — highest minimum rating across members — rather than highest average.

## Protocol

```
Phase 1 — Candidate generation
  Generator (synthesis owner or dedicated synthesizer) produces 3-5
  candidate synthesis statements for the same question. EACH CANDIDATE:
    - Resolves the agreed findings the same way
    - Names the genuine disagreements explicitly
    - Adopts a different stance on how to handle the disagreements
        Compromise — blend positions in the artifact
        Sequential — adopt one position now, revisit at trigger T
        Escalate    — name the disagreement; defer decision to parent thread
        Defer       — pick majority position; preserve minority as dissent

Phase 2 — Member rating
  Each member rates each candidate on three dimensions (0-10):
    Faithfulness — does the candidate represent my evidence accurately?
    Acceptability — would I put my name on this artifact as is?
    Dissent honesty — does it name disagreements where I disagreed?

  Members rate INDEPENDENTLY (no inter-member visibility) to prevent
  collusion or anchoring.

Phase 3 — Maximin selection
  For each candidate, take the MIN rating across members for each dimension.
  Selected candidate = highest minimum on the Acceptability dimension.

  Tie-breakers in order:
    1. Highest minimum on Faithfulness
    2. Highest second-lowest Acceptability rating
    3. Smallest spread between member ratings
    4. Most explicit dissent surfacing
```

## Why Maximin, Not Average

Averaging produces synthesis statements that are mildly acceptable to everyone but excellent to no one — and members with strong minority evidence are systematically outvoted. Maximin selects the statement that the **least-satisfied member** can live with, which forces synthesis to either:
- Genuinely accommodate minority evidence, OR
- Name the dissent explicitly so the minority member can sign off without endorsing

This is the operational form of the truthful-revelation principle from mechanism 7: members are incentivized to rate honestly because their lowest rating is decisive.

## When To Use

- Multi-objective decisions where dominant-perspective synthesis would erase minority evidence (pricing × growth × compliance, performance × maintainability × delivery)
- Cross-functional teams where each member represents a stakeholder whose buy-in matters downstream (architecture RFCs, GTM plans, regulatory submissions)
- Decisions reviewed by people who weren't in the team — explicit dissent surfacing makes the artifact auditable
- Recurring teams where synthesis quality has degraded into "average wins"

## When NOT To Use

- Single-objective questions with a right answer — use mechanism 13 (reasoning-tree audit) instead
- Time-pressured decisions where 3-5 candidate generation is too expensive
- Teams of 2 — maximin collapses to "weakest acceptor," a weak signal at n=2

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| One candidate that just averages perspectives | Force candidates to take *different stances* on disagreement (compromise vs. sequential vs. escalate vs. defer) |
| Members rate by political preference, not evidence faithfulness | Anchor each rating dimension to evidence; "would you put your name on it" is the load-bearing dimension |
| Picking by average rating | Defeats the purpose. Maximin (or highest second-lowest as a tie-break) is the rule |
| Treating dissent as a synthesis failure | Dissent surfacing is a feature; an artifact with no named disagreement when the team disagreed is the failure mode |
| Letting members see each other's ratings before submitting their own | Independent rating prevents anchoring; collect all ratings before revealing |

## Related

- [`07-mechanism-design-synthesis.md`](07-mechanism-design-synthesis.md) — generative social choice is the recommended candidate-selection step inside the truthful-revelation protocol
- [`09-pareto-nash.md`](09-pareto-nash.md) — Pareto frontier mapping when "compromise" needs a frontier rather than a single point
- [`12-negotiation-zopa-batna.md`](12-negotiation-zopa-batna.md) — when the disagreement is over a numeric range, negotiation is more efficient than candidate generation
- [`13-reasoning-tree-audit.md`](13-reasoning-tree-audit.md) — use FPD audit when there is a right answer; use generative social choice when buy-in matters
