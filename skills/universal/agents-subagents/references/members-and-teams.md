---
description: Canonical library structure, member-vs-variant rule, and skill linkage rule.
last_verified: 2026-08-27
status: stable
---

# Shared Members and Team Recipes

## Table of Contents

- [Canonical Library Structure](#canonical-library-structure)
- [Member vs Variant Rule](#member-vs-variant-rule)
- [Skill Linkage Rule](#skill-linkage-rule)

The canonical library separates reusable members from team composition.

## Canonical Library Structure

- `agents/` contains one canonical definition per reusable role.
- `agents/teams/*/team.yaml` composes those members into repository team recipes. These YAML files are not native Claude or Codex runtime manifests.
- `scripts/deploy-preset.sh` installs the referenced native agent definitions and stores recipe metadata for launchers, so multiple recipes can coexist without duplicating agent files in `agents/`.
- [team-coverage.md](team-coverage.md) records which domains are team-backed, member-only, or intentionally direct-use only.

## Member vs Variant Rule

Use a shared member when a role is reusable across teams with the same workflow and output contract. Create a variant only when a role genuinely changes behavior, scope, or deliverable.

Treat `agents/` as the single source of truth. The legacy `assets/presets/` directory was removed; old preset-style names still resolve through `data/naming-aliases.json`.

## Skill Linkage Rule

- Canonical skill linkage is defined by the same skill ids in each runtime member. Claude members carry that mapping in frontmatter `skills:`.
- Codex project, repo, and user installs may include `[[skills.config]]` entries for referenced, discoverable skill folders. These entries are per-skill enablement overrides in that custom agent's configuration layer; they do not eagerly inject the full `SKILL.md` or bypass normal skill discovery and activation. Footer text remains catalog metadata and an inline fallback.
- Those ids must resolve to the shared-skills catalog under `skills/`.
- At runtime, the skill content should come from `.agents/skills/` locations such as `$REPO_ROOT/.agents/skills/` and `$HOME/.agents/skills/`, not from this repo's `assets/` directory.
