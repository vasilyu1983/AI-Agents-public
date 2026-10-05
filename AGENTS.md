# Repository Guidelines

Instructions for AI coding agents working in this repository.

## Map

- `skills/universal/<name>/` — skills. `SKILL.md` holds the judgment; depth goes in `references/`, runnable code in `scripts/`, data a script reads in `data/`.
- `agents/claude/*.md` — subagent definitions. `agents/codex/*.toml` is generated from them.
- `agents/teams/<id>/team.yaml` — team recipes.
- `agents/workflows/<id>.manifest.json` — workflow sources. `<id>.js` and `<id>.codex-plan.json` are generated.
- `hooks/`, `rules/` — opt-in hooks and language rules.

## Rules

- Never hand-edit a generated file. Edit the source, then regenerate:
  - `python3 skills/universal/agents-subagents/scripts/generate_workflows.py`
  - `python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --write`
  - `python3 skills/universal/agents-subagents/scripts/generate-team-diagrams.py`
  - `python3 skills/universal/agents-subagents/scripts/generate_team_member_matrix.py`
- Validate an edited skill: `python3 skills/universal/agents-skills/scripts/validate_skill.py skills/universal/<name>`.
- Keep volatile facts (current versions, prices, limits) out of skill prose. Give a lookup step instead.
- Never invent a number or a citation. Quote only what you read in the source.
- Never commit secrets, credentials or personal data.
- In a shared working tree, do not run `git stash`, `git reset --hard`, path `git checkout`/`git restore` or `git clean -f`.

## Checks

```bash
python3 skills/universal/agents-subagents/scripts/generate_workflows.py --check
python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --check
node agents/workflows/test-adversarial-review.mjs
python3 hooks/test_git_safety_guard.py
python3 hooks/test_config_guard.py
```
