# Integration Scenarios

Use this file when you need a concrete recipe for a common AI-feature integration moment. The decision core, including the single Traps and Anti-Patterns table, stays in [SKILL.md](../SKILL.md#traps-and-anti-patterns).

SDK function names below are generic on purpose. Look up the current names in your SDK's docs and migration guide when writing code.

## End-to-End Flow

```text
AI feature request
  -> Classify: chat, generation, extraction, search, or agent-adjacent UX
  -> Route architecture, RAG, or agent-heavy work to companion skills
  -> Define typed request and response contract
  -> Choose provider, streaming, safety, and cost controls
  -> Implement product UX states and observability
  -> Verify provider behavior and eval evidence
```

## Scenarios

Recipes keyed to symptoms or integration moments. Each lists the shortest path to a working, production-safe implementation.

### S1 — Streaming chat with citations

1. Define the server endpoint with the SDK's streaming call and the chosen provider. Decide the streaming mode first: citation answers a user may act on in a regulated domain are buffered until the output guardrail passes ([SKILL.md: Streaming Architecture](../SKILL.md#streaming-architecture)).
2. Include a `citations` tool or instruct the model to embed `[source:N]` markers in prose.
3. Pipe the `ReadableStream` to the HTTP response as SSE.
4. On the client, use the SDK's chat UI hook (or a custom reader) to render tokens progressively; parse `[source:N]` markers into inline links.
5. Handle mid-stream errors with a visible inline retry control that preserves conversation context.
6. Log each completed turn with `{ conversationId, model, inputTokens, outputTokens, latencyMs }` for cost tracking.

### S2 — Structured extraction with a schema + retry-on-schema-fail

1. Define the target shape as one schema (e.g. Zod) and bind it with the SDK's schema-output facility (look up its current name in the SDK's migration guide). Schema design rules: [ai-prompt-engineering core-patterns](../../ai-prompt-engineering/references/core-patterns.md#schema-design-for-llm-output).
2. On a validation error, log the raw response and retry once, feeding the validator's error text back to the model. If the retry also fails, take the degraded path; do not loop.
3. Use a discriminated union (`{ type: "success" | "parse_error" | "refused" }`) to handle all branches.
4. Validate the complete object before any persistence or side-effect call.
5. Track schema-fail rate per endpoint; alert if it exceeds 1% — signals prompt drift or model regression.

### S3 — Tool-calling agent with indirect-prompt-injection guard

1. Define tools with minimal, read-only side effects; server owns writes, model only requests them.
2. Add an input-sanitization step: strip `\nAssistant:`, `\nHuman:`, and instruction-override patterns before injecting user input into prompts.
3. After each tool call, verify the returned result matches the declared tool schema before passing back to the model.
4. Audit-log every tool call with `{ tool, args, result, conversationId }` for post-incident tracing.
5. Give every side-effecting tool call an idempotency key from (conversation, turn, call index). Regenerate and retry replay the stored tool results; "stop generating" cancels pending tool executions.
6. Before enabling tools, lint the agent config: `python3 scripts/check_injection_defenses.py <agent-config.json>` (exit 1 when an allowlist, output validation or prompt isolation is missing).
7. Add an output filter that refuses responses containing suspicious lateral instructions or role-change attempts.

### S4 — Multi-provider routing on rate-limit

1. Abstract provider calls behind a single `AIProvider` interface; swap implementations without changing call sites.
2. Implement a circuit breaker: after N `429` responses in M seconds, route to the fallback provider.
3. Maintain per-model prompt variants; run quality gates before switching traffic to an alternate model.
4. Alert on circuit-breaker activation; log which provider is active per request for cost attribution.
5. Add a `--dry-run` mode in staging that exercises the fallback path without real traffic.

### S5 — RAG with stale-cache invalidation

1. Cache retrieval results with a `content_hash` and `retrieved_at` timestamp in the cache key.
2. On each query, compare the source document's `updated_at` against cached `retrieved_at`; evict on mismatch.
3. Build a background job to re-index documents when source content changes; see [ai-rag](../../ai-rag/SKILL.md) for chunking strategy.
4. Return `{ answer, sources[{ id, title, url, retrieved_at }] }` to the UI for attribution.
5. Track cache-hit rate and stale-eviction rate; tune TTL to balance freshness against provider cost.
