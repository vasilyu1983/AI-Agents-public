# Troubleshooting

Find the symptom, then apply the fix. If none matches, open an issue with the command you ran and the exact error.

## Install

| Symptom | Cause | Fix |
|---|---|---|
| Claude Code lists each skill twice | Both the plugin and the symlinks deliver skills | Keep one path. Remove the plugin, or remove the links ([Getting started, section 10](getting-started.md#10-uninstall)). |
| `sync-skills.sh` reports `External skipped` | A real folder, file or foreign symlink already has that skill's name | Expected: the script never overwrites them. Rename or remove the other copy if you want this one. |
| A skill is missing after `git pull` | The new skill is not linked yet | `bash scripts/distribution/sync-skills.sh` |
| Skills stop working after you moved the clone | The links point to the old folder | Run `sync-skills.sh` from the new location; it replaces links into this repository |
| `/plugin install` cannot find `ai-agents` | The marketplace was not added | `/plugin marketplace add vasilyu1983/AI-Agents-public` first |
| Plugin items do not appear | The session loaded before the install | `/reload-plugins`, or start a new session |

## Skills

| Symptom | Cause | Fix |
|---|---|---|
| A skill does not load for a task that fits | The task wording does not match the description | Name the skill: "Use the software-code-review skill." |
| A skill name "does not exist" | The name was guessed | Check `ls skills/universal/<name>/SKILL.md`, or search the [catalog](reference/catalog.md) |
| `run-workflow` never starts by itself | It is manual-only | Invoke it by name |
| A skill script fails with a missing module | The script needs a package | Read the top of the script or the skill; install the package in a virtual environment |

## Workflows

| Symptom | Cause | Fix |
|---|---|---|
| `/<id>` is not found | The workflow is not linked, or you used the wrong name form | Clone install: `sync-skills.sh claude`. Plugin: use `/ai-agents:<id>`. |
| A workflow runs old code after an edit | The session read the workflow before the edit | Start a new session |
| `BLOCKED head_moved` | Someone committed or switched branch during the run | Do not commit during a run. Re-run. |
| `BLOCKED index_changed` | Something staged files during the run | Unstage, then re-run |
| `BLOCKED protected_changed` | A protected file such as `AGENTS.md` changed | Edit protected files yourself, outside the run |
| `BLOCKED out_of_scope` | A writer changed a file outside its plan | Read the escalation; widen the plan if the change was needed |
| `BLOCKED tests_not_red` | `feature-delivery`: the new tests pass before the change | The tests do not pin the behaviour. Fix the plan's tests. |
| `INCOMPLETE` | An agent failed, timed out, or broke the schema | Re-run. The result names the agent. |
| `expert-board` stops at once | `contextData` misses a required key | Add every key the board lists ([catalog](reference/catalog.md#expert-boards)) |
| A run is slow or costly | Many findings, rounds or members | Narrow `target`, drop extra `dimensions`, lower `maxRounds` |

## Hooks

| Symptom | Cause | Fix |
|---|---|---|
| Every `git` command is blocked | `git-safety-guard.py` is missing from `~/.agents/hooks/` | Link it again ([Hooks and safety](hooks-and-safety.md#2-install-the-hooks)), or remove its settings entry |
| `BLOCKED by git-safety-guard` | The command can destroy uncommitted work | Use the safe alternative in [Hooks and safety, section 4](hooks-and-safety.md#4-when-a-command-is-blocked) |
| A Codex hook does not run | The hook is new or changed and not trusted | Approve it under `/hooks`, then start a new session |
| An agent edited `.eslintrc` anyway | It used a shell command, not `Write` or `Edit` | Expected limit of `config-guard.py`; review the diff |
| No desktop notification | No notifier found | macOS needs `osascript`; Linux needs `notify-send` |

## Subagents

| Symptom | Cause | Fix |
|---|---|---|
| A deployed agent shows old behaviour | Installs are copies | Run `deploy-preset.sh` again with `--force` |
| `generate_codex_agents.py --check` fails | A Codex file was edited by hand, or a Claude file changed | `generate_codex_agents.py --write` |
| A Codex agent is not found | Codex names use underscores | Use `dev_feature_reviewer`, not `dev-feature-reviewer` |
