# Context-Window, Retries, And Fallback Routing

Provider runtimes need explicit policy for “what happens when the ideal request cannot be sent or cannot succeed.”

## Context-window strategy

Define a strict order of operations:

1. prune obviously irrelevant context
2. summarize or compress older turns
3. preserve tool-call and approval facts needed for continuity
4. only then truncate or drop lower-priority material

Do not let each provider invent its own truncation logic independently.

## Retry classes

Keep retries class-specific:

- transport or transient network error
- rate limit
- provider timeout
- malformed streaming payload
- malformed tool-call payload
- policy refusal
- context overflow

Each class may deserve a different response: retry, reformulate, fallback, or escalate. Give each class its own budget, honour provider retry/reset hints for rate limits, and cap the whole turn.

The retry-safety boundary is the first emitted delta. Before any content or tool-call delta reaches consumers, a failed request may be retried transparently. After that, a retry is a new attempt: mark or retract the partial output and never re-dispatch tool calls from the failed attempt.

## Fallback routing

Fallback is safe only when you define:

- which providers are semantically acceptable substitutes
- whether tool calling must remain enabled
- whether structured output must remain strict
- whether prompt caching or long-context behavior is required
- what user-visible notice is emitted when fallback occurs
- that a per-provider circuit opens on sustained failure before fallback starts

A cross-provider fallback also drops provider-specific reasoning items (record the loss) and starts with a cold prompt cache, so its cost includes the lost cache.

## Edge cases

- **Fallback to weaker tool semantics**: if the fallback provider cannot match the primary tool-call contract, the runtime should degrade visibly or disable the workflow.
- **Cross-provider resume**: a restored session may need a different provider than the original one; document what must be preserved semantically.
- **Retry storms**: multiple nested retries across provider, tool, and network layers can explode latency and cost if not bounded centrally.
- **Long-context overflow during verification**: verification agents often load more files than the implementation agent; keep separate policy for them.

## Practical tip

The safest fallback policy for coding agents is usually conservative:

- only targets that passed the same parity suite as the primary, same-family or not
- among those, prefer equivalent tool-call and structured-output support
- visible degradation notice if capability drops
