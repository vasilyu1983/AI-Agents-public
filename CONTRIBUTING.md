# Contributing

Thank you for helping. This repository is the public edition of a larger private library, so read "How changes land" before you start a large change.

## How changes land

- Issues and small pull requests are welcome: a fix to a skill, a broken link, a wrong command, a failing check.
- The public tree is rebuilt from the private library. An accepted pull request is applied there and comes back in the next build. Your change can therefore appear in a later commit, with your credit in the message.
- For a new skill, subagent or workflow, open an issue first and describe the use case.

## Report a problem

Give:

1. What you ran: the prompt, `/<workflow>` and its arguments, or the command.
2. What you expected.
3. What happened, with the exact error text.
4. The runtime (Claude Code or Codex) and the install path (plugin or clone).

Report a security problem privately: see [SECURITY.md](SECURITY.md).

## Make a change

1. Fork the repository and create a branch.
2. Make the change. [docs/customizing.md](docs/customizing.md) explains how to write a skill, subagent, team, workflow or rule.
3. Run the checks for what you changed (table below).
4. Open a pull request. Say what changed, why, and which checks you ran.

| You changed | Run |
|---|---|
| A skill | `python3 skills/universal/agents-skills/scripts/validate_skill.py skills/universal/<name>` |
| A subagent | `python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --check` |
| A team | `generate-team-diagrams.py --check` and `generate_team_member_matrix.py --check` |
| A workflow | `generate_workflows.py --check` and `node agents/workflows/test-adversarial-review.mjs` |
| A hook | `python3 hooks/test_git_safety_guard.py` and `python3 hooks/test_config_guard.py` |

## Rules for content

- **No secrets or personal data.** No keys, tokens, passwords, real customer data or real personal details, even in examples. Use `example.com` and clearly fake values.
- **No invented facts.** Cite only what you read in the source. A number needs a source; a claim of improvement needs a comparison.
- **No volatile data in prose.** Do not write current versions, prices or limits into a skill. Write a step that looks them up.
- **Generated files stay generated.** Edit the source and run the generator. See [docs/concepts.md](docs/concepts.md#generated-files).
- **Small diffs.** Change only what the fix needs.

## Commit messages

Use a short, imperative subject: "Fix the branch target in adversarial-review docs".
