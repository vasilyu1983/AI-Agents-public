# Product Integration Patterns

Use this file when the request is about product UX and systems behavior around AI features rather than raw model choice.

## Streaming UX

- Stream progressively on low-risk surfaces; buffer high-stakes output until the output guardrail passes (see Streaming Architecture below). Batch/offline tasks do not stream.
- Preserve user context when retries happen; do not wipe the composer or draft.
- Expose `stop`, `retry`, and `undo/apply` controls for any user-visible generation.
- Distinguish loading, generating, validating, and failed states in the UI.

## Structured Output

- Prefer tool calling or schema-constrained generation over regex parsing, and validate before persisting or triggering side effects.
- Keep a degraded path: partial parse, human review, or explicit retry.
- Schema design, strict mode vs tool calling, discriminated unions, the repair loop and schema versioning: [ai-prompt-engineering core-patterns](../../ai-prompt-engineering/references/core-patterns.md#schema-design-for-llm-output).

## Persistence

- Store conversations and AI actions server-side with timestamps, model ID, prompt version, and feedback markers.
- Treat system prompts, tools, and post-processors as deployable product logic.
- Keep an audit trail when generations can affect business records, user content, or support workflows.

## Degraded Mode

- Define what the product does when the model is unavailable: fallback provider, simpler model, or non-AI path.
- Make degraded mode explicit in the UI when user expectations would otherwise be violated.
- Prefer keeping the core product usable without AI rather than blocking the entire journey.

## Streaming Architecture

Match the streaming mode to guardrail risk. Fail closed applies to the release, not to the tokens: a guardrail cannot block text already rendered.

- **Low-risk surfaces** (drafting, brainstorming, internal tools): stream tokens and run output checks in parallel on sentence or chunk boundaries. On a violation, stop the stream, retract the rendered text, and log the event.
- **High-stakes or regulated output** (medical, legal, financial, PII-bearing, anything a user may act on): buffer server-side until the output guardrail passes, then release. Show a progress state (for example "checking the answer") to cover the latency.
- **Server-side**: use the SDK's streaming call (look up the current function name and its structured-stream option in the SDK docs). Pipe the stream to the HTTP response as Server-Sent Events or a ReadableStream.
- **Client-side**: consume the ReadableStream, render text progressively as tokens arrive. For structured output, handle partial JSON gracefully — do not parse until a complete object boundary.
- **Error handling in streams**: the stream can error mid-response. Handle connection drops, timeouts, and model errors. Surface errors to the user inline (not as a separate error page). Provide a "retry" action that preserves conversation context.
- **Cancellation**: support "stop generating" — abort the fetch on the client, which should propagate to cancel the upstream API call and any pending tool executions. Do not charge for tokens you did not use.
- **Backpressure**: if the client cannot consume tokens fast enough (slow rendering, network congestion), the server should respect backpressure rather than buffering unboundedly.

## Conversation and Context Management

- **Message history storage**: store in a database, not just client state. Users expect conversations to persist across sessions and devices. Schema: `{ id, conversationId, role, content, toolCalls, toolResults, createdAt }`.
- **Context window management — default policy**: (1) a fixed budget for the system prompt and tool definitions, never truncated; (2) pinned user facts (preferences, constraints, entity IDs); (3) the last N turns verbatim; (4) when history exceeds about half of the remaining budget, summarize older turns into one block; (5) keep the full transcript server-side so the summary can be redone or audited. Use a pure sliding window only for stateless chit-chat. Track token usage per conversation. Memory design and compaction verification: [ai-context-layer context-hygiene](../../ai-context-layer/references/context-hygiene.md).
- **System prompts**: version them in code, do not hardcode strings. System prompts are product logic — they should go through code review, have tests, and be deployable independently when possible.
- **Multi-turn with tools**: when the model calls a tool, execute it and include the result in the message history. The model needs to see previous tool results to maintain coherent multi-step reasoning.
- **Conversation branching**: when a user "regenerates" a response, you are branching the conversation. Decide: replace the last message (simpler) or maintain a tree of branches (more flexible, more complex).
- **Idempotent tool calls**: give every side-effecting tool call an idempotency key derived from (conversation, turn, call index), and make the tool honor it. Regenerate and stream-retry replay the stored tool results instead of re-executing write tools; only read-only tools may be re-run.
