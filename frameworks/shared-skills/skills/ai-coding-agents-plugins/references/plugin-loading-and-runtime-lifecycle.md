# Plugin Loading And Runtime Lifecycle

## Table Of Contents

- [Design Goal](#design-goal)
- [Discovery Sources](#discovery-sources)
- [Activation Pipeline](#activation-pipeline)
- [Component Reload Rules](#component-reload-rules)
- [Hot Reload And Session State](#hot-reload-and-session-state)
- [Failure Handling](#failure-handling)

## Design Goal

A coding-agent plugin system should not just "scan a folder." It should provide a repeatable lifecycle:

1. discover candidate plugins
2. validate manifests and paths
3. load enabled plugins into a normalized registry
4. rebuild component registries
5. reconnect or refresh side-effectful integrations
6. report errors without corrupting the session

That is the pattern visible in `claude_code`, where plugin loading is tied to cache invalidation, command and agent refresh, hook registration, and MCP diffing instead of being treated as a one-off file read.

## Discovery Sources

`pluginLoader.ts` explicitly describes multiple plugin discovery sources:

- installed or marketplace-backed plugins
- session-only plugins, such as inline or `--plugin-dir` sources
- built-in plugins managed through a separate built-in registry

For new coding-agent CLIs, encode this as host-owned precedence:

- core runtime capabilities
- built-in plugins that ship with the product
- installed plugins from user settings or marketplaces
- session-local overlays or inline plugins

The important part is not the exact source list. The important part is that each source class should be tracked separately so the runtime can explain where a capability came from and how it can be reloaded or disabled.

## Activation Pipeline

The `claude_code` pattern is modular:

- `pluginLoader.ts` discovers and normalizes loaded plugins
- capability-specific loaders rebuild commands, agents, hooks, output styles, or MCP integrations
- `refreshActivePlugins(...)` clears plugin caches and refreshes app state
- the CLI then updates mutable command and agent registries and diffs MCP server state

That suggests a good implementation model:

1. load manifests and enablement state
2. build a normalized list of enabled plugins
3. call dedicated loaders for each capability family
4. rebuild runtime registries only after plugin state is internally consistent
5. apply transport or connection diffs after registry rebuild

Do not let every component loader re-discover plugins independently from disk with its own policy rules. Centralize plugin selection first, then let specialized loaders consume that normalized state.

## Component Reload Rules

The source shows that not every capability reloads the same way:

- commands and agents can be rebuilt into fresh registries
- hooks require atomic clear-and-register behavior
- MCP servers may need a reconnect or config diff
- output styles can refresh their caches independently

This is the right default model:

- **pure metadata capabilities** can usually be rebuilt in memory
- **callback registries** need atomic swap behavior
- **transport-backed capabilities** need explicit reconnect or diff logic
- **long-lived external processes** may require staged teardown and restart

Do not market a plugin system as "hot reloadable" unless each capability family has a safe reload path.

## Hot Reload And Session State

Two `claude_code` patterns are worth copying:

- the runtime keeps mutable current command and agent registries so a live session can reflect plugin changes
- reload returns refreshed commands, agents, plugin list, MCP server status, and error count instead of silently mutating state

That is a strong contract for coding-agent CLIs with REPLs or SDK sessions:

- reload should be an explicit control action
- reload should return a structured summary
- caches must be cleared before reconstruction
- SDK- or flag-injected components should survive plugin reload if they live outside disk-backed plugin state

Treat reload as a state transition, not an implementation detail.

## Failure Handling

The source consistently uses best-effort aggregation:

- collect load errors per plugin
- let one failing capability family log errors without discarding successful state changes in others
- return success for the reload action when the registry swap succeeded, even if some readouts fail afterward

That yields better operational behavior for coding-agent hosts:

- manifest validation errors should identify the plugin and field
- registry rebuild errors should not leave partial duplicate registrations behind
- the user should be able to see which plugins are enabled, failed, or blocked
- disabling or uninstalling a plugin should immediately stop future behavior from that plugin, even before the next full reload where possible

The host should own error collection and reporting. Plugins should never decide what counts as a recoverable partial failure.
