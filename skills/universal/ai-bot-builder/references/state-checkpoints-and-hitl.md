# State, Checkpoints, and Human-in-the-Loop

## Table of Contents

- [When to Checkpoint](#when-to-checkpoint)
- [Checkpointer Setup](#checkpointer-setup)
- [Thread IDs and Config](#thread-ids-and-config)
- [Interrupt Patterns (HITL)](#interrupt-patterns-hitl)
- [Resume with Command](#resume-with-command)
- [Replay and Time-Travel](#replay-and-time-travel)
- [Recovery Patterns](#recovery-patterns)
- [Audit Trail](#audit-trail)
- [Anti-Patterns](#anti-patterns)
- [Check](#check)

**Purpose.** Wire LangGraph persistence, human approval gates, and recovery for bots that cannot safely run end-to-end without a pause.

**API check.** Before implementing a pause, check the [LangGraph releases page](https://github.com/langchain-ai/langgraph/releases) and interrupt docs for the version you pin; use its documented `interrupt()` and `Command(resume=...)` pattern.

## When to Checkpoint

Add a checkpointer when any of the following are true:

- The bot has turns that span minutes or hours (async approval, email back-and-forth)
- A turn involves a destructive, financial, legal, or irreversible action
- You need to resume after a worker crash mid-turn
- You need to audit how the bot reached a decision (replay)
- The bot is multi-user and conversations are concurrent

For a single-turn, stateless Q&A bot with no side effects, skip the checkpointer.

With a checkpointer, LangGraph normally saves state at each super-step boundary; choose node boundaries for recoverable work and review before side effects. The [persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence) describe this behavior. Set `durability="sync"` when a step must be persisted before the next one executes; `"async"` can continue while a write is in flight, and `"exit"` omits intermediate persistence. Test recovery for the selected mode and make external side effects idempotent.

## Checkpointer Setup

Pick the checkpointer by environment:

| Checkpointer | When | Notes |
|--------------|------|-------|
| `InMemorySaver` | Tests, local dev | Lost on process exit |
| `SqliteSaver` | Single-instance bots, small prod | File-backed, no concurrent writes |
| `PostgresSaver` | Multi-instance production | Requires Postgres; enable async variant |
| `RedisSaver` | Ephemeral state, low-latency | Use for short-TTL checkpoints |

### Postgres (production default)

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# One-time schema setup
async with AsyncPostgresSaver.from_conn_string(PG_DSN) as saver:
    await saver.setup()

# Build graph with checkpointer
async with AsyncPostgresSaver.from_conn_string(PG_DSN) as saver:
    app = graph.compile(checkpointer=saver)
    result = await app.ainvoke(
        {"message": user_msg, "user_id": user_id},
        config={"configurable": {"thread_id": conversation_id}},
    )
```

### SQLite (single-instance)

```python
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async with AsyncSqliteSaver.from_conn_string("bot_state.db") as saver:
    app = graph.compile(checkpointer=saver)
```

### In-memory (tests)

```python
from langgraph.checkpoint.memory import InMemorySaver
app = graph.compile(checkpointer=InMemorySaver())
```

## Thread IDs and Config

Every invocation needs a `thread_id` that identifies the conversation:

```python
config = {"configurable": {"thread_id": f"conv_{conversation_id}"}}
result = await app.ainvoke(inputs, config=config)
```

**Rules:**
- `thread_id` must be stable per conversation. Use your canonical `conversation_id`.
- Different users → different `thread_id`. Never share threads across users.
- For multi-surface bots (web + WhatsApp), decide whether surfaces share a thread (continuity across channels) or separate threads (channel-scoped). Document the choice.
- Include `user_id` in state, not in config — config is routing, state is data.

## Interrupt Patterns (HITL)

Pause the graph before a risky action, wait for a human, then resume.

### Pattern 1: `interrupt()` inside a node (preferred, v1.1+)

```python
from langgraph.types import interrupt, Command

def approve_refund(state: BotState) -> dict:
    # Pause and wait for external resume
    decision = interrupt({
        "type": "approval_required",
        "action": "refund",
        "amount": state["refund_amount"],
        "user_id": state["user_id"],
        "reason": state["refund_reason"],
    })
    # After resume, `decision` is whatever was passed to Command(resume=...)
    if decision.get("approved"):
        return {"approved": True, "approver": decision["approver"]}
    return {"approved": False, "approver": decision["approver"], "denial_reason": decision.get("reason", "")}

graph.add_node("approve", approve_refund)
graph.add_edge("plan_refund", "approve")
graph.add_conditional_edges("approve", lambda s: "execute" if s["approved"] else "notify_denied")
```

The graph halts at `interrupt()`. The payload is serialized into the checkpoint and surfaced to the caller. No background polling needed.

### Pattern 2: `interrupt_before` / `interrupt_after`

Configure interrupts at compile time for nodes that always require approval:

```python
app = graph.compile(
    checkpointer=saver,
    interrupt_before=["execute_refund", "delete_account"],
)
```

The graph halts before running those nodes. Use this when the pause point is static.

### Triggering and surfacing the interrupt

```python
# First call — runs until interrupt, then returns
config = {"configurable": {"thread_id": conv_id}}
result = await app.ainvoke({"message": user_msg}, config=config)

state = await app.aget_state(config)
if state.next:  # graph is paused
    interrupt_payload = state.tasks[0].interrupts[0].value
    await notify_operator(interrupt_payload)
    # ... operator reviews in dashboard
```

## Resume with Command

After the operator decides, resume with `Command(resume=...)`:

```python
from langgraph.types import Command

approval = {"approved": True, "approver": "agent_42"}
result = await app.ainvoke(
    Command(resume=approval),
    config={"configurable": {"thread_id": conv_id}},
)
```

The value passed to `resume=` becomes the return value of `interrupt()` inside the node. The graph picks up exactly where it paused — no replay of completed nodes.

**Rules:**
- Resume-with-update: `Command(resume=..., update={"field": value})` — use sparingly; updating state after a pause makes replay harder to reason about.
- If the operator denies, resume with the denial payload and route to a "notify user" node, not to the execute node.
- Timeout approvals. A pending interrupt should not live forever — implement a sweeper that resumes stale interrupts with `{"approved": False, "reason": "timeout"}`.

## Replay and Time-Travel

Inspect any checkpoint:

```python
history = [s async for s in app.aget_state_history(config)]
for snapshot in history:
    print(snapshot.values)        # state at that point
    print(snapshot.next)          # what would run next
    print(snapshot.metadata)      # step, source, write counts
```

Replay from a past checkpoint:

```python
# Pick a checkpoint by config (config contains checkpoint_id)
past_config = history[3].config  # 4th-most-recent snapshot

# Re-run from that point
result = await app.ainvoke(None, config=past_config)
```

**Use cases:**
- **Audit**: explain why the bot made a decision by inspecting state at each node
- **Debug**: replay a production bug with the exact state
- **Branch**: fork a conversation from a past point with a different input

**Limits:**
- Tool calls with side effects will re-execute on replay unless idempotent or mocked. Always replay with mocked tools in debug.
- Replay is cheap for deterministic graphs; expensive for LLM-heavy ones because every LLM call re-runs.

## Recovery Patterns

### On node failure

```python
async def fetch_account_with_fallback(state: BotState, *, clients) -> dict:
    try:
        account = await clients.crm.get_account(state["user_id"])
        return {"account": account.model_dump()}
    except CRMTimeout:
        # Route to human rather than continue with empty account
        return {"route": "escalate", "escalation_reason": "crm_timeout"}
```

**Rules:**
- Define per-node failure behavior: retry, fallback, escalate, or fail-closed.
- Never let retries mutate state invisibly. If a retry is partial, checkpoint before and after.
- For idempotent tool calls, use `tenacity` or similar with exponential backoff.
- For non-idempotent tool calls (send email, charge card), never retry without checking the effect via an idempotency key.

### Circuit breaker around external services

```python
from pybreaker import CircuitBreaker
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

@breaker
async def call_crm(user_id: str):
    return await crm.get_account(user_id)
```

If the CRM is down, the breaker trips and subsequent calls fail fast — route to a graceful degradation path.

## Audit Trail

For any bot with side effects, write an audit record on every decision:

```python
async def write_audit(state: BotState, *, clients) -> dict:
    await clients.db.insert("bot_decisions", {
        "conversation_id": state["conversation_id"],
        "user_id": state["user_id"],
        "node": "approve_refund",
        "route": state.get("route"),
        "decision": state.get("decision"),
        "confidence": state.get("confidence"),
        "approved_by": state.get("approver"),
        "latency_ms": state.get("latency_ms"),
        "checkpoint_id": state.get("__checkpoint_id__"),
        "ts": datetime.utcnow(),
    })
    return {}
```

Combined with LangGraph's checkpoint history, you get two complementary audit trails:
- **Checkpoint history** — full state at every step, replayable, heavyweight
- **Audit table** — structured decision records, queryable, lightweight

Keep both. The audit table is what you query for reporting; the checkpoint history is what you use for debugging.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| Checkpointing everything | Checkpoint table grows unbounded, write latency dominates | Checkpoint at meaningful boundaries (pre/post side-effect, pre/post approval) |
| No TTL on pending interrupts | Stuck conversations hold operator attention forever | Sweeper resumes stale interrupts with `{"approved": False, "reason": "timeout"}` |
| Shared thread_id across users | Conversation leaks across tenants | Namespace `thread_id` with `user_id`, enforce at query layer |
| Mutating state in the approval gate node | State diff between pause and resume becomes opaque | Interrupt with a payload, resume with a decision, keep state changes minimal |
| Retrying a non-idempotent tool call | Duplicate sends, double-charges | Use idempotency keys; check effect before retry |
| Using interrupt for UX "typing…" delays | Checkpoint write amplification | Use streaming, not interrupts, for UX affordances |
| Resuming with `update=` to patch state | Replay semantics get confusing | Redesign the node so resume data flows through `interrupt()` return value |

## Check

Checkpoints and HITL are working if: (1) a worker crash mid-turn does not lose the user's context — the next request resumes from the last checkpoint, (2) every destructive action has a checkpoint before and after, (3) pending approvals have a TTL and are swept, (4) replaying a past checkpoint with mocked tools reproduces the same routing and responses, and (5) the audit table answers "what did the bot do and why" in one query.
