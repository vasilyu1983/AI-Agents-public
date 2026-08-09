# Shared Skills

140 agent skills for Claude Code, Codex, and any runtime that supports the
[Agent Skills specification](https://agentskills.io/specification).

Each skill is a self-contained folder: a `SKILL.md` entry point plus optional `references/`
loaded on demand, deterministic `scripts/`, output `assets/`, and curated `data/`.

## Skill Families

| Family | Count | Covers |
| --- | ---: | --- |
| `software-*` | 34 | Backend, frontend, iOS, Android, desktop, security, payments, performance, architecture |
| `ai-*` | 21 | RAG, evals, prompt engineering, pretraining, post-training, inference, MLOps, scaling laws |
| `qa-*` | 17 | Test strategy, debugging, resilience, observability, accessibility, mobile, Playwright |
| `foundations-*` | 16 | Queueing, control, information, game, decision, network, reliability, causal-inference theory |
| `ai-coding-agents-*` | 13 | Coding-agent runtime internals: sandboxing, permissions, sessions, tool and provider runtimes |
| `dev-*` | 10 | Git workflow, API design, dependency management, code graphs, planning |
| `agents-*` | 6 | Hooks, MCP servers, skill authoring, swarm orchestration, repo memory |
| `data-*` | 5 | Lakehouse, streaming, SQL optimization, analytics engineering, Metabase |
| `ops-*` | 4 | DevOps platform, incident response, cost optimization, NUKE CI/CD |
| `document-*` | 4 | docx, pdf, pptx, xlsx creation and extraction |
| `docs-*` | 3 | Docs-as-code, AI-ready PRDs, note retrieval |
| `research-*` | 3 | arXiv triage, GitHub repo mining, research method extraction |
| `product-*` | 2 | Product management, help centers |
| `gamedev-*` | 2 | Godot, Roblox |

Counts are literal directory-name prefixes, so `ai-coding-agents-*` is counted separately
from `ai-*` and the parent `ai-coding-agents` skill falls under `ai-*`. Verify with:

```bash
ls -d skills/*/ | xargs -n1 basename | sed 's/-.*//' | sort | uniq -c | sort -rn
```

## Install

Symlink a skill so edits take effect without re-syncing:

```bash
# Claude Code
ln -s "$PWD/skills/<skill-name>" ~/.claude/skills/<skill-name>

# All skills at once
for s in skills/*/; do ln -s "$PWD/$s" ~/.claude/skills/"$(basename "$s")"; done
```

Then invoke by name in Claude Code. For Codex, point at the skill's `SKILL.md` directly.

## SKILL.md Contract

```yaml
---
name: skill-name
description: "What it does. Use when <trigger condition>."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.0"
last_validated: YYYY-MM-DD
---
```

The `description` is what an agent matches against when routing, so it states both the
capability and the trigger. `compatibility` flags runtime assumptions — `Portable core` means
no runtime-specific dependencies.

## Design Conventions

- **`SKILL.md` stays small.** It routes; `references/` carry the depth. This keeps the hot
  context cheap and loads detail only when the task needs it.
- **Scripts are deterministic.** Anything a plain script can decide should not cost a model call.
- **`data/sources.json`** records where a skill's claims came from, so they can be re-verified
  as the underlying tools change.
- **Learnings loops.** Some skills carry `learnings.md` — dated, append-only notes on what went
  wrong in practice, consolidated periodically.

## Scope

This is a curated public subset of a larger private library. Project-specific, client-scoped,
marketing, startup, and legal skills are not published here, and a few skills that depend on
internal libraries are excluded because they are not usable outside their origin repo.

## License

MIT — see [LICENSE](../../LICENSE).
