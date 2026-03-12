# Protocol Decision Tree — MCP vs A2A Selection Guide

*Purpose: Clear decision framework for choosing between Model Context Protocol (MCP) and Agent-to-Agent Protocol (A2A).*

**When to use this guide**: User is building agent infrastructure and needs to decide which protocol(s) to implement.

---

## TL;DR Decision Matrix

| Question | Answer | Use |
|----------|--------|-----|
| Does agent need external data/tools? | Yes | **MCP** |
| Do multiple agents need to coordinate? | Yes | **A2A** |
| Building reusable tool library? | Yes | **MCP** |
| Need agent task delegation? | Yes | **A2A** |
| Connecting to databases/APIs? | Yes | **MCP** |
| Agent discovery/capability routing? | Yes | **A2A** |

**Most production systems use BOTH protocols for different purposes.**

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

## Detailed Decision Framework

### Scenario 1: Agent Needs to Access External Systems

**Question**: Does your agent need to query databases, call APIs, read files, or execute tools?

**Answer**: Use **MCP**

**Why**: MCP standardizes how agents connect to external data sources and tools.

**Example architecture**:
```
┌─────────────┐
│   Agent     │
└──────┬──────┘
       │ (via MCP Client)
       ▼
┌──────────────────────┐
│   MCP Servers        │
├──────────────────────┤
│ • Database Server    │
│ • Filesystem Server  │
│ • API Wrapper Server │
│ • Search Server      │
└──────────────────────┘
```

**Real-world examples**:
- Customer support agent querying CRM database
- Code assistant reading project files
- Research agent searching web/documents
- DevOps agent managing infrastructure APIs

**Implementation**: See [mcp-practical-guide.md](mcp-practical-guide.md)

---

### Scenario 2: Multiple Agents Need to Coordinate

**Question**: Do you have multiple specialized agents that need to collaborate or delegate tasks?

**Answer**: Use **A2A**

**Why**: A2A provides structured handoffs with validation and observability.

**Example architecture**:
```
┌──────────────┐     A2A     ┌──────────────┐
│ Manager      │────────────→│ Worker A     │
│ Agent        │             │ (Specialist) │
└──────┬───────┘             └──────────────┘
       │ A2A                 ┌──────────────┐
       └────────────────────→│ Worker B     │
                             │ (Specialist) │
                             └──────────────┘
```

**Real-world examples**:
- Project manager agent delegating to dev/test/deploy agents
- Research coordinator distributing search tasks
- Content creation workflow (research → write → edit → publish)
- Customer inquiry routing to specialized support agents

**Implementation**: See [a2a-handoff-patterns.md](a2a-handoff-patterns.md)

---

### Scenario 3: Building Multi-Agent System with External Tools

**Question**: Do agents need BOTH external tools AND inter-agent coordination?

**Answer**: Use **BOTH MCP and A2A**

**Why**: Protocols are complementary, not competitive.

**Example architecture**:
```
┌────────────────────────────────────────────┐
│  Manager Agent                             │
│  ├─ Uses MCP for: DB access, file ops     │
│  └─ Uses A2A for: Delegating to workers   │
└────────┬───────────────────┬───────────────┘
         │ A2A               │ A2A
         ▼                   ▼
┌────────────────┐   ┌────────────────┐
│  Worker A      │   │  Worker B      │
│  Uses MCP for: │   │  Uses MCP for: │
│  • API calls   │   │  • File writes │
│  • Validation  │   │  • Email send  │
└────────────────┘   └────────────────┘
```

**Real-world example: Content Publishing System**
```
Manager Agent (Coordinator)
├─ MCP: Read content guidelines from docs
├─ MCP: Query content calendar database
└─ A2A: Delegate tasks ↓

    Research Agent
    ├─ MCP: Search web for sources
    ├─ MCP: Access research database
    └─ A2A: Handoff to Writer ↓

        Writer Agent
        ├─ MCP: Read style guide
        ├─ MCP: Use grammar checking tool
        └─ A2A: Handoff to Editor ↓

            Editor Agent
            ├─ MCP: Access revision history
            ├─ MCP: Publish to CMS API
            └─ A2A: Return to Manager
```

**Key insight**: MCP handles vertical integration (agent ↔ tools), A2A handles horizontal integration (agent ↔ agent).

---

## Decision by Use Case

### 1. Single Agent with Tools

**Characteristics**:
- One agent handles all tasks
- Needs external data/APIs
- No delegation required

**Protocol**: **MCP only**

**Example**: Personal assistant agent
```
Assistant Agent
├─ MCP: Calendar API
├─ MCP: Email API
├─ MCP: Weather API
└─ MCP: Notes database
```

---

### 2. Multi-Agent Collaboration (No External Tools)

**Characteristics**:
- Multiple specialized agents
- Pure reasoning/planning tasks
- No external data needed

**Protocol**: **A2A only**

**Example**: Creative writing team
```
Plot Designer ─A2A→ Character Developer ─A2A→ Scene Writer
      ↑                                           │
      └───────────────── A2A ─────────────────────┘
```

---

### 3. Multi-Agent System with Shared Tool Access

**Characteristics**:
- Multiple agents
- Each needs external tools
- Coordination required

**Protocol**: **Both MCP and A2A**

**Example**: Software development team
```
Product Manager Agent
├─ MCP: Jira API, user research database
└─ A2A: Delegates to ↓

    Backend Developer Agent
    ├─ MCP: GitHub API, database schema
    └─ A2A: Collaborates with ↓

        Frontend Developer Agent
        ├─ MCP: Figma API, component library
        └─ A2A: Handoff to ↓

            QA Tester Agent
            ├─ MCP: Test framework, bug tracker
            └─ A2A: Report back to Product Manager
```

---

### 4. Agent Needs Dynamic Tool Discovery

**Characteristics**:
- Agent discovers available tools at runtime
- Different tools for different contexts
- Need standardized tool interface

**Protocol**: **MCP** (with tool discovery)

**Example**: Development assistant
```
Dev Assistant Agent
├─ Discovers available MCP servers
├─ Dynamically loads appropriate tools
└─ Adapts to different project types

Available MCP Servers:
• Python tools (pytest, mypy, black)
• Node tools (npm, eslint, prettier)
• Database tools (postgres, redis, mongo)
• Cloud tools (aws, gcp, azure)
```

---

### 5. Agent Needs Dynamic Agent Discovery

**Characteristics**:
- Coordinator discovers available agents
- Delegates based on capabilities
- Agents join/leave dynamically

**Protocol**: **A2A** (with agent cards)

**Example**: Customer support routing
```
Support Coordinator Agent
├─ Discovers available specialist agents
├─ Routes based on agent capabilities
└─ Dynamically scales with demand

Available Specialist Agents:
• Billing Agent (capabilities: payments, refunds, invoicing)
• Technical Agent (capabilities: troubleshooting, bug_reports)
• Account Agent (capabilities: profile, security, authentication)
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
| **Adoption** | Anthropic, OpenAI, Google | Anthropic, multi-agent frameworks |

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

**Why wrong**: Loses A2A benefits (context propagation, trace_id, validation)

**Right**:
```
Agent A ─A2A→ Agent B
```

**Fix**: If it involves reasoning/intelligence, use A2A for proper handoffs.

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

**Guide**: [mcp-practical-guide.md](mcp-practical-guide.md)

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

## Quick Reference: When to Use What

### Use MCP when agent needs:

- Database queries
- File system access
- API calls to third-party services
- Search capabilities
- Tool execution
- Resource retrieval
- Prompt templates

### Use A2A when you need:

- Task delegation between agents
- Agent collaboration workflows
- Capability-based routing
- Multi-agent coordination
- Handoff validation
- Cross-vendor agent communication
- Trace propagation across agents

### Use BOTH when:

- Building complex multi-agent systems
- Agents need external tools AND coordination
- Enterprise-scale agent architectures
- Maximum observability required

---

## Next Steps

**After choosing your protocol(s)**:

1. **MCP path**: Read [mcp-practical-guide.md](mcp-practical-guide.md) → Build server → Test with Inspector → Deploy
2. **A2A path**: Read [a2a-handoff-patterns.md](a2a-handoff-patterns.md) → Design handoffs → Implement validation → Monitor traces
3. **Both paths**: Start with MCP (simpler), add A2A when coordination needed

**Architecture references**:
- MCP deep dive: `frameworks/shared-foundations/protocols/mcp/mcp-architecture.md`
- A2A deep dive: `frameworks/shared-foundations/protocols/a2a/a2a-architecture.md`

**Questions to ask yourself**:
- How many agents? (1 = maybe just MCP, 2+ = consider A2A)
- Do they work together or independently? (together = A2A)
- What external systems? (databases/APIs = MCP)
- Need cross-vendor compatibility? (yes = use standard protocols)

---

## Summary

**Simple rule of thumb**:

```
Agent ↔ External System = MCP
Agent ↔ Agent          = A2A
```

**Remember**: These protocols are **complementary**, not competing. Most production systems use both for different purposes. Choose based on what you're connecting, not on preference.
