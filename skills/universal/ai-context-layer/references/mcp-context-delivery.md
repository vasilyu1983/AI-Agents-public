# MCP Context Delivery

MCP (Model Context Protocol) is the standard mechanism for delivering context from external systems to agents and AI-powered applications. Use MCP when the context source is a service, database, or API that the agent needs to access at runtime.

## MCP Primitives for Context

MCP exposes three primitives, each suited to a different context need:

- **Resources**: read-only context the server exposes. Use for entity profiles, memory snapshots, knowledge source catalogs, and configuration. The agent reads resources without side effects.
- **Tools**: actions the agent can invoke. Use for live data fetches (billing state, entitlement checks), writes (memory updates, feedback submission), and multi-step retrieval.
- **Prompts**: reusable prompt templates the server provides. Use for standardized context assembly instructions or domain-specific reasoning templates.

## When to Use MCP for Context Delivery

Use MCP when:

- The context source is an external service with its own API (CRM, ticketing, knowledge base, internal tools).
- Multiple agents or surfaces need access to the same context source with consistent contracts.
- You want to decouple context sources from the agent implementation — swap providers without changing agent code.
- The context source requires authentication that should be managed at the server boundary, not in the agent.

Use direct API calls instead when:

- The source is a local database or in-process cache with no need for protocol abstraction.
- Latency is critical and the MCP transport overhead is unacceptable.
- The context source is used by exactly one agent and will not be reused.

## MCP Resource Patterns for Context Layers

- **Entity profile server**: exposes `user/{id}`, `org/{id}`, `product/{id}` as resources. The agent reads the relevant profile as part of context assembly.
- **Memory server**: exposes `memory/{entity_id}` as a resource for reading learned memories. Exposes `update_memory` as a tool for writing corrections and new memories.
- **Knowledge catalog server**: exposes `sources/` as a resource listing available knowledge sources. Exposes `retrieve` as a tool that accepts a query and returns grounded results with evidence metadata.
- **Feedback server**: exposes `submit_feedback` as a tool for recording corrections and outcomes.

## OpenMemory MCP (P10 + P13 Hybrid)

OpenMemory MCP is Mem0's local-first MCP memory server. It runs memory storage
on your own machine or infra (P10 filesystem-as-memory) while exposing the
memory API as an MCP server that any MCP-compatible client can call (P13
managed-memory boundary). Compatible with Claude Desktop, Cursor, and VS Code.

**Pattern classification.** P10 + P13 hybrid: storage stays local (you own the
bytes), MCP is the delivery layer (the agent calls memory via the protocol, not
a hardcoded SDK). This is the same boundary characteristic as the Anthropic
Memory Tool — the vendor ships the interface, you own the storage.

**When to use.**
- You want Mem0 extraction and recall without routing memories through an
  external cloud service.
- Multiple MCP-compatible tools (Claude Desktop, an IDE agent, a terminal agent)
  need to share a memory context across sessions.
- Privacy or compliance constraints rule out cloud-hosted memory.

**Boundary rules (same as Anthropic Memory Tool, Case 2 in
`managed-memory-boundaries.md`).**
- Storage owner: you. Scope and forget are your responsibility.
- Extraction model runs locally or via a locally-configured provider.
- Operational truth (account state, billing, permissions) must not flow through
  OpenMemory MCP — route those to tools or SQL as usual (P1).

See [managed-memory-boundaries.md](managed-memory-boundaries.md) for the full
P13 boundary checklist.

## Security and Tenant Isolation

- Use OAuth2 or token-based authentication on MCP servers. Never rely on network-level isolation alone.
- Enforce tenant scope at the MCP server boundary. The server validates that the requesting agent has access to the requested entity scope before returning context.
- Log all context access with actor identity, entity scope, and timestamp for audit.

See [agents-mcp](../../agents-mcp/SKILL.md) for MCP server implementation patterns.

## Upcoming Spec Revision

Check the current MCP specification revision before relying on the transport and session details here. Revisions can change the transport (for example toward a stateless HTTP core) and add extensions; re-check the context-delivery patterns in this file (Resources, Tools, Prompts, tenant isolation, OpenMemory integration) against each new revision — especially any change to how session-bound context and memory servers keep scope across requests.
