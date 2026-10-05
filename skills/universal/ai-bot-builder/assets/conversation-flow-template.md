# Conversation Flow Template

Use this template to define a conversation state machine for a bot.

## Flow Identity

- **Flow name:** [e.g., "Order Status Inquiry"]
- **Entry condition:** [e.g., "User asks about an order"]
- **Success outcome:** [e.g., "User receives current order status"]
- **Failure outcome:** [e.g., "Issue escalated to human with context"]

## States

### State: [state_name]

- **Entry action:** [What the bot does on entering this state]
- **Bot message:** [What the bot says]
- **Expected inputs:**
  - [Input type 1] → transitions to [next_state]
  - [Input type 2] → transitions to [next_state]
- **Fallback:** [What happens on unexpected input]
- **Max turns:** [Number before forced transition]
- **Tools used:** [List of tools called in this state]

### State: greeting

- **Entry action:** Greet user, acknowledge their request
- **Bot message:** "Hi! I can help you with [topic]. [Context-specific opener]."
- **Expected inputs:**
  - Provides key information (e.g., order number) → `lookup`
  - Asks a question → `intent_classification`
  - Unclear → `clarification`
- **Fallback:** → `clarification`
- **Max turns:** 2

### State: intent_classification

- **Entry action:** Classify user intent from message
- **Expected inputs:**
  - Confidence > 0.85 → [domain-specific state]
  - Confidence 0.6-0.85 → `confirm_intent`
  - Confidence < 0.6 → `clarification`
- **Max turns:** 1

### State: [domain_handler]

- **Entry action:** [Execute domain logic — tool calls, lookups, etc.]
- **Bot message:** [Response with information or next question]
- **Expected inputs:**
  - Issue resolved → `resolution`
  - More information needed → [slot_filling state]
  - Cannot resolve → `escalation`
- **Fallback:** Re-ask with alternatives
- **Max turns:** [budget]
- **Tools used:** [list]

### State: escalation

- **Entry action:** Package context for human agent
- **Context transfer:** [intent, slots, conversation summary, customer data]
- **Bot message:** "Let me connect you with a team member who can help with this. I'll share our conversation so you won't need to repeat yourself."
- **Max turns:** 1

### State: resolution

- **Entry action:** Confirm resolution, collect satisfaction
- **Bot message:** "[Summary of what was resolved]. Is there anything else I can help with?"
- **Expected inputs:**
  - No further questions → `closing`
  - New question → `intent_classification`
- **Max turns:** 2

### State: closing

- **Entry action:** End conversation, log outcome
- **Bot message:** "Thanks for reaching out. [Satisfaction prompt if applicable]"
- **Max turns:** 1

## Flow Diagram

```
[greeting] → [intent_classification] → [domain_handler] → [resolution] → [closing]
                    ↓                         ↓
              [clarification]           [escalation]
                    ↓
           [intent_classification]
```

## Slot Requirements

| Slot | Type | Required | Validation | Prompt |
|------|------|----------|------------|--------|
| [slot_name] | [type] | [yes/no] | [rule] | [question to ask] |

## Turn Budget

- **Total conversation:** [max turns]
- **Per state:** [specified per state above]
- **Warning at:** [80% of budget]
- **Force escalation at:** [100% of budget]
