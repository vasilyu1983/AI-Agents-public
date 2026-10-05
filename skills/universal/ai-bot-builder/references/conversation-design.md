# Conversation Design

Use this reference when designing the conversation flow, state machine, fallback behavior, and multi-turn interaction patterns for a bot.

## Table of Contents

- [Conversation as State Machine](#conversation-as-state-machine)
- [State Design](#state-design)
- [Fallback Hierarchy](#fallback-hierarchy)
- [Slot Filling](#slot-filling)
- [Turn Management](#turn-management)
- [Intent Routing](#intent-routing)
- [Clarification Patterns](#clarification-patterns)
- [Confirmation Patterns](#confirmation-patterns)
- [Error Recovery](#error-recovery)
- [Multi-Turn Context](#multi-turn-context)
- [Conversation Boundaries](#conversation-boundaries)

## Conversation as State Machine

Model every bot conversation as a state machine, not a script. Scripts break on unexpected input. State machines handle it.

**State definition:**

```
State:
  name: string                    # Unique state identifier
  entry_conditions: list          # What brings the user here
  bot_action: string              # What the bot does on entry
  expected_inputs: list           # What the user might say
  transitions: dict               # input_type → next_state
  fallback: string                # Where to go on unexpected input
  max_turns_in_state: int         # Before forcing a transition
```

**Example — support bot:**

```
States:
  greeting → intent_classification → [
    order_status → resolution,
    billing_question → resolution,
    technical_issue → troubleshooting → [resolution, escalation],
    unknown → clarification → intent_classification
  ] → closing

  Any state → escalation (on explicit request, confidence < threshold, or max turns exceeded)
```

**Rules:**
1. Every state must have a fallback transition. No dead ends.
2. Every state must have a max turn limit. Infinite loops are bugs.
3. Escalation is reachable from any state.
4. The closing state must exist and include satisfaction measurement.

## State Design

Keep conversation state minimal, typed, and serializable.

**Core state fields:**

```python
class ConversationState(TypedDict):
    # Identity
    session_id: str
    user_id: str | None
    channel: str                    # web_chat, whatsapp, sms, email, phone

    # Conversation tracking
    messages: list[Message]         # Full conversation history
    current_state: str              # State machine position
    turn_count: int                 # Total turns in this conversation
    turns_in_current_state: int     # Turns in current state

    # Intent and context
    intent: str | None              # Classified intent
    confidence: float               # Intent classification confidence
    slots: dict[str, SlotValue]     # Collected data slots
    context: dict                   # Domain-specific context (order, account, etc.)

    # Outcome tracking
    resolution_status: str | None   # resolved, escalated, abandoned
    escalation_reason: str | None
    satisfaction_score: int | None  # 1-5 if collected
```

**Rules:**
- Separate durable state (persisted across turns) from transient state (per-turn computation).
- Keep slots explicit and typed. Don't rely on free-text parsing of conversation history.
- Track `turns_in_current_state` separately from `turn_count` for per-state timeout logic.

## Fallback Hierarchy

When the bot doesn't understand the user, apply this hierarchy in order:

```
Level 1: Clarify
  "I'm not sure I understood. Could you rephrase that?"
  → Stay in current state, increment turn counter

Level 2: Offer alternatives
  "I can help with [option A], [option B], or [option C]. Which would you like?"
  → Stay in current state, present available transitions

Level 3: Narrow scope
  "Let me ask a specific question instead: [direct question about the most likely intent]"
  → Attempt slot filling with a targeted question

Level 4: Escalate
  "I'm having trouble understanding your request. Let me connect you with a human agent."
  → Transition to escalation state with full context transfer
```

**Rules:**
- Never repeat the same fallback message twice in a row. Rotate through levels.
- Track consecutive fallbacks. Three consecutive fallbacks at any level → escalate.
- Log every fallback for later analysis. Recurring fallbacks reveal conversation design gaps.

## Slot Filling

When the bot needs structured data from the user, use explicit slot filling instead of free-form extraction.

**Slot definition:**

```python
class Slot:
    name: str                       # e.g., "order_number"
    prompt: str                     # "What's your order number?"
    validation: Callable            # e.g., lambda x: re.match(r'ORD-\d{6}', x)
    error_message: str              # "That doesn't look like an order number. It should be like ORD-123456."
    required: bool
    max_attempts: int = 3           # Before giving up on this slot
    alternatives: list[str]         # Other ways to ask
```

**Filling strategy:**
1. Check if the slot was already provided in the initial message (proactive extraction).
2. If not, ask the prompt.
3. Validate the response. On failure, show error_message and re-ask (using alternatives to avoid repetition).
4. After max_attempts, either skip (if optional) or escalate (if required).

**Multi-slot filling:**
- Fill the most important slot first (the one that unlocks the most information).
- Ask one slot at a time. Don't overwhelm with multiple questions.
- Confirm all slots together before acting: "So that's order ORD-123456, placed on March 15th. Is that correct?"

## Turn Management

**Turn budgets by bot type:**

| Bot type | Max turns | Notes |
|----------|-----------|-------|
| Support bot (simple lookup) | 5-8 | If not resolved by turn 8, escalate |
| Support bot (troubleshooting) | 8-12 | More turns needed for diagnostic steps |
| Sales bot (qualification) | 5-8 | Qualify quickly, hand off to human for complex deals |
| Sales bot (scheduling) | 3-5 | Calendar booking should be fast |
| Workflow bot | Varies | Set per-workflow, not globally |

**Turn budget enforcement:**
- Track `turn_count` and `turns_in_current_state` in state.
- At 80% of budget: "I want to make sure we resolve this. Let me [take specific action]."
- At 100% of budget: escalate with full context or offer to create a ticket.
- Never let a conversation run indefinitely without resolution or escalation.

## Intent Routing

**LLM-native classification** (preferred for most bots):

```python
INTENT_CLASSIFIER_PROMPT = """Classify the user's message into one of these intents:
- order_status: User wants to check an order
- billing: User has a billing question or issue
- technical: User has a technical problem
- feedback: User wants to give feedback
- other: None of the above

Respond with only the intent name."""
```

**Confidence thresholds:**

| Confidence | Action |
|------------|--------|
| > 0.85 | Route directly to intent handler |
| 0.6 - 0.85 | Confirm with user: "It sounds like you're asking about [intent]. Is that right?" |
| < 0.6 | Use clarification pattern: ask the user to choose from options |

These fixed cutoffs are a starting point, not a calibrated threshold — they are stake-blind (a 0.9-confidence match on a delete/purchase intent still warrants confirmation) and should be re-derived from your own classifier's calibration curve. For the underlying grounding-criterion logic (why the confirmation bar should scale with stakes and reversibility, not sit at a fixed number), see [`foundations-grounding-communication`](../../foundations-grounding-communication/references/primitives-overview.md#2-grounding-criterion).

**Multi-intent handling:**
- If the user mentions multiple topics, address the primary intent first, then acknowledge the secondary: "Let me help with your order first, then we can look at your billing question."
- Track unaddressed intents in state and return to them.

## Clarification Patterns

**Disambiguation:**
```
User: "I need help with my account"
Bot: "I can help with that. Are you looking to:
  1. Check your account balance
  2. Update your account details
  3. Resolve a billing issue
  4. Something else"
```

**Implicit confirmation:**
```
User: "I want to return my order"
Bot: "I'll help you with a return. Could you share your order number?"
```
The bot implicitly confirms the intent (return) while advancing the conversation (asking for order number).

**Explicit confirmation (for high-stakes actions):**
```
User: "Cancel my subscription"
Bot: "Just to confirm — you'd like to cancel your subscription to [Plan Name] ($X/month). This will take effect on [date]. Shall I proceed?"
```

## Confirmation Patterns

Use confirmation before any action with side effects:

| Action risk | Confirmation type |
|-------------|-------------------|
| Read-only (lookup, search) | None needed |
| Reversible (create ticket, schedule meeting) | Implicit: "I've created ticket #123 for you." |
| Costly (refund, plan change) | Explicit: "This will refund $X to your card ending in 1234. Confirm?" |
| Irreversible (account deletion, subscription cancellation) | Double confirmation: explicit + re-state consequences |

**Record the confirmation, not just the words.** The question is for the user. For the gate, emit it as a tool call that names the action and the arguments being agreed to, one call per action:

```
Bot: "This will refund $20 for order 55 to your card ending in 1234. Shall I proceed?"
  tool_calls: request_confirmation {"action": "issue_refund", "args": {"order_id": "55"}}
User: "Yes"   (a button UI can send "confirmed": true on the user turn)
Bot: tool_calls: issue_refund {"order_id": "55", "customer_id": "C-9981"}
```

`scripts/conversation_eval.py` passes the refund because a confirmed request matches its name and `order_id`. It fails a refund of order 77, a second refund, or a refund made before the user answers. Always put the agreed arguments in `args`, because an empty `args` covers only a call with no arguments. A reply that mixes yes and no ("Yes to the refund, but don't delete my account") grants nothing, so ask again, one action per question. A transcript with no recorded request can only be judged by English-text rules, which misread ordinary phrasings, so those findings are warnings.

## Error Recovery

When a tool call fails or an external system is unavailable:

```
Level 1: Retry silently (once, with backoff)
Level 2: Acknowledge and try alternative
  "I'm having trouble looking that up. Let me try another way."
Level 3: Acknowledge and offer workaround
  "Our order system is temporarily unavailable. I can take your details and follow up by email."
Level 4: Escalate with context
  "I'm unable to complete this right now due to a system issue. Let me connect you with a team member who can help."
```

**Rules:**
- Never expose raw error messages to users.
- Never silently retry more than once.
- Always offer an alternative path forward.
- Log all errors for operational monitoring.

## Multi-Turn Context

**Context window management:**
- Keep the full conversation history in state, but only send relevant context to the LLM.
- For long conversations (>10 turns), summarize earlier turns and keep recent ones verbatim.
- Include tool results in context — the bot needs to reference what it already looked up.

**Context carryover between states:**
- When transitioning states, carry forward collected slots and resolved context.
- Don't re-ask questions the user already answered.
- Reference previous answers: "Earlier you mentioned order ORD-123456. I can see it was delivered on..."

## Conversation Boundaries

Define what the bot will and won't do:

**In-scope boundaries:**
- What topics the bot handles
- What actions the bot can take
- What information the bot can access

**Out-of-scope handling:**
```
User: "Can you write me a poem?"
Bot: "I'm here to help with [domain]. For [out-of-scope topic], I'd suggest [alternative]. Is there anything else I can help with regarding [domain]?"
```

**Safety boundaries:**
- Never provide medical, legal, or financial advice (unless the bot is specifically designed for that domain with appropriate disclaimers).
- Never share information about other users or accounts.
- Never execute actions outside the defined tool set.
- Redirect manipulation attempts: "I'm designed to help with [domain]. I can't help with that request."
