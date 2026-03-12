# Pydantic AI — Production Patterns

**Version**: v1.66.0 (March 2026) | V1.0.0 GA: September 2025 | V2 planned: April 2026+

**What**: Type-safe Python agent framework from the Pydantic team. FastAPI-style DX for GenAI — agents are Python functions + Pydantic schemas, not YAML configs or graph definitions.

**When to choose over alternatives**: Type safety is critical, you want native MCP + A2A interoperability, your team already uses Pydantic/FastAPI, or you need durable execution with minimal infrastructure.

---

## Table of Contents

1. [Agent Definition](#agent-definition)
2. [Tool Use](#tool-use)
3. [Structured Outputs](#structured-outputs)
4. [Dependencies (Dependency Injection)](#dependencies)
5. [MCP Integration](#mcp-integration)
6. [A2A Protocol Support](#a2a-protocol-support)
7. [pydantic-graph (FSM Workflows)](#pydantic-graph-fsm-workflows)
8. [Durable Execution](#durable-execution)
9. [Human-in-the-Loop (HITL)](#human-in-the-loop)
10. [Multi-Agent Patterns](#multi-agent-patterns)
11. [Streaming](#streaming)
12. [Testing](#testing)
13. [Observability](#observability)
14. [Model Support](#model-support)
15. [Migration Notes](#migration-notes)

---

## Agent Definition

An `Agent` is the central abstraction — it wraps a model, system prompt, tools, output type, and dependencies.

```python
from pydantic_ai import Agent

agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    system_prompt='You are a helpful customer service agent.',
    result_type=str,        # or a Pydantic model
    retries=3,              # auto-retry on validation failure
)

result = await agent.run('How do I return a product?')
print(result.output)        # typed as str
print(result.usage())       # token counts
```

**System prompts** can be static strings or dynamic functions:

```python
@agent.system_prompt
async def add_context(ctx: RunContext[MyDeps]) -> str:
    user = await ctx.deps.db.get_user(ctx.deps.user_id)
    return f'Current user: {user.name}, plan: {user.plan}'
```

---

## Tool Use

Tools are Python functions registered via decorators. Two types:

- `@agent.tool` — receives `RunContext` (access to deps, retry count, etc.)
- `@agent.tool_plain` — plain function, no context needed

```python
from pydantic_ai import Agent, RunContext

agent = Agent('openai:gpt-4o', deps_type=DatabaseConn)

@agent.tool
async def lookup_order(ctx: RunContext[DatabaseConn], order_id: str) -> str:
    """Look up order status by ID."""
    order = await ctx.deps.get_order(order_id)
    return f'Order {order_id}: {order.status}, shipped: {order.shipped_date}'

@agent.tool_plain
def calculate_refund(price: float, days_since_purchase: int) -> float:
    """Calculate refund amount based on return policy."""
    if days_since_purchase <= 30:
        return price
    elif days_since_purchase <= 60:
        return price * 0.5
    return 0.0
```

**Toolsets**: Tools are organized into `toolsets` — modular collections that can be combined. MCP servers are one type of toolset.

**Tool validation** (v1.63.0+): Use `args_validator` for pre-execution argument checks.

---

## Structured Outputs

Use `result_type` with Pydantic models for type-safe, validated outputs:

```python
from pydantic import BaseModel

class TicketResponse(BaseModel):
    answer: str
    confidence: float  # 0.0 to 1.0
    sources: list[str]
    needs_escalation: bool

agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    result_type=TicketResponse,
    retries=3,  # retries if output fails validation
)

result = await agent.run('Customer asks about refund policy')
response: TicketResponse = result.output  # fully typed
if response.needs_escalation:
    await escalate(response)
```

The model auto-retries when the LLM output doesn't match the schema — the validation error is sent back to the model as feedback.

**Streamed structured output**: Pydantic AI supports token-by-token streaming with immediate validation as data arrives.

---

## Dependencies

`deps_type` enables dependency injection (like FastAPI's `Depends`):

```python
from dataclasses import dataclass

@dataclass
class ServiceDeps:
    db: DatabasePool
    http_client: httpx.AsyncClient
    user_id: str

agent = Agent(
    'openai:gpt-4o',
    deps_type=ServiceDeps,
    result_type=TicketResponse,
)

# At runtime
async with httpx.AsyncClient() as client:
    deps = ServiceDeps(db=pool, http_client=client, user_id='user-123')
    result = await agent.run('Check my order status', deps=deps)
```

Tools access deps via `RunContext[ServiceDeps]` — full type checking and IDE auto-completion.

---

## MCP Integration

Pydantic AI has first-class MCP support. MCP servers are registered as **toolsets** on agents.

**Three transport types** (StreamableHTTP preferred, SSE deprecated):

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE, MCPServerStreamableHTTP

# Streamable HTTP — preferred transport for remote servers
api_server = MCPServerStreamableHTTP('http://localhost:3002/mcp')

# Stdio — runs MCP server as a subprocess (local tools)
docs_server = MCPServerStdio('python', args=['docs_mcp_server.py'], timeout=10)

# SSE — deprecated, use StreamableHTTP for new projects
search_server = MCPServerSSE('http://localhost:3001/sse')

# Combine multiple MCP servers as toolsets
agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    toolsets=[docs_server, search_server, api_server],
)

# Context manager handles connection lifecycle
async with agent:
    result = await agent.run('Search docs for refund policy')
```

**Load from config file**:

```python
from pydantic_ai.mcp import load_mcp_servers

servers = load_mcp_servers('mcp_config.json')
agent = Agent('openai:gpt-4o', toolsets=list(servers.values()))
```

**Pydantic AI as MCP server**: Agents can also expose their tools as MCP servers, allowing other MCP clients to connect to them.

---

## A2A Protocol Support

Native support for Google's Agent-to-Agent (A2A) open standard — agents interoperate across frameworks and vendors.

**Expose an agent as an A2A server**:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='Customer service bot')
app = agent.to_a2a()
# Run with: uvicorn my_module:app --host 0.0.0.0 --port 8000
```

`to_a2a()` returns an ASGI application (compatible with uvicorn, any ASGI server).

**FastA2A**: A separate Pydantic library (`fasta2a` on PyPI) built on Starlette that provides the underlying A2A server implementation. Supports pluggable **Storage**, **Broker**, and **Worker** components.

**Architecture**: Storage separates A2A-protocol-format task storage from internal conversation context — agents maintain rich internal state while exposing only A2A-compliant messages externally.

---

## pydantic-graph (FSM Workflows)

`pydantic-graph` is a type-centric library for building finite state machines, bundled with Pydantic AI. Each `Agent` internally uses pydantic-graph for its execution flow.

**Core concepts**:

- **Nodes**: Define logic and outgoing edges via return type annotations
- **Edges**: Type-checked transitions (the compiler catches invalid flows)
- **State persistence**: Snapshots before/after each node for durability

**Built-in node types**: `UserPromptNode`, `ModelRequestNode`, `CallToolsNode`, `End`

**State persistence implementations**:

| Implementation | Storage | Use Case |
|---|---|---|
| `SimpleStatePersistence` | In-memory (latest only) | Dev/testing |
| `FullStatePersistence` | In-memory (all snapshots) | Debugging, replay |
| `FileStatePersistence` | JSON files | Simple production, recovery |

State persistence enables interruption and resumption — the graph run can resume from any node. This is the foundation for HITL workflows and crash recovery.

---

## Durable Execution

Agents preserve progress across crashes, API failures, and restarts. Three first-party integrations:

**Temporal** — wraps agent as workflow activities:

```python
from pydantic_ai.durable_exec.temporal import TemporalAgent, PydanticAIWorkflow
from temporalio import workflow

agent = Agent('openai:gpt-4o', instructions='...', name='support')
temporal_agent = TemporalAgent(agent)

@workflow.defn
class SupportWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [temporal_agent]
    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await temporal_agent.run(prompt)
        return result.output
```

**DBOS** — checkpoints to database (SQLite/Postgres):

```python
from pydantic_ai.durable_exec.dbos import DBOSAgent
dbos_agent = DBOSAgent(agent)
result = await dbos_agent.run('prompt')
```

**pydantic-graph persistence** — file-based or in-memory state snapshots for simpler use cases.

**Note**: `run_stream()` is NOT supported in Temporal/DBOS workflows — use `event_stream_handler` instead.

**What this means in practice**:

- API timeout mid-conversation → resume from last successful step
- Server restart → reload state from persistence, continue
- Human approval needed → persist state, wait, resume when approved

---

## Human-in-the-Loop

Use `approval_required()` on any toolset. When a tool needs approval, the agent returns `DeferredToolRequests` instead of executing.

```python
from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults

# Flag tools requiring approval (based on tool name, args, or context)
approval_toolset = my_toolset.approval_required(
    lambda ctx, tool_def, tool_args: tool_def.name.startswith('dangerous')
)

agent = Agent(
    'openai:gpt-4o',
    toolsets=[approval_toolset],
    output_type=[str, DeferredToolRequests],
)

# First run — agent returns deferred requests
result = agent.run_sync('Do the dangerous thing')
# result.output is DeferredToolRequests with .approvals list

# Second run — pass approval decisions back
result = agent.run_sync(
    message_history=result.all_messages(),
    deferred_tool_results=DeferredToolResults(
        approvals={
            'tool_call_id_1': True,   # approved
            'tool_call_id_2': False,  # denied
        }
    )
)
```

The approval callback receives `(ctx, tool_def, tool_args)` and returns `bool`. Denied calls get error responses sent back to the model.

**Use cases**: Financial transactions, PII handling, high-risk tool calls, compliance gates.

---

## Multi-Agent Patterns

**Delegation**: One agent calls another as a tool:

```python
support_agent = Agent('openai:gpt-4o', system_prompt='You handle support')
billing_agent = Agent('openai:gpt-4o', system_prompt='You handle billing')

@support_agent.tool
async def escalate_to_billing(ctx: RunContext[Deps], issue: str) -> str:
    """Escalate billing issues to the billing specialist."""
    result = await billing_agent.run(issue, deps=ctx.deps)
    return result.output
```

**A2A for cross-framework**: Use `to_a2a()` to expose agents as A2A endpoints — other agents (even non-Pydantic AI) can call them.

**Orchestration patterns**:

- **Agent-as-tool**: Register one agent as a tool on another (simple delegation)
- **Sequential pipeline**: Chain agents via application code
- **A2A mesh**: Expose each agent as an A2A server, route via protocol

---

## Streaming

```python
async with agent.run_stream('Explain our return policy') as stream:
    async for chunk in stream.stream_text():
        print(chunk, end='', flush=True)

# Streamed structured output — validates as tokens arrive
async with agent.run_stream('Analyze this ticket', result_type=Analysis) as stream:
    async for partial in stream.stream_output():
        update_ui(partial)  # partial Pydantic model, validated incrementally
```

---

## Testing

Pydantic AI provides test doubles that avoid calling real LLMs:

```python
from pydantic_ai.models.test import TestModel, FunctionModel

# TestModel — returns predictable outputs
with agent.override(model=TestModel()):
    result = await agent.run('test prompt')
    assert result.output == expected  # deterministic

# FunctionModel — custom logic for complex test scenarios
def mock_response(messages, info):
    if 'refund' in messages[-1].content:
        return 'Processing refund...'
    return 'How can I help?'

with agent.override(model=FunctionModel(mock_response)):
    result = await agent.run('I need a refund')
```

**pydantic_evals**: Built-in evaluation framework for systematic agent testing:

- Dataset management (define test cases with expected outputs)
- CLI for running eval suites
- Logfire visualization of results

---

## Observability

**Built-in OpenTelemetry support**: Pydantic AI emits spans for model calls, tool calls, and agent runs.

**Pydantic Logfire**: First-party observability platform with deep integration:

- Real-time trace visualization
- Token usage tracking
- Tool call monitoring
- Cost tracking per agent/model

OpenTelemetry spans follow GenAI semantic conventions — compatible with any OTel backend (Datadog, New Relic, Grafana, etc.).

---

## Model Support

20+ LLM providers via a unified interface:

| Provider | Models | Notes |
|---|---|---|
| OpenAI | GPT-4o, GPT-4o-mini, o1, o3, GPT-5.2 | Full support |
| Anthropic | Claude Sonnet 4, Claude Haiku, Opus | Full support |
| Google | Gemini 3.1 Pro, Gemini Flash | Including image models |
| Qwen | Qwen 3.5 | Native structured output (v1.66.0+) |
| Groq | Llama, Mixtral | Via OpenAI-compatible API |
| Ollama | Local models | Via OpenAI-compatible API |

---

## Migration Notes

### From LangGraph

| LangGraph Concept | Pydantic AI Equivalent |
|---|---|
| `StateGraph` | `pydantic-graph` nodes + edges |
| `add_node()` / `add_edge()` | Type-annotated return types |
| `ToolNode` | `@agent.tool` / `@agent.tool_plain` |
| State channels | `deps_type` + `RunContext` |
| Checkpointer | State persistence (`FileStatePersistence`) |
| LangSmith | Pydantic Logfire / OpenTelemetry |

### From CrewAI

| CrewAI Concept | Pydantic AI Equivalent |
|---|---|
| `Crew` | Application-level orchestration |
| `Agent` (role-based) | `Agent` with system prompt |
| `Task` | Agent run with specific prompt |
| `Tool` | `@agent.tool` decorator |

---

## Decision: When to Use Pydantic AI

**Choose Pydantic AI when**:

- Type safety and IDE support matter (team uses mypy/pyright)
- You need native MCP + A2A interoperability
- Your stack is already Pydantic/FastAPI
- You want durable execution without heavy infrastructure
- You need streamed structured outputs

**Choose something else when**:

- You need visual workflow editing → LangGraph
- Fastest possible MVP → OpenAI Agents SDK or CrewAI
- Google Cloud / Vertex AI native → Google ADK
- Enterprise AWS managed → Bedrock Agents
