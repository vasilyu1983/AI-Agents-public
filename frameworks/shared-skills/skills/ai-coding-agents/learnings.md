# ai-coding-agents — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Don't pin dated model snapshots (e.g. claude-sonnet-4-20250514, o4-mini) in example code — they go stale; use generic placeholders.
- [2026-07-11] Don't treat GitHub Copilot CLI as a mere terminal helper — 2026 added custom .agent.md agents, a plugin system, and pre-wired GitHub MCP.
## Domain Knowledge

- [2026-07-11] Subagents/forks may nest to depth 5 since v2.1.172; forks count toward the cap since v2.1.187 — old 'one level of forking only' claim was stale.
- [2026-07-11] Claude Code Agent spawns run in background by default since v2.1.198 (was foreground/mixed before).
## Open Questions

## Consolidated Principles

