# Method: Polarity Management

## Purpose

Recognize that some "problems" are actually polarities — ongoing tensions to be managed, not solved. Map the upside and downside of each pole over time, then design a management system that rides the tension instead of trying to pick a winner. Barry Johnson's 1992 framework from *Polarity Management: Identifying and Managing Unsolvable Problems*.

## When To Use

- Ongoing tensions that keep returning no matter how many times you "decide": speed vs quality, centralization vs autonomy, growth vs profit, feature velocity vs stability
- Platform architecture tradeoffs (reliability vs cost, flexibility vs simplicity)
- Org design decisions (specialists vs generalists, remote vs in-person, process vs autonomy)
- Any time you notice: "we keep having this debate and picking one side, then the other side's downsides hit us, then we pick the other side, and the cycle repeats"
- When the debate is framed as "A or B" but actually both are needed

## When NOT To Use

- Genuine either/or decisions (use Dialectical Inquiry)
- One-time decisions (polarities are about ongoing management, not point decisions)
- Decisions where one pole has no upside (that's not a polarity, that's just a wrong answer)

## The Polarity Map

For any polarity, draw a 2×2 grid with the two poles at the top and "upside" / "downside" on the vertical axis:

```
                      Pole A                      Pole B
                      ─────                       ─────
Upside         [+A: what's great       [+B: what's great
                    about A]                  about B]

Downside       [−A: what hurts         [−B: what hurts
                    when overused]            when overused]
```

The key insight: **the downsides of over-using one pole look exactly like the upsides of the other pole**. That's why teams oscillate — they run away from a pole's downside into the opposite pole's upside, then discover its downside, then swing back.

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (new, pre-debate)**: The orchestrator diagnoses the polarity. If the debate has been happening repeatedly (more than twice in a quarter), suspect a polarity. Name the two poles explicitly.

**Round 1**: Split agents into two groups. Group A advocates for pole A, group B for pole B. Each group fills in the upside of their pole AND the downside of the opposite pole (they're the same thing from different angles).

**Round 2**: Agents fill in the downsides of their own pole (when overused). This is the hard part — defending your pole while honestly naming its failure modes.

**Round 3 (synthesis)**: Synthesis owner writes a management system, not a decision. The memo should include:
- Early warning signs that we're over-indexing on pole A (downside symptoms)
- Early warning signs that we're over-indexing on pole B (downside symptoms)
- The shift action when each warning fires
- The target state: constant small corrections between poles, not a fixed point

## Launch Prompt

```text
DEBATE METHOD: Polarity Management

Round 0 polarity diagnosis:
The debate topic is: [DECISION]
This is a polarity if: the team has debated this more than twice before OR
both sides have strong ongoing arguments OR picking one side historically led
to the other side's problems emerging.

Name the two poles:
Pole A: [NAME]
Pole B: [NAME]

Assign agents:
Group A (2 agents): defend pole A
Group B (2 agents): defend pole B
Synthesis: 1 agent (team's synthesis owner)

Round 1 instruction (both groups):

"Your group is defending [POLE X]. Fill in two quadrants of the polarity map:

1. UPSIDE OF [POLE X]: What is great about this pole? What benefits does it
   deliver when we commit to it? Name concrete examples.

2. DOWNSIDE OF [OPPOSITE POLE]: What hurts when the other pole is over-used?
   These are the same insights from a different angle — the upside of your
   pole and the downside of the opposite pole describe the same underlying
   reality.

List at least 3 items in each quadrant with concrete examples."

Round 2 instruction (both groups):

"Now fill in the downside of YOUR pole. This is uncomfortable — you're defending
this pole, but you must honestly name what goes wrong when it's over-used.

DOWNSIDE OF [POLE X]: What hurts when this pole is over-used or pursued to the
exclusion of the other? Name the specific symptoms that appear when the team
has gone too far in this direction.

List at least 3 items with concrete examples. If your list is short or vague,
the other group will fill it in for you later — and they will not be gentle."

Synthesis owner instruction (Round 3):

"Your memo is a MANAGEMENT SYSTEM, not a decision. Deliver:

1. The full 2×2 polarity map with both groups' inputs.

2. Early warning signs for over-indexing on pole A: What symptoms tell us we've
   gone too far toward A? These come from Group A's Round 2 admissions.

3. Early warning signs for over-indexing on pole B: Same, from Group B.

4. The shift action: When we see pole A downside symptoms, we shift toward B
   in these specific ways: [list]. Same for B → A.

5. The target state: describe what 'healthy oscillation' looks like. The team
   is never at a fixed point; it's making constant small corrections.

6. A named review cadence: when will we re-check the polarity? (Monthly,
   quarterly, per release?)"
```

## Integration With The 3-Of-5 Pattern

Polarity Management fits 5-member teams naturally:
1. Split 2-2-1: two agents per pole, one synthesizer
2. Each pole gets parallel development in Round 1
3. Honest downside admissions in Round 2
4. Synthesis writes the management system
5. No reduction needed

For a 3-agent team: 1-1-1 split is workable, but the polarity map loses depth with only one defender per pole.

## Evidence

- Barry Johnson, *Polarity Management: Identifying and Managing Unsolvable Problems* (1992). Still the canonical reference; used in executive coaching, org development, and change management.
- [Polarity Partnerships](https://www.polaritypartnerships.com/) — active practitioner community; used at Johnson & Johnson, Cisco, and across healthcare org design work.
- Jim Collins and Jerry Porras, *Built to Last* (1994) — the "genius of the AND" argument against "tyranny of the OR" is a polarity-management insight, even though Collins doesn't use the term.

## Common Mistakes

- **Treating a polarity as a problem**: the whole point is that polarities don't have solutions. If you try to "solve" a polarity, you'll be back debating it in 6 weeks.
- **Picking a pole**: even if one pole seems obviously correct now, the downsides will emerge. Polarities are about oscillating within a range, not picking a fixed point.
- **Skipping the honest downside admission**: if each group refuses to name the downsides of their own pole, the polarity map is theater.
- **No review cadence**: without a scheduled re-check, the team will drift to an extreme and forget to correct.
- **Using it for one-time decisions**: polarities are ongoing. A one-time architecture decision (monolith vs microservices, committed once) is not a polarity — it's a dialectical choice.
