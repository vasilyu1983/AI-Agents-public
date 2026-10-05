# ai-coding-agents-state — Learnings

Merged from ai-coding-agents-state and ai-coding-agents-state on 2026-09-29; entries carried unchanged.

## Patterns That Work


## Mistakes to Avoid

- [2026-07-11] cleanupPeriodDays defaults to 30 days, not 7; background-agent worktrees live at project-relative .claude/worktrees/, not ~/.claude/worktrees/<id>/.
- [2026-07-11] Don't conflate /fork (subagent-level context inheritance, CLAUDE_CODE_FORK_SUBAGENT) with /branch or --fork-session (mints a whole new independent session) — both officially documented but easily confused.

## Domain Knowledge

- [2026-07-11] Claude Code checkpoint/rewind tracks only file-editing-tool changes, never bash-modified files (rm/mv/cp) — verified 2026-07-11 against code.claude.com/docs/en/checkpointing.
- [2026-07-11] Claude Code: Task tool renamed Agent (v2.1.63); subagents run background-by-default (v2.1.198); background permission prompts now route to the parent session instead of auto-denying (v2.1.186) — verified 2026-07-11.

## Open Questions


## Consolidated Principles

