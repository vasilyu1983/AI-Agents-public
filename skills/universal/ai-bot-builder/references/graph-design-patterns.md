# LangGraph Graph Design Patterns

## Table of Contents

- [When LangGraph Earns Its Overhead](#when-langgraph-earns-its-overhead)
- [State Schema](#state-schema)
- [Node Patterns](#node-patterns)
- [Edge Patterns](#edge-patterns)
- [Router as Node](#router-as-node)
- [Subgraphs](#subgraphs)
- [Common Graph Shapes](#common-graph-shapes)
- [Anti-Patterns](#anti-patterns)
- [Check](#check)

**Purpose.** Concrete patterns for structuring LangGraph bots. Covers state schemas, node boundaries, edge rules, routers, and subgraphs with production-ready code.

**Target version.** These patterns were written against the LangGraph 1.2 line. Before pinning, read the releases page for the newest release and its supported Python range — see [`framework-selection.md`](framework-selection.md) for the version-support detail and why the older "pin 3.13" advice no longer applies. This stack ships minor releases on a near-weekly cadence.

## When LangGraph Earns Its Overhead

Use LangGraph when at least two of these are true:

- The flow has cycles (ReAct-style tool loops, retry-on-failure)
- You need checkpoints for pause/resume across turns
- You need human-in-the-loop approval gates
- The state is complex enough that a plain dict is error-prone
- You need LangSmith tracing

If the flow is a linear cascade (spam → router → support → reply), a plain async function with if/elif routing is simpler, faster to test, and has zero framework overhead. See `ai-agents/SKILL.md` for the build-vs-not decision.

## State Schema

Define state **before** writing nodes. State drives node signatures and test fixtures.

### Basic state

```python
from typing import TypedDict, Annotated
from operator import add

class BotState(TypedDict, total=False):
    # Inputs
    user_id: str
    conversation_id: str
    message: str

    # Routing
    intent: str
    confidence: float
    route: str  # "support" | "sales" | "escalate" | "refuse"

    # Accumulated context
    history: Annotated[list[dict], add]  # reducer: append, don't overwrite
    recalled_facts: list[dict]

    # Outputs
    response: str
    requires_approval: bool
    decision: dict  # structured audit record
```

**Rules:**
- `total=False` lets nodes return partial updates without listing every field.
- Use `Annotated[list, add]` for fields that nodes append to (messages, traces). Without the reducer, a node returning `{"history": [msg]}` overwrites the whole list.
- Keep state typed, minimal, and serializable. No httpx clients, no open sockets, no callables. Inject those as `clients` kwargs to nodes.
- Separate durable state (things a checkpoint should capture) from transient execution data (current LLM response object being streamed).

### Messages state

For chat-style bots, LangGraph ships a prebuilt messages reducer:

```python
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
```

`add_messages` handles both append and update-by-id semantics — if a node returns a message with an existing `id`, it replaces rather than duplicates.

## Node Patterns

### Pure function signature

```python
def classify_intent(state: BotState, *, clients: Clients) -> dict:
    """Return a partial state update. Never mutate state in place."""
    message = state["message"]
    result = clients.llm.classify(message, intents=["support", "sales", "other"])
    return {
        "intent": result.intent,
        "confidence": result.confidence,
    }
```

**Rules:**
- Signature is `(state, *, clients) -> dict`. Never `(state) -> dict` with globals — that kills testability.
- Inject clients via `functools.partial` when adding nodes:
  ```python
  from functools import partial
  graph.add_node("classify", partial(classify_intent, clients=clients))
  ```
- One node does one job. Good node types: classify, call a tool, transform state, format output, apply a filter.
- Avoid giant nodes that hide orchestration inside one prompt (anti-pattern).

### Async nodes

Any node that makes an HTTP call should be async:

```python
async def fetch_account(state: BotState, *, clients: Clients) -> dict:
    account = await clients.crm.get_account(state["user_id"])
    return {"account": account.model_dump()}
```

LangGraph awaits async nodes automatically when `graph.ainvoke()` is used.

### Node testing

Nodes are trivially testable because they are pure functions:

```python
def test_classify_intent_support():
    state = {"message": "my card is blocked"}
    clients = MockClients(llm=FakeLLM(intent="support", confidence=0.95))
    result = classify_intent(state, clients=clients)
    assert result["intent"] == "support"
    assert result["confidence"] == 0.95
```

## Edge Patterns

### Linear edge

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(BotState)
graph.add_node("classify", partial(classify_intent, clients=clients))
graph.add_node("respond", partial(generate_response, clients=clients))
graph.add_edge(START, "classify")
graph.add_edge("classify", "respond")
graph.add_edge("respond", END)
app = graph.compile()
```

Use `START` and `END` constants for new code. `set_entry_point()` remains documented as equivalent to `add_edge(START, key)`, but explicit entry edges are easier to inspect and diff.

### Conditional edge

```python
def route_by_intent(state: BotState) -> str:
    """Routing function returns a node name or END."""
    if state.get("confidence", 0) < 0.6:
        return "clarify"
    return {
        "support": "support_flow",
        "sales": "sales_flow",
        "other": "refuse",
    }.get(state["intent"], "refuse")

graph.add_conditional_edges(
    "classify",
    route_by_intent,
    # Optional path map for clarity and graph visualization
    {
        "clarify": "clarify",
        "support_flow": "support_flow",
        "sales_flow": "sales_flow",
        "refuse": "refuse",
    },
)
```

**Rules:**
- Routing functions return strings (node names) or `END`.
- Prefer deterministic routing (rule-based, confidence-threshold) over free-form planner branching unless the workflow truly needs it.
- Keep the path map — it documents valid transitions and helps graph visualization.

## Router as Node

For bots with many routes, centralize routing in a dedicated node rather than a single 20-branch conditional edge:

```python
class RouteDecision(BaseModel):
    route: Literal["support", "sales", "billing", "escalate", "refuse"]
    confidence: float
    reason: str

async def router_node(state: BotState, *, clients: Clients) -> dict:
    decision = await clients.llm.structured(
        system=ROUTER_SYSTEM_PROMPT,
        user=state["message"],
        schema=RouteDecision,
    )
    return {
        "route": decision.route,
        "confidence": decision.confidence,
        "decision": {
            "node": "router",
            "route": decision.route,
            "confidence": decision.confidence,
            "reason": decision.reason,
        },
    }

def pick_next(state: BotState) -> str:
    return state["route"]

graph.add_node("router", partial(router_node, clients=clients))
graph.add_conditional_edges("router", pick_next, {
    "support": "support_flow",
    "sales": "sales_flow",
    "billing": "billing_flow",
    "escalate": "human_handoff",
    "refuse": "refuse",
})
```

Benefits: routing logic is a testable node (not buried in an edge function), routing decisions land in the audit record, and the router can be swapped (rule-based → LLM → ensemble) without touching edges.

## Subgraphs

Extract reusable workflow sections into subgraphs. Each bot domain (support, sales, billing) can be a subgraph with its own state schema that the parent composes:

```python
# Subgraph state — narrower than parent
class SupportState(TypedDict, total=False):
    message: str
    account: dict
    kb_results: list[dict]
    response: str

def build_support_subgraph(clients: Clients):
    g = StateGraph(SupportState)
    g.add_node("fetch_account", partial(fetch_account, clients=clients))
    g.add_node("search_kb", partial(search_kb, clients=clients))
    g.add_node("generate", partial(generate_support_reply, clients=clients))
    g.add_edge(START, "fetch_account")
    g.add_edge("fetch_account", "search_kb")
    g.add_edge("search_kb", "generate")
    g.add_edge("generate", END)
    return g.compile()

# Parent graph adds the subgraph as a node
support_app = build_support_subgraph(clients)
graph.add_node("support_flow", support_app)
```

**When to use subgraphs:**
- The same flow is reused across bot surfaces (web chat + WhatsApp + email)
- A domain flow is complex enough (5+ nodes) to warrant its own file and tests
- You want to deploy parts of the graph independently (LangGraph Platform)

**When not to use subgraphs:**
- The flow is only 2–3 nodes — subgraph overhead exceeds the win
- The child state needs every field the parent has — you are not actually separating concerns

## Common Graph Shapes

### ReAct loop (tool-using bot)

```
START → agent → [tool | END]
         ▲        │
         └────────┘
```

```python
def should_continue(state: ChatState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

graph = StateGraph(ChatState)
graph.add_node("agent", partial(agent_node, clients=clients))
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")
```

### Plan → Approve → Execute

```
START → plan → [approve_gate (interrupt)] → execute → END
```

See [`state-checkpoints-and-hitl.md`](state-checkpoints-and-hitl.md) for the approval-gate implementation.

### Classify → Route → Respond (most support bots)

```
START → pre_filter → classify → {support | sales | refuse | escalate}
                                    │
                                    ▼
                                 respond → post_filter → END
```

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|-------------|-------------|-----|
| Giant node with prompt that owns routing + tools + persona + tone | Handoff, retries, root-cause analysis all become impossible | Split into classify → route → respond nodes |
| State dict with no schema (`dict[str, Any]`) | Refactors silently break downstream nodes | Use `TypedDict` with `total=False` |
| Mutating state in place (`state["history"].append(msg)`) | LangGraph can't apply the reducer correctly; breaks replay | Return `{"history": [msg]}` and use `Annotated[list, add]` |
| Using globals for clients | Nodes become untestable without monkey-patching | Inject via `functools.partial(node, clients=clients)` |
| Building a cyclic graph when the flow is linear | Framework overhead without benefit | Use plain async Python with if/elif |
| One subgraph per node | Overhead with no reuse or separation | Only extract subgraphs that are reused or ≥5 nodes |
| `graph.set_entry_point()` | Still documented as equivalent, but less explicit | Use `graph.add_edge(START, "first_node")` |

## Check

A LangGraph bot is well-designed when: (1) every node is a pure function you can unit-test without running the graph, (2) the state schema is typed and minimal, (3) routing logic lives in a dedicated node or edge function — not smeared across prompts, (4) replaying a checkpoint produces the same state transition it did originally, and (5) a new contributor can read the graph file and tell you what the bot does in under five minutes.
