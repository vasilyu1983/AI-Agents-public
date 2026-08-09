# AI Agents Library

## Production-Ready AI Agent Prompts & Skills

<div align="center">

**28 Custom GPT agents** and **140 agent skills** for ChatGPT, Claude Code, and Codex.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Custom GPTs](https://img.shields.io/badge/Custom%20GPTs-28-blue)](./custom-gpt)
[![Skills](https://img.shields.io/badge/Skills-140-purple)](./frameworks/shared-skills)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Quick Start](#quick-start) • [Skills](#agent-skills) • [Custom GPTs](#custom-gpt-agents) • [Contributing](#contributing)

</div>

---

## What's Inside

Two things, usable independently:

- **[`frameworks/shared-skills/`](frameworks/shared-skills/)** — 140 agent skills following the
  [Agent Skills specification](https://agentskills.io/specification). Drop into `~/.claude/skills/`.
- **[`custom-gpt/`](custom-gpt/)** — 28 Custom GPT system prompts for ChatGPT, written to fit
  the GPT builder's 8000-character Instructions limit.

## Quick Start

```bash
git clone https://github.com/vasilyu1983/AI-Agents-public.git
cd AI-Agents-public

# One skill
ln -s "$PWD/frameworks/shared-skills/skills/ai-rag" ~/.claude/skills/ai-rag

# All of them
for s in frameworks/shared-skills/skills/*/; do
  ln -s "$PWD/$s" ~/.claude/skills/"$(basename "$s")"
done
```

Symlinks mean edits take effect immediately — no re-sync step.

For a Custom GPT: open `custom-gpt/<category>/<agent>/01_*.md`, paste into the GPT builder's
Instructions field, and attach the sibling `02_sources-*.json` as Knowledge if present.

## Agent Skills

| Family | Count | Covers |
| --- | ---: | --- |
| `software-*` | 34 | Backend, frontend, iOS, Android, desktop, security, payments, performance |
| `ai-*` | 21 | RAG, evals, prompt engineering, pretraining, post-training, inference, MLOps |
| `qa-*` | 17 | Test strategy, debugging, resilience, observability, accessibility, Playwright |
| `foundations-*` | 16 | Queueing, control, information, game, decision, reliability theory for systems |
| `ai-coding-agents-*` | 13 | Coding-agent runtime internals: sandboxing, permissions, sessions, tools |
| `dev-*` | 10 | Git workflow, API design, dependency management, code graphs, planning |
| `agents-*` | 6 | Hooks, MCP servers, skill authoring, swarm orchestration, repo memory |
| `data-*` | 5 | Lakehouse, streaming, SQL optimization, analytics engineering |
| `ops-*` | 4 | DevOps platform, incident response, cost optimization, CI/CD |
| `document-*` | 4 | docx, pdf, pptx, xlsx |
| `docs-*` | 3 | Docs-as-code, AI-ready PRDs, note retrieval |
| `research-*` | 3 | arXiv triage, GitHub mining, research method extraction |
| `product-*` | 2 | Product management, help centers |
| `gamedev-*` | 2 | Godot, Roblox |

Two areas are unusually deep and harder to find elsewhere: **coding-agent runtime internals**
(how agent CLIs actually implement sandboxing, permissions, and session resume) and
**systems-theory foundations** (queueing and control theory applied to real design decisions,
not as abstract math).

Full breakdown: [`frameworks/shared-skills/README.md`](frameworks/shared-skills/README.md).

### How a skill is structured

```text
<skill-name>/
├── SKILL.md      # Entry point — frontmatter + routing. Kept small.
├── references/   # Depth, loaded only when the task needs it
├── scripts/      # Deterministic helpers — no model call needed
├── assets/       # Templates and output contracts
└── data/         # sources.json and curated data
```

`SKILL.md` stays cheap enough to hold in context; `references/` carry the detail and cost
nothing until read.

## Custom GPT Agents

28 agents across six categories:

| Category | Count |
| --- | ---: |
| Productivity | 8 |
| Lifestyle | 7 |
| Programming | 5 |
| Education | 3 |
| Research & Analysis | 3 |
| Writing | 2 |

Each folder holds `01_*.md` (the system prompt) and, where useful, a curated sources JSON.

## Repository Layout

```text
AI-Agents-public/
├── custom-gpt/                      # 28 Custom GPT prompts by category
├── frameworks/
│   └── shared-skills/skills/        # 140 agent skills
├── CONTRIBUTING.md
└── LICENSE
```

## Scope

This is a curated public subset of a larger private library. Project-specific, client-scoped,
marketing, startup, and legal skills are not published, and skills depending on internal
libraries are excluded because they cannot be used outside their origin repo.

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Useful contributions:
correcting something that has gone stale, adding a reference that saved you time, or
reporting a skill that misfires.

## License

MIT — see [LICENSE](LICENSE). Use freely, including commercially.
