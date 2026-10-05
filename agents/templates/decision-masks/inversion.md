# Mask: Inversion

## Purpose

Reframe a decision backwards. Instead of asking "how do we succeed?", ask "how would we guarantee failure, and then avoid those actions." Charlie Munger's adaptation of Carl Jacobi's mathematical principle: "invert, always invert."

## When To Apply

- Architecture decisions where happy-path thinking dominates
- Risk and compliance reviews (payments, security, data protection)
- Release gating ("what would guarantee a failed launch?")
- Migration planning ("what would guarantee a broken cutover?")
- Pricing decisions ("what would guarantee customer churn?")
- Any decision where the upside is being over-weighted and downside is under-examined
- Founder blindspot reviews (inversion exposes optimism bias)

## Reasoning Rewrite

The mask changes the question being asked:

| Original question | Inverted question |
|---|---|
| How do we make this launch successful? | How would we guarantee a failed launch? Then avoid those actions. |
| What architecture should we pick? | What architecture would most likely break in 2 years? Then don't pick that. |
| How do we grow this product? | What would most effectively kill growth? Then stop doing those things. |
| How do we raise prices safely? | What pricing change would guarantee a churn wave? Then don't do that. |
| How do we onboard users faster? | What onboarding flow would make users give up? Then fix those specific friction points. |
| How do we pass this customer's security review? | How would we fail their security review? Then harden those specific areas. |

The key: inversion doesn't replace the original question. It runs alongside and exposes blind spots the forward framing misses.

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the Inversion mask:

```text
MASK: Inversion

In addition to your normal analysis, you must also answer the inverted question.
Do not skip this — the inversion is what the mask is for.

Inverted question: "What would most effectively GUARANTEE failure of this
decision? List at least 5 specific actions, policies, or choices that would
make failure inevitable. Then flag which of those failure-causing patterns
are already present (even partially) in the current proposal."

The inverted question is not a risk list. A risk list says "things that might
go wrong." The inverted question says "things that would RELIABLY cause
failure if we did them on purpose." The difference is intentionality.

Return your analysis in two parts:
1. Forward analysis (your normal stakeholder-role read)
2. Inverted analysis (the 5+ failure-guaranteeing actions and which are
   already present)

The inverted analysis is often more valuable than the forward analysis.
Do not rush it or list vague platitudes like "bad planning" — name specific
actions.
```

## Worked Example

**Decision**: Should we migrate from Postgres to a distributed SQL database for the main product database?

**Forward analysis** (standard): Scalability wins, eventual consistency, operational complexity, migration cost, rollback risk, etc.

**Inverted analysis**: "How would we guarantee this migration fails catastrophically?"
1. Cut over during peak traffic without a parallel-run period
2. Skip the query-compatibility audit for existing ORMs and hand-written SQL
3. Under-provision the new cluster based on current average load (not peak + 50%)
4. Don't train the on-call team on the new database's failure modes before cutover
5. Migrate on a Friday afternoon before a long weekend
6. Assume the existing monitoring and alerting works on the new cluster without re-validation

Then the check: **which of these are already in the current plan?** If the plan says "cutover in Q4" without naming the traffic window, #1 is partially present. If the plan doesn't mention a query audit, #2 is present. That's where the decision actually needs to change.

## Common Mistakes

- **Treating inversion as a risk list**: risks are things that might go wrong. Inversion is things that would reliably cause failure if done on purpose. The intentionality matters — it sharpens the thinking.
- **Listing vague failure modes**: "bad execution" or "under-preparation" are not useful. Name specific actions.
- **Skipping the "already present" check**: the whole point is finding which failure-causing patterns are already in the proposal. Without that step, inversion is academic.
- **Using it on every decision**: inversion is heavy. Use it when upside thinking dominates, not as a default.

## Evidence

- Charlie Munger, "The Psychology of Human Misjudgment" (1995 Harvard speech, expanded in *Poor Charlie's Almanack*). Munger adopted the principle from 19th-century mathematician Carl Jacobi's "man muss immer umkehren" ("one must always invert").
- Widely cited in Farnam Street's decision-making literature and Berkshire Hathaway shareholder letters.
