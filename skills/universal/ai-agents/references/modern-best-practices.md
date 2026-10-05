# Modern Best Practices — Current Production Standards

**Purpose**: Production-ready patterns aligned with current industry standards (MCP, A2A, NIST AI RMF, OpenTelemetry GenAI).

**Before recommending a vendor**: verify framework language support, transport guidance, authorization flows, pricing, and lifecycle claims against primary docs before making vendor recommendations.

---
## Table of Contents

- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
- [Agent-to-Agent Protocol (A2A)](#agent-to-agent-protocol-a2a)
- [ADK Implementation Notes](#adk-implementation-notes)
- [Agentic RAG (Dynamic Retrieval)](#agentic-rag-dynamic-retrieval)
- [Handoff-First Orchestration](#handoff-first-orchestration)
- [Multi-Layer Guardrails](#multi-layer-guardrails)
- [Agent Framework Landscape](#agent-framework-landscape)
- [OpenTelemetry for Agents](#opentelemetry-for-agents)
- [Service & Transport Layer (API Frontends)](#service--transport-layer-api-frontends)
- [Code/SWE Agents (SE 3.0)](#codeswe-agents-se-30)
- [Parallel Execution & Model Routing](#parallel-execution--model-routing)
- [Key Modern Migrations](#key-modern-migrations)
- [Usage Notes](#usage-notes)


## Model Context Protocol (MCP)

**What**: Open standard for connecting agents to tools, resources, and prompts.

**Governance**: MCP is an LF Projects, LLC project with individual (not company-seated) maintainers; A2A sits under the Agentic AI Foundation. Read <https://modelcontextprotocol.io/community/governance> before making claims about governance or membership.

**When to use**: Standardize tool and data access across hosts, models, and runtimes.

**Architecture**:
```yaml
MCP Host (AI App) → MCP Client → MCP Server
```

**Key Principles**:

- MCP is an integration layer, not an agent architecture.
- Use it for: tool access, resource retrieval, prompt templates, and shared capability boundaries.
- Default transports to `stdio` or Streamable HTTP; treat older SSE-only guidance as compatibility material, not the default.
- For remote MCP, use explicit authorization and least-privilege scopes; verify current OAuth/OIDC guidance in the spec.
- Tool design matters more than transport choice: publish narrow tasks, not raw backend complexity.
- Mark destructive or side-effectful tools clearly and validate all inputs/outputs against schema.
- Treat tool definitions and tool results as untrusted input; defend against prompt injection, tool shadowing, confused deputy, and over-broad scopes.
- Keep capability negotiation explicit and fail closed on unsupported methods or ambiguous contracts.

**Operational Concerns**:

- Prompt injection via tool descriptions or tool results
- Combined permissions enabling file or data exfiltration
- Lookalike tools silently replacing trusted ones
- Missing auth scopes or tenant boundaries on remote servers
- Mitigation: least privilege, schema validation, signature/publisher checks where available, and explicit policy checks

**Implementation Resources**:
- [`agents-mcp`](../../agents-mcp/SKILL.md) - MCP server builds and examples
- [`tool-design-specs.md`](tool-design-specs.md) - MCP implementation patterns
- [`protocol-decision-tree.md`](protocol-decision-tree.md) - When to use MCP vs A2A

---

## Agent-to-Agent Protocol (A2A)

**What**: Open protocol for agent-to-agent communication, task execution, and capability discovery between agentic applications. A2A was donated by Google to Linux Foundation governance. Before implementation, check the A2A spec site for the current version and each framework's docs for native A2A support; the answer decides whether you need an adapter.

**When to use**: Multi-agent systems, task delegation, agent cards/discovery, long-running tasks, and cross-runtime orchestration.

**Architecture**:
```yaml
Agent A (Sender) → A2A Message → Agent B (Receiver)
   ↓                                      ↓
Validates payload            Executes task + returns result
```

**Key Principles**:

- Treat handoffs as versioned APIs with strict schema validation.
- Always propagate `trace_id` or equivalent correlation metadata across handoffs.
- Use agent cards for capability discovery and routing, not natural-language guessing.
- Preserve ownership, timeout, retry, and escalation semantics at handoff boundaries.
- Support async task execution and explicit terminal states for long-running work.
- Validate input/output schemas and refusal/error envelopes on every handoff.

**Core Message Schema**:
```json
{
  "schemaVersion": "v1",
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

**Critical Insight**: Most multi-agent failures are handoff and context-transfer failures, not base-model failures.

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
- [`rag-patterns.md`](rag-patterns.md) - Agent-side retrieval rules and pointers into `ai-rag`
- [`../../ai-rag/references/contextual-retrieval-guide.md`](../../ai-rag/references/contextual-retrieval-guide.md) - Contextual retrieval implementation and validation

---

## Handoff-First Orchestration

**What**: Treat agent handoffs as versioned APIs with strict validation

**Critical Insight**: Most agent failures are handoff/context-transfer issues, not model issues

**Best Practices**:
```yaml
handoff_payload:
  schemaVersion: "v1"
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

## Agent Framework Landscape

Do not rank frameworks by hype or popularity. Pick by control flow, language, deployment target, auditability requirements, and how much of the runtime you want to own. The selection matrix, per-framework profiles, anti-patterns, and migration paths live in [`framework-landscape.md`](framework-landscape.md); verify current support matrices in [`../data/sources.json`](../data/sources.json) before final recommendations.

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
- [`../../dev-api-design/SKILL.md`](../../dev-api-design/SKILL.md) - API contract design and OpenAPI templates

---

## Code/SWE Agents (SE 3.0)

**What**: Autonomous coding agents that perform end-to-end software engineering tasks

**Scale**: peer-reviewed measurements put coding-agent adoption at roughly 16–23% of active GitHub projects showing agent traces by late 2025 (129,134-project study, arXiv:2601.18341) — treat any single-vendor "N hundred thousand PRs in N weeks" headline number as promotional and unverifiable; cite the study instead if precision matters

**SE 3.0 Paradigm**: Intent-driven, conversational development where developers collaborate with autonomous AI teammates

**Architecture Patterns**:

- **Multi-Agent SWE** (HyperAgent): Planner → Navigator → Code Editor → Executor
- **Minimal Agent** (Lita/Mini-SWE): ~100-line implementation; the original mini-swe-agent result was 68% on SWE-bench (2025), later re-benchmarked at >74% on SWE-bench Verified (2026) as the harness matured — check the current README before quoting a number

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

## Parallel Execution & Model Routing

**Parallel Execution**:

- Pattern: define the task, let the agent execute in the background, start a new task; check the tool's docs for its parallel-agent limit

**Model Routing / Cooperative Systems**:

- Smaller models handle routine tasks, delegate to larger models when needed
- Cost optimization through intelligent model selection

Focus on operationalization over demos.

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
