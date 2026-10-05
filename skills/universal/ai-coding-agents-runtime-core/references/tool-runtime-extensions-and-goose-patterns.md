# Tool Runtime Extensions and Goose Patterns

Moved from the former tools skill. The main SKILL.md carries the rules; this file carries the reference-runtime extensions and cross-platform patterns.

## Reference Runtime: Tool System Extensions

These rules come from Claude Code's tool system. Look up the current tool names, rule syntax, and limits in its tools reference before copying them; the rules below are the durable part.

### Plugin-activated built-ins (LSP)

A built-in that activates when a plugin supplies its configuration (an LSP tool activated by plugin-supplied language-server config, for example) is its own origin class: not MCP-backed, not deferred, and always-loaded once the plugin activates. Tool pool rebuild on plugin reload must include its activation and deactivation, and deny rules against it follow the same path-pattern format as file-read rules.

The highest-value path is diagnostics. A language server pushes diagnostics to its client as notifications (`textDocument/publishDiagnostics` goes server → client). The runtime is the client: after an edit it injects the fresh diagnostics into the model's context without a separate tool call, which shortens the write → observe → fix loop from a shell round-trip to an in-pipeline event.

### Parameterized spawn rules

A subagent-spawning tool can take a type parameter in permission rules (for example `Agent(code-reviewer)` allows one subagent type, and a deny on the wildcard blocks spawning entirely). This is the same family as command-, path-, and domain-parameterized rules. Match the type specifier against the subagent name at spawn time, not at tool-registration time, so the rule can be written before the subagent definition exists.

### Subagent dispatch modes

- **Dispatch returns a handle; completion is a separate event.** A reference runtime can launch subagents in the background by default and run one in the foreground only when the parent needs the result before continuing; look up the host's current default in its sub-agents docs. A runtime that assumes synchronous return-on-call will race or hang on background completions.
- **Route background permission prompts to a visible session.** A background subagent's tool call that needs approval must surface in a session the user can see, named by subagent, with a per-call deny that does not kill the subagent. Silently auto-denying and continuing without the capability is a silent-failure trap.
- **Nesting depth is a field of the dispatch contract.** Carry the depth counter in the spawn contract and refuse an over-limit spawn locally with a clear error, instead of letting it round-trip to a server rejection. The limit and whether it can be configured are host-specific; look them up.
- **Claude Code fork mode is a third dispatch mode, not a variant of foreground/background.** Its documented conversation fork inherits the parent conversation and shares the parent's prompt-cache prefix; named subagents start from their own definitions. Keep this platform-scoped: another runtime's “fork” may copy a session, create a branch, or start fresh. Treat fork, named-background, and named-foreground as separate branches with explicit effective context and visibility rules.

Cross-cutting judgment call: a message delivered to a resumed or running subagent (via `SendMessage`) is task direction from its own launcher, not user consent or approval for a permission-gated action — the same trust boundary that applies to any agent-to-agent message applies here. A tool runtime's permission layer must not treat "another agent said so" as equivalent to a human granting a permission.

## Cross-Platform Patterns (Goose)

Goose's tool runtime lines up with this skill's existing tool contract, but two patterns are worth lifting explicitly.

### Unified tool origin (`type:` + `name:`)

Goose tools come from extensions declared as `{type: builtin|mcp, name: ...}`. Every tool surfaces to the model under one addressing scheme regardless of origin, and the tool registry's entry type carries `origin` rather than splitting across parallel registries.

- **Pattern:** model tool entries with a single discriminated shape: `{origin: Builtin|Mcp|AcpDelegated, name, schema, schema_version, activation_scope}`. Prompt-cache ordering and deny filtering apply uniformly.
- **Anti-pattern:** a "built-in tools table" separate from an "MCP tools table" with parallel permission and rendering semantics — exactly the pattern this skill already flags, but worth reinforcing.

### Toolshim as a tool-layer adapter

When the provider is a non-function-calling model (see `ai-coding-agents-provider-runtime`), the toolshim presents normalized tool-call events to the tool registry. The tool runtime does not care that the provider synthesized the call from text — the contract at the registry boundary stays the same.

- **Pattern:** the tool registry's call-in interface must not assume native function calling exists. The registry receives a `ToolInvocation` event; who produced it (native provider, toolshim adapter, ACP-delegated agent) is a provenance field, not a branching condition.
- **Anti-pattern:** tool registry code that reaches back into provider internals to decide whether to execute a call. That couples tool dispatch to provider brand and makes toolshim-wrapped providers unusable.
- **Recipe:** every `ToolInvocation` carries `invoked_by: ProviderId | ToolshimId | AcpAgentId`. Telemetry attributes cost, latency, and failure back to the invoker class, but execution flow does not branch on it.

### Runtime as both tool client and tool server

A runtime can be a tool client (it connects to external MCP servers to acquire tools) and also expose itself over a wire protocol as a tool for editors and orchestrators. Any runtime that exposes itself this way applies its full approval policy to remote callers, not just to local interactive sessions. Approval bypasses for "trusted AI callers" are architectural holes: the server-side approval policy applies regardless of caller identity.

For the server-side transport and how each runtime exposes itself, see [`../ai-coding-agents-surfaces/SKILL.md`](../../ai-coding-agents-surfaces/SKILL.md).

### Remote / ACP-delegated tool rendering

When a delegated ACP agent uses tools, their invocations and results must render in the orchestrator's REPL like local tool uses. This extends the skill's existing "normalize remote results" rule across the agent-delegation boundary.

- **Pattern:** the REPL treats tool events with `origin: AcpAgentId` identically to local tool events for rendering purposes; differences are in permission routing (orchestrator approves for the delegated agent) and accounting (costs attributed to the delegated agent row).

