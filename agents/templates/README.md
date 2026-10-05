# Templates

Scaffolds for new agent members, teams, and specialized harnesses in the `agents-subagents` skill.

## Members and Teams

Use these when adding a new agent member or team to `agents/` or `agents/teams/`.

| Template | Use for | Output path |
|---|---|---|
| [`member-claude.md.template`](member-claude.md.template) | New Claude Code agent definition (DEEP pattern) | `agents/claude/<kebab-name>.md` |
| [`member-codex.toml.template`](member-codex.toml.template) | Codex agent definition with the same role contract | `agents/codex/<snake_name>.toml` |
| [`team.yaml.template`](team.yaml.template) | New team definition (members + concurrency + optional debate) | `agents/teams/<team-name>/team.yaml` |

### Source-of-truth rule

Skill linking is runtime-independent: Claude uses the `.md` frontmatter `skills:` block, and Codex carries the same skill ids in its TOML footer. The deploy script parses the target runtime's member metadata and appends `[[skills.config]]` entries to the Codex `.toml` at deploy time.

- Keep the Claude and Codex role briefs identical, but make each file self-contained for its runtime.
- Curate skill ids carefully — 2-5 slugs that match the agent's actual reach.
- The Codex closing "Teammate note" line names the same skill slugs as the Claude frontmatter, without depending on Claude files at install time.
- Do not rely on one runtime's agent file being present when installing the other runtime.

### Project-isolation rule

`project-*` members may only link to `project-<same-family>-*` skills. Never cross-link with domain skills (`software-*`, `marketing-*`, `qa-*`, etc.). See repo-root `CLAUDE.md` for the canonical rule.

### Canonical exemplars

When in doubt, copy structure from these in-repo examples rather than rewriting from scratch:

- [`agents/claude/dev-feature-implementer.md`](../claude/dev-feature-implementer.md) — DEEP claude exemplar with `permissionMode: acceptEdits` + `isolation: worktree` (implementer-class).
- [`agents/claude/product-strategist.md`](../claude/product-strategist.md) — Inline Brief richness exemplar (sub-headers + multi-scenario Output Contract).
- [`agents/codex/qa_test_reviewer.toml`](../codex/qa_test_reviewer.toml) — Codex Teammate-note pattern.
- [`agents/teams/software-code-review-board/team.yaml`](../teams/software-code-review-board/team.yaml) — Retained team with debate block enabled.
- [`agents/workflows/expert-board.manifest.json`](../workflows/expert-board.manifest.json) — Canonical policy source for generic review-board modes.

### Authoring workflow

1. Copy the relevant template(s) into the target path with the final filename.
2. Fill the runtime member file with a self-contained role brief — the Inline Brief is where the agent's domain expertise lives, not the skills it links to.
3. Keep the Claude body and Codex `developer_instructions` identical. Put the same skill ids in Claude `skills:` and in the Codex footer.
4. (Teams only) Confirm every member listed has both a Claude `.md` and Codex `.toml` on disk.
5. Run the verification suite documented in `references/runtime-smoke-tests.md` (frontmatter parity, skill-slug resolution, pair completeness).

For deeper guidance on member design, sub-header patterns, and team selection, see [`references/members-and-teams.md`](../../skills/universal/agents-subagents/references/members-and-teams.md).

## Specialized harness templates

These are not blank scaffolds — they are functional harness prompts loaded by the runtime. Edit only with intent.

- `debate-orchestrator.md` — orchestrator prompt for debate-mode teams.
- `debate-synthesizer.md` — synthesizer that resolves debate perspectives into a single artifact.
- `perspective-agent.md` — reusable perspective-lens scaffold for debate participants.
- `browser-verifier.md` — minimal harness for agents that drive a browser session.
- `growth/` — growth-team harness fragments.

## Method libraries

Three indexed libraries of overlays you compose at team launch:

- [`debate-methods/`](debate-methods/) — 10 methods that restructure the team's discussion (Courtroom, Pre-Mortem, Six Hats, Dialectical, Steel-Manning, etc.).
- [`decision-masks/`](decision-masks/) — 7 cognitive frames that decorate a single agent's brief (Inversion, First Principles, Regret-Min, Second-Order, Anchoring Reset, Base-Rate Reset, Constitutional self-critique).
- [`game-theory/`](../../skills/universal/foundations-game-theory/assets/templates/game-theory/) and [`team-theory/`](../../skills/universal/foundations-team-theory/assets/templates/team-theory/) — 22 mechanisms (10 incentive mechanisms in foundations-game-theory; the 12 shared-payoff aggregation and credit ones in foundations-team-theory, with stubs at the old paths) for coordination, synthesis, contribution tracking, act/escalate gates, attested delegation, and coalition routing (Auction routing, Shapley, Reasoning-Tree Audit, Credibility Scoring, Generative Social Choice, Meta-Debate Routing, Online Shapley Prompt Evolution, Beyond Majority Voting, Radial Consensus Score, Conformal Social Choice, Attested Delegation Contracts, Coalition Formation Routing, etc.).

For cross-folder stacks mapping decision archetypes (regulatory go/no-go, Series A, architecture RFC, pricing, migration, etc.) to a recommended debate method + masks + game-theory mechanism stack, see [`composition-recipes.md`](composition-recipes.md).
