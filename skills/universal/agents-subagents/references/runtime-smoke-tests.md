---
description: Runtime-surface confidence check beyond repo validation.
last_verified: 2026-08-27
status: stable
---

# Runtime Smoke Tests

Runtime-surface smoke-test matrix for `agents-subagents`.

Use this checklist when you want stronger confidence than repo validation alone. The goal is to confirm that the documented runtime surfaces actually work with the current global and project agent registries, shared teams, and debate flows.

## Table of Contents

- [What This Covers](#what-this-covers)
- [Current Status](#current-status)
- [Claude Smoke Tests](#claude-smoke-tests)
- [Codex Smoke Tests](#codex-smoke-tests)
- [Shared Team And Debate Checks](#shared-team-and-debate-checks)
- [Pass Criteria](#pass-criteria)

## What This Covers

This matrix is intentionally narrower than full product QA. It validates:

- installed global agents
- repo-local agent overrides
- shared members and shared teams
- debate launch paths
- the documented runtime surfaces for Claude Code and Codex

This matrix does **not** try to exhaustively test every plugin, MCP server, or skill in the surrounding ecosystem.

## Current Status

After the last local check recorded in this repo (re-run the checks below before relying on it):

- repo validation is clean
- canonical Claude/Codex member parity is complete
- shared teams and debates are documented
- CLI help confirms the expected runtime flags and surfaces exist locally:
  - `claude --help` includes `--agent` and `--agents`
  - `codex --help` includes CLI, `app`, and `cloud`

What is still recommended:

- run the smoke tests below after major changes to agent naming, deployment, repository team recipes, or runtime-surface docs
- treat any unchecked row as “documented but not fully runtime-verified on this machine”

## Claude Smoke Tests

| Surface | Check | Expected Result |
|--------|-------|-----------------|
| Global agent | `claude agents` shows installed personal agents | target agent appears from `~/.claude/agents/` |
| Project agent | add a temporary repo-local agent and run `claude agents` | project agent appears and overrides global agent of the same name |
| Whole-session agent | run `claude --agent <name> -p "say your role"` | output reflects the selected agent role |
| Session-scoped agents | run `claude --agents '<json>' -p "use reviewer"` | temporary agent is accepted for the session without writing repo files |
| Interactive team surface | launch a documented team prompt in Claude interactive mode | teammates or delegated workers follow the team contract |
| Debate surface | run a debate-enabled team or debate overlay prompt | output includes recommendation, dissent, and action items |

## Codex Smoke Tests

| Surface | Check | Expected Result |
|--------|-------|-----------------|
| Global agent | inspect `~/.codex/agents/`, restart Codex, and explicitly ask the parent to spawn the exact registered name | the named role launches and its instructions apply; `/agent` is only a thread inspector/switcher |
| Project agent | add a temporary repo-local agent in `.codex/agents/`, restart, and explicitly spawn it | repo-local role launches without TOML parse errors |
| Clean-context custom agent | spawn the exact role with `fork_turns: "none"` and a self-contained sentinel brief | the worker uses the brief without relying on parent history |
| App surface | launch `codex app` and confirm agents are available | same canonical agents are visible through the app surface |
| Cloud task surface | use `codex cloud` to submit or browse a test task and inspect its isolated environment | the Cloud task runs in its configured environment; do not assume local `~/.codex/agents/` was deployed |
| Cloud internet controls | inspect the environment config for Codex cloud internet access | default-off stays intact, or any enabled access is restricted to explicit domains and HTTP methods |
| Scheduled task surface | create and inspect a recurring task in a surface that supports Scheduled tasks, such as web or desktop | the schedule, project/environment, and output are visible; CLI Cloud commands are not treated as Scheduled-task management |
| Local scheduled isolation | when a desktop schedule uses a local project, select the documented local or worktree execution mode | concurrent work uses an explicit worktree or an otherwise safe single-writer plan |

## Shared Team And Debate Checks

Run these once per major release of `agents-subagents`:

| Area | Check | Expected Result |
|------|-------|-----------------|
| Shared team install | install a representative team on Claude and Codex | members deploy without duplication or parse errors |
| Shared member install | install one canonical member directly on both runtimes | member is available and linked skills remain valid |
| Team prompt docs | use a prompt from `team-prompt-patterns.md` | prompt launches the intended team mode cleanly |
| Scenario docs | use a scenario from `team-scenarios.md` | selected team fits the scenario and produces the expected output contract |
| Debate quickstart | follow the debate quickstart for each runtime you use | each runtime reaches a decision-log style output |
| Context-first behavior | provide `docs/` plus `dev-context-*` artifacts to an engineering team | workers use prepared context first instead of rereading the whole repo |

## Pass Criteria

Treat `agents-subagents` as runtime-QA complete when all of these are true:

1. `validate_skill.py` passes
2. `audit_team_coverage.py` passes
3. Claude global, project, `--agent`, and `--agents` surfaces are smoke-tested
4. Codex global, project, CLI, and clean-context named-agent surfaces are smoke-tested
5. One shared team and one debate flow succeed on each runtime you actively use
6. Engineering teams still honor the context-first rule using `docs/` and `dev-context-*` artifacts
7. Cloud and Scheduled-task rows pass separately if those surfaces are part of the deployment; neither is inferred from local custom-agent success

If only the repo validators pass, treat the skill as **repo-ready**.
If the matrix above also passes on the runtimes you use, treat the skill as **runtime-ready**.
