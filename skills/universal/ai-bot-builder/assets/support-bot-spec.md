# Support Bot Specification Template

Use this template to define a support bot before implementation.

## Bot Identity

- **Name:** [bot name]
- **Persona:** [brief personality description — e.g., "Friendly, concise, solution-oriented"]
- **Tone:** [e.g., "Professional but warm. Uses contractions. Avoids jargon."]
- **Channel(s):** [web chat / WhatsApp / SMS / email / in-app]

## Scope

### In-Scope Topics
- [ ] [Topic 1 — e.g., Order status inquiries]
- [ ] [Topic 2 — e.g., Returns and refunds]
- [ ] [Topic 3 — e.g., Account management]

### Out-of-Scope Topics
- [ ] [Topic — e.g., Legal disputes] → [Redirect: "Please contact legal@company.com"]
- [ ] [Topic — e.g., Product feature requests] → [Redirect: "I'll note that as feedback"]

## Tools and Integrations

| Tool | Purpose | API | Auth |
|------|---------|-----|------|
| Knowledge base search | Answer questions from help articles | [API endpoint] | [API key / OAuth] |
| Order lookup | Check order status by order number or email | [API endpoint] | [API key] |
| Ticket creation | Create support tickets for unresolved issues | [e.g., Zendesk API] | [OAuth] |
| Account lookup | Verify customer identity and pull account data | [API endpoint] | [API key] |

## Conversation Flows

### Primary Flows
1. **[Flow name]:** [Entry condition] → [Key steps] → [Resolution / Escalation]
2. **[Flow name]:** ...

### Escalation Triggers
- Confidence score < [threshold, e.g., 0.6]
- User explicitly asks for human
- Topic is out of scope
- Turn count > [max, e.g., 10]
- Sentiment detected as [frustrated / angry]
- [Custom trigger]

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Containment rate | > [X]% | Conversations resolved without human |
| CSAT | > [X]/5 | Post-conversation survey |
| Resolution rate | > [X]% | Issue confirmed resolved |
| Avg turns to resolution | < [X] | Turns in resolved conversations |
| Cost per conversation | < $[X] | Token + tool + infra costs |

## Safety Rules

- [ ] Never provide medical/legal/financial advice
- [ ] Never share data from other customer accounts
- [ ] Never execute actions outside defined tool set
- [ ] Always offer human escalation path
- [ ] [Custom safety rule]

## Pre-Launch Checklist

- [ ] Conversation flows tested with multi-turn eval suite
- [ ] Fallback hierarchy verified for all states
- [ ] Escalation path tested end-to-end
- [ ] Safety boundaries tested with adversarial inputs
- [ ] Analytics instrumented (containment, CSAT, escalation)
- [ ] Cost per conversation estimated and within budget
- [ ] PII handling reviewed and compliant
- [ ] Channel-specific constraints verified
