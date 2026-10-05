# Zero-to-Working Recipe: Empty Repo → Working AGENTS.md / CLAUDE.md

A copy-paste 5-step recipe. From a repo with no agent memory files to a working setup in under 10 minutes.

## Table of Contents

- [Step 1 — Create the project memory file for your runtime](#step-1--create-the-project-memory-file-for-your-runtime)
- [Step 2 — Verify the agent reads it](#step-2--verify-the-agent-reads-it)
- [Step 3 — Add a validation script (optional but recommended)](#step-3--add-a-validation-script-optional-but-recommended)
- [Step 4 — Add a .claude/ memory folder for project-specific context (optional)](#step-4--add-a-claude-memory-folder-for-project-specific-context-optional)
- [Step 5 — Commit and confirm](#step-5--commit-and-confirm)
- [Common Mistakes at Setup](#common-mistakes-at-setup)
- [References](#references)

---

## Step 1 — Create the project memory file for your runtime

Pick the file that matches how you launch the agent:

| Runtime | File to create | Location |
|---------|---------------|----------|
| Claude Code | `CLAUDE.md` | repo root |
| Codex / OpenAI Agents SDK | `AGENTS.md` | repo root |
| Both | Both files | repo root (can share content or symlink one to the other) |

**Minimal CLAUDE.md to paste in:**

```markdown
# Project Instructions

## What This Repo Is
This repo is [one sentence: what does this codebase do?].

## Boundaries

### Always Do
- [non-negotiable steps the agent must follow, e.g. "run tests before committing"]

### Ask First
- Rename files or directories
- Remove or restructure public APIs

### Never Do
- Commit secrets, credentials, or PII
- [any hard prohibitions specific to this repo]

## Stack
- Language: [e.g. TypeScript, Python]
- Framework: [e.g. Next.js, FastAPI]
- Test runner: [e.g. Jest, pytest]
- Package manager: [e.g. npm, uv]

## Run / Test / Lint
```bash
# Run locally
[insert command]

# Run tests
[insert command]

# Lint
[insert command]
```

## Start Here (load on demand)
- `docs/architecture.md` — system design (load only when task touches architecture)
```

---

## Step 2 — Verify the agent reads it

Start a new Claude Code session in the repo and run:

```
/context
```

You should see your CLAUDE.md under **Memory files**. If it is not listed, confirm the file is in the repo root and that you are inside the repo directory when you launched the session.

For Codex, confirm with:

```bash
codex --show-context
```

---

## Step 3 — Add a validation script (optional but recommended)

If the repo uses the `agents-memory` skill, a lint script already exists. Run it to catch common problems:

```bash
bash skills/universal/agents-memory/scripts/lint_claude_memory.sh .
```

If you are not using the shared-skills framework, create a minimal check:

```bash
#!/usr/bin/env bash
# scripts/check_agent_memory.sh
set -euo pipefail

FILE="${1:-CLAUDE.md}"
[[ -f "$FILE" ]] || { echo "MISSING: $FILE"; exit 1; }

# Check for unresolved template placeholders
if grep -qE '\[.*\]' "$FILE"; then
  echo "WARN: $FILE may still contain placeholder text (lines with [brackets])"
fi

# Check it is not empty
wc_lines=$(wc -l < "$FILE")
[[ "$wc_lines" -gt 5 ]] || { echo "FAIL: $FILE is too short ($wc_lines lines) — fill it in"; exit 1; }

echo "OK: $FILE looks populated"
```

---

## Step 4 — Split out topic files (optional)

Claude Code does not load a repo-local `.claude/memory/` folder; auto memory lives outside the repo under `~/.claude/projects/<project>/memory/` and is machine-local. For committed, team-shared context that should not sit in the root file, use the two mechanisms the runtime actually reads:

```
.claude/
  rules/
    testing.md               # loads every session, same priority as CLAUDE.md
    api.md                   # add `paths:` frontmatter to load only for matching files
docs/
  decisions.md               # linked from CLAUDE.md as a pointer, read on demand
```

Point to long material instead of importing it: an `@docs/decisions.md` import loads the whole file at launch and spends context every session, while a plain-prose pointer ("architecture decisions: `docs/decisions.md`") lets the agent read it only when needed.

---

## Step 5 — Commit and confirm

```bash
git add CLAUDE.md .claude/rules/ 2>/dev/null || git add CLAUDE.md
git commit -m "docs: add agent memory files (CLAUDE.md)"
```

Start a fresh session and confirm:

1. The agent reads your Boundaries section and does not ask about things listed in "Always Do."
2. The agent pauses before actions listed in "Ask First."
3. The agent refuses actions listed in "Never Do."

If any of those checks fail, tighten the wording. Use imperative phrasing ("Run tests before committing") not aspirational phrasing ("Try to run tests").

---

## Common Mistakes at Setup

| Mistake | Symptom | Fix |
|---------|---------|-----|
| File in wrong directory | Agent ignores CLAUDE.md | Move to repo root; confirm with `/context` |
| Placeholder text left in | Agent follows vague instructions loosely | Replace all `[brackets]` with real content |
| "Never Do" list empty | Agent does things it should not | Add 3–5 hard prohibitions relevant to this repo |
| Stack section missing | Agent guesses the test command wrong | Fill in language, framework, and test runner explicitly |
| File too long (>500 lines) | Slow session start, high token cost | Move deep reference material to `references/` and link from CLAUDE.md |

---

## References

- Memory patterns: `memory-patterns.md`
- Memory discipline: `memory-discipline.md`
- Traps and anti-patterns: `traps-and-antipatterns.md`
- CLAUDE.md fragment library: `claude-md-fragments.md`
- Lint script: `../scripts/lint_claude_memory.sh`
