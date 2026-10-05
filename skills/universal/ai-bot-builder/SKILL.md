---
name: ai-bot-builder
description: "Builds production AI bots with Python for support, sales, and custom domains. Use when designing conversation flows, personas, escalation, or LangGraph state."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# AI Bot Builder

Use this skill to build, ship, and iterate on conversational AI bots — support, sales, or domain-specific — using pure Python frameworks and AI coding agents.

This skill absorbs `ai-langgraph-bots` and is the single entry point for stateful bot implementation, including LangGraph graph design, checkpoints, and human-in-the-loop.

Default posture: explicit conversation state, typed tool contracts, deterministic escalation rules, guardrails before launch, compliance filtering before responses reach users, and analytics from day one. No visual workflow tools — code-first only.

## When to Use This Skill

- Building a support bot, sales bot, or domain-specific conversational agent
- Designing conversation flows, fallback trees, and state machines
- Choosing a Python bot framework (LangGraph, Claude Agent SDK, Pydantic AI); voice frameworks belong to ai-voice-bots
- Migrating a bot from visual workflow tools (n8n, Langflow) to native Python
- Integrating bots with ticketing, CRM, knowledge bases, or booking systems
- Designing human handoff and escalation protocols
- Adding post-generation compliance/safety filtering to bot responses
- Planning bot analytics, A/B testing, and improvement loops
- Implementing LangGraph graph state, checkpoints, and human approval for bots
- Testing multi-turn conversation quality and regressions

## When NOT to Use This Skill

| Need | Route to |
|------|----------|
| Voice pipeline engineering (STT, TTS, telephony) | [`../ai-voice-bots/SKILL.md`](../ai-voice-bots/SKILL.md) |
| Agent architecture decisions (build-vs-not, shape) | [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md) |
| RAG / retrieval system design | [`../ai-rag/SKILL.md`](../ai-rag/SKILL.md) |
| KB/vector-brain construction, ingest scripts, SQL, manifests, eval seeds | [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md) |
| Prompt engineering and structured outputs | [`../ai-prompt-engineering/SKILL.md`](../ai-prompt-engineering/SKILL.md) |
| N8N / visual workflow automation | [`../software-workflow-automation/SKILL.md`](../software-workflow-automation/SKILL.md) |
| Help center content design | [`../product-help-center/SKILL.md`](../product-help-center/SKILL.md) |
| Agent eval harnesses and red-team packs | [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) |

## Quick Reference

| Need | Default | Notes |
|------|---------|-------|
| Choose a bot framework | `references/framework-selection.md` | Pure Python: LangGraph, Claude Agent SDK, Pydantic AI; voice → [`../ai-voice-bots/SKILL.md`](../ai-voice-bots/SKILL.md) |
| Design conversation flows | `references/conversation-design.md` | State machines, fallback trees, slot filling, multi-turn |
| Define bot personality | `references/persona-design.md` | Tone, brand voice, safety boundaries |
| Build a support bot | `references/support-bot-patterns.md` | Zendesk/Intercom/Freshdesk, KB grounding, resolution tracking |
| Build a sales bot | `references/sales-bot-patterns.md` | CRM integration, lead qualification, demo booking |
| Add human handoff | `references/handoff-to-human.md` | Escalation triggers, warm handoff, queue routing |
| Route across channels | `references/channel-routing.md` | Web chat, WhatsApp, SMS, email, in-app |
| Wire persistent memory | `references/bot-memory-integration.md` | remember/recall loop, memory tier by bot type, anti-pattern blocks |
| Defend against injection | `references/injection-and-jailbreak-defense.md` | Spotlighting, canary, tool-output sanitization, red-team pack |
| Migrate from n8n / Langflow | `references/migration-from-n8n.md` | Node mapping, secret hygiene, gap closure, before/after |
| Measure and improve | `references/bot-analytics-improvement.md` | CSAT, containment rate, A/B, improvement loops |
| Deploy to production | `references/production-deployment.md` | Serving, scaling, canary, cost per conversation |
| Roll out new bot versions without dropping sessions | `references/stateful-rollout-and-blue-green.md` | Cohort canary, checkpoint migration, graceful drain, rollback |
| Rotate provider keys and survive provider outages | `references/secret-rotation-and-model-fallback.md` | Two-key window, hot reload, fallback chain, circuit breakers |
| Pick a hosting platform (Vercel, Fly.io, Railway, Render, Cloudflare) | [`../software-paas-hosting/references/agent-hosting-matrix.md`](../software-paas-hosting/references/agent-hosting-matrix.md) | Text-bot stacks B1–B4 with concrete platform choices |
| Design LangGraph state | `references/graph-design-patterns.md` | State, nodes, edges, routers, subgraphs |
| Add checkpoints or HITL | `references/state-checkpoints-and-hitl.md` | Persistence, replay, approval, recovery |
| Test graph workflows | `references/testing-and-production.md` | Graph testing, observability, handoff |

## Default Workflow

1. **Classify** the bot type (support, sales, or custom domain) and identify the primary user task.
2. **Define persona** — tone, brand voice, safety boundaries, and guardrailed behavior.
3. **Design conversation flow** — state machine with happy path, fallbacks, slot filling, and escalation triggers.
4. **Choose framework** — select from pure Python options based on state needs, tool integration, and deployment target.
5. **Integrate domain tools** — ticketing, CRM, knowledge base, calendar, or custom APIs via MCP or direct SDK.
6. **Add guardrails** — input validation, output filtering, PII handling, topic boundaries, and abuse prevention.
7. **Build evaluation suite** — multi-turn evals, edge cases, adversarial inputs, and regression baselines.
8. **Deploy with analytics** — instrument containment rate, CSAT, escalation rate, cost per conversation, and set up improvement loops.

## Bot Type Decision Tree

```
What is the bot's primary job?
├── Answer questions / resolve issues
│   ├── Has a knowledge base or help center? → Support Bot (KB-grounded)
│   └── Needs to query live systems (orders, accounts)? → Support Bot (tool-using)
├── Qualify leads / book meetings / handle objections
│   └── Sales Bot
├── Execute workflows (approvals, scheduling, data entry)
│   └── Workflow Bot — consider LangGraph graph-shaped orchestration
└── Multi-domain or unclear
    └── Start with the dominant use case; add domains incrementally
```

## Framework Selection

| Framework | Best for | State model | Streaming | Voice support |
|-----------|----------|-------------|-----------|---------------|
| **LangGraph** | Complex multi-step bots with branching, checkpoints, HITL | Explicit typed graph state | Yes (via callbacks) | Via Pipecat/LiveKit integration |
| **Claude Agent SDK** | Tool-using bots with Anthropic models | SDK-managed conversation | Yes (native) | No (text-only) |
| **Pydantic AI** | Lightweight bots with structured outputs | Pydantic models | Yes | No |

Voice frameworks (Pipecat, LiveKit Agents) are owned by [`../ai-voice-bots/SKILL.md`](../ai-voice-bots/SKILL.md) — this skill is not voice/STT/TTS. Go there for framework choice, imports, and pipeline code; come back here for conversation state, persona, and guardrails once the graph/agent "brain" is decided.

Default: **LangGraph** for complex stateful bots, **Claude Agent SDK** for simpler tool-using bots, **ai-voice-bots' pick** when voice is primary. For linear decision cascades without cycles or checkpoints, consider plain async Python — LangGraph's dependency chain (`langchain-core` and its transitive packages) may not be worth the overhead.

> **Pydantic AI:** its major-version rewrite moved extension points to a composable `capabilities=[...]` API and removed `history_processors=`, `event_stream_handler=` and `prepare_tools=` from the `Agent` constructor. Check which major version you have installed before copying an example, and read the current upgrade guide at [ai.pydantic.dev](https://ai.pydantic.dev/). Migration notes → [references/framework-selection.md](references/framework-selection.md).

Full comparison → [references/framework-selection.md](references/framework-selection.md)

## LangGraph for Bots

Reach for LangGraph when the bot needs cycles, explicit state, checkpoints, or human approval — not as a default. For a linear cascade (spam → router → support → reply) with no cycles or HITL, plain async Python with if/elif routing is simpler and has zero framework overhead.

Key guardrails:

- **Python compatibility:** look up the Python range your LangGraph release supports on the [LangGraph releases page](https://github.com/langchain-ai/langgraph/releases) before upgrading Python. The framework ships minor releases often, so any "safe ceiling" copied from a doc goes stale within months; pin the version your CI tests.
- **Use `START` for new code.** `set_entry_point()` is still documented as equivalent to `add_edge(START, key)`, but the `START` edge is clearer and matches current examples. Import `from langgraph.graph import StateGraph, START, END`.
- **State before nodes.** `TypedDict` with `total=False`, reducer-annotated fields for accumulated data.
- **Pure nodes.** `(state, *, clients) -> dict` via `functools.partial` — testable without monkey-patching.
- **Place node boundaries around recoverable work and approval gates.** With a checkpointer, LangGraph persists state at super-step boundaries; choose the required durability mode and make side effects idempotent. Put approval gates before destructive, financial, or irreversible actions. See [references/state-checkpoints-and-hitl.md](references/state-checkpoints-and-hitl.md).

Full depth:
- Graph patterns (state schemas, routers, subgraphs, anti-patterns) → [references/graph-design-patterns.md](references/graph-design-patterns.md)
- Checkpoints + HITL (interrupt, Command resume, replay, audit) → [references/state-checkpoints-and-hitl.md](references/state-checkpoints-and-hitl.md)
- Testing (three-tier pyramid, red-team pack) → [references/testing-and-production.md](references/testing-and-production.md)

## Conversation Design Principles

1. **State machine, not script.** Model conversations as states with transitions, not linear scripts. Every state has: entry conditions, expected user inputs, bot actions, and exit transitions.
2. **Fallback hierarchy.** Unknown input → clarify → rephrase → offer alternatives → escalate. Never dead-end.
3. **Slot filling over free chat.** When collecting structured data, use explicit slots with validation. Confirm before committing.
4. **Escalation is not failure.** Design escalation as a first-class path with context transfer, not a last resort.
5. **Turn budget.** Set maximum turns before forced escalation from the p90 turns-to-resolution in your own logs, per bot type, and use the same number as `max_turns` in the `conversation_eval.py` rubric.

Full depth → [references/conversation-design.md](references/conversation-design.md)

## Production Defaults

- **Language:** Python, async by default. Pin whatever your CI actually tests, not whatever the docs said last quarter — see the LangGraph Python-compatibility note above.
- **Framework:** FastAPI for serving, selected bot framework for orchestration
- **Streaming:** SSE or WebSocket for real-time responses
- **Cost tracking:** Token counting per conversation, cost per resolution metric
- **Prompt-prefix caching:** the main multi-turn cost lever, because every turn resends the history. Keep the system prompt and tool definitions byte-stable and first (no timestamps or per-user values in them, tools in a fixed order) and put the cache breakpoint at the end of the history. Summarizing or rewriting history invalidates the cached prefix, so summarize only at a planned cache break. `scripts/bot_cost_estimator.py --cache` models this write-then-read pattern.
- **Guardrails:** Input validation (max length, encoding, null bytes), output filtering, PII detection, topic boundaries
- **Bot-identity disclosure (EU AI Act Art. 50(1), applies from 2 Aug 2026):** tell users they are talking to an AI at the latest at the first interaction, not only "when asked". The exception covers only cases where this is obvious to a reasonably well-informed, observant person given the context, so do not rely on it by default. See `startup-compliance-enterprise-readiness/references/regulatory-overlays.md` for the full obligation set and dates.
- **Compliance filter:** Post-generation check before any response reaches the user — block investment advice, tipping-off language, unmasked PII. Use regex for fast checks; LLM call only for ambiguous cases. Essential for regulated industries (finance, healthcare).
- **PII scrubbing:** Run card number regex before phone regex — phone patterns are greedy and consume card numbers if run first. Order: URLs → emails → card numbers → phone numbers.
- **Human escalation:** Always-available path with context transfer. Prepare operator-facing summary (structured handoff) alongside user-facing confirmation.
- **Dedup:** Redis TTL keys, not in-memory. Two levels: exact event ID, with a TTL at least the channel provider's maximum webhook redelivery window (look it up in that provider's webhook docs), and a text hash with a TTL about as long as the double-submit window you see in your logs. Survives restarts, scales across instances.
- **Rubric-graded outcomes (when output quality is load-bearing):** for structured reports, formal/regulated responses, or document generation, add a revision loop — the task agent produces output, an isolated grader agent scores it against a rubric *in its own context window* (no access to the writer's chain-of-thought), the writer revises until the rubric passes or `max_iterations` is hit. See `references/testing-and-production.md` for the pattern, which is framework-agnostic; check whether your agent runtime has a native outcome or grader hook before building the loop yourself.
- **Conversation memory:** Extract structured facts from each turn, not raw message logs (blocks anti-pattern A1 from [`ai-context-layer`](../ai-context-layer/references/anti-patterns-catalog.md)). Pick a memory pattern: P2 (support bots), P4 (sales bots with temporal facts), P6 (episodic-semantic for general bots) from [`ai-context-layer/patterns-catalog.md`](../ai-context-layer/references/patterns-catalog.md). Wire the `remember / recall` loop per [references/bot-memory-integration.md](references/bot-memory-integration.md). Load recalled facts only for support tiers — spam filter and router stay single-turn to avoid history-bias.
- **Domain knowledge:** Keep curated knowledge retrieval separate from operational truth, memory, safety, and tone. If the bot uses SQL-backed RAG, stage database rollout before semantic retrieval: schema/RLS, minimal lexical search, content seed, ranking tuning, evals, then vector or full-text indexes after capability probes. Keep simple lexical retrieval when evals pass; defer embeddings, editor workflows, localization, and search infrastructure until traffic, corpus size, quality, or audit triggers justify them.
- **Testing:** Three-tier test pyramid — unit tests for pure nodes, integration tests with mocked HTTP (respx), golden eval harness split into deterministic (regex/fast-path) and LLM tiers. Run deterministic tests in CI on every push; LLM eval on demand.
- **Analytics:** Containment rate, CSAT, escalation rate, cost per conversation from day one. Write every decision to an analytics table (conversation_id, decision, route, confidence, tier, latency).
- **Docker:** Non-root user, minimal base image (Alpine or distroless), read-only filesystem, `no-new-privileges`, secrets from manager not env files in production.
- **Model identifiers:** Keep the model ID in config/env, not hardcoded in prompts or code samples — provider families rename and reprice on a cadence of months, not years (tiering, tier names, and prices have all shifted materially within a single year across major vendors). Pin the exact ID your CI tests in one place (`MODEL_ID` env var or a config file), and re-verify it against the vendor's current model list before every deploy, not from memory.

## Intent Automation Gate

Classify each supported intent as `answer`, `read`, `propose`, `mutate`, or `handoff`, then give it an explicit tool allowlist, confirmation rule, fallback, and success signal. Unknown intents and failed preconditions must take the handoff or safe-answer path; they must not inherit the nearest intent's tools. Before launch, measure wrong-action and failed-handoff rates per intent alongside containment, because higher containment can hide harmful automation.

## Known Traps

- Treating escalation as a fallback only. Support and sales bots need an operator path that is designed upfront, instrumented, and tested like any other successful outcome.
- Hiding orchestration inside one giant prompt or one giant LangGraph node. That makes handoff, retries, and root-cause analysis much harder when the bot misroutes or loops.
- Letting curated knowledge, user memory, live account state, safety policy, and tone collapse into one prompt block. Mature bots assemble typed slices with evidence and trust levels so each concern can be tested separately.
- Adding semantic search, long-term memory, or editorial workflow before the bot has eval failures, corpus pressure, real usage, or an operating team that needs those controls.
- Sharing one conversation state model across web chat, email, SMS, and messaging channels without channel-specific limits. Attachment handling, latency expectations, and retry semantics differ materially.
- Applying compliance, policy, or PII checks after tools have already fired or messages have already been queued. Guardrails must sit before side effects and before user-visible output.
- Treating synthetic "happy path" transcripts as production proof. Multi-turn regressions usually appear in recovery paths, partial-tool failures, and human-handoff boundaries.
- Treating prompt injection as a content-moderation problem instead of a security problem. The LLM is not a security boundary — defense lives in code around it: spotlighting, canary tokens, tool-output sanitization, privilege separation, and a red-team pack in CI. See [references/injection-and-jailbreak-defense.md](references/injection-and-jailbreak-defense.md).
- Wiring a managed memory vendor (Mem0, Zep, Letta, Cognee) directly into bot core logic with vendor-specific calls scattered across nodes/tools. Memory vendors churn on schema and pricing; put a thin `MemoryService` interface between the bot and the vendor SDK so a vendor swap is a one-file change, not a rewrite.

## Common Anti-Patterns

- Using LangGraph by default for short linear bots where plain async Python would be simpler, easier to test, and easier to operate.
- Letting one prompt own routing, retrieval, tool planning, tone, and policy at the same time instead of separating those concerns.
- Rebuilding ticketing, CRM, or booking semantics inside prompt text instead of using typed tool contracts and explicit field validation.
- Measuring success only with aggregate CSAT or containment while ignoring escalation quality, incorrect automation, and cost per resolved conversation.

## Navigation

**References**
- [references/index.md](references/index.md) — Reference navigation map
- [references/framework-selection.md](references/framework-selection.md) — Pure Python framework comparison
- [references/conversation-design.md](references/conversation-design.md) — State machines, fallback trees, multi-turn flows
- [references/persona-design.md](references/persona-design.md) — Bot personality, tone, brand voice
- [references/support-bot-patterns.md](references/support-bot-patterns.md) — Support bot integration patterns
- [references/sales-bot-patterns.md](references/sales-bot-patterns.md) — Sales bot integration patterns
- [references/handoff-to-human.md](references/handoff-to-human.md) — Escalation orchestration
- [references/channel-routing.md](references/channel-routing.md) — Omnichannel routing
- [references/bot-memory-integration.md](references/bot-memory-integration.md) — Persistent memory wiring (remember/recall loop, pattern selection, anti-pattern blocks)
- [references/injection-and-jailbreak-defense.md](references/injection-and-jailbreak-defense.md) — Direct/indirect injection, spotlighting, canary, red-team pack
- [references/migration-from-n8n.md](references/migration-from-n8n.md) — Migration from n8n/Langflow/Agent Builder to native Python
- [references/bot-analytics-improvement.md](references/bot-analytics-improvement.md) — Metrics and improvement loops
- [references/production-deployment.md](references/production-deployment.md) — Serving and scaling
- [references/secret-rotation-and-model-fallback.md](references/secret-rotation-and-model-fallback.md) — Secret rotation and model fallback
- [references/stateful-rollout-and-blue-green.md](references/stateful-rollout-and-blue-green.md) — Stateful rollout and blue-green deployment
- [references/graph-design-patterns.md](references/graph-design-patterns.md) — LangGraph state, nodes, edges, subgraphs
- [references/state-checkpoints-and-hitl.md](references/state-checkpoints-and-hitl.md) — LangGraph persistence, replay, approval
- [references/testing-and-production.md](references/testing-and-production.md) — LangGraph testing and observability

**Assets**
- [assets/support-bot-spec.md](assets/support-bot-spec.md) — Support bot specification template
- [assets/sales-bot-spec.md](assets/sales-bot-spec.md) — Sales bot specification template
- [assets/conversation-flow-template.md](assets/conversation-flow-template.md) — Conversation state machine template
- [assets/bot-safety-checklist.md](assets/bot-safety-checklist.md) — Pre-launch safety gate
- [assets/handoff-protocol.md](assets/handoff-protocol.md) — Human handoff contract template
- [assets/pricing-template.json](assets/pricing-template.json) — Empty `--pricing` rates file for `bot_cost_estimator.py`
- [assets/templates/end-to-end-bot-recipe.md](assets/templates/end-to-end-bot-recipe.md) — Zero-to-shipped walkthrough (LangGraph + Twilio); voice pipelines belong to [`ai-voice-bots`](../ai-voice-bots/SKILL.md)

**Scripts**
- `python3 scripts/conversation_eval.py --input conversations.jsonl [--min-pass-rate 1.0] [--warnings-fail]` — Multi-turn conversation evaluator. Have the bot record each confirmation it asks for as a `request_confirmation` tool call (`{"action": "issue_refund", "args": {"order_id": "55"}}`). The evaluator then fails any state-changing call that no confirmed request covers, and exits 1 when the pass rate is below `--min-pass-rate` (default 1.0). Set `require_confirmation_tool: true` in the rubric once the bot emits the call, so a transcript without it fails instead of passing. Without the call, a text heuristic reports warnings only; pass `--warnings-fail` to make those warnings fail the gate too
- `python3 scripts/bot_cost_estimator.py --pricing rates.json --model <name> --avg-turns 8` — Per-conversation cost estimator. Ships no prices: copy `assets/pricing-template.json`, fill in rates from each provider's pricing page, and pass it with `--pricing`; without it the script exits 2 and prints no estimate. It also accepts the dated price file of [ops-cost-optimization](../ops-cost-optimization/SKILL.md)'s `cost_estimator.py` (`checked` date plus `models` with `input_per_1m`/`output_per_1m` and optional cache rates), so one file can feed both the per-call and the per-conversation estimate
- `python3 scripts/red_team_pack.py --input responses.jsonl` — Prompt-injection, PII-leak, and jailbreak detection against bot responses

**Data**
- [data/sources.json](data/sources.json) — Curated external sources

## Related Skills

- [../ai-agents/SKILL.md](../ai-agents/SKILL.md) — Agent architecture and build-vs-not decisions
- [../ai-voice-bots/SKILL.md](../ai-voice-bots/SKILL.md) — Voice pipeline engineering (STT/TTS, telephony)
- [../ai-rag/SKILL.md](../ai-rag/SKILL.md) — Retrieval and grounding for KB-powered bots
- [../ai-context-layer/SKILL.md](../ai-context-layer/SKILL.md) — User profiles, memory, context assembly
- [../ai-context-layer/references/conversational-surfaces-cross-platform.md](../ai-context-layer/references/conversational-surfaces-cross-platform.md) — Cross-platform composition recipe: how a Telegram/Discord/WhatsApp/Slack bot composer relates to iOS/Android/web composers via a shared `EvidenceBundle` and typed answer contract; LangGraph + Mem0 baseline; with-model and without-model paths
- [../ai-prompt-engineering/SKILL.md](../ai-prompt-engineering/SKILL.md) — System prompts and structured outputs
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) — MCP tool integration
- [../agents-subagents/SKILL.md](../agents-subagents/SKILL.md) — Specialist sub-bot delegation
- [../agents-hooks/SKILL.md](../agents-hooks/SKILL.md) — Bot safety hooks and guardrails
- [../software-ai-integration/SKILL.md](../software-ai-integration/SKILL.md) — Chat UI, streaming, multi-provider routing
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — FastAPI serving patterns
- [../software-realtime/SKILL.md](../software-realtime/SKILL.md) — WebSocket/SSE transport
- [../qa-agent-testing/SKILL.md](../qa-agent-testing/SKILL.md) — Eval harnesses and regression packs
- [../product-help-center/SKILL.md](../product-help-center/SKILL.md) — Help center design for bot grounding

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
