# AI Coding Tool Capability Matrix

Purpose: compare stable instruction and workflow surfaces, not volatile pricing, model names, or benchmark marketing.

Last verified: 2026-03-13

## Use This Matrix For

- deciding where project context should live
- choosing between shared and tool-specific instruction layers
- planning which tool should own which workflow

Do not use this file for:
- current pricing
- current model lineup
- benchmark claims
- privacy or retention claims without a fresh primary-source check

## Stable Capability Matrix

| Tool | Shared context surface | Scoped instructions | Custom agents / skills | Approval / execution model | Official docs |
|------|------------------------|---------------------|------------------------|----------------------------|---------------|
| Claude Code | `CLAUDE.md` | linked docs and repo memory | `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` | explicit tool permissions and approvals | Anthropic docs |
| GitHub Copilot | `AGENTS.md` where supported plus repo instructions | `.github/instructions/*.instructions.md` | `.github/agents/`, `.github/skills/` | coding-agent workflows tied to GitHub surfaces | GitHub docs |
| Cursor | root `AGENTS.md` or project rules | `.cursor/rules/` | rule-based guidance, CLI workflows | approval-aware CLI and IDE workflows | Cursor docs |
| Portable baseline | `AGENTS.md` | link to deeper docs | none by default | depends on tool | repo-owned docs |

## Selection Heuristics

### Choose Claude Code when:
- the workflow is Claude-first
- you want explicit repo memory and agent layering
- hooks, subagents, or skills are central to the workflow

### Choose GitHub Copilot when:
- the workflow is GitHub-native
- you need repository instructions, path-specific rules, and custom agents inside GitHub
- the implementation handoff will run through PRs, issues, or Actions

### Choose Cursor when:
- the team works primarily in Cursor
- scoped project rules matter more than a heavy shared memory file
- you want a shared `AGENTS.md` plus Cursor-specific rule overlays

### Choose the portable baseline when:
- the repo must support multiple tools
- the team wants one canonical instruction layer
- tool-specific differences can stay small and isolated

## Working Pattern For Multi-Tool Repos

1. Keep shared repo facts in `AGENTS.md`.
2. Add `CLAUDE.md` only for Claude-specific behavior.
3. Add `.github/copilot-instructions.md` and path-specific instruction files for Copilot-specific behavior.
4. Add `.cursor/rules/` for Cursor-specific behavior.
5. Link everything back to canonical docs under `docs/`.

## Verification Rule

Before shipping recommendations about a tool:
- verify the current official docs in `data/sources.json`
- do not cite pricing or model variants from memory
- label volatile claims with a verification date

## Intentional Omissions

This matrix intentionally omits:
- price tables
- context window numbers
- vendor benchmark charts
- "best tool overall" recommendations

Those details change too quickly and should be checked live against primary sources.
