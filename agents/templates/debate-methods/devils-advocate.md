# Method: Devil's Advocate (Formal Opposition)

## Purpose

Pre-assign one agent the role of formal opposition, regardless of their actual view. Structurally prevents groupthink by guaranteeing at least one dissenting voice per debate. The Catholic Church's original 1587 design (*advocatus diaboli*) for canonization review — still the canonical pattern after 450 years.

## When To Use

- Any debate where groupthink risk is high (homogeneous team, time pressure, strong consensus forming too fast)
- Incident response rollback vs fix-forward decisions
- Enterprise-readiness reviews (customer diligence is adversarial by design)
- Release go/no-go gates
- Pricing changes when everyone on the team "feels good" about the new price
- Architecture RFCs where the current preferred direction has no internal opposition
- Any decision where the cost of being wrong exceeds the cost of appointing an opposer

## When NOT To Use

- When genuine disagreement is already present in Round 1 (the formal opposer becomes redundant)
- Low-stakes reversible decisions
- Pure creative exploration (use Six Hats green-hat mode instead)

## The Role

One agent is pre-assigned to oppose the decision, regardless of what they would naturally think. They are not a contrarian — they are a structured opposer. Their job:

1. **Argue the strongest case against** the proposal, not the weakest
2. **Steel-man the opposition** — the version the team would most struggle to refute
3. **Name specific failure modes** with evidence, not vague concerns
4. **Propose a concrete alternative**, not just criticism
5. **Stay in role even if they personally agree** with the proposal

This is not "the skeptic" or "the pessimist." Those are natural dispositions. The devil's advocate is a structural role assigned for this one debate.

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (new, pre-debate)**: Orchestrator picks one agent and assigns them the devil's advocate role. The other agents are told who the devil's advocate is so they don't mistake opposition for genuine disagreement.

**Round 1 (modified)**: The devil's advocate writes their position as formal opposition. Other agents write their natural positions in their stakeholder roles.

**Round 2**: Standard rebuttal. Other agents must directly address the devil's advocate's strongest points. They cannot ignore the opposition.

**Round 3 (synthesis)**: Synthesis owner explicitly records whether the devil's advocate's strongest points were resolved, partially addressed, or left open. Unresolved opposition is flagged as a decision risk.

## Launch Prompt

```text
DEBATE METHOD: Devil's Advocate

Round 0 assignment:
- Devil's advocate: [AGENT NAME, ROLE]
- All other agents: told in their brief that [AGENT] is the formal opposer

Devil's advocate brief (Round 1):

"You are the formal opposition for this debate. Your assigned role overrides
your natural view. Regardless of what you actually think about this proposal,
your job is to build the strongest possible case against it.

Requirements:
1. Present the strongest argument against the proposal — not the easiest to
   refute. Imagine a skeptical buyer, a hostile auditor, or a competitor looking
   for weakness.
2. Name at least 3 specific failure modes with concrete evidence or precedent.
3. Propose a concrete alternative that addresses the same underlying goal.
4. Do not hedge. Do not say 'on the other hand.' Your job is opposition, not
   balance.
5. Stay in role for all debate rounds. You can update your stance in the final
   synthesis, but not during the debate itself."

Other agents' brief:
"Note: [AGENT] is the formal devil's advocate for this debate. Their opposition
is a structural role, not their natural view. You must directly address their
strongest points in Round 2 — you cannot dismiss the opposition as biased or
ignore it."

Synthesis owner instruction:
"Explicitly record:
- Which of the devil's advocate's points were resolved in debate
- Which were partially addressed
- Which were left open
Unresolved opposition is a decision risk. Flag it in the final memo."
```

## Integration With The 3-Of-5 Pattern

Devil's Advocate works cleanly with 3-of-5. In the Round 2 selection:
1. All 5 members do Round 1 reads in their stakeholder roles
2. Pre-assigned devil's advocate is one of the 3 selected for Round 2
3. The other 2 are picked for being most opposed to the devil's advocate's position
4. Synthesis owner stays neutral

## Evidence

- Catholic Church, *Promotor Fidei* (Promoter of the Faith), instituted 1587 by Pope Sixtus V. Formal opposition in canonization reviews; abolished as mandatory in 1983 but the pattern persists.
- [Janis, *Groupthink* (1972)](https://en.wikipedia.org/wiki/Groupthink) — Irving Janis's foundational work on group decision failures, explicitly recommends pre-assigned devil's advocate as a structural antidote.
- CIA Red Teams, military war-gaming, Israeli Defense Forces' "Tenth Man Rule" (if 9 agree, the 10th is obligated to oppose).

## Common Mistakes

- **Assigning the role to the natural skeptic**: the point is structural opposition from someone who doesn't naturally oppose. If the "assigned opposer" is already the team contrarian, the role has no effect.
- **Letting the devil's advocate hedge**: "well, I kind of see both sides" defeats the method. Enforce the no-hedging rule.
- **Ignoring opposition in synthesis**: the memo must name whether the devil's advocate's points were resolved. Skipping this step turns the exercise into theater.
- **Running it on low-stakes decisions**: the overhead (one agent committing to structural opposition) is only worth it on decisions where being wrong hurts.
