---
name: software-ai-integration
description: "Applies production AI integration patterns for chat, structured output, guardrails, provider routing, and AI UX. Use when adding LLM-powered features to an application."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# AI-Augmented Product Engineering

## Quick Reference

| Concern | Defaults |
|---|---|
| LLM API integration | Vercel AI SDK by default; use a direct provider SDK when its capabilities or smaller abstraction fit better (see Integration and Gateway Choice) |
| Streaming responses | SSE / ReadableStream from the SDK's server streaming call; streaming mode matched to guardrail risk (see Streaming Architecture) |
| Structured output | Schema-constrained output or tool calling, one schema definition (e.g. Zod) validated in code; contract rules in ai-prompt-engineering |
| Chat interface | The SDK's chat UI hook, or a custom streaming UI |
| AI-assisted forms | Inline suggestions, auto-complete, content generation |
| Guardrails | Input/output filtering, content moderation, PII detection |
| Cost management | Token counting, caching (semantic + exact), model routing |
| Multi-provider | Thin internal router for one product; consider a Portkey-class gateway for shared routing or policy (see Integration and Gateway Choice) |
| Evaluation | Human feedback, LLM-as-judge, A/B testing AI variants |
| RAG in products | Vector search + context injection (see also ai-rag for deeper patterns) |

## When NOT to Use This Skill

- **LLM lifecycle management (fine-tuning, deployment, monitoring)** → [ai-llm](../ai-llm/SKILL.md)
- **Agent system architecture and orchestration** → [ai-agents](../ai-agents/SKILL.md)
- **Prompt engineering techniques and patterns** → [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)
- **RAG system architecture (indexing, retrieval, chunking)** → [ai-rag](../ai-rag/SKILL.md)
- **ML model training and data science** → [ai-ml-data-science](../ai-ml-data-science/SKILL.md)
- **MLOps and model serving infrastructure** → [ai-mlops](../ai-mlops/SKILL.md)
- **Building MCP servers and tool protocols** → [agents-mcp](../agents-mcp/SKILL.md)

## When NOT to Add AI At All

Not every "AI feature" request should become one. Apply this filter before the decision tree below:

- **Deterministic logic solves it.** If the mapping from input to output is a rule, a regex, a lookup table, or a small classifier that can be trained offline, an LLM call adds latency, cost, and non-determinism for no accuracy gain. Reach for an LLM when the input space is open-ended natural language or the task requires judgment a rule set cannot encode.
- **The eval bar cannot be met.** If nobody can articulate what "correct" looks like well enough to write 20-50 test cases with expected outputs, the team cannot tell if the feature works, regresses, or is safe to ship. Build the eval set before writing the first prompt (see [ai-evals](../ai-evals/SKILL.md)) — "we'll know it when we see it" is not a launch gate.
- **The failure mode is unacceptable and unrecoverable.** High-stakes one-shot actions (irreversible financial transfers, medical dosing, legal filings) need a human-in-the-loop confirmation step even when the model is highly accurate; if the product cannot afford *any* rate of wrong output and cannot insert a checkpoint, do not automate that step with an LLM.
- **A cheaper, boring solution already ships the value.** Autocomplete from historical data, templated responses, or a search index often satisfy the underlying user need without a model call. Prototype the non-AI version first if it is cheap to build — it is also the fallback path required by the guardrail rules below.

## Integration and Gateway Choice

| Need | Default | Change when |
|---|---|---|
| Product chat, streaming, extraction | Vercel AI SDK; direct provider SDK when its capabilities or a smaller abstraction matter | Use an embedded copilot shell when its UI is central to the feature; use agent orchestration only for stateful multi-step work |
| Moderation and prompt-injection checks | Provider moderation if available, otherwise a tested classifier | Add a dedicated guard service if adversarial testing shows the simpler gate misses required cases |
| Evaluation and traces | Keep product-specific criteria in code; use existing observability or an LLM tracing service | Build storage only when retention, access, or query requirements cannot be met |
| Provider routing | Thin internal router for one product | Consider a Portkey-class gateway when several teams need common budgets or policy; first check vendor ownership/control continuity and assign owners for keys, prompt/log retention, residency, export, and rollback |

Keep prompts, schemas, eval criteria, and business rules under product ownership even when infrastructure is bought.

## Workflow

1. Classify the feature shape: chat, generation, extraction, search, or agent-adjacent UX.
2. Confirm the product boundary and route architecture-heavy or retrieval-heavy work to the adjacent skill when needed.
3. Pick the primary pattern from the decision tree, then define the request contract, latency target, and safety checks.
4. Apply the relevant implementation guidance for streaming, structure, cost, and guardrails.
5. Verify current provider capabilities with the navigation references and fact-checking rules before final recommendations.

## Decision Tree

```text
What kind of AI feature?
├─ Chat / conversational UI
│  ├─ Web app → app AI SDK (chat UI hook + server streaming call)
│  │  ├─ Conversation history → Store in DB, not just client state
│  │  ├─ Streaming markdown → Progressive render with remark/rehype
│  │  └─ Multi-turn with tools → Tool results in message history
│  └─ Mobile / native → Direct SSE consumption + custom UI
├─ Content generation ("write for me")
│  ├─ Short-form (titles, descriptions) → Single generation + schema
│  └─ Long-form (articles, reports)
│     └─ Draft → Review → Edit → Apply pattern with undo support
├─ Inline suggestions (autocomplete)
│  ├─ Latency-critical → Smallest, fastest model tier that passes the evals
│  ├─ UI pattern → Ghost text, accept with Tab, dismiss with Esc
│  └─ Trigger → Debounce input (300-500ms), cancel in-flight requests
├─ Data extraction / classification
│  ├─ Structured output with schema validation in code
│  ├─ Batch processing → Queue + worker pattern
│  └─ Confidence scores → Include in schema, filter by threshold
├─ Search / Q&A over content
│  └─ RAG pattern (see ai-rag) + this skill for product integration
└─ Agent features (multi-step autonomous)
   └─ ai-agents for architecture, this skill for product UX integration
```

## Streaming Architecture

Stream server-side (the SDK's streaming call, piped as SSE/ReadableStream) and render progressively client-side, but **match the streaming mode to guardrail risk**:

- **Low-risk surfaces** (drafting, brainstorming, internal tools): stream tokens and run output checks in parallel on sentence or chunk boundaries. On a violation, stop the stream, retract the rendered text in the UI, and log it.
- **High-stakes or regulated output** (medical, legal, financial, PII-bearing, anything a user may act on): buffer server-side until the output guardrail passes, then release. Show a progress state to cover the latency.
- **Fail closed applies to the release, not to the tokens.** A guardrail cannot block tokens already rendered, so a surface that must never show unchecked text is a buffered surface.

Handle mid-stream errors inline with a context-preserving retry, make "stop generating" cancel the upstream call and any pending tool executions, and respect backpressure. Details: [references/product-integration-patterns.md](references/product-integration-patterns.md#streaming-architecture).

## Structured Output Wiring

- **Bind the schema with the SDK's schema-output facility and validate the parsed object.** Look up the current function name in the SDK's migration guide or changelog when writing code; these APIs are renamed between major versions. One schema definition (e.g. Zod) gives both types and runtime validation.
- **Check the provider's strict-schema subset before deployment.** Compile the canonical schema for each provider/model path and reject unsupported keywords or shapes; never silently weaken required constraints. Provider schema acceptance is a deployment gate, while application validation still gates persistence and side effects.
- **Stream partial objects for display only.** Validate the complete object before persistence or any side effect.
- **Handle non-success responses explicitly.** A refusal or token-limit truncation can bypass the expected object shape. Inspect the provider/SDK completion status before parsing; record a typed refusal or incomplete result, then retry only when safe and bounded or route to review.
- **Contract design lives in ai-prompt-engineering:** schema field order, closed enums with `unknown`, strict schema mode vs tool calling, discriminated unions, and the one-retry repair loop are in [ai-prompt-engineering core-patterns](../ai-prompt-engineering/references/core-patterns.md#schema-design-for-llm-output). Schema-constrained modes guarantee syntax where supported, not correctness.

## Conversation & Context Management

Store message history server-side, version system prompts in code, and keep tool results in history.

**Default history policy** (switch to a pure sliding window only for stateless chit-chat):

1. Fixed budget for the system prompt plus tool definitions; never truncate them.
2. Then pinned user facts (stated preferences, constraints, entity IDs).
3. Then the last N turns verbatim.
4. When history exceeds about half of the remaining budget, summarize the older turns into one block.
5. Keep the full transcript server-side, so a summary can be redone or audited.

Memory design and how to verify that compaction kept what matters: [ai-context-layer context-hygiene](../ai-context-layer/references/context-hygiene.md).

**Regenerate and retry must not re-execute side effects.** Give every side-effecting tool call an idempotency key derived from (conversation, turn, call index), and make the tool honor it. Regenerate and stream-retry replay the stored tool results instead of calling write tools again; "stop generating" cancels pending tool executions, not only the token stream. Details: [references/product-integration-patterns.md](references/product-integration-patterns.md#conversation-and-context-management).

## Cost Control

| Control | Default rule |
|---------|-------------|
| Token estimation | Estimate input tokens before sending; warn or truncate at budget threshold; use tiktoken or provider tokenizer |
| Caching | Exact-match cache for deterministic queries; semantic cache (embeddings) for FAQ-style; set TTLs |
| Model routing | Small, fast tier for classification/extraction/autocomplete; frontier tier for complex reasoning/long-form; confirm each choice with evals |
| Usage tracking | Track tokens per user, per feature, per model; budget alerts at 70% and 90% of monthly allocation |
| Rate limiting | Apply per user tier at the application layer; return clear error messages with upgrade paths |
| Prompt optimization | Audit system prompts for verbosity; measure quality vs. length trade-offs |

See [references/rollout-and-observability.md](references/rollout-and-observability.md) for cost dashboards, eval loops, and feature-flag rollout patterns.

### Prompt-caching break-even rule

Caching pays only once a cached prefix is reused enough to amortize the cache-write premium. Cost model (per prefix token, prices as multiples of the normal input price, which is 1): the first call writes the cache at multiplier `w` (> 1); each later call that hits the cache before it expires reads at multiplier `r` (< 1); without caching every call pays 1.

- Derivation: for 1 write + `k` reads, no-cache cost = `(1 + k)·1`; cached cost = `w + k·r`; caching wins when `w + k·r < 1 + k`, i.e. **`k > (w − 1)/(1 − r)` reads**.
- Equivalently, in total calls `n = 1 + k`: `n > (w − r)/(1 − r)`. Both forms are the same rule; state which count you are using.
- Take `w` and `r` for the specific model and cache TTL from the provider's pricing page at use time — they differ by provider, model, and TTL. Every expiry or prefix change costs another write, so count only reads inside one TTL window.

The payoff depends on cache terms and prompt layout; use [ai-prompt-engineering: Cache-Aware Prompt Layout](../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout) to keep reusable prefixes stable.

Apply the same break-even logic before adopting batch-API discounts (take the current discount from the provider's batch pricing) versus real-time calls: batch trades latency for cost, so it fits delay-tolerant, non-interactive work (bulk classification, offline enrichment, nightly reports) — it is not a substitute for interactive features, which need real-time calls.

## AI UX Patterns

| Pattern | Rule |
|---------|------|
| Loading states | Show tokens as they arrive on streamed surfaces; show a progress state on buffered (high-stakes) surfaces |
| Regenerate + stop | Always provide both controls; regenerate replays stored tool results, stop cancels pending tool executions |
| Confidence | Label AI output; use qualifiers for uncertain responses; never present with same certainty as DB reads |
| Feedback | Thumbs up/down minimum; corrections more valuable; route both into eval pipelines |
| Graceful degradation | Core product must work when AI provider is down — cache, fallback, or queue |
| Attribution | Clearly label AI-generated content; Art. 50 EU AI Act requires disclosure for interactive systems |
| Undo / edit | Allow editing before AI output takes effect; require confirmation for destructive actions |

## Guardrails & Safety

| Layer | Rule |
|-------|------|
| Input | Enforce length limits; detect instruction-override patterns; sanitize before prompt injection |
| Output | Scan for PII (names, emails, SSNs); use the provider's moderation endpoint if it offers one, otherwise a classifier call to a model; add a dedicated vendor (Lakera-class) for adversarial-grade detection (see Build vs. Buy) |
| High-stakes | Route medical/legal/financial AI output through human review; track review latency |
| Audit logging | Log prompts + responses separately from app logs; mask PII; set retention policy |
| Rate limiting | Rate limit to prevent abuse (injection attempts, data extraction) — beyond cost control |
| Fail closed | When guardrails time out or fail, block the release and log; never pass unfiltered. On streamed surfaces this means stop and retract; surfaces that must never show unchecked text are buffered (see Streaming Architecture) |
| Agent config lint | Before enabling tools on a feature, run `python3 scripts/check_injection_defenses.py <agent-config.json>`: it fails (exit 1) when the tool allowlist, retrieval-source allowlist, structured output validation or system-prompt isolation is missing |

## Multi-Provider Strategy

Abstract provider calls behind a single `AIProvider` interface (AI SDK's provider pattern achieves this). Never swap models for all users at once — use feature flags and circuit breakers.

Steps: provider abstraction (resolve current model IDs at each provider's docs at use-time, never hardcode a "best model"), fallback chain (primary → fallback → degraded mode) with a circuit breaker after N failures in M seconds, per-model prompt variants tested before switching traffic, and percentage A/B rollout gated on feedback, task completion, and error rates. See [references/rollout-and-observability.md](references/rollout-and-observability.md#multi-provider-rollout-steps) for the step table and eval loop patterns.

### Fallback Equivalence Gate

Do not treat API compatibility as behavioral equivalence. Before enabling a fallback, replay a representative eval set against every provider/model path and compare schema validity, tool permissions, citation requirements, refusal behavior, latency, and unit cost. For cross-cloud failover, test an allowed same-model route before switching provider families, and verify residency, key custody, prompt/log retention, and outage independence. Do not splice a second provider into a partially delivered stream; start a new request with stored tool results and idempotency keys. If any required contract fails, use a named degraded experience.

## Traps and Anti-Patterns

One list for the traps, the old Do/Avoid table and the architecture anti-patterns.

| Trap | Do instead |
|---|---|
| Treating provider uptime as guaranteed, or graceful degradation as a diagram-only requirement | Keep the core product working when AI is down, and prove the fallback path under a real provider failure (see Fallback Equivalence Gate) |
| Keeping conversation history only in browser or mobile client state | Store history server-side as the canonical record for regeneration, resume and support workflows |
| Assuming schema-shaped output is safe because the model usually behaves, or parsing prose with regex | Use schema-constrained output or tool calling (choice rule in [ai-prompt-engineering core-patterns](../ai-prompt-engineering/references/core-patterns.md#schema-design-for-llm-output)) and validate every response before persistence or side effects |
| Swapping models or providers for all users behind the same endpoint | Re-run prompt, latency and eval gates, then roll out behind flags with A/B gates |
| Logging full prompts and responses without a PII and retention policy | Mask PII and set retention (see Guardrails: Audit logging) |
| Shipping AI output without user controls or labeling | Provide regenerate, stop generating and undo on every AI output; label AI-generated content for users and audit trails |
| Testing only against mocks, or only against live calls | Use mocked LLM responses in unit tests and real calls in integration tests |
| Streaming high-stakes output before the output guardrail passes | Match streaming mode to guardrail risk; buffer until the guardrail passes where unchecked text must never show (see Streaming Architecture) |
| Regenerate or stream-retry re-executing side-effecting tool calls | Idempotency keys per (conversation, turn, call index); replay stored tool results (see Conversation & Context Management) |
| Letting the model call or own the core product workflow | The product owns the workflow; otherwise the model becomes a single point of failure and a hard-to-audit orchestrator |
| Treating tool outputs as instructions | Tool results are an indirect prompt injection vector: treat them as untrusted data and parse and validate them before acting, especially before write or send operations |
| Hiding weak application contracts behind longer prompts | Fix validation, state and orchestration in code; prompt length hides these defects and makes them harder to debug |
| Letting the AI path directly mutate durable product state | Require confirmation, undo or compensating logic; the server owns writes, the model only requests them |
| Expanding one AI service into a catch-all abstraction | Keep routing, prompt logic, persistence, moderation and analytics under separate owners; a catch-all service also makes the injection attack surface unbounded |

## Scenarios

The end-to-end flow diagram and step-by-step recipes (streaming chat with citations, schema extraction with retry, injection-guarded tool calling, multi-provider routing on rate-limit, RAG with stale-cache invalidation) live in [references/integration-scenarios.md](references/integration-scenarios.md).

## Navigation

### References
- [references/product-integration-patterns.md](references/product-integration-patterns.md) — streaming UX, structured output, persistence, and degraded-mode patterns
- [references/rollout-and-observability.md](references/rollout-and-observability.md) — cost controls, feature flags, evaluation loops, and operations
- [references/integration-scenarios.md](references/integration-scenarios.md) — end-to-end flow and step-by-step integration recipes (S1–S5)
- [references/prompt-injection-and-ai-act.md](references/prompt-injection-and-ai-act.md) — architecture-level injection defenses (the attack taxonomy is owned by ai-prompt-engineering), prompt/response logging, model version pin strategy, and a deployer-facing EU AI Act engineering checklist (disclosure, marking, logging) that points to qualified EU regulatory counsel for statute detail
- [data/sources.json](data/sources.json) — official SDK, provider, and safety/eval sources

### Related Skills

- [software-backend](../software-backend/SKILL.md) — Backend service patterns
- [software-frontend](../software-frontend/SKILL.md) — Frontend application development
- [software-realtime](../software-realtime/SKILL.md) — Real-time communication and streaming
- [software-security-appsec](../software-security-appsec/SKILL.md) — Application security and threat modeling

## Freshness Protocol

AI integration tooling changes rapidly. Freshness-check before answering questions about SDKs, model capabilities, or provider-specific patterns.

Triggers: SDK version questions, "is X still recommended?", streaming API changes, provider capability changes, new model releases.

Process: start from [data/sources.json](data/sources.json), run a targeted web search, check the changelog and migration guide of each SDK you use; app-level AI SDKs and provider SDKs release often, with breaking renames.

## Regulatory Traps

*Statute detail, status, and application dates are owned by qualified EU regulatory counsel. The engineering trigger table (prohibited practices, Art. 50 transparency, Annex III high-risk deployer duties, GPAI provider-vs-deployer split, enforcement) lives in [references/prompt-injection-and-ai-act.md](references/prompt-injection-and-ai-act.md#3-eu-ai-act-obligations); confirm scope and dates with legal before relying on any row.*

**Indirect prompt injection** is the primary exploit path: attacker-controlled data in retrieved documents, tool outputs, or web results overrides system instructions. Mitigations: isolate retrieved content with structural tags, enforce least-privilege tool scopes, validate model output before write/send operations, and test with adversarial documents in CI. Defense must be architectural — model-side mitigations reduce but do not eliminate risk.

See [references/prompt-injection-and-ai-act.md](references/prompt-injection-and-ai-act.md) for injection defence patterns and the deployer logging checklist.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
