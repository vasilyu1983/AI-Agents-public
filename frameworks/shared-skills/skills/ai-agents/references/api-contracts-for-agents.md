# API Contracts for Agents

Use these envelopes when exposing agents/LLMs via REST/gRPC/GraphQL.

## Request Envelope
- `trace_id` (propagate) + `request_id`
- `actor`: user/org ids, roles/scopes, auth method
- `intent`: task description, system instructions
- `context_refs`: doc ids, vector keys, cache keys
- `tools_allowed`: ids + args schema; per-request allowlist
- `safety`: moderation level, PII policy, jailbreak guard on/off
- `delivery`: `stream` (SSE/WebSocket), `async` (202 + polling), callback URL + HMAC
- `params`: temperature, top_p, max_tokens, stop, seed

## Response Envelope
- `choices[]`: message, role, finish_reason
- `stream_delta`: partial tokens/chunks when streaming
- `citations[]`: source_id, span, url
- `tool_calls[]`: name, args, status, result (if inline), latency_ms
- `usage`: prompt_tokens, completion_tokens, cost
- `trace_id` echoed; `rate_limit`: limit/remaining/reset

## Errors (RFC 7807)
- Types: `model_timeout`, `tool_failed`, `guardrail_blocked`, `retrieval_miss`, `validation_error`, `quota_exceeded`
- Include `trace_id`, `hint`, `retryable`

## Streaming
- SSE fields: `event=delta|done|error`, `id`, `data` (JSON lines)
- WebSocket: close codes documented; heartbeat/ping interval; backpressure guidance
- Keep-alives for idle connections; clear retry/backoff policy

## Long-Running Jobs
- `202 Accepted` + `Location` for status; payload includes `job_id`, `state`, `eta`, `expires_at`
- States: queued → running → succeeded | failed | cancelled
- Callbacks: signed (HMAC), replay-protected, include `trace_id`

## Safety & Guardrails
- Pre: moderation, injection scan, scope/role checks, tool allowlist enforcement
- During: block high-risk tool calls unless approved; cap batch sizes, TTLs
- Post: PII redaction, policy filters, optional hallucination/citation checks

## Observability
- Propagate `traceparent`/`tracestate` or `trace_id` header end-to-end
- Spans: `llm_call`, `retrieval`, `tool_call`, `memory_op`
- Logs: request envelope sans secrets, guardrail outcomes, rate-limit decisions
