# Tool Registry And Pool Assembly

## Table Of Contents

- [Core Pattern](#core-pattern)
- [Useful Tool Contract](#useful-tool-contract)
- [Base Tool Set](#base-tool-set)
- [Pool Assembly](#pool-assembly)
- [Filter Before Exposure](#filter-before-exposure)
- [Stable Ordering For Prompt Cache](#stable-ordering-for-prompt-cache)
- [Special Modes](#special-modes)
- [Design Rules To Reuse](#design-rules-to-reuse)

## Core Pattern

Treat tools as first-class runtime objects with a rich contract, not just callables.

From the April 2026 `claude_code` snapshot:

- the shared interface lives in `Tool.ts`
- pool assembly lives in `tools.ts`
- merge and coordinator-mode filtering lives in `utils/toolPool.ts`

## Useful Tool Contract

The runtime’s tool interface includes:

- identity
  - `name`
  - optional `aliases`
  - optional `searchHint`
- execution
  - `call`
  - input schema
  - optional output schema
- safety
  - `validateInput`
  - `checkPermissions`
  - `isReadOnly`
  - optional `isDestructive`
- runtime behavior
  - `interruptBehavior`
  - concurrency safety
  - transparent-wrapper behavior
- presentation
  - user-facing name
  - activity description
  - tool-use rendering
  - tool-result rendering
- discovery
  - `shouldDefer`
  - `alwaysLoad`
  - MCP metadata

This is a strong pattern for coding-agent CLIs because it keeps validation, rendering, and execution expectations on one stable contract.

## Base Tool Set

`getAllBaseTools()` is the source of truth for built-ins.

It uses:

- feature gates
- environment gates
- runtime mode gates
- helper functions for optional tool families

Reusable rule:

- keep one exhaustive base-tool function
- apply filtering after base enumeration
- avoid duplicating the built-in list across REPL, headless, and worker flows

## Pool Assembly

The runtime uses distinct stages:

1. `getTools(permissionContext)`
   - built-ins only
   - special mode handling
   - blanket deny filtering
   - REPL-only tool hiding
   - `isEnabled()` checks

2. `assembleToolPool(permissionContext, mcpTools)`
   - merge built-ins with MCP tools
   - filter MCP tools by deny rules
   - dedupe by name
   - sort for prompt-cache stability

3. `mergeAndFilterTools(initialTools, assembled, mode)`
   - prepend initial or startup tools
   - dedupe again
   - partition built-ins from MCP
   - apply coordinator-mode filtering

This separation is worth copying:

- one function for built-ins
- one function for full runtime pool
- one function for mode-specific merged views

## Filter Before Exposure

`filterToolsByDenyRules()` removes blanket-denied tools before they reach the model.

Important pattern:

- do not rely on call-time denial alone
- hide impossible tools from planning-time context
- apply the same matching rules to built-ins and MCP tools

## Stable Ordering For Prompt Cache

The repo keeps built-ins as a contiguous prefix and sorts built-ins separately from MCP tools.

Why:

- prompt-cache keys depend on tool ordering
- letting MCP tools interleave with built-ins can invalidate downstream cache keys

Reusable rule:

- if your provider caches prompt prefixes, keep tool ordering deterministic and partitioned by source when needed

## Special Modes

`getTools()` handles special modes such as:

- simple mode
- REPL mode hiding primitive tools behind a wrapper
- coordinator mode allowing only orchestration-safe tools

This is a better pattern than cloning multiple tool registries for each mode.

## Design Rules To Reuse

- Keep one rich tool contract.
- Build one canonical base-tool list.
- Assemble built-ins and external tools through a single pool function.
- Filter deny-listed tools before exposure.
- Preserve deterministic ordering for cache-sensitive providers.
