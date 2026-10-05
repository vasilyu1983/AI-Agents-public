# AI-Agents

**Ready-made expertise and multi-agent runs for Claude Code and Codex.**

Out of the box, Claude Code works as one assistant in one chat. This repository adds three things:

- **Skills:** instructions the assistant loads by itself when your task needs them, for example a code-review checklist.
- **Subagents:** specialists, such as a security reviewer, that work in a separate context and report back.
- **Saved workflows:** multi-step runs, such as "review my diff with 4 reviewers, then try to disprove each finding". The rules of each run are enforced in code, so an agent cannot skip a step.

Install it as a Claude Code plugin in three commands, or clone it and link it.

| What you get | How many | Where |
|---|---|---|
| Skills: engineering, AI, data, QA, ops, docs, research, applied theory | 140+ | `skills/universal/` |
| Subagents with explicit boundaries | 85 | `agents/claude/`, `agents/codex/` |
| Team recipes | 8 | `agents/teams/` |
| Saved workflows with guarantees in code | 8 | `agents/workflows/` |
| Opt-in hooks: git safety, lint-config guard, notifications | 3 | `hooks/` |
| Language and domain rules | 14 folders | `rules/` |

The exact, current list is in the generated [catalog](docs/reference/catalog.md).

## Quick start

Pick **one** install path. Claude Code only: use the plugin. Codex, or you want to edit skills: clone and link.

### Claude Code plugin

```text
/plugin marketplace add vasilyu1983/AI-Agents-public
/plugin install ai-agents@ai-agents
/reload-plugins
```

Then, in a repository with uncommitted changes:

```text
/ai-agents:adversarial-review
```

Four reviewers read your diff. Two more agents (refuters) then try to disprove each finding. A finding is dropped only if both disprove it. The run changes no files.

**Cost:** each reviewer and refuter is a full agent session on your own plan. One run starts 4 reviewers plus 2 refuters per finding, and takes several minutes. Run it on a small diff first.

The run ends with a verdict: `CLEAN` (no findings), `FINDINGS` (each with `file:line`, severity and title), or `INCOMPLETE` (an agent failed; re-run). [Workflows](docs/workflows.md#adversarial-review) shows the full result.

### Clone and link (Claude Code and Codex)

```bash
git clone https://github.com/vasilyu1983/AI-Agents-public.git ~/AI-Agents-public
cd ~/AI-Agents-public
bash scripts/distribution/sync-skills.sh
```

Then start a new session and type `/adversarial-review`. In Codex, which has no workflow commands, invoke the `run-workflow` skill and name the workflow; the skill makes Codex follow the workflow step by step.

[Getting started](docs/getting-started.md) covers both paths, subagent installs, checks, updates and removal.

## Documentation

| Guide | Read it to |
|---|---|
| [Getting started](docs/getting-started.md) | Install, check, update and uninstall |
| [Concepts](docs/concepts.md) | Understand skills, subagents, teams, workflows, hooks and rules, and how they connect |
| [Workflows](docs/workflows.md) | Run each of the 8 workflows: arguments, stages, verdicts, cost |
| [Skills](docs/skills.md) | Find, use and read skills |
| [Agents and teams](docs/agents-and-teams.md) | Use, brief and install subagents and teams |
| [Hooks and safety](docs/hooks-and-safety.md) | Install the hooks; what the git guard blocks; recovery |
| [Codex](docs/codex.md) | What differs in Codex |
| [Customizing](docs/customizing.md) | Write your own skill, subagent, team, workflow or rule |
| [Troubleshooting](docs/troubleshooting.md) | Fix a symptom |
| [Catalog](docs/reference/catalog.md) | Every skill, subagent, team, workflow and board, generated from the files |

## The workflows

| Workflow | What it does | Edits files? |
|---|---|---|
| `adversarial-review` | Four reviewers on a diff, then two refuters per finding | No |
| `review-fix-loop` | Review and fix in rounds, or build against frozen acceptance checks | Yes, in scope |
| `source-check` | Checks every quote, link, figure and attribution in a document against its source, then fixes confirmed defects | Yes, the target |
| `feature-delivery` | Plan, test first, implement, review. Stops for your approval after the plan. | Yes, the plan's files |
| `build-mvp` | Cuts a PRD into thin slices and builds each approved slice; a fresh judge checks every slice | Yes, each slice's files |
| `epic-delivery` | Delivers an epic as file-owning tasks in dependency waves, then one integration review | Yes, each task's files |
| `expert-board` | A board of specialists on one decision: blind memos, optional debate, weighted synthesis | No |
| `marketing-campaign` | Research, one positioning lock, channel drafts, review against the lock | No |

No workflow commits, pushes, opens a pull request or approves anything. You review and commit.

## Why it works this way

These are design choices. The workflow tests in `agents/workflows/test-*.mjs` check the ones enforced in code.

- **Guarantees live in code, not in prompts.** Fresh agents each round, a two-refuter quorum, frozen acceptance checks, round caps and plateau stops are enforced by the workflow runtime. A prompt that imitates a workflow has none of them.
- **The tree is checked, not trusted.** Writing workflows snapshot the working tree after every step. A write outside the plan, a staged file, a moved `HEAD` or a touched instruction file stops the run.
- **Every subagent states what it does not do.** Reviewers cannot edit, so they report instead of quietly patching.
- **Skills hold judgment, not data.** A skill tells the agent what it would get wrong without it. Versions, prices and limits change, so skills look them up instead of hard-coding them.
- **Small context.** The runtime reads only each skill's short description until a task needs the skill. References load only when a step asks for them.

## Layout

```text
skills/universal/<name>/   SKILL.md + references/, scripts/, data/, assets/
agents/claude/             subagent definitions (source)
agents/codex/              Codex subagents (generated)
agents/teams/<id>/         team recipes
agents/workflows/          <id>.manifest.json (source) -> <id>.js and <id>.codex-plan.json (generated)
agents/templates/          templates for new agents and teams
hooks/                     opt-in hooks, their tests, and hooks.json
rules/                     common, language and domain rules
scripts/distribution/      sync-skills.sh: the clone installer
custom-gpt/                Custom GPT prompts
docs/                      the guides above
.claude-plugin/            Claude Code plugin and marketplace manifests
```

## What this edition leaves out

This is the public edition of a private library. It is built from an explicit allowlist, and every build is scanned for private names and credential patterns before release.

- Marketing and startup domain playbooks are not published. The marketing and startup subagents run on their own instructions.
- Legal, client-specific and personal content is not published, nor are the workflows and boards that depend on it. All 8 workflows listed above work in this edition.
- The library's own maintenance tooling (graph export, skill router, audit tools) is not published.

## Requirements

Claude Code with saved-workflow support (type `/workflows`; if the command is unknown, update Claude Code), or Codex; `git`; Python 3.10 or later; Node.js 18 or later for the workflow tests. macOS or Linux (Windows through WSL).

## Security

The hooks are opt-in, and the plugin installs none. Skills may ship scripts that an agent can run; read them before you allow them. See [SECURITY.md](SECURITY.md) to report a problem.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under MIT; see [LICENSE](LICENSE).
