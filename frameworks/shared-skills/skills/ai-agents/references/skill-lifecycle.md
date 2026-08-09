# Skill Lifecycle — Create, Validate, Share

Use this when packaging Claude skills for reuse and team distribution.

## Create
- Run the skill init script (if available) to scaffold `SKILL.md`, `scripts/`, `references/`, `assets/` with kebab-case naming and matching frontmatter.
- Write `SKILL.md` in imperative style; keep it lean and link to resources for depth.

## Validate
- Ensure frontmatter name matches directory, and description is specific and activation-friendly.
- Check structure: required `SKILL.md`; optional `references/`, `scripts/`, `assets/`.
- Run validation tooling if present; fix any missing metadata or naming issues.

## Package & Share
- Package as a zip (validation first); include all referenced files.
- Post summary to Slack via automation (Rube/Slack integration): name, description, link, and key resources.
- Keep versions discoverable; update team channels when new skills land or change materially.
