# Provider Capability Matrix

Cross-provider reference for Claude, OpenAI, Gemini, and Ollama. Use this when writing provider-abstraction shims, parity tests, or feature-flag guards in a multi-provider coding-agent runtime.

**Last reviewed:** 2026-07-11 against current OpenAI API docs (developers.openai.com), OpenAI Agents SDK docs, Gemini API docs (ai.google.dev), and Anthropic/Claude platform docs (platform.claude.com, docs.claude.com). This matrix is a design-time compatibility guide, not a source of truth for exact model names, beta headers, quotas, prices, or context windows. Verify those volatile fields against provider docs during implementation.

---

## Feature Matrix

| Capability | Claude (Anthropic) | OpenAI | Gemini (Google) | Ollama (local) |
|---|---|---|---|---|
| **Streaming (SSE/token)** | Yes — `stream: true` on Messages API | Yes — `stream: true` on Chat Completions | Yes — `streamGenerateContent` | Yes — `stream: true` on `/api/generate` and `/api/chat` |
| **Structured output (JSON mode)** | Yes — direct JSON tool schemas; confirm beta-specific flows per feature | Yes — schema-constrained output exists in current OpenAI APIs and Agents SDK guardrails/output-type flows | Yes — `responseMimeType: "application/json"` + `responseSchema` | Model-dependent; many GGUF models support grammar-constrained generation via `format: "json"` |
| **Native tool / function calls** | Yes — `tools: [...]`; parallel behavior varies by model and API surface | Yes — function tools, hosted tools, MCP tools, and Agents SDK tool abstractions; guardrail coverage differs by tool class | Yes — `tools: [functionDeclarations: [...]]` | Yes (OpenAI-compatible API mode) — model-dependent; not all GGUF models follow tool-call grammar reliably |
| **Vision (image input)** | Yes — `image` content block in Messages API (base64 or URL) | Yes — model-dependent image input in current multimodal APIs | Yes — inline image `Part` (JPEG, PNG, WEBP, HEIC, HEIF) | Model-dependent; LLaVA-family and Moondream support vision; most code models do not |
| **Prompt/context caching** | Yes — cache breakpoints on supported content blocks; TTL and pricing are provider-controlled | Managed and API-surface-dependent; do not assume a portable explicit cache API | Yes — implicit context caching for long contexts; explicit `cachedContents` API where available | N/A — inference runs locally; KV cache is managed by the runtime (llama.cpp, ollama serve) |
| **Streaming tool calls** | Yes — tool use events streamed in `content_block_delta` events | Yes — `tool_calls` streamed as deltas in `chat.completion.chunk` | Yes — `functionCall` part streamed in `generateContentResponse` | Model-dependent; streaming tool-call deltas not universally supported |
| **Max context window** | Model-dependent; query model metadata or docs at runtime | Model-dependent; query model metadata or docs at runtime | Model-dependent; long-context Gemini variants exist, but limits vary by model and tier | Model-dependent; common GGUF sizes: 4 k-128 k unless configured higher |
| **System prompt** | Yes — `system` top-level field | Yes — `messages[0].role = "system"` | Yes — `systemInstruction` field | Yes — `system` field (OpenAI-compat) or `system` in Modelfile |
| **Multi-turn conversation** | Yes — `messages: [...]` alternating user/assistant | Yes — `messages: [...]` array | Yes — `contents: [...]` with `role: user/model` | Yes — `messages: [...]` (OpenAI-compat `/api/chat`) |
| **Token usage reporting** | Yes — `usage` in response: `input_tokens`, `output_tokens`, `cache_read_input_tokens` | Yes — `usage.prompt_tokens`, `completion_tokens` | Yes — `usageMetadata.promptTokenCount`, `candidatesTokenCount` | Yes — `eval_count`, `prompt_eval_count` in response |
| **Cancellation / abort** | Yes — abort the SSE stream (client-side) | Yes — abort the SSE stream | Yes — cancel via HTTP abort | Yes — interrupt via connection close |
| **Batch / async inference** | Yes — Message Batches API (`/v1/messages/batches`) | Yes — Batch API (`/v1/batches`) | Yes — Batch prediction via Vertex AI | No native batch API; run multiple requests in parallel |

---

## Notes by Provider

### Claude (Anthropic)
- Prompt caching is the primary cost-reduction lever for coding agents; always set `cache_control` on the system prompt and shared tool definitions.
- Thinking/reasoning blocks are model- and feature-dependent. Shims must tolerate extra non-text content blocks rather than assuming every response is plain text.
- Computer-use and other beta tools require explicit feature gating. Store the beta/header version outside business logic and fail closed when the provider rejects it.

### OpenAI
- Current Agents SDK docs expose agents, tools, guardrails, MCP, tracing, sessions, memory, and sandbox agents. Provider shims should model those as capabilities, not as one monolithic "OpenAI chat" path.
- Tool guardrails apply to custom function tools; hosted tools, built-in execution tools, handoffs, and `Agent.as_tool()` have different guardrail coverage. Do not promise a single guardrail hook covers every execution surface.
- Parallel tool calls and hosted tools should be normalized into an internal `ToolCallReady` event; never assume a single tool call per assistant turn.

### Gemini (Google)
- `responseMimeType: "application/json"` + `responseSchema` is the Gemini equivalent of JSON mode.
- `cachedContents` API allows explicit cache creation for large shared contexts; useful for coding agents that load the full codebase into context. Explicit-cache token discounts and default TTL are model-generation- and tier-dependent — verify the current discount and TTL against `ai.google.dev` before sizing a caching strategy; do not hardcode a specific percentage into runtime logic or cost projections.
- Vision supports PDFs as well as images (`application/pdf` MIME type in `inlineData`).
- Rate limits differ significantly between Gemini Flash (high throughput) and Gemini Pro (lower); default to Flash for parallel subagents.

### Ollama (local)
- Capability varies by model. Always probe with a test request before assuming tool-call or vision support.
- Grammar-constrained JSON (`format: "json"`) works on most models but does not enforce a schema — only that the output is valid JSON.
- No authentication — treat as a trusted internal service only; never expose Ollama to the public network.
- Context window is set in the `Modelfile` `PARAMETER num_ctx`; the default (often 2 k–4 k) is too small for most coding tasks. Set explicitly.

---

## Shim Design Notes

**Streaming normalization:** All four providers stream tool calls differently. The shim must buffer partial tool-call chunks until the tool name and full argument JSON are complete, then emit a single normalized `ToolCallReady` event.

**Structured output fallback:** If the target provider does not support schema-enforced JSON output, fall back to prompt-engineering (e.g. "respond only with valid JSON matching this schema: …") plus a post-parse validation step.

**Cache portability:** Prompt-cache strategies written for Claude (`cache_control` breakpoints) do not translate to OpenAI or Gemini. Guard cache-optimization code behind a `provider.supportsExplicitPromptCache` capability flag.

**Vision absence:** Ollama coding models typically lack vision. The shim must check `provider.supportsVision` before sending image content blocks; fall back to OCR-extracted text or skip the image context.

---

## Capability Flag Interface (TypeScript)

```typescript
interface ProviderCapabilities {
  streaming: boolean;
  structuredOutput: "schema" | "json_only" | "none";
  toolCalls: boolean;
  parallelToolCalls: boolean;
  vision: boolean;
  promptCache: "explicit" | "implicit" | "none";
  maxContextTokens: number;
  batchInference: boolean;
}
```

Use this interface in your provider shim to gate feature usage at runtime without hardcoding provider names in business logic.
