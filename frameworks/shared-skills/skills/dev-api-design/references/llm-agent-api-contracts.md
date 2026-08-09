# LLM/Agent API Contracts

Use these contracts when exposing LLMs, agent tools, or multimodal models over HTTP/gRPC/GraphQL.

**Freshness anchor:** 2026-07-11 — verified against the MCP 2026-07-28 spec release candidate, official MCP site, OpenAI, and Google Cloud guidance.

## Table of Contents

- [Optional: AI/Automation](#optional-aiautomation)
- [Request Shape](#request-shape)
- [Response Shape (Sync/Stream)](#response-shape-syncstream)
- [Errors (use RFC 9457)](#errors-use-rfc-9457)
- [Long-Running Jobs](#long-running-jobs)
- [Streaming (SSE/WebSocket)](#streaming-ssewebsocket)
- [Safety & Guardrails](#safety-&-guardrails)
- [Observability](#observability)
- [Agent Experience (AX) — 2026 Trend](#agent-experience-ax-—-2026-trend)
- [AX Design Principles](#ax-design-principles)
- [Agent-Friendly Patterns](#agent-friendly-patterns)
- [Model Context Protocol (MCP) Integration](#model-context-protocol-mcp-integration)
- [What MCP Provides](#what-mcp-provides)
- [MCP API Contract Considerations](#mcp-api-contract-considerations)
- [MCP Security Concerns](#mcp-security-concerns)
- [Example: Exposing API as MCP Tool](#example-exposing-api-as-mcp-tool)
- [Resources](#resources)

## Optional: AI/Automation

This resource is only relevant if your API surface includes AI/agent capabilities. Do not apply these patterns to normal REST/GraphQL/gRPC APIs unless explicitly required.

## Request Shape
- `trace_id` + `request_id`
- `actor`: user_id, org_id, roles/scopes, auth method
- `prompt`: user text; `system_instructions`
- `context_refs`: doc ids, vector store keys, cache keys
- `tools_allowed`: ids + args schema; allowlist per request
- `model_params`: temperature, top_p, max_tokens, stop, seed
- `safety`: moderation level, PII policy, jailbreak guard on/off
- `delivery`: `stream=true|false`, `async=true|false`, callback URL + HMAC secret

## Response Shape (Sync/Stream)
- `choices[]`: message, role, finish_reason
- `stream_delta`: partial tokens or chunks
- `citations[]`: source_id, span, url
- `tool_calls[]`: name, args, status, result (if inline), latency_ms
- `usage`: prompt_tokens, completion_tokens, cost
- `trace_id` echoed; `rate_limit`: limit/remaining/reset

## Errors (use RFC 9457)
- `model_timeout`, `tool_failed`, `guardrail_blocked`, `retrieval_miss`, `validation_error`, `quota_exceeded`
- Include `trace_id`, `hint`, `retryable`

## Long-Running Jobs
- `202 Accepted` + `Location` for status; payload: `job_id`, `state`, `expires_at`, `eta`
- `state` transitions: queued → running → succeeded | failed | cancelled
- Webhooks: signed with HMAC; replay protection; include `trace_id`

## Streaming (SSE/WebSocket)
- SSE fields: `event=delta|done|error`, `id`, `data` (JSON lines)
- Close codes: document retry guidance; include `retry` in SSE if applicable
- Keep-alives: comment frames to avoid idle timeouts

## Safety & Guardrails
- Pre-check: content moderation, prompt injection scan, policy scope check
- Tool gating: enforce allowlist, validate args schema, human approval for high-risk
- Post-check: PII redaction, policy filters, hallucination/citation checks when available

## Observability
- Propagate `traceparent`/`tracestate` or `trace_id` header
- Emit spans: `llm_call`, `retrieval`, `tool_call`, `memory_op`
- Log: request envelope sans secrets, rate-limit decisions, guardrail outcomes

---

## Agent Experience (AX) — 2026 Trend

APIs increasingly consumed by AI agents, not just humans. Design for machine-first consumption.

### AX Design Principles

- **Strong schema**: OpenAPI 3.2 or 3.1 with complete type definitions
- **Predictable shapes**: Consistent response structure across endpoints
- **Explicit errors**: RFC 9457 Problem Details with actionable `hint` fields
- **Discovery**: Machine-readable capability descriptions
- **Rate limits for burst**: Agents generate 1000s of calls in short bursts
- **Side effects explicit**: Mark mutating actions, approval boundaries, and idempotency clearly

### Agent-Friendly Patterns

- Return `capabilities` endpoint listing available actions
- Include `retry_after` in 429 responses (agents can auto-retry)
- Provide `example_requests` in OpenAPI for agent prompting
- Use semantic action names agents can reason about

### CLI as Agent Interface

CLIs are a common agent tool surface alongside REST and MCP. The same AX principles apply:

- **Non-interactive**: every input as a flag; agents cannot handle interactive prompts
- **Predictable structure**: consistent noun-verb pattern across all subcommands
- **Machine-parseable output**: `--json` flag, structured success responses with IDs and URLs
- **Idempotent and retry-safe**: agents retry constantly; same command twice should be a no-op
- **Progressive discovery**: useful `--help` with examples per subcommand, not a docs dump
- **Actionable errors**: show correct invocation on failure, not a hang

For full CLI-for-agents patterns, see [`../../software-devtools/SKILL.md`](../../software-devtools/SKILL.md) § Agent-Friendly CLI Patterns.

---

## Model Context Protocol (MCP) Integration

MCP is an open protocol for exposing tools, resources, and prompts to AI clients. On 2025-12-09, Anthropic donated MCP to the newly formed Agentic AI Foundation (AAIF) under the Linux Foundation, alongside Block's goose and OpenAI's AGENTS.md — it is now a vendor-neutral, community-governed standard. Per Anthropic's Dec 2025 ecosystem update, MCP SDKs had passed 97M+ monthly downloads and 10,000+ active public servers; a Stacklok 2026 survey separately found 41% of surveyed software organizations in limited or broad production with MCP servers. The 2026-07-28 spec release candidate was locked 2026-05-21; final publication is 2026-07-28 (still forthcoming as of this writing — verify it has shipped before depending on RC-only behavior).

**Current transport standard:** Streamable HTTP is the preferred remote transport. `stdio` remains standard for local/embedded servers. The 2026-07-28 RC makes MCP servers formal OAuth 2.1 resource servers (RFC 9728 Protected Resource Metadata, RFC 8707 Resource Indicators) — the clearest signal that OAuth 2.1 is becoming the standard auth mechanism for remote MCP servers, though the spec has not yet finalized as of this writing.

### What MCP Provides

- Universal tool-exposure layer over existing APIs for LLM consumption
- Structured bridge between AI agent and external tools/resources/prompts
- Natural language discovery of API capabilities via tool descriptions
- Versioned protocol; check https://modelcontextprotocol.io/specification/ for the current stable version

### MCP API Contract Considerations

- **Expose via MCP server**: Publish a stable tool layer over domain operations, not a thin REST mirror
- **Tool descriptions**: Clear, concise descriptions for LLM reasoning (tested against actual LLM calls)
- **Argument schemas**: JSON Schema for all tool parameters; prefer narrow enums and explicit bounds over open strings
- **Long-running work**: Use task/job semantics for async operations; do not pretend everything is synchronous
- **Auth**: OAuth 2.1 for remote servers; document how API auth, user consent, and tenant boundaries map to MCP calls
- **Observability**: Correlate MCP tool calls with underlying API traces and audit logs

### MCP Security Concerns

- Treat every tool argument as untrusted input
- Constrain filesystem, shell, and network access behind least-privilege boundaries
- Validate schemas server-side even when the client already validated
- Keep destructive or external side effects explicit and auditable
- Apply the same authz and tenancy checks you would apply on the underlying API

### Example: Exposing API as MCP Tool

```json
{
  "name": "search_products",
  "description": "Search product catalog by query and filters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search terms" },
      "category": { "type": "string", "enum": ["electronics", "clothing", "home"] },
      "max_price": { "type": "number", "description": "Maximum price in USD" }
    },
    "required": ["query"]
  }
}
```

### Resources

- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [OpenAI Remote MCP Tools](https://platform.openai.com/docs/guides/tools-remote-mcp)
- [Google Vertex AI MCP Guide](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/mcp/use-mcp)
