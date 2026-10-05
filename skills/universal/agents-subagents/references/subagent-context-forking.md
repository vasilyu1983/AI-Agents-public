---
description: Official Claude Code surfaces for forking context into a subagent or a separate background session.
last_verified: 2026-08-27
status: stable
---

# Subagent Context Forking

Operational notes on Claude Code's context-fork mechanism for subagents — the mode where children inherit the parent's full conversation instead of starting blank.

Sources: [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) and [agent view](https://code.claude.com/docs/en/agent-view).

Cross-link: [`context-first-protocol.md`](context-first-protocol.md).

## Table of Contents

- [Default vs Fork Mode](#default-vs-fork-mode)
- [Current Fork Surfaces](#current-fork-surfaces)
- [Cache-Prefix Sharing](#cache-prefix-sharing)
- [Subagent File Format](#subagent-file-format)
- [On-Disk Locations and Precedence](#on-disk-locations-and-precedence)
- [Built-in Explore + Plan Subagents](#built-in-explore--plan-subagents)
- [Context Timeline Hook](#context-timeline-hook)

## Default vs Fork Mode

By default, a subagent starts with a **blank context** — its own system prompt, its own tools, no parent history. The parent only sees the final summary the subagent returns.

That isolation is the point most of the time: 30 minutes of grep/find/ls noise stays inside the child and never compacts away your real reasoning. The cost: when you have already invested 100K tokens building understanding, a blank child has to redo that work.

Fork mode addresses the second case: the subagent starts with **an exact copy of the parent's context at the moment of fork**.

## Current Fork Surfaces

With agent view enabled, the commands have distinct meanings:

```text
/subtask    # create a background subagent from the current context
/fork       # copy the whole current session into a separate background session
```

Use `/subtask` when the current conversation should remain the lead and consume a result notification. Use `/fork` when the copied session should continue as an independently steerable session. Do not document `/fork` as the universal subagent command: its meaning depends on agent-view configuration, and current agent-view documentation assigns subagent creation to `/subtask`.

## Cache-Prefix Sharing

- Forked children can reuse the parent's prompt-cache prefix.
- Output tokens are still generated normally.
- Anthropic documents cache reuse but does not promise a fixed multiplier such as "10× cheaper." Measure the active runtime before using cache savings in a budget.
- Dispatching related children from one stable parent prefix can reduce repeated input work, but coordination and output costs still scale with fan-out.

Plan multi-child fan-outs accordingly — group related lookups into one parent session and fork from there, rather than starting fresh sessions per question.

Model selection and background behavior remain runtime-scoped. Verify the selected model through runtime telemetry when a cost or capability boundary depends on it.

## Subagent File Format

A subagent is a Markdown file with frontmatter. Claude Code auto-loads it and invokes when the `description` matches the task.

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and maintainability. Use after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Start the review immediately
```

The `description` field acts as the routing signal — write it for the matcher, not for humans.

## On-Disk Locations and Precedence

Common filesystem paths, within the wider managed/session/project/personal/plugin precedence:

1. `.claude/agents/` — repo-scoped, checked in, team-shared. **Wins** when a same-name file exists.
2. `~/.claude/agents/` — user-global, personal. Fallback.

A repo-local file with the same name overrides the user-global one — useful when one agent name needs different behavior per repo.

## Built-in Explore + Plan Subagents

Claude Code ships two read-only built-ins. They are **not** forks: each starts with a fresh context and, unlike other subagents, skips `CLAUDE.md` and the git status snapshot to stay fast and cheap. They share no prompt prefix with the parent, so do not count on cache reuse from them.

- **`Explore`** — read-only search subagent. Fires grep/find/glob in its own window and returns the relevant findings, not the search transcript.
- **`Plan`** — investigates and produces an implementation plan. Reads files, understands architecture, returns a step-by-step doc.

Standard flow: parent reasons → invokes `Explore` to gather → invokes `Plan` to design → **human (or lead) reviews the plan** → parent executes edits. The saving comes from keeping the search transcript out of the parent's window, not from cache sharing. Source: [Claude Code sub-agents docs](https://code.claude.com/docs/en/sub-agents) ("Explore and Plan skip your CLAUDE.md files and the git status snapshot"; a fork is the only subagent that inherits the parent conversation), verified 2026-09-27.

**Do not auto-chain Explore → Plan → Execute without a checkpoint.** Plan-mode output should land back in the parent for review before any write-capable worker runs. Auto-chaining bypasses the cheapest place to catch a misframed task — between understanding the codebase and changing it. The review step can be a one-line "looks right, proceed" from the operator; the gate is what matters, not the ceremony.

## Context Timeline Hook

The context-timeline observability hook can show what each fork is consuming,
but it is optional third-party code. Do not execute a moving `@latest` package
directly. Select an exact published version, stage its package without running
lifecycle scripts, inspect its source, transitive dependencies, hook actions,
network behavior, and requested filesystem access, and test it in a credential-
free disposable profile. Install only the exact reviewed artifact after explicit
operator approval. This repository does not name a version because it has not
independently reviewed and approved one.

Reference: <https://www.aitmpl.com/component/hook/monitoring/context-timeline>

Surfaces per-turn token usage, cache hits, and fork boundaries in a timeline view starting from session open. Treat this as optional third-party observability, not evidence of a guaranteed discount.
