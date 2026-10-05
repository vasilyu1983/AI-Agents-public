# Agents and Teams

A subagent is a specialist that works in its own context and returns a report. A team is a recipe that groups subagents for one kind of job. This page explains how to use, install and combine them.

- [1. When to use a subagent](#1-when-to-use-a-subagent)
- [2. Anatomy of a subagent](#2-anatomy-of-a-subagent)
- [3. The families](#3-the-families)
- [4. Use a subagent](#4-use-a-subagent)
- [5. Teams](#5-teams)
- [6. Install and remove](#6-install-and-remove)
- [7. Subagent, team or workflow?](#7-subagent-team-or-workflow)

## 1. When to use a subagent

Use a subagent when the work is one of these:

- **Read-heavy.** A broad search or a long review would fill your main session's context. The subagent reads, and you get only its conclusion.
- **Independent.** Two or more questions do not depend on each other. Separate subagents can work on them in parallel.
- **A second opinion.** A reviewer that did not write the code finds different problems than the author.

Do not use a subagent for a small edit you can make directly. Each subagent is a full model session, so it costs time and tokens.

## 2. Anatomy of a subagent

```markdown
---
name: software-security-reviewer
family: software
description: "Audit code for security vulnerabilities, auth flaws, and secrets exposure. Use proactively after code changes or before releases ... Reports vulnerabilities ranked by exploitability; does not patch code or rotate secrets."
tools:
  - Read
  - Grep
  - Glob
  - Bash
disallowedTools:
  - Agent
maxTurns: 8
skills:
  - software-security-appsec
  - qa-security-testing
  - qa-testing-strategy
  - software-crypto-web3
---

# Instructions the subagent follows
```

| Field | Meaning |
|---|---|
| `name` | The id you use to ask for it |
| `family` | Its group, the same as the name prefix |
| `description` | What it does, when to use it, what it produces, and what it does **not** do |
| `tools` | The only tools it may call. Reviewers are read-only. |
| `disallowedTools` | Tools it may never call. `Agent` here means it cannot start its own subagents. |
| `maxTurns` | A cap on its number of turns |
| `skills` | Skills preloaded into its context. `skills: []` means none. |

The "does not" clause is a boundary. A reviewer that cannot edit code reports problems instead of quietly patching them, so you see every finding.

Codex uses the same agents in TOML: `agents/codex/<name_with_underscores>.toml`. These files are generated from the Claude files. Text that differs by runtime sits between `<!-- claude-only -->` and `<!-- /claude-only -->`, or inside `<!-- codex-only ... -->`, in the Claude file.

## 3. The families

| Family | Prefix | Typical work |
|---|---|---|
| AI and ML | `ai-` | Agent architecture, context and retrieval design, evals, MLOps, data science, forecasting |
| Data | `data-` | Analytics models, schemas, SQL tuning, streaming, governance, instrumentation |
| Development | `dev-` | Implement, test first, review, research, plan migrations, map dependencies, build context packets |
| Documentation | `docs-` | PRDs, docs structure, runbook and docs audits, note curation |
| Operations | `ops-` | Incidents, rollback plans, rollout reviews, platform, cost |
| Product | `product-` | Discovery, scope, strategy, user research |
| Quality | `qa-` | Debugging, test review, observability, resilience, mobile release |
| Software | `software-` | Security, performance, architecture, frontend, mobile, payments, accessibility, UX |
| Marketing | `marketing-` | Strategy, SEO, answer engines, paid acquisition, creative, email, PR, analytics |
| Startup | `startup-` | Competition, pricing, growth, partnerships, negotiation, trends, review mining |

The marketing and startup agents in this edition carry no preloaded skills; they run on their own instructions. Every agent and its preloaded skills are in the [catalog](reference/catalog.md#subagents).

## 4. Use a subagent

In Claude Code, name the agent and the task:

```text
Use dev-feature-reviewer on the diff in src/payments.
Use software-security-reviewer and software-performance-reviewer in parallel on this PR.
```

- With the plugin, the agent's name has the prefix `ai-agents:`, for example `ai-agents:dev-feature-reviewer`.
- `/agents` lists the agents Claude Code can see.

Write a good brief. A subagent starts with none of your conversation. Give it:

1. The goal, in one sentence.
2. The exact paths or the diff to look at.
3. What you already know or ruled out.
4. What to return, and how short.

In Codex, agents live in `~/.codex/agents/` with snake_case names, for example `dev_feature_reviewer`. Ask Codex to spawn the agent by that name.

## 5. Teams

A team recipe is `agents/teams/<id>/team.yaml`. The [catalog](reference/catalog.md#teams) lists all 8 teams and their members.

| Team | Use it for |
|---|---|
| `dev-feature-delivery` | Research, implement and review one change in stages |
| `software-code-review-board` | A security, performance and test review of one diff |
| `dev-migration-map` | Plan a framework, repository or platform migration |
| `dev-context-preparation` | Build reusable context (repo profiles, code graphs, task packets) before engineering work |
| `docs-knowledge` | Docs structure, PRDs, note retrieval and docs quality |
| `product-surface` | Frontend, UX, accessibility and localisation review of one surface |
| `ai-knowledge-bot-builder` | Design a bot with memory and a knowledge base |
| `marketing-campaign` | The roster for the `marketing-campaign` workflow (opt-in) |

What a recipe controls:

- `members`: the core roster, installed by default.
- `expansion_gate.candidate_specialists`: optional members, installed only with `--include-candidates`.
- `required_context`: what you must provide before the team starts.
- `concurrency_mode`: `staged` (one stage after another) or `parallel`.
- `synthesis_owner`: the member who merges the results.
- `owned_files`: which member may write which files. Most members are read-only.
- `do_not_touch`: paths no member may change.

## 6. Install and remove

All commands run from the repository root.

```bash
# List
bash skills/universal/agents-subagents/scripts/deploy-preset.sh --list
bash skills/universal/agents-subagents/scripts/deploy-preset.sh --list-members

# Install a team for Claude Code, for this repository only
bash skills/universal/agents-subagents/scripts/deploy-preset.sh dev-migration-map --platform claude --project

# Install one agent for Codex, for your user
bash skills/universal/agents-subagents/scripts/deploy-preset.sh software-security-reviewer --member --platform codex --user

# Remove a team
bash skills/universal/agents-subagents/scripts/deploy-preset.sh software-code-review-board --platform claude --project --remove
```

| Flag | Meaning |
|---|---|
| `--member` | The target is one agent |
| `--platform claude\|codex` | Default: `claude` |
| `--user`, `--project`, `--repo PATH` | Where to install. Default: `--user`. |
| `--include-candidates` | Also install the optional specialists |
| `--force` | Replace existing agent files |
| `--refresh-managed` | Refresh only files the installer owns and you have not changed |
| `--remove` | Uninstall |

Bulk install of every default team:

```bash
bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --dry-run
bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --confirm-bulk-deploy --platform both
bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --confirm-bulk-deploy --include-opt-in
```

- Without `--dry-run` or `--remove`, the bulk install refuses to write unless you pass `--confirm-bulk-deploy`.
- `--platform` takes `claude`, `codex` or `both`. The default is `both`.

How installs behave:

- An install copies files. It does not link them. Run it again after you change an agent.
- The installer records a checksum for each file it writes. A refresh replaces only files you have not changed; your local edits stay.
- An install rewrites links of the form `../../skills/universal/agents-subagents/references/<file>.md` to the installed skill path, so they keep working.

## 7. Subagent, team or workflow?

| You need | Use |
|---|---|
| One specialist opinion | A subagent |
| A fixed group of specialists you run often | A team, installed once |
| A process with checks: refuters, frozen tests, round caps, a tree check | A saved [workflow](workflows.md) |

A prompt that asks several agents to "review, then refute, then fix" is not a workflow. It has none of the checks in code. Use the saved workflow.
