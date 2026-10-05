# CLAUDE.md Instruction Budget

**This file is the single owner of the instruction-budget rule in this skill.** Other files link here instead of restating the figure.

Operational ceilings and structure for `CLAUDE.md` / `AGENTS.md` files.

Sources:

- Instruction-count estimate: HumanLayer, [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md). The post says frontier thinking models can follow roughly 150–200 instructions with reasonable consistency, and describes that as an informal estimate, not a rigorous measurement.
- 5-section template, hard caps, and rule examples: @zodchiii, 2026-04-27 — <https://x.com/zodchiii/status/2048683276194185640> (one practitioner's working notes).

Cross-links: [`memory-architecture-ceilings.md`](memory-architecture-ceilings.md), [`claude-md-fragments.md`](claude-md-fragments.md), [`loading-and-layers.md`](loading-and-layers.md).

## Table of Contents

- [Instruction Budget](#instruction-budget)
- [Layer Hierarchy](#layer-hierarchy)
- [5-Section Template](#5-section-template)
- [Hard Caps](#hard-caps)
- [Adherence Markers](#adherence-markers)
- [High-Impact Rule Examples](#high-impact-rule-examples)
- [What NOT To Include](#what-not-to-include)
- [Delete-Line Test](#delete-line-test)
- [Auto-Memory Location](#auto-memory-location)

## Instruction Budget

- Adherence degrades as the number of always-loaded instructions grows. HumanLayer's informal estimate puts the point where following becomes unreliable at **roughly 150–200 distinct instructions** in the active prompt. Treat it as a direction, not a threshold. No controlled study behind it is known to this skill.
- The runtime's own system prompt uses part of that budget. Its size changes between releases. Do not plan against a fixed count for it.
- Past the ceiling, instruction-following degrades silently: the model still follows most rules and drops the rest without warning.
- Practical rule: every line in always-loaded memory must name the mistake it prevents. If you cannot name one, delete the line. Measure adherence on your own repeated mistakes, not against a published number.
- Newer model generations tend to do better with fewer, judgment-framed rules than with long rule lists. See [coding-behavior.md](coding-behavior.md#calibrate-contract-density-to-the-model-generation).

## Layer Hierarchy

Claude Code loads its memory tiers **and concatenates them into context. No tier overrides or replaces another.** When two tiers conflict, both instructions are in context and the model may follow either one. Resolve conflicts by editing the files. Do not assume the later or narrower tier wins.

1. **Managed policy** — an organization-wide file at an OS-specific system path (see the Claude Code memory docs for the current paths). Individuals cannot exclude it.
2. **User** — `~/.claude/CLAUDE.md` plus `~/.claude/rules/*.md`. Personal preferences and default tools.
3. **Project** — `./CLAUDE.md` or `./.claude/CLAUDE.md`, plus `.claude/rules/*.md`. Checked in, team-wide.
4. **Project-local** — `./CLAUDE.local.md`. Gitignored, per developer.

Treat all tiers as one budget pool. The ceiling above applies to their *sum*. **Do not repeat rules across tiers**: if the user tier says "run tests," the project tier does not repeat it.

Whether a repo's `AGENTS.md` fills the project tier (natively or through an import) is a runtime fact that changes between releases. It is a lookup step, covered in [loading-and-layers.md](loading-and-layers.md#agentsmd-in-claude-code-lookup-step).

## 5-Section Template

Standard sections, ordered by load-bearing weight:

1. **Commands** — exact shell invocations the agent should prefer (build, test single file, test all, lint, type check, dev). Without this, Claude burns turns guessing `npm test` when the project uses `pnpm vitest`.
2. **Architecture** — the minimum map needed to navigate the repo: top-level dirs with a one-line purpose, entry points, ownership. Not a full directory listing.
3. **Rules** — hard "do / never do" lines. Keep under 15. Negative rules ("NEVER commit .env") are as load-bearing as positive ones.
4. **Workflow** — how the agent should approach tasks: clarifying questions before complex work, minimal changes, separate commits per logical change, when to ask and when to act.
5. **Out-of-scope** — explicit non-goals so the agent stops volunteering them: manually maintained files, integrations not to modify, infra it should not touch.

## Hard Caps

- **Ceiling: 200 lines per always-loaded file.** `scripts/lint_claude_memory.sh` warns past it. Treat a file near the ceiling as a pruning task, not a target.
- **Lean target: under ~80 lines** for a root `CLAUDE.md` (the template author's figure, from practice). Most repos that follow the exception-file test land well below the ceiling.
- Hard rules in the Rules section: **<15**.
- Each rule: one line, imperative voice, no rationale prose.

## Adherence Markers

Emphasis markers such as `IMPORTANT:` or `YOU MUST` can raise adherence on the rule they prefix, but they lose their effect as they multiply. Newer models can also over-apply an emphasized rule in situations it was not meant for. Anthropic's guidance for recent model generations favors calm, judgment-framed rules over emphatic ones. Use a marker only on a rule whose violation has caused a real incident, and re-test after a model upgrade whether it is still needed.

## High-Impact Rule Examples

Lines the template author reports as the biggest output-quality lift in production CLAUDE.md tuning:

- `Run type check after every code change` — prevents shipping broken types.
- `Make minimal changes, don't refactor unrelated code` — prevents whole-file rewrites for one-line fixes.
- `Create separate commits per logical change` — prevents the 47-file monster commit.
- `When unsure between two approaches, explain both and let me choose` — prevents silent architectural decisions.
- `Static export only, no SSR` (when applicable) — prevents server-side code in a static-deploy site.

Each prevents a specific recurring mistake. That is the bar.

## What NOT To Include

- Personality instructions (`be a senior engineer`, `think step by step`).
- Code formatting rules the linter already enforces.
- `@`-imports that pull entire docs into every session. They crowd out hard rules.
- Duplicate rules across tiers (see hierarchy section).
- Anything Claude will learn on its own via auto-memory after one session.

## Delete-Line Test

For every line in `CLAUDE.md`, ask: *"Does removing this line cause Claude to make a mistake I have actually seen?"*

- If **no** — delete it.
- If **yes** — keep it, and record the mistake it prevents (a short "why" or an issue link) so the next pruning pass can judge it.

The file compounds: in month one it saves repeating yourself; by month six it has captured every recurring mistake and prevents them automatically.

## Auto-Memory Location

Claude Code's auto-memory writes to:

```text
~/.claude/projects/<project>/memory/
```

The docs say only that `<project>` is derived from the git repository. In practice the segment is the repo root's absolute path with `/` replaced by `-` (for example `-Users-alice-code-my-repo`), **not** the directory basename. Confirm with `/memory` before scripting against it. All worktrees and subdirectories within the same repo share one auto-memory directory.

`MEMORY.md` is the index file and loads at startup up to a size cap; content past the cap is not loaded. Topic files (`debugging.md`, `api-conventions.md`, and so on) are not loaded at startup. Claude reads them on demand. **Lookup step:** check the Claude Code memory docs (<https://code.claude.com/docs/en/memory>) for the current cap, minimum version, and disable switches (a settings key and an environment variable) before quoting them. Keep `MEMORY.md` well inside the cap, because lines past it are silently dropped.

Auto-memory does **not** count against the `CLAUDE.md` budget.
