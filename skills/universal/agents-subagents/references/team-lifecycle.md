---
description: Setup, run, and cleanup lifecycle for repository team recipes and native runtime agents.
last_verified: 2026-09-16
status: stable
---

# Agent Team Lifecycle

Use this reference for the canonical setup, run, and cleanup sequence when deploying repository team recipes. A `team.yaml` is launcher/installer metadata, not native runtime configuration. Claude can reuse installed members in interactive Agent Teams. Codex runs the installed custom agents through a parent-led subagent workflow.

Default rule: use a single member or bounded subagent first. Escalate to a team only when several specialists need distinct outputs or direct coordination.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Run](#run)
- [Cleanup](#cleanup)
- [Dual-Platform Deployment](#dual-platform-deployment)
- [Usefulness Review](#usefulness-review)
- [Constraints](#constraints)
- [Troubleshooting](#troubleshooting)

Related references:

- [Team Scenarios and Prompt Library](team-scenarios.md)
- [Team Prompt Patterns](team-prompt-patterns.md)
- [Team Coverage Map](team-coverage.md)
- [Universal Team Playbook](universal-team-playbook.md)
- [Team Selection Guide](team-selection-guide.md)

## Prerequisites

- a Claude Code version that supports interactive agent teams, if you plan to use them (check the agent-teams docs)
- Agent teams enabled: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or environment
- For Codex: custom agents in `.codex/agents/` (project) or `~/.codex/agents/` (personal)
- A launch prompt that names goal, required context, ownership, execution mode, debate rule, synthesis owner, and cleanup expectation

## Setup

### 1. Choose a team recipe

Available teams in `agents/teams/`. Read-only panels are not here — they run as
`expert-board` boards (see [team-coverage.md](team-coverage.md)):

| Team | Members | Best For |
|------|---------|----------|
| `software-code-review-board` | software-security-reviewer, software-performance-reviewer, qa-test-reviewer | Multi-perspective code review |
| `dev-feature-delivery` | dev-feature-researcher, dev-feature-implementer, dev-feature-reviewer | Feature development with verification |
| `dev-context-preparation` | dev-portfolio-mapper, dev-repo-context-curator, dev-code-graph-builder, dev-context-packet-synthesizer | Build reusable context artifacts before engineering work |
| `dev-migration-map` | dev-portfolio-mapper, dev-dependency-auditor, dev-migration-planner, ops-rollout-reviewer | Migrations and cutovers |
| `docs-knowledge` | docs-codebase-architect, docs-ai-prd-writer, docs-notes-retrieval-curator, docs-quality-auditor | Docs systems and knowledge operations |
| `product-surface` | software-frontend-lead, software-ux-designer, software-accessibility-reviewer, software-localisation-reviewer | Frontend and UX surface quality |

Bounded idea, growth, monetization, marketing, architecture, incident, release,
and enterprise review panels are not installed recipes. In Claude, run the saved
`expert-board` workflow with the corresponding `board` mode. In Codex, select the
same board and mode from the generated `expert-board.codex-plan.json` and have the
parent execute its spawn/wait/follow-up contract. Generic role briefs need no
team installation; named `agent_type` entries still require that custom agent to
be available in the active Codex runtime.

### 2. Install the team

```bash
# Install a team to user-level (available in all projects)
bash scripts/deploy-preset.sh dev-migration-map --platform claude --user

# Install a team to project-level (available in current project only)
bash scripts/deploy-preset.sh software-code-review-board --platform claude --project

# Install one shared member directly
bash scripts/deploy-preset.sh software-security-reviewer --member --platform claude --project

# For Codex
bash scripts/deploy-preset.sh dev-migration-map --platform codex --user
```

This installs native member files into `.claude/agents/` or `.codex/agents/`. Runtime-neutral recipe metadata is stored under `.agents/team-recipes/<platform>/`; neither Claude nor Codex reads `team.yaml` directly.

### 3. Prepare context (recommended for engineering packs)

Before `dev-feature-delivery` or `software-code-review-board`, prefer passing artifact paths instead of asking every worker to rediscover the repo:

- `docs/**/*.md` or a repo-specific docs hub with prepared architecture notes, context packets, ADRs, migration plans, and runbooks
- `profiles/*.json`
- `catalog/*.md`
- `graphs/system-edges.json`
- `graphs/knowledge-graph.json`
- `code-profiles/<repo>.json`
- `graphs/code-graph.json`
- `reports/query-*.md`

The `dev-context-preparation` pack exists to create or refresh these artifacts. If a repo already has prepared context in `docs/`, workers should consume that first. If artifacts are missing, workers should do bounded local reading rather than whole-portfolio discovery.

Default discovery rule:
- Only `dev-context-preparation` roles should perform broad repo discovery by default.
- Other engineering members should work from `docs/`, graphs, profiles, query reports, and a bounded set of source files.
- Treat the lead thread as the source of truth for requirements and final decisions. Workers should receive small context packets, not the whole live conversation.

### 4. Verify deployment

- Claude Code: type `@` and check the typeahead for agent names — this is the verification step. Agent-file changes hot-reload in the active session.
- Claude Code: before the session, run `claude plugin validate .claude/agents` (or `~/.claude/agents`) to find files whose frontmatter doesn't parse. It checks only the directory you name and does not flag a file whose frontmatter parses but has no `name`. Check `claude plugin --help` that your version has it.
- Claude Code: **`claude agents` is not a member registry.** It opens agent view — "one screen for all your background sessions: what's running, what needs your input, and what's done." "Despite the similar name, `/agents` is separate from `claude agents`", and in recent releases `/agents` no longer opens a panel either: it prints a notice pointing to the subagent file locations. Neither command tells you whether a preset installed.
- Codex: restart the session, then smoke-test the exact registered name with a spawn request. `/agent` inspects and switches active agent threads; it is not the custom-agent registry.

## Run

### Interactive team (Claude Code collaborative mode)

Use a team launcher prompt or write your own. Example:

```text
Create an agent team with 3 reviewers:
- software-security-reviewer: audit auth, input validation, secrets exposure
- software-performance-reviewer: check queries, memory, caching, bundle size
- qa-test-reviewer: validate coverage, edge cases, flake risk
Have each reviewer work independently, then share findings.
Synthesize into a prioritized report.
Clean up the team when done.
```

Monitor teammates:
- **In-process mode**: up and down arrows select a teammate in the agent panel, Enter opens its transcript and lets you message it, Escape clears the selection. Ctrl+T toggles task list.
- **Split-pane mode**: click into any pane to interact directly.

Run teams in this order:
- round 1: independent reads
- round 2: debate only if a named trigger is hit
- synthesis: lead or named synthesis owner writes the memo and cleans up the team

### Headless subagent fan-out (CI/CD)

Agent teams require interactive mode. For CI/CD, use `claude -p` with `--agents` for subagent-based fan-out:

```bash
bash scripts/headless-review.sh
```

This runs a single session that spawns subagents (not teammates). Subagents report back but cannot message each other.

### Codex multi-agent (explicit orchestration mode)

Codex delegation follows a direct user request or applicable `AGENTS.md`/skill policy:

```text
Spawn security_reviewer, performance_reviewer, and test_reviewer agents in parallel.
Wait for all to complete, then summarize findings.
```

For an `expert-board` panel, do not translate the manifest by hand. Verify the
generated adapter, then use the selected board variant as the launch contract:

```bash
python3 scripts/generate_codex_expert_board_plan.py --check
```

The adapter deliberately is not a native saved workflow. The Codex parent
validates context and locks weights, calls `spawn_agent` for the blind panel with
`fork_turns: "none"`, calls `wait_agent`, sends the challenge with
`send_input`, waits again, applies the EVPI expansion gate, and synthesizes.
It must not start normal dispatch until all required context values are nonblank;
an exact algedonic signal returns immediately. Challenge only on an exact
documented debate trigger. If a named `agent_type` is unavailable, retry once
without `agent_type` using the same self-contained brief and constraints.

## Cleanup

### Automatic cleanup

Include "clean up the team when done" in the team prompt. Current Claude Code handles setup and cleanup automatically; the retired `TeamCreate` and `TeamDelete` tools are not part of the current flow.

### Manual cleanup

1. Ask the lead to shut down each teammate:
   ```text
   Ask all teammates to shut down
   ```
2. After teammates stop, ask the lead to clean up:
   ```text
   Clean up the team
   ```

### Legacy orphaned-team cleanup

Current Claude Code removes native team state automatically. Use the legacy cleanup script only to inspect state left by an older runtime, and require its explicit destructive-cleanup option before deletion:

```bash
bash scripts/teardown-team.sh --legacy-cleanup
```

### Remove an installed team

```bash
bash scripts/deploy-preset.sh dev-migration-map --platform claude --user --remove
```

This removes the team metadata and deletes only those member files that are no longer referenced by another installed team in the same scope.

## Dual-Platform Deployment

Canonical members live under `agents/`, while teams live under `agents/teams/`:

```
members/
  claude/         # canonical .md files
  codex/          # canonical .toml files, plus generated fallbacks if missing

teams/{team}/
  team.yaml       # logical team composition and defaults
```

Installed state separates native agents from repository recipe metadata:

```
.codex/agents/{member}.toml                    # native Codex custom agent
.agents/team-recipes/codex/{team}.members      # installer-owned member index
.agents/team-recipes/codex/{team}/team.yaml    # repository recipe metadata; Codex does not read it
```

Members share the same role brief, workflow, and output contract. Differences:

| Aspect | Claude Code | Codex |
|--------|-------------|-------|
| Format | YAML frontmatter + markdown body | TOML fields |
| Skills | `skills:` list (standalone subagents only) | Optional `[[skills.config]]` per-skill enablement overrides for discoverable skill folders; normal discovery/activation still applies, and the inline brief remains the fallback |
| Permissions | `permissionMode` | `sandbox_mode` |
| Team communication | SendMessage, shared task list | Parent-led spawn/follow-up/wait is portable; use direct messaging only where the active surface exposes it |
| Context sharing | Team lead can pass artifact paths or prompt context to teammates; teammates do not inherit the full lead transcript | Use `fork_turns: "none"` when clean context is required; other fork settings may inherit parent history. In every case the parent passes a self-contained brief and synthesizes worker results. |

## Usefulness Review

Decide which teams and members to install or retire from the operator's own evidence, not from a published ranking:

1. Count recent use per domain from commit history and session history across the operator's projects.
2. Score each member for maturity against the current member template.
3. Keep the two axes separate. **Usefulness** (share of real work the role serves) drives install and retire. **Maturity** drives upgrade priority only; a low-usefulness member stays in the shared catalog.
4. Install a role only when its usefulness is non-trivial. Flag it for upgrade when usefulness is high and maturity is low.

Re-run the review when the session mix shifts for several weeks, project focus changes, the installed set drifts from the last review, a rare domain becomes recurring, or the member template version advances. A ranking older than its evidence window is history, not guidance.

## Constraints

- **Agent teams require interactive mode.** `claude -p` (headless) cannot run agent teams. Use subagent fan-out for CI/CD instead.
- **`skills:` not applied to teammates.** When an agent definition is used as a teammate, the `skills` and `mcpServers` fields are ignored. Teammates load skills from project/user settings. Each canonical member includes an inline role brief to compensate.
- **Context artifacts beat repeated discovery.** For engineering work, prefer graph/profile/report inputs before cold repo scans.
- **Lead-thread history does not carry over.** Pass the decision frame and required context explicitly; do not assume teammates can infer it from the lead session.
- **One team per session.** Clean up the current team before starting a new one.
- **No nested teams.** Teammates cannot spawn their own teams.
- **Cleanup is automatic in current Claude Code.** The lead should still wait for teammates and close the work cleanly; do not call retired team lifecycle tools.
- **Bound Codex nesting through policy.** Public configuration does not document a universal `max_depth` key; mark leaf roles and nesting limits in prompts or `AGENTS.md`.
- **A Codex thread is not filesystem isolation.** Same-chat workers share the checkout. Keep review panels read-only, assign one writer, or use a separate worktree for independent implementation.
- **The generated Codex plan is an adapter, not a saved workflow.** The parent executes its explicit primitives; Cloud tasks and Scheduled tasks are separate runtime surfaces and do not automatically deploy local custom-agent definitions.

### Codex scheduled tasks — what the docs actually support

Decide with these facts before reaching for a schedule ([learn.chatgpt.com/docs/automations](https://learn.chatgpt.com/docs/automations); re-read them before relying on a limit):

| Question | Answer |
|---|---|
| Where can you create one? | Desktop app (project-scoped or standalone) and web (ChatGPT Work). "Codex CLI doesn't provide the Scheduled management interface" — the CLI and IDE extension expose no scheduling at all. |
| Do custom skills and plugins work? | Yes — you can "combine scheduled tasks with skills for more complex work"; plugins where your plan includes them. |
| Model and effort | Selectable, or left on defaults. |
| Approvals and sandbox | "Scheduled tasks run unattended and use your default sandbox settings", and can run with `approval_policy = "never"` subject to org policy. |
| Where does the work land? | Desktop: the project directory, or an isolated git worktree that "keeps changes from scheduled tasks separate". Web: the cloud — "they don't keep a local folder or worktree available between runs". |
| Does the machine need to be up? | For a local project run, yes — "keep the computer on and the app running". |
| Recurrence and triggers | Custom RFC 5545 `RRULE` recurrence, and Gmail / Slack / GitHub event triggers, are **web/mobile only** on eligible plans. |

Design consequence: a scheduled task is a fine home for an unattended read-and-report role that carries its own skill, and a poor home for anything that assumes a locally installed member fleet or an approval prompt someone will answer.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Teammates not appearing | Check agent teams are enabled. Use the up/down arrows in the agent panel in in-process mode; an idle row hides 30s after the whole panel goes idle and reappears on the teammate's next turn. |
| `@-mention` doesn't show agent | Check the file exists under `.claude/agents/` or `~/.claude/agents/` and parses: `claude plugin validate <dir>` (where your version has it). Agent-file changes hot-reload; restart only if the typeahead stays stale. `claude agents` will not help — it lists background sessions, not installed members. |
| Too many permission prompts | Pre-approve tools in permission settings before spawning. |
| Teammates stopping on errors | Select them in the agent panel (up/down arrows, then Enter) and message them directly with additional instructions. |
| Lead finishes before teammates | Tell the lead: "Wait for all teammates to finish before proceeding." |
| Orphaned tmux sessions | `tmux ls` then `tmux kill-session -t <name>`. |
| Legacy stale team state | Inspect first; use `scripts/teardown-team.sh --legacy-cleanup` only for state left by older Claude releases. |
| Reviewers reread the whole repo | Provide `docs/**/*.md`, `graphs/code-graph.json`, and `reports/query-*.md` in the launch brief before the review starts. |
