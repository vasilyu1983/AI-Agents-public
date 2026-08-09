---
name: ai-coding-agents-provider-runtime
description: "Designs provider runtimes for coding agents. Use when modeling model abstraction, streaming semantics, tool-call normalization, retries, or fallback routing."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Provider Runtime

Use this skill to design or review the model-provider layer inside a coding-agent runtime: provider abstraction, streaming semantics, tool-call protocol normalization, context-window strategy, retries, and fallback routing.

This skill owns the model-facing runtime surface for coding agents. It is the main missing layer when trying to generalize Claude Code-derived patterns toward Codex-class portability.

## ASCII Flow

```text
agent turn
  |
  v
provider selection
  capability needs + model policy + cost/latency + context window
  |
  v
request normalization
  messages + tools + structured outputs + cache hints + metadata
  |
  v
provider stream
  tokens + tool calls + errors + usage events
  |
  v
runtime event model
  normalized deltas + retries/fallbacks + final response
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should providers and streaming semantics be normalized? | [`references/provider-abstraction-and-stream-normalization.md`](references/provider-abstraction-and-stream-normalization.md) | Stable provider interface, streaming event model, and tool-call normalization |
| How should retries, context windows, and fallback routing work? | [`references/context-window-retries-and-fallback-routing.md`](references/context-window-retries-and-fallback-routing.md) | Provider selection, truncation rules, retry classes, and fallback policy |
| How does OpenAI Codex check local OSS provider readiness? | [`references/openai-codex-local-oss-provider-readiness.md`](references/openai-codex-local-oss-provider-readiness.md) | Ollama/LM Studio readiness workflow, model presence, version gates, fetch/load diagnostics, and capability-driven selection |
| What exactly differs across Claude, OpenAI, Gemini, and Ollama today? | [`references/provider-capability-matrix.md`](references/provider-capability-matrix.md) | Feature-by-feature comparison (streaming, structured output, tool calls, vision, caching) plus a capability-flag interface and shim design notes |

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
| Tool registry and tool execution | [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md) |
| Settings and policy precedence | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) |
| Generic LLM provider strategy and serving | [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md), [`../ai-llm-inference/SKILL.md`](../ai-llm-inference/SKILL.md) |

## Default Workflow

1. **Define the provider contract.** Keep request shape, streaming events, tool calls, usage accounting, and error taxonomy behind one internal interface.
2. **Normalize partial output.** Providers stream differently, so convert them into one local event model before the rest of the runtime sees them.
3. **Separate capability from policy.** A provider may support long context, prompt caching, or tool calls, but the runtime still decides when to use them.
4. **Model context-window behavior explicitly.** Decide how truncation, summarization, replay, and prompt-cache constraints affect agent turns and resume flows.
5. **Separate task budget from token budget.** Long-running coding loops often need a workflow or task budget independent of per-request token accounting.
6. **Classify retries and recoveries.** Transport failure, rate limiting, provider timeout, malformed tool output, `max_output_tokens`, and policy refusal should not share the same retry behavior.
7. **Design fallback routing deliberately.** Fallbacks should preserve semantics where possible and degrade visibly when they cannot.
8. **Track provider usage.** Cost, token counts, cache hits, and latency should be attributable per provider and per turn.
9. **Test cross-provider parity.** Ensure the same agent workflow behaves acceptably across supported providers, not only the default one.

## Host Rules

- Keep one internal message and event model even when upstream providers differ.
- Normalize tool-call arguments and structured outputs before downstream handling.
- Preserve provider-specific capabilities as optional flags, not hard-coded assumptions.
- Do not collapse `max_output_tokens` into a generic model failure if the runtime supports bounded recovery or continuation prompts.
- Make task-budget pressure and token-budget pressure visible as different runtime concerns.
- Make fallback routing observable to the user and to telemetry.
- Avoid silent semantic drift when a fallback model cannot match the primary provider’s behavior.
- Keep retry logic bounded and class-specific.

## Scratch-Rebuild Coverage

- Coverage strength:
  strong for provider abstraction, stream normalization, class-specific retries, and visible fallback routing instead of pretending providers are interchangeable
- Missing for faithful reproduction:
  task-budget handling distinct from token accounting, bounded `max_output_tokens` recovery, and explicit continuation or recovery-message patterns are still too implicit
- Required additions:
  document task-budget-versus-token-budget behavior, `max_output_tokens` recovery as its own failure class, and the telemetry fields needed to explain when a provider run recovered versus failed outright

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

- **Don't build the full abstraction before the second provider is real.** A `Provider` interface, capability-flag matrix, and cross-provider parity suite earn their cost at the second production provider, not the first. A single well-tested adapter with a documented seam (where the interface will go) is the right amount of abstraction for a one-provider runtime; building the matrix for a hypothetical future provider is premature and adds real maintenance drag for no current benefit.
- **"Same vendor, smaller model" is not an automatically safe fallback.** Smaller models in the same family frequently have materially worse tool-call argument fidelity and structured-output adherence than the primary model, even with an identical API surface. Treat every fallback target — same-vendor or cross-vendor — as untrusted until it has passed the same parity suite as the primary.
- **Retry budgets must be sized per class and per user-visible turn, not globally.** A single global retry counter shared across transport errors, rate limits, and malformed-tool-output will let one degraded dependency silently eat the whole latency budget for a turn the user is actively waiting on. Give each retry class its own budget, and give the overall turn a hard ceiling independent of any single class.
- **Auto-fallback from cloud to local is a privacy and quality decision, not a routing convenience.** If a runtime silently downgrades from a cloud provider to a local model when cloud auth or availability fails, that changes what data leaves the machine and what quality/tool-call guarantees apply. This must be a visible, loggable decision — never an invisible one made purely to keep the turn alive.
- **Cost dashboards that only show per-provider token spend hide the actual failure signal.** A runaway agent loop and a legitimately expensive single turn look identical in aggregate token cost. Instrument task-budget and token-budget as separate telemetry dimensions from the start — retrofitting this distinction after an incident is far more expensive than building it in.
- **A provider "supports tool calls" claim is a spectrum, not a boolean.** Native parallel tool calls, streamed partial arguments, and toolshim-synthesized calls all satisfy a naive "supports tools: true" flag but have different failure modes under malformed output. Do not let a capability flag hide which of these three a given provider actually implements.

## OpenAI Codex: Responses API vs Chat-Completions Dispatch

Source: `codex-rs/core/` (dispatch logic), `codex-rs/chatgpt/` (ChatGPT account auth path); OpenAI migration guide https://developers.openai.com/api/docs/guides/migrate-to-responses

**Responses API is now the recommended path for all new agentic work.** The Assistants API is sunset as of August 26, 2026. Key reasons to prefer Responses API for coding-agent runtimes:

- Built-in tool primitives: `code_interpreter`, `file_search`, remote MCP tools available without custom tool wiring.
- Stateful context management without the threading model overhead of Assistants.
- 40-80% better cache utilization in agentic workloads compared to Chat Completions (per OpenAI's own benchmarks). This gain is specific to reasoning models: it comes from persisting chain-of-thought tokens across turns via `previous_response_id` (or encrypted reasoning items when stateless) — Chat Completions has no equivalent, so non-reasoning-model workloads should not expect this improvement. Track cache-hit events as a separate telemetry dimension — they have different cost multipliers than uncached inference.
- Better performance on reasoning models and multi-turn loops.

**Judgment call:** the 40-80% figure is real but conditional — do not cite it when advising a runtime that only calls non-reasoning models. Verify which model family is in play before using this number to justify a migration.

Codex's core provider layer supports two distinct OpenAI dispatch paths:

| Path | Crate / module | Auth mechanism | Use case |
|------|---------------|----------------|---------|
| Responses API | `codex-rs/core/` | API key (`OPENAI_API_KEY`) | Recommended path for new agentic work; structured tool calls, streaming, built-in tools, prompt caching |
| ChatGPT account | `codex-rs/chatgpt/` | Browser session / OAuth (ChatGPT account login via `codex login`) | Users who access OpenAI through ChatGPT Plus/Team, not a paid API key |

The `codex-rs/chatgpt` crate hosts first-party ChatGPT-account API surfaces (per its own README, "should be primarily built and maintained by OpenAI employees"); as the codebase has grown, session/OAuth token acquisition has moved toward a dedicated `codex-rs/login` crate rather than living entirely inside `chatgpt`. Either way, this path does not use the standard `Authorization: Bearer <API_KEY>` header — it authenticates from the ChatGPT session. The provider contract (streaming events, tool calls, usage) is normalized to the same internal event model by both paths — upstream consumers of the provider layer should not branch on which path ran. Codex's crate layout evolves quickly (dozens of crates now exist beyond the two discussed here); re-check the current tree before citing an exact file path.

Design rule: when adding a new OpenAI API surface (e.g. a new beta endpoint), decide at crate-selection time whether it belongs in the core Responses API path or requires a separate auth-specific crate. Do not add ChatGPT-account authentication logic to the core API path, and do not add Responses API logic to the `chatgpt` crate.

## Cross-Platform Patterns (Goose)

Goose (Rust; originally built by Block) broadens the provider-runtime surface beyond the Claude Code lineage. Block donated Goose to the newly formed Agentic AI Foundation (AAIF) at the Linux Foundation on April 7, 2026 — the same announcement bundled Anthropic's donation of the Model Context Protocol (MCP) and OpenAI's donation of AGENTS.md as separate, parallel contributions to the same foundation. Do not describe Anthropic or OpenAI as co-founders of Goose itself; they contributed different projects to AAIF, not to Goose's codebase. The repository moved to `github.com/aaif-goose/goose`. "Goose 2.0" (the project's own informal name for its April 2026 architecture overhaul) ships ACP as the default server interface (not a subcommand), which affects how ACP-delegated provider routing is framed below. Three patterns are worth importing.

### Toolshim — tool-calling over non-function-calling models

Some providers (Ollama, older open-weights, some completion-only endpoints) do not expose a native function-calling contract. A **toolshim** is a provider-side adapter that synthesizes tool-call semantics on top of text generation: it prompts the model in a structured way, parses the output into normalized tool-call events, and emits them through the same internal event model as native function-calling providers.

- **Pattern:** model the toolshim as a provider adapter, not as a tool-layer hack. The rest of the runtime must not be able to tell whether function calling was native or synthesized.
- **Anti-pattern:** branching in the tool registry or agent loop on "provider supports tools." That couples upstream code to provider brand and makes retries / streaming / partial output inconsistent.
- **Recipe:** add a `supports_native_tool_calls: bool` capability flag; when false, route through the shim adapter. The shim must emit the same streaming event shape, the same tool-call IDs, and the same malformed-tool-output retry class as native providers.

### Agent-as-provider — ACP-delegated providers

An external coding agent (Claude Code, Codex, another Goose instance) reachable over **Agent Client Protocol (ACP)** stdio can be used as a provider. The local runtime sends a prompt and a tool schema; the remote agent does its own loop and returns completions plus structured tool events.

- **Pattern:** model ACP-delegated agents through the same `Provider` contract as LLM vendors. Capability flags advertise which turns route to agents (long-horizon planning, complex multi-file edits) versus direct LLM calls.
- **Anti-pattern:** treating the delegated agent as a remote runtime (see `ai-coding-agents-remote-runtime`). That is the reverse direction — there, your agent is the server to an editor. Here, the remote agent is *your provider*. Conflating the two produces double-stack approval bridges.
- **Recipe:** expose an `acp://` provider URI scheme. Attribute usage, cost, and latency to the delegated-agent provider like any other row in the per-provider telemetry table. Falling back from an agent-provider to a bare-LLM provider is a *semantic* fallback and must be user-visible.

### Provider matrix as a coverage expectation

A general-purpose coding-agent runtime should aspire to cover ≥12 providers, using the Goose 2.0 baseline (15+ providers) as the upper bound: Anthropic, OpenAI (Responses API), Google/Gemini (Gemini API + Vertex), Azure OpenAI, AWS Bedrock, OpenRouter, Ollama, LM Studio, plus ACP-delegated agents, and additional cloud or hosted providers. Gemini-specific notes: the Gemini API supports 1M-token context on long-context models, `cachedContents` for explicit context caching, and `responseMimeType: "application/json"` + `responseSchema` for structured output — all three matter for coding-agent workloads. The Gemini CLI (`github.com/google-gemini/gemini-cli`) is an open-source (Apache 2.0) TypeScript first-party reference implementation; Google discontinued its free consumer tier in June 2026 (source still builds and runs for enterprise-license or paid-API-key users) — if you use it as a design reference, do not assume free-tier auth is still a live entitlement path worth modeling. If your provider abstraction makes it expensive to add the 12th provider, the abstraction is wrong.

- **Pattern:** treat every new provider as a conformance test against the normalized event model and tool-call contract, not as a bespoke branch.
- **Anti-pattern:** calling a provider "supported" when only chat completion has been exercised — no tool calls, no streaming edge cases, no `max_output_tokens` recovery.
- **Recipe:** a cross-provider parity test suite that runs the same three workflows (code review, edit-and-test, plan-then-execute) against every registered provider and scores tool-call fidelity, streaming stability, and recovery behavior.

## Navigation

### References

- [`references/provider-abstraction-and-stream-normalization.md`](references/provider-abstraction-and-stream-normalization.md) — Provider interfaces, streaming event models, and tool-call normalization
- [`references/context-window-retries-and-fallback-routing.md`](references/context-window-retries-and-fallback-routing.md) — Context-window policy, retry classes, and fallback routing
- [`references/openai-codex-local-oss-provider-readiness.md`](references/openai-codex-local-oss-provider-readiness.md) — OpenAI Codex local OSS provider readiness checks, model availability, version gates, and remediation classes
- [`references/provider-capability-matrix.md`](references/provider-capability-matrix.md) — Cross-provider feature matrix, shim design notes, and a capability-flag interface for Claude, OpenAI, Gemini, and Ollama

### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for provider-runtime design

### Related Skills

- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md)
- [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md)
- [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md)
- [`../ai-llm/SKILL.md`](../ai-llm/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Provider protocols change quickly. Preserve the runtime architecture, but verify current request and streaming contracts against the target providers before implementation.
- “Compatible” tool calling is not the same as “identical” tool calling. Always normalize and test the actual edge behavior.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
