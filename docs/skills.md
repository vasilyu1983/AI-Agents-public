# Skills

A skill is a folder of instructions that the runtime loads when your task matches it. This page explains how to find, use and judge the skills in this repository. To write a new one, see [Customizing](customizing.md#write-a-skill).

- [1. The families](#1-the-families)
- [2. How a skill loads](#2-how-a-skill-loads)
- [3. Find the right skill](#3-find-the-right-skill)
- [4. Use a skill on purpose](#4-use-a-skill-on-purpose)
- [5. Read a skill](#5-read-a-skill)
- [6. Scripts inside skills](#6-scripts-inside-skills)
- [7. Learnings](#7-learnings)

## 1. The families

The prefix of a skill's name is its family. The [catalog](reference/catalog.md#skills) lists every skill with its description.

| Family | Prefix | Covers |
|---|---|---|
| Software engineering | `software-` | Architecture, backend, frontend, mobile, security, code review, clean code, payments, UX |
| AI and ML | `ai-` | LLM apps, agents, RAG, evals, fine-tuning, MLOps, inference, prompt engineering, context design |
| AI coding-agent internals | `ai-coding-agents-` | How coding-agent harnesses work: runtime core, state, safety envelope, settings and policy, plugins, provider runtime, observability and evals |
| Agent engineering | `agents-` | Writing skills, subagents, hooks, memory files and MCP servers; swarm orchestration; skill feedback loops |
| Quality and testing | `qa-` | Test strategy, debugging, refactoring, resilience, accessibility, observability |
| Development workflow | `dev-` | Git workflow and commit messages, API design, context preparation (code graphs, multi-repo), dependency management, workflow planning, AI-coding metrics |
| Data | `data-` | Analytics engineering, lakehouse platforms, Metabase, SQL optimisation, streaming |
| Operations | `ops-` | Incident response, DevOps platforms, cost optimisation, NUKE CI/CD builds |
| Documentation | `docs-` | Codebase docs, AI-ready PRDs, note retrieval |
| Document formats | `document-` | Reading and writing PDF, Word, spreadsheet and slide files |
| Research | `research-` | arXiv triage, Git repository mining, research scouting |
| Product | `product-` | Product management, help-center content |
| Foundations | `foundations-` | Applied theory: decision, game, control, queueing, information, reliability and team theory; statistics, causal inference, optimisation, formal methods, distributed systems, safety engineering and more |
| Game development | `gamedev-` | Godot and Roblox |
| Workflow runner | `run-workflow` | Runs a saved workflow, mainly from Codex |

## 2. How a skill loads

1. At session start, the runtime reads each skill's `name` and `description` only.
2. You describe a task. The runtime compares it with the descriptions.
3. It loads the `SKILL.md` of the best match.
4. `SKILL.md` tells the agent when to open a reference, for example "read `references/auth.md` when the diff touches login". The reference loads only then.

Every description has the same shape: "Does X. Use when Y." The "Use when" part is what the runtime matches. If a skill does not load for a task that should match, see [Troubleshooting](troubleshooting.md).

## 3. Find the right skill

| Method | How |
|---|---|
| Ask the agent | "Which skill covers database migrations?" The agent sees all descriptions. |
| Search the catalog | Open [`docs/reference/catalog.md`](reference/catalog.md) and search the page. |
| Search the files | `grep -l "migration" skills/universal/*/SKILL.md` |
| Check a name | `ls skills/universal/<name>/SKILL.md`. A skill exists only if this file exists. |

Do not guess a skill name. A plausible name that does not exist fails silently: the agent works without the skill.

## 4. Use a skill on purpose

- **Let it load.** Describe the task plainly. This is the normal path.
- **Name it.** "Use the software-code-review skill on this diff." The agent loads it even if the match was weak.
- **Invoke it.** In Claude Code, `/<skill-name>` loads a skill directly. With the plugin, add the prefix: `/ai-agents:<skill-name>`.
- **Manual-only skills.** A skill whose front matter has `disable-model-invocation: true` never loads by itself. You must invoke it. `run-workflow` is one.

## 5. Read a skill

A `SKILL.md` is written for an agent, but it is readable. The usual sections:

| Section | Tells you |
|---|---|
| Front matter | `name`, `description`, and sometimes `version` and `last_validated` |
| Quick reference | A table: situation and action |
| Workflow | The ordered steps the agent follows |
| Gotchas | Real failures the skill prevents |
| Navigation | Links to the skill's references and to neighbouring skills |

A skill holds judgment, not current data. Where a fact changes quickly, such as a version, a price or a limit, the skill gives a step to look it up instead of a number.

## 6. Scripts inside skills

Some skills ship runnable scripts in `scripts/`. The agent may run them as part of the skill.

- Read a script before you allow it to run. [SECURITY.md](../SECURITY.md) explains what runs on your machine.
- Scripts that need extra packages say so at the top of the file or in the skill.
- Data a script reads lives in `data/`, with a `source` and a `last_verified` date.

## 7. Learnings

Many skills have two learnings files:

| File | Content |
|---|---|
| `learnings.md` | Dated lessons appended after real use |
| `learnings.consolidated.md` | The reviewed summary of those lessons |

The agent reads the consolidated file when it is relevant. A lesson does not change `SKILL.md` by itself; a maintainer folds proven lessons into the skill.
