# Settings Source Precedence And Managed Policy

## Table Of Contents

- [Core Pattern](#core-pattern)
- [Source Layers](#source-layers)
- [Precedence](#precedence)
- [Managed Settings As Base Plus Drop-Ins](#managed-settings-as-base-plus-drop-ins)
- [Plugin-Only Customization Policy](#plugin-only-customization-policy)
- [Source Labels Matter](#source-labels-matter)
- [Design Rules To Reuse](#design-rules-to-reuse)

## Core Pattern

Model runtime settings as layered sources with explicit precedence.

From the April 2026 `claude_code` snapshot:

- `utils/settings/constants.ts` defines the canonical source list
- `utils/settings/settings.ts` loads and merges sources
- managed settings support a base file plus sorted drop-ins
- policy can restrict entire customization surfaces to admin-trusted sources only

## Source Layers

The runtime uses these sources:

- user settings
- project settings
- local gitignored settings
- CLI flag settings
- managed policy settings

Important rule from the source:

- managed policy and flag settings are always included
- editable-source restrictions do not remove those layers

This is a strong pattern for coding-agent CLIs because org policy and explicit CLI overrides should not disappear behind user preferences.

## Precedence

`SETTING_SOURCES` documents that later sources override earlier ones.

Keep this model explicit:

- user
- project
- local
- flag
- policy

If the target runtime needs a different order, document it once and reuse the same ordering everywhere:

- file loading
- UI labels
- conflict explanations
- settings export

This `user → project → local → flag → policy` list is deliberately the same relative order as Claude Code's verified precedence (`~/.claude/settings.json` < `.claude/settings.json` < `.claude/settings.local.json` < CLI flags < managed policy — see [`settings-precedence-table.md`](settings-precedence-table.md)). Local outranking project is the detail auditors get backwards most often; do not "simplify" it to user/project/local alphabetical or size order without checking the target runtime's own docs.

## Managed Settings As Base Plus Drop-Ins

`loadManagedFileSettings()` loads:

- one base managed settings file
- zero or more alphabetically sorted drop-ins

Pattern to reuse:

- one admin-owned base file for defaults
- drop-in fragments for independent teams or policies
- deterministic alphabetical merge order

This avoids one giant central file and still keeps precedence predictable.

## Plugin-Only Customization Policy

`pluginOnlyPolicy.ts` models `strictPluginOnlyCustomization`.

Reusable pattern:

- some customization surfaces can be locked to admin-trusted sources only
- trusted sources can include:
  - managed policy
  - built-ins
  - plugins gated by separate marketplace or trust controls
- user, project, local, and flag sources are blocked for those surfaces

This is useful for:

- commands
- skills
- hooks
- MCP configuration

when organizations want controlled extensibility without fully disabling plugins.

## Source Labels Matter

The runtime keeps distinct source-display helpers:

- lowercase inline labels
- capitalized UI labels
- short display names

Copy this idea.

Users need to understand whether a rule came from:

- user settings
- project settings
- current session
- CLI arguments
- enterprise policy

without reading raw config files.

## Design Rules To Reuse

- Keep a single canonical ordered list of settings sources.
- Treat policy and CLI overlays as special sources, not just more files.
- Use managed base files plus drop-ins for admin control.
- Allow policy to lock specific customization surfaces to trusted sources only.
- Make source origin visible in UI and diagnostics.
