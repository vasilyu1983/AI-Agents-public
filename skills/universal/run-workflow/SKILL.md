---
name: run-workflow
description: "Launches a saved multi-agent workflow by id on Claude Code or Codex. Use when the user asks to run a saved workflow or review loop."
compatibility: "Claude Code and Codex. Manual-only: `disable-model-invocation` applies in Claude Code; `agents/openai.yaml` sets `policy.allow_implicit_invocation: false` for Codex. Needs the library checkout that holds `agents/workflows/`."
disable-model-invocation: true
version: "1.0"
last_validated: 2026-10-03
---

# Run a Saved Workflow

A saved workflow keeps its guarantees in code or in a generated plan, not in a prompt: fresh agents each round, the refuter quorum, the frozen acceptance checks, the round cap. This skill finds the workflow and hands off to that code or plan. It never improvises a workflow of its own.

## Quick Reference

| Situation | Action |
|---|---|
| Which workflows exist? | Read `agents/workflows/*.manifest.json` now. The id is the file name before `.manifest.json`. Never list from memory. |
| Claude Code | Give the user the exact `/<id>` command with its args. Do not run the steps yourself. |
| Codex, `<id>.codex-plan.json` exists | Execute its `execution_contract` from this parent session with `spawn_agent` and `wait_agent`. |
| Codex, manifest engine `command` | Run the manifest's `command.run` with the chosen options. No agents. |
| Codex, no plan and not a command | Stop. Say this workflow has no Codex plan yet. |
| A member failed or returned nothing usable | The verdict is INCOMPLETE, never a pass. |
| Commit, push, merge or open a PR | Never. Report the tree state and leave it to the user. |

## Workflow

1. **Find the library.** Installs are symlinks, so resolve this skill's real path first. `agents/workflows/` sits three levels above the real skill folder (`skills/universal/run-workflow/`):

   ```bash
   lib="$(cd "$(dirname "$(realpath "<this-skill-dir>/SKILL.md")")/../../.." && pwd)"
   ls "$lib"/agents/workflows/*.manifest.json
   ```

2. **List and pick.** For each manifest, show the id, `workflow.engine` and `workflow.description`. If the user named an id with no manifest, say so and list the ids that exist. Take the args from `workflow.whenToUse`. Ask for a missing required arg, such as the frozen spec and acceptance checks of a build loop, instead of inventing one.

3. **Claude Code: hand off.** Reply with the one command to type: `/<id>` followed by the args object `whenToUse` describes. Do not re-implement the workflow inline, because an imitation drops the checks the script enforces in code. If `/<id>` is not found, the library sync has not linked `agents/workflows/<id>.js` into the Claude workflows folder; say so and stop.

4. **Codex: execute the plan from the parent session.**
   - If the plan has a `context_budget` block, follow its `extract` command instead of loading the whole file.
   - Run the `execution_contract` phases in order. Each phase names its owner, its primitive (`spawn_agent`, `wait_agent`, `send_input`, `close_agent`, local reasoning or an immediate return) and its gate. This session does every dispatch, wait, merge and verdict; workers never spawn workers.
   - Brief each worker on its own: the plan's `task_name` and `fork_turns`, its rules, and the user's args. Keep to `workspace`: one writer at a time.
   - Keep to the plan's agent cap. Spawn only the members, refuter `count`, `max_dynamic_members` and rounds (`maxRounds`, else `max_rounds_default`) it allows. Run no more at once than the session's thread limit, and queue the rest.
   - Apply `incomplete_rule`: a failed, timed-out or malformed member makes the verdict INCOMPLETE. Name that member. Do not rerun it silently or do its part yourself.
   - Close every worker you spawned before you report.

5. **Report.** Give the verdict, the stop reason, the open items or escalation, and any member that failed. When a fixer or builder ran, list its changes from `git status --short` and say that nothing was committed.

## Gotchas

- A `.js` file in `agents/workflows/` with no manifest still runs on Claude Code as `/<id>`, but it has no Codex plan. Do not offer it on Codex.
- A plan's stop rule is part of the contract. Stopping early at a "good enough" round, or running past the cap, breaks the guarantee the user asked for.

## Navigation

- [agents-subagents](../agents-subagents/SKILL.md) - choose between a saved workflow, subagents and a team; Claude saved-workflow behaviour is in its [workflow runtime reference](../agents-subagents/references/workflow-runtime.md).
- [agents/workflows/](../../../agents/workflows/) - the manifests, Claude scripts and generated Codex plans.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
