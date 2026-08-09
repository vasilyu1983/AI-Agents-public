# Claude Code Skill and Plugin Loading

Curated implementation notes extracted from the local `claude_code` source snapshot. Use this file when you need the runtime behavior behind skill discovery, frontmatter parsing, and built-in plugin-backed skills.

## Table of Contents

- [Skill discovery paths](#skill-discovery-paths)
- [Frontmatter fields the loader cares about](#frontmatter-fields-the-loader-cares-about)
- [Prompt-budget behavior](#prompt-budget-behavior)
- [Built-in plugin skill behavior](#built-in-plugin-skill-behavior)
- [Design implications for this skill family](#design-implications-for-this-skill-family)
- [Source anchors](#source-anchors)

## Skill discovery paths

The runtime resolves skill directories by source:

- project settings: `.claude/skills`
- user settings: Claude config home `skills`
- policy settings: managed `.claude/skills`
- plugin source: plugin-provided skill bundles

The loader also deduplicates files by canonical real path so the same skill does not appear twice through overlapping directories or symlinks.

## Frontmatter fields the loader cares about

The skill loader extracts more than `name` and `description`. Relevant parsed fields include:

- `description`
- `allowed-tools`
- `argument-hint`
- `arguments`
- `when_to_use`
- `version`
- `model`
- `disable-model-invocation`
- `user-invocable`
- `hooks`
- `context`
- `agent`
- `effort`
- `shell`
- `paths`

Notable behavior:
- `displayName` comes from frontmatter `name` when present.
- `description` falls back to markdown extraction if frontmatter does not provide one.
- `context: fork` is treated specially as an execution-context signal. When set, the runtime spawns a subagent using the skill body as the task prompt instead of injecting it into the current conversation. The `agent` field selects which subagent type executes the forked skill (e.g., `Explore`, `general-purpose`). This is the inverse of the subagent `skills:` preloading pattern — here the skill controls the prompt and the subagent is the executor.
- invalid `effort` values are logged and ignored.
- hooks are schema-validated before use.

## Prompt-budget behavior

The runtime estimates skill frontmatter token cost from only:
- skill name
- description
- when-to-use text

That matches the intended progressive-disclosure model: routing metadata stays cheap, while full content is loaded only on invocation.

## Built-in plugin skill behavior

Built-in plugins differ from normal bundled skills:

- they are user-toggleable through plugin settings
- they can provide multiple component types such as skills, hooks, and MCP servers
- they are registered in a built-in plugin registry

When exposed as commands, built-in plugin skills still use `source: bundled` so they remain visible to the skill system, analytics, and prompt-truncation exemptions. The user-toggleable plugin state is tracked separately on the loaded plugin record.

## Design implications for this skill family

- Keep trigger metadata compact because the loader budgets around routing text, not full skill bodies.
- Use references and assets for depth instead of bloating `SKILL.md`.
- Treat plugin-provided skills and filesystem skills as distinct distribution paths even when they surface similarly in the UI.
- Avoid assuming every loader-visible field is portable across platforms; several are Claude-specific runtime extensions.

## Source anchors

- `skills/loadSkillsDir.ts`
- `plugins/builtinPlugins.ts`
