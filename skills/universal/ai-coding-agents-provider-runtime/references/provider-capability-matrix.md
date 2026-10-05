# Provider Capability Matrix

Cross-provider reference for Claude, OpenAI, Gemini, and Ollama. Use this when writing provider-abstraction shims, parity tests, or feature-flag guards in a multi-provider coding-agent runtime.

This matrix is a design-time compatibility guide: it says **where** each capability lives and what to check, not what the current values are. Wire shapes, beta flags, quotas, prices, context windows, and model support change; verify every cell against the provider docs listed in [`../data/sources.json`](../data/sources.json) during implementation, and let the parity suite, not this table, decide what a provider supports.

---

## Feature Matrix

| Capability | Claude (Anthropic) | OpenAI | Gemini (Google) | Ollama (local) |
|---|---|---|---|---|
| **Streaming (SSE/token)** | Yes — `stream: true` on Messages API | Yes — streamed events; event names and shapes differ between the Responses and Chat Completions surfaces | Yes — `streamGenerateContent` | Yes — `stream: true` on `/api/generate` and `/api/chat` |
| **Structured output (JSON mode)** | Yes — tool input schemas or schema-constrained output; check current docs for which models and surfaces enforce the schema | Yes — schema-constrained output exists in current OpenAI APIs and Agents SDK guardrails/output-type flows | Yes — `responseMimeType: "application/json"` + `responseSchema` | Model-dependent; check whether the local server's `format` field accepts a JSON schema or only JSON mode, and validate after parsing either way |
| **Native tool / function calls** | Yes — `tools: [...]`; parallel behavior varies by model and API surface | Yes — function tools, hosted tools, MCP tools, and Agents SDK tool abstractions; guardrail coverage differs by tool class | Yes — `tools: [functionDeclarations: [...]]` | Yes (OpenAI-compatible API mode) — model-dependent; not all GGUF models follow tool-call grammar reliably |
| **Vision (image input)** | Yes — `image` content block in Messages API (base64 or URL) | Yes — model-dependent image input in current multimodal APIs | Yes — inline image `Part`; accepted formats and size limits vary, so look them up | Model-dependent; LLaVA-family and Moondream support vision; most code models do not |
| **Prompt/context caching** | Yes — cache breakpoints on supported content blocks; TTL and pricing are provider-controlled | Automatic prefix caching on supported models, plus documented request-level controls; read the current prompt-caching docs for controls, minimum prefix length, and retention | Yes — implicit context caching for long contexts; explicit `cachedContents` API where available | N/A — inference runs locally; KV cache is managed by the runtime (llama.cpp, ollama serve) |
| **Streaming tool calls** | Yes — tool use events streamed in `content_block_delta` events | Yes — tool-call argument deltas streamed; event names differ between Responses and Chat Completions | Yes — `functionCall` part streamed in `generateContentResponse` | Model-dependent; streaming tool-call deltas not universally supported |
| **Max context window** | Model-dependent; query model metadata or docs at runtime | Model-dependent; query model metadata or docs at runtime | Model-dependent; long-context Gemini variants exist, but limits vary by model and tier | Model-dependent; read the configured context length for the loaded model rather than assuming the model's maximum |
| **System prompt** | Yes — `system` top-level field | Yes — an instructions field or a system-role message, depending on API surface | Yes — `systemInstruction` field | Yes — `system` field (OpenAI-compat) or `system` in Modelfile |
| **Multi-turn conversation** | Yes — `messages: [...]` alternating user/assistant | Yes — a message array, or input items chained to a previous response, depending on API surface | Yes — `contents: [...]` with `role: user/model` | Yes — `messages: [...]` (OpenAI-compat `/api/chat`) |
| **Token usage reporting** | Yes — `usage` in response: `input_tokens`, `output_tokens`, `cache_read_input_tokens` | Yes — `usage` object; token field names differ by API surface, so map them explicitly | Yes — `usageMetadata.promptTokenCount`, `candidatesTokenCount` | Yes — `eval_count`, `prompt_eval_count` in response |
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
- Choose subagent models by measured tool-call fidelity (the parity suite) and your account quota, not by tier name. Read quotas from the provider console for the account in use.

### Ollama (local)
- Capability varies by model. Always probe with a test request before assuming tool-call or vision support.
- Structured output support depends on the server version and model: check whether a JSON schema can be passed or only JSON mode is available, and schema-validate the parsed output in both cases.
- No authentication — treat as a trusted internal service only; never expose Ollama to the public network.
- The context length actually used is a server or Modelfile setting (`num_ctx`), and the default is frequently too small for coding tasks. Read it and set it explicitly.

---

## Shim Design Notes

**Streaming normalization:** All four providers stream tool calls differently. The shim must buffer partial tool-call chunks until the tool name and full argument JSON are complete, then emit a single normalized `ToolCallReady` event.

**Structured output fallback:** If the target provider does not support schema-enforced JSON output, fall back to prompt-engineering (e.g. "respond only with valid JSON matching this schema: …") plus a post-parse validation step.

**Cache portability:** Explicit-breakpoint cache strategies do not translate to providers that cache automatically by prefix, or that use a separate cached-content resource. Guard cache-optimization code behind a `promptCache` capability value, and keep the request prefix byte-stable on every provider (see SKILL.md Expert Judgment Calls).

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
