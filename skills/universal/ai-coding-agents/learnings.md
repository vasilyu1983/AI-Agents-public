# ai-coding-agents — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Don't pin dated model snapshots (e.g. claude-sonnet-4-20250514, o4-mini) in example code — they go stale; use generic placeholders.
- [2026-07-11] Don't treat GitHub Copilot CLI as a mere terminal helper — it supports custom .agent.md agents, a plugin system, and pre-wired GitHub MCP; check its docs for the current surface.
## Domain Knowledge

- [2026-07-11] An old 'one level of forking only' claim went stale, and so did the depth cap and background-default version gates recorded to replace it (corrected 2026-09-25). Nesting depth, fork counting, and background-by-default spawns are runtime defaults that change between releases: look them up in the sub-agents docs, never record them as facts here.
## Open Questions

## Consolidated Principles

