# Modern Best Practices — Current Production Standards

**Purpose**: Production-ready patterns aligned with 2025-2026 industry standards (MCP, A2A, NIST AI RMF, OpenTelemetry GenAI).

**March 2026 Updates**: 14-framework landscape (Claude Agent SDK, MS Agent Framework, LlamaIndex, Mastra, SmolAgents, Agno, Haystack, DSPy added). MCP governance transferred to Agentic AI Foundation (Linux Foundation). Parallel execution patterns and model routing emerging. Pydantic AI v1.66.0 with native A2A and MCP toolsets.

---

## Model Context Protocol (MCP)

**What**: Open standard for connecting agents to tools and data sources (adopted by Anthropic, OpenAI, Google)

**Governance (Dec 2025)**: MCP donated to Agentic AI Foundation (AAIF), a Linux Foundation directed fund co-founded by Anthropic, Block, and OpenAI.

**When to use**: All new tool integrations (standardized replacement for custom APIs)

**Architecture**:
```yaml
MCP Host (AI App) → MCP Client → MCP Server
```

**Key Principles**:

- MCP is an integration layer, NOT an agent framework
- Complements LangChain/LangGraph/CrewAI (doesn't replace them)
- Use for: tool access, resource retrieval, prompt templates
- Security: Validate tool permissions, watch for prompt injection, verify tool signatures
- Tool design: Publish tasks (not raw APIs), keep granular, concise outputs, and explicit validation. Use structured content (references/prompts/roots) only when needed.
- Threats: Tool shadowing, malicious tool definitions/contents, over-broad scopes, Confused Deputy. Mitigate with scopes, signatures, schema validation, and policy checks.
- Message types: JSON-RPC with tool definitions, tool results, errors, structured content; standardize transports and fail closed on unknown methods.

**Security Concerns (April 2025 Disclosure)**:

- Prompt injection via tool descriptions
- Tool permissions allowing file exfiltration when combined
- Lookalike tools silently replacing trusted ones
- Mitigation: SAST/SCA pipelines, schema validation, signature verification

**Top MCP Servers (2026)**: K2view, Vectara, Zapier, Notion, Supabase, Pinecone, Salesforce

**Implementation Resources**:
- [`mcp-practical-guide.md`](mcp-practical-guide.md) - Copy-paste MCP server examples
- [`tool-design-specs.md`](tool-design-specs.md) - MCP implementation patterns
- [`protocol-decision-tree.md`](protocol-decision-tree.md) - When to use MCP vs A2A

---

## Agent-to-Agent Protocol (A2A)

**What**: Standardized protocol for agent-to-agent communication, coordination, and task delegation

**When to use**: Multi-agent systems, task delegation, collaborative workflows, agent orchestration

**Architecture**:
```yaml
Agent A (Sender) → A2A Message → Agent B (Receiver)
   ↓                                      ↓
Validates payload            Executes task + returns result
```

**Key Principles**:

- Treat handoffs as versioned APIs with strict JSON Schema validation
- Always propagate `trace_id` for full observability across agent chains
- Include agent cards for capability discovery and dynamic routing
- Support async communication patterns with error recovery
- Validate input/output schemas on every handoff

**Core Message Schema**:
```json
{
  "schemaVersion": "v1.2",
  "trace_id": "req-abc-123",
  "sender": {"agent_id": "...", "agent_type": "..."},
  "receiver": {"agent_id": "...", "agent_type": "..."},
  "task": {"type": "...", "description": "..."},
  "context": {...},
  "constraints": {...}
}
```

**Orchestration Patterns**:

- **Sequential**: A → B → C (linear handoff chain)
- **Manager-Worker**: Manager delegates subtasks to specialized workers
- **Group Chat**: Collaborative multi-agent discussion
- **Handoff**: Dynamic delegation based on context and capabilities

**Critical Insight**: Most agent failures are handoff/context-transfer issues, not model issues. Validation required.

**Implementation Resources**:
- [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) - Implementation patterns
- [`protocol-decision-tree.md`](protocol-decision-tree.md) - MCP vs A2A selection
- [`multi-agent-patterns.md`](multi-agent-patterns.md) - Orchestration templates

---

## ADK Implementation Notes

**Parent/Child Agents**: Use coordinator agents to delegate to specialized sub-agents; keep clear descriptions and instructions for routing.

**Custom Agents**: Extend BaseAgent for non-LLM behaviors; emit events and respect invocation context.

**Aggregation**: Use evaluators/majority vote when combining parallel agent outputs.

**Exceptions**: Implement error-handling patterns for tool/agent failures; degrade gracefully and surface traces.

---

## Agentic RAG (Dynamic Retrieval)

**What**: Multi-step retrieval with query rewriting, hybrid search, and optional chunk context augmentation (validate on your corpus).

**Pattern**:
```text
query → rewrite → embed → retrieve → contextual_rerank → filter → inject → cite
```

**Contextual Retrieval** (Anthropic 2024):

- Add context to each chunk before embedding
- Combine semantic (embeddings) + keyword (BM25)
- Mandatory reranking step
- 200-400 token chunks
- Route queries by domain first

**Old vs New**:
- **Old**: Static one-shot retrieval
- **New**: Iterative retrieval with adaptation

**Implementation Resources**:
- [`rag-patterns.md`](rag-patterns.md) - Contextual retrieval implementation
- [`../assets/rag/rag-advanced.md`](../assets/rag/rag-advanced.md) - Production template

---

## Handoff-First Orchestration

**What**: Treat agent handoffs as versioned APIs with strict validation

**Critical Insight**: Most agent failures are handoff/context-transfer issues, not model issues

**Best Practices**:
```yaml
handoff_payload:
  schemaVersion: "v1.2"
  trace_id: "abc-123"
  context: {validated_json}
  task: {atomic_instruction}
  constraints: {hard_limits}
```

**Patterns**:

- **Sequential**: A → B → C (linear pipeline)
- **Handoff**: Dynamic delegation based on context
- **Group Chat**: Collaborative multi-agent discussion
- **Magentic**: Manager coordinates specialized workers

**Validation**: JSON Schema required for every handoff

**Implementation Resources**:
- [`a2a-handoff-patterns.md`](a2a-handoff-patterns.md) - Handoff protocols
- [`multi-agent-patterns.md`](multi-agent-patterns.md) - Orchestration templates

---

## Multi-Layer Guardrails

**What**: Defense-in-depth for production safety (NIST AI RMF, OWASP GenAI Top 10)

**Required Layers**:

1. **Input validation**: PII redaction, content filtering, prompt injection detection
2. **RBAC/ABAC**: Fine-grained authorization per tool/action
3. **Tool gating**: Signature verification (Sigstore/Cosign), human approval for high-risk
4. **Output filtering**: PII detection, policy checks, compliance validation
5. **Observability**: OpenTelemetry GenAI spans, SIEM integration, real-time alerts

**Human-in-the-Loop Required For**:

- Financial transactions
- Database modifications
- Legal/compliance actions
- Irreversible operations

**Implementation Resources**:
- [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) - Complete guardrails implementation
- [`../ai-mlops/`](../../ai-mlops/SKILL.md) - Security patterns

---

## Agent Framework Landscape (2026)

**What**: Multiple production-grade frameworks now compete for different use cases

### Framework Comparison (March 2026)

**Tier 1 — Production-Grade**

| Framework | Architecture | Best For | Languages | Ease |
|-----------|--------------|----------|-----------|------|
| **LangGraph** | Graph-based, stateful | Enterprise, compliance, auditability | Python, JS | Medium |
| **Claude Agent SDK** | Event-driven, tool-centric | Anthropic ecosystem, Computer Use, MCP-native | Python, TS | Easy |
| **OpenAI Agents SDK** | Tool-centric, lightweight | Fast prototyping, OpenAI ecosystem | Python | Easy |
| **Google ADK** | Code-first, multi-language | Gemini/Vertex AI, polyglot teams | Python, TS, Go, Java | Medium |
| **Pydantic AI** | Type-safe, graph FSM | Production Python, type safety, MCP+A2A native | Python | Medium |
| **MS Agent Framework** | Kernel + multi-agent | Enterprise Azure, .NET/Java teams | Python, .NET, Java | Medium |

**Tier 2 — Specialized**

| Framework | Architecture | Best For | Languages | Ease |
|-----------|--------------|----------|-----------|------|
| **LlamaIndex** | Event-driven workflows | RAG-native agents, retrieval-heavy | Python, TS | Medium |
| **CrewAI** | Role-based crews | Team workflows, content generation | Python | Easiest |
| **Mastra** | Vercel AI SDK-based | TypeScript/Next.js teams | TypeScript | Easy |
| **SmolAgents** | Code-first, minimalist | Lightweight, fewer LLM calls (~30%) | Python | Easy |
| **Agno** | FastAPI-native runtime | Production Python, 100+ integrations | Python | Easy |
| **AWS Bedrock Agents** | Managed infrastructure | Enterprise AWS, knowledge bases | Python | Easy |

**Tier 3 — Niche**: Haystack (enterprise RAG+agents pipeline), DSPy (declarative prompt optimization)

### LangGraph (Recommended for Production)

**Why**: LangChain team recommends LangGraph for all new production agents

**Benefits**:

- Durable runtime with state persistence
- Visual workflow graphs
- Built-in checkpoints and error recovery
- Native observability with LangSmith
- Lowest latency in benchmarks

### OpenAI Agents SDK (New March 2025)

**What**: Lightweight, production-ready upgrade from experimental Swarm project

**Benefits**:

- Super easy onboarding (few lines of code)
- Provider-agnostic (100+ LLMs via OpenAI-compatible APIs)
- Strong in agent handoffs
- Well-documented

**Limitations**: No built-in rollback semantics, simpler error recovery than LangGraph

**Pattern**: Some teams use "OpenAI SDK with LangGraph" for best of both worlds

### Google ADK (Agent Development Kit)

**What**: Code-first, model-agnostic framework optimized for Gemini

**Languages**: Python, TypeScript, Go, Java (all actively maintained)

**Benefits**:

- Gemini 3 Pro/Flash support
- Multi-agent hierarchies
- Vertex AI Agent Engine deployment
- Interactions API integration

### Pydantic AI

**What**: Type-safe Python agent framework from the Pydantic team. FastAPI-style DX for GenAI.

**Version**: v1.66.0 (March 2026) | V1.0.0 GA: September 2025

**Benefits**:

- Full type safety (IDE auto-completion, write-time error detection)
- First-class MCP client: `MCPServerStdio`, `MCPServerSSE`, `MCPServerStreamableHTTP` — also acts as MCP server
- Native A2A support: `agent.to_a2a()` returns an ASGI app for agent-to-agent interoperability
- Human-in-the-loop via pydantic-graph interruption and state persistence
- Durable execution (survives API failures, restarts) with Prefect integration
- pydantic-graph for FSM workflows with type-checked edges
- `pydantic_evals` for systematic agent testing (datasets, CLI, Logfire visualization)
- `TestModel` / `FunctionModel` for deterministic testing without LLM calls
- OpenTelemetry + Pydantic Logfire for observability
- 20+ LLM providers (OpenAI, Anthropic, Google Gemini 3.1, Qwen 3.5, Groq, Ollama)

**Status**: Production-stable, rapid iteration (v1.0 → v1.66 in 6 months). V2 planned April 2026+.

**Deep dive**: [`pydantic-ai-patterns.md`](pydantic-ai-patterns.md) — full implementation patterns, code examples, migration guides

### Claude Agent SDK (Sep 2025)

**What**: Official Anthropic agent SDK. Functional API (not class-based) — agents defined via `query()` with options. Powers Claude Code. 1.85M+ weekly npm downloads.

**Benefits**:

- Built-in tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch, Task (subagents)
- Custom tools as in-process MCP servers via `tool()` + `create_sdk_mcp_server()`
- 18-event hook system (`PreToolUse`, `PostToolUse`, `PermissionRequest`, etc.) for guardrails
- Computer Use support with sandboxed environments
- Subagents via `AgentDefinition` with parallel execution

**Languages**: Python (v0.1.47), TypeScript (v0.2.69)

**Deep dive**: [`claude-agent-sdk-patterns.md`](claude-agent-sdk-patterns.md) — full API patterns, hooks, multi-agent, testing

### Microsoft Agent Framework (RC Feb 2026, GA Q1 2026)

**What**: Unified framework merging Semantic Kernel + AutoGen (both now in maintenance mode). Graph-based workflows for multi-agent orchestration.

**Benefits**:

- Python, .NET (C#) at RC; Java on roadmap — broadest enterprise language support
- Graph-based workflow composition (sequential, concurrent, handoff, group chat)
- Session-based state management, middleware pipeline, telemetry
- Deep Azure AI Foundry / Azure OpenAI integration
- Few-lines-of-code agent creation with type-safe tool definitions

**Note**: Existing AutoGen/Semantic Kernel projects require migration. API surface consolidated around `agent.run()` / `client.get_response()`.

### LlamaIndex Workflows (v2.15.0)

**What**: Event-driven, async-first workflow engine for RAG-native agents. 35k+ GitHub stars.

**Benefits**:

- Strongest retrieval foundation — purpose-built for RAG-heavy agents
- Serializable workflow state (pause/resume) with AgentWorkflow for multi-agent orchestration
- LlamaAgents Builder: natural-language-to-agent-workflow generation
- `llama-agents` for microservice-based multi-agent deployment
- Python and TypeScript SDKs

**Note**: Event-driven paradigm has a steeper learning curve than imperative approaches. Non-RAG use cases can feel like fighting the framework.

### Tier 2 Highlights

- **CrewAI**: Role-based crews, easiest onboarding, best for fast prototyping
- **Mastra** (v1.9.0): TypeScript-first (Gatsby team, $13M seed YC W25), built on Vercel AI SDK. Observational memory, 40+ LLM providers, built-in eval primitives. Leading choice for Next.js teams
- **SmolAgents** (v1.23.0): HuggingFace's ~1000-line minimalist framework, code-first (writes Python not JSON tool calls), ~30% fewer LLM calls. Multimodal. Hub integration for sharing agents/tools
- **Agno** (v2.4.0, formerly Phidata): FastAPI-native runtime, ~50x lower memory than LangGraph, ~10,000x faster instantiation. 100+ integrations, built-in memory/knowledge bases/guardrails
- **AWS Bedrock Agents**: Managed infrastructure with knowledge bases, action groups, and enterprise AWS integration

### Tier 3

- **Haystack** (deepset, v2.12.0): Pipeline-as-directed-multigraph with Agent component, AsyncPipeline for parallel execution. Used by Airbus, Economist, NVIDIA
- **DSPy** (Stanford, v2.6.x): "Programming, not prompting" — optimizers (MIPROv2, BootstrapFewShot) compile signatures into prompts/weights. ReAct agent module for tool use. Documented 24%→51% accuracy improvements

### Framework Selection Guide

```text
Which framework?
    ├─ MVP/Prototyping?
    │   ├─ Python → OpenAI Agents SDK or CrewAI
    │   └─ TypeScript → Mastra or Claude Agent SDK
    ├─ Production →
    │   ├─ Auditability/compliance? → LangGraph
    │   ├─ Type safety + MCP/A2A native? → Pydantic AI
    │   ├─ Anthropic models + Computer Use? → Claude Agent SDK
    │   ├─ Google Cloud / Gemini? → Google ADK
    │   ├─ Azure / .NET / Java? → MS Agent Framework
    │   ├─ AWS managed? → Bedrock Agents
    │   └─ RAG-heavy? → LlamaIndex Workflows
    ├─ Minimalist / Research →
    │   ├─ Fewest LLM calls? → SmolAgents
    │   └─ Optimize prompts automatically? → DSPy
    └─ Enterprise pipeline → Haystack
```

**Resources**: See [`../data/sources.json`](../data/sources.json) for documentation links

---

## OpenTelemetry for Agents

**What**: Standardized observability using OpenTelemetry GenAI semantic conventions

**Required Telemetry**:
```yaml
spans:
  - llm_call: {prompt, response, tokens, latency}
  - tool_call: {name, params, result, duration}
  - retrieval: {query, chunks, scores}
  - memory_op: {read/write, key, size}
```

**Metrics to Track**:

- Tool success rate ≥95%
- Average latency < target
- Token cost < budget
- Evaluation score ≥ threshold
- Task success/containment rate ≥ target; escalation rate within budget
- User satisfaction or reviewer score tracked; flag drift in response quality
- Instrument like A/B experiments: track goal completion time, cost, and quality deltas across variants

**Platforms**: Azure AI Foundry, LangSmith, Arize, New Relic, Datadog

**Implementation Resources**:
- [`evaluation-and-observability.md`](evaluation-and-observability.md) - Complete observability guide
- [`../qa-observability/`](../../qa-observability/SKILL.md) - OpenTelemetry patterns

---

## Service & Transport Layer (API Frontends)

**What**: HTTP/gRPC/GraphQL contracts for agent endpoints

**Best Practices**:

- Use [`../dev-api-design/`](../../dev-api-design/SKILL.md) for HTTP/gRPC/GraphQL contracts, auth, rate limits, error shapes
- Expose agent endpoints with: `trace_id`, scopes/roles, tool allowlist, safety level, delivery mode (sync/stream/async)
- Prefer SSE/WebSocket for token streams; 202 + polling for long jobs; HMAC-signed webhooks for callbacks
- Standardize errors: model_timeout, tool_failed, guardrail_blocked, retrieval_miss, validation_error, quota_exceeded
- Observability: propagate `traceparent`; emit spans for llm_call, retrieval, tool_call; include rate-limit headers
- MTTD (Mean Time To Detect) for anomalies

**Implementation Resources**:
- [`api-contracts-for-agents.md`](api-contracts-for-agents.md) - Request/response envelopes, safety gates
- [`../../dev-api-design/assets/fastapi/`](../../dev-api-design/assets/fastapi/) - FastAPI templates

---

## Code/SWE Agents (SE 3.0)

**What**: Autonomous coding agents that perform end-to-end software engineering tasks

**Scale**: 400,000+ PRs created by OpenAI Codex alone within 2 months (May 2025)

**SE 3.0 Paradigm**: Intent-driven, conversational development where developers collaborate with autonomous AI teammates

**Architecture Patterns**:

- **Multi-Agent SWE** (HyperAgent): Planner → Navigator → Code Editor → Executor
- **Minimal Agent** (Lita/Mini-SWE): 100-line implementation achieving 68% of full-agent performance

**Critical Finding**: 29.6% of "plausible" SWE-Bench fixes introduce behavioral regressions

**Implication**: Test passing is insufficient; production deployments require:

- Behavioral regression testing
- Human code review
- Integration testing beyond unit tests
- Semantic diff analysis

**Guardrails for Code Agents**:

```yaml
execution_limits:
  max_steps: 50
  max_file_edits: 20
  timeout_minutes: 30

forbidden_operations:
  - delete_repository
  - force_push
  - modify_ci_config
  - access_secrets

review_triggers:
  - changes_to_security_files
  - more_than_10_files_modified
```

**Implementation Resources**:

- [`code-swe-agents.md`](code-swe-agents.md) - Complete patterns and architecture
- [`../data/sources.json`](../data/sources.json) - Research papers (SE 3.0, HyperAgent)

---

## Parallel Execution & Model Routing (2026 Trends)

**Parallel Execution**:

- Cursor now runs up to 8 agents in parallel
- Apps like Conductor and Verdent AI support background task execution
- Pattern: Define task, let LLM execute in background, start new task

**Model Routing / Cooperative Systems**:

- Smaller models handle routine tasks, delegate to larger models when needed
- Cost optimization through intelligent model selection
- "Whoever nails system-level integration will shape the market"

**Market Context**: Gartner predicts agents entering "trough of disillusionment" in 2026. Focus on operationalization over demos.

---

## Key Modern Migrations

**Traditional → Modern**:

- Custom APIs → Model Context Protocol (MCP)
- Static RAG → Agentic RAG with contextual retrieval
- Ad-hoc handoffs → Versioned handoff APIs with JSON Schema
- Single guardrail → Multi-layer defense (5+ layers)
- LangChain agents → LangGraph stateful workflows
- Custom observability → OpenTelemetry GenAI standards
- Model-centric → Context engineering-centric
- Code completion → Autonomous SWE agents (SE 3.0)
- Single framework → Framework selection by use case (2026)
- Sequential execution → Parallel agent execution

---

## Usage Notes

- **Default to modern standards**: MCP for tools, agentic RAG for retrieval, handoff-first for multi-agent
- **Reference specialized skills** for deep implementation (see Related Skills in main SKILL.md)
- **Use templates** for structured artifacts (see Navigation: Templates in main SKILL.md)
