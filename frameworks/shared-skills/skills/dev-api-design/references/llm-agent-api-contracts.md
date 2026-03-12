# LLM/Agent API Contracts

Use these contracts when exposing LLMs, agent tools, or multimodal models over HTTP/gRPC/GraphQL.

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

- **Strong schema**: OpenAPI 3.1+ with complete type definitions
- **Predictable shapes**: Consistent response structure across endpoints
- **Explicit errors**: RFC 9457 Problem Details with actionable `hint` fields
- **Discovery**: Machine-readable capability descriptions
- **Rate limits for burst**: Agents generate 1000s of calls in short bursts

### Agent-Friendly Patterns

- Return `capabilities` endpoint listing available actions
- Include `retry_after` in 429 responses (agents can auto-retry)
- Provide `example_requests` in OpenAPI for agent prompting
- Use semantic action names agents can reason about

---

## Model Context Protocol (MCP) Integration

MCP is Anthropic's open standard (Nov 2024) for AI-to-API integration. Adopted by OpenAI, Google DeepMind.

### What MCP Provides

- Universal adapter wrapping existing APIs for LLM consumption
- Structured bridge between AI agent and external tools
- Natural language discovery of API capabilities

### MCP API Contract Considerations

- **Expose via MCP server**: Wrap REST/GraphQL endpoints for agent access
- **Tool descriptions**: Clear, concise descriptions for LLM reasoning
- **Argument schemas**: JSON Schema for all tool parameters
- **Security**: MCP inherits API auth; validate all inputs (43% of MCP implementations have injection vulnerabilities)

### MCP Security Concerns (2025)

- Command injection in 43% of tested implementations
- SSRF vulnerabilities in 30%
- Arbitrary file access in 22%
- Mitigation: Treat MCP tool calls as untrusted input; validate strictly

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
- [MCP Security Assessment (Equixly 2025)](https://equixly.com/blog/mcp-security-assessment)
- [Building AI Agents with MCP (Red Hat)](https://developers.redhat.com/articles/2026/01/08/building-effective-ai-agents-mcp)
