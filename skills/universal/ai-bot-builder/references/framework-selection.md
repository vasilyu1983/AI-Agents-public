# Framework Selection for AI Bots

Use this reference when choosing a code-first framework for building a conversational AI bot. Default scope is Python; **Mastra** is the supported TypeScript path for teams shipping bots to Vercel/Cloudflare/Netlify edge runtimes. No visual workflow tools.

> For visual workflow tools (N8N, Langflow), see [`../software-workflow-automation/SKILL.md`](../../software-workflow-automation/SKILL.md).

## Table of Contents

- [Decision Gate](#decision-gate)
- [Framework Comparison](#framework-comparison)
- [LangGraph](#langgraph)
- [Claude Agent SDK](#claude-agent-sdk)
- [Pydantic AI](#pydantic-ai)
- [Pipecat](#pipecat)
- [LiveKit Agents](#livekit-agents)
- [Mastra (TypeScript)](#mastra-typescript)
- [When to Combine Frameworks](#when-to-combine-frameworks)
- [Migration Paths](#migration-paths)

## Decision Gate

```
Does your bot need voice (phone, IVR, real-time speech)?
├── Yes → Pipecat (default) or LiveKit Agents
│         └── For conversation logic inside the voice pipeline:
│             └── LangGraph or Claude Agent SDK as the "brain"
└── No (text only) →
    Is the runtime TypeScript (edge / Vercel / Cloudflare / Netlify)?
    ├── Yes → Mastra (TS-first, Zod tools, edge deployers)
    └── No (Python) →
        Does it need complex multi-step workflows with branching, checkpoints, or HITL?
        ├── Yes → LangGraph
        └── No →
            Is Anthropic Claude the primary model?
            ├── Yes → Claude Agent SDK
            └── No → Pydantic AI (model-agnostic)
```

## Framework Comparison

| Criterion | LangGraph | Claude Agent SDK | Pydantic AI | Pipecat | LiveKit Agents |
|-----------|-----------|-----------------|-------------|---------|----------------|
| **Primary use** | Complex stateful bots | Tool-using Claude bots | Lightweight structured agents | Voice + multimodal bots | Voice bots with room infra |
| **State model** | Explicit typed graph state | SDK-managed conversation | Pydantic models | Pipeline processor state | Room + agent state |
| **Control flow** | Graph: nodes, edges, routers | Sequential tool calls | Sequential / parallel tool calls | Pipeline: processors in chain | Pipeline: agent session (STT→LLM→TTS) |
| **Streaming** | Via callbacks/events | Native streaming | Yes | Native (audio + text) | Native (audio + text) |
| **Checkpoints** | Built-in persistence | Manual | Manual | N/A | N/A |
| **Human-in-the-loop** | First-class (interrupt, approve, resume) | Manual implementation | Manual implementation | Via pipeline interruption | Via room events |
| **Voice support** | No (integrate with Pipecat/LiveKit) | No | No | Primary (STT→LLM→TTS) | Primary (STT→LLM→TTS) |
| **Model agnostic** | Yes (any LLM) | Anthropic only | Yes (any LLM) | Yes (any LLM) | Yes (any LLM) |
| **Testing** | Graph transition testing, replay | Standard unit/integration | Standard unit/integration | Pipeline processor testing | Room simulation testing |
| **Deployment** | Any Python hosting | Any Python hosting | Any Python hosting | Requires WebSocket/WebRTC | Requires LiveKit server |
| **Ecosystem** | LangChain tools, LangSmith tracing | Anthropic tools, MCP | Logfire observability | Daily/Twilio transports | LiveKit Cloud, plugins |
| **Learning curve** | Medium-high (graph concepts) | Low | Low | Medium (pipeline concepts) | Medium (room concepts) |
| **Best for bots** | Support bots with complex routing, multi-step resolution | Simple Q&A bots, tool-calling assistants | Lightweight agents, structured data extraction | Voice support/sales bots | Voice bots needing rooms |

## LangGraph

**When to choose:** The bot has complex, branching conversation flows that benefit from explicit state management, checkpoints, and human approval gates.

**Python version: look it up before pinning.** Read the supported Python range for the LangGraph release you will pin on the [LangGraph releases page](https://github.com/langchain-ai/langgraph/releases) and its `pyproject.toml`; the decision it feeds is your runtime image's Python version. Check the installed dependency chain in CI before upgrading Python.

**When NOT to choose LangGraph:** If your bot's decision flow is a linear cascade (e.g., spam → router → support → reply) without cycles, checkpoints, or human-in-the-loop gates, consider a plain async Python function. Check the dependency tree and supported Python range of the release you would deploy; a `TypedDict` state dict with explicit if/elif routing may be enough for a linear pipeline.

**Bot patterns:**

- **Support bot with routing:** Classify intent → route to specialist subgraph → resolve or escalate. Each path is an explicit graph branch with its own tools and fallback behavior.
- **Sales bot with qualification:** Intake → qualify (BANT/MEDDPICC scoring) → route to demo booking or nurture. Checkpoint at qualification decision for human review.
- **Workflow bot:** Multi-step data collection with validation, approval gates, and compensating actions on failure.

**Architecture:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from functools import partial

class BotState(TypedDict, total=False):
    messages: list          # Conversation history
    intent: str             # Classified intent
    slots: dict             # Collected data slots
    escalation_reason: str
    turn_count: int
    decision: str           # Terminal decision
    reply_text: str         # Final response

# Nodes are pure functions: (state, clients) → partial state update
async def classify_intent(state: BotState, *, llm_client) -> dict:
    # LLM classifies user intent from latest message
    ...
    return {"intent": "support", "turn_count": state.get("turn_count", 0) + 1}

async def handle_support(state: BotState, *, llm_client, kb_client) -> dict:
    # Tool calls: search KB, create ticket, check order status
    ...
    return {"decision": "ANSWER", "reply_text": answer}

def check_escalation(state: BotState) -> Literal["escalate", "continue", "resolve"]:
    # Deterministic: confidence < threshold, turn_count > max, or explicit request
    ...

# Inject clients via partial — keeps nodes testable without monkey-patching
graph = StateGraph(BotState)
graph.add_node("classify", partial(classify_intent, llm_client=openai))
graph.add_node("support", partial(handle_support, llm_client=openai, kb_client=kb))
graph.add_node("escalate", escalate_to_human)
graph.add_node("resolve", format_resolution)
graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route_by_intent)
graph.add_conditional_edges("support", check_escalation)
```

**Key rules:**
- Define state before nodes. State is the contract. Use `TypedDict(total=False)` so nodes return partial updates.
- One node, one job: classify, call tool, transform, or format.
- Inject external clients via `functools.partial`, not global imports.
- Use `graph.add_edge(START, "first_node")` — not the deprecated `set_entry_point()`.
- Routing functions return node name strings or `END`.
- Explicit conditional edges over hidden prompt-level branching.
- Checkpoints before risky side effects.
- Full depth → [`graph-design-patterns.md`](graph-design-patterns.md), [`state-checkpoints-and-hitl.md`](state-checkpoints-and-hitl.md)

## Claude Agent SDK

**When to choose:** The bot uses Anthropic Claude as the primary model, needs tool calling, and the conversation flow is relatively linear (no complex branching requiring graph state).

**Bot patterns:**

- **Q&A support bot:** System prompt defines persona and boundaries. Tools provide KB search, account lookup, and ticket creation. Claude manages multi-turn naturally.
- **Simple sales assistant:** Tools for CRM lookup, calendar availability check, and meeting booking. Claude handles qualification conversationally.

**Architecture:**

```python
import os
import anthropic

client = anthropic.Anthropic()

tools = [
    {
        "name": "search_knowledge_base",
        "description": "Search the support knowledge base for articles matching the user's question.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_support_ticket",
        "description": "Create a support ticket when the issue cannot be resolved automatically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["subject", "description"]
        }
    }
]

# Bot loop
messages = []
while True:
    user_input = get_user_message()
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model=os.environ["ANTHROPIC_MODEL_ID"],  # pin the current model ID in config, verify against provider docs
        max_tokens=1024,
        system=SUPPORT_BOT_SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )

    # Handle tool use, then continue conversation
    ...
```

**Key rules:**
- System prompt carries persona, boundaries, and escalation rules.
- Tools are the bot's capabilities — keep them well-typed and documented.
- Use `stop_reason == "tool_use"` to detect when Claude wants to call a tool.
- For complex branching, consider LangGraph instead.

## Pydantic AI

**When to choose:** Lightweight bot with structured inputs/outputs, model-agnostic, and the conversation flow is simple enough that Pydantic model validation provides sufficient structure.

**Bot patterns:**

- **Data extraction bot:** Collect structured information from conversation (lead details, issue reports, feedback forms).
- **Classification bot:** Route incoming messages to the right team or workflow based on structured classification.

**Architecture:**

```python
import os
from pydantic_ai import Agent
from pydantic import BaseModel

class LeadInfo(BaseModel):
    name: str
    company: str
    use_case: str
    budget_range: str | None = None
    timeline: str | None = None

sales_agent = Agent(
    f"anthropic:{os.environ['ANTHROPIC_MODEL_ID']}",  # pin the current model ID in config
    result_type=LeadInfo,
    system_prompt="You are a sales qualification bot. Collect lead information through natural conversation.",
)

result = await sales_agent.run("Hi, I'm interested in your API product for my startup")
lead = result.data  # Typed LeadInfo
```

**The stable V2 line began with v2.0.0 on 2026-06-23 and is a breaking rewrite, not an incremental bump.** Current first-party migration docs still map `history_processors=` → `capabilities=[ProcessHistory(...)]`, `event_stream_handler=` → `capabilities=[ProcessEventStream(...)]`, and `prepare_tools=` → `capabilities=[PrepareTools(...)]`; the separate Harness package supplies composed capabilities. Do not treat v2.0.0 as the latest release or hard-pin it without checking the current changelog. Teams on v1.x should budget a real migration pass and resolve current V1 deprecations first. [Checked 2026-09-07 against the version policy, V1→V2 migration map, capabilities docs, and Harness overview.]

## Pipecat

**When to choose:** The bot needs voice capabilities (phone, IVR, real-time speech) as a primary modality. Pipecat is the default voice bot framework — maximum flexibility and vendor-neutral building blocks, but more verbose configuration than LiveKit.

**Bot patterns:**

- **Voice support bot:** Phone IVR with STT → LLM → TTS pipeline. Handles VAD, barge-in, and DTMF fallback.
- **Voice sales bot:** Outbound or inbound sales calls with natural conversation, CRM integration, and meeting booking.

> Full Pipecat patterns → [`../../ai-voice-bots/references/pipecat-patterns.md`](../../ai-voice-bots/references/pipecat-patterns.md)

**Pipeline shape** (no imports on purpose: Pipecat moves module paths and renames aggregators between releases, so take them from the current Pipecat docs or ai-voice-bots): transport in → STT → user-turn aggregator → LLM or graph processor → TTS → assistant-turn aggregator → transport out.

## LiveKit Agents

**When to choose:** Voice bot needs room-based infrastructure (multiple participants, recording, screen sharing), you're already using LiveKit's WebRTC stack, or you want a cleaner API with less boilerplate than Pipecat. LiveKit has built-in turn detection based on their own open-weights model.

> Full LiveKit patterns → [`../../ai-voice-bots/references/livekit-agents-patterns.md`](../../ai-voice-bots/references/livekit-agents-patterns.md)

## OpenAI Realtime API (Speech-to-Speech)

**When to consider:** Direct speech-to-speech is attractive when latency matters and the session design can meet the required transcript, intervention, and audit controls.

OpenAI's Realtime speech-to-speech path can generate audio directly without a separate application STT→text→TTS cascade. Measure end-to-end latency on the chosen transport, model, and network before choosing it for speed.

**Trade-off:** Realtime sessions can emit input and output transcript events, but transcript availability is not the same as a synchronous text approval gate before audio playback. If policy requires inspecting every utterance before users hear it, design and test an application-level hold or use a cascaded text path. See [OpenAI's Realtime conversation guide](https://developers.openai.com/api/docs/guides/realtime-conversations) and [live-session transcript events](https://developers.openai.com/api/docs/guides/live-conversations).

**Use when:** A measured latency benefit matters and the chosen session design meets the application's transcript, intervention, and audit requirements. Route voice pipeline implementation to `ai-voice-bots`.

## Mastra (TypeScript)

**When to choose:** TypeScript-first team shipping conversational bots to edge runtimes (Vercel, Cloudflare Workers, Netlify) where Python is a poor fit.

Check the [Mastra changelog and package release](https://github.com/mastra-ai/mastra/releases) before selecting an API or deployer; examples written for an older release may no longer run.

**Why it's on this list:** Mastra combines agent, workflow, memory, evaluation, and tracing primitives in a TypeScript stack. Compare the capabilities needed by this bot against the installed release.

**Core primitives:**

- **Agents** — model-driven loops with working memory and conversation memory as first-class primitives.
- **Workflows** — deterministic step graphs. **Separate from agents by design** — compose both, don't conflate them.
- **Tools** — Zod schemas; the schema doubles as the prompt-facing description the model sees.
- **Mastra Model Router** — provider selection; check supported models and fallback behavior in the current docs.
- **Evals + tracing** — built-in, no separate service needed for day-one observability.

**Bot patterns:**

- **Support bot on edge:** Agent (intent + tool calls) → workflow (deterministic ticket creation, KB lookup) → handoff to human via webhook. Deploy to Cloudflare Workers, scale to zero between sessions.
- **Sales bot embedded in Next.js app:** Agent with conversation memory keyed by user id; Vercel deployer ships it next to the app.
- **Multi-tenant chatbot:** Working memory scoped per tenant, Mastra Cloud handles autoscaling + rollbacks.

For implementation, copy the current [Mastra agent](https://mastra.ai/docs/agents/overview) and [workflow](https://mastra.ai/docs/workflows/overview) examples, then pin and test the installed package. The old `new Workflow`/`new Step` and object-shaped `model` example did not match the current first-party examples.

**When NOT to choose Mastra:**

- Team is Python-first → LangGraph or Pydantic AI.
- You need LangSmith specifically (org-wide tracing standard) → LangGraph.js.
- Heavy voice/telephony — Mastra has no first-class voice pipeline; pair Pipecat (Python) with the agent in a sidecar, or use OpenAI Realtime via the OpenAI Agents SDK.
- You need long-running graph checkpointing with HITL interrupt/resume semantics matching LangGraph — Mastra workflows are deterministic but the resumable-graph idiom is different; verify it covers your case.

**Deployment:**

- `@mastra/deployer-vercel`, `@mastra/deployer-cloudflare`, `@mastra/deployer-netlify` — scale-to-zero edge.
- **Mastra Cloud** for managed hosting with Studio (UI), GitHub-connected deploys, autoscaling, instant rollbacks, eval dashboards.

**Mastra vs LangGraph.js:** LangGraph.js is the lower-level graph primitive with the strongest checkpoint/Store story; Mastra is the higher-level batteries-included framework. If you're picking between them and don't already have a LangSmith dependency, Mastra is the faster path; pick LangGraph.js when you need the graph + Store as your primary persistence model.

**Sources:** <https://mastra.ai/docs>, <https://github.com/mastra-ai/mastra>

## Multi-Agent Routing: Handoffs vs Agents-as-Tools

When a bot routes between specialists, OpenAI's Agents SDK docs codify a hard decision rule worth applying regardless of framework:

- **Handoffs** — use when a specialist agent should *own the next user-facing response*. Control transfers; the specialist replies to the user directly. The SDK `handoff()` accepts `input_type` (a small Pydantic model of model-generated handoff metadata), `input_filter` (scrub/transform context before transfer), and `on_handoff` callbacks.
- **Agents-as-tools** — use when the orchestrator *retains control of the final answer* and specialists are called as bounded helpers whose output the orchestrator composes.
- **Default to agents-as-tools in grey-area cases.** Routing logic stays in one place and traces are easier to debug. Reach for handoffs only when the specialist genuinely should take over the conversation.

Source: OpenAI Agents SDK docs (`openai.github.io/openai-agents-python/handoffs/`); open-source at `github.com/openai/openai-agents-python`. The rule is design guidance, not a benchmarked result.

## When to Combine Frameworks

Common combinations:

| Pattern | Frameworks | Why |
|---------|-----------|-----|
| Voice bot with complex logic | Pipecat + LangGraph | Pipecat handles audio pipeline, LangGraph manages conversation state and branching |
| Multi-model text bot | LangGraph + Claude Agent SDK | LangGraph for orchestration, Claude SDK for Anthropic-specific tool calling within nodes |
| Voice bot with structured extraction | Pipecat + Pydantic AI | Pipecat handles voice, Pydantic AI structures extracted data |

**Integration pattern:** The voice/pipeline framework handles I/O and transport. The conversation framework handles state, routing, and tool orchestration. Keep them loosely coupled via typed message interfaces.

## Migration Paths

| From | To | When | How |
|------|----|------|-----|
| **n8n / Langflow** | **Native Python** | Need observability, testing, compliance, or Python-version control | See SKILL.md "Migrating from Visual Workflow Tools" section |
| Claude Agent SDK | LangGraph | Bot needs branching, checkpoints, or HITL | Extract tool definitions, wrap in graph nodes, add state model |
| Pydantic AI | LangGraph | Bot grows beyond simple structured output | Keep Pydantic models as state, add graph orchestration |
| Pydantic AI | Claude Agent SDK | Committing to Anthropic models | Replace Agent with anthropic.Anthropic client, keep tool schemas |
| Text-only (any) | Pipecat | Adding voice modality | Keep conversation logic, wrap in Pipecat pipeline as LLM processor |
| LangGraph | Plain async | Bot is a linear cascade, no cycles/checkpoints/HITL | Keep node functions, replace graph with async orchestrator function, drop `langgraph` dep |

### n8n → Python Migration Checklist

When replacing an n8n bot with native Python:

1. Extract all prompts verbatim from n8n Set/Config nodes (they're string values in the workflow JSON)
2. Map n8n nodes to Python functions: IF nodes → routing function, HTTP nodes → typed client, Code nodes → port directly
3. Move hardcoded secrets (Telegram tokens in URL fields are common) to env vars immediately
4. Add what n8n can't do: compliance filter, conversation memory, structured observability, rate limiting, input validation
5. If multiple implementations exist (n8n + Agent Builder + CustomGPT), merge the best of each
6. Build a golden test suite from real reviewed conversations before cutting over
7. Run shadow traffic (both systems in parallel) before gradual rollout
