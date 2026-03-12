# Prioritization Frameworks

Detailed patterns for prioritizing features, initiatives, and deciding what to stop.

---

## RICE Scoring

**Formula**: (Reach x Impact x Confidence) / Effort

| Factor | How to Estimate | Scale |
|--------|----------------|-------|
| Reach | Number of users/customers affected per quarter | Absolute number |
| Impact | How much this moves the target metric per user | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| Confidence | How confident are you in reach and impact estimates | 100% = high, 80% = medium, 50% = low |
| Effort | Person-weeks (or person-days for small items) | Absolute number |

### Worked Example

| Initiative | Reach | Impact | Confidence | Effort | RICE Score |
|-----------|-------|--------|------------|--------|------------|
| Onboarding redesign | 500 new users/qtr | 2 (high) | 80% | 4 weeks | 200 |
| Export to CSV | 100 users/qtr | 1 (medium) | 100% | 0.5 weeks | 200 |
| AI-powered search | 300 users/qtr | 3 (massive) | 50% | 8 weeks | 56 |

**Interpretation**: Onboarding redesign and CSV export score equally. CSV export is faster to validate — ship it first, then start onboarding redesign.

### RICE Anti-Patterns
- Gaming confidence to 100% on pet projects
- Estimating reach based on total users instead of affected users
- Not updating scores after new information
- Using RICE for strategic bets (use cost-of-delay or opportunity scoring instead)

---

## ICE Scoring

**Formula**: Impact x Confidence x Ease

Simpler than RICE. Good for quick gut-check sessions.

| Factor | Scale | Description |
|--------|-------|-------------|
| Impact | 1-10 | How much this moves the target metric |
| Confidence | 1-10 | How sure you are about impact and feasibility |
| Ease | 1-10 | How easy to implement (10 = trivial, 1 = massive effort) |

**When to use**: Fast prioritization in a team session. Not rigorous enough for board-level decisions.

---

## Opportunity Scoring (JTBD-Aligned)

**Formula**: Importance + (Importance - Satisfaction)

Based on outcome-driven innovation (ODI) and jobs-to-be-done.

| Step | Action |
|------|--------|
| 1 | List the outcomes (jobs) users are trying to achieve |
| 2 | Survey users: rate importance (1-10) and satisfaction (1-10) for each |
| 3 | Calculate opportunity score: Importance + max(Importance - Satisfaction, 0) |
| 4 | High importance + low satisfaction = underserved opportunity |

**When to use**: Discovery-driven prioritization. Requires user research data.

---

## Cost of Delay

**Formula**: Value per unit time / Duration

| Type | Pattern | Example |
|------|---------|---------|
| Standard | Linear value over time | Feature that saves $10K/month — every month delayed costs $10K |
| Urgent | Decaying value (window closing) | Seasonal feature, competitive response, compliance deadline |
| Fixed date | Binary (value drops to zero after date) | Conference demo, regulatory deadline, contract requirement |

**When to use**: Time-sensitive decisions. Forces the question: "What does it cost us to NOT do this now?"

---

## Scope Negotiation Scripts

### "Can we add X?"

> "We can add X. Here's the trade-off: it would push back [existing item] by [time]. Is X more important than [existing item]? If so, let's swap. If not, let's add X to the backlog for next quarter."

### "This is a must-have"

> "I hear you — let me understand the outcome you're trying to achieve. [Listen.] Got it. We could solve that with [smaller scope option] in [shorter time]. Would that achieve 80% of the value? If so, let's start there and iterate."

### "The competitor has this"

> "They do. The question is whether our customers are choosing them because of this feature, or despite not having it. Let me check win/loss data and talk to 3 customers. If it's a real decision driver, we'll prioritize it."

### "Everything is priority 1"

> "If everything is priority 1, nothing is. Let's force-rank the top 5. Which one would you ship if you could only ship one this quarter? That's priority 1."

---

## Kill Decision Framework

### Pre-Define Kill Criteria (Before Starting)

For every initiative, document:
1. **Usage threshold**: Minimum adoption within a defined window
2. **Cost ceiling**: Maximum investment before mandatory review
3. **Time limit**: Ship-or-kill deadline
4. **Metric guardrail**: Metrics that must not degrade

### Kill Decision Meeting

Run quarterly. For each initiative past its evaluation window:
1. Review pre-defined kill criteria vs actuals
2. Three options: **Continue** (criteria met), **Pivot** (partial signal, change approach), **Kill** (criteria missed, no pivot path)
3. Document the decision and reasoning
4. Communicate to stakeholders

### What Makes Killing Hard (and How to Handle It)
- **Sunk cost fallacy**: "We already invested X." → Reframe: "Would we start this today knowing what we know?"
- **Political cost**: "Stakeholder Y pushed for this." → Reframe: "We learned [what]. Here's what we're doing instead."
- **Emotional attachment**: "The team worked hard." → Acknowledge the work, redirect the energy.
