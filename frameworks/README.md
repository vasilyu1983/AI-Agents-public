# Frameworks

Reusable assets for AI coding agents — Claude Code, Codex CLI, and any runtime implementing the
[Agent Skills specification](https://agentskills.io/specification).

## Contents

Everything here lives in [`shared-skills/`](shared-skills/) — 140 agent skills, the main
body of work. See its [README](shared-skills/README.md) for the family breakdown and
install steps.

## Start Here

Install one skill:

```bash
ln -s "$PWD/shared-skills/skills/<skill-name>" ~/.claude/skills/<skill-name>
```

## What a Skill Is

A folder an agent loads on demand, rather than instructions crammed into a system prompt:

```text
<skill-name>/
├── SKILL.md      # Entry point — frontmatter + routing. Kept small.
├── references/   # Depth, loaded only when the task needs it
├── scripts/      # Deterministic helpers — no model call needed
├── assets/       # Templates and output contracts
└── data/         # sources.json and curated data
```

The split is the point. `SKILL.md` stays cheap enough to keep in hot context; `references/`
hold the detail and cost nothing until read. A skill that inlines everything defeats this.

## Coverage

Strongest areas, by volume and by how hard the material is to find elsewhere:

- **Coding-agent runtime internals** (13 skills) — sandboxing, permission models, session
  lifecycle, tool and provider runtimes, terminal UX. Design notes for building agent CLIs.
- **Systems-theory foundations** (16 skills) — queueing, control, information, game, decision,
  and reliability theory applied to real system design decisions.
- **AI/ML engineering** (21 skills) — retrieval, evals, pretraining through inference.
- **Software and QA** (51 skills) — implementation and verification across web, mobile, backend.

## License

MIT — see [LICENSE](../LICENSE).
