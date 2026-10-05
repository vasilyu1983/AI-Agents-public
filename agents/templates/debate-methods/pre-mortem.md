# Method: Pre-Mortem

## Purpose

Imagine the decision has already failed, then work backwards to identify the failure modes you are currently blind to. Gary Klein's 2007 technique, empirically shown to improve risk identification by 30% over forward brainstorming.

## When To Use

- Before shipping a high-stakes release (go/no-go gates)
- Before making a pricing change with meaningful churn or cash-flow downside
- Before a migration or cutover with rollback implications
- Before committing to an architecture decision that will shape 12+ months
- Before a pivot, fundraise, or major GTM shift
- When founder intuition is strong but evidence is thin
- When the team is converging too quickly on a single answer (happy-path thinking)

## When NOT To Use

- Small, reversible decisions (the overhead isn't worth it)
- Execution work with a clear spec
- When the team is paralyzed by risk already — pre-mortem adds to pessimism

## The Core Question

> *"It is now 12 months after this decision. The decision failed spectacularly. Write the autopsy. What happened?"*

That's it. The framing flip — from "what could go wrong?" to "what DID go wrong" — is the entire technique. The past-tense framing bypasses the optimism bias that blocks forward risk brainstorming.

## Protocol

### Integration With Existing Debate Rounds

**Round 1 (unchanged)**: Perspective agents read independently in their stakeholder roles and produce positions.

**Round 2 (pre-mortem overlay)**: Instead of standard rebuttal, each agent rewrites their Round 1 position as an autopsy. The instruction is the same for all agents — they don't split lenses. The diversity comes from their Round 1 stakeholder role.

**Round 3 (synthesis)**: Synthesis owner collects all autopsies and clusters failure modes. Output: a ranked list of failure modes + the specific guardrails or preconditions that would prevent each one.

## Launch Prompt

```text
DEBATE METHOD: Pre-Mortem

Round 2 instruction for each perspective agent:

"Assume this decision has been implemented. It is now 12 months later. The
decision failed spectacularly. The team is writing the autopsy.

From your stakeholder role, answer:

1. What specifically went wrong? Be concrete. Not 'we were not careful enough' but
   'we underestimated the migration lockout window by 4x and lost 18 hours of
   production writes.'

2. What were the early warning signs we ignored? List at least 3.

3. Who saw it coming but was not heard? Why weren't they heard?

4. What would have prevented this? What specific guardrail, test, or pre-condition
   would have caught it before it was too late?

5. Which of these warning signs are *already present* in the current proposal?
   This is the punchline. Be honest."

Synthesis owner instruction:
"Collect all autopsies. Cluster the failure modes. For each cluster:
- Name the failure mode
- Count how many agents independently surfaced it
- Name the specific guardrail that prevents it
- Flag which warning signs are already present in the current proposal

Do not rank by severity. Rank by 'how many independent agents saw it' — that's
the signal for 'this is a real risk, not one person's hobbyhorse.'"
```

## Integration With The 3-Of-5 Pattern

Pre-Mortem works with all 5 members, not 3. The power comes from independent autopsies. Run it as:
1. All 5 members do Round 1 positions
2. All 5 members write autopsies in Round 2 (do NOT reduce to 3)
3. Synthesis owner clusters and ranks

Five autopsies is within the noise ceiling for pre-mortem specifically because each agent is writing in isolation, not debating. Debate cost is what scales poorly, not parallel writing.

## Evidence

- Gary Klein, ["Performing a Project Premortem"](https://hbr.org/2007/09/performing-a-project-premortem), Harvard Business Review, September 2007. Research showed 30% more failure modes identified vs standard brainstorming.
- Daniel Kahneman, *Thinking, Fast and Slow* (2011), ch. 24 — endorses pre-mortem as one of the few reliable de-biasing techniques.
- [Klein, Koller, & Lovallo, "Bias Busters"](https://www.mckinsey.com/) — McKinsey Quarterly validation across strategy reviews.

## Common Mistakes

- **Phrasing as future tense**: "What could go wrong?" is forward brainstorming, not pre-mortem. The past-tense ("it DID fail") is essential.
- **Skipping question 5**: "Which warning signs are already present?" is the payoff. Without it, you have a theoretical risk list, not a decision change.
- **Ranking by severity instead of independent discovery**: one loud voice dominates. Rank by how many agents independently surfaced the same failure — that's the real signal.
- **Running it AFTER the decision is locked**: pre-mortem must happen before commitment. Post-lock, it becomes a CYA exercise.
