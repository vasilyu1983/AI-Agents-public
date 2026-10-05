# Protocol Decision Tree — MCP vs A2A Selection Guide

*Purpose: Clear decision framework for choosing between Model Context Protocol (MCP) and Agent-to-Agent Protocol (A2A).*

**When to use this guide**: User is building agent infrastructure and needs to decide which protocol(s) to implement.

---
## Table of Contents

- [TL;DR Decision Matrix](#tldr-decision-matrix)
- [Visual Decision Tree](#visual-decision-tree)
- [Protocol Comparison Table](#protocol-comparison-table)
- [Common Anti-Patterns](#common-anti-patterns)
- [BAD: Anti-Pattern 1: Using A2A for Tool Access](#bad-anti-pattern-1-using-a2a-for-tool-access)
- [BAD: Anti-Pattern 2: Using MCP for Agent Coordination](#bad-anti-pattern-2-using-mcp-for-agent-coordination)
- [BAD: Anti-Pattern 3: Building Custom Protocol](#bad-anti-pattern-3-building-custom-protocol)
- [BAD: Anti-Pattern 4: Mixing Protocol Responsibilities](#bad-anti-pattern-4-mixing-protocol-responsibilities)
- [Implementation Checklist](#implementation-checklist)
- [Implementing MCP](#implementing-mcp)
- [Implementing A2A](#implementing-a2a)
- [Migration Strategies](#migration-strategies)
- [From Custom Tool Integration → MCP](#from-custom-tool-integration-→-mcp)
- [Agent code tightly coupled to GitHub API](#agent-code-tightly-coupled-to-github-api)
- [Agent uses MCP tool](#agent-uses-mcp-tool)
- [From Custom Agent Communication → A2A](#from-custom-agent-communication-→-a2a)
- [No validation, no trace propagation](#no-validation-no-trace-propagation)
- [Validated schema, full observability](#validated-schema-full-observability)
- [Next Steps](#next-steps)
- [Protocol Facts Checked Against the Specs (2026-09-27)](#protocol-facts-checked-against-the-specs-2026-09-27)
- [Summary](#summary)


## TL;DR Decision Matrix

| Question | Answer | Use |
|----------|--------|-----|
| Does agent need external data/tools? | Yes | **MCP** |
| Do multiple agents need to coordinate? | Yes | **A2A** |
| Building reusable tool library? | Yes | **MCP** |
| Need agent task delegation? | Yes | **A2A** |
| Connecting to databases/APIs? | Yes | **MCP** |
| Agent discovery/capability routing? | Yes | **A2A** |

**Most production systems use BOTH protocols for different purposes.** MCP is vertical integration (agent ↔ tools, data, prompts; implementation in [agents-mcp](../../agents-mcp/SKILL.md)); A2A is horizontal (agent ↔ agent handoffs, delegation, capability discovery via Agent Cards; implementation in [a2a-handoff-patterns.md](a2a-handoff-patterns.md)). A manager that reads a database and delegates to workers uses both: MCP for the read, A2A for the delegation.

---

## Visual Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│  What are you trying to accomplish?                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│ Agent needs   │         │ Agents need   │
│ external      │         │ to coordinate │
│ capabilities  │         │ with each     │
│               │         │ other         │
└───────┬───────┘         └───────┬───────┘
        │                         │
        ▼                         ▼
┌───────────────────────┐ ┌───────────────────────┐
│ Use MCP               │ │ Use A2A               │
│                       │ │                       │
│ • Tool access         │ │ • Task handoffs       │
│ • Data retrieval      │ │ • Delegation          │
│ • Resource management │ │ • Collaboration       │
│ • API integration     │ │ • Orchestration       │
└───────────────────────┘ └───────────────────────┘
```

---

## Protocol Comparison Table

| Aspect | MCP | A2A |
|--------|-----|-----|
| **Purpose** | Connect agents to tools/data | Connect agents to agents |
| **Direction** | Vertical (agent ↔ external) | Horizontal (agent ↔ agent) |
| **Primary Use** | Tool execution, data access | Task delegation, coordination |
| **Communication** | Request-response | Message passing with handoffs |
| **Discovery** | Tool/resource discovery | Agent capability discovery |
| **Validation** | Tool input schema | Handoff payload schema |
| **Observability** | Tool call traces | Handoff chain traces |
| **State** | Stateless tools | Stateful conversations |
| **Governance** | Originated at Anthropic; now an LF Projects, LLC project with individual (not company) maintainers — <https://modelcontextprotocol.io/community/governance> | Originated at Google, donated to the Linux Foundation, now under the Agentic AI Foundation; TSC includes AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, ServiceNow — <https://a2a-protocol.org/latest/> |

---

## Common Anti-Patterns

### BAD: Anti-Pattern 1: Using A2A for Tool Access

**Wrong**:
```
Agent A ─A2A→ Agent B (wrapper around database)
```

**Why wrong**: Agent B is just a thin wrapper around a tool, not adding intelligence

**Right**:
```
Agent A ─MCP→ Database Server
```

**Fix**: If it's just executing a tool, use MCP directly.

---

### BAD: Anti-Pattern 2: Using MCP for Agent Coordination

**Wrong**:
```
Agent A ─MCP→ "Agent B Tool" (agent exposed as MCP tool)
```

**Why wrong**: Loses A2A benefits (task lifecycle, Agent Card discovery, streaming and push updates, cross-vendor interoperability)

**Right**:
```
Agent A ─A2A→ Agent B
```

**Fix**: Use A2A when the callee crosses a vendor, organisation, or trust boundary, or needs a long-running task with its own lifecycle. Inside one runtime, agent-as-tool is legitimate and simpler (Claude Code subagents, ADK `AgentTool`, OpenAI Agents `as_tool()`); the cost you pay is no standard task state and no discovery, which only matters once a second party must call the agent.

---

### BAD: Anti-Pattern 3: Building Custom Protocol

**Wrong**:
```
Agent A ─custom JSON→ Agent B
Agent A ─custom API→ Tool Server
```

**Why wrong**: Reinventing the wheel, no interoperability, no tooling

**Right**:
```
Agent A ─A2A→ Agent B
Agent A ─MCP→ Tool Server
```

**Fix**: Use standard protocols unless you have very specific needs.

---

### BAD: Anti-Pattern 4: Mixing Protocol Responsibilities

**Wrong**:
```
MCP Tool that calls other agents (mixing vertical + horizontal)
```

**Why wrong**: Violates separation of concerns, hard to trace

**Right**:
```
Agent ─A2A→ Other Agent (coordination)
Agent ─MCP→ Tool (execution)
```

**Fix**: Keep protocols focused on their primary purpose.

---

## Implementation Checklist

### Implementing MCP

- [ ] Identify all external data sources (databases, APIs, files)
- [ ] Group related tools into logical MCP servers
- [ ] Define tool schemas (input/output)
- [ ] Implement security validation
- [ ] Add observability (traces, metrics)
- [ ] Test with MCP Inspector
- [ ] Document tools for agents
- [ ] Deploy with monitoring

**Guide**: [agents-mcp/references/mcp-custom.md](../../agents-mcp/references/mcp-custom.md)

### Implementing A2A

- [ ] Map agent collaboration workflows
- [ ] Define agent capabilities (agent cards)
- [ ] Design handoff message schemas
- [ ] Implement validation for all handoffs
- [ ] Add trace_id propagation
- [ ] Build error recovery mechanisms
- [ ] Set up agent registry/discovery
- [ ] Monitor handoff metrics

**Guide**: [a2a-handoff-patterns.md](a2a-handoff-patterns.md)

---

## Migration Strategies

### From Custom Tool Integration → MCP

**Before**: Direct API calls in agent code
```python
# Agent code tightly coupled to GitHub API
response = requests.post(
    "https://api.github.com/repos/owner/repo/issues",
    headers={"Authorization": f"token {GITHUB_TOKEN}"},
    json={"title": title, "body": body}
)
```

**After**: MCP server abstracts integration
```python
# Agent uses MCP tool
result = await mcp_client.call_tool(
    "create_github_issue",
    repo="owner/repo",
    title=title,
    body=body
)
```

**Benefits**: Reusable across agents, testable, secure, observable

---

### From Custom Agent Communication → A2A

**Before**: Ad-hoc JSON messages
```python
# No validation, no trace propagation
message = {"task": "analyze", "data": {...}}
requests.post(f"{agent_b_url}/tasks", json=message)
```

**After**: Structured A2A handoffs
```python
# Validated schema, full observability
handoff = {
    "schemaVersion": "v1.2",
    "trace_id": trace_id,
    "sender": {...},
    "receiver": {...},
    "task": {"type": "analyze", "description": "..."},
    "context": {...}
}
validate_handoff_schema(handoff)
await send_a2a_message(agent_b_id, handoff)
```

**Benefits**: Validation, traceability, error recovery, interoperability

---

## Next Steps

**After choosing your protocol(s)**:

1. **MCP path**: Read [agents-mcp](../../agents-mcp/SKILL.md) → Build server → Test with Inspector → Deploy
2. **A2A path**: Read [a2a-handoff-patterns.md](a2a-handoff-patterns.md) → Design handoffs → Implement validation → Monitor traces
3. **Both paths**: Start with MCP (simpler), add A2A when coordination needed

**Architecture references**:
- MCP: [`agents-mcp`](../../agents-mcp/SKILL.md) and the spec at <https://modelcontextprotocol.io/specification/latest>
- A2A: [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) and the spec at <https://a2a-protocol.org/latest/specification/>

**Questions to ask yourself**:
- How many agents? (1 = maybe just MCP, 2+ = consider A2A)
- Do they work together or independently? (together = A2A)
- What external systems? (databases/APIs = MCP)
- Need cross-vendor compatibility? (yes = use standard protocols)

---

## Protocol Facts Checked Against the Specs (2026-09-27)

These are the load-bearing wire-level facts. Re-check the two spec URLs before quoting them; both protocols cut releases several times a year.

| Fact | MCP (spec 2026-07-28) | A2A (spec 1.0.0) |
|---|---|---|
| Standard transports / bindings | `stdio` (client-launched subprocess) and Streamable HTTP (POST to one endpoint; replies as JSON or a request-scoped SSE stream). The older HTTP+SSE transport is no longer a standard binding; treat SSE-only servers as legacy. Custom transports over a byte stream should reuse stdio framing. | JSON-RPC 2.0, gRPC, and HTTP+JSON/REST bindings with identical semantics. |
| Discovery | Client lists tools/resources/prompts after connecting. | Agent Card at `https://{host}/.well-known/agent-card.json` (RFC 8615); `agents/getExtendedCard` for an authenticated, richer card. |
| Core operations | `tools/call`, `resources/read`, `prompts/get` plus list methods. Servers no longer initiate JSON-RPC requests in the current revision; interop with older `initialize`-based servers is via the compatibility matrix in the spec's versioning page. | `message/send`, `message/stream`, `tasks/get`, `tasks/list`, `tasks/cancel`, `tasks/subscribe`, `pushNotificationConfigs/{create,get,list,delete}`. |
| State model | Stateless per call; sessions are a transport concern. | Task lifecycle: `SUBMITTED`, `WORKING`, `INPUT_REQUIRED`, `AUTH_REQUIRED`, `COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`. Design handoff handling around `INPUT_REQUIRED` and `AUTH_REQUIRED`, which are the states most home-grown envelopes forget. |
| Authorization | HTTP transports: OAuth 2.1 (PKCE), server publishes RFC 9728 Protected Resource Metadata, client sends RFC 8707 `resource`; tokens in the `Authorization` header only, never the query string. `stdio` servers take credentials from the environment and must not run the OAuth flow. | Standard web auth declared in the Agent Card (OAuth 2, API keys, mTLS); A2A does not define its own auth scheme. |
| Sources | <https://modelcontextprotocol.io/specification/latest/basic/transports>, <https://modelcontextprotocol.io/specification/latest/basic/authorization> | <https://a2a-protocol.org/latest/specification/>, <https://a2a-protocol.org/latest/topics/agent-discovery/> |

Decision consequence: if your "A2A" payload is a JSON blob POSTed to `/tasks` with no task id, no state enum, and no Agent Card, you have a custom protocol (Anti-Pattern 3) wearing the A2A name. Either adopt the real wire format via a framework that ships it, or call it an internal handoff envelope and do not promise interoperability.

## Summary

**Simple rule of thumb**:

```
Agent ↔ External System = MCP
Agent ↔ Agent          = A2A
```

**Remember**: These protocols are **complementary**, not competing. Most production systems use both for different purposes. Choose based on what you're connecting, not on preference.
