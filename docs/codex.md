# Codex

The harness serves Codex from the same files as Claude Code. This page lists what differs.

| Part | Claude Code | Codex |
|---|---|---|
| Skills | `~/.claude/skills/` | `~/.agents/skills/` |
| Link the skills | `sync-skills.sh claude` | `sync-skills.sh agents` |
| Subagents | `agents/claude/<name>.md` | `agents/codex/<name_with_underscores>.toml` (generated) |
| Install subagents | `deploy-preset.sh <team> --platform claude` | `deploy-preset.sh <team> --platform codex` |
| Saved workflows | `/<id>`, run by the Claude Code workflow runtime | The `run-workflow` skill runs `<id>.codex-plan.json` from your session |
| Hooks | `~/.claude/settings.json` | `~/.codex/hooks.json` (git safety guard only) |
| Plugin | Supported (`.claude-plugin/`) | Not packaged; use the clone install |

## Set up

Run these in your clone. First link the skills:

```bash
bash scripts/distribution/sync-skills.sh agents
```

Then install subagents. Choose one:

- **Only the teams your workflows need.** [Workflows, section 1](workflows.md#1-choose-a-workflow) lists the team for each workflow. Example:

  ```bash
  bash skills/universal/agents-subagents/scripts/deploy-preset.sh dev-feature-delivery --platform codex --user
  ```

- **Every default team.** This writes one `.toml` file per agent into `~/.codex/agents/`. Preview first; the dry run lists each file. The opt-in `marketing-campaign` team is skipped unless you add `--include-opt-in`.

  ```bash
  bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --dry-run --platform codex
  bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --confirm-bulk-deploy --platform codex
  ```

To remove a team later, run `deploy-preset.sh <team> --platform codex --remove`. Start a new Codex session after any install.

## Run a workflow

1. Invoke the `run-workflow` skill. It is manual-only, so Codex does not start it by itself.
2. Name the workflow id and give its arguments, for example: "Run adversarial-review on branch feature/login."
3. Your Codex session becomes the parent. It follows the plan's `execution_contract`: it starts each worker, waits, merges the results and writes the verdict. Workers never start workers.
4. The parent keeps the plan's caps on members, refuters and rounds. A failed worker makes the verdict `INCOMPLETE`.

[Workflows, section 6](workflows.md#6-run-a-workflow-in-codex) has the full contract.

**Limit.** The Codex plans pass static checks. They have had less end-to-end use than the Claude Code workflows. Report a plan that does not run as described.

## Instructions

Codex reads `AGENTS.md` in each repository. This repository's `AGENTS.md` tells an agent how to work here: the map, the generated files, and the checks.
