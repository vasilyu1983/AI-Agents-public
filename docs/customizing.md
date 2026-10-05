# Customizing

This page shows how to write a skill, a subagent, a team or a workflow, and which checks to run. Work in a clone (install path B), so your changes take effect at once.

- [Write a skill](#write-a-skill)
- [Write a subagent](#write-a-subagent)
- [Write a team](#write-a-team)
- [Write a workflow](#write-a-workflow)
- [Add a rule](#add-a-rule)
- [Checks before you commit](#checks-before-you-commit)

## Write a skill

1. **Check that no skill covers it.** Search the [catalog](reference/catalog.md#skills). Extend an existing skill if one is close.
2. **Create the folder.** The folder name is the skill name: lowercase letters, digits and hyphens, at most 64 characters, no `--`.

   ```text
   skills/universal/my-skill/
   └── SKILL.md
   ```

3. **Write the front matter.**

   ```markdown
   ---
   name: my-skill
   description: "Reviews Terraform plans for destructive changes. Use when a plan deletes or replaces a stateful resource."
   ---
   ```

   - `name` must match the folder name.
   - Write `description` in the third person: "Reviews ...", not "Review ..." or "Use this to ...".
   - Put the key use case first. The runtime matches tasks against this text.
   - The validator rejects a description over 1024 characters and warns on a long one.

4. **Write the body.** Keep only what a strong model would get wrong without it.
   - Give one default and the condition for leaving it, not a menu of options.
   - Build the "Gotchas" section from real failures.
   - Give exact commands only for fragile steps.
   - Do not write current versions, prices or limits. Write a step that looks them up.
   - Keep `SKILL.md` under 500 lines. Move depth to `references/` and link each reference from the step that needs it, with the condition: "Read `references/state-moves.md` when the plan moves a resource."

5. **Validate.**

   ```bash
   python3 skills/universal/agents-skills/scripts/validate_skill.py skills/universal/my-skill
   ```

   It prints `## Errors` and `## Warnings`. Fix every error.

6. **Link it** (clone install): `bash scripts/distribution/sync-skills.sh`. Start a new session and give a task that should load the skill.

The `agents-skills` skill holds the full authoring guide. Ask the agent to use it while you write.

## Write a subagent

1. Copy the template:

   ```bash
   cp agents/templates/member-claude.md.template agents/claude/my-reviewer.md
   ```

2. Fill the front matter. The description has three parts: what it does, when to use it, and what it produces and does not do.
3. Give it the fewest tools that work. A reviewer needs `Read`, `Grep`, `Glob`, and maybe `Bash`. Only a writer needs `Edit` and `Write`.
4. List preloaded skills under `skills:`, or write `skills: []`.
5. Generate the Codex version and check it:

   ```bash
   python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --write
   python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --check
   ```

   `--write` writes changed files and never deletes old ones. `--diff my-reviewer` shows the output for one agent.

6. Install it: `deploy-preset.sh my-reviewer --member --platform claude --user`.

Never edit `agents/codex/*.toml` by hand. The next `--write` replaces your edit, and `--check` fails on it.

## Write a team

1. Copy `agents/templates/team.yaml.template` to `agents/teams/<id>/team.yaml`.
2. Fill `members`, `required_context`, `concurrency_mode`, `synthesis_owner`, `owned_files` and `do_not_touch`. Every member must exist in `agents/claude/`.
3. Regenerate the team views and check them:

   ```bash
   python3 skills/universal/agents-subagents/scripts/generate-team-diagrams.py
   python3 skills/universal/agents-subagents/scripts/generate_team_member_matrix.py
   python3 skills/universal/agents-subagents/scripts/generate-team-diagrams.py --check
   python3 skills/universal/agents-subagents/scripts/generate_team_member_matrix.py --check
   ```

4. Install it: `deploy-preset.sh <id> --platform claude --user`.

## Write a workflow

1. Copy the manifest of the closest workflow in `agents/workflows/` to `<id>.manifest.json`.
2. Set `engine`, `codex: "parent-led"`, `description`, `whenToUse` and `phases`. Each phase title must match a `phase()` call in the engine exactly.
3. Reuse a `review` or `loop` block from another manifest with `extends`.
4. Generate and check:

   ```bash
   python3 skills/universal/agents-subagents/scripts/generate_workflows.py
   python3 skills/universal/agents-subagents/scripts/generate_workflows.py --check
   ```

5. Link it: `bash scripts/distribution/sync-skills.sh claude`. Then run `/<id>` on a small target.

Engine behaviour lives in `skills/universal/agents-subagents/scripts/<engine>_runtime.js`. Change it there, never in a generated `<id>.js`. [Workflows, section 8](workflows.md#8-change-or-add-a-workflow) has more detail.

## Add a rule

1. Create `rules/<domain>/<topic>.md`.
2. Start it with front matter that lists the files it applies to:

   ```markdown
   ---
   paths:
     - "**/*.tf"
   ---
   ```

3. Keep the body short: 12 lines or fewer.
4. End with `Why and procedure: <path#anchor>`, pointing to the skill that explains the rule.

## Checks before you commit

| You changed | Run |
|---|---|
| A skill | `python3 skills/universal/agents-skills/scripts/validate_skill.py skills/universal/<name>` |
| A subagent | `python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --check` |
| A team | Both team generators with `--check` |
| A workflow | `generate_workflows.py --check`, then `node agents/workflows/test-adversarial-review.mjs` |
| A hook | `python3 hooks/test_git_safety_guard.py` and `python3 hooks/test_config_guard.py` |
| The sync script | `python3 scripts/distribution/test_sync_skills.py` |
