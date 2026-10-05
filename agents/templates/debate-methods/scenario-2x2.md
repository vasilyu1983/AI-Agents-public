# Method: Scenario Planning (2×2 Futures)

## Purpose

Build 4 contrasting futures on 2 axes of uncertainty, then test the decision against each. Developed at Royal Dutch Shell by Pierre Wack in the 1970s; still the industry standard for long-horizon strategic decisions under high uncertainty.

## When To Use

- High-uncertainty strategy decisions (GTM model, pivot, fundraise, international expansion)
- Channel prioritization under uncertainty
- Market timing decisions ("is this too early? too late?")
- Competitive response planning
- Long-horizon architecture decisions where the environment may shift
- Any decision where the main risk is "we picked right for today but the world changes"

## When NOT To Use

- Short-horizon execution decisions (the environment doesn't shift enough to matter)
- Low-uncertainty environments (you're overthinking it)
- Single-axis decisions (use Dialectical Inquiry instead)
- Reversible decisions (just pick and adjust; scenario planning is for commitment decisions)

## The 2×2 Structure

Pick **two axes of uncertainty** that are:
1. **Critical** to the decision (changing the axis value would change the right answer)
2. **Uncertain** (you genuinely don't know how they'll resolve)
3. **Independent** (they're not the same axis restated)
4. **Bounded** (each has a clear "low" and "high" end you can describe)

Then build 4 quadrants — one future per corner of the 2×2. Each future gets a short name and a description.

Example axes for "should we go PLG or sales-led for the new product?":
- Axis 1: How willing is our ICP to self-serve? (low → high)
- Axis 2: How complex is our use case to understand? (low → high)

Quadrants:
- **Self-serve + simple** → PLG dominates (clear PLG win)
- **Self-serve + complex** → PLG-led with a sales-assist layer
- **Sales-assisted + simple** → Mixed motion with PLG optional
- **Sales-assisted + complex** → Sales-led dominates (clear sales win)

## Protocol

### Integration With Existing Debate Rounds

**Round 0 (new, pre-debate)**: Orchestrator names the two axes of uncertainty. This is the hardest part of the method — bad axes produce useless scenarios. Name them before launching agents.

**Round 1**: Each of 4 agents takes one quadrant and writes a short scenario (the world in 12-24 months if that quadrant becomes reality). They also write what the decision should be in that world.

**Round 2**: All 4 scenarios are cross-read. Each agent answers:
1. Does the proposed decision work in my quadrant?
2. Which quadrants does the proposed decision fail in?
3. What early signals would tell us which quadrant is emerging?

**Round 3 (synthesis)**: Synthesis owner writes the memo. The decision should either:
- Work well in ≥3 of 4 quadrants (robust decision)
- Work in 2 of 4 and have a clear trigger to pivot (bet-with-hedge decision)
- Work in only 1-2 quadrants — which means it's a bet, and the memo must name the bet explicitly

## Launch Prompt

```text
DEBATE METHOD: Scenario 2×2

Round 0 axis selection:
The orchestrator must name the 2 axes before launching. Axes should be
critical, uncertain, independent, and bounded.

Axis 1: [NAME]
  Low end: [DESCRIPTION]
  High end: [DESCRIPTION]

Axis 2: [NAME]
  Low end: [DESCRIPTION]
  High end: [DESCRIPTION]

Four quadrants:
  Q1 (low Axis 1, low Axis 2): [QUADRANT NAME]
  Q2 (low Axis 1, high Axis 2): [QUADRANT NAME]
  Q3 (high Axis 1, low Axis 2): [QUADRANT NAME]
  Q4 (high Axis 1, high Axis 2): [QUADRANT NAME]

Round 1 instruction (one agent per quadrant):

"You own Quadrant [N]: [NAME]. Your job is to describe this future as if it
has already become reality in 12-24 months.

1. Paint the world. What does this future look like? Be concrete and vivid —
   name specific market conditions, user behaviors, competitor moves.
2. What leading indicators would we see in the next 3-6 months if this future
   is emerging?
3. In this world, what is the right decision for the question we are debating?
4. Is the currently-proposed decision right or wrong in this world?"

Round 2 cross-read instruction:

"Read all four quadrant scenarios. Answer:
1. Does the currently-proposed decision work in your quadrant? Yes / no /
   partial.
2. Which quadrants does the proposed decision fail in? Name them.
3. What early signal would tell us which quadrant we're actually heading
   toward? Be specific — 'conversion rate drops below X' or 'competitor Y
   ships feature Z' or 'segment A churn exceeds B.'"

Synthesis owner instruction:

"Your memo classifies the proposed decision as:
- ROBUST: works in ≥3 of 4 quadrants. Proceed with confidence.
- BET WITH HEDGE: works in 2 of 4 quadrants. Proceed with a named trigger to
  pivot if the signal shifts.
- NARROW BET: works in only 1-2 quadrants. Name the bet explicitly and the
  alternative plan if you're wrong.

For BET and NARROW BET, explicitly list the leading indicators from Round 2
that would trigger a pivot."
```

## Integration With The 3-Of-5 Pattern

Scenario 2×2 wants 4 agents, one per quadrant. In a 5-member team:
1. All 5 members do Round 1 stakeholder reads as normal
2. Pick 4 members for the 4 quadrants (the 5th can synthesize or sit out the Round 1 quadrant work and join synthesis)
3. The 5th member's Round 1 stakeholder read passes in as written context
4. Synthesis owner writes the final memo

In a 3-member team, split the 4 quadrants across 3 agents (one takes 2 quadrants) or drop to 2×1 (just two opposed futures). Running 4 full quadrants with only 3 agents stretches them thin.

## Evidence

- Pierre Wack, ["Scenarios: Uncharted Waters Ahead"](https://hbr.org/1985/09/scenarios-uncharted-waters-ahead), Harvard Business Review, September 1985. The foundational public description of how Shell used scenario planning to anticipate the 1973 oil crisis.
- Peter Schwartz, *The Art of the Long View* (1991) — standard practitioner's guide.
- Kees van der Heijden, *Scenarios: The Art of Strategic Conversation* (2005) — used in most executive education programs as the canonical scenario planning reference.

## Common Mistakes

- **Picking dependent axes**: if Axis 1 and Axis 2 move together, you only have 2 real quadrants, not 4. The axes must be independent.
- **Axes that aren't uncertain**: if you already know how the axis will resolve, it's not an axis of uncertainty. Pick something you actually don't know.
- **Describing scenarios vaguely**: "things get worse" is not a scenario. Name specific market conditions, user behaviors, and competitor moves.
- **Not naming the leading indicators**: the whole point is to know which scenario is emerging. Without specific triggers, the exercise is theoretical.
- **Using it for short-horizon decisions**: scenario planning is for 12+ month horizons. For next-quarter decisions, use a different method.
