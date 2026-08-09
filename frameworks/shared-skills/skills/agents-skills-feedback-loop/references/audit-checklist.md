# Audit Checklist

Run periodically (monthly) across all wired skills to catch loop drift.

## Mechanical Checks

For every skill that has a `learnings.md` or `learnings.consolidated.md`:

1. **Addendum present?** Does `SKILL.md` contain the *Learnings Loop* section? If not, the loop is orphaned.
2. **Both files within caps?** Raw ≤150, consolidated ≤60.
3. **Dates well-formed?** Every entry starts with `- [YYYY-MM-DD]`.
4. **One bullet per entry?** No multi-paragraph entries.
5. **No undated entries?** Reject.
6. **Section headers match the canonical five?** No invented sections except the optional `## Filter Override`.

Run:

```bash
for skill in frameworks/shared-skills/skills/*/; do
  if [ -f "$skill/learnings.consolidated.md" ]; then
    python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/consolidate.py "$skill" --audit
  fi
done
```

## Semantic Checks (human)

- **Stale entries.** Any entry older than 90 days that has not recurred — flag for removal.
- **Promotion-out candidates.** Consolidated entries that have been stable for 3+ cycles — promote to host's `references/` and remove from loop.
- **Contradictions.** An entry contradicts the host skill's `SKILL.md` — fix the skill, not the loop.
- **Cross-skill leakage.** An entry that really belongs in another skill — move it.
- **Generic advice.** An entry that is really a coding rule — move to `CLAUDE.md` or `coding-behavior.md` and delete from loop.

## Orphan Detection

A loop is orphaned when:

- Host skill was renamed or deleted but learnings files remain.
- Host skill's `SKILL.md` no longer carries the addendum (someone edited it out).
- Last append was >180 days ago AND consolidated is empty.

Action: delete the loop files. Do not preserve.

## Reporting

The audit produces a single line per skill:

```
<skill>  raw=<n>/150  consolidated=<n>/60  oldest=<YYYY-MM-DD>  addendum=<yes|no>  status=<ok|warn|orphan>
```

Anything not `status=ok` needs a human pass.
