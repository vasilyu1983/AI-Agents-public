# Stakeholder Management

Patterns for managing board members, investors, early customers, co-founders, and team leads — especially for technical founders stepping into PM responsibilities.

---
## Table of Contents

- [Board & Investor Communication](#board-&-investor-communication)
- [Monthly Update Format](#monthly-update-format)
- [Principles](#principles)
- [Early Customer Management](#early-customer-management)
- [Communication Cadence](#communication-cadence)
- [Sharing Roadmap Intent (Not Commitments)](#sharing-roadmap-intent-not-commitments)
- [Handling Feature Requests](#handling-feature-requests)
- [Co-Founder Alignment](#co-founder-alignment)
- [Weekly Co-Founder Sync (30 min)](#weekly-co-founder-sync-30-min)
- [Common Co-Founder Misalignment Patterns](#common-co-founder-misalignment-patterns)
- [Decision Rights Framework](#decision-rights-framework)
- [Stakeholder Map at Scale](#stakeholder-map-at-scale)
- [Saying No to Stakeholders](#saying-no-to-stakeholders)
- [Framework: Acknowledge → Explain → Redirect](#framework-acknowledge-→-explain-→-redirect)
- [Common Scenarios](#common-scenarios)
- [Anti-Patterns](#anti-patterns)


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

## Stakeholder Map at Scale

For staff and principal PMs at larger companies, the stakeholder surface expands well beyond board and co-founders. Below is the core map: what each function needs from the PM, when to involve them, and their RACI role on typical product decisions.

**RACI key used here:**
- **D** = Decision owner (has final call)
- **C** = Consulted before decision (input materially shapes outcome)
- **I** = Informed after decision (no input required, but must know)

| Stakeholder | What they need from PM | When to involve | Typical RACI |
|-------------|------------------------|-----------------|--------------|
| **Engineering lead** | Clear requirements, stable scope, early visibility into upcoming work, explicit trade-off decisions on scope vs. timeline | Before spec is locked; immediately on any scope change | C on roadmap; D on technical approach |
| **Design / UX** | Problem framing before solutions, user research access, design review time built into schedule | Before any user-facing work starts; not after wireframes exist | C on spec; D on interaction patterns |
| **Data science / Analytics** | Metric definitions, instrumentation requirements, experiment design approval | Before launch for any experiment; before spec for metric-heavy features | C on success metrics; D on experiment methodology |
| **Legal / Privacy** | Data collection scope, third-party integrations, regulated feature areas (payments, health, minors) | As early as possible for regulated areas — legal holds can kill timelines | C on data handling; D on compliance requirements |
| **Security** | Auth flows, data storage decisions, third-party API access | At design stage for any new data surface or auth change | C on design; D on security requirements |
| **Marketing** | Launch timing, naming, positioning, go-to-market readiness, feature announcements | 4–8 weeks before launch; at roadmap planning for major bets | C on positioning; I on shipping decisions |
| **Sales** | Deal-blocking gaps, enterprise feature requests, pricing implications, beta access for prospects | Quarterly roadmap reviews; immediately for deal-critical blockers | I on most roadmap; C on enterprise-tier decisions |
| **Customer success** | Rollout sequencing, customer communication, migration support burden, early warning on churn risk | Before any change to existing workflows; during beta for high-touch accounts | I on roadmap; C on rollout plan |
| **Finance** | Cost implications of infrastructure changes, revenue model impact, headcount tied to bets | For any bet with material cost or revenue impact (typically >$50K or >0.5 HC) | C on business case; I on execution |

**Practical guidance:**
- Over-communicate with engineering and design — they are execution partners, not recipients of finished specs.
- Involve legal and security earlier than feels necessary; they cannot move faster than their process allows.
- Sales and CS are your earliest signal on real-world friction — treat their escalations as leading indicators, not noise.
- Informed stakeholders who feel surprised become blockers; send a weekly digest or use a shared roadmap artifact rather than one-off Slack messages.

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
