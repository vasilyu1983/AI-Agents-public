# ai-coding-agents-runtime-core — Learnings

Merged from ai-coding-agents-runtime-core and ai-coding-agents-runtime-core on 2026-09-29; entries carried unchanged.

## Patterns That Work


## Mistakes to Avoid

- [2026-07-11] Prior /agents and fork-activation claims were stale. Re-verify young Claude Code commands and flags against official docs, not tweets.

## Domain Knowledge


## Open Questions


## Consolidated Principles


## Carried Raw Entries

- [2026-07-11] Web-verified against `code.claude.com/docs/en` (tools-reference, sub-agents, mcp) and the `anthropics/claude-code` changelog: Agent-tool subagents now run in the background by default, and background-subagent permission prompts surface in the parent session (earlier they auto-denied silently, a silent-failure trap). Folded into SKILL.md as undated rules. The depth-cap and always-loaded-split claims from the same pass were later found wrong or volatile (2026-09 audit) and removed; look those up per host.
