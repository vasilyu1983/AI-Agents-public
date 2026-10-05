# Psychological Safety in Code Reviews

Scope: review-comment tone and disagreement handling. General team-culture material is out of scope; see Resources.

## Contents

- [Why It Matters](#why-it-matters)
- [Comment Tone Rules](#comment-tone-rules)
- [Comment Shape](#comment-shape)
- [Precedence for Resolving Technical Disagreements](#precedence-for-resolving-technical-disagreements)
- [Disagreement Steps](#disagreement-steps)
- [Tone Anti-Patterns](#tone-anti-patterns)
- [Resources](#resources)

## Why It Matters

A mixed-methods study in *Empirical Software Engineering* — interviews plus a 423-person survey of agile teams — found that **psychological safety induces social enablers that advance teams' ability to pursue software quality** ("The Role of Psychological Safety in Promoting Software Quality in Agile Teams," Springer). Treat this as support for the practice, not a promise of identical effects. In review terms: people who feel safe raise issues, ask questions, and admit mistakes instead of hiding them.

## Comment Tone Rules

| Rule | Avoid | Prefer |
|------|-------|--------|
| Talk about the code, not the person | "You always miss edge cases" | "This path doesn't handle an empty list; add a guard for `[]`" |
| Explain the why | "Use parameterized queries" | "User input reaches the query string, which allows SQL injection; parameterize it" |
| Ask when you are unsure | "Change this to X" | "question: is there a reason for Y here? X might avoid [issue]" |
| Be specific and actionable | "This could be better" | "Two writers can update this row concurrently; consider optimistic locking with a version field" |
| Don't minimize the work | "Just refactor this" | "Extracting validation would need new unit tests; worth it on this critical path?" |
| Acknowledge what works | Only listing problems | One concrete `praise:` when something is genuinely good |

Label intent explicitly (Conventional Comments: `issue:`, `suggestion:`, `question:`, `nitpick:`, `praise:`, plus REQUIRED/OPTIONAL) so blocking vs non-blocking is clear without relying on tone.

## Comment Shape

```text
<label> (<priority>): <what you observed, with file:line>
Why: <impact — correctness, security, user, operability>
Suggestion: <smallest concrete fix or a question>
```

Example:

```text
issue (P1, REQUIRED): payment/retry.ts:42 retries a non-idempotent charge call.
Why: a timeout after the provider accepted the charge would double-charge the customer.
Suggestion: pass an idempotency key derived from the order ID, or retry only on connection errors.
```

## Precedence for Resolving Technical Disagreements

*Attribution: pattern from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), commit `7676817`, `skills/code-review-and-quality/SKILL.md`. MIT license. Recorded 2026-08-09 in `docs/research/2026-08-09-skill-addyosmani-agent-skills-scan.md`.*

The steps below cover tone and de-escalation. They do not say whose argument wins when good-faith disagreement remains. Use this order:

1. **Technical facts and data override opinions.** A benchmark, a reproduction, a profiler trace, or a citation to the language/framework spec settles the question. Restate the disagreement as "show me the data" before it becomes a style debate.
2. **Style guides are the absolute authority on style matters.** An enforced style guide (linter config, documented convention, prior team decision) decides formatting, naming, and structural-style questions. Reopening a settled call in review is bikeshedding.
3. **Software design is evaluated on engineering principles, not personal preference.** Absent data or a style rule, argue from named principles (coupling, cohesion, testability, blast radius, matching the codebase's conventions), not "I'd just do it this way."

Only escalate once all three levels are checked and the disagreement is still unresolved.

## Disagreement Steps

1. **Understand**: "question: can you help me understand the reasoning behind [decision]?"
2. **State the concern**: "I see the point about [their reasoning]. My concern is [specific issue] because [explanation]."
3. **Offer an alternative**: "Would [alternative] address both concerns?"
4. **Escalate (critical issues only)**: "This matters because [impact]. Can we get input from [owner] before merging?"

When someone disagrees with your feedback: reconsider honestly, look for a middle ground, and let the author decide on OPTIONAL/SUGGESTION items.

## Tone Anti-Patterns

- **Bikeshedding**: many comments on trivial style while logic and risk go unexamined. Let formatters and linters own style.
- **Impact-free nitpicks**: "this function is 51 lines, max is 50." Comment on responsibilities and testability instead.
- **Vague criticism**: "not best practice" with no observed problem or fix.
- **"Just" language**: understates effort and reads as dismissive.
- **Silent approval**: approving without reading is not kindness; it removes the safety net the author relies on.

## Resources

- **Research**: [The Role of Psychological Safety in Promoting Software Quality in Agile Teams](https://link.springer.com/article/10.1007/s10664-024-10512-1) (Empirical Software Engineering, Springer)
- **Related research**: [Understanding and Effectively Mitigating Code Review Anxiety](https://link.springer.com/article/10.1007/s10664-024-10550-9) (Empirical Software Engineering, Springer)
- **Google**: [Google Engineering Practices - Code Review](https://google.github.io/eng-practices/review/)
- **Microsoft**: [Code With Engineering Playbook - Code Reviews](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/)
- **Book**: "The Fearless Organization" by Amy Edmondson
