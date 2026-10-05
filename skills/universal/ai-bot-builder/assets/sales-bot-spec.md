# Sales Bot Specification Template

Use this template to define a sales bot before implementation.

## Bot Identity

- **Name:** [bot name]
- **Persona:** [e.g., "Consultative, confident, curious. Asks good questions."]
- **Tone:** [e.g., "Professional, enthusiastic without being pushy. Uses 'we' language."]
- **Channel(s):** [web chat / WhatsApp / SMS / email / phone]

## Scope

### Bot Handles
- [ ] Inbound lead qualification
- [ ] Demo/meeting booking
- [ ] Pricing questions (within approved ranges)
- [ ] Product feature inquiries
- [ ] Follow-up re-engagement

### Human Handles (handoff triggers)
- [ ] Enterprise deals (> $[threshold])
- [ ] Custom pricing negotiations
- [ ] Legal/compliance questions
- [ ] Technical deep dives requiring SE
- [ ] Competitor comparison requests (if policy requires human)

## CRM Integration

| System | Purpose | API | Fields Written |
|--------|---------|-----|----------------|
| [e.g., HubSpot] | Lead/deal management | [API endpoint] | lead_status, score, notes, meeting_booked |
| [e.g., Calendly] | Meeting booking | [API endpoint] | meeting_type, datetime, attendees |
| [e.g., Slack] | Sales team notifications | Webhook | New qualified lead alerts |

## Qualification Framework

Framework: [BANT / MEDDPICC / CHAMP / Custom]

| Criterion | Question | Scoring |
|-----------|----------|---------|
| [e.g., Budget] | [e.g., "What's your approximate budget for this?"] | [e.g., >$50K = 3, $20-50K = 2, <$20K = 1, unknown = 0] |
| [e.g., Authority] | [e.g., "Who else would be involved in this decision?"] | [scoring] |
| [e.g., Need] | [e.g., "What problem are you trying to solve?"] | [scoring] |
| [e.g., Timeline] | [e.g., "When are you looking to have this in place?"] | [scoring] |

Qualification threshold: [score] / [max] → Qualified lead → handoff to sales rep

## Conversation Flows

### Inbound Lead Qualification
Entry: User initiates chat on pricing/product page
→ Greeting + context-aware opener (reference the page they're on)
→ Discovery questions (2-3 key qualification criteria)
→ If qualified: offer demo booking
→ If not qualified: provide resources, offer to follow up later

### Demo Booking
Entry: User asks for demo or bot detects high intent
→ Confirm meeting type (intro call / product demo / technical review)
→ Check calendar availability
→ Book meeting + send confirmation
→ Create/update CRM record

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Qualification rate | > [X]% | Leads that meet qualification threshold |
| Meeting booking rate | > [X]% | Qualified leads who book a meeting |
| Lead-to-opportunity rate | > [X]% | Leads that become pipeline opportunities |
| Avg qualification time | < [X] turns | Turns to reach qualification decision |
| Cost per qualified lead | < $[X] | Token + tool + infra costs per qualified lead |

## Objection Handling

| Objection | Bot Response Strategy |
|-----------|----------------------|
| Price too high | Reframe value, offer comparison, suggest starter tier |
| Not the right time | Understand timeline, offer to follow up, provide resources |
| Using competitor | Acknowledge, ask what they'd improve, offer comparison |
| Need to check with team | Offer to send summary, suggest group demo |
| Just browsing | Provide value (resources, case study), offer low-commitment next step |

## Safety Rules

- [ ] Never misrepresent product capabilities
- [ ] Never share competitor pricing details
- [ ] Never offer unauthorized discounts
- [ ] Never pressure or manipulate
- [ ] Disclose bot identity at the latest at the first interaction (EU AI Act Art. 50(1), applies from 2 Aug 2026), not only "when asked". The "obvious to a reasonably well-informed user" exception is narrow, so default to an explicit first-turn disclosure
- [ ] [Custom safety rule]
