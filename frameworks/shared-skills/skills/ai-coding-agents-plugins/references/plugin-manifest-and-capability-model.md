# Plugin Manifest And Capability Model

## Table Of Contents

- [Design Goal](#design-goal)
- [Package Shape](#package-shape)
- [Identity And Source](#identity-and-source)
- [Capability Families](#capability-families)
- [Namespacing And Collision Control](#namespacing-and-collision-control)
- [Manifest Defaults Worth Copying](#manifest-defaults-worth-copying)

## Design Goal

For coding-agent runtimes, the plugin manifest should be the host's typed declaration of what a plugin may contribute. Do not force the runtime to execute arbitrary plugin code just to discover what the plugin is.

The `claude_code` source points to a stable pattern:

- plugin metadata lives in `plugin.json`
- standard directories provide conventional component homes
- the host still validates and normalizes each capability type before registration
- built-in plugins and installed plugins eventually become the same loaded-plugin shape, even if their sources differ

That is the right model to copy for coding-agent CLIs.

## Package Shape

The `pluginLoader.ts` header documents a pragmatic package shape:

```text
my-plugin/
├── plugin.json
├── commands/
├── agents/
├── skills/
├── hooks/
└── output-styles/
```

The schema layer adds a useful rule: keep common directories as the default discovery path, but allow the manifest to supplement them with explicit relative paths. In `schemas.ts`, commands, agents, skills, output styles, hooks, and MCP servers can all be declared directly in the manifest, not just inferred from directory presence.

Use that as the host contract:

- conventional directories for common cases
- manifest-declared additional paths for non-standard layouts
- explicit manifest validation before activation

## Identity And Source

The codebase distinguishes plugin identity from plugin path:

- marketplace or installed plugins use a `name@marketplace` style source identifier
- session-local plugins use an inline source sentinel
- built-ins use `name@builtin`

That separation matters because a coding-agent runtime usually needs all of the following:

- a stable logical plugin ID
- a user-facing display name
- a physical path or repository origin
- an enablement state
- a trust or source class

Do not make filesystem location the primary identifier. Use a stable plugin ID, then attach path, marketplace, or built-in status as metadata.

## Capability Families

The `claude_code` plugin subsystem effectively exposes these capability families:

- commands
- skills
- agents
- hooks
- MCP servers
- output styles

That is a strong default list for coding-agent runtimes because it separates:

- prompt-driven entrypoints
- reusable prompt packs
- delegated worker definitions
- lifecycle interception
- external tool transports
- rendering or response-mode customization

Keep these capability families typed in the host model. Avoid a generic `components: any[]` shape unless the runtime has a strict second-layer schema per capability type.

**The family list keeps growing — plan for it.** As of mid-2026, the strongest production plugin systems (Claude Code, and convergently GitHub Copilot CLI) have added at least four more typed families beyond the original six: LSP servers (real-time diagnostics and code navigation, distinct from MCP because they speak a different protocol to a locally installed binary), background monitors (long-lived shell watchers that push notifications rather than answer tool calls), themes (pure presentation, zero tool-call surface), and channels (message-injection bindings on top of an existing MCP server, e.g. Telegram/Slack/Discord). The expert move is to design the capability-family enum as open-ended from day one — a `family` discriminator plus a per-family registration handler — so adding LSP or monitors later is a new case, not a schema migration. Runtimes that hardcoded "plugins have commands, skills, agents, hooks, MCP" paid for it when LSP and monitors arrived.

A second convergence worth designing for explicitly: Claude Code's manifest treats `experimental.themes` and `experimental.monitors` as a distinct, unstable sub-namespace inside the same manifest, with the runtime warning (not erroring) when authors declare them at the top level instead. That is a reusable pattern for any host adding a new capability family — ship it nested under an `experimental` key first, promote it to top-level once the schema stabilizes, and keep both spellings valid with a deprecation warning during the transition instead of a breaking change.

## Namespacing And Collision Control

The `claude_code` loaders do not trust plugin content to remain globally unique. They namespace plugin-provided components in host code:

- commands are prefixed with the plugin name and nested namespace path
- agents are prefixed with the plugin name and namespace path
- output styles are prefixed with `pluginName:styleName`

That pattern is essential for coding-agent CLIs because slash commands, agent names, and style IDs are all user-visible surfaces with collision risk.

Copy these rules:

- the host owns final public names
- names should be deterministic from plugin name plus relative component path
- plugin authors can influence local names, but not bypass host namespacing
- duplicate-path and duplicate-name checks should happen before registration

## Manifest Defaults Worth Copying

From the schema and loader patterns, these defaults are worth preserving:

- keep metadata declarative: name, version, description, homepage, repository, license, keywords
- model dependencies explicitly instead of requiring plugins to probe each other
- reserve sentinel source names such as `inline` and `builtin`
- validate relative paths and refuse path traversal
- allow manifest-level extension of default directories instead of replacing them
- keep manifest parsing lenient at runtime if needed, but provide a stricter validator for authors

For a new coding-agent runtime, a good manifest baseline is:

- `id`
- `version`
- `display_name`
- `description`
- `capabilities`
- `dependencies`
- `default_enabled`
- `trust_level`
- optional capability-specific path fields

The host should then compile that into a normalized loaded-plugin object before any commands, agents, hooks, or MCP servers are made visible.

**Ignore-unknown-fields is a distribution feature, not laziness.** Claude Code's manifest parser silently ignores unrecognized top-level keys at load time (a typed-field-mismatch still fails, e.g. `keywords` as a string instead of an array). That single choice lets one `plugin.json` double as an npm `package.json`, a VS Code/Cursor extension manifest, or an MCPB/DXT bundle manifest, which materially lowers the cost of supporting a new coding-agent runtime — authors do not have to fork their manifest per host. Pair it with a separate strict-mode author tool (`claude plugin validate --strict`) that turns unknown-field and near-miss-field-name warnings into errors during CI, so typos are caught before publish without punishing every runtime load with pedantic parsing. Copy both halves: lenient runtime, strict authoring tool — not just one.
