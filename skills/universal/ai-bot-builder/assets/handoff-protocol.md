# Human Handoff Protocol Template

Use this template to define how the bot hands off conversations to human agents.

## Handoff Context Payload

When escalating to a human agent, the bot packages this context:

```json
{
  "handoff_id": "hoff_abc123",
  "timestamp": "2026-03-31T14:30:00Z",
  "channel": "web_chat",

  "customer": {
    "user_id": "usr_456",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "account_tier": "premium",
    "previous_interactions": 3
  },

  "conversation": {
    "session_id": "sess_789",
    "turn_count": 7,
    "duration_seconds": 180,
    "summary": "Customer asked about a delayed order (ORD-123456). Bot confirmed the order exists and is in transit but customer is unsatisfied with the estimated delivery date.",
    "intent": "order_delay_complaint",
    "sentiment": "frustrated",
    "slots_collected": {
      "order_number": "ORD-123456",
      "order_status": "in_transit",
      "estimated_delivery": "2026-04-03"
    }
  },

  "escalation": {
    "reason": "customer_dissatisfied",
    "trigger": "sentiment_threshold",
    "priority": "high",
    "suggested_actions": [
      "Offer expedited shipping or partial refund",
      "Confirm updated delivery estimate with logistics"
    ]
  },

  "full_transcript": [
    {"role": "user", "content": "Where is my order?", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ]
}
```

## Escalation Triggers

| Trigger | Detection Method | Priority |
|---------|------------------|----------|
| User explicitly asks for human | Keyword/intent match: "talk to a person", "human agent" | High |
| Confidence below threshold | Intent classification score < [0.6] | Medium |
| Turn budget exceeded | `turn_count > max_turns` | Medium |
| Sentiment threshold | Negative sentiment detected for [2+] consecutive turns | High |
| Topic out of scope | Intent classified as out-of-scope | Medium |
| Loop detected | Same fallback triggered [3+] times | High |
| High-value action | Action value > $[threshold] or irreversible action | High |

## Queue Routing

| Routing Strategy | When to Use |
|------------------|-------------|
| **Skill-based** | Multiple support teams with different expertise |
| **Priority-based** | Mix of urgency levels (account tier, issue severity) |
| **Load-balanced** | Single team, distribute evenly |
| **Round-robin** | Fairness matters, all agents equally capable |

**Routing fields:**
- `queue_name`: Target queue identifier
- `required_skills`: Skills the human agent needs
- `priority`: 1 (highest) to 5 (lowest)
- `estimated_wait_time`: Show to user if available

## User Communication

### During Handoff
```
"I'm connecting you with a team member who can help with this. I've shared our conversation
so you won't need to repeat yourself. [Estimated wait: X minutes]"
```

### If No Agent Available
```
"Our team is currently busy. I can:
1. Keep you in the queue (estimated wait: X minutes)
2. Create a ticket and have someone reach out within [SLA]
3. Try to help you with something else in the meantime

What would you prefer?"
```

### After Handoff
The human agent sees:
- Conversation summary (not just raw transcript)
- Customer details and account context
- Suggested actions
- Full transcript (expandable)

## SLAs

| Metric | Target |
|--------|--------|
| Handoff acknowledgment | < 30 seconds (bot confirms handoff initiated) |
| Agent pickup | < [X] minutes (depends on queue, time of day) |
| Context delivery | Instant (payload delivered with handoff) |
| Resolution after handoff | Track separately from bot resolution |

## Reverse Handoff (Human → Bot)

When the human resolves part of the issue and hands back:
- Human marks which topics are resolved
- Bot resumes with updated state (resolved slots, remaining topics)
- Bot confirms: "I see [agent name] helped with [topic]. Is there anything else I can assist with?"
