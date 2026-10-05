# Bot Memory Integration

## Table of Contents

- [The Problem With "Last N Messages"](#the-problem-with-last-n-messages)
- [Memory Tier Selection By Bot Type](#memory-tier-selection-by-bot-type)
- [The Remember / Recall Loop](#the-remember--recall-loop)
- [Framework-Specific Wiring](#framework-specific-wiring)
- [Anti-Patterns To Block In Every Bot](#anti-patterns-to-block-in-every-bot)
- [Contradiction Handling In Bots](#contradiction-handling-in-bots)
- [Vendor Selection For Bot Memory](#vendor-selection-for-bot-memory)
- [Check](#check)

**Purpose.** Wire persistent memory from `ai-context-layer` into conversational
bots. This reference replaces the "store last N messages" default with an
extraction-first architecture that uses named patterns (P1–P16) and blocks
named anti-patterns (A1–A34) from the context-layer catalog.

Cross-skill: uses patterns and anti-patterns from
[`../ai-context-layer/references/patterns-catalog.md`](../../ai-context-layer/references/patterns-catalog.md)
and [`../ai-context-layer/references/anti-patterns-catalog.md`](../../ai-context-layer/references/anti-patterns-catalog.md).

## The Problem With "Last N Messages"

Storing raw conversation turns as "memory" is anti-pattern **A1 — Chat
transcripts as memory**. It fails because:

- noise accumulates (greetings, corrections, meta-talk);
- recall degrades as the store grows;
- contradictions are invisible;
- there is no stable fact to reference or invalidate.

The fix: **extract typed facts at write time, store the facts, keep the raw
turns separately for audit.**

## Memory Tier Selection By Bot Type

| Bot type | Primary memory pattern | Why | Operational truth (P1) |
|----------|----------------------|-----|------------------------|
| Support bot | P2 + P6 (structured + episodic-semantic) | Preferences and past issues persist across tickets | Account state, plan, billing stay in CRM/ticketing via tool calls |
| Sales bot | P4 + P6 (temporal KG + episodic-semantic) | Deal intent evolves over time; stale signals must be invalidated | Deal stage, pipeline state stay in CRM |
| Knowledge bot | P7 + P8 (LLM Wiki + evidence-bearing retrieval) | Recurring queries should hit compiled pages, not re-run RAG | Domain docs, product state stay in operational stores |
| Customer success bot | P4 + P2 (temporal KG + structured) | Per-customer config and decision history tracked temporally | Account health, usage metrics stay in backend |
| Compliance bot | P4 + audit contract (temporal + bi-temporal) | Every recommendation must be traceable; bi-temporal audit mandatory | Regulatory state stays in compliance systems |

When in doubt, start with **P2 (structured memory) + P1 (operational truth
in tools)** — the simplest composition that blocks A1.

### When to layer in P14–P16

| Bot characteristic | Add | Why |
|--------------------|-----|-----|
| Memory store grows >10k facts/user OR contradictions accumulate | **P14** sleep-time consolidation | Background dedup + contradiction resolution off the user's critical path; gate writes to block A31 (sleep-time pollution) |
| Bot ships repeatable workflows, scripts, or playbooks (sales motion, runbook execution, sales-objection handling) | **P15** procedural memory | Skill library separate from episodic/semantic; avoids re-deriving the same plan |
| Multiple bots / sub-agents share a memory store (compliance bot reads what support bot wrote; supervisor + worker pair) | **P16** multi-agent barriers | Scratch namespace + promote gate; blocks A32 (uncoordinated cross-agent writes) |
| Bot is voice-first and bundle assembly must fit ≤300ms | RA13 voice-tier dual-agent split | Fast Talker / Slow Thinker router; standard P2/P6 retrieval cannot meet the budget |

## The Remember / Recall Loop

Wire memory into the conversation turn cycle:

```text
user message arrives
  │
  ├─ recall(user_id, session_context)
  │   → fetch relevant memories from P2/P4/P6
  │   → fetch live state from P1 tools (CRM, ticketing, billing)
  │   → assemble ContextBundle with per-surface budget
  │
  ├─ generate response (LLM call with context bundle)
  │
  ├─ post-generation compliance filter
  │   → block unsafe content before it reaches the user
  │
  ├─ deliver response to user
  │
  └─ remember(conversation_turn, extracted_facts)
      → extract atomic facts from the turn
      → reconcile against existing memory (detect contradictions)
      → store with source_episode_id, confidence, validity window
      → if contradiction detected: flag (attribution / temporal / stale)
```

**Critical rule**: `remember()` runs *after* the response is delivered, not
before. It is a background operation that must not add latency to the user's
response.

## Framework-Specific Wiring

### LangGraph

Memory integrates as graph state + tool calls:

- **State**: add `user_memories: list[LearnedMemory]` and
  `recalled_context: ContextBundle` to the graph's `TypedDict` state.
- **Recall node**: runs before the response node; calls the memory service
  (Mem0 / Zep / Cognee) and injects results into state.
- **Remember node**: runs after the response node; extracts facts and writes
  to the memory service. This node should be a background task that does not
  block the user response edge.
- **Checkpoint**: checkpoint state *after* recall but *before* response, so
  replay starts with the correct memory snapshot.
- **Human handoff**: when escalating, include `user_memories` in the handoff
  payload so the operator has the full context.

### Claude Agent SDK

Memory integrates as tool definitions:

- **`recall_user_memory` tool**: called by the agent at the start of each
  turn to fetch relevant memories. Returns structured facts, not raw text.
- **`remember_fact` tool**: called by the agent after a turn to store a new
  extracted fact. The agent decides what is worth remembering (self-editing
  variant — P3).
- **System prompt injection**: alternatively, inject recalled memories into
  the system prompt before each turn (simpler, less agent autonomy).
- **When to use P3 vs P2**: use P3 (self-editing) when the agent should
  decide what to remember; use P2 (app-orchestrated) when the application
  controls memory writes and the agent only reads.

### Plain Async Python

For simple bots without LangGraph overhead:

```python
async def handle_turn(user_id: str, message: str) -> str:
    memories = await memory_service.recall(user_id, query=message)
    live_state = await tools.fetch_account(user_id)
    bundle = assemble_context(memories, live_state, surface="chat")

    response = await llm.generate(system=bundle.prompt, user=message)
    response = compliance_filter(response)

    # Background: extract and store facts
    asyncio.create_task(
        memory_service.remember(user_id, episode=message, response=response)
    )
    return response
```

## Anti-Patterns To Block In Every Bot

| Anti-pattern | Signal in bot code | Fix |
|-------------|-------------------|-----|
| A1 Chat transcripts as memory | `messages.append({"role": "user", "content": msg})` stored as "memory" | Extract facts first, store structured memory |
| A2 Vector DB as system of record | Bot reads account state from embeddings instead of CRM | Use P1 tool calls for operational truth |
| A5 Prompt stuffing | Entire conversation history injected into system prompt | Use ContextBundle with per-surface token budget |
| A10 No tenant scope | Memory recalled without `user_id` or `tenant_id` filter | Enforce owner_scope on every recall |
| A11 No forget path | User says "forget my preferences" but nothing happens | Wire `forget()` to the bot's command handler |
| A13 No provenance | Bot says "you told me X" but can't cite when or where | Store `source_episode_id` on every fact |

## Contradiction Handling In Bots

When the `remember()` step detects a contradiction:

- **Attribution conflict** (two sources say different things): store both,
  flag the page, and surface to the user: "I have conflicting information
  about X. Which is correct?"
- **Temporal conflict** (new value supersedes old): close the old validity
  window, store the new fact with `supersedes_id`. No user action needed.
- **Stale conflict** (fact past its TTL): filter from recall by default.
  If the user asks about the stale fact, qualify: "Last time I checked
  (date), X was true. Want me to verify?"

## Vendor Selection For Bot Memory

Route from `ai-context-layer/references/vendor-landscape-2026-04.md`:

- **Mem0** — best for P2 + P6 (support bots, personal assistants).
  Managed, drop-in. Pro tier for graph.
- **Zep / Graphiti** — best for P4 (sales bots, customer success).
  Temporal validity, non-destructive invalidation.
- **Cognee** — best for P5 + P7 (knowledge bots). Poly-store, four-verb
  lifecycle, graph viewer.
- **Letta** — best for P3 (long-running agents with self-editing memory).
  OS-style context management.
- **LangGraph Store** — best for P2 when already using LangGraph.
  Application-owned, namespaced.

## Check

The bot memory integration is working if: (1) no raw conversation turns are
stored as the primary memory artifact, (2) a returning user gets personalized
context without re-stating preferences, (3) the bot can explain *why* it
believes a fact about the user by citing a specific episode, (4) a user
requesting "forget X" sees the fact removed from future recall, and (5)
contradictions between old and new user statements are handled at ingest,
not surfaced as inconsistent bot answers.
