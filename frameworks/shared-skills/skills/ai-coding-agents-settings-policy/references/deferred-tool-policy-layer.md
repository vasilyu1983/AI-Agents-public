# Deferred Tool Policy Layer

ToolSearch is the runtime mechanism through which a model discovers and loads deferred tools. Whether a tool is deferred — and whether the model is allowed to invoke ToolSearch at all — is governed by the settings layer, not by the tool itself.

## Table of Contents

- [What "deferred" means](#what-deferred-means)
- [Settings that govern deferral](#settings-that-govern-deferral)
- [How the settings layer gates ToolSearch](#how-the-settings-layer-gates-toolsearch)
- [Policy decision flow](#policy-decision-flow)
- [Interaction with the tool registry](#interaction-with-the-tool-registry)
- [Example: managed policy restricts ToolSearch to MCP tools only](#example-managed-policy-restricts-toolsearch-to-mcp-tools-only)
- [Example: fully open configuration (development)](#example-fully-open-configuration-development)
- [What ToolSearch does NOT control](#what-toolsearch-does-not-control)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## What "deferred" means

A deferred tool is not visible to the model on turn one. Its schema is withheld from the tool list sent with the initial system prompt. To use it, the model must first call `ToolSearch` with a query that matches the tool's description; the runtime then loads the full schema and makes the tool callable.

This has two effects:

1. **Prompt-cache economics**: a smaller up-front tool list means a more stable prompt-cache prefix. Adding or removing deferred tools does not invalidate the cache for always-loaded tools.
2. **Policy gating**: the ability to trigger deferral, and the ability to call ToolSearch, can be controlled by settings.

## Settings that govern deferral

| Setting key | Type | Default | Description |
|-------------|------|---------|-------------|
| `toolsearch_enabled` | boolean | `true` | Whether the model can call ToolSearch at all. When `false`, deferred tools are invisible for the session. |
| `toolsearch_scope` | enum | `"all"` | Which tool categories can be discovered via ToolSearch. Values: `"all"`, `"mcp_only"`, `"builtins_only"`, `"none"`. |
| `defer_by_default` | boolean | `false` | Whether unrecognized or late-registered tools are deferred automatically unless marked `alwaysLoad`. |
| `always_load_overrides` | list[string] | `[]` | Tool names that must appear on turn one regardless of their `shouldDefer` flag. |
| `toolsearch_min_trust_class` | string | `"user"` | Minimum trust class required to enable ToolSearch. See [`plugin-only-restriction-recipes.md`](plugin-only-restriction-recipes.md). |

## How the settings layer gates ToolSearch

The precedence rules in [`settings-precedence-table.md`](settings-precedence-table.md) apply. Managed policy wins over user settings:

```json
// managed_policy/tools.json
{ "toolsearch_enabled": false, "toolsearch_scope": "none" }
```

When this policy is active:

- `ToolSearch` is not included in the turn-one tool list.
- Deferred tools cannot be loaded.
- Tools that would normally be deferred remain entirely invisible.
- Tools marked `alwaysLoad: true` are still loaded — they are independent of ToolSearch.

## Policy decision flow

```
Is toolsearch_enabled = false?
├── YES → ToolSearch is not offered; deferred tools stay hidden for this session
└── NO  → ToolSearch is offered; proceed

  What is toolsearch_scope?
  ├── "none"         → Same as toolsearch_enabled = false
  ├── "mcp_only"     → Only MCP-sourced tools can be discovered
  ├── "builtins_only"→ Only built-in tools can be discovered
  └── "all"          → All deferred tools can be discovered (default)

  Is the calling source's trust class ≥ toolsearch_min_trust_class?
  ├── NO  → ToolSearch is blocked; log a trust-class violation
  └── YES → ToolSearch is available to the model
```

## Interaction with the tool registry

At session startup the tool pool is assembled as follows:

1. All `alwaysLoad` tools are included in the initial tool list.
2. All `shouldDefer` tools are registered in the deferred pool but withheld from the initial list.
3. If `toolsearch_enabled = false`, the deferred pool is frozen — tools in it cannot be loaded regardless of model behavior.
4. `ToolSearch` itself is an `alwaysLoad` built-in when `toolsearch_enabled = true`. It is the only tool that can promote deferred tools to callable.

```
Initial tool list (sent to model turn 1):
  [alwaysLoad tools]
  + ToolSearch (if enabled)

Deferred pool (hidden from model):
  [shouldDefer tools]
  → promoted one at a time as ToolSearch loads them
```

## Example: managed policy restricts ToolSearch to MCP tools only

```json
// managed_policy/toolsearch.json
{
  "toolsearch_scope": "mcp_only",
  "toolsearch_min_trust_class": "policy"
}
```

Effect:
- The model can call ToolSearch.
- ToolSearch only returns schemas for MCP-sourced tools.
- Built-in deferred tools remain invisible.
- A user or project file attempting `"toolsearch_scope": "all"` is blocked (min_trust_class = "policy").

## Example: fully open configuration (development)

```json
// user settings.json
{
  "toolsearch_enabled": true,
  "toolsearch_scope": "all",
  "defer_by_default": true
}
```

Effect:
- All tools that declare `shouldDefer: true` are deferred.
- `defer_by_default: true` also defers tools that do not explicitly declare a defer preference.
- The model sees `ToolSearch` and can discover any deferred tool.

## What ToolSearch does NOT control

- Whether a tool is permitted to execute (that is [`ai-coding-agents-permissions`](../../ai-coding-agents-permissions/SKILL.md)).
- Whether a tool exists in the registry (that is tool-pool assembly, see [`tool-registry-and-pool-assembly.md`](../../ai-coding-agents-tools/references/tool-registry-and-pool-assembly.md)).
- The ordering of `alwaysLoad` tools in the initial list (that is prompt-cache ordering, same reference).

## Anti-patterns

- Gating ToolSearch from inside the ToolSearch implementation itself. The settings layer should prevent ToolSearch from being offered to the model — not have ToolSearch refuse to run after being called.
- Allowing low-trust sources (local settings, project files) to override `toolsearch_min_trust_class` downward. Trust-class rules apply to this setting the same way they apply to all plugin-only surfaces.
- Confusing "ToolSearch disabled" with "deferred tools disabled." `alwaysLoad` tools are never affected by ToolSearch state.

## Related

- [`settings-precedence-table.md`](settings-precedence-table.md) — Full source-precedence table
- [`plugin-only-restriction-recipes.md`](plugin-only-restriction-recipes.md) — Trust-class enforcement for plugin surfaces
- [`../../ai-coding-agents-tools/references/deferred-loading-execution-and-remote-results.md`](../../ai-coding-agents-tools/references/deferred-loading-execution-and-remote-results.md) — ToolSearch execution pipeline
- [`../../ai-coding-agents-tools/references/deferral-eligibility-decision-tree.md`](../../ai-coding-agents-tools/references/deferral-eligibility-decision-tree.md) — When a tool should be deferred
