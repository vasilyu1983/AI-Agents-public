# Getting Started

This guide installs the harness, checks that it works, and shows how to update and remove it.

- [1. Requirements](#1-requirements)
- [2. Choose one install path](#2-choose-one-install-path)
- [3. Path A: Claude Code plugin](#3-path-a-claude-code-plugin)
- [4. Path B: clone and link](#4-path-b-clone-and-link)
- [5. Install subagents for Codex or by team](#5-install-subagents-for-codex-or-by-team)
- [6. Add the hooks (optional)](#6-add-the-hooks-optional)
- [7. Check the install](#7-check-the-install)
- [8. Your first ten minutes](#8-your-first-ten-minutes)
- [9. Update](#9-update)
- [10. Uninstall](#10-uninstall)

## 1. Requirements

| Need | Why |
|---|---|
| Claude Code, Codex, or both | The two runtimes this harness serves |
| `git` | To clone the repository (path B) and for the workflows' tree checks |
| Python 3.10 or later | Generators, hooks and bundled skill scripts |
| Node.js 18 or later | Only to run the workflow tests |
| macOS or Linux | The install scripts are Bash. On Windows, use WSL. |

The harness needs no API key of its own. It runs inside your Claude Code or Codex session and uses that session's model.

## 2. Choose one install path

| Path | You get | Choose it when |
|---|---|---|
| **A. Plugin** | Skills, Claude subagents and saved workflows, managed by Claude Code | You use Claude Code only and want the fastest setup |
| **B. Clone and link** | Skills for Claude Code and Codex, saved workflows, and edits that take effect at once | You use Codex, or you want to change skills and agents |

Use only one path on a machine. If both are active, Claude Code lists each skill twice.

## 3. Path A: Claude Code plugin

In Claude Code, run:

```text
/plugin marketplace add vasilyu1983/AI-Agents-public
/plugin install ai-agents@ai-agents
```

- `ai-agents` before the `@` is the plugin. `ai-agents` after the `@` is the marketplace.
- The plugin reads `.claude-plugin/plugin.json`. It adds `skills/universal/`, `agents/claude/` and the 8 workflow scripts in `agents/workflows/`.
- The plugin does not install hooks. Section 6 adds them by hand.
- Run `/reload-plugins`, or start a new session, to load the plugin.
- **Plugin names carry a prefix.** Run a workflow as `/ai-agents:adversarial-review`, and name a subagent as `ai-agents:dev-feature-reviewer`. With path B, the same items have no prefix: `/adversarial-review`. The other guides use the short form.

## 4. Path B: clone and link

1. Clone the repository to a folder you will keep. The links point into this folder, so do not delete or move it later.

   ```bash
   git clone https://github.com/vasilyu1983/AI-Agents-public.git ~/AI-Agents-public
   cd ~/AI-Agents-public
   ```

2. Link the skills and workflows:

   ```bash
   bash scripts/distribution/sync-skills.sh
   ```

   | Command | Links |
   |---|---|
   | `sync-skills.sh` | Both targets below |
   | `sync-skills.sh claude` | Skills into `~/.claude/skills/`, workflows into `~/.claude/workflows/` |
   | `sync-skills.sh agents` | Skills into `~/.agents/skills/`, which Codex reads |

   The script prints one summary line per target: `Linked`, `External skipped`, `Stale removed` and `Total visible`.

3. Start a new Claude Code or Codex session.

What the sync script will and will not do:

- It creates symlinks only. An edit in the clone takes effect at once, with no re-sync.
- It never overwrites a real folder, a plain file, or a symlink that points outside this repository. It reports each of those as skipped.
- It removes only symlinks that point into this repository and no longer match a current skill or workflow.

## 5. Install subagents for Codex or by team

The plugin (path A) already gives Claude Code every subagent. Use this section for Codex, or to install only some agents.

```bash
# See what exists
bash skills/universal/agents-subagents/scripts/deploy-preset.sh --list            # teams
bash skills/universal/agents-subagents/scripts/deploy-preset.sh --list-members    # single agents

# Install one team for Claude Code, for your user
bash skills/universal/agents-subagents/scripts/deploy-preset.sh software-code-review-board --platform claude --user

# Install one team for Codex
bash skills/universal/agents-subagents/scripts/deploy-preset.sh dev-feature-delivery --platform codex --user

# Install one agent
bash skills/universal/agents-subagents/scripts/deploy-preset.sh software-security-reviewer --member --platform codex --user
```

| Flag | Meaning |
|---|---|
| `--member` | The target is one agent, not a team |
| `--platform claude\|codex` | Runtime. Default: `claude` |
| `--user` | Install into `~/.claude/agents/` or `~/.codex/agents/` (default) |
| `--project` | Install into `.claude/agents/` or `.codex/agents/` of the current repository |
| `--repo PATH` | Install into another repository |
| `--include-candidates` | Also install the team's optional specialists |
| `--force` | Replace existing agent files |
| `--remove` | Uninstall the team or agent |

To install every default team at once, preview first. The bulk install refuses to write without `--confirm-bulk-deploy`.

```bash
bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --dry-run
bash skills/universal/agents-subagents/scripts/deploy-all-teams.sh --confirm-bulk-deploy --platform both
```

Installed agents are copies, not links. After you change an agent in the clone, deploy it again.

## 6. Add the hooks (optional)

Hooks run code on every matching tool call, so they are opt-in. [Hooks and safety](hooks-and-safety.md) explains what each one blocks and gives the exact settings for Claude Code and Codex.

## 7. Check the install

| Check | How | Expected |
|---|---|---|
| Skills load | In a new session, ask: "Which skills do you have for code review?" | Names such as `software-code-review` |
| One skill, by path | `ls ~/.claude/skills/software-code-review/SKILL.md` (path B) | The file exists |
| Workflows | In Claude Code, type `/adversarial-review` (plugin: `/ai-agents:adversarial-review`) | Claude Code offers the workflow |
| Subagents | In Claude Code, run `/agents` | Names such as `dev-feature-reviewer` (plugin: `ai-agents:dev-feature-reviewer`) |
| Codex agents | `ls ~/.codex/agents/` | Files such as `dev_feature_reviewer.toml` |
| Repository checks | `python3 skills/universal/agents-subagents/scripts/generate_workflows.py --check` in the clone | Exit code 0 |

## 8. Your first ten minutes

1. **Use a skill without naming it.** Ask a normal task, for example "Review this function for SQL injection." The runtime matches your task against each skill's description and loads the skill that fits.
2. **Review your current changes.** In a repository with uncommitted edits, type:

   ```text
   /adversarial-review
   ```

   With the plugin, type `/ai-agents:adversarial-review`. Four reviewers read the diff. Two refuters then try to disprove each finding. A finding survives only if at least one refuter fails to disprove it. The run changes no files.
3. **Ask for a specialist.** "Use dev-feature-reviewer on this diff." The subagent works in its own context and returns a report.
4. **Plan a change.** Type:

   ```text
   /feature-delivery {"mode": "fix", "task": "<the bug, in one sentence>"}
   ```

   The first run stops with a plan for you to approve. See [Workflows](workflows.md#feature-delivery) for the second run.

## 9. Update

| Path | Update |
|---|---|
| A. Plugin | `/plugin marketplace update ai-agents`, then `/reload-plugins` |
| B. Clone | `git -C ~/AI-Agents-public pull`, then `bash scripts/distribution/sync-skills.sh` to link new skills and remove stale links |

Deployed subagents are copies. Run `deploy-preset.sh` again for each team you use, with `--force` if you have not changed the installed copy.

## 10. Uninstall

**Path A:** run `/plugin uninstall ai-agents@ai-agents`, then `/plugin marketplace remove ai-agents`.

**Path B:** remove only the symlinks that point into your clone. First list them:

```bash
REPO="$HOME/AI-Agents-public"
find ~/.claude/skills ~/.agents/skills ~/.claude/workflows -maxdepth 1 -type l -lname "$REPO/*" -print
```

If the list shows only links into your clone, delete them:

```bash
find ~/.claude/skills ~/.agents/skills ~/.claude/workflows -maxdepth 1 -type l -lname "$REPO/*" -delete
```

**Subagents:** run `deploy-preset.sh <team> --remove` with the same `--platform` and scope you installed with.

**Hooks:** remove the entries you added from your settings files, and delete the scripts from `~/.agents/hooks/`.
