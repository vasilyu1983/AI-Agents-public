# Stakeholder Management

Patterns for managing board members, investors, early customers, co-founders, and team leads — especially for technical founders stepping into PM responsibilities.

---

## Board & Investor Communication

### Monthly Update Format

Keep it short (1 page max). Investors read 50+ updates per month.

```
Subject: [Company] — [Month] Update

HEADLINE: One sentence — the most important thing that happened.

METRICS (table):
- MRR / Revenue
- Burn / Runway
- Key product metric (activation, retention, or PMF indicator)
- Pipeline (if B2B)

WINS (3 max):
- [Win 1]
- [Win 2]
- [Win 3]

LEARNINGS (1-2):
- What we learned and what we're changing

CHALLENGES (1-2):
- What's hard right now

ASKS (specific):
- Intro to [specific person/company]
- Advice on [specific decision]
- [Other specific, actionable ask]
```

### Principles
- Lead with "what we learned" not "what we shipped"
- Never surprise investors with bad news — surface problems early
- Make asks specific and actionable (not "help us grow")
- Share metrics consistently — same format every month
- Acknowledge mistakes openly; show what you're doing differently

---

## Early Customer Management

Early customers are partners, not just users. They shaped the product and their continued engagement matters.

### Communication Cadence

| Activity | Frequency | Purpose |
|----------|-----------|---------|
| Usage check-in | Bi-weekly | Are they getting value? What's broken? |
| Roadmap preview | Monthly | Share direction, get input on priorities |
| Feature feedback | As-needed | Targeted questions about specific features |
| Business review | Quarterly | Formal review of value delivered, renewal, expansion |

### Sharing Roadmap Intent (Not Commitments)

> "We're exploring [direction] because we're seeing [signal]. We haven't committed to building [specific feature] yet. What would be most valuable for your use case?"

**Never say**: "We're building X by [date]" (unless it's in active development with a committed timeline).

### Handling Feature Requests

1. Thank them and document the request
2. Understand the underlying need: "What would this enable you to do that you can't do today?"
3. Assess against strategy: Does this align with where we're going?
4. Respond honestly:
   - "This aligns with our roadmap — we'll prioritize it" (only if true)
   - "This is a great idea but not in our current focus. Here's why, and here's what we're focusing on instead."
   - "We won't build this because [reason]. Here's an alternative approach."

---

## Co-Founder Alignment

### Weekly Co-Founder Sync (30 min)

1. **What happened this week** (5 min each)
2. **Decisions needed** (10 min) — explicitly list decisions, not just discussion topics
3. **Disagree and commit** (5 min) — any unresolved disagreements? Pick one path, commit, set a review date
4. **Next week priorities** (5 min) — top 3 each, no overlap

### Common Co-Founder Misalignment Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Different visions | Roadmap conflicts, feature disagreements | Align on 6-month vision quarterly; write it down |
| Different risk tolerance | One moves fast, other blocks | Define decision rights: who owns what domain |
| Unequal contribution | Resentment, passive-aggressive behavior | Track commitments weekly; address directly within 1 week |
| Communication breakdown | Surprises, duplicate work | Daily standup (5 min) + weekly sync (30 min) |

### Decision Rights Framework

Define who makes final calls in each domain:
- Product direction → [Name]
- Technical architecture → [Name]
- Hiring → [Joint, with veto rights]
- Spending > $X → [Joint]
- Customer-facing commitments → [Name]
- Fundraising → [Joint]

"Disagree and commit" only works if decision rights are clear. Otherwise every disagreement becomes a negotiation.

---

## Saying No to Stakeholders

### Framework: Acknowledge → Explain → Redirect

> **Acknowledge**: "I understand why [feature/request] matters to you."
> **Explain**: "We're not doing it because [reason tied to strategy, not capacity]."
> **Redirect**: "Here's what we're doing instead and why it addresses the underlying need."

### Common Scenarios

**Investor pushes a feature idea:**
> "That's an interesting direction. Right now our data shows [metric], which tells us [insight]. We're focused on [current priority] because it addresses [root cause]. If [metric] changes, we'll revisit."

**Enterprise customer demands custom feature:**
> "We want to keep you successful. Building a custom feature would slow down the platform improvements that benefit all customers, including you. Can we explore [alternative: configuration, integration, workflow change] instead?"

**Board member questions product strategy:**
> "Here's the data behind our current strategy: [metrics]. Our hypothesis is [statement]. We'll know if we're right by [date] when we measure [metric]. If we're wrong, here's our pivot plan."

**Team member wants to build something "cool":**
> "I love the technical ambition. Let's check: does this move [our target metric]? If yes, let's prioritize it properly. If not, let's save it for a hack week or side project."

---

## Anti-Patterns

- **Stakeholder-driven roadmap**: Letting the loudest voice determine priorities instead of data and strategy.
- **Information asymmetry**: Different stakeholders hear different versions of the strategy.
- **Over-promising**: Saying yes to everything to avoid conflict, then under-delivering.
- **Under-communicating**: Assuming silence means alignment. It doesn't — it means they'll be surprised later.
- **Avoiding hard conversations**: Letting disagreements fester instead of addressing them within 48 hours.
