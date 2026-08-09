# Learnings File Format

## Shape

Two files, same five sections, different lifecycles.

```markdown
# <Skill Name> — Learnings

## Patterns That Work
- [YYYY-MM-DD] One sentence. Concrete enough to change behavior next time.

## Mistakes to Avoid
- [YYYY-MM-DD] What failed, why, and the one-line prevention rule.

## Domain Knowledge
- [YYYY-MM-DD] A fact about the domain that the model would not infer from the codebase.

## Open Questions
- [YYYY-MM-DD] An unresolved question worth carrying forward. Remove when answered.

## Consolidated Principles
- [YYYY-MM-DD] A synthesized rule promoted from repeated patterns. Only present in `learnings.consolidated.md`.
```

## Rules for One Good Entry

- **Atomic.** One insight per bullet. If you need a colon and a comma, split it.
- **Dated.** ISO `YYYY-MM-DD`. Relative dates ("last week") are rejected on append.
- **Behavior-changing.** If knowing this entry would not change what the next session does, it is a comment, not a learning. Cut it.
- **Specific.** "Webhook needs HMAC in header, not body" beats "be careful with webhook auth."
- **Self-contained.** A reader who has not seen the original session must understand the entry. No "we", no "the bug from yesterday".

## Quality Filters

✅ Include:

- Concrete API/schema/protocol behavior that surprised you
- A workaround whose reason is non-obvious from the code
- An anti-pattern that produced a real incident or rework
- A dated domain fact (statute, scheme rulebook, vendor policy) with a citation

❌ Exclude:

- Generic coding advice (belongs in `CLAUDE.md` or `coding-behavior.md`)
- One-off situations unlikely to recur
- Content already documented in the codebase
- Anything that reads like a diary entry ("today I learned…")

## Section Choice (when in doubt)

| Situation | Section |
|---|---|
| Approach worked, would use again | Patterns That Work |
| Approach failed, would avoid | Mistakes to Avoid |
| Fact about the world, not about a choice | Domain Knowledge |
| Something you want to investigate later | Open Questions |
| Rule synthesized from ≥2 prior entries | Consolidated Principles |

## Length and Aging

- Raw `learnings.md`: hard cap 150 entries. At cap, `append_learning.py` refuses and prints the consolidate command.
- Consolidated `learnings.consolidated.md`: hard cap 60 entries. At cap, promote to `references/` of the host skill.
- Unconsolidated entries older than 90 days are flagged for removal during consolidation unless re-dated by recurrence.
