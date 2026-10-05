---
name: ai-coding-agents-provider-runtime
description: "Designs provider runtimes for coding agents. Use when modeling model abstraction, streaming semantics, tool-call normalization, retries, or fallback routing."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Provider Runtime

Use this skill to design or review the model-provider layer inside a coding-agent runtime: provider abstraction, streaming semantics, tool-call protocol normalization, context-window strategy, retries, and fallback routing.

This skill owns the model-facing runtime surface for coding agents.

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should providers and streaming semantics be normalized? | [references/provider-abstraction-and-stream-normalization.md](references/provider-abstraction-and-stream-normalization.md) | Stable provider interface, streaming event model, and tool-call normalization |
| How should retries, context windows, and fallback routing work? | [references/context-window-retries-and-fallback-routing.md](references/context-window-retries-and-fallback-routing.md) | Provider selection, truncation rules, retry classes, and fallback policy |
| How does OpenAI Codex check local OSS provider readiness? | [references/openai-codex-local-oss-provider-readiness.md](references/openai-codex-local-oss-provider-readiness.md) | Ollama/LM Studio readiness workflow, model presence, version gates, fetch/load diagnostics, and capability-driven selection |
| Where does each capability live per provider, and what must be checked? | [references/provider-capability-matrix.md](references/provider-capability-matrix.md) | Per-capability lookup guide (streaming, structured output, tool calls, vision, caching) plus a capability-flag interface and shim design notes |

## When To Use

- Design multi-provider support for a coding-agent CLI
- Normalize tool-call and structured-output behavior across providers
- Review streaming token handling or partial message assembly
- Add retry, timeout, or fallback policy for model requests
- Decide how context windows and prompt-cache constraints affect runtime behavior

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| Tool registry and tool execution | [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md) |
| Settings and policy precedence | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) |
| Generic LLM provider strategy and serving | [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md), [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md) |
| LLM features inside an application (structured output, guardrails, app-level provider routing) rather than a coding-agent runtime | [`../software-ai-integration/SKILL.md`](../software-ai-integration/SKILL.md) |

## Default Workflow

1. **Define the provider contract.** Keep request shape, streaming events, tool calls, usage accounting, and error taxonomy behind one internal interface.
2. **Normalize partial output.** Providers stream differently, so convert them into one local event model before the rest of the runtime sees them.
3. **Separate capability from policy.** A provider may support long context, prompt caching, or tool calls, but the runtime still decides when to use them.
4. **Model context-window behavior explicitly.** Decide how truncation, summarization, replay, and prompt-cache constraints affect agent turns and resume flows.
5. **Separate task budget from token budget.** See [Output-Limit Recovery And Budgets](#output-limit-recovery-and-budgets).
6. **Classify retries and recoveries.** Transport failure, rate limiting, provider timeout, malformed tool output, `max_output_tokens`, and policy refusal should not share the same retry behavior.
7. **Design fallback routing deliberately.** Fallbacks should preserve semantics where possible and degrade visibly when they cannot.
8. **Track provider usage.** Cost, token counts, cache hits, and latency should be attributable per provider and per turn.
9. **Test cross-provider parity.** Ensure the same agent workflow behaves acceptably across supported providers, not only the default one. Use [assets/templates/parity-test-checklist.md](assets/templates/parity-test-checklist.md) as the per-provider pass/fail matrix.

## Host Rules

- Keep one internal message and event model even when upstream providers differ.
- Normalize tool-call arguments and structured outputs before downstream handling.
- Preserve provider-specific capabilities as optional flags, not hard-coded assumptions.
- Do not collapse `max_output_tokens` into a generic model failure if the runtime supports bounded recovery or continuation prompts.
- Make fallback routing observable to the user and to telemetry.
- Avoid silent semantic drift when a fallback model cannot match the primary provider’s behavior.
- Keep retry logic bounded and class-specific; retry transparently only before the first streamed delta.

## Output-Limit Recovery And Budgets

Treat an output-limit stop as its own normalized finish class, separate from context overflow, transport truncation, timeout, and user cancellation. Persist the provider response ID or continuation handle, emitted item boundaries, usage, and last complete semantic unit. Resume only through a provider-supported continuation path or a new request carrying an explicit bounded summary; never concatenate a guessed suffix or replay side-effecting tool calls blindly. Cap continuation attempts and make partial output visible when recovery cannot complete.

Keep task budget independent from provider token counters. Track input/context, cached input, reasoning, output, tool-call, wall-time, retry, and external-spend fields when available, marking unsupported dimensions as unknown rather than zero. A provider response can fit its token limit and still exceed the task budget; conversely, an output-limit recovery may remain inside the task budget. Emit `recovery_attempted`, `recovery_succeeded`, and terminal reason so downstream evals can tell recovery from ordinary success.

## Build Order

1. Define one internal provider contract and event model.
2. Normalize provider streams into that model before downstream use.
3. Add capability flags for tools, caching, context length, and structured output.
4. Add class-specific retry and timeout handling.
5. Add context-window policy and fallback routing.
6. Add usage accounting, task-budget tracking, and recovery telemetry.

## Core Invariants

- The rest of the runtime should consume one provider-agnostic message model.
- Provider capability does not equal runtime policy.
- Retry policy must depend on failure class, not provider brand.
- Fallback routing must be visible whenever semantics may change.
- Task-budget pressure and token-budget pressure must stay distinguishable.

- “Compatible” tool calling is not the same as “identical” tool calling. Always normalize and test the actual edge behavior.

## Failure Modes

- Treating provider streams as identical and leaking provider-specific quirks upward.
- Counting `max_output_tokens` as a generic hard failure when bounded recovery exists.
- Retrying malformed tool output as if it were a network glitch.
- Silent fallback to a weaker model with different semantics.
- Cost and usage accounting that cannot explain which provider path actually ran.

## Minimal Viable Version

- One provider interface for requests, streams, tool calls, and usage.
- One normalized event model for partial output.
- One retry classifier separating transport, rate limit, timeout, and policy errors.
- One context-window policy for truncation or summarization.
- One observable fallback path with explicit user-visible degradation.

## What Strong Implementations Add

- Prompt-cache-aware turn planning.
- Distinct task budgets for long-running agent loops.
- Bounded continuation or recovery prompts for `max_output_tokens`.
- Per-provider latency, cost, cache-hit, and fallback telemetry.
- Cross-provider parity tests for the same workflow and tool traffic.
- **Toolshim adapters** for providers without native function calling, hidden behind the same event contract.
- **ACP-delegated "agent-as-provider"** routing, where an external agent reached over stdio behaves as a provider row in the matrix.

## Known Traps

- Letting provider-specific event shapes leak upward until the rest of the runtime is implicitly coupled to one vendor’s streaming contract.
- Treating model compatibility as a binary label and not testing tool-call edge cases, truncation behavior, or structured-output failure modes.
- Retrying every provider error indiscriminately and turning permanent failures into latency explosions or duplicate tool traffic.
- Falling back across providers without reconciling context windows, cache semantics, safety settings, or tool schema differences.
- Hiding fallback and recovery behavior because the final output looked acceptable, even though runtime cost and determinism changed materially.

## Common Anti-Patterns

- Building provider support as `if provider == x` branches without a stable contract.
- Letting provider-specific event shapes leak into the rest of the runtime.
- Treating every failure as retryable.
- Advertising “compatible providers” without testing tool-call edge behavior.
- Hiding fallback decisions because the output “looked close enough.”

## Expert Judgment Calls

These are the calls a senior reviewer makes that a checklist alone will not catch.

- **One adapter plus a seam until the second provider; after that, adding a provider costs only a conformance-suite run.** A `Provider` interface, capability-flag matrix, and cross-provider parity suite earn their cost at the second production provider, not the first. A single well-tested adapter with a documented seam (where the interface will go) is the right amount of abstraction for a one-provider runtime. Once the second provider is real, an abstraction that makes the next provider a code branch rather than a conformance run is the wrong abstraction.
- **"Same vendor, smaller model" is not an automatically safe fallback.** Smaller models in the same family frequently have materially worse tool-call argument fidelity and structured-output adherence than the primary model, even with an identical API surface. Treat every fallback target — same-vendor or cross-vendor — as untrusted until it has passed the same parity suite as the primary.
- **Retry budgets must be sized per class and per user-visible turn, not globally.** A single global retry counter shared across transport errors, rate limits, and malformed-tool-output will let one degraded dependency silently eat the whole latency budget for a turn the user is actively waiting on. Give each retry class its own budget, and give the overall turn a hard ceiling independent of any single class.
- **Auto-fallback from cloud to local is a privacy and quality decision, not a routing convenience.** If a runtime silently downgrades from a cloud provider to a local model when cloud auth or availability fails, that changes what data leaves the machine and what quality/tool-call guarantees apply. This must be a visible, loggable decision — never an invisible one made purely to keep the turn alive.
- **Cost dashboards that only show per-provider token spend hide the actual failure signal.** A runaway agent loop and a legitimately expensive single turn look identical in aggregate token cost. Instrument task-budget and token-budget as separate telemetry dimensions from the start — retrofitting this distinction after an incident is far more expensive than building it in.
- **The retry-safety boundary is the first emitted delta.** Before any content or tool-call delta has reached consumers, a failed request may be retried transparently. After a delta was emitted, and especially after tool-call arguments streamed or a tool ran, a retry is a new attempt: retract or mark the partial output, and never re-dispatch tool calls from the failed attempt.
- **Reasoning state round-trips verbatim and is not portable.** Within a tool-use loop, return thinking or reasoning items unchanged, including signatures or encrypted payloads; stripping, editing, or reordering them breaks the request or degrades reasoning. On cross-provider fallback, drop them, record the loss, and treat the fallback as a semantic change.
- **Keep the cache prefix byte-stable.** Order each request stable-to-volatile (tools, then system, then history), keep tool ordering deterministic, and keep timestamps, per-turn tool-list changes, and reordered MCP tools out of the prefix; any of these silently zeroes cache hits. A fallback to another model or provider starts cold, so its cost includes the lost cache.
- **A provider "supports tool calls" claim is a spectrum, not a boolean.** Native parallel tool calls, streamed partial arguments, and toolshim-synthesized calls all satisfy a naive "supports tools: true" flag but have different failure modes under malformed output. Do not let a capability flag hide which of these three a given provider actually implements.

## Endpoint And Auth-Mode Choices

- **Prefer the endpoint that round-trips reasoning state** across turns (a stored response ID or encrypted reasoning items), and check the vendor's deprecation notices before choosing a surface. Track cache hits as their own telemetry dimension; they price differently from uncached input.
- **Keep auth-mode-specific transport behind the provider contract.** A subscription or account session and an API key may use different transports and auth headers, but both must normalize to the same streaming events, tool calls, and usage. Consumers never branch on which auth path ran, and account-session logic never leaks into the API-key path or the reverse.

## Cross-Platform Patterns (Goose)

Goose (open-source Rust coding agent) broadens the provider-runtime surface beyond the Claude Code lineage. Three patterns are worth importing.

### Toolshim — tool-calling over non-function-calling models

Some providers (older open-weights models, completion-only endpoints) do not expose a native function-calling contract. A **toolshim** is a provider-side adapter that synthesizes tool-call semantics on top of text generation: it prompts the model in a structured way, parses the output into normalized tool-call events, and emits them through the same internal event model as native function-calling providers.

- **Pattern:** model the toolshim as a provider adapter, not as a tool-layer hack. The rest of the runtime must not be able to tell whether function calling was native or synthesized.
- **Anti-pattern:** branching in the tool registry or agent loop on "provider supports tools." That couples upstream code to provider brand and makes retries / streaming / partial output inconsistent.
- **Recipe:** add a `supports_native_tool_calls: bool` capability flag; when false, route through the shim adapter. The shim must emit the same streaming event shape, the same tool-call IDs, and the same malformed-tool-output retry class as native providers.

### Agent-as-provider — ACP-delegated providers

An external coding agent (Claude Code, Codex, another Goose instance) reachable over **Agent Client Protocol (ACP)** stdio can be used as a provider. The local runtime sends a prompt and a tool schema; the remote agent does its own loop and returns completions plus structured tool events.

- **Pattern:** model ACP-delegated agents through the same `Provider` contract as LLM vendors. Capability flags advertise which turns route to agents (long-horizon planning, complex multi-file edits) versus direct LLM calls.
- **Anti-pattern:** treating the delegated agent as a remote runtime (see `ai-coding-agents-surfaces`). That is the reverse direction — there, your agent is the server to an editor. Here, the remote agent is *your provider*. Conflating the two produces double-stack approval bridges.
- **Recipe:** expose an `acp://` provider URI scheme. Attribute usage, cost, and latency to the delegated-agent provider like any other row in the per-provider telemetry table. Falling back from an agent-provider to a bare-LLM provider is a *semantic* fallback and must be user-visible.

### Adding a provider is a conformance run

Provider coverage is not a count to aspire to; each supported provider is a row that has passed the parity suite. Read provider-specific context limits, caching APIs, and structured-output parameters from [references/provider-capability-matrix.md](references/provider-capability-matrix.md) and the provider's current docs, not from memory. When using a vendor's open-source CLI as a design reference, do not assume its auth or entitlement paths are still live.

- **Pattern:** treat every new provider as a conformance test against the normalized event model and tool-call contract, not as a bespoke branch.
- **Anti-pattern:** calling a provider "supported" when only chat completion has been exercised — no tool calls, no streaming edge cases, no `max_output_tokens` recovery.
- **Recipe:** a cross-provider parity test suite that runs the same three workflows (code review, edit-and-test, plan-then-execute) against every registered provider and scores tool-call fidelity, streaming stability, and recovery behavior.

## Navigation

### References

- [references/provider-abstraction-and-stream-normalization.md](references/provider-abstraction-and-stream-normalization.md) — Provider interfaces, streaming event models, and tool-call normalization
- [references/context-window-retries-and-fallback-routing.md](references/context-window-retries-and-fallback-routing.md) — Context-window policy, retry classes, and fallback routing
- [references/openai-codex-local-oss-provider-readiness.md](references/openai-codex-local-oss-provider-readiness.md) — OpenAI Codex local OSS provider readiness checks, model availability, version gates, and remediation classes
- [references/provider-capability-matrix.md](references/provider-capability-matrix.md) — Per-capability lookup guide, shim design notes, and a capability-flag interface for Claude, OpenAI, Gemini, and Ollama

### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for provider-runtime design

### Related Skills

- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md)
- [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md)
- [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md)
- [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md)
- [`../software-ai-integration/SKILL.md`](../software-ai-integration/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
