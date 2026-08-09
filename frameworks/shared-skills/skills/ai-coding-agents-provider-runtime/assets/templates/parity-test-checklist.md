# Provider Parity Test Checklist

Run this checklist when onboarding a new provider, upgrading a provider SDK, or adding a new capability to the shim. One column per provider; check each cell before declaring the shim production-ready.

---

## How to Use

Mark each cell: `pass`, `fail`, `n/a` (provider does not support the feature), or `skip+reason`. A shim is shippable for a given provider when all non-`n/a` cells are `pass`.

---

## Streaming

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| Stream starts within 2 s on a short prompt | | | | |
| First token arrives before the full response | | | | |
| Stream terminates cleanly (`stop_reason` or equivalent) | | | | |
| Abort mid-stream produces no partial state on server | | | | |
| Shim emits `StreamChunk` events in order | | | | |
| Shim emits `StreamEnd` exactly once | | | | |

**Resolution if failing:** Check that the shim is not buffering the full response before emitting events; verify the SSE/WebSocket connection is not being wrapped in a Promise-collecting adapter.

---

## Structured Output (JSON mode)

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| Provider returns valid JSON when schema enforced | | | | |
| Shim post-validates JSON against the requested schema | | | | |
| Invalid JSON triggers `StructuredOutputError`, not a crash | | | | |
| Fallback prompt-engineering path activates when provider lacks schema support | | | | |
| Schema passed to provider matches the JSON Schema spec version the provider expects | | | | |

**Resolution if failing:** Confirm the provider's schema format version (draft-07 vs 2020-12); some providers reject unknown keywords. Add a schema-normalization step in the shim.

---

## Tool Calls

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| Single tool call returns correct `name` and `arguments` | | | | |
| Parallel tool calls: multiple tools in one turn are all received | | | | |
| Tool result correctly returned to model in next turn | | | | |
| Unknown tool name triggers `ToolNotRegistered`, not a silent drop | | | | |
| Tool-call argument JSON is valid against the tool's schema | | | | |
| Streaming tool-call chunks are buffered until complete before dispatch | | | | |

**Resolution if failing:** Parallel tool calls return an array in some providers; verify the shim handles both single-object and array forms. For streaming, ensure the argument accumulator resets per tool call ID.

---

## Vision (Image Input)

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| JPEG base64 image is accepted | | | | |
| PNG base64 image is accepted | | | | |
| Image URL (https) is accepted | | | | |
| `provider.supportsVision = false` flag set correctly for non-vision models | | | | |
| Sending image to non-vision provider triggers `CapabilityNotSupported`, not a 400 | | | | |

**Resolution if failing:** Check `supportsVision` flag in the capability object before calling the provider. Add a pre-flight capability check in the shim's `sendMessage` path.

---

## Prompt Cache

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| Explicit cache breakpoints set correctly for supported providers | | | | |
| `cache_read_input_tokens` (or equivalent) appears in usage stats | | | | |
| Cache hit rate > 0 on repeated identical prompts | | | | |
| Shim skips cache headers for providers that do not support explicit caching | | | | |
| Cache invalidation on settings reload does not cause API error | | | | |

**Resolution if failing:** Verify `cache_control` header format matches the provider version; Anthropic added prompt caching in a specific API version. For providers without explicit cache APIs, document that cache stats will always be zero.

---

## Token Usage Reporting

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| `input_tokens` (or equivalent) present in every response | | | | |
| `output_tokens` (or equivalent) present in every response | | | | |
| Token counts are non-zero for non-empty prompts | | | | |
| Shim normalizes provider-specific field names to a common `TokenUsage` object | | | | |
| Token usage accumulates correctly across a multi-turn session | | | | |

**Resolution if failing:** Each provider uses different field names (`usage.prompt_tokens` vs `usage.input_tokens` vs `usageMetadata.promptTokenCount`). The shim's normalization step must cover all variants; add a fallback of zero to prevent null-pointer errors in the cost-accounting layer.

---

## Error Handling

| Test | Claude | OpenAI | Gemini | Ollama |
|------|--------|--------|--------|--------|
| Rate limit (429) triggers exponential backoff, not crash | | | | |
| Auth failure (401/403) surfaces `AuthenticationError` immediately (no retry) | | | | |
| Model overload (529 / 503) retried up to `max_retries` | | | | |
| Context-length exceeded error triggers `ContextOverflowError` | | | | |
| Network timeout retried with exponential backoff | | | | |
| All error types map to a provider-agnostic error class | | | | |

**Resolution if failing:** Build an error-classification table in the shim: HTTP status + error message pattern → canonical error class. Never let provider-specific error shapes leak into business logic.
