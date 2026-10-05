# Shared Members

Canonical reusable agent definitions for this skill.

Install recurring named specialists into `.claude/agents/` or `.codex/agents/`,
then compose retained delivery and install rosters through
`agents/teams/*/team.yaml`. Bounded `expert-board` panels use generic role briefs
and do not require their former board recipes or member installation.

Rules:

- One member id maps to one canonical agent definition
- `agents/` is the source of truth for shared roles
- Team recipes reference member ids rather than duplicating agent files
- Create a team-specific variant only when workflow, output contract, or tool scope materially differs
- Canonical member ids use the same family-prefix style as the shared skill catalog (for example `software-security-reviewer`, `dev-feature-implementer`, `startup-growth-specialist`)
- Old unprefixed ids still resolve through `data/naming-aliases.json`, but new docs and installs should use the canonical prefixed ids
- Every canonical member declares relevant shared-skill ids in its runtime-specific catalog form. Claude subagents use frontmatter `skills:`. Codex footer text is repository metadata; installers materialize native `[[skills.config]]` without requiring Claude files on the target machine.
- Codex installs at every supported scope materialize installer-owned `.toml` files so native skill blocks can be attached. Managed checksums distinguish unchanged installer artifacts from user-customized agents.
- Those skill ids are catalog references. Runtime discovery comes from repository or user skill folders such as `.agents/skills/` and `$HOME/.agents/skills/`. Codex installs materialize the needed skill links before wiring `[[skills.config]]`; the inline brief remains the fallback when a skill cannot be resolved.

## Lifecycle gotchas

These trip up first-time contributors. Read before adding, renaming, or removing a member.

- **Adding a member is two steps, not one.** Drop the canonical file under `agents/claude/<id>.md` (and optionally a paired `agents/codex/<snake_id>.toml` — Codex filenames are underscore-delimited: `software-security-reviewer.md` pairs with `software_security_reviewer.toml`; 0/141 use the kebab id) **and** reference the id from at least one team recipe under `members:` or `expansion_gate.candidate_specialists:`. Files referenced by no recipe are skipped by bulk deployment even though they exist on disk.
- **Core is automatic; candidates are explicit.** `members:` are the default/core roster and install by default. `candidate_specialists:` are expansion lanes and install only with `--include-candidates`.
- **Renames are not free.** If you rename, update every team recipe that references the id, then run an explicit team operation or confirmed bulk deployment so installer-owned stale artifacts can be pruned. `deploy-preset.sh --member <id>` does not prune.
- **Managed-copy semantics.** Installs materialize native files so runtime-specific configuration can be attached. The installer records checksums and refreshes or removes only unchanged installer-owned artifacts; local modifications are preserved. Redeploy after canonical edits.
- **Opt-in recipes gate their members.** A member listed only in recipes marked `install: opt-in` requires either an explicit `deploy-preset.sh <team>` operation or confirmed bulk deployment with `--confirm-bulk-deploy --include-opt-in`. Add `--include-candidates` when expansion specialists must also be materialized.
- **Installs rewrite reference links; do not invent new `../` hops.** Both the Claude and Codex install paths rewrite `../../skills/universal/agents-subagents/references/<file>.md` in the installed copy to the deployed skill path (`~/.claude/skills/agents-subagents/references/…` or `~/.agents/skills/…`), leaving the canonical file untouched. That is the only escaping-hop shape with a rewrite rule: a member is installed by verbatim copy into an `agents/` directory, so any other `../` link dangles at runtime even though it resolves in the repo. Link a reference with exactly `../../skills/universal/agents-subagents/references/<file>.md`, keep everything else in-file, and expect `validate_catalog_integrity.py` to fail any other `../` hop.
- **Codex members are generated; edit only the Claude file.** `agents/codex/*.toml` is built from `agents/claude/*.md` by `python3 skills/universal/agents-subagents/scripts/generate_codex_agents.py --write`. Text that differs by runtime goes inside `<!-- claude-only -->` … `<!-- /claude-only -->` or `<!-- codex-only` … `-->` line markers in the Claude file (syntax in the generator's docstring). `generate_codex_agents.py --check` fails on any hand edit to a Codex file.
- **Validate before committing.** `python3 skills/universal/agents-subagents/scripts/validate_catalog_integrity.py` checks Claude/Codex parity and team-coverage after any member change. A diff in member counts is the first signal that one platform's source got out of sync.

Run `deploy-preset.sh --list-members` or `ls agents/claude/` for the current full list of canonical members.

Commonly reused members include:

- `software-security-reviewer`
- `software-performance-reviewer`
- `qa-test-reviewer`
- `software-solution-architect`
- `ops-incident-commander`
- `dev-portfolio-mapper`
- `startup-growth-specialist`
- `startup-painpoint-scout`
- `startup-pricing-advisor`
- `marketing-strategist`
- `ai-agent-architect`
- `ai-bot-builder-lead`
- `data-analytics-engineer`
- `software-frontend-lead`
- `software-payments-architect`
- `software-mobile-architect`
