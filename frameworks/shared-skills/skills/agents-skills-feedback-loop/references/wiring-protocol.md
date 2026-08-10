# Wiring Protocol

How to opt a skill into the learnings loop. Five mechanical steps.

## Step 1 — Seed the files

From the host skill's directory (e.g. `frameworks/shared-skills/skills/project-taxation/`):

```bash
cp ../agents-skills-feedback-loop/assets/learnings.template.md ./learnings.consolidated.md
# learnings.md is created on first append by the script; do not pre-create empty.
```

Edit the header of `learnings.consolidated.md` to name the host skill.

## Step 2 — Add the addendum to `SKILL.md`

Append this block, verbatim, near the end of the host's `SKILL.md` (before any `## See Also`):

```markdown
## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
```

No other edit to the host skill is required.

## Step 3 — Confirm the commit policy

Both `learnings.md` (raw) and `learnings.consolidated.md` are **committed** — this
is deliberate, for multi-machine continuity (May 2026 consensus). Only the
optional machine-specific file is gitignored. The repo-root `.gitignore` carries:

```
frameworks/shared-skills/skills/*/learnings.local.md
```

Verify before first append: `git check-ignore -v <skill>/learnings.local.md`
should match, and `<skill>/learnings.md` should NOT be ignored. If your fork wants
raw learnings kept local instead, add `frameworks/shared-skills/skills/*/learnings.md`
to `.gitignore` and document the override — but the repo default is committed.

## Step 4 — First append (smoke test)

```bash
python3 frameworks/shared-skills/skills/agents-skills-feedback-loop/scripts/append_learning.py \
  frameworks/shared-skills/skills/project-taxation \
  --section "Patterns That Work" \
  --text "Learnings loop wired on $(date +%Y-%m-%d); confirms file shape."
```

Confirms the script can read the directory and write a valid entry.

## Step 5 — Register the host in `agents-skills-feedback-loop`'s consolidated registry (optional)

If you want a portfolio view of which skills have loops wired, add a line to `agents-skills-feedback-loop/learnings.consolidated.md` under *Domain Knowledge*:

```markdown
- [YYYY-MM-DD] Loop wired into `project-taxation`. Filter override: HMRC-anchored only.
```

## Override Filters (when the default is wrong)

The default *what counts as a learning* filter lives in `references/learnings-format.md`. To override for a specific skill, add a section to that skill's `learnings.consolidated.md`:

```markdown
## Filter Override
- Reject entries not citing an HMRC manual section or a dated statute.
- Reject entries about UI/UX (out of scope for this skill).
```

`append_learning.py` reads this section if present and warns when a candidate entry would violate it. Enforcement is advisory; the operator still decides.

## When Not to Wire

- The host skill is one-off, internal, or wraps a stable API with no edge cases.
- The host skill is a router (`router-*`) — routers should not accrue domain memory.
- The host skill is itself memory infrastructure (`agents-memory`, `agents-skills-feedback-loop`).
