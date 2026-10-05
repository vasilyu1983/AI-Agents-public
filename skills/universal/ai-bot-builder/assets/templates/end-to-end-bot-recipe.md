# End-to-End Bot Recipe: Zero to Shipped

**Stack covered**: LangGraph + Twilio (phone/SMS bot). Step 5B points to the voice path; voice pipelines are owned by [`ai-voice-bots`](../../../ai-voice-bots/SKILL.md).

This is a runnable walkthrough, not a conceptual guide. Every step has a concrete action and a verification check. Follow in order.

---

## Prerequisite Checklist

Before starting, verify:

- [ ] A Python version inside the range your LangGraph release supports: read it on the [LangGraph releases page](https://github.com/langchain-ai/langgraph/releases) (see [`framework-selection.md`](../../references/framework-selection.md)) and pin the one your CI tests
- [ ] `uv` or `pip` package manager available
- [ ] Redis instance available (local Docker or cloud) for dedup and session state
- [ ] API keys obtained: LLM provider (Anthropic/OpenAI), STT/TTS if voice (Deepgram, ElevenLabs)
- [ ] For Twilio path: Twilio account + phone number + ngrok or a public endpoint for webhooks
- [ ] For the voice path (Step 5B): transport and STT/TTS accounts as ai-voice-bots specifies

---

## Step 1: Project Scaffold

```bash
mkdir my-bot && cd my-bot
python3 -m venv .venv && source .venv/bin/activate   # the Python version you checked above

# LangGraph + Twilio path. Pin the versions your CI tests in a lock file.
pip install langgraph langchain-anthropic fastapi uvicorn httpx respx redis pydantic

# Voice path: take the pipecat-ai extras and version from ai-voice-bots, not from here.
```

**Verify**: `python3 -c "import langgraph; print(langgraph.__version__)"` — must import without error.

---

## Step 2: Define the Conversation State

```python
# bot/state.py
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class BotState(TypedDict, total=False):
    messages: Annotated[list, add_messages]          # conversation history
    user_intent: Optional[str]                        # classified intent
    collected_slots: dict                             # slot-filling accumulator
    escalation_reason: Optional[str]                  # set when escalating
    turn_count: int                                   # enforce turn budget
    session_id: str                                   # for dedup and memory recall
    recalled_facts: list                              # from memory layer
```

**Why**: state before nodes — define the TypedDict first so every node has a typed contract to work against.

**Verify**: `python3 -c "from bot.state import BotState; print('OK')`

---

## Step 3: Define Pure Nodes

```python
# bot/nodes.py
from functools import partial
from bot.state import BotState

async def classify_intent(state: BotState, *, llm) -> dict:
    """Classify the latest user message into an intent."""
    latest = state["messages"][-1].content if state.get("messages") else ""
    # Replace with your intent classifier — keep this node pure (no I/O side effects)
    intent = await llm.ainvoke(f"Classify this user message into: support|sales|general|escalate\n\n{latest}")
    return {"user_intent": intent.content.strip().lower(), "turn_count": state.get("turn_count", 0) + 1}

async def generate_response(state: BotState, *, llm) -> dict:
    """Generate the bot's response using the assembled context."""
    # Load recalled facts into system prompt
    facts = "\n".join(state.get("recalled_facts", [])) or "No prior context."
    system = f"You are a helpful bot. Known facts about this user:\n{facts}"
    response = await llm.ainvoke([{"role": "system", "content": system}] + state["messages"])
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content=response.content)]}

async def escalate(state: BotState, *, llm) -> dict:
    """Prepare escalation payload."""
    reason = state.get("escalation_reason", "User requested human agent")
    summary = await llm.ainvoke(f"Write a 2-sentence operator summary for: {state['messages']}")
    return {"messages": [], "escalation_reason": f"{reason}\n\nSummary: {summary.content}"}

def build_nodes(llm):
    return {
        "classify": partial(classify_intent, llm=llm),
        "respond": partial(generate_response, llm=llm),
        "escalate": partial(escalate, llm=llm),
    }
```

**Why pure nodes**: `(state, *, clients) -> dict` via `functools.partial` — testable without monkey-patching.

---

## Step 4: Build the Graph

```python
# bot/graph.py
from langgraph.graph import StateGraph, START, END
from bot.state import BotState
from bot.nodes import build_nodes

def should_escalate(state: BotState) -> str:
    if state.get("user_intent") == "escalate":
        return "escalate"
    if state.get("turn_count", 0) >= 10:                  # turn budget
        return "escalate"
    return "respond"

def build_graph(llm):
    nodes = build_nodes(llm)
    g = StateGraph(BotState)

    g.add_node("classify", nodes["classify"])
    g.add_node("respond", nodes["respond"])
    g.add_node("escalate", nodes["escalate"])

    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", should_escalate, {"respond": "respond", "escalate": "escalate"})
    g.add_edge("respond", END)
    g.add_edge("escalate", END)

    return g.compile()
```

**Verify**: `python3 -c "from bot.graph import build_graph; print('graph compiles')"` — must compile without error.

---

## Step 5A: Twilio Webhook Server (LangGraph + Twilio path)

```python
# server_twilio.py
import os, json
from fastapi import FastAPI, Form, Response
from langchain_anthropic import ChatAnthropic
from bot.graph import build_graph

app = FastAPI()
llm = ChatAnthropic(model=os.environ["ANTHROPIC_MODEL_ID"], api_key=os.environ["ANTHROPIC_API_KEY"])  # pin the current model ID in config
graph = build_graph(llm)

@app.post("/webhook/voice")
async def voice_webhook(CallSid: str = Form(...), SpeechResult: str = Form("")):
    """Twilio calls this for each user utterance (voice)."""
    state = {"messages": [{"role": "user", "content": SpeechResult}], "session_id": CallSid}
    result = await graph.ainvoke(state)
    last_msg = next((m for m in reversed(result.get("messages", [])) if hasattr(m, "content")), None)
    reply = last_msg.content if last_msg else "I'm sorry, could you repeat that?"
    twiml = f'<Response><Say>{reply}</Say><Gather input="speech" action="/webhook/voice"/></Response>'
    return Response(content=twiml, media_type="application/xml")
```

**Test locally**:
```bash
uvicorn server_twilio:app --port 8000
ngrok http 8000  # copy the ngrok URL into Twilio voice webhook config
```

---

## Step 5B: Voice Path (owned by ai-voice-bots)

This recipe does not ship voice code. Pipecat moved its transport, service and aggregator modules between releases, so a pasted import list goes stale; the one kept here broke on the 1.x line. To add voice, keep the Step 3 graph as the conversation brain and follow [`ai-voice-bots/references/pipecat-patterns.md`](../../../ai-voice-bots/references/pipecat-patterns.md) ("LangGraph Integration") with imports taken from the current Pipecat docs. The pipeline shape stays: transport in, STT, user-turn aggregation, a processor that calls the compiled graph, TTS, assistant-turn aggregation, transport out. Without the graph processor the pipeline transcribes but never answers.

---

## Step 6: Add Guardrails

```python
# bot/guardrails.py
import re

PII_PATTERNS = [
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),   # card numbers — run before phone
    re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),  # phone numbers
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # email
]

BLOCKED_TOPICS = ["investment advice", "medical diagnosis", "legal advice"]

def scrub_pii(text: str) -> str:
    for pattern in PII_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text

def check_compliance(text: str) -> tuple[bool, str]:
    """Return (is_blocked, reason). Block before response reaches user."""
    lower = text.lower()
    for topic in BLOCKED_TOPICS:
        if topic in lower:
            return True, f"Response blocked: contains restricted topic '{topic}'."
    return False, ""
```

**Key rule**: run guardrails before any response reaches the user and before any tool fires.

**Verify**:
```python
from bot.guardrails import scrub_pii, check_compliance
assert "[REDACTED]" in scrub_pii("Call me at 555-123-4567")
assert check_compliance("This is investment advice")[0] is True
print("Guardrail tests pass")
```

---

## Step 7: Add Redis Dedup

```python
# bot/dedup.py
import redis.asyncio as aioredis
import hashlib

async def is_duplicate(r: aioredis.Redis, event_id: str, text: str) -> bool:
    """Two-level dedup: exact event ID (15-min TTL) + text hash (8-sec TTL)."""
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    if await r.set(f"event:{event_id}", "1", nx=True, ex=900) is None:
        return True
    if await r.set(f"texthash:{text_hash}", "1", nx=True, ex=8) is None:
        return True
    return False
```

---

## Step 8: Unit Tests for Nodes

```python
# tests/test_nodes.py
import asyncio
from unittest.mock import AsyncMock
from bot.nodes import classify_intent
from bot.state import BotState
from langchain_core.messages import HumanMessage, AIMessage

def test_classify_intent_support():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="support")
    state = BotState(messages=[HumanMessage(content="My order is missing.")], turn_count=0)
    result = asyncio.run(classify_intent(state, llm=mock_llm))
    assert result["user_intent"] == "support"
    assert result["turn_count"] == 1

def test_turn_budget_triggers_escalation():
    from bot.graph import should_escalate
    state = BotState(user_intent="general", turn_count=10)
    assert should_escalate(state) == "escalate"
```

Run: `python3 -m pytest tests/ -v`

---

## Step 9: Run the Red-Team Pack

```bash
# Generate a sample JSONL for your bot's responses
python3 scripts/red_team_pack.py --input sample_responses.jsonl

# Expected: all test categories report PASS or flag true positives only
```

See [`scripts/red_team_pack.py`](../../scripts/red_team_pack.py) for the full pack.

---

## Step 10: Pre-Launch Checklist

- [ ] Unit tests for all pure nodes pass
- [ ] Guardrails tested with adversarial inputs (card numbers, restricted topics)
- [ ] Dedup tested across restarts (Redis TTL verified)
- [ ] Red-team pack passes (prompt injection, PII leak, jailbreak categories)
- [ ] Escalation path tested end-to-end (operator summary generated)
- [ ] Cost tracking per conversation instrumented
- [ ] Turn budget enforced (max 10 turns before forced escalation)
- [ ] Compliance filter runs before every user-visible response

See [`../assets/bot-safety-checklist.md`](../bot-safety-checklist.md) for the full safety gate.

---

## Reference Map

| Need | Reference |
|------|-----------|
| LangGraph state, nodes, checkpoints | [`references/graph-design-patterns.md`](../../references/graph-design-patterns.md) |
| Human-in-the-loop approval | [`references/state-checkpoints-and-hitl.md`](../../references/state-checkpoints-and-hitl.md) |
| Pipecat pipeline patterns | [`ai-voice-bots/references/pipecat-patterns.md`](../../../ai-voice-bots/references/pipecat-patterns.md) |
| Injection and jailbreak defense | [`references/injection-and-jailbreak-defense.md`](../../references/injection-and-jailbreak-defense.md) |
| Memory integration | [`references/bot-memory-integration.md`](../../references/bot-memory-integration.md) |
| Production deployment | [`references/production-deployment.md`](../../references/production-deployment.md) |
