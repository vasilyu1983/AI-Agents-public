# AgentOps Patterns

Operational framework for managing autonomous AI agents in production — the evolution of MLOps for agentic systems.

---

## Overview

**AgentOps** (Agent Operations) is an emerging discipline focused on the lifecycle management of autonomous AI agents. As AI agents become more sophisticated and prevalent in production environments, traditional MLOps practices are insufficient for their unique operational requirements.

**Why AgentOps matters:**
- Agents exhibit unpredictable execution paths
- Multi-agent systems have complex interaction patterns
- Output quality varies based on context and tool usage
- Behavior can shift over time without model changes
- Traditional monitoring misses agent-specific failure modes

**Market context:** The AI agents market is projected to grow from ~$5B (2024) to ~$50B by 2030.

---

## AgentOps vs MLOps vs LLMOps

| Aspect | MLOps | LLMOps | AgentOps |
|--------|-------|--------|----------|
| **Primary artifact** | Model weights | Prompts + model | Agent graph + tools |
| **Execution** | Deterministic inference | Single LLM call | Multi-step reasoning |
| **Observability** | Metrics (latency, accuracy) | Token usage, evals | Session traces, tool calls |
| **Failure modes** | Data drift, model decay | Hallucination, refusal | Loop failures, tool errors |
| **Versioning** | Model versions | Prompt versions | Agent graph + tool versions |
| **Testing** | Unit tests, A/B tests | Eval suites | Scenario simulations |

---

## Core AgentOps Capabilities

### 1. Session Tracing & Replay

Track complete agent execution paths with point-in-time precision.

**What to capture:**
- LLM calls (input, output, tokens, latency)
- Tool invocations (name, arguments, results)
- Multi-agent handoffs and delegations
- Decision points and reasoning steps
- Error states and recovery attempts

**Implementation:**
```python
import agentops

# Initialize at agent startup
agentops.init(api_key="your-api-key")

# Automatic instrumentation captures:
# - All LLM calls
# - Tool usage
# - Agent state transitions
# - Cost and latency metrics
```

### 2. Cost & Latency Tracking

Monitor resource consumption across agent sessions.

**Key metrics:**
- Token usage per session (input, output, total)
- Cost per agent run (model-weighted)
- Latency per step and end-to-end
- Tool call frequency and duration
- Cache hit rates

**Example dashboard metrics:**
```
session_token_cost{agent="support-bot", model="gpt-4"} 0.15
session_latency_p99{agent="support-bot"} 12.5s
tool_invocations_total{tool="search", agent="support-bot"} 342
```

### 3. Multi-Agent Visualization

Understand complex agent interactions and delegation patterns.

**Visualization types:**
- Execution flow diagrams
- Agent communication graphs
- Tool dependency maps
- State transition timelines

### 4. Debugging & Root Cause Analysis

Drill into specific spans to diagnose failures.

**Debug workflow:**
1. Identify failing session from alerts
2. Replay session with full context
3. Inspect tool call arguments and responses
4. Trace reasoning chain to failure point
5. Reproduce in isolated environment

---

## AgentOps Tools & Platforms

### Dedicated AgentOps Platforms

| Tool | Type | Key Features | Best For |
|------|------|--------------|----------|
| **[AgentOps.ai](https://www.agentops.ai/)** | SaaS | Session replay, cost tracking, CrewAI/LangGraph integration | Python-first teams |
| **[Langfuse](https://langfuse.com/)** | OSS/SaaS | Tracing, evals, prompt management, OpenTelemetry | Open-source preference |
| **[LangSmith](https://smith.langchain.com/)** | SaaS | LangChain native, playground, datasets | LangChain users |
| **[IBM watsonx AgentOps](https://www.ibm.com/think/topics/agentops)** | Enterprise | OpenTelemetry-based, enterprise governance | Regulated industries |
| **[Arize AI](https://arize.com/)** | SaaS | ML/LLM observability, drift detection, tracing | Full-stack observability |
| **[Braintrust](https://www.braintrust.dev/)** | SaaS | Evals, logging, prompt playground | Eval-focused teams |

### Agent Frameworks with Built-in Observability

| Framework | Observability | Integration |
|-----------|---------------|-------------|
| **CrewAI** | Native AgentOps support | 2-line setup |
| **LangGraph** | LangSmith native | Automatic tracing |
| **OpenAI Agents SDK** | AgentOps compatible | SDK integration |
| **Autogen/AG2** | AgentOps supported | Direct integration |
| **LlamaIndex** | Multiple backends | Pluggable tracing |

---

## Implementation Patterns

### Pattern 1: Minimal AgentOps Setup

For quick observability with CrewAI:

```python
import agentops
import os

# Set API key
os.environ["AGENTOPS_API_KEY"] = "your-api-key"

# Automatic instrumentation - no code changes to agents
agentops.init()

# Your CrewAI code runs as normal
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find relevant information",
    backstory="Expert researcher"
)

# All LLM calls, tool usage automatically tracked
```

### Pattern 2: OpenTelemetry-Based Tracing

Enterprise-grade approach (IBM watsonx pattern):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Initialize tracer
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="your-collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent-service")

# Instrument agent execution
def run_agent(user_input: str):
    with tracer.start_as_current_span("agent_session") as session_span:
        session_span.set_attribute("user.input", user_input)

        with tracer.start_as_current_span("llm_call") as llm_span:
            response = llm.generate(user_input)
            llm_span.set_attribute("tokens.input", response.usage.input_tokens)
            llm_span.set_attribute("tokens.output", response.usage.output_tokens)
            llm_span.set_attribute("model", "claude-3-5-sonnet")

        with tracer.start_as_current_span("tool_call") as tool_span:
            tool_span.set_attribute("tool.name", "search")
            result = search_tool(response.content)
            tool_span.set_attribute("tool.result_length", len(result))
```

### Pattern 3: Langfuse Open-Source Setup

```python
from langfuse import Langfuse
from langfuse.decorators import observe

langfuse = Langfuse()

@observe()
def agent_step(input_text: str):
    # Automatically traced
    response = llm.generate(input_text)
    return response

@observe()
def run_agent(user_query: str):
    # Parent trace captures all nested calls
    step1 = agent_step(user_query)
    step2 = agent_step(f"Analyze: {step1}")
    return step2
```

---

## AgentOps Metrics & Alerts

### Core Metrics to Track

**Session-level:**
- `agent_session_duration_seconds` - End-to-end execution time
- `agent_session_cost_usd` - Total cost per session
- `agent_session_steps_total` - Number of reasoning steps
- `agent_session_success_rate` - Completion rate

**LLM-level:**
- `llm_tokens_total{type="input|output"}` - Token consumption
- `llm_latency_seconds` - Model response time
- `llm_error_rate` - API errors, rate limits

**Tool-level:**
- `tool_invocations_total{tool="name"}` - Tool usage frequency
- `tool_latency_seconds{tool="name"}` - Tool execution time
- `tool_error_rate{tool="name"}` - Tool failure rate

**Agent-specific:**
- `agent_loop_iterations` - Iterations before completion
- `agent_delegation_count` - Multi-agent handoffs
- `agent_retry_count` - Retry attempts

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Session cost | >$0.50 | >$2.00 | Cost cap, review agent |
| Session duration | >30s | >120s | Timeout, investigate loop |
| Tool error rate | >5% | >15% | Check tool availability |
| Loop iterations | >10 | >20 | Possible infinite loop |

---

## AgentOps Workflow Checklist

### Pre-Production

- [ ] Agent observability platform selected (AgentOps.ai, Langfuse, etc.)
- [ ] Session tracing enabled for all agent types
- [ ] Cost tracking configured with budgets
- [ ] Tool invocations instrumented
- [ ] Multi-agent interactions traced
- [ ] Baseline metrics established

### Production Monitoring

- [ ] Dashboards configured for key metrics
- [ ] Alerts set for cost spikes, latency, errors
- [ ] Session replay available for debugging
- [ ] Cost budgets enforced per agent/user
- [ ] Regular review of agent behavior patterns

### Incident Response

- [ ] Runbook for agent loop detection
- [ ] Runbook for cost spike investigation
- [ ] Runbook for tool failure cascades
- [ ] Session replay used for root cause analysis
- [ ] Post-incident analysis documents agent-specific failures

---

## OpenTelemetry Semantic Conventions for GenAI

The OpenTelemetry project defines standard attributes for GenAI observability:

**LLM Attributes:**
- `gen_ai.system` - Provider (openai, anthropic, etc.)
- `gen_ai.request.model` - Model name
- `gen_ai.usage.input_tokens` - Input token count
- `gen_ai.usage.output_tokens` - Output token count
- `gen_ai.response.finish_reason` - Completion reason

**Tool Attributes:**
- `gen_ai.tool.name` - Tool name
- `gen_ai.tool.call.id` - Unique call ID
- `gen_ai.tool.call.arguments` - Tool arguments (redacted if sensitive)

**Reference:** https://opentelemetry.io/docs/specs/semconv/gen-ai/

---

## Related Resources

- [LLM & RAG Production Patterns](llm-rag-production-patterns.md) - Production patterns for LLM systems
- [Monitoring Best Practices](monitoring-best-practices.md) - General ML monitoring
- [Incident Response Playbooks](incident-response-playbooks.md) - Incident handling
- [API Design Patterns](api-design-patterns.md) - Agent API design

---

## External References

- **AgentOps.ai:** https://docs.agentops.ai/
- **Langfuse:** https://langfuse.com/docs
- **LangSmith:** https://docs.smith.langchain.com/
- **IBM AgentOps:** https://www.ibm.com/think/topics/agentops
- **OpenTelemetry GenAI:** https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **Arize AI:** https://docs.arize.com/
