# Claude Code Agent Runtime Patterns

Curated implementation notes extracted from the local `claude_code` source snapshot that seeded this skill. Use this file when you need the practical rules behind Claude Code agent definitions rather than just the public-facing authoring shape.

## Table of Contents

- [Agent file locations and naming](#agent-file-locations-and-naming)
- [Persisted frontmatter shape](#persisted-frontmatter-shape)
- [Validation rules that matter in practice](#validation-rules-that-matter-in-practice)
- [Persistence and edit behavior](#persistence-and-edit-behavior)
- [Design implications for this skill](#design-implications-for-this-skill)
- [Source anchors](#source-anchors)

## Agent file locations and naming

- Project agents live under `.claude/agents/`.
- User agents live under the Claude config home `agents/` directory.
- New agent files are named from `agentType`, but existing agents preserve the original filename when editing.
- Built-in and plugin agents are not written back to the filesystem like normal markdown agents.

## Persisted frontmatter shape

The local implementation formats agent files as markdown with YAML frontmatter plus a markdown body:

```yaml
---
name: my-agent
description: "When to use this agent"
tools: Read, Grep, Glob
model: inherit
effort: medium
color: blue
memory: project
---

System prompt body...
```

Observed implementation details:
- `description` is the persisted trigger string.
- `tools` is omitted entirely when the agent has full tool access.
- the formatter escapes backslashes, double quotes, and newline sequences inside `description`.
- `model`, `effort`, `color`, and `memory` are optional and serialized only when set.

## Validation rules that matter in practice

The local validator applies several constraints before an agent is accepted:

- `agentType` must start and end with an alphanumeric character.
- internal characters may be letters, numbers, or hyphens.
- minimum length is 3; maximum length is 50.
- duplicate agent types are rejected across different sources.
- missing `description` is an error.
- `description` under 10 characters triggers a warning; over 5000 triggers a warning.
- missing system prompt is an error.
- system prompt under 20 characters is rejected; over 10,000 triggers a warning.
- undefined tools means full tool access; empty tool arrays are allowed but warned because the agent becomes very constrained.
- tool names are resolved against the available tool registry and invalid entries are rejected.

## Persistence and edit behavior

- Project and local agents are written with explicit directory creation before save.
- Saves can be strict (`wx`) to prevent accidental overwrite on create.
- Updates reuse the actual file path rather than recomputing from `agentType`.
- Deletes are blocked for built-in agents and ignore missing-file errors for normal agents.
- The runtime keeps a distinction between source types such as user settings, project settings, policy settings, built-in, plugin, and CLI-provided agents.

## Design implications for this skill

- Treat Claude Code agent definitions as a persisted interface, not just a prompt template.
- Keep agent names short and stable because file names, UI menus, and duplicate detection all key off them.
- Keep the trigger description specific and concise: it drives routing and is also stored verbatim in frontmatter.
- Prefer explicit tool scoping because “all tools” is the default when `tools` is absent.
- When porting between platforms, separate the stable task contract from Claude-specific frontmatter fields.

## Source anchors

- `components/agents/types.ts`
- `components/agents/validateAgent.ts`
- `components/agents/agentFileUtils.ts`
