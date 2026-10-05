# A2A Handoff Patterns — Agent Coordination Guide

*Purpose: Practical patterns for agent-to-agent communication, task handoffs, and multi-agent orchestration using the A2A protocol.*

**When to use this guide**: User asks to coordinate multiple agents, implement agent delegation, or build collaborative AI workflows.

**Scope note**: the schemas in this file are an *internal handoff envelope* (`schemaVersion`, `trace_id`, `sender`/`receiver`, `task`, `context`) that you validate yourself. They are not the A2A wire format. The real protocol has Agent Cards at `/.well-known/agent-card.json`, `message/send` / `message/stream` / `tasks/*` operations, and a task-state enum (`SUBMITTED` … `INPUT_REQUIRED`, `AUTH_REQUIRED`, `COMPLETED`, `FAILED`, `CANCELED`, `REJECTED`). Use the envelope inside one runtime; when a second vendor or organisation must call your agent, adopt the protocol through a framework that ships it and map the envelope fields onto A2A `Message`/`Task` objects. Verified facts and spec links: [`protocol-decision-tree.md` § Protocol Facts](protocol-decision-tree.md#protocol-facts-checked-against-the-specs-2026-09-27).

---
## Table of Contents

- [Quick Decision: Do I Need A2A?](#quick-decision-do-i-need-a2a)
- [A2A Architecture (Quick Reference)](#a2a-architecture-quick-reference)
- [Core A2A Message Schema](#core-a2a-message-schema)
- [Patterns 1-3: Sequential, Manager-Worker, Group Chat](#patterns-1-3-sequential-manager-worker-group-chat)
- [Pattern 4: Agent Card Discovery](#pattern-4-agent-card-discovery)
- [Agent Card Schema (internal registry example)](#agent-card-schema-internal-registry-example)
- [Discovery Implementation](#discovery-implementation)
- [Usage: Manager discovers appropriate agent](#usage-manager-discovers-appropriate-agent)
- [Find agent that can write SQL and optimize queries](#find-agent-that-can-write-sql-and-optimize-queries)
- [Pattern 5: Error Recovery and Retry](#pattern-5-error-recovery-and-retry)
- [Validation & Schema Management](#validation--schema-management)
- [Handoff Schema Validation](#handoff-schema-validation)
- [Define A2A handoff schema](#define-a2a-handoff-schema)
- [Observability & Monitoring](#observability--monitoring)
- [Full Trace Tracking](#full-trace-tracking)
- [Metrics to Track](#metrics-to-track)
- [Handoff metrics](#handoff-metrics)
- [A2A vs MCP: When to Use What](#a2a-vs-mcp-when-to-use-what)
- [Production Checklist](#production-checklist)
- [Next Steps](#next-steps)


## Quick Decision: Do I Need A2A?

**Use A2A when**:
- Multiple agents need to collaborate on a task
- Delegating subtasks to specialized agents
- Building manager-worker agent patterns
- Need traceable, auditable agent communication
- Agents from different vendors/frameworks must interoperate

**Don't use A2A when**:
- Single agent handles everything (no coordination needed)
- Agent needs external data/tools (use MCP instead)
- Simple sequential pipeline without decision-making

---

## A2A Architecture (Quick Reference)

```
┌──────────────┐                           ┌──────────────┐
│  Agent A     │    A2A Message Protocol   │  Agent B     │
│  (Sender)    │ ───────────────────────→  │  (Receiver)  │
│              │                           │              │
│ - Creates    │    {                      │ - Validates  │
│   task       │      task,                │   payload    │
│ - Packages   │      context,             │ - Executes   │
│   context    │      constraints          │   task       │
│ - Sends      │    }                      │ - Returns    │
│              │                           │   result     │
└──────────────┘                           └──────────────┘
```

**Key concept**: A2A = structured handoffs with validation, not just message passing.

---

## Core A2A Message Schema

Every A2A handoff includes:

```json
{
  "schemaVersion": "v1.2",
  "trace_id": "req-abc-123-xyz",
  "timestamp": "2025-01-15T10:30:00Z",
  "sender": {
    "agent_id": "sales-analyzer-01",
    "agent_type": "data-analyst",
    "capabilities": ["sql", "visualization", "forecasting"]
  },
  "receiver": {
    "agent_id": "report-generator-03",
    "agent_type": "document-writer",
    "required_capabilities": ["pdf-generation", "charting"]
  },
  "task": {
    "type": "generate_report",
    "description": "Create quarterly sales report",
    "priority": "high",
    "deadline": "2025-01-16T17:00:00Z"
  },
  "context": {
    "sales_data": {...},
    "previous_reports": [...],
    "template_id": "q4-2024"
  },
  "constraints": {
    "max_pages": 20,
    "output_format": "pdf",
    "include_sections": ["summary", "trends", "forecast"]
  },
  "metadata": {
    "correlation_id": "campaign-456",
    "user_id": "user-789",
    "session_id": "sess-012"
  }
}
```

**Validation requirements**:
- JSON Schema validation on every handoff
- Required fields: `schemaVersion`, `trace_id`, `task`, `sender`, `receiver`
- Optional fields: `context`, `constraints`, `metadata`
- Receivers MUST validate before executing

---

## Patterns 1-3: Sequential, Manager-Worker, Group Chat

Owned by [`multi-agent-patterns.md`](multi-agent-patterns.md) (Sequential Orchestration, Magentic Pattern, Group Chat Orchestration). Every hop in those topologies carries the envelope above: preserve `trace_id` across the chain, validate on receipt, include prior results in `context`, and set `constraints` for the next agent.

---

## Pattern 4: Agent Card Discovery

**Use case**: Agents advertise capabilities so others can discover and delegate appropriately.

The card below is an illustrative registry record for an in-house registry. A spec-conformant A2A Agent Card is a different document (name, description, `url`, `capabilities` such as streaming and push notifications, `skills`, `securitySchemes`, `defaultInputModes`/`defaultOutputModes`) served at `/.well-known/agent-card.json`; generate it from the framework rather than hand-writing it (<https://a2a-protocol.org/latest/topics/agent-discovery/>). In Google ADK the card is generated from the agent definition and a remote agent is consumed through `RemoteA2aAgent`, which handles auth, serialization, and result streaming (<https://google.github.io/adk-docs/a2a/>). A registry keyed on those cards is what lets a coordinator delegate to a specialist owned by another team, language, or framework without hardcoded URLs.

### Agent Card Schema (internal registry example)

```json
{
  "agent_id": "sql-expert-agent-05",
  "agent_type": "database-specialist",
  "version": "2.1.0",
  "capabilities": [
    "sql-query-generation",
    "query-optimization",
    "database-schema-analysis",
    "data-validation"
  ],
  "supported_databases": ["postgres", "mysql", "bigquery"],
  "constraints": {
    "max_query_complexity": "high",
    "timeout_seconds": 300,
    "max_result_rows": 10000
  },
  "input_schema": {
    "type": "object",
    "required": ["query_description", "database_type"],
    "properties": {
      "query_description": {"type": "string"},
      "database_type": {"type": "string", "enum": ["postgres", "mysql", "bigquery"]},
      "optimization_level": {"type": "string", "enum": ["none", "standard", "aggressive"]}
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "sql_query": {"type": "string"},
      "execution_plan": {"type": "string"},
      "estimated_cost": {"type": "number"}
    }
  },
  "availability": {
    "status": "online",
    "uptime_sla": "99.9%",
    "rate_limit": "100 requests/minute"
  },
  "endpoints": {
    "handoff": "https://api.example.com/agents/sql-expert-05/handoff",
    "health": "https://api.example.com/agents/sql-expert-05/health"
  }
}
```

### Discovery Implementation

```python
class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, agent_card):
        """Register agent with capabilities"""
        validate_agent_card(agent_card)
        self.agents[agent_card["agent_id"]] = agent_card

    def discover(self, required_capabilities):
        """Find agents matching required capabilities"""
        matching_agents = []

        for agent_id, card in self.agents.items():
            if all(cap in card["capabilities"] for cap in required_capabilities):
                matching_agents.append(card)

        return matching_agents


# Usage: Manager discovers appropriate agent
registry = AgentRegistry()

# Find agent that can write SQL and optimize queries
candidates = registry.discover([
    "sql-query-generation",
    "query-optimization"
])

if candidates:
    best_agent = select_best_agent(candidates)  # e.g., by uptime, rate limit
    handoff = create_handoff(best_agent["agent_id"], task)
    result = await send_to_agent(best_agent["endpoints"]["handoff"], handoff)
```

---

## Pattern 5: Error Recovery and Retry

**Use case**: Handle failures gracefully with fallback strategies.

```python
async def resilient_handoff(handoff_message, max_retries=3):
    """Handoff with automatic retry and fallback"""
    original_receiver = handoff_message["receiver"]["agent_id"]

    for attempt in range(max_retries):
        try:
            # Attempt handoff
            result = await send_to_agent(original_receiver, handoff_message)

            # Validate result
            if validate_result(result):
                return result

            # Invalid result - log and retry
            log_warning(f"Invalid result from {original_receiver}, attempt {attempt+1}")

        except TimeoutError:
            log_error(f"Timeout on attempt {attempt+1}")

        except AgentUnavailableError:
            # Try fallback agent with same capabilities
            fallback_agent = await find_fallback_agent(
                required_capabilities=handoff_message["receiver"]["required_capabilities"]
            )

            if fallback_agent:
                log_info(f"Switching to fallback agent: {fallback_agent['agent_id']}")
                handoff_message["receiver"]["agent_id"] = fallback_agent["agent_id"]
            else:
                raise NoAvailableAgentError()

        # Exponential backoff
        await asyncio.sleep(2 ** attempt)

    # All retries exhausted
    raise MaxRetriesExceededError(f"Failed after {max_retries} attempts")


async def find_fallback_agent(required_capabilities):
    """Find alternative agent with same capabilities"""
    registry = AgentRegistry()
    candidates = registry.discover(required_capabilities)

    # Filter by availability
    available = [c for c in candidates if c["availability"]["status"] == "online"]

    if not available:
        return None

    # Select best by uptime/load
    return max(available, key=lambda a: a["availability"]["uptime_sla"])
```

**Error handling best practices**:
- Always include `trace_id` in error responses
- Log failures with full context
- Implement exponential backoff
- Have fallback agents ready
- Set reasonable timeouts (30-300s)
- Return actionable error messages

---

## Validation & Schema Management

### Handoff Schema Validation

```python
from jsonschema import validate, ValidationError

# Define A2A handoff schema
A2A_HANDOFF_SCHEMA = {
    "type": "object",
    "required": ["schemaVersion", "trace_id", "sender", "receiver", "task"],
    "properties": {
        "schemaVersion": {"type": "string", "pattern": "^v[0-9]+\\.[0-9]+$"},
        "trace_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "sender": {
            "type": "object",
            "required": ["agent_id", "agent_type"],
            "properties": {
                "agent_id": {"type": "string"},
                "agent_type": {"type": "string"}
            }
        },
        "receiver": {
            "type": "object",
            "required": ["agent_id", "agent_type"],
            "properties": {
                "agent_id": {"type": "string"},
                "agent_type": {"type": "string"}
            }
        },
        "task": {
            "type": "object",
            "required": ["type", "description"],
            "properties": {
                "type": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
            }
        }
    }
}

def validate_handoff_schema(handoff_message):
    """Validate A2A handoff message against schema"""
    try:
        validate(instance=handoff_message, schema=A2A_HANDOFF_SCHEMA)
        return True
    except ValidationError as e:
        log_error(f"Schema validation failed: {e.message}")
        return False
```

---

## Observability & Monitoring

### Full Trace Tracking

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

async def traced_handoff(handoff_message):
    """Handoff with full OpenTelemetry tracing"""
    with tracer.start_as_current_span("agent_handoff") as span:
        # Add handoff metadata to span
        span.set_attribute("a2a.trace_id", handoff_message["trace_id"])
        span.set_attribute("a2a.sender.id", handoff_message["sender"]["agent_id"])
        span.set_attribute("a2a.receiver.id", handoff_message["receiver"]["agent_id"])
        span.set_attribute("a2a.task.type", handoff_message["task"]["type"])

        try:
            result = await send_to_agent(
                handoff_message["receiver"]["agent_id"],
                handoff_message
            )

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("a2a.result.status", "success")
            return result

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("a2a.error", str(e))
            span.record_exception(e)
            raise
```

### Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Handoff metrics
handoff_total = Counter('a2a_handoff_total', 'Total handoffs', ['sender', 'receiver'])
handoff_duration = Histogram('a2a_handoff_duration_seconds', 'Handoff latency')
handoff_errors = Counter('a2a_handoff_errors', 'Failed handoffs', ['error_type'])
active_handoffs = Gauge('a2a_active_handoffs', 'Currently processing handoffs')

async def monitored_handoff(handoff_message):
    """Handoff with metrics"""
    sender = handoff_message["sender"]["agent_id"]
    receiver = handoff_message["receiver"]["agent_id"]

    handoff_total.labels(sender=sender, receiver=receiver).inc()
    active_handoffs.inc()

    start_time = time.time()

    try:
        result = await send_to_agent(receiver, handoff_message)
        return result
    except Exception as e:
        handoff_errors.labels(error_type=type(e).__name__).inc()
        raise
    finally:
        duration = time.time() - start_time
        handoff_duration.observe(duration)
        active_handoffs.dec()
```

---

## A2A vs MCP: When to Use What

| Scenario | Use A2A | Use MCP |
|----------|---------|---------|
| Agent needs external data | | [check] |
| Agent needs to call tools | | [check] |
| Multiple agents collaborate | [check] | |
| Task delegation | [check] | |
| Agent discovery | [check] | |
| Cross-vendor interop | [check] | |
| Database/API access | | [check] |
| Standardized tool library | | [check] |

**Complementary use**: Many systems use BOTH:
- MCP: Agent ↔ Tools/Data
- A2A: Agent ↔ Agent

---

## Production Checklist

Before deploying A2A coordination:

- [ ] All handoffs have JSON Schema validation
- [ ] `trace_id` propagates through entire workflow
- [ ] Error handling with fallback agents
- [ ] Timeouts set on all handoffs (30-300s)
- [ ] Observability: traces, metrics, logs
- [ ] Agent registry with capability discovery
- [ ] Rate limiting per agent
- [ ] Authentication between agents
- [ ] Audit log of all handoffs
- [ ] Circuit breakers for failing agents
- [ ] Health checks for all agents
- [ ] Monitoring dashboard with handoff metrics

---

## Next Steps

**After implementing A2A patterns**:
1. Test handoffs with invalid payloads (validation)
2. Simulate agent failures (resilience)
3. Monitor trace propagation (observability)
4. Benchmark handoff latency (performance)
5. Document agent capabilities (discovery)

**Related guides**:
- `frameworks/shared-foundations/protocols/a2a/a2a-architecture.md` - Full protocol specification
- `frameworks/shared-foundations/protocols/a2a/a2a-implementation.md` - Implementation details
- `frameworks/shared-foundations/protocols/a2a/a2a-examples.md` - Real-world examples
- [`agents-mcp`](../../agents-mcp/SKILL.md) - For agent-to-tool integration (complementary)
- `multi-agent-patterns.md` - Additional orchestration strategies

**Official resources**:
- A2A Specification: https://a2a.anthropic.com/
- Agent Communication Best Practices: https://www.anthropic.com/research/agent-coordination
