# Handoff to Human

Use this reference when designing escalation triggers, context transfer, queue routing, and reverse handoff patterns.

## Table of Contents

- [Escalation Triggers](#escalation-triggers)
- [Warm Handoff Protocol](#warm-handoff-protocol)
- [Cold Handoff](#cold-handoff)
- [Queue Routing Patterns](#queue-routing-patterns)
- [Context Transfer Format](#context-transfer-format)
- [Handoff SLAs](#handoff-slas)
- [Reverse Handoff](#reverse-handoff)
- [Analytics](#analytics)

## Escalation Triggers

Escalation should be deterministic, not a fallback of last resort. Define triggers explicitly.

**Trigger taxonomy:**

| Trigger | Detection method | Priority |
|---------|-----------------|----------|
| Explicit request | User says "talk to a human", "agent", "representative" | Immediate |
| Confidence threshold | Intent classifier confidence < 0.5 for 2+ consecutive turns | High |
| Topic boundary | Intent classified as out-of-scope or regulated domain | High |
| Sentiment detection | Negative sentiment sustained across 3+ turns | High |
| Loop detection | Bot repeats the same clarification or fallback 3 times | High |
| Turn budget exceeded | `turn_count` exceeds max for this bot type | Medium |
| Tool failure | Critical tool fails after retry (e.g., payment system down) | Medium |
| High-value customer | VIP tier detected via account lookup | Medium |
| Complex multi-issue | 3+ distinct intents detected in one conversation | Low |

**Implementation:**

```python
from dataclasses import dataclass
from enum import Enum

class EscalationReason(str, Enum):
    EXPLICIT_REQUEST = "explicit_request"
    LOW_CONFIDENCE = "low_confidence"
    TOPIC_BOUNDARY = "topic_boundary"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    LOOP_DETECTED = "loop_detected"
    TURN_BUDGET = "turn_budget_exceeded"
    TOOL_FAILURE = "tool_failure"
    VIP_CUSTOMER = "vip_customer"
    MULTI_ISSUE = "multi_issue"

@dataclass
class EscalationDecision:
    should_escalate: bool
    reason: EscalationReason | None
    priority: str                   # "immediate", "high", "medium", "low"
    suggested_queue: str | None     # Skill-based routing hint

def check_escalation(state: dict) -> EscalationDecision:
    # Explicit request — always honor immediately
    if _user_requested_human(state["messages"][-1]):
        return EscalationDecision(True, EscalationReason.EXPLICIT_REQUEST, "immediate", None)

    # Loop detection — same fallback 3+ times
    if state.get("consecutive_fallbacks", 0) >= 3:
        return EscalationDecision(True, EscalationReason.LOOP_DETECTED, "high", None)

    # Turn budget
    if state["turn_count"] >= state.get("max_turns", 12):
        return EscalationDecision(True, EscalationReason.TURN_BUDGET, "medium", None)

    # Confidence threshold — 2 consecutive low-confidence turns
    if state.get("consecutive_low_confidence", 0) >= 2:
        return EscalationDecision(True, EscalationReason.LOW_CONFIDENCE, "high", None)

    return EscalationDecision(False, None, "none", None)
```

**Rules:**
- Explicit requests are non-negotiable. Never argue with "let me talk to a human."
- Don't escalate on a single low-confidence turn — give the clarification system one chance.
- Log every escalation trigger for tuning thresholds.

## Warm Handoff Protocol

Warm handoff transfers the conversation to a human agent with full context. The user doesn't have to repeat themselves.

**Protocol steps:**

```
1. Bot acknowledges the handoff
   "I'm going to connect you with a team member who can help with this."

2. Bot packages context (see Context Transfer Format)

3. Bot sets expectations
   "You'll be connected shortly. Expected wait time is about [X] minutes."

4. Bot hands off to queue with context payload

5. Human agent receives context and opens with:
   "[Name], I've reviewed your conversation. I can see you need help with [summary].
    Let me take it from here."
```

**Bot-side handoff message:**

```python
HANDOFF_MESSAGES = {
    "explicit_request": "Of course — let me connect you with a team member right now.",
    "low_confidence": "I want to make sure you get the right help. Let me connect you with someone who can assist.",
    "negative_sentiment": "I can see this hasn't been going well. Let me get you to someone who can help directly.",
    "tool_failure": "I'm having trouble accessing our systems right now. Let me connect you with a team member who can help.",
    "turn_budget_exceeded": "This is taking longer than it should. Let me connect you with a specialist.",
}
```

**Rules:**
- Never say "I can't help you" — say "let me connect you with someone who can."
- Always set wait time expectations. If you can't estimate, say "as soon as possible."
- Never drop the conversation silently — confirm the handoff was initiated.

## Cold Handoff

Cold handoff routes the user to a queue without transferring conversation context. Use sparingly.

**When cold handoff is acceptable:**
- Channel doesn't support context transfer (e.g., phone callback).
- User requests a specific department the bot can't route context to.
- Integration with the agent desk doesn't support context injection.

**Cold handoff message:**

```
"I'm going to transfer you to our [department] team. You may need to briefly
describe your issue again. They'll be able to help you directly."
```

**Rules:**
- Always warn the user they may need to repeat their issue.
- Provide a reference number if possible so the agent can look up prior context.
- Track cold handoffs separately — they're a worse user experience and should be minimized.

## Queue Routing Patterns

**Skill-based routing:**

```python
QUEUE_ROUTES = {
    "billing": {"queue": "billing_team", "priority": "normal"},
    "technical": {"queue": "tech_support_l1", "priority": "normal"},
    "account_security": {"queue": "security_team", "priority": "high"},
    "cancellation": {"queue": "retention_team", "priority": "high"},
    "vip": {"queue": "vip_support", "priority": "immediate"},
}

def route_to_queue(intent: str, customer_tier: str) -> dict:
    if customer_tier == "vip":
        return QUEUE_ROUTES["vip"]
    return QUEUE_ROUTES.get(intent, {"queue": "general_support", "priority": "normal"})
```

**Priority-based routing:**

| Priority | SLA | Use case |
|----------|-----|----------|
| Immediate | < 1 min | VIP, account security, explicit "urgent" |
| High | < 5 min | Payment issues, cancellation intent, sustained negative sentiment |
| Normal | < 15 min | General support, feature questions |
| Low | < 1 hour | Feedback, non-urgent requests |

**Load-balanced routing:**
- Distribute across available agents by current load, not round-robin.
- Factor in agent skill match AND current queue depth.
- If all agents in a skill queue are busy, overflow to general queue with a note about required skill.

## Context Transfer Format

Package everything the human agent needs to continue seamlessly.

**Transfer payload:**

```python
from dataclasses import dataclass, field

@dataclass
class HandoffContext:
    # Conversation summary
    summary: str                        # 2-3 sentence summary of the conversation
    intent: str                         # Classified intent
    escalation_reason: str              # Why the bot escalated

    # Collected data
    slots: dict[str, str]               # All collected slot values
    tool_results: list[dict]            # Results from tool calls (order lookups, etc.)

    # Customer data
    customer_id: str | None
    customer_tier: str | None           # "free", "pro", "enterprise", "vip"
    customer_name: str | None

    # Conversation history
    message_count: int
    messages: list[dict]                # Full conversation history
    bot_actions_taken: list[str]        # What the bot already tried

    # Metadata
    channel: str                        # web_chat, whatsapp, sms, etc.
    session_id: str
    started_at: str                     # ISO 8601
    escalated_at: str                   # ISO 8601
    sentiment_trajectory: list[str]     # e.g., ["neutral", "neutral", "negative", "negative"]

    # Suggested action
    suggested_next_step: str | None     # What the bot thinks the agent should do
```

**Summary generation:**

```python
SUMMARY_PROMPT = """Summarize this bot conversation for a human support agent in 2-3 sentences.
Include: what the customer wants, what the bot already tried, and why the bot escalated.

Conversation:
{conversation_history}

Escalation reason: {escalation_reason}
Collected data: {slots}
"""
```

**Rules:**
- The summary should be actionable — the agent should know exactly what to do next.
- Include what the bot already tried so the agent doesn't repeat failed approaches.
- Include tool results so the agent doesn't re-query the same systems.
- Never include raw system prompts or internal bot configuration in the transfer.

## Handoff SLAs

Define SLAs for the handoff process itself, not just the agent response.

| Metric | Target | Measurement point |
|--------|--------|-------------------|
| Handoff initiation | < 2 seconds | Time from trigger to queue placement |
| Acknowledgment | < 30 seconds | Time from queue to "agent is joining" message |
| First agent response | < 2 minutes | Time from agent assignment to first message |
| Context load time | < 5 seconds | Time for agent desk to display context payload |

**SLA enforcement:**

```python
import time

async def monitor_handoff(session_id: str, queue_entry_time: float):
    acknowledgment_deadline = queue_entry_time + 30
    response_deadline = queue_entry_time + 120

    while True:
        status = await get_handoff_status(session_id)

        if status == "acknowledged":
            break

        if time.time() > acknowledgment_deadline:
            await send_user_message(session_id, "We're still finding the right team member. Thank you for your patience.")
            await re_prioritize(session_id, priority="high")

        if time.time() > response_deadline:
            await offer_callback(session_id)
            break

        await asyncio.sleep(5)
```

**Rules:**
- Send periodic updates if wait exceeds SLA. Don't leave users in silence.
- Offer a callback option if wait exceeds 2x the SLA target.
- Track SLA compliance per queue for staffing decisions.

## Reverse Handoff

When the human agent's portion is complete, hand the conversation back to the bot.

**Use cases:**
- Agent resolved the complex issue; bot handles closing and CSAT collection.
- Agent answered the specialized question; bot resumes for remaining routine items.
- Agent approved a high-value action; bot executes the workflow.

**Protocol:**

```python
@dataclass
class ReverseHandoffContext:
    resolution_summary: str             # What the agent resolved
    remaining_items: list[str]          # Unaddressed intents for the bot to handle
    agent_notes: str                    # Anything the bot should know
    state_updates: dict[str, str]       # Slot updates from the agent interaction

async def reverse_handoff(session_id: str, context: ReverseHandoffContext):
    # Update conversation state with agent's resolution
    state = await load_state(session_id)
    state["agent_resolution"] = context.resolution_summary
    state["slots"].update(context.state_updates)

    if context.remaining_items:
        # Bot picks up remaining items
        await send_bot_message(
            session_id,
            f"Thanks for waiting. {context.resolution_summary} "
            f"Now, let me help with your other question about {context.remaining_items[0]}."
        )
    else:
        # Bot handles closing
        await send_bot_message(
            session_id,
            f"Glad we could get that sorted. Is there anything else I can help with?"
        )
```

**Rules:**
- The bot should acknowledge the agent's resolution, not re-explain it.
- If the user addressed multiple issues, the bot should return to unresolved ones.
- Always offer a chance for the user to continue or close.

## Analytics

Track handoff performance to improve both the bot and the human support operation.

**Core handoff metrics:**

| Metric | Formula | Target |
|--------|---------|--------|
| Escalation rate | Escalated / Total conversations | < 20% for mature bots |
| Resolution after escalation | Resolved by agent / Escalated | > 90% |
| Repeat escalation rate | Users who escalate again within 24h / Escalated | < 10% |
| Human intervention success | CSAT for escalated vs. non-escalated | Escalated CSAT within 0.5 of bot-resolved CSAT |
| Unnecessary escalation rate | Agent resolved in < 1 min / Escalated | < 15% (indicates bot could have handled it) |

**Escalation reason breakdown:**

Track the distribution of escalation reasons over time. A healthy bot should show:
- Explicit request: 30-50% (users who just prefer humans)
- Topic boundary: 20-30% (expected — bot has defined scope)
- Low confidence / loop: < 15% (conversation design issues)
- Negative sentiment: < 10% (bot quality issues)
- Tool failure: < 5% (infrastructure issues)

**Review cadence:**
- Daily: monitor escalation rate and SLA compliance.
- Weekly: review escalation reason distribution and top failure conversations.
- Monthly: tune escalation thresholds and update queue routing rules.

For dashboard implementation and alerting patterns, see [bot-analytics-improvement.md](bot-analytics-improvement.md).
