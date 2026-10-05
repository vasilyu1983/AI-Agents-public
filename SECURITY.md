# Security

## Reporting

Report a vulnerability through GitHub's private vulnerability reporting on this repository ("Security" tab, "Report a vulnerability"). Do not open a public issue for it.

## What runs on your machine

- **Skills** are instructions. Some ship scripts in `scripts/`; an agent may run them. Read a script before you allow it.
- **Workflows** launch several agents. Each one states its scope and its stop points in `meta.description`.
- **Hooks** are not installed by the plugin. You copy the entries you want into your own settings.
- `scripts/distribution/sync-skills.sh` creates symlinks only and never overwrites a real file or a foreign symlink.

## Third-party skills

Review any skill from another source before you install it: read `SKILL.md` and every script it ships.
