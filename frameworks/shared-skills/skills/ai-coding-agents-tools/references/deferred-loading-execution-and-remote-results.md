# Deferred Loading, Execution, And Remote Results

## Deferred Loading

The runtime uses `ToolSearch` plus two explicit flags:

- `shouldDefer`
- `alwaysLoad`

`tools/ToolSearchTool/prompt.ts` applies the deferral rules:

- MCP tools defer by default
- tools with `shouldDefer` defer
- tools with `alwaysLoad` never defer
- `ToolSearch` itself never defers
- some communication and agent-launch tools are forced to appear on turn one

Reusable rule:

- make deferral explicit on the tool contract
- add explicit opt-outs for tools that are operationally required on turn one
- keep discovery separate from execution

## Tool Search As Discovery Layer

`ToolSearch` is a meta-tool:

- it returns schemas for deferred tools
- the runtime only makes those tools callable after discovery
- the provider receives `defer_loading` metadata instead of full eager schemas

This keeps the initial prompt smaller without losing access to large MCP or workflow-specific tool surfaces.

## Execution Pipeline

`services/tools/toolExecution.ts` is the key reference for execution flow.

It handles:

- tool lookup
- progress events
- input validation
- permission and hook integration
- telemetry and tracing
- result shaping and storage
- follow-up message construction

Important pattern:

- keep execution policy in one central pipeline
- individual tools define their local behavior, but do not own global tracing, hook execution, or transcript shaping

## Transparent Wrapper Tools

The tool interface supports transparent wrappers.

Example pattern:

- a wrapper tool delegates rendering to nested progress events
- the wrapper itself emits no separate visible result block

Use this for:

- REPL or shell wrappers
- composite tools
- orchestration tools that expose inner work as the real visible activity

## Remote Tool Results

`remote/sdkMessageAdapter.ts` converts SDK messages into the same local message model used by the REPL.

Key patterns:

- detect tool-result user messages by content shape, not by unreliable parent IDs
- convert remote tool results into the same `UserMessage` form as local results
- convert historical user text only when needed
- ignore noisy success-result messages when they add no value

This is the right model for hybrid runtimes:

- remote and local tool uses should collapse, search, and render the same way
- normalize transport differences at the adapter boundary

## Remote Permission Bridges

The tool layer also interacts with remote permission flow:

- server-side permission requests arrive as control messages
- remote tool use may need synthetic local tool wrappers
- local UI still needs tool-like artifacts so prompts and decisions remain coherent

If you separate permission architecture into its own subsystem, keep the tool layer compatible with synthetic or proxied tools.

## Design Rules To Reuse

- Use explicit defer and always-load flags.
- Keep discovery and execution separate.
- Centralize tracing, hooks, and result shaping in the execution pipeline.
- Normalize remote results into the same local message model as early as possible.
- Use transparent wrapper tools for composite behaviors.
