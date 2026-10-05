# Mask: Regret Minimization

## Purpose

Classify a decision by the shape of its regret curve. Reversible-cheap decisions and irreversible-expensive decisions should be made with completely different rigor. Jeff Bezos's 1997 framework from the founding of Amazon: "project yourself forward to age 80 and ask what you'd regret more — doing this or not doing this?"

## When To Apply

- Any decision where "should we do this at all?" is the real question (not just "how should we do it?")
- Reversibility is ambiguous (is this a "two-way door" or a "one-way door"?)
- Decisions where the team is paralyzed by analysis
- Decisions that get rushed because they feel urgent but are actually reversible
- Career-shaping, fundraise, pivot, or commitment decisions
- Pricing changes with meaningful cohort implications
- Migration decisions ("is this the kind of migration where rollback is realistic?")
- Any decision where one side is treating it as "just a choice" and the other side is treating it as "betting the company"

## Reasoning Rewrite

The mask sorts decisions into two categories, then applies different rigor:

### Two-Way Doors (Reversible)

These are decisions you can walk back from relatively cheaply. For these:
- Bias strongly toward ACTION
- Make them quickly with 70% of the information you'd want
- Plan a review point to check if the decision is working
- Regret minimization question: "Will I regret NOT trying this? If so, try it."

Examples: launching a new landing page variant, trying a new marketing channel, adopting a new internal tool, most reversible product experiments.

### One-Way Doors (Irreversible)

These are decisions that are expensive or impossible to walk back from. For these:
- Bias toward DELIBERATION
- Demand 90% of the information you'd want
- Make them slowly with explicit structured process (dialectical inquiry, pre-mortem, scenario planning)
- Regret minimization question: "Will I regret doing this and finding out I was wrong? If so, what would make me sure?"

Examples: raising a priced round at a high valuation, firing a senior person, committing to a hard pivot, public pricing changes, architectural decisions with 2+ year dependency graphs, reputation-defining PR moves.

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the Regret Minimization mask:

```text
MASK: Regret Minimization

Before analyzing the decision itself, classify it:

STEP 1: Is this a two-way door or a one-way door?

Two-way door: We can walk this back within [reasonable timeframe] at
[reasonable cost]. Specifically:
- If we decide yes and it's wrong, how do we reverse it? What does that cost?
- If we decide no and it's wrong, how do we course-correct? What does that cost?
- If both reverse paths are cheap, it's a two-way door.

One-way door: Walking back is expensive, impossible, or damages something
irrecoverable. Specifically:
- Reputation, trust, relationships, or commitments that can't be un-made
- Capital that can't be un-committed
- Time windows that can't be re-opened
- Competitive advantage or IP that can't be re-captured

STEP 2: Apply the correct regret question.

For two-way doors: "Imagine we did NOT do this. In 12 months, will we regret
not trying? If yes, the bias should be toward action. Speed matters more than
perfection."

For one-way doors: "Imagine we DID this and it was the wrong call. In 5-10
years, will we regret it enough that we would have preferred a slower, more
deliberate decision process? If yes, demand more evidence before committing."

STEP 3: Name the current decision process and check if it matches the door type.

- If this is a two-way door but the team is using heavy deliberation — the
  process is too expensive. Accelerate.
- If this is a one-way door but the team is moving fast — the process is
  dangerously light. Slow down and add structure (pre-mortem, dialectical
  inquiry, devil's advocate).

Return your analysis in three parts:
1. Door classification (one-way or two-way, with reasoning)
2. Regret question applied (the honest answer to the correct question)
3. Process recommendation (speed up or slow down; add or remove structure)
```

## Worked Example

**Decision**: Should we raise prices on existing customers by 30%?

**Step 1 — Door classification**:
- If we raise and lose customers, can we walk it back? Lowering the price again is possible, but damaged trust is hard to rebuild. Customers who churn and tell their network won't un-tell.
- This is a **one-way door** — the reputation component is irreversible.

**Step 2 — Regret question**:
- "Imagine we raised prices and half of existing customers churned. In 5-10 years, would we regret moving fast and not testing the price change in a cohort first?"
- Yes. The regret case for a rushed price change is permanent churn and reputation damage.

**Step 3 — Process check**:
- The team is currently planning to announce the price change next Monday after a 2-week deliberation.
- Recommendation: slow down. This is a one-way door. Run a cohort test with new customers first, or announce the change with a 90-day grandfather window. Add pre-mortem and steel-manning to the decision process.

**Alternative decision**: "Should we try a new email campaign for cold leads?"
- Door: two-way. If it flops, we stop the campaign and no one remembers.
- Regret question: "Will I regret not trying?" Yes — cold lead volume is low enough that any signal is valuable.
- Process: ship it this week. No heavy deliberation needed.

## Common Mistakes

- **Classifying every decision as one-way**: slows the team to a halt. Most decisions are two-way doors and benefit from action bias.
- **Classifying every decision as two-way**: leads to reckless irreversible moves. Ask honestly: "if this is wrong, what exactly is the cost of walking it back?"
- **Skipping step 3**: the point of the mask is changing the decision process, not just labeling the decision. If you classify and don't act on the classification, the mask did nothing.
- **Letting sunk cost affect door classification**: "we've already spent 6 months on this" is not a reason to treat a one-way door as closed. The door type is about the future, not the past.

## Evidence

- Jeff Bezos, 1997 letter to Amazon shareholders (and many public discussions since). The "regret minimization framework" is Bezos's most-cited decision heuristic.
- Amazon's "Type 1 vs Type 2 decisions" framework from the 2015 shareholder letter formalizes the one-way/two-way door distinction.
- Daniel Kahneman and Amos Tversky's research on loss aversion (*Thinking, Fast and Slow*, 2011) — regret minimization works because humans systematically over-weight future regret relative to current gain; leaning into that bias for irreversible decisions and against it for reversible ones produces better outcomes than "rational" expected-value analysis.
