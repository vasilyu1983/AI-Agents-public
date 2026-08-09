# CLAUDE.md Instruction Budget

Operational ceilings and structure for `CLAUDE.md` / `AGENTS.md` files, derived from a working-day post on instruction-following degradation in Claude Code.

Source: @zodchiii, 2026-04-27 — <https://x.com/zodchiii/status/2048683276194185640>

Cross-links: [`memory-architecture-ceilings.md`](memory-architecture-ceilings.md), [`claude-md-fragments.md`](claude-md-fragments.md).

## Table of Contents

- [Instruction Budget](#instruction-budget)
- [3-Tier Hierarchy](#3-tier-hierarchy)
- [5-Section Template](#5-section-template)
- [Hard Caps](#hard-caps)
- [Adherence Markers](#adherence-markers)
- [High-Impact Rule Examples](#high-impact-rule-examples)
- [What NOT To Include](#what-not-to-include)
- [Delete-Line Test](#delete-line-test)
- [Auto-Memory Location](#auto-memory-location)

## Instruction Budget

- Empirical instruction-count ceiling for reliable adherence: **~150–200 distinct instructions** in the active prompt.
- Claude Code's built-in system prompt already consumes **~50** of that budget.
- Remaining budget for project + user `CLAUDE.md` combined: **~100–150 lines of hard rules**.
- Past the ceiling, instruction-following degrades silently — the model still complies with most rules, drops the rest without warning.

## 4-Tier Hierarchy

Loaded in this order; later layers can override earlier ones (verified against official docs 2026-06-09):

1. **Managed policy** — macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md`. Organization-wide, cannot be excluded by individuals.
2. `~/.claude/CLAUDE.md` — user-global. Personal preferences, default tools, identity. Also `~/.claude/rules/*.md` for personal path-scoped rules.
3. `./CLAUDE.md` or `./.claude/CLAUDE.md` — project-shared. Checked in. Team-wide rules.
4. `./CLAUDE.local.md` — project-local. Gitignored. Per-developer overrides and secrets-adjacent context.

Treat all four tiers as one budget pool, not independent budgets — the ~150–200 ceiling applies to their *sum*. **Do not repeat rules across tiers**: if user-global says "run tests," project does not repeat it.

## 5-Section Template

Standard sections, ordered by load-bearing weight:

1. **Commands** — exact shell invocations the agent should prefer (build, test single file, test all, lint, type check, dev). Without this, Claude burns turns guessing `npm test` when the project uses `pnpm vitest`.
2. **Architecture** — minimum map needed to navigate the repo: top-level dirs with one-line purpose, entry points, ownership. Not a full directory listing.
3. **Rules** — hard "do / never do" lines. Keep under 15. Negative rules ("NEVER commit .env") are as load-bearing as positive ones.
4. **Workflow** — how the agent should approach tasks: clarifying questions before complex work, minimal changes, separate commits per logical change, when to ask vs when to act.
5. **Out-of-scope** — explicit non-goals so the agent stops volunteering them: files manually maintained, integrations not to modify, infra it should not touch.

## Hard Caps

- Total `CLAUDE.md` length: **<80 lines** (template-author target: <60).
- Hard rules in the Rules section: **<15**.
- Each rule: one line, imperative voice, no rationale prose.

## Adherence Markers

`IMPORTANT:` and `YOU MUST` markers measurably improve adherence on the rules they prefix — confirmed in Anthropic's own docs. Use sparingly; overuse flattens the signal. Reserve for rules whose violation has caused a real bug.

## High-Impact Rule Examples

Lines reported as biggest output-quality lift in production CLAUDE.md tuning:

- `IMPORTANT: run type check after every code change` — prevents shipping broken types.
- `Make minimal changes, don't refactor unrelated code` — prevents whole-file rewrites for one-line fixes.
- `Create separate commits per logical change` — prevents the 47-file monster commit.
- `When unsure between two approaches, explain both and let me choose` — prevents silent architectural decisions.
- `Static export only, no SSR` (when applicable) — prevents server-side code in a static-deploy site.

Each prevents a specific recurring mistake. That is the bar.

## What NOT To Include

- Personality instructions (`be a senior engineer`, `think step by step`).
- Code formatting rules the linter already enforces.
- `@`-imports that pull entire docs into every session — they crowd out hard rules.
- Duplicate rules across tiers (see hierarchy section).
- Anything Claude will learn on its own via auto-memory after one session.

## Delete-Line Test

For every line in `CLAUDE.md`, ask: *"Does removing this line cause Claude to make a mistake I have actually seen?"*

- If **no** — delete it.
- If **yes** — keep, and ideally tag with `IMPORTANT:`.

The file compounds: month one it saves repeating yourself, month six it has captured every recurring mistake and prevents them automatically.

## Auto-Memory Location

Claude Code's auto-memory writes to:

```text
~/.claude/projects/<project>/memory/
```

The `<project>` segment is derived from the git repository root. All worktrees and subdirectories within the same repo share one auto-memory directory; outside a git repo the project root is used.

Inspect with the `/memory` slash command. `MEMORY.md` is the index file. Topic files (`debugging.md`, `api-conventions.md`, etc.) are NOT loaded at startup — Claude reads them on demand via file tools. `MEMORY.md` itself loads at startup (first 200 lines or first 25 KB, whichever comes first); content beyond that threshold is not loaded. Verified against official docs 2026-06-09: <https://code.claude.com/docs/en/memory>.

Auto-memory does **not** count against the `CLAUDE.md` budget. Requires Claude Code v2.1.59 or later (`claude --version`). Disable per-project with `"autoMemoryEnabled": false` in settings, or globally with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
